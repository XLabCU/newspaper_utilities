#!/usr/bin/env python3
"""
Dashboard Generator
Creates a single-page HTML dashboard with interactive visualizations.
"""

import json
import argparse
from pathlib import Path
from datetime import datetime
from config_loader import load_config


def load_data_files(data_dir: Path) -> dict:
    """Load all data files for dashboard."""
    data = {}

    # Required files
    required_files = {
        'tagged_articles': 'tagged_articles.json',
        'timeline': 'timeline.json',
        'text_analysis': 'text_analysis.json',
    }

    # Optional files
    optional_files = {
        'entities': 'entities.json',
        'entity_network': 'entity_network.json',
        'entity_cooccurrence_d3': 'entity-cooccurrence_d3.json',
        'temporal_timeline': 'temporal-network_timeline.json'
    }

    # Load required files
    for key, filename in required_files.items():
        file_path = data_dir / filename
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                data[key] = json.load(f)
        else:
            print(f"Warning: Required file not found: {filename}")
            data[key] = {}

    # Load optional files
    for key, filename in optional_files.items():
        file_path = data_dir / filename
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                data[key] = json.load(f)

    return data


def generate_dashboard_html(data: dict, config_loader, output_path: Path):
    """Generate HTML dashboard."""

    project_metadata = config_loader.get_project_metadata()
    dashboard_config = config_loader.get_dashboard_config()

    # Get project info
    project_name = project_metadata.get('name', 'Newspaper Analysis')
    project_description = project_metadata.get('description', '')

    # Get theme
    theme = dashboard_config.get('theme', {})
    primary_color = theme.get('primary_color', '#2C3E50')
    secondary_color = theme.get('secondary_color', '#E74C3C')
    background = theme.get('background', '#ECF0F1')

    # Prepare data for embedding
    timeline_data = json.dumps(data.get('timeline', {}))
    text_analysis_data = json.dumps(data.get('text_analysis', {}))
    tagged_articles_data = json.dumps(data.get('tagged_articles', {}))
    entity_network_data = json.dumps(data.get('entity_cooccurrence_d3', {}))

    # Generate HTML
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{project_name} - Interactive Dashboard</title>

    <!-- CSS Libraries -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">

    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: {background};
            color: #2c3e50;
            line-height: 1.6;
        }}

        .header {{
            background: linear-gradient(135deg, {primary_color} 0%, {secondary_color} 100%);
            color: white;
            padding: 2rem;
            text-align: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}

        .header h1 {{
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
        }}

        .header p {{
            font-size: 1.1rem;
            opacity: 0.9;
        }}

        .stats-bar {{
            background: white;
            padding: 1.5rem 2rem;
            display: flex;
            justify-content: space-around;
            flex-wrap: wrap;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        }}

        .stat {{
            text-align: center;
            padding: 1rem;
        }}

        .stat-value {{
            font-size: 2rem;
            font-weight: bold;
            color: {primary_color};
        }}

        .stat-label {{
            font-size: 0.9rem;
            color: #7f8c8d;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 2rem;
        }}

        .section {{
            background: white;
            margin-bottom: 2rem;
            border-radius: 10px;
            padding: 2rem;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        }}

        .section-title {{
            font-size: 1.8rem;
            margin-bottom: 1.5rem;
            color: {primary_color};
            border-bottom: 3px solid {secondary_color};
            padding-bottom: 0.5rem;
        }}

        .tabs {{
            display: flex;
            border-bottom: 2px solid #ecf0f1;
            margin-bottom: 2rem;
        }}

        .tab {{
            padding: 1rem 2rem;
            cursor: pointer;
            border: none;
            background: none;
            font-size: 1rem;
            color: #7f8c8d;
            transition: all 0.3s;
        }}

        .tab.active {{
            color: {primary_color};
            border-bottom: 3px solid {secondary_color};
            margin-bottom: -2px;
        }}

        .tab-content {{
            display: none;
        }}

        .tab-content.active {{
            display: block;
        }}

        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 2rem;
        }}

        .card {{
            background: #f8f9fa;
            padding: 1.5rem;
            border-radius: 8px;
            border-left: 4px solid {secondary_color};
        }}

        .card h3 {{
            margin-bottom: 1rem;
            color: {primary_color};
        }}

        #networkGraph {{
            width: 100%;
            height: 600px;
            border: 1px solid #ecf0f1;
            border-radius: 8px;
        }}

        #timelineChart {{
            width: 100%;
            height: 400px;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
        }}

        th, td {{
            padding: 0.75rem;
            text-align: left;
            border-bottom: 1px solid #ecf0f1;
        }}

        th {{
            background: #f8f9fa;
            font-weight: 600;
            color: {primary_color};
        }}

        tr:hover {{
            background: #f8f9fa;
        }}

        .search-box {{
            width: 100%;
            padding: 0.75rem;
            border: 2px solid #ecf0f1;
            border-radius: 5px;
            font-size: 1rem;
            margin-bottom: 1rem;
        }}

        .search-box:focus {{
            outline: none;
            border-color: {primary_color};
        }}

        .tag-filter {{
            display: inline-block;
            padding: 0.5rem 1rem;
            margin: 0.25rem;
            border-radius: 20px;
            cursor: pointer;
            transition: all 0.3s;
            border: 2px solid #ecf0f1;
        }}

        .tag-filter:hover {{
            background: {primary_color};
            color: white;
            border-color: {primary_color};
        }}

        .tag-filter.active {{
            background: {secondary_color};
            color: white;
            border-color: {secondary_color};
        }}

        @media (max-width: 768px) {{
            .header h1 {{
                font-size: 1.8rem;
            }}

            .stats-bar {{
                flex-direction: column;
            }}

            .grid {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1><i class="fas fa-newspaper"></i> {project_name}</h1>
        <p>{project_description}</p>
    </div>

    <div class="stats-bar">
        <div class="stat">
            <div class="stat-value" id="totalArticles">0</div>
            <div class="stat-label">Total Articles</div>
        </div>
        <div class="stat">
            <div class="stat-value" id="totalEntities">0</div>
            <div class="stat-label">Entities Found</div>
        </div>
        <div class="stat">
            <div class="stat-value" id="timeSpan">-</div>
            <div class="stat-label">Time Span</div>
        </div>
        <div class="stat">
            <div class="stat-value" id="tagCount">0</div>
            <div class="stat-label">Tag Categories</div>
        </div>
    </div>

    <div class="container">
        <!-- Timeline Section -->
        <div class="section">
            <h2 class="section-title"><i class="fas fa-clock"></i> Timeline</h2>
            <div id="timelineChart"></div>
        </div>

        <!-- Network Visualization -->
        <div class="section">
            <h2 class="section-title"><i class="fas fa-project-diagram"></i> Entity Network</h2>
            <div id="networkGraph"></div>
            <div style="margin-top: 1rem; text-align: center; color: #7f8c8d;">
                <p>Drag nodes to rearrange • Hover for details • Zoom with scroll</p>
            </div>
        </div>

        <!-- Text Analysis -->
        <div class="section">
            <h2 class="section-title"><i class="fas fa-chart-bar"></i> Text Analysis</h2>
            <div id="textAnalysisContent"></div>
        </div>

        <!-- Article Browser -->
        <div class="section">
            <h2 class="section-title"><i class="fas fa-search"></i> Article Browser</h2>
            <input type="text" class="search-box" id="articleSearch" placeholder="Search articles...">
            <div id="tagFilters" style="margin-bottom: 1rem;"></div>
            <div id="articleTable"></div>
        </div>
    </div>

    <!-- JavaScript Libraries -->
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>

    <script>
        // Embedded data
        const timelineData = {timeline_data};
        const textAnalysisData = {text_analysis_data};
        const taggedArticlesData = {tagged_articles_data};
        const entityNetworkData = {entity_network_data};

        // Initialize dashboard
        document.addEventListener('DOMContentLoaded', function() {{
            initializeStats();
            initializeTimeline();
            initializeNetwork();
            initializeTextAnalysis();
            initializeArticleBrowser();
        }});

        function initializeStats() {{
            const articles = taggedArticlesData.articles || [];
            const metadata = taggedArticlesData.metadata || {{}};

            document.getElementById('totalArticles').textContent = articles.length;

            // Count unique entities
            const entityCount = (entityNetworkData.nodes || []).length;
            document.getElementById('totalEntities').textContent = entityCount;

            // Get date range
            const dates = articles.map(a => a.date).filter(d => d).sort();
            if (dates.length > 0) {{
                const firstDate = new Date(dates[0]).getFullYear();
                const lastDate = new Date(dates[dates.length - 1]).getFullYear();
                document.getElementById('timeSpan').textContent =
                    firstDate === lastDate ? firstDate : `${{firstDate}}-${{lastDate}}`;
            }}

            // Count tags
            const tags = new Set();
            articles.forEach(a => {{
                (a.tags || []).forEach(t => tags.add(t.tag));
            }});
            document.getElementById('tagCount').textContent = tags.size;
        }}

        function initializeTimeline() {{
            const container = document.getElementById('timelineChart');

            const localPubs = timelineData.local_publications || [];
            const refEvents = timelineData.reference_events || [];

            if (localPubs.length === 0) {{
                container.innerHTML = '<p style="text-align: center; color: #7f8c8d;">No timeline data available</p>';
                return;
            }}

            // Create simple timeline visualization
            const html = `
                <div style="overflow-x: auto;">
                    <table>
                        <thead>
                            <tr>
                                <th>Date</th>
                                <th>Headline</th>
                                <th>Tags</th>
                                ${{refEvents.length > 0 ? '<th>Related Event</th>' : ''}}
                            </tr>
                        </thead>
                        <tbody>
                            ${{localPubs.map(pub => `
                                <tr>
                                    <td>${{pub.date_display || pub.date}}</td>
                                    <td>${{pub.headline}}</td>
                                    <td>${{(pub.tags || []).join(', ')}}</td>
                                    ${{refEvents.length > 0 ? `<td>${{pub.correlated_event || '-'}}</td>` : ''}}
                                </tr>
                            `).join('')}}
                        </tbody>
                    </table>
                </div>
            `;

            container.innerHTML = html;
        }}

        function initializeNetwork() {{
            const nodes = entityNetworkData.nodes || [];
            const links = entityNetworkData.links || [];

            if (nodes.length === 0) {{
                document.getElementById('networkGraph').innerHTML =
                    '<p style="text-align: center; padding: 2rem; color: #7f8c8d;">Entity network will be displayed here after running entity extraction</p>';
                return;
            }}

            const width = document.getElementById('networkGraph').offsetWidth;
            const height = 600;

            const svg = d3.select('#networkGraph')
                .append('svg')
                .attr('width', width)
                .attr('height', height);

            const simulation = d3.forceSimulation(nodes)
                .force('link', d3.forceLink(links).id(d => d.id).distance(100))
                .force('charge', d3.forceManyBody().strength(-300))
                .force('center', d3.forceCenter(width / 2, height / 2));

            const link = svg.append('g')
                .selectAll('line')
                .data(links)
                .enter().append('line')
                .attr('stroke', '#999')
                .attr('stroke-opacity', 0.6)
                .attr('stroke-width', d => Math.sqrt(d.value));

            const node = svg.append('g')
                .selectAll('circle')
                .data(nodes)
                .enter().append('circle')
                .attr('r', d => d.size || 5)
                .attr('fill', d => d.color || '#999')
                .call(d3.drag()
                    .on('start', dragstarted)
                    .on('drag', dragged)
                    .on('end', dragended));

            node.append('title')
                .text(d => `${{d.name}}\\nType: ${{d.type}}\\nMentions: ${{d.mentions || d.degree}}`);

            simulation.on('tick', () => {{
                link
                    .attr('x1', d => d.source.x)
                    .attr('y1', d => d.source.y)
                    .attr('x2', d => d.target.x)
                    .attr('y2', d => d.target.y);

                node
                    .attr('cx', d => d.x)
                    .attr('cy', d => d.y);
            }});

            function dragstarted(event, d) {{
                if (!event.active) simulation.alphaTarget(0.3).restart();
                d.fx = d.x;
                d.fy = d.y;
            }}

            function dragged(event, d) {{
                d.fx = event.x;
                d.fy = event.y;
            }}

            function dragended(event, d) {{
                if (!event.active) simulation.alphaTarget(0);
                d.fx = null;
                d.fy = null;
            }}
        }}

        function initializeTextAnalysis() {{
            const container = document.getElementById('textAnalysisContent');
            const groups = textAnalysisData.comparison_groups || [];

            if (groups.length === 0) {{
                container.innerHTML = '<p style="color: #7f8c8d;">No text analysis data available</p>';
                return;
            }}

            let html = '<div class="grid">';

            groups.forEach(group => {{
                html += `
                    <div class="card">
                        <h3>${{group.label}}</h3>
                        <p style="color: #7f8c8d; margin-bottom: 1rem;">${{group.description || ''}}</p>
                        <table>
                            <tr>
                                <td>Articles:</td>
                                <td><strong>${{group.stats.article_count}}</strong></td>
                            </tr>
                            <tr>
                                <td>Avg Sentence Length:</td>
                                <td><strong>${{group.stats.avg_sentence_length}}</strong></td>
                            </tr>
                            <tr>
                                <td>Exclamations/Article:</td>
                                <td><strong>${{group.stats.exclamations_per_article}}</strong></td>
                            </tr>
                            <tr>
                                <td>Sensational Words/Article:</td>
                                <td><strong>${{group.stats.sensational_words_per_article}}</strong></td>
                            </tr>
                        </table>
                    </div>
                `;
            }});

            html += '</div>';
            container.innerHTML = html;
        }}

        function initializeArticleBrowser() {{
            const articles = taggedArticlesData.articles || [];

            // Create tag filters
            const tags = new Set();
            articles.forEach(a => {{
                (a.tags || []).forEach(t => tags.add(t.tag));
            }});

            const tagFiltersHtml = Array.from(tags).map(tag =>
                `<span class="tag-filter" data-tag="${{tag}}">${{tag}}</span>`
            ).join('');

            document.getElementById('tagFilters').innerHTML = tagFiltersHtml;

            // Add event listeners to tag filters
            document.querySelectorAll('.tag-filter').forEach(filter => {{
                filter.addEventListener('click', function() {{
                    this.classList.toggle('active');
                    filterArticles();
                }});
            }});

            // Add search listener
            document.getElementById('articleSearch').addEventListener('input', filterArticles);

            // Initial render
            renderArticles(articles);
        }}

        function filterArticles() {{
            const searchTerm = document.getElementById('articleSearch').value.toLowerCase();
            const activeTags = Array.from(document.querySelectorAll('.tag-filter.active'))
                .map(el => el.dataset.tag);

            const articles = taggedArticlesData.articles || [];

            const filtered = articles.filter(article => {{
                // Search filter
                const matchesSearch = !searchTerm ||
                    article.headline.toLowerCase().includes(searchTerm) ||
                    (article.full_text || '').toLowerCase().includes(searchTerm);

                // Tag filter
                const articleTags = (article.tags || []).map(t => t.tag);
                const matchesTags = activeTags.length === 0 ||
                    activeTags.some(tag => articleTags.includes(tag));

                return matchesSearch && matchesTags;
            }});

            renderArticles(filtered);
        }}

        function renderArticles(articles) {{
            const container = document.getElementById('articleTable');

            if (articles.length === 0) {{
                container.innerHTML = '<p style="text-align: center; color: #7f8c8d;">No articles found</p>';
                return;
            }}

            const html = `
                <div style="overflow-x: auto;">
                    <table>
                        <thead>
                            <tr>
                                <th>Date</th>
                                <th>Headline</th>
                                <th>Tags</th>
                                <th>Words</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${{articles.slice(0, 50).map(article => `
                                <tr>
                                    <td>${{article.date || '-'}}</td>
                                    <td>${{article.headline || 'Untitled'}}</td>
                                    <td>${{{(article.tags || []).map(t => t.tag).join(', ')}}</td>
                                    <td>${{article.word_count || '-'}}</td>
                                </tr>
                            `).join('')}}
                        </tbody>
                    </table>
                    ${{articles.length > 50 ? `<p style="text-align: center; margin-top: 1rem; color: #7f8c8d;">Showing 50 of ${{articles.length}} articles</p>` : ''}}
                </div>
            `;

            container.innerHTML = html;
        }}
    </script>
</body>
</html>
"""

    # Write HTML file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"Dashboard generated: {output_path}")


def main():
    # Parse arguments
    parser = argparse.ArgumentParser(
        description="Generate interactive HTML dashboard"
    )
    parser.add_argument(
        '--config',
        type=str,
        default=None,
        help='Path to configuration file'
    )
    parser.add_argument(
        '--output',
        type=str,
        default=None,
        help='Output HTML file path (default: dashboard/index.html)'
    )
    args = parser.parse_args()

    # Load configuration
    config = load_config(args.config)

    print("=" * 60)
    print("Dashboard Generator")
    print("=" * 60)

    # Setup paths
    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent
    data_dir = project_root / "data" / "processed"

    if args.output:
        output_path = Path(args.output)
    else:
        output_path = project_root / "dashboard" / "index.html"

    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Load data
    print("\nLoading data files...")
    data = load_data_files(data_dir)

    # Generate dashboard
    print("\nGenerating dashboard...")
    generate_dashboard_html(data, config, output_path)

    print("\n" + "=" * 60)
    print("Complete!")
    print("=" * 60)
    print(f"\nDashboard: {output_path}")
    print(f"\nOpen in browser:")
    print(f"  file://{output_path.absolute()}")


if __name__ == "__main__":
    main()
