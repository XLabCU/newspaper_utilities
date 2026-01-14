"""
Graph export to GraphML and GEXF formats (for Gephi, Cytoscape).
"""

import networkx as nx
from typing import Dict, Any
from pathlib import Path


class GraphExporter:
    """Export networks to graph file formats."""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize graph exporter.

        Args:
            config: Configuration dictionary
        """
        self.config = config

    def export_graphml(self, G: nx.Graph, output_path: str):
        """
        Export graph to GraphML format.

        Args:
            G: NetworkX graph
            output_path: Output file path
        """
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        # Ensure all node/edge attributes are GraphML-compatible
        G_copy = self._prepare_graph_for_export(G)

        nx.write_graphml(G_copy, output_path)
        print(f"Exported GraphML to: {output_path}")

    def export_gexf(self, G: nx.Graph, output_path: str):
        """
        Export graph to GEXF format.

        Args:
            G: NetworkX graph
            output_path: Output file path
        """
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        # Ensure all node/edge attributes are GEXF-compatible
        G_copy = self._prepare_graph_for_export(G)

        nx.write_gexf(G_copy, output_path)
        print(f"Exported GEXF to: {output_path}")

    def _prepare_graph_for_export(self, G: nx.Graph) -> nx.Graph:
        """
        Prepare graph for export by converting attributes to compatible types.

        Args:
            G: NetworkX graph

        Returns:
            Prepared graph copy
        """
        G_copy = G.copy()

        # Convert node attributes to strings/numbers
        for node in G_copy.nodes():
            attrs = G_copy.nodes[node]
            for key, value in list(attrs.items()):
                if not isinstance(value, (str, int, float, bool)):
                    attrs[key] = str(value)

        # Convert edge attributes to strings/numbers
        for u, v in G_copy.edges():
            attrs = G_copy.edges[u, v]
            for key, value in list(attrs.items()):
                if not isinstance(value, (str, int, float, bool)):
                    attrs[key] = str(value)

        return G_copy
