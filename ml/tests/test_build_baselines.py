from datetime import datetime, timezone

from ml.training.build_baselines import build_all_baselines, compute_source_baseline


def _obs(frp, month, hour, day=10):
    return {
        "frp": frp,
        "timestamp_utc": datetime(2024, month, day, hour, 0, tzinfo=timezone.utc),
    }


def test_baseline_stats_on_known_values():
    observations = [_obs(100, 1, 18), _obs(120, 1, 19), _obs(140, 1, 20)]
    baseline = compute_source_baseline(observations)

    assert baseline["mean_frp"] == 120.0
    assert baseline["median_frp"] == 120.0
    assert baseline["frp_std"] > 0
    assert baseline["observation_count"] == 3
    assert baseline["typical_hours"][18] == 1
    assert baseline["typical_hours"][19] == 1
    assert baseline["monthly_profile"][1] == 120.0


def test_baseline_handles_missing_frp_gracefully():
    observations = [
        {"frp": None, "timestamp_utc": datetime(2024, 1, 10, 12, tzinfo=timezone.utc)},
        {"frp": None, "timestamp_utc": datetime(2024, 1, 11, 13, tzinfo=timezone.utc)},
    ]
    baseline = compute_source_baseline(observations)

    assert baseline["mean_frp"] is None
    assert baseline["frp_std"] is None
    assert baseline["median_frp"] is None
    assert baseline["observation_count"] == 2
    # Missing FRP is not the same as "no fire" — hour histogram still counts
    # the observation itself, just not its intensity.
    assert baseline["typical_hours"][12] == 1


def test_build_all_baselines_skips_empty_sources():
    result = build_all_baselines({"src-1": [_obs(100, 1, 18)], "src-2": []})
    assert "src-1" in result
    assert "src-2" not in result


def test_seasonal_profile_groups_by_agnidrishti_seasons():
    # Jan (winter=1), Apr (summer=2), Jul (monsoon=3), Nov (post-monsoon=4)
    observations = [_obs(100, 1, 10), _obs(200, 4, 10), _obs(300, 7, 10), _obs(400, 11, 10)]
    baseline = compute_source_baseline(observations)

    assert baseline["seasonal_profile"][1] == 100.0
    assert baseline["seasonal_profile"][2] == 200.0
    assert baseline["seasonal_profile"][3] == 300.0
    assert baseline["seasonal_profile"][4] == 400.0
