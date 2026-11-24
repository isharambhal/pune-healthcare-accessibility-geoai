
from pathlib import Path

import geopandas as gpd
import pandas as pd

PROJECT = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    PROJECT / "data/raw/healthcare/"
    "osm_healthcare_facilities.gpkg"
)

COVERAGE_FILE = (
    PROJECT / "data/processed/healthcare/"
    "healthcare_original_network_coverage.csv"
)

OUTPUT_DIR = PROJECT / "data/processed/healthcare"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_GPKG = OUTPUT_DIR / "healthcare_inventory_preliminary.gpkg"
OUTPUT_CSV = OUTPUT_DIR / "healthcare_inventory_preliminary.csv"
REVIEW_CSV = OUTPUT_DIR / "healthcare_review_required.csv"


# -------------------------------------------------
# 1. Load source data
# -------------------------------------------------

print("Loading original healthcare dataset...")

gdf = gpd.read_file(INPUT_FILE)

print("Original features:", len(gdf))


# -------------------------------------------------
# 2. Standardise facility names
# -------------------------------------------------

NAME_FIELDS = [
    "name",
    "name:en",
    "name:mr",
    "name:hi",
    "alt_name",
    "short_name",
    "short_name:en"
]


def first_available_name(row):

    for field in NAME_FIELDS:

        value = row.get(field)

        if pd.notna(value) and str(value).strip():
            return str(value).strip(), field

    return None, None


name_results = gdf.apply(first_available_name, axis=1)

gdf["display_name"] = name_results.apply(lambda x: x[0])
gdf["name_source"] = name_results.apply(lambda x: x[1])

gdf["name_missing_flag"] = gdf["display_name"].isna()


# -------------------------------------------------
# 3. Define transparent classification rules
# -------------------------------------------------

amenity_map = {
    "hospital": "hospital",
    "clinic": "clinic",
    "pharmacy": "pharmacy",
    "doctors": "doctor",
    "dentist": "dentist",
    "nursing_home": "nursing_home",
    "hospital;clinic": "mixed_clinic_hospital",
    "clinic;hospital": "mixed_clinic_hospital"
}

healthcare_map = {
    "hospital": "hospital",
    "clinic": "clinic",
    "pharmacy": "pharmacy",
    "doctor": "doctor",
    "dentist": "dentist",
    "laboratory": "diagnostic_service",
    "diagnostic_center": "diagnostic_service",
    "sample_collection": "diagnostic_service",
    "centre": "health_centre",
    "alternative": "alternative_care",
    "physiotherapist": "physiotherapy",
    "optometrist": "optometry",
    "hospice": "hospice",
    "chemist": "chemist",
    "psychotherapist": "mental_health_service",
    "counselling": "mental_health_service",
    "clinic;hospital": "mixed_clinic_hospital",
    "hospital;clinic": "mixed_clinic_hospital"
}


def clean_tag(value):

    if pd.isna(value):
        return None

    value = str(value).strip().lower()

    return value if value else None


def classify_facility(row):

    amenity = clean_tag(row.get("amenity"))
    healthcare = clean_tag(row.get("healthcare"))

    amenity_class = amenity_map.get(amenity)
    healthcare_class = healthcare_map.get(healthcare)

    # Both tags provide different classifications.
    if amenity_class and healthcare_class:

        if amenity_class != healthcare_class:
            return "review_tag_conflict", "review_tag_conflict"

        if amenity_class == "mixed_clinic_hospital":
            return amenity_class, "review_mixed_category"

        return amenity_class, "classified_from_both_tags"

    # A mixed category requires manual confirmation.
    if amenity_class == "mixed_clinic_hospital":
        return amenity_class, "review_mixed_category"

    if healthcare_class == "mixed_clinic_hospital":
        return healthcare_class, "review_mixed_category"

    # Use the available specific classification.
    if amenity_class:
        return amenity_class, "classified_from_amenity"

    if healthcare_class:
        return healthcare_class, "classified_from_healthcare"

    # Generic or unknown tags need review.
    if amenity == "yes" or healthcare == "yes":
        return "unspecified_healthcare", "review_generic_yes_tag"

    if healthcare:
        return "unmapped_healthcare_value", "review_unmapped_healthcare"

    if amenity:
        return "unmapped_amenity_value", "review_unmapped_amenity"

    return "unclassified", "review_unclassified"


classification = gdf.apply(classify_facility, axis=1)

gdf["facility_category"] = classification.apply(lambda x: x[0])
gdf["classification_status"] = classification.apply(lambda x: x[1])


# -------------------------------------------------
# 4. Add stable source identifiers
# -------------------------------------------------

gdf["source_key"] = (
    gdf["element"].astype(str)
    + "/"
    + gdf["id"].astype(str)
)

gdf["geometry_type"] = gdf.geometry.geom_type


# -------------------------------------------------
# 5. Calculate representative coordinates
# -------------------------------------------------

print("Calculating representative coordinates...")

representative_points = (
    gpd.GeoSeries(gdf.geometry, crs=gdf.crs)
    .to_crs("EPSG:32643")
    .representative_point()
    .to_crs("EPSG:4326")
)

gdf["representative_lon"] = representative_points.x.values
gdf["representative_lat"] = representative_points.y.values


# -------------------------------------------------
# 6. Attach nearest original road-edge distances
# -------------------------------------------------

coverage = pd.read_csv(COVERAGE_FILE)

coverage["source_key"] = (
    coverage["element"].astype(str)
    + "/"
    + coverage["id"].astype(str)
)

distance_lookup = coverage.set_index(
    "source_key"
)["nearest_original_edge_distance_m"]

gdf["nearest_road_edge_distance_m"] = (
    gdf["source_key"].map(distance_lookup)
)


# -------------------------------------------------
# 7. Flag records for manual review
# -------------------------------------------------

review_reasons = []

for _, row in gdf.iterrows():

    reasons = []

    if row["name_missing_flag"]:
        reasons.append("missing_name")

    if str(row["classification_status"]).startswith("review"):
        reasons.append(row["classification_status"])

    if row["geometry_type"] != "Point":
        reasons.append("non_point_geometry_check")

    review_reasons.append("; ".join(reasons))


gdf["review_reasons"] = review_reasons

gdf["needs_review"] = gdf["review_reasons"] != ""


# -------------------------------------------------
# 8. Save preliminary inventory
# -------------------------------------------------

print("Saving preliminary inventory...")

# Remove only previously generated output files.
for output in [OUTPUT_GPKG]:
    if output.exists():
        output.unlink()

gdf.to_file(
    OUTPUT_GPKG,
    driver="GPKG"
)

gdf.drop(columns="geometry").to_csv(
    OUTPUT_CSV,
    index=False
)

gdf.loc[gdf["needs_review"]].drop(
    columns="geometry"
).to_csv(
    REVIEW_CSV,
    index=False
)


# -------------------------------------------------
# 9. Print summary
# -------------------------------------------------

print("\n========== INVENTORY SUMMARY ==========")

print("Total features:", len(gdf))

print("\nFacility categories:")
print(gdf["facility_category"].value_counts())

print("\nClassification status:")
print(gdf["classification_status"].value_counts())

print("\nMissing names:", gdf["name_missing_flag"].sum())

print("Records requiring review:", gdf["needs_review"].sum())

print("\nGeometry types:")
print(gdf["geometry_type"].value_counts())

print("\nOutput files:")
print(OUTPUT_GPKG)
print(OUTPUT_CSV)
print(REVIEW_CSV)

print("\nInventory preparation completed.")
