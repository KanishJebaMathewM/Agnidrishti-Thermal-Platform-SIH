# Canonical ordered list of feature columns for model input.
# The model must always see features in this exact order.
# NEVER reorder this list. Append new features at the end with a version bump.

FEATURE_COLUMNS_V1 = [
    "frp",
    "bright_ti4",
    "bright_ti5",
    "temp_diff_ti4_ti5",
    "confidence_encoded",
    "hour_of_day",
    "day_of_week",
    "month",
    "is_night",
    "season",
    "has_baseline",
    "frp_deviation",
    "frp_zscore",
    "nearest_industrial_dist_km",
    "is_forest",
    "land_use_encoded",
    "source_exists",
]

CLASS_LABELS = [
    "Industrial Incident",
    "Persistent Flare/Kiln",
    "Agricultural Burn",
    "Forest Fire",
    "Unknown",
]

CLASS_TO_IDX = {c: i for i, c in enumerate(CLASS_LABELS)}
IDX_TO_CLASS = {i: c for i, c in enumerate(CLASS_LABELS)}
