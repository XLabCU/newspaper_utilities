"""
Network metrics calculation (centrality, clustering, etc.).
"""

import networkx as nx
from typing import Dict, Any, List
from collections import defaultdict


class MetricsCalculator:
    """Calculate various network metrics."""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize metrics calculator.

        Args:
            config: Network analysis configuration
        """
        self.config = config
        self.metrics_config = config.get('metrics', {})
        self.node_metrics = self.metrics_config.get('node_metrics', [])
        self.graph_metrics = self.metrics_config.get('graph_metrics', [])
        self.temporal_metrics = self.metrics_config.get('temporal_metrics', [])

    def calculate_all(self, networks: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate all configured metrics for all networks.

        Args:
            networks: Dictionary of network graphs

        Returns:
            Dictionary of calculated metrics
        """
        metrics = {}

        for network_name, network_data in networks.items():
            print(f"Calculating metrics for {network_name}...")

            # Handle different network types
            if isinstance(network_data, list):
                # Temporal network (list of graphs)
                metrics[network_name] = self._calculate_temporal_metrics(network_data)
            elif isinstance(network_data, dict):
                # Tag-based networks (dict of graphs)
                metrics[network_name] = {}
                for tag, G in network_data.items():
                    metrics[network_name][tag] = self.calculate_graph_metrics(G)
            else:
                # Single graph
                metrics[network_name] = self.calculate_graph_metrics(network_data)

        return metrics

    def calculate_graph_metrics(self, G: nx.Graph) -> Dict[str, Any]:
        """
        Calculate all metrics for a single graph.

        Args:
            G: NetworkX graph

        Returns:
            Dictionary of metrics
        """
        metrics = {}

        # Node-level metrics
        if self.node_metrics:
            metrics['node_metrics'] = self._calculate_node_metrics(G)

        # Graph-level metrics
        if self.graph_metrics:
            metrics['graph_metrics'] = self._calculate_graph_level_metrics(G)

        return metrics

    def _calculate_node_metrics(self, G: nx.Graph) -> Dict[str, Dict[str, float]]:
        """
        Calculate node-level metrics.

        Args:
            G: NetworkX graph

        Returns:
            Dictionary mapping metric names to node-value dicts
        """
        metrics = {}

        if 'degree_centrality' in self.node_metrics:
            metrics['degree_centrality'] = nx.degree_centrality(G)

        if 'betweenness_centrality' in self.node_metrics:
            metrics['betweenness_centrality'] = nx.betweenness_centrality(G)

        if 'closeness_centrality' in self.node_metrics:
            metrics['closeness_centrality'] = nx.closeness_centrality(G)

        if 'eigenvector_centrality' in self.node_metrics:
            try:
                metrics['eigenvector_centrality'] = nx.eigenvector_centrality(G, max_iter=1000)
            except:
                # Eigenvector centrality may not converge
                metrics['eigenvector_centrality'] = {n: 0.0 for n in G.nodes()}

        if 'pagerank' in self.node_metrics:
            metrics['pagerank'] = nx.pagerank(G)

        if 'clustering_coefficient' in self.node_metrics:
            metrics['clustering'] = nx.clustering(G)

        return metrics

    def _calculate_graph_level_metrics(self, G: nx.Graph) -> Dict[str, Any]:
        """
        Calculate graph-level metrics.

        Args:
            G: NetworkX graph

        Returns:
            Dictionary of graph metrics
        """
        metrics = {
            'num_nodes': G.number_of_nodes(),
            'num_edges': G.number_of_edges()
        }

        if 'density' in self.graph_metrics:
            metrics['density'] = nx.density(G)

        # Connected components
        if G.is_directed():
            metrics['num_components'] = nx.number_weakly_connected_components(G)
        else:
            metrics['num_components'] = nx.number_connected_components(G)
            if metrics['num_components'] > 0:
                largest_cc = max(nx.connected_components(G), key=len)
                metrics['largest_component_size'] = len(largest_cc)

        # Metrics that require connected graph
        if nx.is_connected(G):
            if 'diameter' in self.graph_metrics:
                metrics['diameter'] = nx.diameter(G)

            if 'average_path_length' in self.graph_metrics:
                metrics['avg_path_length'] = nx.average_shortest_path_length(G)

        # Degree distribution
        degrees = [d for n, d in G.degree()]
        if degrees:
            metrics['avg_degree'] = sum(degrees) / len(degrees)
            metrics['max_degree'] = max(degrees)
            metrics['min_degree'] = min(degrees)

        return metrics

    def _calculate_temporal_metrics(self, temporal_graphs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate temporal network metrics.

        Args:
            temporal_graphs: List of temporal graph snapshots

        Returns:
            Dictionary of temporal metrics
        """
        metrics = {
            'time_periods': len(temporal_graphs),
            'periods': []
        }

        # Track entity lifecycles
        entity_timelines = defaultdict(lambda: {
            'first_appearance': None,
            'last_appearance': None,
            'appearances': [],
            'peak_mentions': 0,
            'total_degree': 0
        })

        for snapshot in temporal_graphs:
            period = snapshot['period']
            G = snapshot['graph']

            # Calculate metrics for this period
            period_metrics = {
                'period': period,
                'num_nodes': G.number_of_nodes(),
                'num_edges': G.number_of_edges(),
                'density': nx.density(G) if G.number_of_nodes() > 0 else 0,
                'article_count': snapshot.get('article_count', 0)
            }

            metrics['periods'].append(period_metrics)

            # Track entity appearances
            for node in G.nodes():
                timeline = entity_timelines[node]
                degree = G.degree(node)

                if timeline['first_appearance'] is None:
                    timeline['first_appearance'] = period

                timeline['last_appearance'] = period
                timeline['appearances'].append({
                    'period': period,
                    'degree': degree
                })
                timeline['total_degree'] += degree
                timeline['peak_mentions'] = max(timeline['peak_mentions'], degree)

        # Calculate temporal metrics for entities
        if 'entity_emergence_rate' in self.temporal_metrics or \
           'entity_persistence' in self.temporal_metrics or \
           'entity_burstiness' in self.temporal_metrics:

            metrics['entity_timelines'] = self._analyze_entity_timelines(entity_timelines)

        return metrics

    def _analyze_entity_timelines(self, entity_timelines: Dict[str, Dict]) -> Dict[str, Any]:
        """
        Analyze entity temporal patterns.

        Args:
            entity_timelines: Entity timeline data

        Returns:
            Dictionary of entity temporal metrics
        """
        import numpy as np

        analyzed = {}

        for entity, timeline in entity_timelines.items():
            appearances = timeline['appearances']

            analysis = {
                'first_appearance': timeline['first_appearance'],
                'last_appearance': timeline['last_appearance'],
                'total_appearances': len(appearances),
                'persistence': len(appearances),
                'peak_mentions': timeline['peak_mentions']
            }

            # Burstiness: variance in mentions
            if len(appearances) > 1:
                degrees = [a['degree'] for a in appearances]
                mean_degree = np.mean(degrees)
                std_degree = np.std(degrees)
                analysis['burstiness'] = std_degree / (mean_degree + 0.001)
            else:
                analysis['burstiness'] = 0

            # Emergence rate: how quickly entity gains prominence
            if len(appearances) >= 2:
                degrees = [a['degree'] for a in appearances]
                peak_idx = np.argmax(degrees)
                if peak_idx > 0:
                    analysis['emergence_rate'] = (degrees[peak_idx] - degrees[0]) / peak_idx
                else:
                    analysis['emergence_rate'] = 0
            else:
                analysis['emergence_rate'] = 0

            analyzed[entity] = analysis

        return analyzed

    def get_top_nodes(self, G: nx.Graph, metric: str = 'degree', n: int = 20) -> List[tuple]:
        """
        Get top N nodes by a specific metric.

        Args:
            G: NetworkX graph
            metric: Metric name ('degree', 'betweenness', 'pagerank', etc.)
            n: Number of top nodes to return

        Returns:
            List of (node, value) tuples
        """
        if metric == 'degree':
            values = dict(G.degree())
        elif metric == 'betweenness':
            values = nx.betweenness_centrality(G)
        elif metric == 'pagerank':
            values = nx.pagerank(G)
        elif metric == 'closeness':
            values = nx.closeness_centrality(G)
        else:
            # Try to get from node metrics
            metrics = self._calculate_node_metrics(G)
            values = metrics.get(metric, {})

        return sorted(values.items(), key=lambda x: x[1], reverse=True)[:n]
