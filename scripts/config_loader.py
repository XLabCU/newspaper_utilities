#!/usr/bin/env python3
"""
Configuration loader for newspaper utilities dashboard.
Provides project metadata and configuration settings.
"""

import json
from pathlib import Path


class ConfigLoader:
    """Loads and manages project configuration."""

    def __init__(self, config_path=None):
        """
        Initialize config loader.

        Args:
            config_path: Optional path to config JSON file
        """
        self.config = {}

        if config_path and Path(config_path).exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        else:
            # Default configuration
            self.config = {
                'project': {
                    'name': 'Historical Newspaper Analysis',
                    'description': 'OCR and analysis of historical newspaper archives'
                },
                'dashboard': {
                    'theme': 'steampunk',
                    'show_images': True,
                    'show_network': True
                }
            }

    def get_project_metadata(self):
        """Get project metadata dictionary."""
        return self.config.get('project', {
            'name': 'Historical Newspaper Analysis',
            'description': 'OCR and analysis of historical newspaper archives'
        })

    def get_dashboard_config(self):
        """Get dashboard configuration."""
        return self.config.get('dashboard', {})


def load_config(config_path=None):
    """
    Load configuration from file or use defaults.

    Args:
        config_path: Optional path to config JSON file

    Returns:
        ConfigLoader instance
    """
    return ConfigLoader(config_path)
