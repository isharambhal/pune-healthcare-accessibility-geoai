from pathlib import Path

import osmnx as ox
import networkx as nx

PROJECT = Path(__file__).resolve().parents[2]

graph_file = (
    PROJECT
    / "data/raw/roads/pmc_roads_drive.graphml"
)

G = ox.io.load_graphml(graph_file)

components = list(nx.weakly_connected_components(G))
components.sort(key=len, reverse=True)

print("\n========== ROAD COMPONENT INSPECTION ==========")

print(f"Total components: {len(components)}")
print("\nLargest 10 components:")

for i, component in enumerate(components[:10], start=1):
    print(f"Component {i}: {len(component)} nodes")

small_components = [
    component for component in components
    if len(component) <= 10
]

print(
    "\nComponents with 10 or fewer nodes:",
    len(small_components)
)

print(
    "Total nodes in these small components:",
    sum(len(c) for c in small_components)
)

print("\n========== COMPLETE ==========")