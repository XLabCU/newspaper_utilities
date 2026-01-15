"""
Entity normalization and aliasing.
"""

from typing import Dict, Any, List
from collections import defaultdict


class EntityNormalizer:
    """Normalize entity names using aliases and fuzzy matching."""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize entity normalizer.

        Args:
            config: Entity extraction configuration
        """
        self.config = config
        self.normalization_config = config.get('normalization', {})
        self.enabled = self.normalization_config.get('enabled', False)

        # Load aliases
        self.aliases = self._load_aliases()

        # Fuzzy matching config
        self.fuzzy_config = self.normalization_config.get('fuzzy_matching', {})
        self.fuzzy_enabled = self.fuzzy_config.get('enabled', False)
        self.fuzzy_threshold = self.fuzzy_config.get('threshold', 0.85)

        # Import fuzzy matching libraries if needed
        if self.fuzzy_enabled:
            try:
                from fuzzywuzzy import fuzz
                self.fuzz = fuzz
            except ImportError:
                print("Warning: fuzzywuzzy not installed. Fuzzy matching disabled.")
                self.fuzzy_enabled = False

    def _load_aliases(self) -> Dict[str, List[str]]:
        """
        Load alias mappings from config.

        Returns:
            Dictionary mapping canonical names to lists of aliases
        """
        return self.normalization_config.get('aliases', {})

    def _get_canonical_name(self, entity_name: str) -> str:
        """
        Get canonical name for an entity using alias mappings.

        Args:
            entity_name: Entity name to normalize

        Returns:
            Canonical name (or original if no alias found)
        """
        # Check if this name is in any alias list
        for canonical, alias_list in self.aliases.items():
            if entity_name in alias_list:
                return canonical
            # Case-insensitive check
            if entity_name.lower() in [a.lower() for a in alias_list]:
                return canonical

        return entity_name

    def _fuzzy_match(self, entity_name: str, known_entities: List[str]) -> str:
        """
        Find best fuzzy match for entity name.

        Args:
            entity_name: Entity name to match
            known_entities: List of known entity names

        Returns:
            Best match or original name if no good match
        """
        if not self.fuzzy_enabled or not known_entities:
            return entity_name

        best_match = entity_name
        best_score = 0

        for known in known_entities:
            # Skip if same length difference is too large
            if abs(len(entity_name) - len(known)) > 3:
                continue

            # Calculate similarity
            score = self.fuzz.ratio(entity_name.lower(), known.lower()) / 100.0

            if score > best_score and score >= self.fuzzy_threshold:
                best_score = score
                best_match = known

        return best_match

    def normalize(self, entities_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize entity names using aliases and fuzzy matching.

        Args:
            entities_data: Raw entity extraction data

        Returns:
            Normalized entity data
        """
        if not self.enabled:
            return entities_data

        print("Normalizing entity names...")

        # Track normalization statistics
        normalization_count = 0

        # Normalize each entity type
        normalized_people = self._normalize_entity_dict(entities_data.get('people', {}))
        normalized_places = self._normalize_entity_dict(entities_data.get('places', {}))
        normalized_orgs = self._normalize_entity_dict(entities_data.get('organizations', {}))

        # Normalize other entity types
        normalized_other = {}
        for entity_type, entities in entities_data.get('other_entities', {}).items():
            normalized_other[entity_type] = self._normalize_entity_dict(entities)

        # Normalize article entities
        normalized_article_entities = []
        for article in entities_data.get('article_entities', []):
            normalized_article = {
                **article,
                'people': [self._get_canonical_name(p) for p in article.get('people', [])],
                'places': [self._get_canonical_name(p) for p in article.get('places', [])],
                'organizations': [self._get_canonical_name(o) for o in article.get('organizations', [])]
            }

            # Normalize other entity types
            for entity_type in normalized_other.keys():
                key = entity_type.lower()
                if key in article:
                    normalized_article[key] = [
                        self._get_canonical_name(e) for e in article[key]
                    ]

            normalized_article_entities.append(normalized_article)

        print(f"Entity normalization complete")

        return {
            'people': normalized_people,
            'places': normalized_places,
            'organizations': normalized_orgs,
            'other_entities': normalized_other,
            'article_entities': normalized_article_entities
        }

    def _normalize_entity_dict(self, entity_dict: Dict[str, int]) -> Dict[str, int]:
        """
        Normalize a dictionary of entities.

        Args:
            entity_dict: Dictionary mapping entity names to counts

        Returns:
            Normalized dictionary with canonical names
        """
        normalized = defaultdict(int)

        # First pass: Apply alias mappings
        for entity_name, count in entity_dict.items():
            canonical = self._get_canonical_name(entity_name)
            normalized[canonical] += count

        # Second pass: Fuzzy matching (optional)
        if self.fuzzy_enabled:
            final_normalized = defaultdict(int)
            known_entities = list(normalized.keys())

            for entity_name, count in normalized.items():
                matched_name = self._fuzzy_match(entity_name, known_entities)
                final_normalized[matched_name] += count

            return dict(final_normalized)

        return dict(normalized)

    def add_alias(self, canonical_name: str, alias: str):
        """
        Add a new alias mapping.

        Args:
            canonical_name: The canonical/standard name
            alias: The alias/variant to map to canonical
        """
        if canonical_name not in self.aliases:
            self.aliases[canonical_name] = []

        if alias not in self.aliases[canonical_name]:
            self.aliases[canonical_name].append(alias)

    def get_normalization_stats(self, original_data: Dict[str, Any], normalized_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get statistics about normalization effects.

        Args:
            original_data: Original entity data
            normalized_data: Normalized entity data

        Returns:
            Dictionary with normalization statistics
        """
        stats = {
            'people': {
                'original_count': len(original_data.get('people', {})),
                'normalized_count': len(normalized_data.get('people', {})),
                'reduction': len(original_data.get('people', {})) - len(normalized_data.get('people', {}))
            },
            'places': {
                'original_count': len(original_data.get('places', {})),
                'normalized_count': len(normalized_data.get('places', {})),
                'reduction': len(original_data.get('places', {})) - len(normalized_data.get('places', {}))
            },
            'organizations': {
                'original_count': len(original_data.get('organizations', {})),
                'normalized_count': len(normalized_data.get('organizations', {})),
                'reduction': len(original_data.get('organizations', {})) - len(normalized_data.get('organizations', {}))
            }
        }

        return stats
