
from pathlib import Path
from datetime import datetime, timezone

import geopandas as gpd
import osmnx as ox

# Project paths
PROJECT_DIR = Path(__file__).resolve().parents[2]

BOUNDARY_FILE = (
    PROJECT_DIR
    / "data"
    / "raw"
    / "boundaries"
    / "PMC Electoral Wards 2025.kml"
)

OUTPUT_DIR = PROJECT_DIR / "data" / "raw" / "roads"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

GRAPH_FILE = OUTPUT_DIR / "pmc_roads_drive.graphml"
GPKG_FILE = OUTPUT_DIR / "pmc_roads_drive.gpkg"
METADATA_FILE = OUTPUT_DIR / "pmc_roads_metadata.txt"

# Configure OSMnx
ox.settings.use_cache = True
ox.settings.log_console = True

# Read PMC boundary
print("Reading PMC 2025 boundary...")

wards = gpd.read_file(BOUNDARY_FILE).to_crs("EPSG:4326")
pmc_boundary = wards.geometry.union_all()

print("Ward polygons:", len(wards))
print("Downloading driving road network...")

# Download road network
G = ox.graph.graph_from_polygon(
    pmc_boundary,
    network_type="drive",
    simplify=True,
    retain_all=True
)

# Convert network into spatial layers
nodes, edges = ox.convert.graph_to_gdfs(G)

# Save original network structure
ox.io.save_graphml(G, GRAPH_FILE)

# Save nodes and roads as separate GeoPackage layers
edges.to_file(
    GPKG_FILE,
    layer="roads",
    driver="GPKG"
)

nodes.to_file(
    GPKG_FILE,
    layer="nodes",
    driver="GPKG"
)

# Metadata
metadata = f"""
Dataset: PMC driving road network
Source: OpenStreetMap
Download date (UTC): {datetime.now(timezone.utc).isoformat()}
Boundary: PMC Electoral Wards 2025
Number of boundary polygons: {len(wards)}
Network type: drive
CRS: {edges.crs}
OSMnx version: {ox.__version__}
Number of road segments: {len(edges)}
Number of network nodes: {len(nodes)}

Files:
- pmc_roads_drive.graphml
- pmc_roads_drive.gpkg

Licence: Open Database License (ODbL)
Attribution: © OpenStreetMap contributors
"""

METADATA_FILE.write_text(metadata.strip(), encoding="utf-8")

print("\n========== ROAD NETWORK SUMMARY ==========")
print("Road segments:", len(edges))
print("Network nodes:", len(nodes))
print("Road CRS:", edges.crs)
print("Road types:")
print(edges["highway"].value_counts().head(15))

print("\nSaved files:")
print(GRAPH_FILE)
print(GPKG_FILE)
print(METADATA_FILE)
