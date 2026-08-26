from workers.enrichment.enrich_geography import enrich_geography_context


def test_point_near_jamnagar_finds_nearest_facility_and_state():
    # Jamnagar Refinery Zone fixture is at (22.2394, 70.0577); Gujarat box covers it.
    context = enrich_geography_context(22.30, 70.10)
    assert context["nearest_facility_name"] == "Jamnagar Refinery Zone"
    assert context["nearest_facility_type"] == "Refinery"
    assert context["nearest_facility_km"] is not None
    assert context["state"] == "Gujarat"


def test_point_in_western_ghats_forest_patch_flagged_as_forest():
    context = enrich_geography_context(13.3, 75.8)
    assert context["is_forest"] is True


def test_point_far_from_everything_returns_none_not_guessed():
    # Middle of the Bay of Bengal — no state box, no forest, no landuse, no
    # facility within 50km. Every field must be None/False, never fabricated.
    context = enrich_geography_context(15.0, 88.0)
    assert context["state"] is None
    assert context["landuse_class"] is None
    assert context["is_forest"] is False
    assert context["nearest_facility_name"] is None
    assert context["nearest_facility_km"] is None


def test_punjab_point_matches_agricultural_landuse():
    context = enrich_geography_context(30.5, 75.5)
    assert context["state"] == "Punjab"
    assert context["landuse_class"] == "Agricultural"
