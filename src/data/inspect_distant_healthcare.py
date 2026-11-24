
from pathlib import Path

import geopandas as gpd
import pandas as pd

PROJECT = Path(__file__).resolve().parents[2]

HEALTHCARE_FILE = (
    PROJECT / "data/raw/healthcare/osm_healthcare_facilities.gpkg"
)

COVERAGE_FILE = (
    PROJECT / "data/processed/healthcare/"
    "healthcare_road_coverage.csv"
)

healthcare = gpd.read_file(HEALTHCARE_FILE)
coverage = pd.read_csv(COVERAGE_FILE)

# Select features more than 250 metres from the nearest road node.
distant = coverage[
    coverage["nearest_road_distance_m"] > 250
].copy()

# Match original records using OSM element and ID.
healthcare["id"] = healthcare["id"].astype(str)
distant["id"] = distant["id"].astype(str)

print("\n========== DISTANT FACILITY DETAILS ==========")

for _, record in distant.iterrows():

    match = healthcare[
        (healthcare["element"] == record["element"]) &
        (healthcare["id"] == record["id"])
    ]

    if match.empty:
        print("\nRecord not found:", record["id"])
        continue

    facility = match.iloc[0]
    geometry = facility.geometry

    print("\nName:", facility.get("name"))
    print("OSM element:", record["element"])
    print("OSM ID:", record["id"])
    print("Geometry type:", geometry.geom_type)

    print(
        "Distance to road node:",
        round(record["nearest_road_distance_m"], 2),
        "m"
    )

    print("Facility bounds:", geometry.bounds)
    print("Healthcare tag:", facility.get("healthcare"))
    print("Amenity tag:", facility.get("amenity"))

print("\nInspection complete.")