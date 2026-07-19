"""Tests for runtime progress reporting."""

from io import StringIO

from faircareai.core.progress import ProgressReporter


def test_progress_reporter_prints_stage_and_elapsed_time() -> None:
    stream = StringIO()
    clock_values = iter([10.0, 12.75])
    reporter = ProgressReporter(enabled=True, stream=stream, clock=lambda: next(clock_values))

    reporter.stage(2, 5, "subgroup bootstrap: insurance (12 groups)")
    reporter.complete()

    output = stream.getvalue()
    assert "[2/5] subgroup bootstrap: insurance (12 groups)" in output
    assert "Audit complete in 2.75s" in output


def test_progress_reporter_can_be_disabled() -> None:
    stream = StringIO()
    reporter = ProgressReporter(enabled=False, stream=stream, clock=lambda: 1.0)

    reporter.stage(1, 5, "validation")
    reporter.complete()

    assert stream.getvalue() == ""
