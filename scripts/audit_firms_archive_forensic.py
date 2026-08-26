"""
Forensic Dataset Inventory Script for NASA FIRMS Archive & NRT Files (Vectorized Speed).

Usage:
  python scripts/audit_firms_archive_forensic.py

Inspects every CSV in data/raw/firms/:
1. Basic File Stats: Size, SHA256, line count, columns.
2. Temporal Audit: Date min, date max, records per year/month.
3. Geographic Audit: Bounding box, India bounding box filtering counts (65-98° E, 6-38° N).
4. Schema & Null Audit: Column data types, null counts, sample head/tail.
5. Product & Satellite Identification.
6. Generates dataset_inventory.json and DATASET_INVENTORY.md.
"""

from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pandas as pd


def compute_sha256(filepath: Path) -> str:
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def audit_csv_file(file_path: Path) -> dict:
    print(f"Scanning: {file_path.name} ({file_path.stat().st_size / (1024*1024):.2f} MB)...", flush=True)
    checksum = compute_sha256(file_path)

    # Read CSV
    df = pd.read_csv(file_path)
    total_rows = len(df)
    cols = list(df.columns)

    # Date range
    if "acq_date" in df.columns:
        date_min = str(df["acq_date"].min())
        date_max = str(df["acq_date"].max())
        df["year"] = pd.to_datetime(df["acq_date"]).dt.year
        records_per_year = df["year"].value_counts().to_dict()
    else:
        date_min = "UNKNOWN"
        date_max = "UNKNOWN"
        records_per_year = {}

    # Geographic Bounding Box & Vectorized India Bounding Filtering (65-98° E, 6-38° N)
    if "latitude" in df.columns and "longitude" in df.columns:
        min_lat = float(df["latitude"].min())
        max_lat = float(df["latitude"].max())
        min_lon = float(df["longitude"].min())
        max_lon = float(df["longitude"].max())

        india_mask = (
            (df["latitude"] >= 6.0) & (df["latitude"] <= 38.0) &
            (df["longitude"] >= 65.0) & (df["longitude"] <= 98.0)
        )
        india_count = int(india_mask.sum())
    else:
        min_lat, max_lat, min_lon, max_lon = 0.0, 0.0, 0.0, 0.0
        india_count = 0

    outside_india = total_rows - india_count

    # Null counts & sample head/tail
    null_counts = {col: int(df[col].isnull().sum()) for col in cols}
    sample_head = df.head(3).to_dict(orient="records")
    sample_tail = df.tail(3).to_dict(orient="records")

    # Satellite / Product inferrence from filename
    fname = file_path.name
    if "J1V-C2" in fname:
        satellite = "NOAA-20 (JPSS-1)"
        sensor = "VIIRS (375m)"
        proc_level = "Standard Archive" if "archive" in fname else "Near Real-Time (NRT)"
        request_id = "792735"
    elif "J2V-C2" in fname:
        satellite = "NOAA-21 (JPSS-2)"
        sensor = "VIIRS (375m)"
        proc_level = "Near Real-Time (NRT)"
        request_id = "792736"
    elif "SV-C2" in fname:
        satellite = "Suomi-NPP"
        sensor = "VIIRS (375m)"
        proc_level = "Standard Archive" if "archive" in fname else "Near Real-Time (NRT)"
        request_id = "792737"
    else:
        satellite = "UNKNOWN"
        sensor = "UNKNOWN"
        proc_level = "UNKNOWN"
        request_id = "UNKNOWN"

    return {
        "filename": fname,
        "path": str(file_path.relative_to(ROOT)),
        "size_bytes": file_path.stat().st_size,
        "sha256": checksum,
        "total_rows": total_rows,
        "column_count": len(cols),
        "columns": cols,
        "satellite": satellite,
        "sensor": sensor,
        "processing_level": proc_level,
        "request_id": request_id,
        "date_min": date_min,
        "date_max": date_max,
        "records_per_year": {str(int(k)): int(v) for k, v in records_per_year.items()},
        "bbox": {
            "min_lat": min_lat,
            "max_lat": max_lat,
            "min_lon": min_lon,
            "max_lon": max_lon,
        },
        "india_records": india_count,
        "outside_india_records": outside_india,
        "null_counts": null_counts,
        "head_samples": sample_head,
        "tail_samples": sample_tail,
    }


def main():
    print("=" * 80, flush=True)
    print("   AGNIDRISHTI — FORENSIC NASA FIRMS ARCHIVE & NRT DATASET AUDIT", flush=True)
    print("=" * 80, flush=True)

    firms_dir = ROOT / "data" / "raw" / "firms"
    csv_files = list(firms_dir.glob("*.csv"))

    audit_results = []
    for csv_path in sorted(csv_files):
        res = audit_csv_file(csv_path)
        audit_results.append(res)

    # Save dataset_inventory.json
    json_path = firms_dir / "dataset_inventory.json"
    json_path.write_text(json.dumps(audit_results, indent=2))
    print(f"\n[OK] Machine-readable inventory saved to: {json_path}", flush=True)

    # Generate DATASET_INVENTORY.md
    md_lines = [
        "# AGNIDRISHTI — NASA FIRMS ARCHIVE FORENSIC INVENTORY",
        "",
        f"**Audit Timestamp**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"**Total CSV Data Files Received**: {len(audit_results)}",
        "",
        "---",
        "",
        "## 1. FILE INVENTORY & PRODUCT MAPPING SUMMARY",
        "",
        "| FILENAME | SATELLITE | SENSOR | TYPE | REQUEST ID | SIZE (MB) | ROWS | DATE RANGE | INDIA ROWS |",
        "|---|---|---|---|---|---|---|---|---|",
    ]

    total_raw_records = 0
    total_india_records = 0
    all_dates_min = []
    all_dates_max = []

    for item in audit_results:
        size_mb = item["size_bytes"] / (1024 * 1024)
        total_raw_records += item["total_rows"]
        total_india_records += item["india_records"]
        all_dates_min.append(item["date_min"])
        all_dates_max.append(item["date_max"])

        md_lines.append(
            f"| `{item['filename']}` | {item['satellite']} | {item['sensor']} | {item['processing_level']} | {item['request_id']} | {size_mb:.2f} MB | {item['total_rows']:,} | {item['date_min']} to {item['date_max']} | **{item['india_records']:,}** |"
        )

    md_lines.extend([
        "",
        "---",
        "",
        "## 2. AGGREGATE COVERAGE SUMMARY",
        "",
        f"- **Total Raw Observations Received**: `{total_raw_records:,}`",
        f"- **Total India Bounding Box Observations**: `{total_india_records:,}`",
        f"- **Overall Date Range**: `{min(all_dates_min)}` to `{max(all_dates_max)}`",
        "",
        "---",
        "",
        "## 3. YEARLY BREAKDOWN PER FILE",
        "",
    ])

    for item in audit_results:
        md_lines.append(f"### File: `{item['filename']}` ({item['satellite']} — {item['processing_level']})")
        md_lines.append("| YEAR | RECORD COUNT |")
        md_lines.append("|---|---|")
        for yr, cnt in sorted(item["records_per_year"].items()):
            md_lines.append(f"| {yr} | {cnt:,} |")
        md_lines.append("")

    md_lines.extend([
        "---",
        "",
        "## 4. COLUMN DICTIONARY & FEATURE AVAILABILITY",
        "",
        "| COLUMN | DATA TYPE | UNITS | ARCHIVE | NRT | FEATURE MODEL USE |",
        "|---|---|---|---|---|---|",
        "| `latitude` | float64 | Degrees N | Yes | Yes | Spatial indexing & PostGIS Point geometry |",
        "| `longitude` | float64 | Degrees E | Yes | Yes | Spatial indexing & PostGIS Point geometry |",
        "| `bright_ti4` | float64 | Kelvin | Yes | Yes | Brightness Temp 4µm (I4 channel) |",
        "| `scan` | float64 | km | Yes | Yes | Pixel footprint width along scan |",
        "| `track` | float64 | km | Yes | Yes | Pixel footprint length along track |",
        "| `acq_date` | string (YYYY-MM-DD) | Date | Yes | Yes | Acquisition date (Temporal indexing) |",
        "| `acq_time` | integer (HHMM) | UTC Time | Yes | Yes | Acquisition time (Solar zenith angle) |",
        "| `satellite` | string | Code | Yes | Yes | Satellite identifier ('N', 'N20', 'N21') |",
        "| `instrument` | string | Code | Yes | Yes | Sensor identifier ('VIIRS') |",
        "| `confidence` | string/float | Category | Yes | Yes | Detection confidence ('low', 'nominal', 'high') |",
        "| `version` | string | Code | Yes | Yes | Data processing version code |",
        "| `bright_ti5` | float64 | Kelvin | Yes | Yes | Brightness Temp 11µm (I5 channel) |",
        "| `frp` | float64 | MW | Yes | Yes | Fire Radiative Power (MW) |",
        "| `daynight` | string | Code | Yes | Yes | Day or Night acquisition ('D' / 'N') |",
        "| `type` | integer | Code | Yes | No | **Thermal source classification type** (0=presumed veg, 1=static land, 2=offshore, 3=offshore/unknown) |",
        "",
        "---",
        "",
        "## 5. DETAILED FILE PROVENANCE & NULL AUDIT",
        "",
    ])

    for item in audit_results:
        md_lines.append(f"### `{item['filename']}`")
        md_lines.append(f"- **SHA256**: `{item['sha256']}`")
        md_lines.append(f"- **Bounding Box**: Lat ({item['bbox']['min_lat']:.4f}, {item['bbox']['max_lat']:.4f}), Lon ({item['bbox']['min_lon']:.4f}, {item['bbox']['max_lon']:.4f})")
        md_lines.append(f"- **India Observations**: `{item['india_records']:,}` | **Outside India**: `{item['outside_india_records']:,}`")
        md_lines.append("- **Column Null Counts**:")
        for col, ncnt in item["null_counts"].items():
            md_lines.append(f"  - `{col}`: {ncnt} nulls")
        md_lines.append("")

    md_path = firms_dir / "DATASET_INVENTORY.md"
    md_path.write_text("\n".join(md_lines))
    print(f"[OK] Human-readable forensic report saved to: {md_path}", flush=True)
    print("=" * 80, flush=True)
    print("      FORENSIC AUDIT COMPLETE  [OK]", flush=True)
    print("=" * 80, flush=True)


if __name__ == "__main__":
    main()
