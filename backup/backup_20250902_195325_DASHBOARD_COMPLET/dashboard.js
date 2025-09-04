/**
 * Dashboard Baguette & Métro - JavaScript en continuité
 * Intégration harmonieuse avec l'application existante
 */

class DashboardManager {
    constructor() {
        this.charts = {};
        this.updateInterval = null;
        this.isInitialized = false;
        
        // Configuration en continuité avec l'app
        this.config = {
            updateFrequency: 30000, // 30 secondes
            apiBaseUrl: 'http://localhost:8000',
            chartColors: {
                primary: '#3498db',
                secondary: '#2c3e50',
                success: '#27ae60',
                warning: '#f39c12',
                danger: '#e74c3c'
            }
        };
        
        this.init();
    }
    
    /**
     * Initialisation du dashboard
     */
    init() {
        if (this.isInitialized) return;
        
        console.log('🚀 Initialisation du Dashboard Baguette & Métro');
        
        // Initialisation des composants
        this.initMetrics();
        this.initCharts();
        this.initComparison();
        this.initRealTimeData();
        
        // Démarrage des mises à jour automatiques
        this.startAutoUpdate();
        
        // Mise à jour initiale
        this.updateDashboard();
        
        this.isInitialized = true;
        console.log('✅ Dashboard initialisé avec succès');
    }
    
    /**
     * Initialisation des métriques principales
     */
    initMetrics() {
        console.log('📊 Initialisation des métriques');
        
        // Métriques avec données simulées cohérentes
        const metrics = {
            'total-vehicles': { value: 1247, change: '+2.5%' },
            'active-lines': { value: 16, change: '0%' },
            'avg-speed': { value: '32.4', change: '+1.2%' },
            'satisfaction': { value: '4.2', change: '+0.3' }
        };
        
        // Application des métriques
        Object.keys(metrics).forEach(id => {
            const element = document.getElementById(id);
            if (element) {
                element.textContent = metrics[id].value;
                
                // Mise à jour du changement
                const changeElement = element.parentElement.querySelector('.metric-change');
                if (changeElement) {
                    changeElement.textContent = metrics[id].change;
                    changeElement.className = `metric-change ${this.getChangeClass(metrics[id].change)}`;
                }
            }
        });
        
        // Mise à jour de la dernière MAJ
        const lastUpdate = document.getElementById('last-update');
        if (lastUpdate) {
            lastUpdate.textContent = new Date().toLocaleTimeString('fr-FR');
        }
    }
    
    /**
     * Initialisation des graphiques Chart.js
     */
    initCharts() {
        console.log('📈 Initialisation des graphiques');
        
        // Graphique de performance des lignes
        this.initLinePerformanceChart();
        
        // Graphique des heures de pointe
        this.initPeakHoursChart();
    }
    
    /**
     * Graphique de performance des lignes
     */
    initLinePerformanceChart() {
        const ctx = document.getElementById('linePerformanceChart');
        if (!ctx) return;
        
        const data = {
            labels: ['Ligne 1', 'Ligne 4', 'Ligne 6', 'Ligne 9', 'Ligne 14'],
            datasets: [{
                label: 'Ponctualité (%)',
                data: [94.2, 91.8, 96.1, 89.7, 98.3],
                backgroundColor: this.config.chartColors.primary,
                borderColor: this.config.chartColors.secondary,
                borderWidth: 2,
                borderRadius: 4
            }]
        };
        
        this.charts.linePerformance = new Chart(ctx, {
            type: 'bar',
            data: data,
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
                        max: 100,
                        ticks: {
                            callback: function(value) {
                                return value + '%';
                            }
                        }
                    }
                }
            }
        });
    }
    
    /**
     * Graphique des heures de pointe
     */
    initPeakHoursChart() {
        const ctx = document.getElementById('peakHoursChart');
        if (!ctx) return;
        
        const data = {
            labels: ['6h', '8h', '10h', '12h', '14h', '16h', '18h', '20h', '22h'],
            datasets: [{
                label: 'Trafic (voyageurs/h)',
                data: [1200, 8500, 3200, 4100, 3800, 7200, 8900, 5400, 2100],
                borderColor: this.config.chartColors.success,
                backgroundColor: 'rgba(39, 174, 96, 0.1)',
                borderWidth: 3,
                fill: true,
                tension: 0.4
            }]
        };
        
        this.charts.peakHours = new Chart(ctx, {
            type: 'line',
            data: data,
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
                        ticks: {
                            callback: function(value) {
                                return (value / 1000).toFixed(1) + 'k';
                            }
                        }
                    }
                }
            }
        });
    }
    
    /**
     * Initialisation de la comparaison Citymapper
     */
    initComparison() {
        console.log('🏆 Initialisation de la comparaison Citymapper');
        
        // Données de comparaison simulées
        const comparisonData = {
            ratp: { accuracy: '94.2%', advantage: 'RATP' },
            citymapper: { accuracy: '89.7%', advantage: 'RATP' }
        };
        
        // Application des données
        const ratpAccuracy = document.getElementById('ratp-accuracy');
        const citymapperAccuracy = document.getElementById('citymapper-accuracy');
        const advantageText = document.getElementById('advantage-text');
        
        if (ratpAccuracy) ratpAccuracy.textContent = comparisonData.ratp.accuracy;
        if (citymapperAccuracy) citymapperAccuracy.textContent = comparisonData.citymapper.accuracy;
        if (advantageText) advantageText.textContent = comparisonData.ratp.advantage;
    }
    
    /**
     * Initialisation des données temps réel
     */
    initRealTimeData() {
        console.log('📡 Initialisation des données temps réel');
        
        // Données simulées cohérentes
        const realtimeData = {
            'total-delays': 12,
            'avg-delay': '3.2',
            'prim-stations': 302
        };
        
        // Application des données
        Object.keys(realtimeData).forEach(id => {
            const element = document.getElementById(id);
            if (element) {
                element.textContent = realtimeData[id];
            }
        });
    }
    
    /**
     * Mise à jour automatique du dashboard
     */
    startAutoUpdate() {
        this.updateInterval = setInterval(() => {
            this.updateDashboard();
        }, this.config.updateFrequency);
        
        console.log(`🔄 Mise à jour automatique configurée (${this.config.updateFrequency / 1000}s)`);
    }
    
    /**
     * Mise à jour complète du dashboard
     */
    async updateDashboard() {
        try {
            console.log('🔄 Mise à jour du dashboard...');
            
            // Mise à jour des métriques
            await this.updateMetrics();
            
            // Mise à jour des données temps réel
            await this.updateRealTimeData();
            
            // Mise à jour de la dernière MAJ
            const lastUpdate = document.getElementById('last-update');
            if (lastUpdate) {
                lastUpdate.textContent = new Date().toLocaleTimeString('fr-FR');
            }
            
            console.log('✅ Dashboard mis à jour avec succès');
            
        } catch (error) {
            console.error('❌ Erreur lors de la mise à jour du dashboard:', error);
        }
    }
    
    /**
     * Mise à jour des métriques via API
     */
    async updateMetrics() {
        try {
            // Simulation de données API (remplacé par de vraies données plus tard)
            const mockData = {
                total_vehicles: Math.floor(1200 + Math.random() * 100),
                active_lines: 16,
                avg_speed: (30 + Math.random() * 5).toFixed(1),
                satisfaction: (4.0 + Math.random() * 0.5).toFixed(1)
            };
            
            // Application des nouvelles données
            this.updateMetricValue('total-vehicles', mockData.total_vehicles);
            this.updateMetricValue('avg-speed', mockData.avg_speed + ' km/h');
            this.updateMetricValue('satisfaction', mockData.satisfaction + '/5');
            
        } catch (error) {
            console.warn('⚠️ Impossible de mettre à jour les métriques:', error);
        }
    }
    
    /**
     * Mise à jour des données temps réel
     */
    async updateRealTimeData() {
        try {
            // Simulation de données temps réel
            const mockData = {
                total_delays: Math.floor(8 + Math.random() * 8),
                avg_delay: (2.5 + Math.random() * 2).toFixed(1),
                prim_stations: 302
            };
            
            // Application des nouvelles données
            this.updateMetricValue('total-delays', mockData.total_delays);
            this.updateMetricValue('avg-delay', mockData.avg_delay);
            
        } catch (error) {
            console.warn('⚠️ Impossible de mettre à jour les données temps réel:', error);
        }
    }
    
    /**
     * Mise à jour d'une valeur métrique
     */
    updateMetricValue(id, newValue) {
        const element = document.getElementById(id);
        if (element) {
            // Animation de transition
            element.style.transition = 'all 0.3s ease';
            element.style.transform = 'scale(1.05)';
            
            setTimeout(() => {
                element.textContent = newValue;
                element.style.transform = 'scale(1)';
            }, 150);
        }
    }
    
    /**
     * Détermination de la classe CSS pour les changements
     */
    getChangeClass(change) {
        if (change.startsWith('+')) return 'positive';
        if (change.startsWith('-')) return 'negative';
        return 'neutral';
    }
    
    /**
     * Nettoyage et destruction du dashboard
     */
    destroy() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
        }
        
        // Destruction des graphiques
        Object.values(this.charts).forEach(chart => {
            if (chart && chart.destroy) {
                chart.destroy();
            }
        });
        
        this.isInitialized = false;
        console.log('🗑️ Dashboard détruit');
    }
}

// Initialisation automatique quand le DOM est prêt
document.addEventListener('DOMContentLoaded', () => {
    console.log('🌍 DOM chargé - Initialisation du Dashboard');
    window.dashboardManager = new DashboardManager();
});

// Gestion de la visibilité de la page pour optimiser les mises à jour
document.addEventListener('visibilitychange', () => {
    if (window.dashboardManager) {
        if (document.hidden) {
            console.log('📱 Page masquée - Pause des mises à jour');
            if (window.dashboardManager.updateInterval) {
                clearInterval(window.dashboardManager.updateInterval);
            }
        } else {
            console.log('📱 Page visible - Reprise des mises à jour');
            window.dashboardManager.startAutoUpdate();
        }
    }
});
