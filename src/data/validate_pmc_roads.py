
from pathlib import Path
import geopandas as gpd
import osmnx as ox
import networkx as nx

PROJECT = Path(__file__).resolve().parents[2]
ROAD_DIR = PROJECT / "data/raw/roads"

gpkg = ROAD_DIR / "pmc_roads_drive.gpkg"
graph_file = ROAD_DIR / "pmc_roads_drive.graphml"

# Read road segments and nodes
roads = gpd.read_file(gpkg, layer="roads")
nodes = gpd.read_file(gpkg, layer="nodes")

# Read network graph
G = ox.io.load_graphml(graph_file)

print("\n========== ROAD NETWORK VALIDATION ==========")

print("Road segments:", len(roads))
print("Network nodes:", len(nodes))
print("Graph nodes:", G.number_of_nodes())
print("Graph edges:", G.number_of_edges())

print("\nCRS:", roads.crs)

print("\nGeometry types:")
print(roads.geometry.geom_type.value_counts())

print("\nRoad categories:")
print(roads["highway"].explode().value_counts().head(20))

# Check road lengths in metres
roads_projected = roads.to_crs("EPSG:32643")
print("\nTotal road segment length (km):",
      round(roads_projected.geometry.length.sum() / 1000, 2))

# Network connectivity
components = list(nx.weakly_connected_components(G))

print("\nWeakly connected components:", len(components))
print("Largest component nodes:",
      max(map(len, components)))

print("\nMissing geometries:", roads.geometry.isna().sum())
print("Invalid geometries:", (~roads.geometry.is_valid).sum())
