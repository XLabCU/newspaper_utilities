"""
Entity extraction using spaCy NER with configurable entity types.
"""

import spacy
from collections import defaultdict
from typing import List, Dict, Any, Set


class EntityExtractor:
    """Extract named entities from articles using spaCy."""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize entity extractor.

        Args:
            config: Entity extraction configuration
        """
        self.config = config
        self.nlp = None
        self._load_model()

        # Get enabled entity types
        self.enabled_types = self._get_enabled_types()

        # Get filtering config
        self.filtering = config.get('filtering', {})

    def _load_model(self):
        """Load spaCy model."""
        print("Loading spaCy model...")
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            print("Downloading spaCy English model...")
            import subprocess
            subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"])
            self.nlp = spacy.load("en_core_web_sm")

    def _get_enabled_types(self) -> Set[str]:
        """Get set of enabled entity types from config."""
        entity_types = self.config.get('entity_types', [])
        return {
            et['name'] for et in entity_types
            if et.get('enabled', True)
        }

    def _should_skip_entity(self, entity_text: str, entity_type: str) -> bool:
        """
        Check if entity should be skipped based on filtering rules.

        Args:
            entity_text: The entity text
            entity_type: The entity type (PERSON, ORG, etc.)

        Returns:
            True if entity should be skipped
        """
        # Check minimum length
        min_length = self.filtering.get('min_entity_length', 3)
        if len(entity_text) < min_length:
            return True

        # Check maximum length
        max_length = self.filtering.get('max_entity_length', 100)
        if len(entity_text) > max_length:
            return True

        # Check single character
        if self.filtering.get('skip_single_char', True) and len(entity_text) <= 1:
            return True

        # Check all caps (likely OCR errors)
        if self.filtering.get('skip_all_caps', True):
            if entity_text.isupper() and len(entity_text) > 1:
                return True

        return False

    def extract(self, articles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Extract entities from articles.

        Args:
            articles: List of article dictionaries

        Returns:
            Dictionary with entity counts and article-entity mappings
        """
        # Entity counts by type
        people = defaultdict(int)
        places = defaultdict(int)
        organizations = defaultdict(int)
        other_entities = defaultdict(lambda: defaultdict(int))

        # Article-entity mappings
        article_entities = []

        print(f"Processing {len(articles)} articles for entity extraction...")

        for i, article in enumerate(articles):
            if (i + 1) % 100 == 0:
                print(f"  Processed {i + 1}/{len(articles)} articles...")

            article_id = article['article_id']
            text = article.get('full_text', '')
            headline = article.get('headline', '')
            combined_text = f"{headline}. {text}"

            # Skip if no text
            if not combined_text.strip():
                continue

            # Process with spaCy (limit to first 1000000 chars for performance)
            doc = self.nlp(combined_text[:1000000])

            # Extract entities by type
            article_people = set()
            article_places = set()
            article_orgs = set()
            article_other = defaultdict(set)

            for ent in doc.ents:
                # Skip if not enabled type
                if ent.label_ not in self.enabled_types:
                    continue

                # Clean entity text
                entity_text = ent.text.strip()

                # Apply filtering rules
                if self._should_skip_entity(entity_text, ent.label_):
                    continue

                # Categorize by type
                if ent.label_ == 'PERSON':
                    people[entity_text] += 1
                    article_people.add(entity_text)
                elif ent.label_ in ['GPE', 'LOC']:
                    places[entity_text] += 1
                    article_places.add(entity_text)
                elif ent.label_ == 'ORG':
                    organizations[entity_text] += 1
                    article_orgs.add(entity_text)
                else:
                    # Other entity types
                    other_entities[ent.label_][entity_text] += 1
                    article_other[ent.label_].add(entity_text)

            # Store article-entity mapping (only if has entities)
            if article_people or article_places or article_orgs or article_other:
                mapping = {
                    'article_id': article_id,
                    'date': article.get('date'),
                    'tags': [t['tag'] for t in article.get('tags', [])],
                    'people': list(article_people),
                    'places': list(article_places),
                    'organizations': list(article_orgs)
                }

                # Add other entity types
                for entity_type, entities in article_other.items():
                    mapping[entity_type.lower()] = list(entities)

                article_entities.append(mapping)

        print(f"Extracted {len(people)} unique people, {len(places)} unique places, "
              f"{len(organizations)} unique organizations")

        return {
            'people': dict(people),
            'places': dict(places),
            'organizations': dict(organizations),
            'other_entities': {
                entity_type: dict(entities)
                for entity_type, entities in other_entities.items()
            },
            'article_entities': article_entities
        }

    def filter_by_mentions(self, entities_data: Dict[str, Any], min_mentions: int = None) -> Dict[str, Any]:
        """
        Filter entities to only include those mentioned at least min_mentions times.

        Args:
            entities_data: Raw entity extraction data
            min_mentions: Minimum number of mentions (uses config default if None)

        Returns:
            Filtered entity data
        """
        if min_mentions is None:
            min_mentions = self.filtering.get('min_mentions', 2)

        # Filter each entity type
        filtered_people = {k: v for k, v in entities_data['people'].items() if v >= min_mentions}
        filtered_places = {k: v for k, v in entities_data['places'].items() if v >= min_mentions}
        filtered_orgs = {k: v for k, v in entities_data['organizations'].items() if v >= min_mentions}

        # Filter other entity types
        filtered_other = {}
        for entity_type, entities in entities_data.get('other_entities', {}).items():
            filtered_other[entity_type] = {k: v for k, v in entities.items() if v >= min_mentions}

        # Get all filtered entity names
        filtered_entities = (
            set(filtered_people.keys()) |
            set(filtered_places.keys()) |
            set(filtered_orgs.keys()) |
            set(e for entities in filtered_other.values() for e in entities.keys())
        )

        # Filter article entities to only include filtered entities
        filtered_article_entities = []
        for article in entities_data['article_entities']:
            filtered_article = {
                **article,
                'people': [p for p in article['people'] if p in filtered_people],
                'places': [p for p in article['places'] if p in filtered_places],
                'organizations': [o for o in article['organizations'] if o in filtered_orgs]
            }

            # Filter other entity types
            for entity_type, entities in filtered_other.items():
                key = entity_type.lower()
                if key in article:
                    filtered_article[key] = [e for e in article[key] if e in entities]

            # Only include if article has at least one filtered entity
            has_entities = (
                filtered_article['people'] or
                filtered_article['places'] or
                filtered_article['organizations'] or
                any(filtered_article.get(et.lower(), []) for et in filtered_other.keys())
            )

            if has_entities:
                filtered_article_entities.append(filtered_article)

        print(f"After filtering (min {min_mentions} mentions):")
        print(f"  People: {len(filtered_people)}")
        print(f"  Places: {len(filtered_places)}")
        print(f"  Organizations: {len(filtered_orgs)}")
        for entity_type, entities in filtered_other.items():
            print(f"  {entity_type}: {len(entities)}")
        print(f"  Articles with entities: {len(filtered_article_entities)}")

        return {
            'people': filtered_people,
            'places': filtered_places,
            'organizations': filtered_orgs,
            'other_entities': filtered_other,
            'article_entities': filtered_article_entities
        }
