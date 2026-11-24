from pathlib import Path

import geopandas as gpd
import pandas as pd
import osmnx as ox

PROJECT = Path(__file__).resolve().parents[2]

HEALTHCARE_FILE = (
    PROJECT / "data/raw/healthcare/osm_healthcare_facilities.gpkg"
)

ROAD_GRAPH = (
    PROJECT / "data/processed/roads/"
    "pmc_roads_largest_component.graphml"
)

OUTPUT_DIR = PROJECT / "data/processed/healthcare"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = OUTPUT_DIR / "healthcare_road_coverage.csv"

print("Loading healthcare facilities...")
healthcare = gpd.read_file(HEALTHCARE_FILE)

print("Loading processed road network...")
G = ox.io.load_graphml(ROAD_GRAPH)

# Convert healthcare geometries to representative points.
# This allows polygon and line features to be checked too.
healthcare = healthcare.to_crs("EPSG:32643")
healthcare["check_point"] = healthcare.geometry.representative_point()

# Create a GeoDataFrame containing the representative points.
points = gpd.GeoDataFrame(
    healthcare.drop(columns="geometry"),
    geometry="check_point",
    crs="EPSG:32643"
)

# Convert points to geographic coordinates for OSMnx.
points = points.to_crs("EPSG:4326")

print("Checking nearest road nodes...")

distances = []
nearest_nodes = []

for point in points.geometry:
    node, distance = ox.distance.nearest_nodes(
        G,
        X=point.x,
        Y=point.y,
        return_dist=True
    )

    nearest_nodes.append(node)
    distances.append(distance)

healthcare["nearest_road_node"] = nearest_nodes
healthcare["nearest_road_distance_m"] = distances

# Categorise distances for inspection.
healthcare["road_distance_category"] = pd.cut(
    healthcare["nearest_road_distance_m"],
    bins=[-1, 100, 250, 500, float("inf")],
    labels=[
        "Within 100 m",
        "100–250 m",
        "250–500 m",
        "Over 500 m"
    ]
)

healthcare.drop(columns="check_point").to_csv(
    OUTPUT_FILE,
    index=False
)

print("\n========== HEALTHCARE ROAD COVERAGE ==========")

print("Total healthcare features:", len(healthcare))

print("\nDistance categories:")
print(
    healthcare["road_distance_category"]
    .value_counts()
    .sort_index()
)

print("\nMedian distance (m):",
      round(healthcare["nearest_road_distance_m"].median(), 2))

print("Maximum distance (m):",
      round(healthcare["nearest_road_distance_m"].max(), 2))

print("\nSaved results:")
print(OUTPUT_FILE)