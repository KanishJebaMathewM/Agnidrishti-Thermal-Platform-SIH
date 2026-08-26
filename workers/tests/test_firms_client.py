from datetime import date

import httpx

from workers.ingestion.firms_client import FIRMSClient, INDIA_BBOX

SAMPLE_CSV = (
    "latitude,longitude,bright_ti4,bright_ti5,scan,track,acq_date,acq_time,"
    "satellite,instrument,confidence,version,bright_t31,frp,daynight,type\n"
    "28.6139,77.2090,365.2,308.1,0.39,0.36,2026-08-25,0315,N,VIIRS,nominal,2.0NRT,300.4,42.1,N,0\n"
)


def _client_with_transport(handler) -> FIRMSClient:
    transport = httpx.MockTransport(handler)
    return FIRMSClient(map_key="TESTKEY", client=httpx.Client(transport=transport))


def test_fetch_nrt_builds_expected_url_and_parses_csv():
    requested_urls = []

    def handler(request: httpx.Request) -> httpx.Response:
        requested_urls.append(str(request.url))
        return httpx.Response(200, text=SAMPLE_CSV)

    client = _client_with_transport(handler)
    df = client.fetch_nrt(days=2)

    assert len(requested_urls) == 1
    assert f"/TESTKEY/VIIRS_SNPP_NRT/{INDIA_BBOX}/2" in requested_urls[0]
    assert len(df) == 1
    assert df.iloc[0]["latitude"] == 28.6139


def test_fetch_nrt_raises_on_http_error():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(403, text="Forbidden")

    client = _client_with_transport(handler)
    try:
        client.fetch_nrt(days=1)
        assert False, "expected an HTTPStatusError"
    except httpx.HTTPStatusError:
        pass


def test_fetch_archive_chunks_multi_year_range_and_rate_limits(monkeypatch):
    requested = []

    def handler(request: httpx.Request) -> httpx.Response:
        requested.append(str(request.url))
        return httpx.Response(200, text=SAMPLE_CSV)

    sleeps = []
    monkeypatch.setattr("workers.ingestion.firms_client.time.sleep", lambda s: sleeps.append(s))

    client = _client_with_transport(handler)
    df = client.fetch_archive(date(2026, 1, 1), date(2026, 1, 25))

    # 25 days -> three <=10-day chunks
    assert len(requested) == 3
    assert len(sleeps) == 2  # rate-limit pause between chunks, not after the last one
    assert len(df) == 3  # one sample row per chunk, concatenated
