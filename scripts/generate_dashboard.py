#!/usr/bin/env python3
"""
Dashboard Generator
Creates a single-page HTML dashboard with interactive visualizations.
Dark steampunk aesthetic with full functionality.
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


def load_metadata(project_root: Path) -> dict:
    """Load preprocessing metadata to get image paths."""
    metadata_file = project_root / "data" / "preprocessed" / "all_metadata.json"
    if metadata_file.exists():
        with open(metadata_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def generate_dashboard_html(data: dict, config_loader, output_path: Path, project_root: Path):
    """Generate comprehensive HTML dashboard with steampunk theme."""

    project_metadata = config_loader.get_project_metadata()
    dashboard_config = config_loader.get_dashboard_config()

    # Get project info
    project_name = project_metadata.get('name', 'Newspaper Analysis')
    project_description = project_metadata.get('description', '')

    # Load preprocessing metadata for image paths
    preprocessing_metadata = load_metadata(project_root)

    # Prepare data for embedding
    timeline_data = json.dumps(data.get('timeline', {}))
    text_analysis_data = json.dumps(data.get('text_analysis', {}))
    tagged_articles_data = json.dumps(data.get('tagged_articles', {}))
    entity_network_data = json.dumps(data.get('entity_cooccurrence_d3', {}))
    preprocessing_metadata_json = json.dumps(preprocessing_metadata)

    # Generate HTML
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{project_name} - Research Dashboard</title>

    <!-- CSS Libraries -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link href="https://fonts.googleapis.com/css2?family=Crimson+Text:ital,wght@0,400;0,600;0,700;1,400&family=Special+Elite&display=swap" rel="stylesheet">

    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        :root {{
            --bg-primary: #1a1410;
            --bg-secondary: #2d2419;
            --bg-tertiary: #3d3229;
            --accent-brass: #b8860b;
            --accent-copper: #cd7f32;
            --accent-bronze: #8b6f47;
            --text-primary: #e8dcc4;
            --text-secondary: #c9b896;
            --text-muted: #8b7e66;
            --border-color: #5a4a3a;
            --shadow: rgba(0, 0, 0, 0.6);
        }}

        body {{
            font-family: 'Crimson Text', serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            line-height: 1.6;
            background-image:
                radial-gradient(circle at 20% 50%, rgba(184, 134, 11, 0.03) 0%, transparent 50%),
                radial-gradient(circle at 80% 80%, rgba(205, 127, 50, 0.03) 0%, transparent 50%);
        }}

        .header {{
            background: linear-gradient(135deg, var(--bg-secondary) 0%, var(--bg-tertiary) 100%);
            border-bottom: 3px solid var(--accent-brass);
            padding: 2rem;
            text-align: center;
            box-shadow: 0 4px 20px var(--shadow);
            position: relative;
        }}

        .header::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: linear-gradient(90deg,
                var(--accent-brass) 0%,
                var(--accent-copper) 50%,
                var(--accent-brass) 100%);
        }}

        .header h1 {{
            font-family: 'Special Elite', cursive;
            font-size: 2.8rem;
            margin-bottom: 0.5rem;
            text-shadow: 2px 2px 4px var(--shadow);
            color: var(--accent-brass);
            letter-spacing: 2px;
        }}

        .header p {{
            font-size: 1.2rem;
            color: var(--text-secondary);
            font-style: italic;
        }}

        .stats-bar {{
            background: var(--bg-secondary);
            border-bottom: 2px solid var(--border-color);
            padding: 1.5rem 2rem;
            display: flex;
            justify-content: space-around;
            flex-wrap: wrap;
            gap: 2rem;
        }}

        .stat {{
            text-align: center;
            padding: 1rem;
            background: var(--bg-tertiary);
            border-radius: 10px;
            border: 2px solid var(--accent-bronze);
            min-width: 150px;
            box-shadow: 0 2px 10px var(--shadow);
        }}

        .stat-value {{
            font-size: 2.5rem;
            font-weight: bold;
            color: var(--accent-brass);
            text-shadow: 1px 1px 2px var(--shadow);
            font-family: 'Special Elite', cursive;
        }}

        .stat-label {{
            font-size: 0.9rem;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 2px;
            margin-top: 0.5rem;
        }}

        .container {{
            max-width: 1600px;
            margin: 0 auto;
            padding: 2rem;
        }}

        .section {{
            background: var(--bg-secondary);
            margin-bottom: 2rem;
            border-radius: 10px;
            padding: 2rem;
            box-shadow: 0 4px 20px var(--shadow);
            border: 2px solid var(--border-color);
        }}

        .section-title {{
            font-family: 'Special Elite', cursive;
            font-size: 2rem;
            margin-bottom: 1.5rem;
            color: var(--accent-brass);
            border-bottom: 2px solid var(--accent-copper);
            padding-bottom: 0.5rem;
            text-shadow: 1px 1px 2px var(--shadow);
        }}

        .section-title i {{
            margin-right: 1rem;
            color: var(--accent-copper);
        }}

        .controls {{
            display: flex;
            gap: 1rem;
            margin-bottom: 1.5rem;
            flex-wrap: wrap;
        }}

        .btn {{
            padding: 0.75rem 1.5rem;
            background: var(--bg-tertiary);
            border: 2px solid var(--accent-brass);
            color: var(--text-primary);
            cursor: pointer;
            border-radius: 5px;
            font-family: 'Crimson Text', serif;
            font-size: 1rem;
            transition: all 0.3s;
        }}

        .btn:hover {{
            background: var(--accent-brass);
            color: var(--bg-primary);
            transform: translateY(-2px);
            box-shadow: 0 4px 10px var(--shadow);
        }}

        .btn.active {{
            background: var(--accent-copper);
            color: var(--bg-primary);
        }}

        .search-box {{
            flex: 1;
            min-width: 300px;
            padding: 0.75rem;
            background: var(--bg-tertiary);
            border: 2px solid var(--border-color);
            border-radius: 5px;
            color: var(--text-primary);
            font-family: 'Crimson Text', serif;
            font-size: 1rem;
        }}

        .search-box:focus {{
            outline: none;
            border-color: var(--accent-brass);
        }}

        #networkGraph {{
            width: 100%;
            height: 700px;
            background: var(--bg-tertiary);
            border: 2px solid var(--border-color);
            border-radius: 10px;
            position: relative;
        }}

        #timelineChart {{
            width: 100%;
            min-height: 400px;
            background: var(--bg-tertiary);
            border: 2px solid var(--border-color);
            border-radius: 10px;
            padding: 1rem;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            background: var(--bg-tertiary);
            border-radius: 10px;
            overflow: hidden;
        }}

        th, td {{
            padding: 1rem;
            text-align: left;
            border-bottom: 1px solid var(--border-color);
        }}

        th {{
            background: var(--bg-primary);
            font-weight: 600;
            color: var(--accent-brass);
            text-transform: uppercase;
            letter-spacing: 1px;
            font-size: 0.9rem;
        }}

        tr:hover {{
            background: rgba(184, 134, 11, 0.1);
            cursor: pointer;
        }}

        .tag-badge {{
            display: inline-block;
            padding: 0.25rem 0.75rem;
            margin: 0.25rem;
            background: var(--bg-primary);
            border: 1px solid var(--accent-bronze);
            border-radius: 15px;
            font-size: 0.85rem;
            color: var(--text-secondary);
        }}

        .card {{
            background: var(--bg-tertiary);
            padding: 1.5rem;
            border-radius: 10px;
            border: 2px solid var(--accent-bronze);
            margin-bottom: 1rem;
        }}

        .card h3 {{
            color: var(--accent-copper);
            margin-bottom: 1rem;
            font-family: 'Special Elite', cursive;
        }}

        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 1.5rem;
        }}

        /* Modal Styles */
        .modal {{
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.9);
            overflow: auto;
        }}

        .modal-content {{
            background: var(--bg-secondary);
            margin: 2% auto;
            padding: 2rem;
            border: 3px solid var(--accent-brass);
            border-radius: 10px;
            width: 90%;
            max-width: 1200px;
            max-height: 90vh;
            overflow: auto;
            box-shadow: 0 8px 40px var(--shadow);
        }}

        .modal-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1.5rem;
            padding-bottom: 1rem;
            border-bottom: 2px solid var(--accent-copper);
        }}

        .modal-header h2 {{
            color: var(--accent-brass);
            font-family: 'Special Elite', cursive;
        }}

        .close {{
            color: var(--accent-brass);
            font-size: 2rem;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s;
        }}

        .close:hover {{
            color: var(--accent-copper);
            transform: scale(1.2);
        }}

        .article-content {{
            margin-top: 1rem;
            line-height: 1.8;
        }}

        .article-image {{
            max-width: 100%;
            border: 2px solid var(--border-color);
            border-radius: 5px;
            margin: 1rem 0;
        }}

        #notepad {{
            width: 100%;
            min-height: 300px;
            background: var(--bg-tertiary);
            border: 2px solid var(--border-color);
            border-radius: 5px;
            padding: 1rem;
            color: var(--text-primary);
            font-family: 'Crimson Text', serif;
            font-size: 1rem;
            resize: vertical;
        }}

        #notepad:focus {{
            outline: none;
            border-color: var(--accent-brass);
        }}

        .notepad-controls {{
            margin-top: 1rem;
            display: flex;
            gap: 1rem;
        }}

        .tooltip {{
            position: absolute;
            background: var(--bg-primary);
            border: 2px solid var(--accent-brass);
            padding: 0.75rem;
            border-radius: 5px;
            pointer-events: none;
            opacity: 0;
            transition: opacity 0.3s;
            z-index: 100;
            max-width: 300px;
            box-shadow: 0 4px 10px var(--shadow);
        }}

        .legend {{
            display: flex;
            gap: 1.5rem;
            flex-wrap: wrap;
            margin-top: 1rem;
            padding: 1rem;
            background: var(--bg-primary);
            border-radius: 5px;
        }}

        .legend-item {{
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}

        .legend-color {{
            width: 20px;
            height: 20px;
            border-radius: 50%;
            border: 2px solid var(--accent-bronze);
        }}

        .loading {{
            text-align: center;
            padding: 2rem;
            color: var(--text-muted);
            font-style: italic;
        }}

        @media (max-width: 768px) {{
            .header h1 {{
                font-size: 1.8rem;
            }}

            .stats-bar {{
                flex-direction: column;
                gap: 1rem;
            }}

            .grid {{
                grid-template-columns: 1fr;
            }}

            .modal-content {{
                width: 95%;
                padding: 1rem;
            }}
        }}

        /* Scrollbar styling */
        ::-webkit-scrollbar {{
            width: 12px;
        }}

        ::-webkit-scrollbar-track {{
            background: var(--bg-primary);
        }}

        ::-webkit-scrollbar-thumb {{
            background: var(--accent-bronze);
            border-radius: 6px;
        }}

        ::-webkit-scrollbar-thumb:hover {{
            background: var(--accent-brass);
        }}
    </style>
</head>
<body>
    <!-- Article Detail Modal -->
    <div id="articleModal" class="modal">
        <div class="modal-content">
            <div class="modal-header">
                <h2 id="modalTitle">Article Details</h2>
                <span class="close" onclick="closeModal('articleModal')">&times;</span>
            </div>
            <div id="modalBody"></div>
        </div>
    </div>

    <!-- Notepad Modal -->
    <div id="notepadModal" class="modal">
        <div class="modal-content">
            <div class="modal-header">
                <h2><i class="fas fa-sticky-note"></i> Research Notes</h2>
                <span class="close" onclick="closeModal('notepadModal')">&times;</span>
            </div>
            <textarea id="notepad" placeholder="Take notes about your research here... Notes are saved automatically in your browser."></textarea>
            <div class="notepad-controls">
                <button class="btn" onclick="downloadNotes()">
                    <i class="fas fa-download"></i> Download Notes
                </button>
                <button class="btn" onclick="clearNotes()">
                    <i class="fas fa-trash"></i> Clear Notes
                </button>
            </div>
        </div>
    </div>

    <div class="header">
        <h1><i class="fas fa-newspaper"></i> {project_name}</h1>
        <p>{project_description}</p>
    </div>

    <div class="stats-bar">
        <div class="stat">
            <div class="stat-value" id="totalArticles">0</div>
            <div class="stat-label">Articles</div>
        </div>
        <div class="stat">
            <div class="stat-value" id="totalEntities">0</div>
            <div class="stat-label">Entities</div>
        </div>
        <div class="stat">
            <div class="stat-value" id="timeSpan">-</div>
            <div class="stat-label">Time Span</div>
        </div>
        <div class="stat">
            <div class="stat-value" id="tagCount">0</div>
            <div class="stat-label">Categories</div>
        </div>
    </div>

    <div class="container">
        <!-- Controls -->
        <div class="section">
            <div class="controls">
                <button class="btn" onclick="openModal('notepadModal')">
                    <i class="fas fa-sticky-note"></i> Research Notes
                </button>
                <button class="btn" onclick="exportData()">
                    <i class="fas fa-download"></i> Export Data
                </button>
            </div>
        </div>

        <!-- Timeline Section -->
        <div class="section">
            <h2 class="section-title"><i class="fas fa-clock"></i> Timeline</h2>
            <div id="timelineChart"></div>
        </div>

        <!-- Entity Network -->
        <div class="section">
            <h2 class="section-title"><i class="fas fa-project-diagram"></i> Entity Network</h2>
            <div class="controls">
                <button class="btn" id="resetZoom" onclick="resetNetworkZoom()">
                    <i class="fas fa-expand"></i> Reset View
                </button>
                <button class="btn" id="togglePhysics" onclick="togglePhysics()">
                    <i class="fas fa-pause"></i> Pause Physics
                </button>
            </div>
            <div id="networkGraph"></div>
            <div class="legend" id="networkLegend"></div>
        </div>

        <!-- Text Analysis -->
        <div class="section">
            <h2 class="section-title"><i class="fas fa-chart-bar"></i> Comparative Text Analysis</h2>
            <div id="textAnalysisContent"></div>
        </div>

        <!-- Article Browser -->
        <div class="section">
            <h2 class="section-title"><i class="fas fa-search"></i> Article Explorer</h2>
            <div class="controls">
                <input type="text" class="search-box" id="articleSearch"
                       placeholder="Search articles by headline or content...">
            </div>
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
        const preprocessingMetadata = {preprocessing_metadata_json};

        let networkSimulation = null;
        let physicsEnabled = true;

        // Initialize dashboard
        document.addEventListener('DOMContentLoaded', function() {{
            initializeStats();
            initializeTimeline();
            initializeNetwork();
            initializeTextAnalysis();
            initializeArticleBrowser();
            loadNotes();
        }});

        function initializeStats() {{
            const articles = taggedArticlesData.articles || [];

            document.getElementById('totalArticles').textContent = articles.length;

            const entityCount = (entityNetworkData.nodes || []).length;
            document.getElementById('totalEntities').textContent = entityCount || 'N/A';

            const dates = articles.map(a => a.date).filter(d => d).sort();
            if (dates.length > 0) {{
                const firstDate = new Date(dates[0]).getFullYear();
                const lastDate = new Date(dates[dates.length - 1]).getFullYear();
                document.getElementById('timeSpan').textContent =
                    firstDate === lastDate ? firstDate : `${{firstDate}}-${{lastDate}}`;
            }}

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
                container.innerHTML = '<p class="loading">No timeline data available</p>';
                return;
            }}

            // Create timeline with Chart.js
            const canvas = document.createElement('canvas');
            canvas.id = 'timelineCanvas';
            container.appendChild(canvas);

            const ctx = canvas.getContext('2d');

            // Prepare data
            const dates = localPubs.map(p => p.date);
            const articleCounts = {{}};
            dates.forEach(date => {{
                articleCounts[date] = (articleCounts[date] || 0) + 1;
            }});

            const chartData = Object.keys(articleCounts).sort().map(date => ({{
                x: date,
                y: articleCounts[date]
            }}));

            new Chart(ctx, {{
                type: 'line',
                data: {{
                    datasets: [{{
                        label: 'Articles Published',
                        data: chartData,
                        borderColor: '#b8860b',
                        backgroundColor: 'rgba(184, 134, 11, 0.2)',
                        tension: 0.4,
                        fill: true
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {{
                        x: {{
                            type: 'time',
                            time: {{
                                unit: 'month'
                            }},
                            ticks: {{
                                color: '#c9b896'
                            }},
                            grid: {{
                                color: '#5a4a3a'
                            }}
                        }},
                        y: {{
                            beginAtZero: true,
                            ticks: {{
                                color: '#c9b896',
                                stepSize: 1
                            }},
                            grid: {{
                                color: '#5a4a3a'
                            }}
                        }}
                    }},
                    plugins: {{
                        legend: {{
                            labels: {{
                                color: '#e8dcc4'
                            }}
                        }},
                        tooltip: {{
                            callbacks: {{
                                label: function(context) {{
                                    return `Articles: ${{context.parsed.y}}`;
                                }}
                            }}
                        }}
                    }}
                }}
            }});
        }}

        function initializeNetwork() {{
            const nodes = entityNetworkData.nodes || [];
            const links = entityNetworkData.links || [];

            if (nodes.length === 0) {{
                document.getElementById('networkGraph').innerHTML =
                    '<p class="loading">Entity network will be displayed here after running entity extraction</p>';
                return;
            }}

            const container = document.getElementById('networkGraph');
            const width = container.offsetWidth;
            const height = 700;

            const svg = d3.select('#networkGraph')
                .append('svg')
                .attr('width', width)
                .attr('height', height);

            // Add zoom behavior
            const g = svg.append('g');
            const zoom = d3.zoom()
                .scaleExtent([0.1, 10])
                .on('zoom', (event) => {{
                    g.attr('transform', event.transform);
                }});
            svg.call(zoom);

            // Create simulation
            networkSimulation = d3.forceSimulation(nodes)
                .force('link', d3.forceLink(links).id(d => d.id).distance(100))
                .force('charge', d3.forceManyBody().strength(-400))
                .force('center', d3.forceCenter(width / 2, height / 2))
                .force('collision', d3.forceCollide().radius(d => (d.size || 5) + 5));

            // Create links
            const link = g.append('g')
                .selectAll('line')
                .data(links)
                .enter().append('line')
                .attr('stroke', '#8b6f47')
                .attr('stroke-opacity', 0.6)
                .attr('stroke-width', d => Math.sqrt(d.value || 1));

            // Create nodes
            const node = g.append('g')
                .selectAll('circle')
                .data(nodes)
                .enter().append('circle')
                .attr('r', d => d.size || 5)
                .attr('fill', d => d.color || '#b8860b')
                .attr('stroke', '#e8dcc4')
                .attr('stroke-width', 1.5)
                .style('cursor', 'pointer')
                .call(d3.drag()
                    .on('start', dragstarted)
                    .on('drag', dragged)
                    .on('end', dragended));

            // Add labels for important nodes
            const label = g.append('g')
                .selectAll('text')
                .data(nodes.filter(d => (d.degree || 0) > 3))
                .enter().append('text')
                .text(d => d.name)
                .attr('font-size', 10)
                .attr('fill', '#e8dcc4')
                .attr('text-anchor', 'middle')
                .attr('dy', d => (d.size || 5) + 15)
                .style('pointer-events', 'none');

            // Tooltip
            const tooltip = d3.select('body').append('div')
                .attr('class', 'tooltip')
                .style('position', 'absolute');

            node.on('mouseover', function(event, d) {{
                tooltip.style('opacity', 1)
                    .html(`
                        <strong>${{d.name}}</strong><br>
                        Type: ${{d.type}}<br>
                        Mentions: ${{d.mentions || d.degree}}<br>
                        Connections: ${{d.degree}}
                    `)
                    .style('left', (event.pageX + 10) + 'px')
                    .style('top', (event.pageY - 28) + 'px');
            }})
            .on('mouseout', function() {{
                tooltip.style('opacity', 0);
            }});

            // Update positions
            networkSimulation.on('tick', () => {{
                link
                    .attr('x1', d => d.source.x)
                    .attr('y1', d => d.source.y)
                    .attr('x2', d => d.target.x)
                    .attr('y2', d => d.target.y);

                node
                    .attr('cx', d => d.x)
                    .attr('cy', d => d.y);

                label
                    .attr('x', d => d.x)
                    .attr('y', d => d.y);
            }});

            function dragstarted(event, d) {{
                if (!event.active && physicsEnabled) networkSimulation.alphaTarget(0.3).restart();
                d.fx = d.x;
                d.fy = d.y;
            }}

            function dragged(event, d) {{
                d.fx = event.x;
                d.fy = event.y;
            }}

            function dragended(event, d) {{
                if (!event.active && physicsEnabled) networkSimulation.alphaTarget(0);
                d.fx = null;
                d.fy = null;
            }}

            // Create legend
            const types = [...new Set(nodes.map(n => n.type))];
            const legend = document.getElementById('networkLegend');
            types.forEach(type => {{
                const sample = nodes.find(n => n.type === type);
                const item = document.createElement('div');
                item.className = 'legend-item';
                item.innerHTML = `
                    <div class="legend-color" style="background: ${{sample.color}}"></div>
                    <span>${{type}}</span>
                `;
                legend.appendChild(item);
            }});
        }}

        function resetNetworkZoom() {{
            d3.select('#networkGraph svg')
                .transition()
                .duration(750)
                .call(d3.zoom().transform, d3.zoomIdentity);
        }}

        function togglePhysics() {{
            physicsEnabled = !physicsEnabled;
            const btn = document.getElementById('togglePhysics');
            if (physicsEnabled) {{
                networkSimulation.alphaTarget(0.3).restart();
                btn.innerHTML = '<i class="fas fa-pause"></i> Pause Physics';
            }} else {{
                networkSimulation.stop();
                btn.innerHTML = '<i class="fas fa-play"></i> Resume Physics';
            }}
        }}

        function initializeTextAnalysis() {{
            const container = document.getElementById('textAnalysisContent');
            const groups = textAnalysisData.comparison_groups || [];

            if (groups.length === 0) {{
                container.innerHTML = '<p class="loading">No text analysis data available</p>';
                return;
            }}

            let html = '<div class="grid">';

            groups.forEach(group => {{
                html += `
                    <div class="card">
                        <h3>${{group.label}}</h3>
                        <p style="color: var(--text-muted); margin-bottom: 1rem;">${{group.description || ''}}</p>
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
                `<span class="tag-badge" style="cursor: pointer;" onclick="toggleTagFilter('${{tag}}')" data-tag="${{tag}}">${{tag}}</span>`
            ).join('');

            document.getElementById('tagFilters').innerHTML = tagFiltersHtml;

            // Add search listener
            document.getElementById('articleSearch').addEventListener('input', filterArticles);

            // Initial render
            renderArticles(articles);
        }}

        function toggleTagFilter(tag) {{
            const badge = document.querySelector(`[data-tag="${{tag}}"]`);
            badge.classList.toggle('active');
            badge.style.background = badge.classList.contains('active') ?
                'var(--accent-brass)' : 'var(--bg-primary)';
            filterArticles();
        }}

        function filterArticles() {{
            const searchTerm = document.getElementById('articleSearch').value.toLowerCase();
            const activeTags = Array.from(document.querySelectorAll('.tag-badge.active'))
                .map(el => el.dataset.tag);

            const articles = taggedArticlesData.articles || [];

            const filtered = articles.filter(article => {{
                const matchesSearch = !searchTerm ||
                    article.headline.toLowerCase().includes(searchTerm) ||
                    (article.full_text || '').toLowerCase().includes(searchTerm);

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
                container.innerHTML = '<p class="loading">No articles found</p>';
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
                            ${{articles.slice(0, 100).map(article => `
                                <tr onclick='showArticleDetail(${{JSON.stringify(article).replace(/'/g, "&apos;")}})'>
                                    <td>${{article.date || '-'}}</td>
                                    <td>${{article.headline || 'Untitled'}}</td>
                                    <td>${{(article.tags || []).map(t =>
                                        `<span class="tag-badge">${{t.tag}}</span>`
                                    ).join('')}}</td>
                                    <td>${{article.word_count || '-'}}</td>
                                </tr>
                            `).join('')}}
                        </tbody>
                    </table>
                    ${{articles.length > 100 ? `<p style="text-align: center; margin-top: 1rem; color: var(--text-muted);">Showing 100 of ${{articles.length}} articles</p>` : ''}}
                </div>
            `;

            container.innerHTML = html;
        }}

        function showArticleDetail(article) {{
            const modal = document.getElementById('articleModal');
            const modalBody = document.getElementById('modalBody');
            document.getElementById('modalTitle').textContent = article.headline || 'Article';

            // Find image path from metadata
            let imagePath = '';
            if (preprocessingMetadata && preprocessingMetadata.snippets) {{
                const snippet = preprocessingMetadata.snippets.find(s =>
                    s.article_id === article.article_id ||
                    (s.page === article.page_number && s.column === article.column)
                );
                if (snippet) {{
                    imagePath = `../data/preprocessed/${{snippet.pdf_stem}}/${{snippet.filename}}`;
                }}
            }}

            let html = `
                <div class="article-content">
                    <p><strong>Date:</strong> ${{article.date || 'Unknown'}}</p>
                    <p><strong>Page:</strong> ${{article.page_number || '-'}}, <strong>Column:</strong> ${{article.column || '-'}}</p>
                    <p><strong>Tags:</strong> ${{(article.tags || []).map(t =>
                        `<span class="tag-badge">${{t.tag}} (${{t.score}})</span>`
                    ).join('')}}</p>
            `;

            if (imagePath) {{
                html += `
                    <div style="margin: 1.5rem 0;">
                        <h3 style="color: var(--accent-copper); margin-bottom: 1rem;">Original Image</h3>
                        <img src="${{imagePath}}" class="article-image" alt="Article scan"
                             onerror="this.style.display='none'; this.nextElementSibling.style.display='block';">
                        <p style="display: none; color: var(--text-muted);">Image not available</p>
                    </div>
                `;
            }}

            html += `
                    <h3 style="color: var(--accent-copper); margin: 1.5rem 0 1rem 0;">Full Text</h3>
                    <div style="line-height: 1.8; text-align: justify;">
                        ${{article.full_text || 'No text available'}}
                    </div>
                </div>
            `;

            modalBody.innerHTML = html;
            modal.style.display = 'block';
        }}

        function openModal(modalId) {{
            document.getElementById(modalId).style.display = 'block';
        }}

        function closeModal(modalId) {{
            document.getElementById(modalId).style.display = 'none';
        }}

        // Close modal when clicking outside
        window.onclick = function(event) {{
            if (event.target.classList.contains('modal')) {{
                event.target.style.display = 'none';
            }}
        }}

        // Notepad functions
        function loadNotes() {{
            const notes = localStorage.getItem('researchNotes');
            if (notes) {{
                document.getElementById('notepad').value = notes;
            }}
        }}

        document.getElementById('notepad').addEventListener('input', function() {{
            localStorage.setItem('researchNotes', this.value);
        }});

        function downloadNotes() {{
            const notes = document.getElementById('notepad').value;
            const blob = new Blob([notes], {{ type: 'text/plain' }});
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'research-notes-' + new Date().toISOString().slice(0,10) + '.txt';
            a.click();
            URL.revokeObjectURL(url);
        }}

        function clearNotes() {{
            if (confirm('Are you sure you want to clear all notes?')) {{
                document.getElementById('notepad').value = '';
                localStorage.removeItem('researchNotes');
            }}
        }}

        function exportData() {{
            const exportData = {{
                project: '{project_name}',
                exported: new Date().toISOString(),
                timeline: timelineData,
                textAnalysis: textAnalysisData,
                articles: taggedArticlesData,
                entities: entityNetworkData
            }};

            const blob = new Blob([JSON.stringify(exportData, null, 2)], {{ type: 'application/json' }});
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'newspaper-analysis-export-' + new Date().toISOString().slice(0,10) + '.json';
            a.click();
            URL.revokeObjectURL(url);
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
    generate_dashboard_html(data, config, output_path, project_root)

    print("\n" + "=" * 60)
    print("Complete!")
    print("=" * 60)
    print(f"\nDashboard: {output_path}")
    print(f"\nOpen in browser:")
    print(f"  file://{output_path.absolute()}")


if __name__ == "__main__":
    main()
