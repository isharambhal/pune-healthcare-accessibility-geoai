
from pathlib import Path
import pandas as pd

PROJECT = Path(__file__).resolve().parents[2]

OUTPUT_DIR = PROJECT / "data/processed/healthcare"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

GROUP_OUTPUT = (
    OUTPUT_DIR / "healthcare_priority_group_decisions.csv"
)

MEMBER_OUTPUT = (
    OUTPUT_DIR / "healthcare_priority_group_members.csv"
)

# Group-level decisions
groups = [
    {
        "candidate_group_id": "DUP_G001",
        "facility_group_id": "SITE_CANDIDATE_001",
        "facility_name": "Ruby Hall Clinic",
        "proposed_interpretation": "multi_service_healthcare_complex",
        "canonical_source_key": "way/53098668",
        "confidence": "medium",
        "decision_rationale": (
            "Both service points lie inside the same facility polygon. "
            "Points are 86.73 m apart and have different classifications. "
            "Preserve hospital and clinic service records separately."
        ),
        "decision_status": "provisional_not_applied"
    },
    {
        "candidate_group_id": "DUP_G002",
        "facility_group_id": "SITE_CANDIDATE_002",
        "facility_name": "Shinde Hospitals",
        "proposed_interpretation": "single_hospital_candidate",
        "canonical_source_key": "node/10219198235",
        "confidence": "high",
        "decision_rationale": (
            "Three similarly named hospital points have matching "
            "classifications and are within 12.76 m. The selected "
            "point has the lowest total distance to the other two."
        ),
        "decision_status": "provisional_not_applied"
    },
    {
        "candidate_group_id": "DUP_G034",
        "facility_group_id": "SITE_CANDIDATE_003",
        "facility_name": "Jupiter Hospital",
        "proposed_interpretation": "hospital_with_nested_emergency_feature",
        "canonical_source_key": "way/1410820103",
        "confidence": "high",
        "decision_rationale": (
            "The smaller emergency-related polygon is completely "
            "contained within the larger hospital polygon. "
            "Preserve the emergency feature as a subfeature."
        ),
        "decision_status": "provisional_not_applied"
    }
]

group_df = pd.DataFrame(groups)

# Individual OSM record roles
members = [
    # Ruby Hall Clinic
    ("DUP_G001", "SITE_CANDIDATE_001",
     "node/10172977877", "hospital_service_point"),

    ("DUP_G001", "SITE_CANDIDATE_001",
     "node/7649461743", "clinic_service_point"),

    ("DUP_G001", "SITE_CANDIDATE_001",
     "way/53098668", "complex_footprint"),

    # Shinde Hospitals
    ("DUP_G002", "SITE_CANDIDATE_002",
     "node/10219198235", "provisional_representative_point"),

    ("DUP_G002", "SITE_CANDIDATE_002",
     "node/10219230632", "alternate_osm_representation"),

    ("DUP_G002", "SITE_CANDIDATE_002",
     "node/10219230642", "alternate_osm_representation"),

    # Jupiter Hospital
    ("DUP_G034", "SITE_CANDIDATE_003",
     "way/1410820103", "primary_hospital_footprint"),

    ("DUP_G034", "SITE_CANDIDATE_003",
     "way/652021497", "nested_emergency_feature")
]

member_df = pd.DataFrame(
    members,
    columns=[
        "candidate_group_id",
        "facility_group_id",
        "source_key",
        "proposed_member_role"
    ]
)

member_df["review_status"] = "provisional_not_applied"
member_df["preserve_original_record"] = True

group_df.to_csv(GROUP_OUTPUT, index=False)
member_df.to_csv(MEMBER_OUTPUT, index=False)

print("\n========== PRIORITY GROUP DECISIONS ==========")

print("Groups documented:", len(group_df))
print("OSM records documented:", len(member_df))

print("\nGroup interpretations:")
print(group_df[
    ["facility_name", "proposed_interpretation", "confidence"]
].to_string(index=False))

print("\nSaved:")
print(GROUP_OUTPUT)
print(MEMBER_OUTPUT)

print("\nOriginal healthcare inventory remains unchanged.")
