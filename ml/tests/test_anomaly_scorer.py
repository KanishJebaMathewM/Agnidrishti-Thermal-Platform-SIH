from ml.inference.anomaly_scorer import (
    Z_SCORE_ANOMALY_THRESHOLD,
    compute_anomaly,
    statistical_anomaly,
)


def _feature_vector(frp_zscore):
    return {"frp_zscore": frp_zscore, "frp": 300.0}


def test_zscore_above_threshold_flags_anomaly():
    result = statistical_anomaly(3.5)
    assert Z_SCORE_ANOMALY_THRESHOLD == 3.0
    assert result["flag"] is True

    combined = compute_anomaly(_feature_vector(3.5), source_baseline={"mean_frp": 100, "frp_std": 20})
    assert combined["anomaly_flag"] is True
    assert combined["baseline_deviation"] == 3.5


def test_zscore_below_one_does_not_flag_anomaly():
    result = statistical_anomaly(0.8)
    assert result["flag"] is False

    combined = compute_anomaly(_feature_vector(0.8), source_baseline={"mean_frp": 100, "frp_std": 20})
    assert combined["anomaly_flag"] is False


def test_missing_baseline_uses_zscore_only():
    # No baseline at all -> feature builder would never have produced a
    # zscore, so frp_zscore is None here. Without an Isolation Forest model
    # either, the combined score must fall back to a neutral (0.0) score
    # rather than erroring, and must not be flagged.
    combined = compute_anomaly({"frp_zscore": None, "frp": 150.0}, source_baseline=None, isolation_forest_model=None)
    assert combined["anomaly_score"] == 0.0
    assert combined["anomaly_flag"] is False
    assert combined["baseline_deviation"] is None
    assert "no baseline" in combined["anomaly_reason"].lower()


def test_anomaly_score_scales_with_zscore_magnitude():
    low = compute_anomaly(_feature_vector(1.0), source_baseline={"mean_frp": 100, "frp_std": 20})
    high = compute_anomaly(_feature_vector(5.0), source_baseline={"mean_frp": 100, "frp_std": 20})
    assert high["anomaly_score"] > low["anomaly_score"]
    assert 0.0 <= low["anomaly_score"] <= 1.0
    assert 0.0 <= high["anomaly_score"] <= 1.0


def test_known_flare_within_normal_range_scores_low_even_with_high_frp():
    # A source with a high but STABLE historical FRP (e.g. a continuous
    # flare) should not be penalized just because its absolute FRP is high —
    # only deviation from its own baseline matters.
    combined = compute_anomaly(_feature_vector(0.2), source_baseline={"mean_frp": 480, "frp_std": 50})
    assert combined["anomaly_flag"] is False
    assert combined["anomaly_score"] < 0.5
