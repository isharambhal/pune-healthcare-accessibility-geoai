
from pathlib import Path

import geopandas as gpd
import osmnx as ox

PROJECT = Path(__file__).resolve().parents[2]

HEALTHCARE_FILE = (
    PROJECT / "data/raw/healthcare/"
    "osm_healthcare_facilities.gpkg"
)

BOUNDARY_FILE = (
    PROJECT / "data/raw/boundaries/"
    "PMC Electoral Wards 2025.kml"
)

GRAPH_FILE = (
    PROJECT / "data/processed/roads/"
    "pmc_roads_largest_component.graphml"
)

# 1. Load MILIT Health Center
healthcare = gpd.read_file(HEALTHCARE_FILE)

clinic = healthcare[
    (healthcare["element"] == "node") &
    (healthcare["id"].astype(str) == "4634645591")
].iloc[0]

clinic_point = clinic.geometry

print("\n========== MILIT HEALTH CENTER ==========")
print("Name:", clinic.get("name:en"))
print("Coordinates:", clinic_point.x, clinic_point.y)

# 2. Check whether the clinic is inside the 2025 boundary
boundary = gpd.read_file(BOUNDARY_FILE).to_crs("EPSG:4326")

study_area = boundary.geometry.union_all()

print("\n========== BOUNDARY CHECK ==========")
print("Inside 2025 boundary:", study_area.covers(clinic_point))

# 3. Load the existing driving network
G = ox.io.load_graphml(GRAPH_FILE)
G_projected = ox.project_graph(G, to_crs="EPSG:32643")

clinic_projected = gpd.GeoSeries(
    [clinic_point], crs="EPSG:4326"
).to_crs("EPSG:32643").iloc[0]

# Find nearest edge in the current driving network
u, v, k = ox.distance.nearest_edges(
    G_projected,
    X=clinic_projected.x,
    Y=clinic_projected.y
)

graph_edges = ox.graph_to_gdfs(
    G_projected,
    nodes=False,
    edges=True
)

nearest_drive_edge = graph_edges.loc[(u, v, k)]

print("\n========== CURRENT DRIVE NETWORK ==========")
print(
    "Nearest drivable edge distance:",
    round(clinic_projected.distance(
        nearest_drive_edge.geometry
    ), 2),
    "metres"
)

# 4. Query all OSM highway features within 2 km.
# This includes roads and other highway-tagged features.
print("\nDownloading nearby OSM highway features...")

features = ox.features_from_point(
    center_point=(clinic_point.y, clinic_point.x),
    tags={"highway": True},
    dist=2000
)

print("Total highway features retrieved:", len(features))

# Keep linear road/path features for distance comparison.
linear = features[
    features.geometry.geom_type.isin(
        ["LineString", "MultiLineString"]
    )
].copy()

linear = linear.to_crs("EPSG:32643")

linear["distance_m"] = linear.geometry.distance(
    clinic_projected
)

linear = linear.sort_values("distance_m")

print("\n========== NEAREST OSM HIGHWAY FEATURES ==========")

columns = [
    "highway",
    "name",
    "name:en",
    "access",
    "vehicle",
    "motor_vehicle",
    "service",
    "foot",
    "distance_m"
]

for column in columns:
    if column not in linear.columns:
        linear[column] = None

print(
    linear[columns]
    .head(15)
    .to_string(index=True)
)

print("\n========== HIGHWAY CATEGORY COUNTS ==========")
print(linear["highway"].astype(str).value_counts().head(20))

print("\nInspection complete.")
