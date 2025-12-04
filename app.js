// Global variables
let networkData = null;
let currentGovernorate = null;
let currentView = 'post';
let simulation = null;
let charts = {};
let currentZoom = null;

// Color schemes
const nodeColors = {
    decision_maker: '#4CAF50',
    process: '#FF9800',
    data_source: '#2196F3'
};

// Initialize the application
async function init() {
    try {
        const response = await fetch('governorate_networks.json');
        networkData = await response.json();
        
        // Populate governorate selector
        const select = document.getElementById('governorate-select');
        select.innerHTML = '<option value="">اختر المحافظة...</option>';
        
        Object.keys(networkData).sort().forEach(gov => {
            const option = document.createElement('option');
            option.value = gov;
            option.textContent = `${gov} (${networkData[gov].metrics.total_companies} شركة)`;
            select.appendChild(option);
        });
        
        // Set default governorate
        if (Object.keys(networkData).length > 0) {
            const firstGov = Object.keys(networkData).sort()[0];
            select.value = firstGov;
            loadGovernorate(firstGov);
        }
        
        // Add event listeners
        select.addEventListener('change', (e) => {
            if (e.target.value) {
                loadGovernorate(e.target.value);
            }
        });
        
        document.getElementById('view-mode').addEventListener('change', (e) => {
            currentView = e.target.value;
            if (currentGovernorate) {
                loadGovernorate(currentGovernorate);
            }
        });
        
    } catch (error) {
        console.error('Error loading data:', error);
        document.getElementById('network-container').innerHTML = 
            '<div class="loading">خطأ في تحميل البيانات. تأكد من وجود ملف governorate_networks.json</div>';
    }
}

// Load governorate data and render
function loadGovernorate(governorate) {
    currentGovernorate = governorate;
    const data = networkData[governorate];
    
    if (!data) return;
    
    // Update metrics
    updateMetrics(data.metrics);
    
    // Render network
    renderNetwork(data);
    
    // Update charts
    updateCharts(data);
}

// Update metrics display
function updateMetrics(metrics) {
    const grid = document.getElementById('metrics-grid');
    grid.innerHTML = '';
    
    const metricCards = [
        {
            title: 'إجمالي الشركات',
            value: metrics.total_companies,
            change: null
        },
        {
            title: 'المرونة في اتخاذ القرار (قبل)',
            value: metrics.avg_pre_bi_agility.toFixed(1),
            change: null
        },
        {
            title: 'المرونة في اتخاذ القرار (بعد)',
            value: metrics.avg_post_bi_agility.toFixed(1),
            change: `+${metrics.avg_agility_improvement.toFixed(1)}`
        },
        {
            title: 'الكفاءة التشغيلية (قبل)',
            value: metrics.avg_pre_bi_efficiency.toFixed(1),
            change: null
        },
        {
            title: 'الكفاءة التشغيلية (بعد)',
            value: metrics.avg_post_bi_efficiency.toFixed(1),
            change: `+${metrics.avg_efficiency_improvement.toFixed(1)}`
        },
        {
            title: 'القرارات المبنية على البيانات (قبل)',
            value: `${metrics.avg_pre_bi_data_driven.toFixed(1)}%`,
            change: null
        },
        {
            title: 'القرارات المبنية على البيانات (بعد)',
            value: `${metrics.avg_post_bi_data_driven.toFixed(1)}%`,
            change: `+${metrics.avg_data_driven_improvement.toFixed(1)}%`
        },
        {
            title: 'نمو الإيرادات',
            value: `+${metrics.avg_revenue_growth.toFixed(1)}%`,
            change: null
        },
        {
            title: 'تقليل التكاليف',
            value: `-${metrics.avg_cost_reduction.toFixed(1)}%`,
            change: null
        }
    ];
    
    metricCards.forEach(metric => {
        const card = document.createElement('div');
        card.className = 'metric-card';
        card.innerHTML = `
            <h3>${metric.title}</h3>
            <div class="value">${metric.value}</div>
            ${metric.change ? `<div class="change">${metric.change}</div>` : ''}
        `;
        grid.appendChild(card);
    });
}

// Render network visualization
function renderNetwork(data) {
    const container = document.getElementById('network-container');
    container.innerHTML = '';
    
    // Determine which network to show
    let network;
    if (currentView === 'pre') {
        network = data.pre_bi_network;
    } else {
        network = data.network;
    }
    
    const width = container.clientWidth;
    const height = container.clientHeight;
    
    // Create SVG with zoom capability
    const svg = d3.select(container)
        .append('svg')
        .attr('class', 'network-svg')
        .attr('width', width)
        .attr('height', height);
    
    // Add zoom behavior
    const zoom = d3.zoom()
        .scaleExtent([0.3, 3])
        .on('zoom', (event) => {
            g.attr('transform', event.transform);
            currentZoom = event.transform;
        });
    
    svg.call(zoom);
    currentZoom = d3.zoomIdentity;
    
    // Create a group for all elements
    const g = svg.append('g');
    
    // Create tooltip
    const tooltip = d3.select('#tooltip');
    
    // Create force simulation with different parameters for pre/post BI
    const chargeStrength = currentView === 'pre' ? -200 : -300;
    const linkDistance = currentView === 'pre' ? 80 : 50;
    
    simulation = d3.forceSimulation(network.nodes)
        .force('link', d3.forceLink(network.links).id(d => d.id).distance(d => linkDistance + d.strength * 30))
        .force('charge', d3.forceManyBody().strength(chargeStrength))
        .force('center', d3.forceCenter(width / 2, height / 2))
        .force('collision', d3.forceCollide().radius(d => d.size + 5))
        .alpha(1)
        .restart();
    
    // Create links
    const link = g.append('g')
        .selectAll('line')
        .data(network.links)
        .enter()
        .append('line')
        .attr('class', d => `link ${d.type}`)
        .attr('stroke-width', d => Math.sqrt(d.strength) * 2);
    
    // Create nodes
    const node = g.append('g')
        .selectAll('circle')
        .data(network.nodes)
        .enter()
        .append('circle')
        .attr('class', d => `node ${d.type}`)
        .attr('r', d => d.size)
        .attr('fill', d => nodeColors[d.type] || '#999')
        .attr('stroke', d => {
            const strokeColors = {
                decision_maker: '#2E7D32',
                process: '#E65100',
                data_source: '#1565C0'
            };
            return strokeColors[d.type] || '#666';
        })
        .attr('stroke-width', d => d.type === 'decision_maker' ? 3 : d.type === 'process' ? 2 : 1.5)
        .call(drag(simulation))
        .on('mouseover', function(event, d) {
            tooltip.style('display', 'block')
                .html(`
                    <strong>${d.label || d.id}</strong><br/>
                    النوع: ${getTypeName(d.type)}<br/>
                    ${d.industry ? `الصناعة: ${d.industry}<br/>` : ''}
                    ${d.agility ? `المرونة: ${d.agility.toFixed(1)}<br/>` : ''}
                    ${d.efficiency ? `الكفاءة: ${d.efficiency.toFixed(1)}<br/>` : ''}
                    ${d.company_count ? `عدد الشركات: ${d.company_count}` : ''}
                `)
                .style('left', (event.pageX + 10) + 'px')
                .style('top', (event.pageY - 10) + 'px');
        })
        .on('mousemove', function(event) {
            tooltip.style('left', (event.pageX + 10) + 'px')
                .style('top', (event.pageY - 10) + 'px');
        })
        .on('mouseout', function() {
            tooltip.style('display', 'none');
        });
    
    // Add labels for important nodes
    const labels = g.append('g')
        .selectAll('text')
        .data(network.nodes.filter(d => d.type !== 'data_source' || d.size > 15))
        .enter()
        .append('text')
        .text(d => d.label || d.id)
        .attr('font-size', d => d.type === 'decision_maker' ? '14px' : '10px')
        .attr('font-weight', d => d.type === 'decision_maker' ? 'bold' : 'normal')
        .attr('fill', '#333')
        .attr('text-anchor', 'middle')
        .attr('dy', d => d.size + 15);
    
    // Update positions on simulation tick
    simulation.on('tick', () => {
        link
            .attr('x1', d => d.source.x)
            .attr('y1', d => d.source.y)
            .attr('x2', d => d.target.x)
            .attr('y2', d => d.target.y);
        
        node
            .attr('cx', d => d.x)
            .attr('cy', d => d.y);
        
        labels
            .attr('x', d => d.x)
            .attr('y', d => d.y);
    });
}

// Drag behavior
function drag(simulation) {
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
    
    return d3.drag()
        .on('start', dragstarted)
        .on('drag', dragged)
        .on('end', dragended);
}

// Get type name in Arabic
function getTypeName(type) {
    const names = {
        decision_maker: 'صانع القرار',
        process: 'عملية/قسم',
        data_source: 'مصدر بيانات'
    };
    return names[type] || type;
}

// Update charts
function updateCharts(data) {
    const metrics = data.metrics;
    
    // Performance Chart
    updatePerformanceChart(metrics);
    
    // Industry Distribution Chart
    updateIndustryChart(metrics);
    
    // Comparison Chart
    updateComparisonChart(metrics);
    
    // Growth Chart
    updateGrowthChart(metrics);
}

function updatePerformanceChart(metrics) {
    const ctx = document.getElementById('performance-chart');
    if (charts.performance) {
        charts.performance.destroy();
    }
    
    charts.performance = new Chart(ctx, {
        type: 'radar',
        data: {
            labels: ['المرونة', 'الكفاءة', 'القرارات المبنية على البيانات', 'نمو الإيرادات', 'تقليل التكاليف'],
            datasets: [{
                label: 'قبل BI',
                data: [
                    metrics.avg_pre_bi_agility * 10,
                    metrics.avg_pre_bi_efficiency,
                    metrics.avg_pre_bi_data_driven,
                    metrics.avg_revenue_growth * 2,
                    metrics.avg_cost_reduction * 2
                ],
                borderColor: 'rgb(255, 99, 132)',
                backgroundColor: 'rgba(255, 99, 132, 0.2)',
                pointBackgroundColor: 'rgb(255, 99, 132)'
            }, {
                label: 'بعد BI',
                data: [
                    metrics.avg_post_bi_agility * 10,
                    metrics.avg_post_bi_efficiency,
                    metrics.avg_post_bi_data_driven,
                    metrics.avg_revenue_growth * 2,
                    metrics.avg_cost_reduction * 2
                ],
                borderColor: 'rgb(54, 162, 235)',
                backgroundColor: 'rgba(54, 162, 235, 0.2)',
                pointBackgroundColor: 'rgb(54, 162, 235)'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                }
            },
            scales: {
                r: {
                    beginAtZero: true,
                    max: 100
                }
            }
        }
    });
}

function updateIndustryChart(metrics) {
    const ctx = document.getElementById('industry-chart');
    if (charts.industry) {
        charts.industry.destroy();
    }
    
    const industries = Object.keys(metrics.industries);
    const counts = Object.values(metrics.industries);
    
    charts.industry = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: industries,
            datasets: [{
                data: counts,
                backgroundColor: [
                    'rgba(255, 99, 132, 0.8)',
                    'rgba(54, 162, 235, 0.8)',
                    'rgba(255, 206, 86, 0.8)',
                    'rgba(75, 192, 192, 0.8)',
                    'rgba(153, 102, 255, 0.8)',
                    'rgba(255, 159, 64, 0.8)',
                    'rgba(199, 199, 199, 0.8)'
                ],
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                }
            }
        }
    });
}

function updateComparisonChart(metrics) {
    const ctx = document.getElementById('comparison-chart');
    if (charts.comparison) {
        charts.comparison.destroy();
    }
    
    charts.comparison = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['المرونة', 'الكفاءة', 'القرارات المبنية على البيانات'],
            datasets: [{
                label: 'قبل BI',
                data: [
                    metrics.avg_pre_bi_agility,
                    metrics.avg_pre_bi_efficiency,
                    metrics.avg_pre_bi_data_driven
                ],
                backgroundColor: 'rgba(255, 99, 132, 0.8)'
            }, {
                label: 'بعد BI',
                data: [
                    metrics.avg_post_bi_agility,
                    metrics.avg_post_bi_efficiency,
                    metrics.avg_post_bi_data_driven
                ],
                backgroundColor: 'rgba(54, 162, 235, 0.8)'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100
                }
            }
        }
    });
}

function updateGrowthChart(metrics) {
    const ctx = document.getElementById('growth-chart');
    if (charts.growth) {
        charts.growth.destroy();
    }
    
    charts.growth = new Chart(ctx, {
        type: 'line',
        data: {
            labels: ['نمو الإيرادات', 'تقليل التكاليف', 'رضا العملاء', 'الحصة السوقية'],
            datasets: [{
                label: 'النمو (%)',
                data: [
                    metrics.avg_revenue_growth,
                    metrics.avg_cost_reduction,
                    metrics.avg_customer_satisfaction,
                    metrics.avg_market_share
                ],
                borderColor: 'rgb(75, 192, 192)',
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                }
            },
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

// Switch view between pre and post BI
function switchView(view) {
    currentView = view;
    
    // Update toggle buttons
    document.getElementById('toggle-post').classList.toggle('active', view === 'post');
    document.getElementById('toggle-pre').classList.toggle('active', view === 'pre');
    
    // Update select
    document.getElementById('view-mode').value = view;
    
    // Reload network
    if (currentGovernorate) {
        loadGovernorate(currentGovernorate);
    }
}

// Reset network view
function resetView() {
    if (simulation) {
        simulation.alpha(1).restart();
    }
}

// Reset zoom
function resetZoom() {
    const svg = d3.select('.network-svg');
    if (svg && svg.node()) {
        svg.transition()
            .duration(750)
            .call(
                d3.zoom().transform,
                d3.zoomIdentity
            );
    }
}

// Export data
function exportData() {
    if (!currentGovernorate || !networkData[currentGovernorate]) {
        alert('يرجى اختيار محافظة أولاً');
        return;
    }
    
    const data = networkData[currentGovernorate];
    const jsonStr = JSON.stringify(data, null, 2);
    const blob = new Blob([jsonStr], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${currentGovernorate}_network_data.json`;
    a.click();
    URL.revokeObjectURL(url);
}

// Initialize on load
window.addEventListener('DOMContentLoaded', init);

// Handle window resize
window.addEventListener('resize', () => {
    if (currentGovernorate) {
        loadGovernorate(currentGovernorate);
    }
});

