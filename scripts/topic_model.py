#!/usr/bin/env python3
"""
Step 7: Topic Modeling (LDA)
- Identifies latent topics within the corpus or specific comparison groups.
- Outputs topic distributions and top keywords for dashboard visualization.
"""

import json
import re
import argparse
from pathlib import Path
from datetime import datetime
from collections import Counter

# Using sklearn for a lightweight, standard implementation
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation

from config_loader import load_config

# Default stop words (I need to update analyze_text.py with this)
def load_stop_words():
    """Load stop words from mallet.txt in the script's directory."""
    stop_words = set()
    
    # Path to mallet.txt relative to this script
    mallet_path = Path(__file__).parent / "mallet.txt"
    
    if mallet_path.exists():
        try:
            with open(mallet_path, 'r', encoding='utf-8') as f:
                for line in f:
                    word = line.strip().lower()
                    # Ignore empty lines and comments
                    if word and not word.startswith('#'):
                        stop_words.add(word)
            print(f"Loaded {len(stop_words)} stop words from {mallet_path.name}")
        except Exception as e:
            print(f"Error reading mallet.txt: {e}. Using minimal fallback.")
            stop_words = {'the', 'and', 'that', 'with', 'for', 'was'}
    else:
        print(f"Warning: {mallet_path} not found. Using minimal fallback.")
        stop_words = {'the', 'and', 'that', 'with', 'for', 'was'}
        
    return stop_words

def clean_text(text):
    """Basic cleaning for topic modeling."""
    if not text:
        return ""
    text = text.lower()
    # Remove numbers and short words
    text = re.sub(r'\b\d+\b', '', text)
    text = re.sub(r'[^\w\s]', ' ', text)
    return text

def filter_articles(articles, filter_config):
    """Filters articles based on the config (reused from analyze_text.py)."""
    if not filter_config:
        return articles
    include_tags = filter_config.get('tags', [])
    exclude_tags = filter_config.get('exclude_tags', [])
    filtered = []
    for art in articles:
        art_tags = [t["tag"] for t in art.get("tags", [])]
        if exclude_tags and any(tag in exclude_tags for tag in art_tags):
            continue
        if include_tags:
            if any(tag in include_tags for tag in art_tags):
                filtered.append(art)
        else:
            filtered.append(art)
    return filtered

def run_lda(articles, n_topics=5, n_words=10, stop_words=None):
    """Runs LDA and returns topics and article assignments."""
    texts = [clean_text(art.get("full_text", "") or art.get("text", "")) for art in articles]
    
    # Vectorization
    vectorizer = CountVectorizer(
        stop_words=list(stop_words),
        max_df=0.95, 
        min_df=2,
        max_features=2000
    )
    
    try:
        dtm = vectorizer.fit_transform(texts)
    except ValueError: # Handle cases with too few articles/words
        return [], []

    # LDA Model
    lda = LatentDirichletAllocation(n_components=n_topics, random_state=42)
    lda_output = lda.fit_transform(dtm)

    # Extract Topics
    feature_names = vectorizer.get_feature_names_out()
    topics = []
    for topic_idx, topic in enumerate(lda.components_):
        top_indices = topic.argsort()[:-n_words - 1:-1]
        top_words = [{"word": feature_names[i], "weight": float(topic[i])} for i in top_indices]
        topics.append({
            "topic_id": topic_idx,
            "top_words": top_words
        })

    # Assign Dominant Topic to Articles
    assignments = []
    for i, probs in enumerate(lda_output):
        dominant_topic = int(probs.argmax())
        assignments.append({
            "article_id": articles[i].get("id", i),
            "date": articles[i].get("date", ""),
            "topic_id": dominant_topic,
            "confidence": round(float(probs[dominant_topic]), 3)
        })

    return topics, assignments

def main():
    parser = argparse.ArgumentParser(description="Topic Modeling for Newspaper Articles")
    parser.add_argument('--config', type=str, default=None, help='Path to config')
    # Default is None here so we can tell if the user actually typed it
    parser.add_argument('--topics', type=int, default=None, help='Override number of topics')
    args = parser.parse_args()

    # Load configuration
    config = load_config(args.config)
    analysis_config = config.get_text_analysis_config()
    
    # --- The Logic ---
    # 1. Get value from YAML (default to 5 if section/key missing)
    topic_cfg = analysis_config.get('topic_modeling', {})
    n_topics = topic_cfg.get('n_topics', 5)

    # 2. If user provided a flag in the terminal, it overrides the YAML
    if args.topics is not None:
        n_topics = args.topics
    
    print(f"Running model with {n_topics} topics...")
    
    # 3. Load Mallet stop words
    mallet_stopwords = load_stop_words()
    
    # 4. Combine with custom stop words from YAML config
    custom_stopwords = set(analysis_config.get('custom_stopwords', []))
    stop_words = mallet_stopwords | custom_stopwords
    
    # Path setup
    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent
    input_file = project_root / "data" / "processed" / "tagged_articles.json"
    output_file = project_root / "data" / "processed" / "topic_model.json"

    if not input_file.exists():
        print(f"Error: {input_file} not found.")
        return

    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    all_articles = data.get("articles", [])

    # We run LDA on the Comparison Groups defined in the YAML
    # (e.g., one model for Ripper news, one for General news)
    comparison_groups = analysis_config.get('comparison_groups', [])
    model_results = []

    for group in comparison_groups:
        print(f"Modeling topics for: {group['label']}...")
        group_articles = filter_articles(all_articles, group.get('filter', {}))
        
        if len(group_articles) < 5:
            print(f"  Skipping {group['label']}: Not enough articles.")
            continue

        topics, assignments = run_lda(
            group_articles, 
            n_topics=args.topics, 
            stop_words=stop_words
        )

        # Calculate topic prevalence over time (useful for dashboard)
        timeline_data = defaultdict(Counter)
        for entry in assignments:
            month = entry['date'][:7] if entry['date'] else "Unknown"
            timeline_data[month][entry['topic_id']] += 1

        model_results.append({
            "group_id": group['id'],
            "group_label": group['label'],
            "topics": topics,
            "assignments": assignments,
            "temporal_distribution": timeline_data
        })

    # Final JSON structure
    report = {
        "metadata": {
            "project_name": config.get_project_metadata()['name'],
            "generated_at": datetime.now().isoformat(),
            "topic_count_requested": args.topics
        },
        "models": model_results
    }

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"Topic modeling complete. Results saved to {output_file}")

from collections import defaultdict
if __name__ == "__main__":
    main()