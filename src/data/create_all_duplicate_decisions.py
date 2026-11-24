
from pathlib import Path

import geopandas as gpd
import pandas as pd

PROJECT = Path(__file__).resolve().parents[2]
BASE = PROJECT / "data/processed/healthcare"

INVENTORY_FILE = BASE / "healthcare_inventory_preliminary.gpkg"
CANDIDATES_FILE = BASE / "healthcare_duplicate_candidate_groups.csv"
PRIORITY_FILE = BASE / "healthcare_priority_group_decisions.csv"

GROUP_OUTPUT = BASE / "healthcare_all_duplicate_group_decisions.csv"
MEMBER_OUTPUT = BASE / "healthcare_all_duplicate_group_members.csv"

# ------------------------------------------------
# 1. Proposed decisions for groups 3–33
# ------------------------------------------------

proposals = {
    "DUP_G003": ("single_hospital_candidate", "High",
                 "Same hospital name, two hospital points 12.33 m apart."),

    "DUP_G004": ("single_hospital_candidate", "High",
                 "Same hospital name and amenity, points 4.34 m apart."),

    "DUP_G005": ("same_site_category_conflict", "Medium",
                 "Same clinic name, points 1.54 m apart. Preserve hospital and clinic tags."),

    "DUP_G006": ("single_hospital_candidate", "High",
                 "Same hospital name and amenity, points 1.99 m apart."),

    "DUP_G007": ("same_site_category_conflict", "Medium",
                 "Apollo Clinic has conflicting clinic and hospital classifications."),

    "DUP_G008": ("same_site_category_conflict", "Medium",
                 "Same establishment name, with clinic and hospital classifications."),

    "DUP_G009": ("single_hospital_candidate", "High",
                 "Same hospital name and tags, points only 0.18 m apart."),

    "DUP_G010": ("single_hospital_candidate", "High",
                 "Same hospital name and tags, points 3.23 m apart. Preserve ONP Hospitals operator."),

    "DUP_G011": ("hospital_point_and_footprint", "High",
                 "Chandralok Hospital point lies inside its same-name polygon."),

    "DUP_G012": ("hospital_point_and_footprint", "High",
                 "Phadke Hospital point lies inside its same-name polygon."),

    "DUP_G013": ("hospital_point_and_multipolygon", "High",
                 "Seth Tarachand Hospital point lies inside its same-name relation."),

    "DUP_G014": ("hospital_point_and_footprint", "High",
                 "Poona Hospital point lies inside its same-name polygon."),

    "DUP_G015": ("hospital_point_and_footprint", "High",
                 "Deendayal Memorial Hospital point lies inside its polygon. Preserve GOVT operator."),

    "DUP_G016": ("hospital_point_and_footprint", "High",
                 "Kamla Nehru Hospital point lies inside its polygon. Preserve GOVT operator."),

    "DUP_G017": ("single_hospital_candidate", "High",
                 "Same hospital name and tags, points 6.15 m apart."),

    "DUP_G018": ("single_hospital_candidate", "High",
                 "Same hospital name and tags, points 2.89 m apart. Preserve Novosalus operator."),

    "DUP_G019": ("hospital_point_and_footprint", "High",
                 "Prayag Hospital point lies inside its same-name polygon."),

    "DUP_G020": ("single_hospital_candidate", "High",
                 "Same hospital name and amenity, points 7.84 m apart."),

    "DUP_G021": ("single_clinic_candidate", "High",
                 "Same clinic name and category, points 2.12 m apart."),

    "DUP_G022": ("single_hospital_candidate", "High",
                 "Same hospital name and tags, points 3.30 m apart."),

    "DUP_G023": ("single_hospital_candidate", "High",
                 "Same hospital name and tags, points 7.63 m apart."),

    "DUP_G024": ("hospital_point_and_footprint", "High",
                 "Lonkar point lies inside the same-name hospital polygon. Preserve operator."),

    "DUP_G025": ("hospital_site_with_doctor_service", "Medium",
                 "Asian Eye Hospital polygon and doctor-classified point share a name and site. Preserve doctor service classification."),

    "DUP_G026": ("single_hospital_candidate", "High",
                 "Same hospital name and tags, points 2.35 m apart. Preserve Novosalus operator."),

    "DUP_G027": ("single_dental_clinic_candidate", "High",
                 "Same dental clinic name and tags, points 4.02 m apart."),

    "DUP_G028": ("single_hospital_candidate", "High",
                 "Same hospital name and amenity, points 5.17 m apart."),

    "DUP_G029": ("hospital_point_and_nearby_footprint", "Medium",
                 "Same hospital name and tags, but the point is 12.53 m from the polygon. Preserve Private operator and verify spatial offset."),

    "DUP_G030": ("hospital_point_and_footprint", "High",
                 "KEM Hospital point lies inside its same-name polygon."),

    "DUP_G031": ("clinic_point_and_footprint", "High",
                 "Ishaan Orthopedic Clinic point touches its same-name polygon boundary."),

    "DUP_G032": ("hospital_point_and_footprint", "High",
                 "Chellaram Hospital point lies inside its same-name polygon."),

    "DUP_G033": ("clinic_point_and_footprint", "High",
                 "Hridan Speciality Clinic point lies inside its same-name polygon.")
}

# ------------------------------------------------
# 2. Load original data and previous priority decisions
# ------------------------------------------------

inventory = gpd.read_file(INVENTORY_FILE).to_crs("EPSG:32643")
inventory = inventory.set_index("source_key")

candidates = pd.read_csv(CANDIDATES_FILE)
priority = pd.read_csv(PRIORITY_FILE)

if len(priority) != 3:
    raise ValueError("Expected three previously reviewed priority groups.")

if len(proposals) != 31:
    raise ValueError("Expected 31 remaining group proposals.")

# ------------------------------------------------
# 3. Build group-level decision register
# ------------------------------------------------

group_rows = []

# Preserve the three existing priority decisions.
for _, row in priority.iterrows():

    group_rows.append({
        "candidate_group_id": row["candidate_group_id"],
        "facility_group_id": row["facility_group_id"],
        "facility_name": row["facility_name"],
        "proposed_interpretation": row["proposed_interpretation"],
        "confidence": row["confidence"],
        "decision_rationale": row["decision_rationale"],
        "decision_status": "provisional_not_applied",
        "manual_confirmation": "pending"
    })

# Add remaining groups.
summary = candidates.groupby("candidate_group_id")

for group_id, (interpretation, confidence, rationale) in proposals.items():

    rows = summary.get_group(group_id)
    keys = sorted(set(rows["source_key"]))

    names = sorted({
        str(inventory.loc[key]["display_name"])
        for key in keys
        if pd.notna(inventory.loc[key]["display_name"])
    })

    # Find a provisional representative point among point records.
    point_keys = [
        key for key in keys
        if inventory.loc[key].geometry.geom_type == "Point"
    ]

    routing_key = ""

    if point_keys:
        distance_sums = {}

        for key in point_keys:
            point = inventory.loc[key].geometry

            distance_sums[key] = sum(
                point.distance(inventory.loc[other].geometry)
                for other in point_keys
            )

        routing_key = min(distance_sums, key=distance_sums.get)

    group_rows.append({
        "candidate_group_id": group_id,
        "facility_group_id": f"SITE_CANDIDATE_{group_id[-3:]}",
        "facility_name": " | ".join(names),
        "proposed_interpretation": interpretation,
        "confidence": confidence,
        "decision_rationale": rationale,
        "provisional_routing_source_key": routing_key,
        "decision_status": "provisional_not_applied",
        "manual_confirmation": "pending"
    })

group_decisions = pd.DataFrame(group_rows)

# ------------------------------------------------
# 4. Build member-level register
# ------------------------------------------------

member_rows = []

for _, group in group_decisions.iterrows():

    group_id = group["candidate_group_id"]

    candidate_members = candidates[
        candidates["candidate_group_id"] == group_id
    ]

    keys = sorted(set(candidate_members["source_key"]))

    for key in keys:

        record = inventory.loc[key]
        geometry_type = record.geometry.geom_type

        role = "alternate_osm_representation"

        if group_id == "DUP_G001":

            if key == "node/10172977877":
                role = "hospital_service_point"
            elif key == "node/7649461743":
                role = "clinic_service_point"
            else:
                role = "healthcare_complex_footprint"

        elif group_id == "DUP_G002":

            if key == "node/10219198235":
                role = "provisional_representative_point"

        elif group_id == "DUP_G034":

            if key == "way/1410820103":
                role = "primary_hospital_footprint"
            else:
                role = "nested_emergency_feature"

        elif group_id == "DUP_G025":

            if geometry_type == "Point":
                role = "doctor_service_point"
            else:
                role = "hospital_footprint"

        elif geometry_type == "Point":

            if key == group.get("provisional_routing_source_key"):
                role = "provisional_routing_point"

        elif geometry_type in ["Polygon", "MultiPolygon"]:

            if group_id == "DUP_G029":
                role = "hospital_footprint_requires_offset_review"
            else:
                role = "facility_footprint"

        member_rows.append({
            "candidate_group_id": group_id,
            "facility_group_id": group["facility_group_id"],
            "source_key": key,
            "display_name": record["display_name"],
            "facility_category": record["facility_category"],
            "healthcare": record.get("healthcare"),
            "amenity": record.get("amenity"),
            "operator": record.get("operator"),
            "geometry_type": geometry_type,
            "proposed_member_role": role,
            "preserve_original_record": True,
            "review_status": "provisional_not_applied",
            "manual_confirmation": "pending"
        })

members = pd.DataFrame(member_rows)

# ------------------------------------------------
# 5. Validate and save
# ------------------------------------------------

if len(group_decisions) != 34:
    raise ValueError("Expected exactly 34 candidate groups.")

if len(members) != 70:
    raise ValueError("Expected exactly 70 candidate OSM records.")

if members["source_key"].nunique() != 70:
    raise ValueError("Duplicate source keys found in member register.")

group_decisions.to_csv(GROUP_OUTPUT, index=False)
members.to_csv(MEMBER_OUTPUT, index=False)

print("\n========== CONSOLIDATED DUPLICATE REGISTER ==========")

print("Candidate groups:", len(group_decisions))
print("Unique OSM records:", len(members))

print("\nGroup confidence:")
print(group_decisions["confidence"].value_counts())

print("\nProposed interpretations:")
print(group_decisions["proposed_interpretation"].value_counts())

print("\nMember roles:")
print(members["proposed_member_role"].value_counts())

print("\nSaved:")
print(GROUP_OUTPUT)
print(MEMBER_OUTPUT)

print("\nAll decisions remain provisional.")
print("Original healthcare inventory was not modified.")
