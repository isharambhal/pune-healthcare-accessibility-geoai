
from pathlib import Path

import geopandas as gpd
import pandas as pd
import osmnx as ox

PROJECT = Path(__file__).resolve().parents[2]

HEALTHCARE_FILE = (
    PROJECT / "data/raw/healthcare/"
    "osm_healthcare_facilities.gpkg"
)

GRAPH_FILE = (
    PROJECT / "data/raw/roads/"
    "pmc_roads_drive.graphml"
)

OUTPUT_DIR = PROJECT / "data/processed/healthcare"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = (
    OUTPUT_DIR / "healthcare_original_network_coverage.csv"
)

print("Loading healthcare facilities...")
healthcare = gpd.read_file(HEALTHCARE_FILE)

print("Loading complete road network...")
G = ox.io.load_graphml(GRAPH_FILE)

print("Converting roads into a spatial GeoDataFrame...")
edges = ox.graph_to_gdfs(
    G,
    nodes=False,
    edges=True
)

# Project both datasets to metres.
edges = edges.to_crs("EPSG:32643")

points = healthcare.copy()
points = points.set_geometry(
    points.geometry.representative_point()
)
points = points.to_crs("EPSG:32643")

print("Building spatial index...")
spatial_index = edges.sindex

distances = []

print("Checking healthcare locations...")

for i, point in enumerate(points.geometry):

    # Query nearby edges using the spatial index.
    nearest_position = spatial_index.nearest(
        point,
        return_all=False
    )

    edge_position = int(nearest_position[1][0])

    nearest_edge = edges.geometry.iloc[edge_position]

    distances.append(point.distance(nearest_edge))

    if (i + 1) % 200 == 0:
        print(f"Processed {i + 1}/{len(points)} facilities")

healthcare["nearest_original_edge_distance_m"] = distances

healthcare["distance_category"] = pd.cut(
    distances,
    bins=[-1, 100, 250, 500, float("inf")],
    labels=[
        "Within 100 m",
        "100–250 m",
        "250–500 m",
        "Over 500 m"
    ]
)

healthcare.to_csv(OUTPUT_FILE, index=False)

print("\n========== ORIGINAL NETWORK COVERAGE ==========")
print("Total healthcare features:", len(healthcare))
print(healthcare["distance_category"].value_counts().sort_index())

print(
    "\nMedian distance (m):",
    round(healthcare["nearest_original_edge_distance_m"].median(), 2)
)

print(
    "Maximum distance (m):",
    round(healthcare["nearest_original_edge_distance_m"].max(), 2)
)

print("\nSaved:", OUTPUT_FILE)
