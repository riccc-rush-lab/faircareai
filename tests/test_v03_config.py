"""Configuration defaults introduced for the v0.3 production-audit release."""

from faircareai.core.config import FairnessConfig


def test_v03_privacy_and_calibration_threshold_defaults() -> None:
    thresholds = FairnessConfig(model_name="test").thresholds

    assert thresholds["suppress_cell_n"] == 11
    assert thresholds["max_oe_deviation"] == 0.10
    assert thresholds["max_calibration_slope_deviation"] == 0.10
