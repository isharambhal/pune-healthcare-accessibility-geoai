
from pathlib import Path
import re
import unicodedata

import geopandas as gpd
import pandas as pd

PROJECT = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    PROJECT / "data/processed/healthcare/"
    "healthcare_inventory_preliminary.gpkg"
)

OUTPUT_DIR = PROJECT / "data/processed/healthcare"
OUTPUT_FILE = OUTPUT_DIR / "healthcare_duplicate_candidates.csv"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

print("Loading preliminary healthcare inventory...")
gdf = gpd.read_file(INPUT_FILE)

# Project geometries into metres.
gdf = gdf.to_crs("EPSG:32643")


def normalize_name(value):
    if pd.isna(value):
        return ""

    value = unicodedata.normalize("NFKC", str(value))
    value = value.casefold()
    value = re.sub(r"[^\w\s]", " ", value)
    value = re.sub(r"\s+", " ", value).strip()

    return value


def get_names(row):
    fields = [
        "display_name",
        "alt_name",
        "alt_name:en",
        "short_name",
        "short_name:en"
    ]

    return {
        normalize_name(row.get(field))
        for field in fields
        if normalize_name(row.get(field))
    }


print("Preparing name comparisons...")

gdf["comparison_names"] = gdf.apply(get_names, axis=1)

spatial_index = gdf.sindex

candidates = []
seen_pairs = set()

print("Searching for nearby matching facilities...")

for i, geom in enumerate(gdf.geometry):

    possible = spatial_index.query(geom.buffer(30))

    for j in possible:

        j = int(j)

        if j <= i:
            continue

        names_i = gdf.iloc[i]["comparison_names"]
        names_j = gdf.iloc[j]["comparison_names"]

        common_names = names_i.intersection(names_j)

        if not common_names:
            continue

        distance = geom.distance(gdf.geometry.iloc[j])

        if distance > 30:
            continue

        pair = (i, j)

        if pair in seen_pairs:
            continue

        seen_pairs.add(pair)

        first = gdf.iloc[i]
        second = gdf.iloc[j]

        candidates.append({
            "source_key_1": first["source_key"],
            "source_key_2": second["source_key"],
            "name_1": first["display_name"],
            "name_2": second["display_name"],
            "category_1": first["facility_category"],
            "category_2": second["facility_category"],
            "geometry_1": first["geometry_type"],
            "geometry_2": second["geometry_type"],
            "common_name": "; ".join(sorted(common_names)),
            "distance_m": round(distance, 2),
            "review_status": "requires_manual_review"
        })

    if (i + 1) % 200 == 0:
        print(f"Checked {i + 1}/{len(gdf)} features")


result = pd.DataFrame(candidates)

result.to_csv(OUTPUT_FILE, index=False)

print("\n========== DUPLICATE CANDIDATE AUDIT ==========")

print("Total source features:", len(gdf))
print("Possible duplicate pairs:", len(result))

if not result.empty:
    print("\nClosest candidate pairs:")
    print(
        result.sort_values("distance_m")
        .head(20)
        .to_string(index=False)
    )
else:
    print("No matching-name pairs found within 30 metres.")

print("\nSaved:", OUTPUT_FILE)
print("\nNo records have been deleted or merged.")
