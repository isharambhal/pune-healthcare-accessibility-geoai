
from pathlib import Path

import geopandas as gpd
import pandas as pd

PROJECT = Path(__file__).resolve().parents[2]
BASE = PROJECT / "data/processed/healthcare"

INVENTORY = BASE / "healthcare_inventory_preliminary.gpkg"
CANDIDATES = BASE / "healthcare_duplicate_candidate_groups.csv"

GROUPS = BASE / "healthcare_all_duplicate_group_decisions.csv"
MEMBERS = BASE / "healthcare_all_duplicate_group_members.csv"

print("Loading datasets...")

inventory = gpd.read_file(INVENTORY)
candidates = pd.read_csv(CANDIDATES)
groups = pd.read_csv(GROUPS)
members = pd.read_csv(MEMBERS)

# Expected group membership from original candidate register.
expected = set(
    zip(
        candidates["candidate_group_id"],
        candidates["source_key"]
    )
)

actual = set(
    zip(
        members["candidate_group_id"],
        members["source_key"]
    )
)

original_keys = set(inventory["source_key"])
member_keys = set(members["source_key"])

print("\n========== REGISTER VALIDATION ==========")

checks = {
    "Expected candidate groups": 34,
    "Actual candidate groups": groups["candidate_group_id"].nunique(),
    "Expected member records": 70,
    "Actual member records": len(members),
    "Unique member OSM IDs": members["source_key"].nunique(),
    "Member records in original inventory": len(
        member_keys.intersection(original_keys)
    ),
    "Membership relationships matching source": len(
        actual.intersection(expected)
    ),
    "Expected membership relationships": len(expected)
}

for label, value in checks.items():
    print(f"{label}: {value}")

print("\n========== INTEGRITY CHECKS ==========")

print(
    "Missing membership relationships:",
    len(expected - actual)
)

print(
    "Unexpected membership relationships:",
    len(actual - expected)
)

print(
    "OSM IDs missing from original inventory:",
    sorted(member_keys - original_keys)
)

print(
    "Duplicate OSM IDs in member register:",
    members["source_key"].duplicated().sum()
)

print(
    "Groups with pending confirmation:",
    (groups["manual_confirmation"] == "pending").sum()
)

print(
    "Members retaining original records:",
    members["preserve_original_record"].sum()
)

# Fail if the register does not match its source.
assert len(groups) == 34
assert len(members) == 70
assert members["source_key"].nunique() == 70
assert expected == actual
assert member_keys.issubset(original_keys)
assert groups["candidate_group_id"].nunique() == 34

print("\nVALIDATION PASSED")
print("No source records were modified.")
