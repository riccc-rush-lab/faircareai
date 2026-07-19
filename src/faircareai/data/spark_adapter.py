"""Guarded conversion of batch PySpark DataFrames to Polars.

PySpark is deliberately not imported at module import time.  This keeps Spark an
optional integration while enforcing a bounded driver collection when it is used.
"""

from __future__ import annotations

from collections.abc import Sequence
from contextlib import suppress
from typing import Any

import polars as pl

from faircareai.core.exceptions import DataValidationError

DEFAULT_MAX_COLLECT_ROWS = 500_000
_COMPLEX_SPARK_TYPES = {"array", "map", "struct"}


def is_pyspark_dataframe(data: object) -> bool:
    """Return whether *data* has the batch PySpark DataFrame interface.

    The module check avoids importing PySpark just to inspect an ordinary pandas
    or Polars object.  The method checks also make this compatible with Spark
    Connect DataFrames and lightweight test doubles.
    """

    cls = type(data)
    module = getattr(cls, "__module__", "")
    spark_module = module == "pyspark.sql" or module.startswith("pyspark.sql.")
    spark_interface = all(
        callable(getattr(data, method, None))
        for method in ("select", "limit", "count", "toPandas")
    )
    return spark_module and spark_interface and hasattr(data, "schema")


def spark_to_polars(
    data: Any,
    columns: Sequence[str],
    *,
    max_collect_rows: int = DEFAULT_MAX_COLLECT_ROWS,
    storage_level: Any | None = None,
) -> pl.DataFrame:
    """Collect a narrow, bounded Spark projection and convert it to Polars.

    Args:
        data: A batch PySpark DataFrame.
        columns: Columns needed by the local audit engine.
        max_collect_rows: Positive upper bound for driver collection.
        storage_level: Internal injection seam for tests.  Production callers
            should leave this unset to use PySpark ``MEMORY_AND_DISK``.

    Raises:
        DataValidationError: If input, schema, or collection safety checks fail.
    """

    _validate_limit(max_collect_rows)
    if not is_pyspark_dataframe(data):
        raise DataValidationError("Expected a batch PySpark DataFrame")
    if bool(getattr(data, "isStreaming", False)):
        raise DataValidationError(
            "Streaming PySpark DataFrames are not supported; materialize a bounded batch first"
        )

    selected_columns = _normalize_columns(columns)
    available = list(getattr(data, "columns", ()))
    missing = [name for name in selected_columns if name not in available]
    if missing:
        raise DataValidationError(
            f"Missing selected Spark columns: {', '.join(missing)}. "
            f"Available columns: {', '.join(available[:10])}"
        )

    _validate_selected_types(data, selected_columns)

    projected = None
    persisted = None
    try:
        projected = data.select(*selected_columns)
        persisted = _persist(projected, storage_level)
        observed_rows = persisted.limit(max_collect_rows + 1).count()
        if observed_rows > max_collect_rows:
            raise DataValidationError(
                f"Spark input exceeds max_collect_rows={max_collect_rows:,} for selected "
                f"columns [{', '.join(selected_columns)}]. Please filter, aggregate, or deliberately "
                "choose a higher positive limit before collecting data to the driver"
            )

        pandas_frame = _to_pandas_with_arrow(persisted)
        return pl.from_pandas(pandas_frame)
    except DataValidationError:
        raise
    except Exception as exc:
        raise DataValidationError(
            "Could not collect selected columns "
            f"[{', '.join(selected_columns)}] from the Spark DataFrame: "
            f"{type(exc).__name__}. The configured row limit was {max_collect_rows:,}; "
            "filter the input or inspect the Spark job logs for details"
        ) from exc
    finally:
        cleanup_target = persisted if persisted is not None else projected
        if cleanup_target is not None:
            # Cleanup must not hide the collection error that led here.
            with suppress(Exception):
                cleanup_target.unpersist()


def _validate_limit(value: int) -> None:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise DataValidationError("max_collect_rows must be a positive integer")


def _normalize_columns(columns: Sequence[str]) -> list[str]:
    if isinstance(columns, str):
        raw_columns: Sequence[str] = [columns]
    else:
        raw_columns = columns

    for column in raw_columns:
        if not isinstance(column, str) or not column:
            raise DataValidationError("Selected Spark column names must be non-empty strings")
    normalized = list(dict.fromkeys(raw_columns))
    if not normalized:
        raise DataValidationError("At least one Spark column must be selected")
    return normalized


def _validate_selected_types(data: Any, columns: Sequence[str]) -> None:
    fields = getattr(getattr(data, "schema", None), "fields", ())
    fields_by_name = {getattr(field, "name", None): field for field in fields}
    unsupported: list[str] = []
    for name in columns:
        field = fields_by_name.get(name)
        data_type = getattr(field, "dataType", None)
        type_name_method = getattr(data_type, "typeName", None)
        if callable(type_name_method):
            type_name = str(type_name_method()).lower()
        else:
            type_name = type(data_type).__name__.removesuffix("Type").lower()
        if type_name in _COMPLEX_SPARK_TYPES:
            unsupported.append(f"{name} ({type_name})")

    if unsupported:
        raise DataValidationError(
            "Selected Spark columns use unsupported complex types: "
            f"{', '.join(unsupported)}. Cast or flatten array, map, and struct columns first"
        )


def _persist(data: Any, storage_level: Any | None) -> Any:
    resolved_level = storage_level
    if resolved_level is None:
        try:
            from pyspark import StorageLevel

            resolved_level = StorageLevel.MEMORY_AND_DISK
        except ImportError:
            # A Spark-compatible test double or alternative runtime may not expose
            # the package in this interpreter. Its default persistence is adequate.
            return data.persist()
    return data.persist(resolved_level)


def _to_pandas_with_arrow(data: Any) -> Any:
    """Enable Arrow when a Spark session is available, restoring its setting."""

    spark_session = getattr(data, "sparkSession", None)
    conf = getattr(spark_session, "conf", None)
    if conf is None:
        return data.toPandas()

    key = "spark.sql.execution.arrow.pyspark.enabled"
    previous: str | None = None
    try:
        previous = conf.get(key, None)
    except (TypeError, AttributeError):
        try:
            previous = conf.get(key)
        except Exception:
            previous = None

    conf.set(key, "true")
    try:
        return data.toPandas()
    finally:
        if previous is not None:
            conf.set(key, previous)
        else:
            unset = getattr(conf, "unset", None)
            if callable(unset):
                unset(key)
