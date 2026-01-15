"""
D3.js format export for web visualizations.
"""

import json
import networkx as nx
from typing import Dict, Any, List
from pathlib import Path


class D3Exporter:
    """Export network data in D3.js-friendly format."""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize D3 exporter.

        Args:
            config: Configuration dictionary
        """
        self.config = config

    def export(self, G: nx.Graph, output_path: str, include_metadata: bool = True):
        """
        Export graph in D3.js force layout format.

        Args:
            G: NetworkX graph
            output_path: Output file path
            include_metadata: Whether to include metadata
        """
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        # Build D3 format
        d3_data = self._build_d3_format(G, include_metadata)

        # Save to file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(d3_data, f, indent=2, ensure_ascii=False)

        print(f"Exported D3.js format to: {output_path}")

    def _build_d3_format(self, G: nx.Graph, include_metadata: bool = True) -> Dict[str, Any]:
        """
        Build D3.js format from graph.

        Args:
            G: NetworkX graph
            include_metadata: Whether to include metadata

        Returns:
            D3-formatted data
        """
        # Create node list
        nodes = []

        for node in G.nodes():
            node_data = {
                'id': node,
                'name': node,
                'group': G.nodes[node].get('community', 0),
                'degree': G.degree(node)
            }

            # Add other node attributes
            for key, value in G.nodes[node].items():
                if key not in node_data and isinstance(value, (str, int, float, bool)):
                    node_data[key] = value

            # Add color based on type
            entity_type = G.nodes[node].get('type', 'UNKNOWN')
            node_data['type'] = entity_type
            node_data['color'] = self._get_type_color(entity_type)

            # Size by mentions or degree
            mentions = G.nodes[node].get('mentions', G.degree(node))
            node_data['size'] = max(5, min(30, mentions))

            nodes.append(node_data)

        # Create edge list
        links = []
        for u, v, data in G.edges(data=True):
            link = {
                'source': u,  # Use actual node ID (entity name) instead of index
                'target': v,  # Use actual node ID (entity name) instead of index
                'value': data.get('weight', 1),
                'weight': data.get('weight', 1)  # Also include as 'weight' for compatibility
            }
            links.append(link)

        # Build final structure
        d3_data = {
            'nodes': nodes,
            'links': links
        }

        # Add metadata if requested
        if include_metadata:
            d3_data['metadata'] = {
                'num_nodes': G.number_of_nodes(),
                'num_edges': G.number_of_edges(),
                'density': nx.density(G)
            }

        return d3_data

    def _get_type_color(self, entity_type: str) -> str:
        """Get color for entity type."""
        colors = {
            'PERSON': '#FF6B6B',
            'PLACE': '#45B7D1',
            'ORG': '#4ECDC4',
            'GPE': '#96CEB4',
            'LOC': '#96CEB4',
            'UNKNOWN': '#808080'
        }
        return colors.get(entity_type, '#808080')

    def export_timeline_format(self, temporal_graphs: List[Dict[str, Any]], output_path: str):
        """
        Export temporal network in timeline-friendly format.

        Args:
            temporal_graphs: List of temporal graph snapshots
            output_path: Output file path
        """
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        timeline_data = {
            'frames': []
        }

        for snapshot in temporal_graphs:
            frame = {
                'period': snapshot['period'],
                'graph': self._build_d3_format(snapshot['graph'], include_metadata=False),
                'article_count': snapshot.get('article_count', 0)
            }
            timeline_data['frames'].append(frame)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(timeline_data, f, indent=2, ensure_ascii=False)

        print(f"Exported timeline format to: {output_path}")
