
from pathlib import Path

import geopandas as gpd
import pandas as pd

PROJECT = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    PROJECT / "data/processed/healthcare/"
    "healthcare_inventory_preliminary.gpkg"
)

OUTPUT_FILE = (
    PROJECT / "data/processed/healthcare/"
    "healthcare_manual_classification_decisions.csv"
)

gdf = gpd.read_file(INPUT_FILE)

decisions = [
    ("node/1065057907", "clinic", "Medium",
     "Name and clinic-related specialties support clinic classification."),

    ("node/3536142573", None, "Unresolved",
     "Healthcare centre and pharmacy tags disagree; insufficient evidence."),

    ("node/5695637393", "pharmacy", "High",
     "Healthcare tag is pharmacy and name is Metro Chemist."),

    ("node/5695637395", "doctor", "High",
     "Healthcare tag is doctor and name indicates medical practice."),

    ("node/5832438811", "diagnostic_service", "Medium",
     "Healthcare tag is laboratory; hospital amenity needs verification."),

    ("node/7040434933", "alternative_care", "Medium",
     "Name and specialty indicate Ayurveda; original healthcare value is retained."),

    ("node/7043686747", "health_centre", "High",
     "CGHS dispensary with healthcare centre and dispensary facility type."),

    ("node/7048261228", "health_centre", "High",
     "CGHS dispensary with healthcare centre and dispensary facility type."),

    ("node/7069577086", "hospital", "Medium",
     "Name and hospital amenity support hospital classification."),

    ("node/7649461736", "hospital", "Medium",
     "Name and hospital amenity support hospital classification."),

    ("node/7649461751", "clinic", "Medium",
     "Healthcare clinic tag and homeopathy specialty support clinic classification."),

    ("node/7649461769", "hospital", "Medium",
     "Name and hospital amenity support hospital classification."),

    ("node/8261110954", "dentist", "High",
     "Dental clinic name and dental specialties support dentist classification."),

    ("node/8811062607", "hospital", "Medium",
     "Name and hospital amenity support hospital classification."),

    ("node/9128865193", None, "Unresolved",
     "Clinic name conflicts with chemist and nursing home tags."),

    ("node/9317125306", "clinic", "Medium",
     "ENT clinic name and otolaryngology specialty support clinic classification."),

    ("way/108099341", "hospital", "High",
     "Hospital name and amenity support hospital classification."),

    ("way/984933921", "clinic", "Medium",
     "Primary Health Clinic name supports clinic classification; generic healthcare tag needs verification.")
]

decisions_df = pd.DataFrame(
    decisions,
    columns=[
        "source_key",
        "proposed_category",
        "confidence",
        "decision_rationale"
    ]
)

# Attach original attributes for traceability.
attributes = [
    "source_key",
    "display_name",
    "healthcare",
    "amenity",
    "healthcare:speciality",
    "health_facility:type",
    "facility_category",
    "geometry_type"
]

decision_log = decisions_df.merge(
    gdf[attributes],
    on="source_key",
    how="left",
    validate="one_to_one"
)

decision_log["decision_status"] = decision_log[
    "proposed_category"
].apply(
    lambda value:
        "needs_manual_verification"
        if pd.isna(value)
        else "proposed_not_yet_applied"
)

decision_log.to_csv(OUTPUT_FILE, index=False)

print("\n========== CLASSIFICATION DECISION LOG ==========")
print("Total reviewed records:", len(decision_log))
print(
    "Proposed classifications:",
    decision_log["proposed_category"].notna().sum()
)
print(
    "Unresolved records:",
    decision_log["proposed_category"].isna().sum()
)

print("\nDecision status:")
print(decision_log["decision_status"].value_counts())

print("\nSaved:", OUTPUT_FILE)