/**
 * 🚀 MODULE DÉCOUPLÉ POUR LA TRANSMISSION DES DONNÉES VERS LE DASHBOARD
 * 
 * Ce module est conçu pour éviter les conflits avec l'édition automatique
 * et assurer une transmission stable des données de la page d'accueil
 * vers le dashboard via sessionStorage.
 */

class DashboardTransmitter {
    
    /**
     * Transmet les données de route vers le dashboard
     * @param {Object} routeData - Données de l'itinéraire calculé
     * @returns {boolean} - Succès de la transmission
     */
    static transmitRouteData(routeData) {
        try {
            console.log('📤 DashboardTransmitter: Début de transmission des données...');
            
            // Structurer les données essentielles pour le dashboard
            const dashboardData = {
                timestamp: new Date().toISOString(),
                totalTime: routeData.eta || routeData.totalTime || 0,
                walkingTime: routeData.walkingTime || 0,
                metroTime: routeData.metroTime || 0,
                bakeryStopTime: routeData.bakeryStopTime || 0,
                bakeriesCount: routeData.bakeries ? routeData.bakeries.length : 0,
                line: routeData.line || 'N/A',
                departure: routeData.start_address || routeData.departure || routeData.start || 'N/A',
                arrival: routeData.end_address || routeData.arrival || routeData.end || 'N/A',
                optimized: routeData.optimized || false,
                
                // Données détaillées des boulangeries
                bakeries: routeData.bakeries ? routeData.bakeries.map(bakery => ({
                    name: bakery.name || 'Boulangerie',
                    distance: bakery.distance || 'Distance N/A',
                    rating: bakery.rating || 'N/A',
                    vicinity: bakery.vicinity || '',
                    is_artisan: bakery.is_artisan || false
                })) : [],
                
                // Métadonnées de la session
                sessionInfo: {
                    language: window.currentLanguage || 'fr',
                    userAgent: navigator.userAgent,
                    timestamp: Date.now()
                }
            };
            
            // Stockage dans localStorage pour transmission vers le dashboard (partage entre onglets)
            localStorage.setItem('dashboardRouteData', JSON.stringify(dashboardData));
            
            // Log de validation
            console.log('✅ DashboardTransmitter: Données transmises avec succès:', dashboardData);
            console.log('📊 DashboardTransmitter: Taille des données:', JSON.stringify(dashboardData).length, 'caractères');
            
            return true;
            
        } catch (error) {
            console.error('❌ DashboardTransmitter: Erreur lors de la transmission:', error);
            return false;
        }
    }
    
    /**
     * Récupère les dernières données de route stockées
     * @returns {Object} - Données de route ou objet vide
     */
    static getLastRouteData() {
        try {
            const storedData = localStorage.getItem('dashboardRouteData');
            if (storedData) {
                const data = JSON.parse(storedData);
                console.log('📥 DashboardTransmitter: Données récupérées:', data);
                return data;
            } else {
                console.log('⚠️ DashboardTransmitter: Aucune donnée trouvée dans localStorage');
                return {};
            }
        } catch (error) {
            console.error('❌ DashboardTransmitter: Erreur lors de la récupération:', error);
            return {};
        }
    }
    
    /**
     * Vérifie si des données sont disponibles pour le dashboard
     * @returns {boolean} - Données disponibles ou non
     */
    static hasData() {
        return localStorage.getItem('dashboardRouteData') !== null;
    }
    
    /**
     * Efface les données stockées (nettoyage)
     */
    static clearData() {
        try {
            localStorage.removeItem('dashboardRouteData');
            console.log('🗑️ DashboardTransmitter: Données effacées');
        } catch (error) {
            console.error('❌ DashboardTransmitter: Erreur lors de l\'effacement:', error);
        }
    }
    
    /**
     * Test de fonctionnement du module
     * @returns {boolean} - Test réussi ou non
     */
    static test() {
        try {
            const testData = {
                totalTime: 25,
                walkingTime: 8,
                metroTime: 12,
                bakeryStopTime: 5,
                bakeriesCount: 1,
                line: "14",
                departure: "Gare de Lyon",
                arrival: "Opéra",
                optimized: true,
                bakeries: [{
                    name: "Boulangerie Test",
                    distance: "5 min",
                    rating: 4.5,
                    vicinity: "Rue de la Paix",
                    is_artisan: true
                }]
            };
            
            // Test de transmission
            const transmissionSuccess = this.transmitRouteData(testData);
            
            // Test de récupération
            const retrievedData = this.getLastRouteData();
            const retrievalSuccess = Object.keys(retrievedData).length > 0;
            
            // 🚀 DÉSACTIVATION DE L'EFFACEMENT AUTOMATIQUE POUR PRÉSERVER LES DONNÉES
            // this.clearData(); // ← DÉSACTIVÉ pour préserver les données entre onglets
            
            const testSuccess = transmissionSuccess && retrievalSuccess;
            console.log(`🧪 DashboardTransmitter: Test ${testSuccess ? 'RÉUSSI' : 'ÉCHOUÉ'}`);
            
            return testSuccess;
            
        } catch (error) {
            console.error('❌ DashboardTransmitter: Erreur lors du test:', error);
            return false;
        }
    }
}

// Export pour utilisation dans d'autres modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = DashboardTransmitter;
}

// Test automatique si le module est chargé directement
if (typeof window !== 'undefined') {
    console.log('🚀 DashboardTransmitter: Module chargé et prêt');
    
    // Test automatique après 1 seconde
    // 🚀 DÉSACTIVATION DU TEST AUTOMATIQUE POUR PRÉSERVER LES DONNÉES RÉELLES
    // setTimeout(() => {
    //     console.log('🧪 DashboardTransmitter: Test automatique en cours...');
    //     DashboardTransmitter.test();
    // }, 1000);
}
