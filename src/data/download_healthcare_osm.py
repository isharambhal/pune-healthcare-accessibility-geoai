
from pathlib import Path
from datetime import datetime, timezone

import geopandas as gpd
import osmnx as ox

# -------------------------------------------------
# 1. Project paths
# -------------------------------------------------
PROJECT_DIR = Path(__file__).resolve().parents[2]

BOUNDARY_FILE = (
    PROJECT_DIR
    / "data"
    / "raw"
    / "boundaries"
    / "PMC Electoral Wards 2025.kml"
)

OUTPUT_DIR = PROJECT_DIR / "data" / "raw" / "healthcare"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = OUTPUT_DIR / "osm_healthcare_facilities.gpkg"
METADATA_FILE = OUTPUT_DIR / "osm_healthcare_metadata.txt"

# -------------------------------------------------
# 2. Read PMC boundary
# -------------------------------------------------
print("Reading PMC 2025 boundary...")

wards = gpd.read_file(BOUNDARY_FILE).to_crs("EPSG:4326")

pmc_boundary = wards.geometry.union_all()

print("Ward polygons:", len(wards))
print("Boundary CRS:", wards.crs)

# -------------------------------------------------
# 3. Configure OSMnx
# -------------------------------------------------
ox.settings.timeout = 180
ox.settings.use_cache = True
ox.settings.log_console = True

# OSM tags: matching any of these tag groups
tags = {
    "amenity": [
        "hospital",
        "clinic",
        "doctors",
        "pharmacy",
        "dentist"
    ],
    "healthcare": True
}

# -------------------------------------------------
# 4. Download healthcare features
# -------------------------------------------------
print("\nDownloading healthcare features from OSM...")
print("This may take several minutes.")

facilities = ox.features.features_from_polygon(
    pmc_boundary,
    tags=tags
)

if facilities.empty:
    raise RuntimeError(
        "No healthcare features returned. "
        "Check the internet connection and OSM query."
    )

# Ensure geographic CRS
facilities = facilities.to_crs("EPSG:4326")

# -------------------------------------------------
# 5. Basic validation
# -------------------------------------------------
facilities = facilities[
    facilities.geometry.notna()
].copy()

facilities["geometry_valid"] = facilities.geometry.is_valid

print("\n========== DOWNLOAD SUMMARY ==========")
print("Total OSM features:", len(facilities))
print("CRS:", facilities.crs)
print("Geometry types:")
print(facilities.geometry.geom_type.value_counts())

print("\nAmenity categories:")
if "amenity" in facilities.columns:
    print(facilities["amenity"].value_counts(dropna=False).head(20))

print("\nHealthcare categories:")
if "healthcare" in facilities.columns:
    print(facilities["healthcare"].value_counts(dropna=False).head(20))

# -------------------------------------------------
# 6. Save GeoPackage
# -------------------------------------------------
facilities.to_file(
    OUTPUT_FILE,
    layer="healthcare_facilities",
    driver="GPKG",
    index=True
)

# -------------------------------------------------
# 7. Save metadata
# -------------------------------------------------
metadata = f"""
Dataset: OpenStreetMap healthcare features
Download time (UTC): {datetime.now(timezone.utc).isoformat()}
Study boundary: PMC 2025 KML
Number of boundary polygons: {len(wards)}
Boundary CRS: EPSG:4326
Output CRS: EPSG:4326
OSMnx version: {ox.__version__}
Number of downloaded features: {len(facilities)}
Output file: {OUTPUT_FILE.name}

OSM tags queried:
amenity=hospital, clinic, doctors, pharmacy, dentist
healthcare=*

Source: OpenStreetMap contributors
Licence: Open Database License (ODbL)
Attribution: © OpenStreetMap contributors
"""

METADATA_FILE.write_text(metadata, encoding="utf-8")

print("\nDownload completed.")
print("GeoPackage:", OUTPUT_FILE)
print("Metadata:", METADATA_FILE)
