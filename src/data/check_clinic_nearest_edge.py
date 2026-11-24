
from pathlib import Path

import geopandas as gpd
import osmnx as ox

PROJECT = Path(__file__).resolve().parents[2]

GRAPH_FILE = (
    PROJECT / "data/raw/roads/"
    "pmc_roads_drive.graphml"
)

HEALTHCARE_FILE = (
    PROJECT / "data/raw/healthcare/"
    "osm_healthcare_facilities.gpkg"
)

G = ox.io.load_graphml(GRAPH_FILE)

healthcare = gpd.read_file(HEALTHCARE_FILE)

clinic = healthcare[
    (healthcare["element"] == "node") &
    (healthcare["id"].astype(str) == "4634645591")
].iloc[0]

# Project graph and clinic to the same metric CRS.
G_projected = ox.project_graph(G, to_crs="EPSG:32643")

clinic_point = gpd.GeoSeries(
    [clinic.geometry],
    crs=healthcare.crs
).to_crs("EPSG:32643").iloc[0]

# Find nearest road edge.
u, v, k = ox.distance.nearest_edges(
    G_projected,
    X=clinic_point.x,
    Y=clinic_point.y
)

edges = ox.graph_to_gdfs(
    G_projected,
    nodes=False,
    edges=True
)

nearest_edge = edges.loc[(u, v, k)]

distance = clinic_point.distance(nearest_edge.geometry)

print("\n========== MILIT HEALTH CENTER ==========")
print("OSM ID:", clinic["id"])
print("Name:", clinic.get("name:en"))
print("Nearest road edge:", (u, v, k))
print("Nearest road distance:", round(distance, 2), "metres")
print("Road attributes:")
print(nearest_edge.drop(labels="geometry").to_string())

print("\nInspection complete.")
