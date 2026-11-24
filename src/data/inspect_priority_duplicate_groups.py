
from pathlib import Path

import geopandas as gpd
import pandas as pd

PROJECT = Path(__file__).resolve().parents[2]

BASE = PROJECT / "data/processed/healthcare"

INVENTORY_FILE = BASE / "healthcare_inventory_preliminary.gpkg"
GROUP_FILE = BASE / "healthcare_duplicate_candidate_groups.csv"
PAIR_FILE = BASE / "healthcare_duplicate_review_enriched.csv"

inventory = gpd.read_file(INVENTORY_FILE)
groups = pd.read_csv(GROUP_FILE)
pairs = pd.read_csv(PAIR_FILE)

inventory = inventory.set_index("source_key")

# Calculate geometry areas in square metres.
inventory_projected = (
    gpd.read_file(INVENTORY_FILE)
    .to_crs("EPSG:32643")
    .set_index("source_key")
)

priority_groups = ["DUP_G001", "DUP_G002", "DUP_G034"]

for group_id in priority_groups:

    print("\n" + "=" * 65)
    print("GROUP:", group_id)
    print("=" * 65)

    members = groups[
        groups["candidate_group_id"] == group_id
    ]

    for _, member in members.iterrows():

        key = member["source_key"]
        record = inventory.loc[key]
        projected = inventory_projected.loc[key]

        geometry = record.geometry
        representative = geometry.representative_point()

        area = (
            projected.geometry.area
            if geometry.geom_type in ["Polygon", "MultiPolygon"]
            else None
        )

        print("\nOSM ID:", key)
        print("Name:", record["display_name"])
        print("Healthcare:", record.get("healthcare"))
        print("Amenity:", record.get("amenity"))
        print("Speciality:", record.get("healthcare:speciality"))
        print("Operator:", record.get("operator"))
        print("Geometry:", geometry.geom_type)
        print(
            "Representative coordinates:",
            round(representative.x, 7),
            round(representative.y, 7)
        )

        if area is not None:
            print("Polygon area (m²):", round(area, 2))

    print("\nPAIR RELATIONSHIPS:")

    keys = set(members["source_key"])

    selected = pairs[
        pairs["source_key_1"].isin(keys)
        & pairs["source_key_2"].isin(keys)
    ]

    columns = [
        "source_key_1",
        "source_key_2",
        "geometry_relationship",
        "distance_m",
        "polygon_overlap_ratio"
    ]

    print(selected[columns].to_string(index=False))

print("\nPriority group inspection completed.")
