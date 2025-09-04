/* 🚇 DONNÉES SIMULÉES CITYMAPPER - BAGUETTE & MÉTRO */
/* Données réalistes pour le dashboard avec métriques Citymapper */

// ============================================================================
// 🎯 GÉNÉRATEUR DE DONNÉES SIMULÉES CITYMAPPER
// ============================================================================

class CitymapperDataSimulator {
    constructor() {
        this.baseTime = Date.now();
        this.lines = [
            { id: '1', name: 'Ligne 1', color: '#FFCD00', status: 'normal' },
            { id: '2', name: 'Ligne 2', color: '#003CA6', status: 'normal' },
            { id: '3', name: 'Ligne 3', color: '#837902', status: 'perturbed' },
            { id: '4', name: 'Ligne 4', color: '#CF009E', status: 'normal' },
            { id: '5', name: 'Ligne 5', color: '#FF7E2E', status: 'normal' },
            { id: '6', name: 'Ligne 6', color: '#6ECA97', status: 'normal' },
            { id: '7', color: '#FA9ABA', status: 'normal' },
            { id: '8', color: '#E19BDF', status: 'normal' },
            { id: '9', color: '#B6BD00', status: 'normal' },
            { id: '10', color: '#C9910D', status: 'normal' },
            { id: '11', color: '#704B1C', status: 'normal' },
            { id: '12', color: '#007852', status: 'normal' },
            { id: '13', color: '#6EC4E8', status: 'normal' },
            { id: '14', color: '#62259D', status: 'normal' },
            { id: 'A', name: 'RER A', color: '#E2231A', status: 'perturbed' },
            { id: 'B', name: 'RER B', color: '#003CA6', status: 'normal' },
            { id: 'C', name: 'RER C', color: '#FDBC00', status: 'normal' },
            { id: 'D', name: 'RER D', color: '#00AC41', status: 'normal' },
            { id: 'E', name: 'RER E', color: '#D85A10', status: 'normal' }
        ];
        
        this.stations = [
            { id: 'chatelet', name: 'Châtelet-Les Halles', passengers: 750000, delay: 0 },
            { id: 'gare_du_nord', name: 'Gare du Nord', passengers: 214000, delay: 2 },
            { id: 'nation', name: 'Nation', passengers: 180000, delay: 0 },
            { id: 'republique', name: 'République', passengers: 165000, delay: 1 },
            { id: 'bastille', name: 'Bastille', passengers: 155000, delay: 0 },
            { id: 'opera', name: 'Opéra', passengers: 145000, delay: 0 },
            { id: 'concorde', name: 'Concorde', passengers: 140000, delay: 0 },
            { id: 'louvre', name: 'Louvre-Rivoli', passengers: 135000, delay: 0 },
            { id: 'hotel_ville', name: 'Hôtel de Ville', passengers: 130000, delay: 0 },
            { id: 'cdg', name: 'Aéroport CDG', passengers: 125000, delay: 3 }
        ];
        
        this.bakeries = [
            { name: 'Boulangerie Julien', rating: 4.8, distance: 120, waitTime: 2 },
            { name: 'Pain & Tradition', rating: 4.6, distance: 200, waitTime: 3 },
            { name: 'Le Grenier à Pain', rating: 4.9, distance: 150, waitTime: 4 },
            { name: 'Boulangerie Poilâne', rating: 4.7, distance: 300, waitTime: 5 },
            { name: 'Du Pain et des Idées', rating: 4.8, distance: 180, waitTime: 3 }
        ];
    }
    
    // 🚇 Générer données RATP réalistes
    generateRATPData() {
        const now = new Date();
        const hour = now.getHours();
        
        // Simulation des perturbations selon l'heure
        let perturbedLines = [];
        if (hour >= 7 && hour <= 9) { // Heure de pointe matin
            perturbedLines = ['3', 'A'];
        } else if (hour >= 17 && hour <= 19) { // Heure de pointe soir
            perturbedLines = ['3', 'A', '1'];
        } else if (hour >= 22 || hour <= 6) { // Nuit
            perturbedLines = [];
        } else { // Heure normale
            perturbedLines = Math.random() > 0.7 ? ['3'] : [];
        }
        
        const linesStatus = this.lines.map(line => {
            const isPerturbed = perturbedLines.includes(line.id);
            return {
                line: line.id,
                name: line.name || `Ligne ${line.id}`,
                color: line.color,
                status: isPerturbed ? 'Perturbé' : 'Normal',
                delay: isPerturbed ? Math.floor(Math.random() * 5) + 1 : 0,
                frequency: isPerturbed ? Math.floor(Math.random() * 3) + 4 : Math.floor(Math.random() * 2) + 2
            };
        });
        
        return {
            timestamp: now.toISOString(),
            global_status: perturbedLines.length === 0 ? 'Normal' : 'Perturbé',
            ponctualite: Math.max(85, 100 - (perturbedLines.length * 8)),
            total_lines: this.lines.length,
            perturbed_lines: perturbedLines.length,
            lines_status: linesStatus
        };
    }
    
    // ⏱️ Générer données de temps de trajet
    generateTravelTimeData() {
        const now = new Date();
        const hour = now.getHours();
        const dayOfWeek = now.getDay();
        
        // Facteurs d'influence
        const isWeekend = dayOfWeek === 0 || dayOfWeek === 6;
        const isRushHour = (hour >= 7 && hour <= 9) || (hour >= 17 && hour <= 19);
        const isNight = hour >= 22 || hour <= 6;
        
        // Temps de base selon le type de trajet
        const baseTimes = {
            'CDG_Versailles': { normal: 89, rush: 120, night: 95 },
            'CDG_Chatelet': { normal: 45, rush: 65, night: 50 },
            'GareNord_Chatelet': { normal: 8, rush: 12, night: 10 },
            'Chatelet_Versailles': { normal: 39, rush: 55, night: 42 }
        };
        
        const travelTimes = {};
        Object.keys(baseTimes).forEach(route => {
            const base = baseTimes[route];
            let time;
            
            if (isNight) {
                time = base.night;
            } else if (isRushHour && !isWeekend) {
                time = base.rush;
            } else {
                time = base.normal;
            }
            
            // Ajouter de la variabilité
            time += Math.floor(Math.random() * 5) - 2;
            travelTimes[route] = Math.max(1, time);
        });
        
        return {
            timestamp: now.toISOString(),
            current_times: travelTimes,
            average_delay: isRushHour ? Math.floor(Math.random() * 8) + 3 : Math.floor(Math.random() * 3),
            congestion_level: isRushHour ? 'Élevé' : isNight ? 'Faible' : 'Modéré',
            recommendations: this.generateTravelRecommendations(hour, isWeekend)
        };
    }
    
    // 🥖 Générer données boulangeries
    generateBakeryData() {
        const now = new Date();
        const hour = now.getHours();
        
        // Simulation de l'affluence selon l'heure
        const isPeakTime = (hour >= 7 && hour <= 9) || (hour >= 17 && hour <= 19);
        const isLunchTime = hour >= 11 && hour <= 14;
        
        const bakeries = this.bakeries.map(bakery => {
            let waitTime = bakery.waitTime;
            let rating = bakery.rating;
            
            if (isPeakTime) {
                waitTime += Math.floor(Math.random() * 3) + 1;
                rating -= 0.1;
            } else if (isLunchTime) {
                waitTime += Math.floor(Math.random() * 2);
            }
            
            return {
                ...bakery,
                waitTime: Math.max(1, waitTime),
                rating: Math.max(4.0, rating),
                isOpen: hour >= 6 && hour <= 20,
                popularity: isPeakTime ? 'Élevée' : isLunchTime ? 'Modérée' : 'Faible'
            };
        });
        
        return {
            timestamp: now.toISOString(),
            total_bakeries: bakeries.length,
            open_bakeries: bakeries.filter(b => b.isOpen).length,
            average_wait_time: Math.round(bakeries.reduce((sum, b) => sum + b.waitTime, 0) / bakeries.length),
            peak_hours: isPeakTime,
            bakeries: bakeries
        };
    }
    
    // 🚶 Générer données piétons
    generatePedestrianData() {
        const now = new Date();
        const hour = now.getHours();
        const dayOfWeek = now.getDay();
        
        const isWeekend = dayOfWeek === 0 || dayOfWeek === 6;
        const isRushHour = (hour >= 7 && hour <= 9) || (hour >= 17 && hour <= 19);
        const isLunchTime = hour >= 11 && hour <= 14;
        
        // Simulation de l'affluence piétonne
        let baseTraffic = 30; // Base 30%
        
        if (isRushHour) baseTraffic += 40;
        if (isLunchTime) baseTraffic += 20;
        if (isWeekend) baseTraffic += 15;
        if (hour >= 22 || hour <= 6) baseTraffic -= 25;
        
        baseTraffic = Math.max(5, Math.min(95, baseTraffic));
        
        const stations = this.stations.map(station => {
            let passengers = station.passengers;
            let delay = station.delay;
            
            if (isRushHour) {
                passengers = Math.floor(passengers * 1.3);
                delay += Math.floor(Math.random() * 3);
            } else if (isLunchTime) {
                passengers = Math.floor(passengers * 1.1);
            } else if (hour >= 22 || hour <= 6) {
                passengers = Math.floor(passengers * 0.3);
                delay = 0;
            }
            
            return {
                ...station,
                passengers: passengers,
                delay: Math.max(0, delay),
                congestion: passengers > 200000 ? 'Élevée' : passengers > 150000 ? 'Modérée' : 'Faible'
            };
        });
        
        return {
            timestamp: now.toISOString(),
            global_traffic: baseTraffic,
            peak_stations: stations.filter(s => s.passengers > 200000).length,
            average_delay: Math.round(stations.reduce((sum, s) => sum + s.delay, 0) / stations.length),
            stations: stations
        };
    }
    
    // 💡 Générer recommandations de voyage
    generateTravelRecommendations(hour, isWeekend) {
        const recommendations = [];
        
        if (hour >= 7 && hour <= 9 && !isWeekend) {
            recommendations.push({
                type: 'warning',
                message: 'Heure de pointe matinale - Prévoyez 15-20 min supplémentaires'
            });
        }
        
        if (hour >= 17 && hour <= 19 && !isWeekend) {
            recommendations.push({
                type: 'warning',
                message: 'Heure de pointe vespérale - Évitez les correspondances complexes'
            });
        }
        
        if (hour >= 11 && hour <= 14) {
            recommendations.push({
                type: 'info',
                message: 'Pause déjeuner - Boulangeries très fréquentées'
            });
        }
        
        if (hour >= 22 || hour <= 6) {
            recommendations.push({
                type: 'info',
                message: 'Service de nuit - Fréquence réduite, planifiez vos trajets'
            });
        }
        
        if (isWeekend) {
            recommendations.push({
                type: 'success',
                message: 'Week-end - Trafic fluide, temps de trajet optimaux'
            });
        }
        
        return recommendations;
    }
    
    // 🎯 Générer données complètes du dashboard
    generateCompleteDashboardData() {
        const ratpData = this.generateRATPData();
        const travelData = this.generateTravelTimeData();
        const bakeryData = this.generateBakeryData();
        const pedestrianData = this.generatePedestrianData();
        
        return {
            timestamp: new Date().toISOString(),
            ratp: ratpData,
            travel_times: travelData,
            bakeries: bakeryData,
            pedestrians: pedestrianData,
            citymapper_metrics: {
                reliability_score: Math.max(70, 100 - (ratpData.perturbed_lines * 10)),
                user_satisfaction: Math.max(75, 100 - (travelData.average_delay * 2)),
                network_efficiency: Math.max(80, 100 - (pedestrianData.average_delay * 3)),
                bakery_accessibility: Math.max(85, 100 - (bakeryData.average_wait_time * 2))
            }
        };
    }
    
    // 🔄 Mettre à jour les données (simulation temps réel)
    updateData() {
        // Simuler des changements progressifs
        const changeProbability = 0.3; // 30% de chance de changement
        
        if (Math.random() < changeProbability) {
            // Changer le statut d'une ligne aléatoirement
            const randomLine = this.lines[Math.floor(Math.random() * this.lines.length)];
            randomLine.status = randomLine.status === 'normal' ? 'perturbed' : 'normal';
        }
        
        return this.generateCompleteDashboardData();
    }
}

// ============================================================================
// 🌐 EXPORT POUR UTILISATION GLOBALE
// ============================================================================

// Créer une instance globale
window.citymapperSimulator = new CitymapperDataSimulator();

// Fonction utilitaire pour obtenir des données fraîches
window.getCitymapperData = () => {
    return window.citymapperSimulator.generateCompleteDashboardData();
};

// Fonction pour mettre à jour les données
window.updateCitymapperData = () => {
    return window.citymapperSimulator.updateData();
};

console.log('🚇 CitymapperDataSimulator initialisé avec succès !');
console.log('📊 Données disponibles via getCitymapperData()');
console.log('🔄 Mise à jour via updateCitymapperData()');

