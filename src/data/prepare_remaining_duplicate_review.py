
from pathlib import Path

import geopandas as gpd
import pandas as pd

PROJECT = Path(__file__).resolve().parents[2]

BASE = PROJECT / "data/processed/healthcare"

INVENTORY_FILE = BASE / "healthcare_inventory_preliminary.gpkg"
GROUP_FILE = BASE / "healthcare_duplicate_candidate_groups.csv"
PAIR_FILE = BASE / "healthcare_duplicate_review_enriched.csv"

SUMMARY_FILE = BASE / "remaining_duplicate_groups_summary.csv"
MEMBER_FILE = BASE / "remaining_duplicate_groups_members.csv"

# Already investigated groups
PRIORITY_GROUPS = {
    "DUP_G001",
    "DUP_G002",
    "DUP_G034"
}

print("Loading healthcare inventory...")

inventory = gpd.read_file(INVENTORY_FILE).set_index("source_key")
groups = pd.read_csv(GROUP_FILE)
pairs = pd.read_csv(PAIR_FILE)

# Exclude the three priority groups.
remaining = groups[
    ~groups["candidate_group_id"].isin(PRIORITY_GROUPS)
].copy()

summary_rows = []
member_rows = []

for group_id, members in remaining.groupby("candidate_group_id"):

    keys = set(members["source_key"])

    group_pairs = pairs[
        pairs["source_key_1"].isin(keys)
        & pairs["source_key_2"].isin(keys)
    ]

    names = []
    pair_evidence = []

    for _, pair in group_pairs.iterrows():
        pair_evidence.append(
            f"{pair['source_key_1']} <-> {pair['source_key_2']}"
            f" | {pair['geometry_relationship']}"
            f" | {pair['distance_m']} m"
        )

    for _, member in members.iterrows():

        key = member["source_key"]
        record = inventory.loc[key]

        if pd.notna(record["display_name"]):
            names.append(str(record["display_name"]))

        member_rows.append({
            "candidate_group_id": group_id,
            "source_key": key,
            "display_name": record["display_name"],
            "facility_category": record["facility_category"],
            "healthcare": record.get("healthcare"),
            "amenity": record.get("amenity"),
            "operator": record.get("operator"),
            "geometry_type": record.geometry.geom_type,
            "representative_lon": record["representative_lon"],
            "representative_lat": record["representative_lat"],
            "review_decision": "",
            "canonical_source_key": "",
            "review_notes": ""
        })

    summary_rows.append({
        "candidate_group_id": group_id,
        "number_of_records": len(members),
        "candidate_pairs": len(group_pairs),
        "facility_names": " | ".join(sorted(set(names))),
        "source_keys": " | ".join(sorted(keys)),
        "pair_evidence": " || ".join(pair_evidence),
        "group_review_decision": "",
        "review_notes": ""
    })

summary = pd.DataFrame(summary_rows)
member_df = pd.DataFrame(member_rows)

summary.to_csv(SUMMARY_FILE, index=False)
member_df.to_csv(MEMBER_FILE, index=False)

print("\n========== REMAINING DUPLICATE REVIEW ==========")

print("Groups:", len(summary))
print("Records:", len(member_df))
print("Candidate pairs:", summary["candidate_pairs"].sum())

print("\nGroup sizes:")
print(summary["number_of_records"].value_counts().sort_index())

print("\nGroups for inspection:")
print(
    summary[
        ["candidate_group_id", "number_of_records", "facility_names"]
    ].to_string(index=False)
)

print("\nSaved:")
print(SUMMARY_FILE)
print(MEMBER_FILE)

print("\nNo records were deleted or merged.")
