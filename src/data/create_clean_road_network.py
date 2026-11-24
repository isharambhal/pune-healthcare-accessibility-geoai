from pathlib import Path

import osmnx as ox
import networkx as nx

PROJECT = Path(__file__).resolve().parents[2]

RAW_GRAPH = (
    PROJECT / "data/raw/roads/pmc_roads_drive.graphml"
)

OUTPUT_DIR = PROJECT / "data/processed/roads"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_GRAPH = OUTPUT_DIR / "pmc_roads_largest_component.graphml"

print("Loading original road network...")

G = ox.io.load_graphml(RAW_GRAPH)

print("Original nodes:", len(G.nodes))
print("Original edges:", len(G.edges))

# Identify weakly connected components
components = list(nx.weakly_connected_components(G))

# Select the largest component
largest_component = max(components, key=len)

# Create a separate graph
G_clean = G.subgraph(largest_component).copy()

print("\n========== CLEAN NETWORK ==========")
print("Original components:", len(components))
print("Clean network nodes:", len(G_clean.nodes))
print("Clean network edges:", len(G_clean.edges))

# Save processed graph
ox.io.save_graphml(G_clean, OUTPUT_GRAPH)

print("\nSaved processed network:")
print(OUTPUT_GRAPH)

print("\nOriginal graph remains unchanged.")