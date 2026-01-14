"""
Entity extraction module for newspaper utilities.
Provides configurable entity extraction, normalization, and custom dictionaries.
"""

from .extractor import EntityExtractor
from .normalizer import EntityNormalizer

__all__ = ['EntityExtractor', 'EntityNormalizer']
