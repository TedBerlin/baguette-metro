// Dashboard Baguette & Métro - Gestionnaire dynamique

class DashboardManager {
    constructor() {
        this.apiBaseUrl = 'http://127.0.0.1:8000';
        this.updateInterval = 30000; // 30 secondes
        this.charts = {};
        this.init();
    }

    async init() {
        console.log('🚀 Initialisation du dashboard...');
        await this.loadDashboardData();
        this.setupCharts();
        this.setupAutoUpdate();
        this.setupEventListeners();
    }

    async loadDashboardData() {
        try {
            console.log('📊 Chargement des données du dashboard...');
            const response = await fetch(`${this.apiBaseUrl}/dashboard/data`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            console.log('✅ Données chargées:', data);
            
            this.updateMetrics(data.metrics);
            this.updateRATPStatus(data.ratp);
            this.updateCitymapperComparison(data.citymapper);
            this.updateRealTimeUpdates(data.citymapper.real_time_updates);
            this.updateLastUpdateTime(data.timestamp);
            
        } catch (error) {
            console.error('❌ Erreur lors du chargement des données:', error);
            this.showError('Erreur de connexion à l\'API');
        }
    }

    updateMetrics(metrics) {
        if (!metrics) return;
        
        document.getElementById('total-routes').textContent = metrics.total_routes || '--';
        document.getElementById('active-users').textContent = metrics.active_users || '--';
        document.getElementById('bakeries-found').textContent = metrics.bakeries_found || '--';
        document.getElementById('eco-percentage').textContent = `${metrics.eco_routes_percentage || '--'}%`;
    }

    updateRATPStatus(ratpData) {
        if (!ratpData) return;

        // État des lignes
        const linesStatusContainer = document.getElementById('ratp-lines-status');
        if (linesStatusContainer && ratpData.lines_status) {
            linesStatusContainer.innerHTML = ratpData.lines_status.map(line => `
                <div class="status-item">
                    <span>${line.line}</span>
                    <span class="status-${line.status.toLowerCase()}">${line.status}</span>
                </div>
            `).join('');
        }

        // Affluence des stations
        const crowdingContainer = document.getElementById('ratp-crowding');
        if (crowdingContainer && ratpData.stations_crowding) {
            crowdingContainer.innerHTML = ratpData.stations_crowding.map(station => `
                <div class="crowding-item">
                    <span>${station.station}</span>
                    <span>${station.crowding} (${station.level}%)</span>
                </div>
            `).join('');
        }

        // Retards et perturbations
        const delaysContainer = document.getElementById('ratp-delays');
        if (delaysContainer && ratpData.delays) {
            delaysContainer.innerHTML = ratpData.delays.map(delay => `
                <div class="delay-item">
                    <span>${delay.line}</span>
                    <span>${delay.delay} - ${delay.reason}</span>
                </div>
            `).join('');
        }
    }

    updateCitymapperComparison(citymapperData) {
        if (!citymapperData || !citymapperData.routes_comparison) return;

        const container = document.getElementById('routes-comparison');
        if (!container) return;

        container.innerHTML = citymapperData.routes_comparison.map(route => `
            <div class="route-card">
                <h4>${route.route}</h4>
                <div class="route-duration">${route.duration}</div>
                <div class="route-cost">${route.cost}</div>
                <div class="route-comfort">Confort: ${route.comfort}</div>
                ${route.eco_friendly ? '<div class="eco-badge">🌱 Éco-responsable</div>' : ''}
            </div>
        `).join('');
    }

    updateRealTimeUpdates(updates) {
        if (!updates) return;

        const container = document.getElementById('real-time-updates');
        if (!container) return;

        container.innerHTML = updates.map(update => `
            <div class="update-item severity-${update.severity}">
                <span class="update-type">${update.type}</span>
                <span class="update-message">${update.message}</span>
            </div>
        `).join('');
    }

    updateLastUpdateTime(timestamp) {
        const timeElement = document.getElementById('last-update-time');
        if (timeElement && timestamp) {
            const date = new Date(timestamp);
            timeElement.textContent = date.toLocaleString('fr-FR');
        }
    }

    setupCharts() {
        console.log('📈 Configuration des graphiques...');
        
        // Graphique des temps de trajet
        this.setupJourneyChart();
        
        // Graphique de l'état RATP
        this.setupRATPStatusChart();
    }

    setupJourneyChart() {
        const ctx = document.getElementById('journey-chart');
        if (!ctx) return;

        this.charts.journey = new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['6h', '8h', '10h', '12h', '14h', '16h', '18h', '20h'],
                datasets: [{
                    label: 'Temps moyen (min)',
                    data: [25, 35, 28, 30, 28, 32, 38, 30],
                    borderColor: '#3498db',
                    backgroundColor: 'rgba(52, 152, 219, 0.1)',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Minutes'
                        }
                    }
                }
            }
        });
    }

    setupRATPStatusChart() {
        const ctx = document.getElementById('ratp-status-chart');
        if (!ctx) return;

        this.charts.ratpStatus = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Normal', 'Perturbé', 'Interrompu'],
                datasets: [{
                    data: [3, 1, 1],
                    backgroundColor: [
                        '#27ae60', // Vert
                        '#f39c12', // Orange
                        '#e74c3c'  // Rouge
                    ],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }

    setupAutoUpdate() {
        console.log('🔄 Configuration de la mise à jour automatique...');
        setInterval(() => {
            this.loadDashboardData();
        }, this.updateInterval);
    }

    setupEventListeners() {
        // Mise à jour manuelle
        document.addEventListener('keydown', (e) => {
            if (e.key === 'r' && e.ctrlKey) {
                e.preventDefault();
                this.loadDashboardData();
            }
        });

        // Mise à jour lors de la visibilité
        document.addEventListener('visibilitychange', () => {
            if (!document.hidden) {
                this.loadDashboardData();
            }
        });
    }

    showError(message) {
        console.error('❌ Erreur dashboard:', message);
        // Ici on pourrait afficher une notification d'erreur
    }

    // Méthode pour forcer la mise à jour
    forceUpdate() {
        this.loadDashboardData();
    }
}

// Initialisation automatique quand le DOM est prêt
document.addEventListener('DOMContentLoaded', () => {
    console.log('🎯 Dashboard Baguette & Métro - Chargement...');
    window.dashboardManager = new DashboardManager();
});

// Export pour utilisation externe
if (typeof module !== 'undefined' && module.exports) {
    module.exports = DashboardManager;
}
