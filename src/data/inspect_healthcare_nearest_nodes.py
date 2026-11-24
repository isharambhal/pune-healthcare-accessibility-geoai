
from pathlib import Path

import geopandas as gpd
import pandas as pd
import osmnx as ox

PROJECT = Path(__file__).resolve().parents[2]

HEALTHCARE_FILE = (
    PROJECT / "data/raw/healthcare/osm_healthcare_facilities.gpkg"
)

COVERAGE_FILE = (
    PROJECT / "data/processed/healthcare/"
    "healthcare_road_coverage.csv"
)

GRAPH_FILE = (
    PROJECT / "data/processed/roads/"
    "pmc_roads_largest_component.graphml"
)

healthcare = gpd.read_file(HEALTHCARE_FILE)
coverage = pd.read_csv(COVERAGE_FILE)
G = ox.io.load_graphml(GRAPH_FILE)

distant = coverage[
    coverage["nearest_road_distance_m"] > 250
]

print("\n========== NEAREST ROAD NODE DETAILS ==========")

for _, record in distant.iterrows():

    facility = healthcare[
        (healthcare["element"] == record["element"]) &
        (healthcare["id"].astype(str) == str(record["id"]))
    ].iloc[0]

    # Use a representative point for consistent comparison.
    point = gpd.GeoSeries(
        [facility.geometry], crs=healthcare.crs
    ).to_crs("EPSG:32643").representative_point().iloc[0]

    point = gpd.GeoSeries(
        [point], crs="EPSG:32643"
    ).to_crs("EPSG:4326").iloc[0]

    node_id = record["nearest_road_node"]
    node = G.nodes[node_id]

    print("\nFacility:", facility.get("name"))
    print("OSM ID:", record["id"])
    print("Facility coordinates:", point.x, point.y)
    print("Nearest road node:", node_id)
    print("Road node coordinates:", node["x"], node["y"])
    print(
        "Distance (m):",
        round(record["nearest_road_distance_m"], 2)
    )

print("\nInspection complete.")