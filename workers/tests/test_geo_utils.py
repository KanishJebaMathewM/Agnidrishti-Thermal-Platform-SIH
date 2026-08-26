from shapely.geometry import box

from workers.utils.geo import is_within_india, lat_lon_to_h3, point_to_wkt
from workers.utils.india_boundary import get_india_geom


def test_lat_lon_to_h3_is_deterministic():
    cell1 = lat_lon_to_h3(28.6139, 77.2090)
    cell2 = lat_lon_to_h3(28.6139, 77.2090)
    assert cell1 == cell2
    assert isinstance(cell1, str) and len(cell1) > 0


def test_lat_lon_to_h3_different_points_different_cells():
    delhi = lat_lon_to_h3(28.6139, 77.2090)
    chennai = lat_lon_to_h3(13.0827, 80.2707)
    assert delhi != chennai


def test_point_to_wkt_format():
    assert point_to_wkt(28.6139, 77.2090) == "SRID=4326;POINT(77.209 28.6139)"


def test_is_within_india_true_for_delhi():
    square = box(70, 20, 80, 30)
    assert is_within_india(25.0, 75.0, square) is True


def test_is_within_india_false_outside_polygon():
    square = box(70, 20, 80, 30)
    assert is_within_india(50.0, 75.0, square) is False


def test_real_india_boundary_contains_known_indian_cities():
    geom = get_india_geom()
    for lat, lon in [(28.6139, 77.2090), (13.0827, 80.2707), (19.0760, 72.8777)]:
        assert is_within_india(lat, lon, geom) is True


def test_real_india_boundary_excludes_neighboring_countries():
    geom = get_india_geom()
    # Karachi, Pakistan and Colombo, Sri Lanka are outside India's boundary
    # but well inside the FIRMS India bounding box rectangle.
    assert is_within_india(24.8607, 67.0011, geom) is False
    assert is_within_india(6.9271, 79.8612, geom) is False
