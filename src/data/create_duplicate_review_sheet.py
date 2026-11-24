
from pathlib import Path

import geopandas as gpd
import pandas as pd

PROJECT = Path(__file__).resolve().parents[2]

INVENTORY_FILE = (
    PROJECT / "data/processed/healthcare/"
    "healthcare_inventory_preliminary.gpkg"
)

CANDIDATE_FILE = (
    PROJECT / "data/processed/healthcare/"
    "healthcare_duplicate_review_enriched.csv"
)

OUTPUT_FILE = (
    PROJECT / "data/processed/healthcare/"
    "healthcare_duplicate_manual_review.csv"
)

gdf = gpd.read_file(INVENTORY_FILE)
candidates = pd.read_csv(CANDIDATE_FILE)

inventory = gdf.set_index("source_key")


def attributes_for(source_key, suffix):

    row = inventory.loc[source_key]

    return {
        f"name_{suffix}": row.get("display_name"),
        f"category_{suffix}": row.get("facility_category"),
        f"healthcare_{suffix}": row.get("healthcare"),
        f"amenity_{suffix}": row.get("amenity"),
        f"speciality_{suffix}": row.get("healthcare:speciality"),
        f"operator_{suffix}": row.get("operator"),
        f"address_{suffix}": row.get("addr:full"),
        f"geometry_{suffix}": row.geometry.geom_type
    }


def suggestion(relationship):

    if relationship == "point_inside_polygon":
        return "Check whether point and polygon represent the same facility"

    if relationship == "point_on_polygon_boundary":
        return "Inspect point and polygon relationship"

    if relationship in [
        "nearby_points",
        "nearly_coincident_points"
    ]:
        return "Check whether records represent the same facility"

    if relationship == "overlapping_polygons":
        return "Compare polygon boundaries and facility identities"

    return "Manual inspection required"


rows = []

for _, candidate in candidates.iterrows():

    key1 = candidate["source_key_1"]
    key2 = candidate["source_key_2"]

    row = candidate.to_dict()

    row.update(attributes_for(key1, "1"))
    row.update(attributes_for(key2, "2"))

    row["suggested_review_action"] = suggestion(
        candidate["geometry_relationship"]
    )

    # Complete these fields only after manual inspection.
    row["review_decision"] = ""
    row["canonical_source_key"] = ""
    row["review_notes"] = ""

    rows.append(row)

review = pd.DataFrame(rows)

review.to_csv(OUTPUT_FILE, index=False)

print("\n========== MANUAL REVIEW SHEET ==========")
print("Candidate pairs:", len(review))

print("\nGeometry relationships:")
print(review["geometry_relationship"].value_counts())

print("\nReview decision fields created:")
print("review_decision")
print("canonical_source_key")
print("review_notes")

print("\nSaved:", OUTPUT_FILE)
print("\nNo healthcare records were deleted or merged.")
