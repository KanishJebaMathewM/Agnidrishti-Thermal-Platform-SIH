from datetime import datetime, timedelta, timezone

from workers.enrichment.update_source_registry import (
    ARCHIVED,
    CANDIDATE,
    MONITORED,
    OBSERVED,
    InMemorySourceRegistryStore,
    archive_stale_sources,
    confirm_source,
    update_source_registry_for_observation,
)

H3_CELL = "873da1146ffffff"


def _obs(day_offset: int, frp=50.0):
    return {
        "h3_cell": H3_CELL,
        "timestamp_utc": datetime(2026, 8, 1, tzinfo=timezone.utc) + timedelta(days=day_offset),
        "frp": frp,
    }


def test_first_observation_creates_source_and_moves_past_new():
    store = InMemorySourceRegistryStore()
    result = update_source_registry_for_observation(_obs(0), store)
    assert result["status"] == OBSERVED  # NEW is transient; by return time it's OBSERVED
    assert result["observation_count"] == 1
    assert store.find_by_h3(H3_CELL)["status"] == OBSERVED


def test_third_observation_within_window_promotes_to_candidate():
    store = InMemorySourceRegistryStore()
    update_source_registry_for_observation(_obs(0), store)
    update_source_registry_for_observation(_obs(2), store)
    result = update_source_registry_for_observation(_obs(4), store)  # 3rd obs, within 7 days
    assert result["status"] == CANDIDATE
    assert result["observation_count"] == 3


def test_observations_outside_window_do_not_count_toward_candidate():
    store = InMemorySourceRegistryStore()
    update_source_registry_for_observation(_obs(0), store)
    update_source_registry_for_observation(_obs(1), store)
    # 20 days later — the first two observations have fallen out of the 7-day window.
    result = update_source_registry_for_observation(_obs(20), store)
    assert result["status"] == OBSERVED
    assert result["observation_count"] == 3


def test_mean_frp_tracks_across_observations():
    store = InMemorySourceRegistryStore()
    update_source_registry_for_observation(_obs(0, frp=40.0), store)
    result = update_source_registry_for_observation(_obs(1, frp=60.0), store)
    assert result["mean_frp"] == 50.0


def test_confirm_source_moves_candidate_to_monitored():
    store = InMemorySourceRegistryStore()
    update_source_registry_for_observation(_obs(0), store)
    update_source_registry_for_observation(_obs(2), store)
    result = update_source_registry_for_observation(_obs(4), store)
    assert result["status"] == CANDIDATE

    confirmed = confirm_source(result["id"], store)
    assert confirmed["status"] == MONITORED


def test_confirm_source_is_noop_when_not_candidate():
    store = InMemorySourceRegistryStore()
    result = update_source_registry_for_observation(_obs(0), store)
    assert result["status"] == OBSERVED

    unchanged = confirm_source(result["id"], store)
    assert unchanged["status"] == OBSERVED


def test_archive_stale_sources_archives_only_monitored_idle_past_k_days():
    store = InMemorySourceRegistryStore()
    result = update_source_registry_for_observation(_obs(0), store)
    update_source_registry_for_observation(_obs(2), store)
    result = update_source_registry_for_observation(_obs(4), store)
    confirm_source(result["id"], store)

    now_too_soon = datetime(2026, 8, 1, tzinfo=timezone.utc) + timedelta(days=4 + 89)
    assert archive_stale_sources(store, now_too_soon) == []
    assert store.get(result["id"])["status"] == MONITORED

    now_stale = datetime(2026, 8, 1, tzinfo=timezone.utc) + timedelta(days=4 + 90)
    archived = archive_stale_sources(store, now_stale)
    assert archived == [result["id"]]
    assert store.get(result["id"])["status"] == ARCHIVED


def test_archive_stale_sources_ignores_non_monitored():
    store = InMemorySourceRegistryStore()
    update_source_registry_for_observation(_obs(0), store)  # stays OBSERVED
    far_future = datetime(2026, 8, 1, tzinfo=timezone.utc) + timedelta(days=365)
    assert archive_stale_sources(store, far_future) == []
