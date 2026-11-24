
from pathlib import Path

import geopandas as gpd
import networkx as nx
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

OUTPUT_DIR = PROJECT / "data/processed/healthcare"

GROUP_FILE = OUTPUT_DIR / "healthcare_duplicate_candidate_groups.csv"
SUMMARY_FILE = OUTPUT_DIR / "healthcare_duplicate_group_summary.csv"

print("Loading candidate pairs and healthcare inventory...")

gdf = gpd.read_file(INVENTORY_FILE)
candidates = pd.read_csv(CANDIDATE_FILE)

# Build a graph of related OSM records.
G = nx.Graph()

for _, row in candidates.iterrows():
    G.add_edge(
        row["source_key_1"],
        row["source_key_2"]
    )

# Find connected groups of candidate records.
components = sorted(
    nx.connected_components(G),
    key=lambda component: (-len(component), sorted(component)[0])
)

inventory = gdf.set_index("source_key")

group_rows = []
summary_rows = []

for number, component in enumerate(components, start=1):

    group_id = f"DUP_G{number:03d}"

    members = sorted(component)

    internal_edges = [
        (u, v)
        for u, v in G.edges
        if u in component and v in component
    ]

    names = []

    for key in members:

        record = inventory.loc[key]

        name = record["display_name"]

        if pd.notna(name):
            names.append(str(name))

        group_rows.append({
            "candidate_group_id": group_id,
            "source_key": key,
            "display_name": name,
            "facility_category": record["facility_category"],
            "healthcare": record.get("healthcare"),
            "amenity": record.get("amenity"),
            "geometry_type": record.geometry.geom_type,
            "review_decision": "pending_manual_review",
            "canonical_source_key": "",
            "review_notes": ""
        })

    summary_rows.append({
        "candidate_group_id": group_id,
        "number_of_records": len(members),
        "number_of_candidate_pairs": len(internal_edges),
        "facility_names": " | ".join(sorted(set(names))),
        "source_keys": " | ".join(members),
        "review_status": "pending_manual_review"
    })

groups = pd.DataFrame(group_rows)
summary = pd.DataFrame(summary_rows)

groups.to_csv(GROUP_FILE, index=False)
summary.to_csv(SUMMARY_FILE, index=False)

print("\n========== DUPLICATE GROUP SUMMARY ==========")

print("Candidate pairs:", len(candidates))
print("Candidate groups:", len(components))
print("Unique records involved:", len(G.nodes))

print("\nGroup sizes:")
print(summary["number_of_records"].value_counts().sort_index())

print("\nLargest candidate groups:")
print(
    summary.head(15).to_string(index=False)
)

print("\nSaved files:")
print(GROUP_FILE)
print(SUMMARY_FILE)

print("\nNo records were deleted or merged.")
