from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
import polars as pl
import pytest

from faircareai.core.exceptions import DataValidationError
from faircareai.data.spark_adapter import is_pyspark_dataframe, spark_to_polars


class AtomicType:
    def typeName(self) -> str:
        return "double"


class ArrayType:
    def typeName(self) -> str:
        return "array"


@dataclass
class Field:
    name: str
    dataType: object


@dataclass
class Schema:
    fields: list[Field]


class FakeStorageLevel:
    MEMORY_AND_DISK = object()


class FakeSparkFrame:
    __module__ = "pyspark.sql.dataframe"

    def __init__(
        self,
        frame: pd.DataFrame,
        *,
        schema: Schema | None = None,
        streaming: bool = False,
        fail_conversion: bool = False,
    ) -> None:
        self.frame = frame
        self.columns = list(frame.columns)
        self.schema = schema or Schema([Field(name, AtomicType()) for name in self.columns])
        self.isStreaming = streaming
        self.fail_conversion = fail_conversion
        self.selected: list[str] | None = None
        self.limit_value: int | None = None
        self.persisted_with: object | None = None
        self.unpersisted = False

    def select(self, *columns: str) -> FakeSparkFrame:
        selected = FakeSparkFrame(
            self.frame.loc[:, list(columns)],
            schema=Schema([f for f in self.schema.fields if f.name in columns]),
            fail_conversion=self.fail_conversion,
        )
        selected.selected = list(columns)
        # Preserve a shared event record on the root object.
        selected._root = getattr(self, "_root", self)
        selected._root.selected = list(columns)
        return selected

    def persist(self, storage_level: object | None = None) -> FakeSparkFrame:
        root = getattr(self, "_root", self)
        root.persisted_with = storage_level
        return self

    def limit(self, value: int) -> FakeSparkFrame:
        root = getattr(self, "_root", self)
        root.limit_value = value
        limited = FakeSparkFrame(
            self.frame.head(value), schema=self.schema, fail_conversion=self.fail_conversion
        )
        limited._root = root
        return limited

    def count(self) -> int:
        return len(self.frame)

    def toPandas(self) -> pd.DataFrame:
        if self.fail_conversion:
            raise RuntimeError("worker disappeared")
        return self.frame.copy()

    def unpersist(self) -> None:
        getattr(self, "_root", self).unpersisted = True


def test_detects_pyspark_lazily_and_rejects_plain_dataframe() -> None:
    fake = FakeSparkFrame(pd.DataFrame({"prediction": [0.2]}))

    assert is_pyspark_dataframe(fake)
    assert not is_pyspark_dataframe(pl.DataFrame({"prediction": [0.2]}))


def test_collects_only_deduplicated_required_columns_with_guard() -> None:
    fake = FakeSparkFrame(
        pd.DataFrame(
            {
                "prediction": [0.2, 0.8],
                "outcome": [0, 1],
                "race": ["A", "B"],
                "unused_phi": ["x", "y"],
            }
        )
    )

    result = spark_to_polars(
        fake,
        ["prediction", "outcome", "race", "race"],
        max_collect_rows=2,
        storage_level=FakeStorageLevel.MEMORY_AND_DISK,
    )

    assert result.columns == ["prediction", "outcome", "race"]
    assert fake.selected == ["prediction", "outcome", "race"]
    assert fake.limit_value == 3
    assert fake.persisted_with is FakeStorageLevel.MEMORY_AND_DISK
    assert fake.unpersisted


@pytest.mark.parametrize("limit", [0, -1, True, 1.5])
def test_rejects_invalid_collection_limits(limit: object) -> None:
    fake = FakeSparkFrame(pd.DataFrame({"prediction": [0.2]}))

    with pytest.raises(DataValidationError, match="positive integer"):
        spark_to_polars(fake, ["prediction"], max_collect_rows=limit)  # type: ignore[arg-type]


def test_rejects_too_many_rows_before_conversion_and_unpersists() -> None:
    fake = FakeSparkFrame(pd.DataFrame({"prediction": [0.1, 0.2, 0.3]}))

    with pytest.raises(DataValidationError, match="2.*filter, aggregate.*higher"):
        spark_to_polars(fake, ["prediction"], max_collect_rows=2)

    assert fake.limit_value == 3
    assert fake.unpersisted


def test_rejects_streaming_missing_and_complex_columns_before_action() -> None:
    streaming = FakeSparkFrame(pd.DataFrame({"prediction": [0.2]}), streaming=True)
    with pytest.raises(DataValidationError, match="Streaming"):
        spark_to_polars(streaming, ["prediction"])

    missing = FakeSparkFrame(pd.DataFrame({"prediction": [0.2]}))
    with pytest.raises(DataValidationError, match="Missing.*outcome"):
        spark_to_polars(missing, ["prediction", "outcome"])
    assert missing.limit_value is None

    complex_frame = FakeSparkFrame(
        pd.DataFrame({"prediction": [[0.2]]}),
        schema=Schema([Field("prediction", ArrayType())]),
    )
    with pytest.raises(DataValidationError, match="array.*prediction|prediction.*array"):
        spark_to_polars(complex_frame, ["prediction"])
    assert complex_frame.limit_value is None


def test_unpersists_and_wraps_conversion_failures_without_values() -> None:
    fake = FakeSparkFrame(pd.DataFrame({"prediction": [0.2]}), fail_conversion=True)

    with pytest.raises(DataValidationError, match="prediction.*Spark DataFrame") as exc_info:
        spark_to_polars(fake, ["prediction"])

    assert fake.unpersisted
    assert "worker disappeared" not in str(exc_info.value)
