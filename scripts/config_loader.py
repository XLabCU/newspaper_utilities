#!/usr/bin/env python3
"""
Configuration loader for newspaper utilities pipeline.
Handles loading and validation of YAML configuration files.
"""

import yaml
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
import copy


class ConfigLoader:
    """Load and manage configuration for newspaper analysis pipeline."""

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize configuration loader.

        Args:
            config_path: Path to project config file. If None, uses default config.
        """
        self.config_path = config_path
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or use defaults."""
        # Load default config
        default_config = self._get_default_config()

        # If no custom config specified, return defaults
        if not self.config_path:
            return default_config

        # Load custom config
        config_file = Path(self.config_path)
        if not config_file.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")

        with open(config_file, 'r') as f:
            custom_config = yaml.safe_load(f)

        # Merge custom config with defaults
        merged_config = self._merge_configs(default_config, custom_config)

        return merged_config

    def _get_default_config(self) -> Dict[str, Any]:
        """Return default configuration."""
        return {
            'project': {
                'name': 'Newspaper Analysis',
                'description': 'Historical newspaper content analysis',
                'researcher': '',
                'date_range': []
            },
            'tags': [
                {
                    'id': 'general',
                    'label': 'General Content',
                    'keywords': [],
                    'weight': 1,
                    'color': '#808080'
                }
            ],
            'timeline': {
                'reference_events': [],
                'correlation_tags': [],
                'local_label': 'Local Publications',
                'reference_label': 'Reference Events'
            },
            'text_analysis': {
                'comparison_groups': [
                    {
                        'id': 'all_articles',
                        'label': 'All Articles',
                        'description': 'All articles in corpus',
                        'filter': {}
                    }
                ],
                'sensational_keywords': [
                    'horror', 'horrible', 'terrible', 'shocking', 'brutal',
                    'savage', 'fiend', 'monster', 'ghastly', 'dreadful',
                    'frightful', 'atrocious', 'heinous', 'gruesome', 'grisly'
                ],
                'custom_stopwords': [],
                'wordcloud': {
                    'max_words': 50,
                    'min_word_length': 3
                }
            },
            'entity_extraction': {
                'entity_types': [
                    {'name': 'PERSON', 'enabled': True, 'color': '#FF6B6B', 'icon': 'person'},
                    {'name': 'ORG', 'enabled': True, 'color': '#4ECDC4', 'icon': 'organization'},
                    {'name': 'GPE', 'enabled': True, 'color': '#45B7D1', 'icon': 'location'},
                    {'name': 'LOC', 'enabled': True, 'color': '#96CEB4', 'icon': 'location'}
                ],
                'filtering': {
                    'min_mentions': 2,
                    'min_entity_length': 3,
                    'max_entity_length': 100,
                    'skip_all_caps': True,
                    'skip_single_char': True
                },
                'normalization': {
                    'enabled': False,
                    'aliases': {},
                    'fuzzy_matching': {
                        'enabled': False,
                        'threshold': 0.85
                    }
                },
                'custom_dictionaries': {}
            },
            'network_analysis': {
                'graphs': [
                    {
                        'name': 'entity_cooccurrence',
                        'enabled': True,
                        'description': 'Entities appearing in same article',
                        'type': 'cooccurrence',
                        'parameters': {
                            'window': 'article',
                            'min_cooccurrences': 2,
                            'weight_by_frequency': True
                        }
                    }
                ],
                'metrics': {
                    'node_metrics': [
                        'degree_centrality',
                        'betweenness_centrality',
                        'pagerank'
                    ],
                    'graph_metrics': [
                        'density',
                        'diameter',
                        'average_path_length'
                    ],
                    'temporal_metrics': []
                },
                'community_detection': {
                    'enabled': False,
                    'algorithms': []
                },
                'filtering': {
                    'min_degree': 1,
                    'min_edge_weight': 0.1,
                    'top_n_nodes': None,
                    'giant_component_only': False
                }
            },
            'dashboard': {
                'title': 'Newspaper Analysis Dashboard',
                'sections': [
                    'tag_distribution',
                    'text_analysis',
                    'article_browser'
                ],
                'theme': {
                    'primary_color': '#2C3E50',
                    'secondary_color': '#3498DB',
                    'background': '#ECF0F1'
                }
            }
        }

    def _merge_configs(self, default: Dict[str, Any], custom: Dict[str, Any]) -> Dict[str, Any]:
        """
        Deep merge custom config into default config.

        Args:
            default: Default configuration
            custom: Custom configuration to overlay

        Returns:
            Merged configuration
        """
        merged = copy.deepcopy(default)

        for key, value in custom.items():
            if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
                merged[key] = self._merge_configs(merged[key], value)
            else:
                merged[key] = value

        return merged

    def get_tags(self) -> List[Dict[str, Any]]:
        """Get tag definitions from config."""
        return self.config.get('tags', [])

    def get_timeline_config(self) -> Dict[str, Any]:
        """Get timeline configuration."""
        return self.config.get('timeline', {})

    def get_text_analysis_config(self) -> Dict[str, Any]:
        """Get text analysis configuration."""
        return self.config.get('text_analysis', {})

    def get_entity_config(self) -> Dict[str, Any]:
        """Get entity extraction configuration."""
        return self.config.get('entity_extraction', {})

    def get_network_config(self) -> Dict[str, Any]:
        """Get network analysis configuration."""
        return self.config.get('network_analysis', {})

    def get_dashboard_config(self) -> Dict[str, Any]:
        """Get dashboard configuration."""
        return self.config.get('dashboard', {})

    def get_project_metadata(self) -> Dict[str, Any]:
        """Get project metadata."""
        return self.config.get('project', {})

    def validate_config(self) -> bool:
        """
        Validate configuration structure.

        Returns:
            True if valid, raises ValueError if invalid
        """
        # Check required top-level keys
        required_keys = ['project', 'tags']
        for key in required_keys:
            if key not in self.config:
                raise ValueError(f"Missing required config key: {key}")

        # Validate tags
        if not isinstance(self.config['tags'], list) or len(self.config['tags']) == 0:
            raise ValueError("Config must have at least one tag defined")

        for tag in self.config['tags']:
            if 'id' not in tag or 'keywords' not in tag:
                raise ValueError(f"Tag missing required fields (id, keywords): {tag}")

        return True

    def save_config(self, output_path: str):
        """
        Save current configuration to file.

        Args:
            output_path: Path to save configuration
        """
        with open(output_path, 'w') as f:
            yaml.dump(self.config, f, default_flow_style=False, sort_keys=False)


def load_config(config_path: Optional[str] = None) -> ConfigLoader:
    """
    Convenience function to load configuration.

    Args:
        config_path: Path to config file, or None for defaults

    Returns:
        ConfigLoader instance
    """
    return ConfigLoader(config_path)


if __name__ == '__main__':
    # Test config loader
    import sys

    if len(sys.argv) > 1:
        config_path = sys.argv[1]
    else:
        config_path = None

    loader = load_config(config_path)
    loader.validate_config()

    print("Configuration loaded successfully!")
    print(f"Project: {loader.get_project_metadata()['name']}")
    print(f"Number of tags: {len(loader.get_tags())}")
    print(f"Timeline events: {len(loader.get_timeline_config().get('reference_events', []))}")
