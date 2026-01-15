"""
JSON export for entity and network data.
"""

import json
import networkx as nx
from typing import Dict, Any
from datetime import datetime
from pathlib import Path


class JSONExporter:
    """Export entity and network data to JSON format."""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize JSON exporter.

        Args:
            config: Configuration dictionary
        """
        self.config = config

    def export(self, data: Dict[str, Any], output_path: str, pretty: bool = True):
        """
        Export data to JSON file.

        Args:
            data: Data to export
            output_path: Output file path
            pretty: Whether to pretty-print JSON
        """
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            if pretty:
                json.dump(data, f, indent=2, ensure_ascii=False, default=self._json_serializer)
            else:
                json.dump(data, f, ensure_ascii=False, default=self._json_serializer)

        print(f"Exported JSON to: {output_path}")

    def export_full_dataset(self, entities_data: Dict[str, Any], networks: Dict[str, Any],
                           metrics: Dict[str, Any], communities: Dict[str, Any],
                           project_metadata: Dict[str, Any], output_path: str):
        """
        Export complete dataset with all analysis results.

        Args:
            entities_data: Entity extraction data
            networks: Network graphs
            metrics: Network metrics
            communities: Community detection results
            project_metadata: Project metadata
            output_path: Output file path
        """
        # Build complete dataset
        dataset = {
            'metadata': {
                **project_metadata,
                'generated_at': datetime.now().isoformat(),
                'data_version': '2.0'
            },
            'entities': self._build_entity_summary(entities_data),
            'networks': self._build_network_summary(networks, metrics, communities),
            'article_entities': entities_data.get('article_entities', [])
        }

        self.export(dataset, output_path)

    def _build_entity_summary(self, entities_data: Dict[str, Any]) -> Dict[str, Any]:
        """Build entity summary for export."""
        all_entities = {}

        # People
        for name, count in entities_data.get('people', {}).items():
            all_entities[name] = {
                'type': 'PERSON',
                'mentions': count
            }

        # Places
        for name, count in entities_data.get('places', {}).items():
            all_entities[name] = {
                'type': 'PLACE',
                'mentions': count
            }

        # Organizations
        for name, count in entities_data.get('organizations', {}).items():
            all_entities[name] = {
                'type': 'ORG',
                'mentions': count
            }

        return all_entities

    def _build_network_summary(self, networks: Dict[str, Any], metrics: Dict[str, Any],
                              communities: Dict[str, Any]) -> Dict[str, Any]:
        """Build network summary for export."""
        network_summary = {}

        for network_name, network_data in networks.items():
            if isinstance(network_data, nx.Graph):
                G = network_data

                summary = {
                    'num_nodes': G.number_of_nodes(),
                    'num_edges': G.number_of_edges(),
                    'density': nx.density(G),
                    'nodes': list(G.nodes()),
                    'edges': [
                        {'source': u, 'target': v, 'weight': data.get('weight', 1)}
                        for u, v, data in G.edges(data=True)
                    ]
                }

                # Add metrics if available
                if network_name in metrics:
                    summary['metrics'] = metrics[network_name]

                # Add communities if available
                if network_name in communities:
                    summary['communities'] = communities[network_name]

                network_summary[network_name] = summary

        return network_summary

    def _json_serializer(self, obj):
        """Custom JSON serializer for special types."""
        if isinstance(obj, nx.Graph):
            return {
                'nodes': list(obj.nodes()),
                'edges': list(obj.edges())
            }
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
