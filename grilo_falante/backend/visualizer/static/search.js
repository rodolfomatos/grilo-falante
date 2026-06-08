/**
 * Grilo Falante Visualizer - Search with HTMX
 */

document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('search-input');
    const searchForm = document.getElementById('search-form');
    const searchResults = document.getElementById('search-results');
    
    if (!searchInput || !searchForm) return;
    
    let debounceTimer;
    
    // Debounced search on input
    searchInput.addEventListener('input', function() {
        clearTimeout(debounceTimer);
        const query = this.value.trim();
        
        if (query.length < 2) {
            searchResults.innerHTML = '';
            return;
        }
        
        debounceTimer = setTimeout(() => {
            performSearch(query);
        }, 300);
    });
    
    // Search on form submit
    searchForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const query = searchInput.value.trim();
        if (query.length >= 2) {
            window.location.href = '/visualizer/search?q=' + encodeURIComponent(query);
        }
    });
    
    async function performSearch(query) {
        try {
            const response = await fetch('/visualizer/api/search?q=' + encodeURIComponent(query));
            const results = await response.json();
            
            if (results.length === 0) {
                searchResults.innerHTML = '<div class="no-results">No results found</div>';
                return;
            }
            
            let html = '';
            for (const result of results.slice(0, 10)) {
                html += `
                    <div class="search-result">
                        <div class="search-result-title">
                            <a href="${result.url}">${result.title}</a>
                        </div>
                        <div class="search-result-snippet">${result.snippet}</div>
                        <div class="search-result-type">${result.result_type}</div>
                    </div>
                `;
            }
            
            searchResults.innerHTML = html;
        } catch (error) {
            console.error('Search error:', error);
        }
    }
});

/**
 * Graph visualization with D3.js
 */
document.addEventListener('DOMContentLoaded', function() {
    const graphContainer = document.getElementById('graph-data');
    if (!graphContainer) return;
    
    const nodesData = JSON.parse(graphContainer.dataset.nodes || '[]');
    const linksData = JSON.parse(graphContainer.dataset.links || '[]');
    
    if (nodesData.length === 0) return;
    
    // Create SVG
    const width = graphContainer.clientWidth;
    const height = graphContainer.clientHeight;
    
    const svg = d3.select('#graph-svg')
        .attr('viewBox', [0, 0, width, height]);
    
    // Color scale by GMIF level
    const colorScale = {
        'M1': '#2e7d32',
        'M2': '#558b2f', 
        'M3': '#f9a825',
        'M4': '#e53935'
    };
    
    // Simulation
    const simulation = d3.forceSimulation(nodesData)
        .force('link', d3.forceLink(linksData).id(d => d.id).distance(100))
        .force('charge', d3.forceManyBody().strength(-300))
        .force('center', d3.forceCenter(width / 2, height / 2));
    
    // Draw links
    const link = svg.append('g')
        .selectAll('line')
        .data(linksData)
        .join('line')
        .attr('class', 'link')
        .attr('stroke', '#999')
        .attr('stroke-opacity', 0.6);
    
    // Draw nodes
    const node = svg.append('g')
        .selectAll('g')
        .data(nodesData)
        .join('g')
        .attr('class', 'node')
        .call(d3.drag()
            .on('start', dragstarted)
            .on('drag', dragged)
            .on('end', dragended));
    
    node.append('circle')
        .attr('r', 8)
        .attr('fill', d => colorScale[d.gmif] || '#36c');
    
    node.append('text')
        .attr('dx', 12)
        .attr('dy', '.35em')
        .text(d => d.label.substring(0, 20));
    
    simulation.on('tick', () => {
        link
            .attr('x1', d => d.source.x)
            .attr('y1', d => d.source.y)
            .attr('x2', d => d.target.x)
            .attr('y2', d => d.target.y);
        
        node.attr('transform', d => `translate(${d.x},${d.y})`);
    });
    
    function dragstarted(event) {
        if (!event.active) simulation.alphaTarget(0.3).restart();
        event.subject.fx = event.subject.x;
        event.subject.fy = event.subject.y;
    }
    
    function dragged(event) {
        event.subject.fx = event.x;
        event.subject.fy = event.y;
    }
    
    function dragended(event) {
        if (!event.active) simulation.alphaTarget(0);
        event.subject.fx = null;
        event.subject.fy = null;
    }
});