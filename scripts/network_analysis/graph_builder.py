"""
Graph construction for entity networks.
"""

import networkx as nx
from typing import Dict, Any, List
from collections import defaultdict
from datetime import datetime


class GraphBuilder:
    """Build various types of entity networks."""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize graph builder.

        Args:
            config: Network analysis configuration
        """
        self.config = config
        self.graphs_config = config.get('graphs', [])

    def build_all_networks(self, entities_data: Dict[str, Any], articles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Build all configured network types.

        Args:
            entities_data: Processed entity data
            articles: List of articles

        Returns:
            Dictionary of network graphs
        """
        networks = {}

        for graph_config in self.graphs_config:
            if not graph_config.get('enabled', True):
                continue

            graph_type = graph_config['type']
            graph_name = graph_config['name']

            print(f"Building {graph_name} network...")

            if graph_type == 'cooccurrence':
                networks[graph_name] = self.build_cooccurrence_network(
                    entities_data, graph_config.get('parameters', {})
                )
            elif graph_type == 'temporal':
                networks[graph_name] = self.build_temporal_network(
                    entities_data, articles, graph_config.get('parameters', {})
                )
            elif graph_type == 'bipartite':
                networks[graph_name] = self.build_bipartite_network(
                    entities_data, graph_config.get('parameters', {})
                )
            elif graph_type == 'tag_based':
                networks[graph_name] = self.build_tag_based_network(
                    entities_data, graph_config.get('parameters', {})
                )

        return networks

    def build_cooccurrence_network(self, entities_data: Dict[str, Any], parameters: Dict[str, Any]) -> nx.Graph:
        """
        Build entity co-occurrence network.

        Args:
            entities_data: Entity extraction data
            parameters: Network parameters

        Returns:
            NetworkX graph
        """
        G = nx.Graph()
        min_cooccurrences = parameters.get('min_cooccurrences', 2)
        weight_by_frequency = parameters.get('weight_by_frequency', True)

        # Build edge weights from article entities
        edge_weights = defaultdict(int)

        for article in entities_data.get('article_entities', []):
            # Get all entities in this article
            all_entities = []
            all_entities.extend(article.get('people', []))
            all_entities.extend(article.get('places', []))
            all_entities.extend(article.get('organizations', []))

            # Add other entity types
            for key, value in article.items():
                if key not in ['article_id', 'date', 'tags', 'people', 'places', 'organizations']:
                    if isinstance(value, list):
                        all_entities.extend(value)

            # Create edges between all pairs
            for i, entity1 in enumerate(all_entities):
                for entity2 in all_entities[i+1:]:
                    edge = tuple(sorted([entity1, entity2]))
                    edge_weights[edge] += 1

        # Add edges that meet minimum threshold
        for (entity1, entity2), weight in edge_weights.items():
            if weight >= min_cooccurrences:
                if weight_by_frequency:
                    G.add_edge(entity1, entity2, weight=weight)
                else:
                    G.add_edge(entity1, entity2, weight=1)

        # Add node attributes
        self._add_node_attributes(G, entities_data)

        print(f"  Co-occurrence network: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")

        return G

    def build_temporal_network(self, entities_data: Dict[str, Any], articles: List[Dict[str, Any]],
                              parameters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Build temporal network (time-sliced).

        Args:
            entities_data: Entity extraction data
            articles: List of articles
            parameters: Network parameters

        Returns:
            List of temporal graph snapshots
        """
        time_slices = parameters.get('time_slices', 'month')

        # Group articles by time period
        temporal_groups = defaultdict(list)

        for article in entities_data.get('article_entities', []):
            date_str = article.get('date')
            if not date_str:
                continue

            try:
                date = datetime.strptime(date_str, "%Y-%m-%d")

                # Group by time slice
                if time_slices == 'day':
                    period = date.strftime("%Y-%m-%d")
                elif time_slices == 'week':
                    period = date.strftime("%Y-W%W")
                elif time_slices == 'month':
                    period = date.strftime("%Y-%m")
                elif time_slices == 'quarter':
                    quarter = (date.month - 1) // 3 + 1
                    period = f"{date.year}-Q{quarter}"
                elif time_slices == 'year':
                    period = str(date.year)
                else:
                    period = date.strftime("%Y-%m")

                temporal_groups[period].append(article)
            except:
                continue

        # Build network for each time period
        temporal_graphs = []

        for period in sorted(temporal_groups.keys()):
            articles_in_period = temporal_groups[period]

            # Create temporary entities data for this period
            period_data = {'article_entities': articles_in_period}

            # Build co-occurrence network for this period
            G = self.build_cooccurrence_network(period_data, parameters)

            temporal_graphs.append({
                'period': period,
                'graph': G,
                'article_count': len(articles_in_period)
            })

        print(f"  Temporal network: {len(temporal_graphs)} time periods")

        return temporal_graphs

    def build_bipartite_network(self, entities_data: Dict[str, Any], parameters: Dict[str, Any]) -> nx.Graph:
        """
        Build bipartite network of entities and articles.

        Args:
            entities_data: Entity extraction data
            parameters: Network parameters

        Returns:
            NetworkX bipartite graph
        """
        G = nx.Graph()

        for article in entities_data.get('article_entities', []):
            article_id = article['article_id']

            # Add article node
            G.add_node(article_id, bipartite=0, node_type='article')

            # Get all entities
            all_entities = []
            all_entities.extend(article.get('people', []))
            all_entities.extend(article.get('places', []))
            all_entities.extend(article.get('organizations', []))

            # Add edges to all entities
            for entity in all_entities:
                G.add_node(entity, bipartite=1, node_type='entity')
                G.add_edge(article_id, entity)

        print(f"  Bipartite network: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")

        return G

    def build_tag_based_network(self, entities_data: Dict[str, Any], parameters: Dict[str, Any]) -> Dict[str, nx.Graph]:
        """
        Build separate networks for each tag.

        Args:
            entities_data: Entity extraction data
            parameters: Network parameters

        Returns:
            Dictionary mapping tag names to networks
        """
        tags = parameters.get('tags', [])
        cross_tag_edges = parameters.get('cross_tag_edges', False)

        tag_networks = {}

        for tag in tags:
            # Filter articles by tag
            tag_articles = [
                article for article in entities_data.get('article_entities', [])
                if tag in article.get('tags', [])
            ]

            if not tag_articles:
                continue

            # Build network for this tag
            tag_data = {'article_entities': tag_articles}
            G = self.build_cooccurrence_network(tag_data, parameters)

            tag_networks[tag] = G

            print(f"  Tag '{tag}' network: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")

        return tag_networks

    def _add_node_attributes(self, G: nx.Graph, entities_data: Dict[str, Any]):
        """
        Add attributes to nodes based on entity data.

        Args:
            G: NetworkX graph
            entities_data: Entity extraction data
        """
        # Combine all entity counts
        all_entities = {}
        all_entities.update({k: ('PERSON', v) for k, v in entities_data.get('people', {}).items()})
        all_entities.update({k: ('PLACE', v) for k, v in entities_data.get('places', {}).items()})
        all_entities.update({k: ('ORG', v) for k, v in entities_data.get('organizations', {}).items()})

        # Add attributes to nodes
        for node in G.nodes():
            if node in all_entities:
                entity_type, mentions = all_entities[node]
                G.nodes[node]['type'] = entity_type
                G.nodes[node]['mentions'] = mentions
            else:
                G.nodes[node]['type'] = 'UNKNOWN'
                G.nodes[node]['mentions'] = 0

    def filter_network(self, G: nx.Graph, filtering_config: Dict[str, Any]) -> nx.Graph:
        """
        Filter network based on configuration.

        Args:
            G: NetworkX graph
            filtering_config: Filtering parameters

        Returns:
            Filtered graph
        """
        min_degree = filtering_config.get('min_degree', 1)
        min_edge_weight = filtering_config.get('min_edge_weight', 0)
        top_n_nodes = filtering_config.get('top_n_nodes')
        giant_component_only = filtering_config.get('giant_component_only', False)

        # Create filtered graph
        filtered_G = G.copy()

        # Remove low-weight edges
        if min_edge_weight > 0:
            edges_to_remove = [
                (u, v) for u, v, data in filtered_G.edges(data=True)
                if data.get('weight', 1) < min_edge_weight
            ]
            filtered_G.remove_edges_from(edges_to_remove)

        # Remove low-degree nodes
        if min_degree > 1:
            nodes_to_remove = [node for node in filtered_G.nodes() if filtered_G.degree(node) < min_degree]
            filtered_G.remove_nodes_from(nodes_to_remove)

        # Keep only top N nodes by degree
        if top_n_nodes:
            degrees = dict(filtered_G.degree())
            top_nodes = sorted(degrees.items(), key=lambda x: x[1], reverse=True)[:top_n_nodes]
            nodes_to_keep = {node for node, _ in top_nodes}
            nodes_to_remove = set(filtered_G.nodes()) - nodes_to_keep
            filtered_G.remove_nodes_from(nodes_to_remove)

        # Keep only giant component
        if giant_component_only and nx.is_connected(filtered_G) is False:
            largest_cc = max(nx.connected_components(filtered_G), key=len)
            nodes_to_remove = set(filtered_G.nodes()) - largest_cc
            filtered_G.remove_nodes_from(nodes_to_remove)

        return filtered_G
