"""Tests for publication-safe small-cell handling."""

from faircareai.core.privacy import mark_suppressed_groups, report_value


def test_marks_nested_group_records_without_removing_raw_values() -> None:
    payload = {
        "groups": {
            "small": {"n": 7, "auroc": 0.61},
            "large": {"n": 20, "auroc": 0.81},
        }
    }

    mark_suppressed_groups(payload, threshold=11)

    assert payload["groups"]["small"]["auroc"] == 0.61
    assert payload["groups"]["small"]["suppressed_in_reports"] is True
    assert payload["groups"]["large"]["suppressed_in_reports"] is False


def test_report_value_replaces_every_small_cell_metric() -> None:
    record = {"n": 7, "tpr": 0.75, "suppressed_in_reports": True}

    assert report_value(record, "n", threshold=11) == "suppressed (n<11)"
    assert report_value(record, "tpr", threshold=11) == "suppressed (n<11)"


def test_report_value_keeps_large_group_value() -> None:
    record = {"n": 12, "tpr": 0.75, "suppressed_in_reports": False}

    assert report_value(record, "tpr", threshold=11) == 0.75
