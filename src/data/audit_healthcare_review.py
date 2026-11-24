
from pathlib import Path
import geopandas as gpd
import pandas as pd

PROJECT = Path(__file__).resolve().parents[2]

FILE = (
    PROJECT / "data/processed/healthcare/"
    "healthcare_inventory_preliminary.gpkg"
)

gdf = gpd.read_file(FILE)

print("\n========== REVIEW AUDIT ==========")

print("Total records:", len(gdf))
print("Records needing review:", gdf["needs_review"].sum())

# Count individual review reasons.
reasons = (
    gdf.loc[gdf["needs_review"], "review_reasons"]
    .str.split("; ")
    .explode()
)

print("\nReview reason counts:")
print(reasons.value_counts())

# Inspect classification conflicts.
conflicts = gdf[
    gdf["classification_status"] == "review_tag_conflict"
]

print("\n========== TAG CONFLICTS ==========")

columns = [
    "element", "id", "display_name",
    "healthcare", "amenity", "facility_category"
]

print(conflicts[columns].to_string(index=False))

# Inspect non-point geometries.
non_points = gdf[gdf["geometry_type"] != "Point"]

print("\n========== NON-POINT FEATURES ==========")

columns = [
    "element", "id", "display_name",
    "healthcare", "amenity",
    "geometry_type", "facility_category"
]

print(non_points[columns].to_string(index=False))

print("\n========== AUDIT COMPLETE ==========")
