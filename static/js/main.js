document.addEventListener('DOMContentLoaded', setupTabs);

let storkChart, hourlyChart, dailyChart, occupancyChart;
let explorerTableInitialized = false;

function setupTabs() {
    const tabButtons = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');

    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            const tabId = button.dataset.tab;
            tabButtons.forEach(btn => btn.classList.remove('active'));
            button.classList.add('active');
            tabContents.forEach(content => {
                content.classList.remove('active');
                if (content.id === tabId) {
                    content.classList.add('active');
                }
            });

            if (tabId === 'explorer' && !explorerTableInitialized) {
                initializeExplorerTable();
                explorerTableInitialized = true;
            }
        });
    });
}

function initializeExplorerTable() {
    const table = $('#detections-table').DataTable({
        ajax: '/all_data',
        columns: [
            { data: 'id' },
            { data: 'timestamp' },
            { data: 'stork_count' },
            { data: 'image_path' }
        ],
        order: [[0, 'desc']]
    });

    $('#filter-form').on('submit', function (e) {
        e.preventDefault();

        const operator = $('#count_operator').val();
        const count = $('#stork_count').val();
        const startDate = $('#start_date').val();
        const endDate = $('#end_date').val();

        const apiUrl = `/query_data?operator=${operator}&count=${count}&start_date=${startDate}&end_date=${endDate}`;

        table.ajax.url(apiUrl).load();
    });

    $('#reset-btn').on('click', function() {
        $('#filter-form')[0].reset();
        table.ajax.url('/all_data').load();
    });
}

function fetchStatusData() {
    fetch('/current_status')
        .then(response => response.json())
        .then(data => {
            document.getElementById('kpi-current-count').innerText = data.current_count;
            document.getElementById('kpi-nest-status').innerText = data.nest_status;
            document.getElementById('kpi-busiest-hour').innerText = data.busiest_hour;
            document.getElementById('kpi-last-seen').innerText = data.last_seen;
        })
        .catch(error => console.error('Error fetching status data:', error));
}

function fetchLatestDetection() {
    fetch('/latest_detection')
        .then(response => response.json())
        .then(data => {
            const gallery = document.getElementById('thumbnail-gallery');
            if (gallery) gallery.innerHTML = '';

            if (data.recent_files && data.recent_files.length > 0) {
                const latestImageFile = data.recent_files[0];
                const imageUrl = '/detections/' + latestImageFile + '?t=' + new Date().getTime();
                document.getElementById('detection-image').src = imageUrl;
                document.getElementById('last-updated').innerText = 'Last updated: ' + new Date().toLocaleTimeString();
                for (let i = 1; i < data.recent_files.length; i++) {
                    const thumbUrl = '/detections/' + data.recent_files[i];
                    const imgElement = document.createElement('img');
                    imgElement.src = thumbUrl;
                    if (gallery) gallery.appendChild(imgElement);
                }
            }
        })
        .catch(error => console.error('Error fetching detections:', error));
}

function renderDetectionChart(chartData) {
    // --- ID CORREGIDO AQUÍ ---
    const canvas = document.getElementById('stork-chart');
    if (!canvas) return; // Comprobación de seguridad
    const ctx = canvas.getContext('2d');
    if (storkChart) {
        storkChart.data.labels = chartData.labels;
        storkChart.data.datasets[0].data = chartData.data;
        storkChart.update();
    } else {
        storkChart = new Chart(ctx, {
            type: 'line',
            data: { labels: chartData.labels, datasets: [{ label: 'Número de Cigüeñas Detectadas', data: chartData.data, borderColor: 'rgb(75, 192, 192)', backgroundColor: 'rgba(75, 192, 192, 0.2)', fill: true, tension: 0.4, pointBackgroundColor: 'rgb(75, 192, 192)' }] },
            options: { scales: { y: { beginAtZero: true, ticks: { stepSize: 1, color: '#ddd' }, grid: { color: 'rgba(255, 255, 255, 0.1)' } }, x: { ticks: { color: '#ddd' }, grid: { color: 'rgba(255, 255, 255, 0.1)' } } }, plugins: { legend: { labels: { color: '#ddd' } } } }
        });
    }
}

function fetchChartData() {
    fetch('/detection_data')
        .then(response => response.json())
        .then(data => { if (data.labels) renderDetectionChart(data); })
        .catch(error => console.error('Error fetching line chart data:', error));
}

function renderHourlyChart(chartData) {
    const canvas = document.getElementById('hourly-chart');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    const labels = chartData.labels.map(h => `${h}:00`);
    if (hourlyChart) {
        hourlyChart.data.labels = labels;
        hourlyChart.data.datasets[0].data = chartData.data;
        hourlyChart.update();
    } else {
        hourlyChart = new Chart(ctx, {
            type: 'bar',
            data: { labels: labels, datasets: [{ label: 'Número Medio de Cigüeñas', data: chartData.data, backgroundColor: 'rgba(183, 230, 28, 0.6)', borderColor: 'rgba(183, 230, 28, 1)', hoverBackgroundColor: 'rgba(183, 230, 28, 0.9)', borderWidth: 1 }] },
            options: { scales: { y: { beginAtZero: true, ticks: { color: '#ddd' }, grid: { color: 'rgba(255, 255, 255, 0.1)' } }, x: { ticks: { color: '#ddd' }, grid: { display: false } } }, plugins: { legend: { labels: { color: '#ddd' } } } }
        });
    }
}

function fetchHourlyData() {
    fetch('/hourly_activity')
        .then(response => response.json())
        .then(data => { if (data.labels) renderHourlyChart(data); })
        .catch(error => console.error('Error fetching hourly data:', error));
}

function renderDailyChart(chartData) {
    const canvas = document.getElementById('daily-chart');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (dailyChart) {
        dailyChart.data.labels = chartData.labels;
        dailyChart.data.datasets[0].data = chartData.data;
        dailyChart.update();
    } else {
        dailyChart = new Chart(ctx, {
            type: 'bar',
            data: { labels: chartData.labels, datasets: [{ label: 'Average Stork Count', data: chartData.data, backgroundColor: 'rgba(255, 159, 64, 0.6)', borderColor: 'rgba(255, 159, 64, 1)', borderWidth: 1 }] },
            options: { scales: { y: { beginAtZero: true } } }
        });
    }
}

function fetchDailyData() {
    fetch('/daily_activity')
        .then(response => response.json())
        .then(data => { if (data.labels) renderDailyChart(data); })
        .catch(error => console.error('Error fetching daily data:', error));
}

function renderOccupancyChart(chartData) {
    const canvas = document.getElementById('occupancy-chart');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (occupancyChart) {
        occupancyChart.data.datasets[0].data = chartData.data;
        occupancyChart.update();
    } else {
        occupancyChart = new Chart(ctx, {
            type: 'doughnut',
            data: { labels: chartData.labels, datasets: [{ label: 'Detections', data: chartData.data, backgroundColor: ['rgba(54, 162, 255, 0.6)', 'rgba(255, 99, 132, 0.6)'], borderColor: ['rgba(54, 162, 235, 1)', 'rgba(255, 99, 132, 1)'], borderWidth: 1 }] }
        });
    }
}

function fetchOccupancyData() {
    fetch('/occupancy_status')
        .then(response => response.json())
        .then(data => { if (data.labels) renderOccupancyChart(data); })
        .catch(error => console.error('Error fetching occupancy data:', error));
}

function updateAllData() {
    fetchStatusData();
    fetchLatestDetection();
    fetchChartData();
    fetchHourlyData();
    fetchDailyData();
    fetchOccupancyData();
}

updateAllData();
setInterval(updateAllData, 30000);

const header = document.querySelector('header');
const tabNav = document.querySelector('.tab-nav');
let lastScrollTop = 0;

window.addEventListener("scroll", function () {
    let scrollTop = window.pageYOffset || document.documentElement.scrollTop;
    
    if (scrollTop > lastScrollTop && scrollTop > 60) {
        header.classList.add('header-hidden');
        tabNav.classList.add('nav-scrolled');
    } else {
        header.classList.remove('header-hidden');
        tabNav.classList.remove('nav-scrolled');
    }
    
    lastScrollTop = scrollTop <= 0 ? 0 : scrollTop;
});