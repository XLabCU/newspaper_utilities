"""
Community detection for entity networks.
"""

import networkx as nx
from typing import Dict, Any, List
from collections import defaultdict


class CommunityDetector:
    """Detect communities in entity networks."""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize community detector.

        Args:
            config: Network analysis configuration
        """
        self.config = config
        self.community_config = config.get('community_detection', {})
        self.enabled = self.community_config.get('enabled', False)
        self.algorithms = self.community_config.get('algorithms', [])

    def detect_communities(self, G: nx.Graph) -> Dict[str, Any]:
        """
        Detect communities using configured algorithms.

        Args:
            G: NetworkX graph

        Returns:
            Dictionary mapping algorithm names to community assignments
        """
        if not self.enabled or not self.algorithms:
            return {}

        communities = {}

        for algo_config in self.algorithms:
            if not algo_config.get('enabled', True):
                continue

            algo_name = algo_config['name']

            print(f"  Running {algo_name} community detection...")

            if algo_name == 'louvain':
                communities[algo_name] = self._detect_louvain(G, algo_config)
            elif algo_name == 'label_propagation':
                communities[algo_name] = self._detect_label_propagation(G)
            elif algo_name == 'girvan_newman':
                communities[algo_name] = self._detect_girvan_newman(G, algo_config)

        return communities

    def _detect_louvain(self, G: nx.Graph, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Detect communities using Louvain algorithm.

        Args:
            G: NetworkX graph
            config: Algorithm configuration

        Returns:
            Community assignment and metrics
        """
        try:
            import community as community_louvain

            resolution = config.get('resolution', 1.0)

            # Run Louvain algorithm
            partition = community_louvain.best_partition(G, resolution=resolution)

            # Calculate modularity
            modularity = community_louvain.modularity(partition, G)

            # Get community sizes
            community_sizes = defaultdict(int)
            for node, comm_id in partition.items():
                community_sizes[comm_id] += 1

            num_communities = len(community_sizes)

            print(f"    Found {num_communities} communities, modularity: {modularity:.3f}")

            return {
                'partition': partition,
                'num_communities': num_communities,
                'modularity': modularity,
                'community_sizes': dict(community_sizes)
            }

        except ImportError:
            print("    Warning: python-louvain not installed. Skipping Louvain.")
            return {}

    def _detect_label_propagation(self, G: nx.Graph) -> Dict[str, Any]:
        """
        Detect communities using label propagation.

        Args:
            G: NetworkX graph

        Returns:
            Community assignment and metrics
        """
        communities = nx.community.label_propagation_communities(G)

        # Convert to partition dict
        partition = {}
        for i, comm in enumerate(communities):
            for node in comm:
                partition[node] = i

        # Calculate community sizes
        community_sizes = defaultdict(int)
        for comm_id in partition.values():
            community_sizes[comm_id] += 1

        num_communities = len(community_sizes)

        print(f"    Found {num_communities} communities")

        return {
            'partition': partition,
            'num_communities': num_communities,
            'community_sizes': dict(community_sizes)
        }

    def _detect_girvan_newman(self, G: nx.Graph, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Detect communities using Girvan-Newman algorithm.

        Args:
            G: NetworkX graph
            config: Algorithm configuration

        Returns:
            Community assignment and metrics
        """
        levels = config.get('levels', 3)

        # Run Girvan-Newman
        communities_generator = nx.community.girvan_newman(G)

        # Get communities at specified level
        for i in range(levels):
            try:
                communities = next(communities_generator)
            except StopIteration:
                break

        # Convert to partition dict
        partition = {}
        for i, comm in enumerate(communities):
            for node in comm:
                partition[node] = i

        # Calculate community sizes
        community_sizes = defaultdict(int)
        for comm_id in partition.values():
            community_sizes[comm_id] += 1

        num_communities = len(community_sizes)

        print(f"    Found {num_communities} communities at level {levels}")

        return {
            'partition': partition,
            'num_communities': num_communities,
            'community_sizes': dict(community_sizes),
            'levels': levels
        }

    def get_community_info(self, G: nx.Graph, partition: Dict[str, int], entities_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Get detailed information about each community.

        Args:
            G: NetworkX graph
            partition: Community assignment (node -> community_id)
            entities_data: Entity data

        Returns:
            List of community information dicts
        """
        # Group nodes by community
        communities = defaultdict(list)
        for node, comm_id in partition.items():
            communities[comm_id].append(node)

        community_info = []

        for comm_id, nodes in communities.items():
            # Get subgraph for this community
            subgraph = G.subgraph(nodes)

            # Get most central nodes
            if len(nodes) > 0:
                degree_centrality = nx.degree_centrality(subgraph)
                top_nodes = sorted(degree_centrality.items(), key=lambda x: x[1], reverse=True)[:5]
            else:
                top_nodes = []

            # Generate community label from top nodes
            if top_nodes:
                label = " / ".join([node for node, _ in top_nodes[:2]])
            else:
                label = f"Community {comm_id}"

            info = {
                'id': comm_id,
                'label': label,
                'size': len(nodes),
                'nodes': nodes,
                'top_nodes': [{'name': node, 'centrality': cent} for node, cent in top_nodes],
                'density': nx.density(subgraph) if len(nodes) > 1 else 0
            }

            community_info.append(info)

        # Sort by size
        community_info.sort(key=lambda x: x['size'], reverse=True)

        return community_info

    def add_communities_to_graph(self, G: nx.Graph, partition: Dict[str, int]):
        """
        Add community assignments as node attributes.

        Args:
            G: NetworkX graph
            partition: Community assignment (node -> community_id)
        """
        for node, comm_id in partition.items():
            if node in G.nodes():
                G.nodes[node]['community'] = comm_id
