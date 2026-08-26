# AGNIDRISHTI — NASA FIRMS PRODUCT RECONCILIATION REPORT

---

## 1. Product Classification & Version Analysis

| NASA FILENAME | SATELLITE | SENSOR | PROCESSING LEVEL | VERSION HEADER | DATE RANGE | RECONCILIATION DETERMINATION |
|---|---|---|---|---|---|---|
| `fire_archive_J1V-C2_792735.csv` | NOAA-20 (JPSS-1) | VIIRS 375m | **Standard Archive** | `2` | 2020-01-01 to 2026-05-31 | Standard quality science product (VNP14IMGTML) processed with 3-month lag by UMD/FIRMS. |
| `fire_archive_SV-C2_792737.csv` | Suomi-NPP | VIIRS 375m | **Standard Archive** | `2` | 2020-01-01 to 2026-04-27 | Standard quality science product (VNP14IMGTML) processed with 3-month lag by UMD/FIRMS. |
| `fire_nrt_J2V-C2_792736.csv` | NOAA-21 (JPSS-2) | VIIRS 375m | **Near Real-Time (NRT)** | `2.0NRT` | 2024-01-17 to 2026-08-26 | NRT product (VJ214IMGDL) processed by LANCE/FIRMS for newer satellite. |
| `fire_nrt_SV-C2_792737.csv` | Suomi-NPP | VIIRS 375m | **Near Real-Time (NRT)** | `2.0NRT` | 2026-04-30 to 2026-08-26 | NRT fallback covering recent 3 months prior to standard archive release. |
| `fire_nrt_J1V-C2_792735.csv` | NOAA-20 (JPSS-1) | VIIRS 375m | **Near Real-Time (NRT)** | `2.0NRT` | 2026-06-01 to 2026-08-26 | NRT fallback covering recent 3 months prior to standard archive release. |

---

## 2. Technical Justification of NRT vs. Standard Quality

1. **Standard Archive Processing (`version == 2`)**:
   * Uses refined post-pass satellite orbital ephemeris and University of Maryland science calibration.
   * Includes the `type` field (0=presumed vegetation fire, 1=active static land source, 2=offshore, 3=offshore/unknown).

2. **Near Real-Time Processing (`version == '2.0NRT'`)**:
   * Produced by LANCE / FIRMS within 3 hours of satellite overpass using real-time predictive orbits.
   * The `type` field is absent in NRT products.

3. **Deduplication Precedence Rule**:
   * When an observation with identical `(latitude, longitude, acq_date, acq_time, satellite)` exists in both Standard Archive and NRT files, **the Standard Archive record (`version == 2`) is retained**, and the NRT record is marked as superseded.
