
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
    "healthcare_duplicate_candidates.csv"
)

OUTPUT_FILE = (
    PROJECT / "data/processed/healthcare/"
    "healthcare_duplicate_review_enriched.csv"
)

print("Loading inventory and duplicate candidates...")

gdf = gpd.read_file(INVENTORY_FILE).to_crs("EPSG:32643")
candidates = pd.read_csv(CANDIDATE_FILE)

inventory = gdf.set_index("source_key")

results = []


def describe_relationship(g1, g2):

    distance = g1.distance(g2)

    if g1.geom_type == "Point" and g2.geom_type in [
        "Polygon", "MultiPolygon"
    ]:
        if g2.contains(g1):
            return "point_inside_polygon"
        if g2.touches(g1):
            return "point_on_polygon_boundary"

    if g2.geom_type == "Point" and g1.geom_type in [
        "Polygon", "MultiPolygon"
    ]:
        if g1.contains(g2):
            return "point_inside_polygon"
        if g1.touches(g2):
            return "point_on_polygon_boundary"

    if g1.geom_type == "Point" and g2.geom_type == "Point":
        return "nearly_coincident_points" if distance < 1 else "nearby_points"

    if g1.geom_type in ["Polygon", "MultiPolygon"] and \
       g2.geom_type in ["Polygon", "MultiPolygon"]:

        if g1.equals(g2):
            return "identical_polygons"

        if g1.intersects(g2):
            return "overlapping_polygons"

    if g1.intersects(g2):
        return "intersecting_geometries"

    return "nearby_non_intersecting_geometries"


print("Inspecting geometry relationships...")

for _, pair in candidates.iterrows():

    key1 = pair["source_key_1"]
    key2 = pair["source_key_2"]

    a = inventory.loc[key1]
    b = inventory.loc[key2]

    g1 = a.geometry
    g2 = b.geometry

    relationship = describe_relationship(g1, g2)
    distance = g1.distance(g2)

    intersection_area = None
    overlap_ratio = None

    if g1.geom_type in ["Polygon", "MultiPolygon"] and \
       g2.geom_type in ["Polygon", "MultiPolygon"]:

        intersection_area = g1.intersection(g2).area
        union_area = g1.union(g2).area

        if union_area > 0:
            overlap_ratio = intersection_area / union_area

    results.append({
        "source_key_1": key1,
        "source_key_2": key2,

        "name_1": a["display_name"],
        "name_2": b["display_name"],

        "category_1": a["facility_category"],
        "category_2": b["facility_category"],

        "healthcare_1": a["healthcare"],
        "healthcare_2": b["healthcare"],

        "amenity_1": a["amenity"],
        "amenity_2": b["amenity"],

        "geometry_1": g1.geom_type,
        "geometry_2": g2.geom_type,

        "geometry_relationship": relationship,
        "distance_m": round(distance, 2),

        "intersection_area_m2": intersection_area,
        "polygon_overlap_ratio": overlap_ratio,

        "review_decision": "pending_manual_review"
    })


result = pd.DataFrame(results)

result.to_csv(OUTPUT_FILE, index=False)

print("\n========== ENRICHED DUPLICATE AUDIT ==========")

print("Candidate pairs:", len(result))

print("\nGeometry relationships:")
print(result["geometry_relationship"].value_counts())

print("\nAll candidate pairs:")

display_columns = [
    "source_key_1",
    "source_key_2",
    "name_1",
    "name_2",
    "geometry_relationship",
    "distance_m",
    "polygon_overlap_ratio"
]

print(result[display_columns].to_string(index=False))

print("\nSaved:", OUTPUT_FILE)
print("\nNo source records were deleted or merged.")
