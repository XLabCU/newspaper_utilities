"""
CSV export for network data (edge lists, node lists).
"""

import csv
import networkx as nx
from typing import Dict, Any
from pathlib import Path


class CSVExporter:
    """Export network data to CSV format."""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize CSV exporter.

        Args:
            config: Configuration dictionary
        """
        self.config = config

    def export_edge_list(self, G: nx.Graph, output_path: str):
        """
        Export graph as CSV edge list.

        Args:
            G: NetworkX graph
            output_path: Output file path
        """
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            # Get all edge attribute keys
            attr_keys = set()
            for u, v, data in G.edges(data=True):
                attr_keys.update(data.keys())

            attr_keys = sorted(attr_keys)

            # Write header
            fieldnames = ['source', 'target'] + attr_keys
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            # Write edges
            for u, v, data in G.edges(data=True):
                row = {'source': u, 'target': v}
                row.update(data)
                writer.writerow(row)

        print(f"Exported edge list to: {output_path}")

    def export_node_list(self, G: nx.Graph, output_path: str):
        """
        Export graph nodes as CSV.

        Args:
            G: NetworkX graph
            output_path: Output file path
        """
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            # Get all node attribute keys
            attr_keys = set()
            for node, data in G.nodes(data=True):
                attr_keys.update(data.keys())

            attr_keys = sorted(attr_keys)

            # Write header
            fieldnames = ['node'] + attr_keys + ['degree']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            # Write nodes
            for node, data in G.nodes(data=True):
                row = {'node': node, 'degree': G.degree(node)}
                row.update(data)
                writer.writerow(row)

        print(f"Exported node list to: {output_path}")
