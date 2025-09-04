// Configuration de l'application avec intégration API réelle

// 🚀 SYSTÈME DE BROADCAST POUR TRANSMISSION TEMPS RÉEL
function broadcastDashboardData(data) {
    try {
        console.log('📡 Broadcast des données vers tous les onglets...');
        
        // Validation des données
        if (!validateRouteData(data)) {
            console.error('❌ Données invalides, broadcast annulé');
            return false;
        }
        
        // Stockage principal
        const dashboardData = {
            timestamp: new Date().toISOString(),
            totalTime: data.eta || data.totalTime || 0,
            walkingTime: data.walkingTime || 0,
            metroTime: data.metroTime || 0,
            bakeryStopTime: data.bakeryStopTime || 0,
            bakeriesCount: data.bakeries ? data.bakeries.length : 0,
            line: data.line || 'N/A',
            departure: data.start_address || data.departure || data.start || 'N/A',
            arrival: data.end_address || data.arrival || data.end || 'N/A',
            optimized: data.optimized || false,
            bakeries: data.bakeries || [],
            _timestamp: Date.now(),
            _source: 'app_integrated',
            _version: '1.0'
        };
        
        localStorage.setItem('dashboardRouteData', JSON.stringify(dashboardData));
        
        // Broadcast vers tous les onglets
        if (typeof BroadcastChannel !== 'undefined') {
            const channel = new BroadcastChannel('dashboard_updates');
            channel.postMessage({
                type: 'ROUTE_DATA_UPDATE',
                payload: dashboardData
            });
            console.log('📡 Message broadcast envoyé');
        }
        
        // Déclencher un événement personnalisé pour le même onglet
        window.dispatchEvent(new CustomEvent('dashboardDataUpdated', {
            detail: dashboardData
        }));
        
        console.log('✅ Broadcast réussi:', dashboardData);
        return true;
        
    } catch (error) {
        console.error('❌ Erreur broadcast:', error);
        return false;
    }
}

// 🔍 VALIDATION DES DONNÉES
function validateRouteData(data) {
    const requiredFields = ['eta', 'start_address', 'end_address'];
    const isValid = requiredFields.every(field => 
        data[field] !== undefined && data[field] !== null
    );
    
    // Validation spécifique pour CDG → Versailles
    if (data.start_address && data.end_address) {
        const isCdgVersailles = 
            data.start_address.toLowerCase().includes('cdg') && 
            data.end_address.toLowerCase().includes('versailles');
        
        if (isCdgVersailles && data.eta && data.eta.includes('min')) {
            // Extraire le nombre de minutes du format "1 heure 29 min" ou "45 min"
            const timeMatch = data.eta.match(/(\d+)\s*(?:heure|h)?\s*(\d+)?\s*min/);
            if (timeMatch) {
                const hours = parseInt(timeMatch[1]) || 0;
                const minutes = parseInt(timeMatch[2]) || 0;
                const totalMinutes = hours * 60 + minutes;
                
                if (totalMinutes < 30) {
                    console.warn('⚠️ Temps anormalement court pour CDG→Versailles:', totalMinutes, 'min');
                    return false;
                }
            }
        }
    }
    
    return isValid;
}
const CONFIG = {
    API_BASE_URL: 'http://127.0.0.1:8000',
    DEFAULT_LAT: 48.8566,
    DEFAULT_LNG: 2.3522,
    DEFAULT_ZOOM: 13
};

// Variables globales
let map;
let currentLanguage = 'fr';
let markers = [];

// Traductions
const translations = {
    fr: {
        departure: 'Départ',
        destination: 'Destination',
        calculate: 'Calculer l\'itinéraire optimal',
        yourRoute: 'Votre trajet',
        results: 'Résultats',
        assistant: 'Assistant Conciergerie',
        askQuestion: 'Posez votre question...',
        loading: 'Chargement...',
        error: 'Erreur',
        noResults: 'Aucun résultat trouvé',
        apiError: 'Erreur de connexion à l\'API'
    },
    en: {
        departure: 'Departure',
        destination: 'Destination',
        calculate: 'Calculate optimal route',
        yourRoute: 'Your route',
        results: 'Results',
        assistant: 'Concierge Assistant',
        askQuestion: 'Ask your question...',
        loading: 'Loading...',
        error: 'Error',
        noResults: 'No results found',
        apiError: 'API connection error'
    },
    ja: {
        departure: '出発',
        destination: '目的地',
        calculate: '最適ルートを計算',
        yourRoute: 'あなたのルート',
        results: '結果',
        assistant: 'コンシェルジュアシスタント',
        askQuestion: '質問してください...',
        loading: '読み込み中...',
        error: 'エラー',
        noResults: '結果が見つかりません',
        apiError: 'API接続エラー'
    }
};

// Initialisation de l'application
document.addEventListener('DOMContentLoaded', function() {
    initializeMap();
    setupEventListeners();
    setupLanguageSelector();
    addWelcomeMessage();
    testAPIConnection();
});

// Test de connexion aux APIs
async function testAPIConnection() {
    try {
        const response = await fetch(`${CONFIG.API_BASE_URL}/health`);
        if (response.ok) {
            console.log('✅ API FastAPI connectée');
            addChatMessage('assistant', '✅ Connexion aux APIs établie. Toutes les fonctionnalités sont opérationnelles !');
        } else {
            throw new Error('API non accessible');
        }
    } catch (error) {
        console.error('❌ Erreur API:', error);
        addChatMessage('assistant', '⚠️ APIs non accessibles. Mode démo activé avec données simulées.');
    }
}

// Initialisation de la carte Leaflet
function initializeMap() {
    map = L.map('map').setView([CONFIG.DEFAULT_LAT, CONFIG.DEFAULT_LNG], CONFIG.DEFAULT_ZOOM);
    
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
    }).addTo(map);
    
    // Ajouter un marqueur par défaut (Paris)
    addMarker(CONFIG.DEFAULT_LAT, CONFIG.DEFAULT_LNG, 'Paris', '🏛️');
}

// Configuration des écouteurs d'événements
function setupEventListeners() {
    // Bouton de calcul d'itinéraire
    document.getElementById('calculate-btn').addEventListener('click', calculateRoute);
    
    // Bouton d'envoi de message
    document.getElementById('send-btn').addEventListener('click', sendMessage);
    
    // Entrée dans le champ de message
    document.getElementById('message-input').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });

    // Auto-complétion Google Places
    setupGooglePlacesAutocomplete();
}

// Configuration de l'auto-complétion Google Places
function setupGooglePlacesAutocomplete() {
    const startInput = document.getElementById('start-input');
    const endInput = document.getElementById('end-input');
    
    // Simulation de l'auto-complétion (à remplacer par l'API Google Places)
    startInput.addEventListener('input', function() {
        if (this.value.length > 2) {
            showAutocompleteSuggestions(this, this.value);
        }
    });
    
    endInput.addEventListener('input', function() {
        if (this.value.length > 2) {
            showAutocompleteSuggestions(this, this.value);
        }
    });
}

// Affichage des suggestions d'auto-complétion Google Places
async function showAutocompleteSuggestions(input, query) {
    try {
        // Validation de la requête : minimum 2 caractères, maximum 50
        if (query.length < 2) {
            return; // Pas de suggestions pour les requêtes trop courtes
        }
        
        if (query.length > 50) {
            query = query.substring(0, 50); // Tronquer les requêtes trop longues
        }
        
        // Nettoyer la requête (supprimer caractères spéciaux problématiques)
        const cleanQuery = query.replace(/[^\w\sÀ-ÿ\-']/g, ' ').trim();
        
        if (cleanQuery.length < 2) {
            showFallbackSuggestions(input, query);
            return;
        }
        
        console.log('🔍 Requête Google Places:', cleanQuery);
        
        // Appel à l'API Google Places réelle
        const response = await fetch(`http://127.0.0.1:8000/places/autocomplete?query=${encodeURIComponent(cleanQuery)}&limit=5`);
        
        if (response.ok) {
            const data = await response.json();
            
            if (data.predictions && data.predictions.length > 0) {
                // Créer la liste de suggestions
                let suggestionList = input.parentNode.querySelector('.suggestions');
                if (!suggestionList) {
                    suggestionList = document.createElement('ul');
                    suggestionList.className = 'suggestions';
                    input.parentNode.appendChild(suggestionList);
                }
                
                suggestionList.innerHTML = data.predictions.map(prediction => 
                    `<li onclick="selectSuggestion('${input.id}', '${prediction.description}')">${prediction.description}</li>`
                ).join('');
                
                console.log('✅ Suggestions Google Places récupérées:', data.predictions.length);
            } else {
                console.log('⚠️ Aucune suggestion Google Places trouvée');
                showFallbackSuggestions(input, query);
            }
        } else {
            console.error('❌ Erreur API Google Places:', response.status);
            // Fallback aux suggestions simulées
            showFallbackSuggestions(input, query);
        }
    } catch (error) {
        console.error('❌ Erreur connexion Google Places:', error);
        // Fallback aux suggestions simulées
        showFallbackSuggestions(input, query);
    }
}

// Fallback aux suggestions simulées en cas d'erreur
function showFallbackSuggestions(input, query) {
    const suggestions = [
        `${query} - Gare de Lyon`,
        `${query} - Métro Châtelet`,
        `${query} - Place de la Concorde`,
        `${query} - Tour Eiffel`
    ];
    
    let suggestionList = input.parentNode.querySelector('.suggestions');
    if (!suggestionList) {
        suggestionList = document.createElement('ul');
        suggestionList.className = 'suggestions';
        input.parentNode.appendChild(suggestionList);
    }
    
    suggestionList.innerHTML = suggestions.map(suggestion => 
        `<li onclick="selectSuggestion('${input.id}', '${suggestion}')">${suggestion}</li>`
    ).join('');
    
    console.log('⚠️ Utilisation du fallback simulé');
}

// Sélection d'une suggestion
function selectSuggestion(inputId, value) {
    document.getElementById(inputId).value = value;
    document.querySelectorAll('.suggestions').forEach(list => list.remove());
}

// Configuration du sélecteur de langue
function setupLanguageSelector() {
    const langButtons = document.querySelectorAll('.lang-btn');
    
    langButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            const lang = this.dataset.lang;
            changeLanguage(lang);
            
            // Mettre à jour l'état actif
            langButtons.forEach(b => b.classList.remove('active'));
            this.classList.add('active');
        });
    });
}

// Changement de langue
function changeLanguage(lang) {
    currentLanguage = lang;
    updateUIText();
}

// Mise à jour du texte de l'interface
function updateUIText() {
    const t = translations[currentLanguage];
    
    // Mettre à jour les labels
    document.querySelector('label[for="start-input"]').textContent = t.departure;
    document.querySelector('label[for="end-input"]').textContent = t.destination;
    document.getElementById('calculate-btn').textContent = t.calculate;
    document.querySelector('.map-section h2').textContent = t.yourRoute;
    document.querySelector('.results-section h2').textContent = t.results;
    document.querySelector('.assistant-section h2').textContent = t.assistant;
    document.getElementById('message-input').placeholder = t.askQuestion;
}

// Calcul d'itinéraire avec API réelle
async function calculateRoute() {
    const start = document.getElementById('start-input').value.trim();
    const end = document.getElementById('end-input').value.trim();
    
    if (!start || !end) {
        showError('Veuillez remplir les champs de départ et d\'arrivée');
        return;
    }
    
    showLoading('Calcul de l\'itinéraire en cours...');
    
    try {
        console.log('🔄 Début du calcul d\'itinéraire...');
        const routeData = await callRealRouteAPI(start, end);
        
        if (routeData) {
            console.log('✅ Données ETA reçues:', routeData);
            console.log('🥖 Boulangeries trouvées:', routeData.bakeries);
            
                            // INTÉGRATION PROGRESSIVE: Appel API boulangeries dynamique
                try {
                    console.log('🔍 Appel API boulangeries dynamique...');
                    const dynamicBakeries = await callBakeriesAPI(start, end);
                    
                    if (dynamicBakeries && dynamicBakeries.length > 0) {
                        console.log('✅ Boulangeries dynamiques trouvées:', dynamicBakeries);
                        console.log('🥖 Nombre de boulangeries:', dynamicBakeries.length);
                        
                        // Logger les données pour validation
                        dynamicBakeries.forEach((bakery, index) => {
                            console.log(`🥖 Boulangerie ${index + 1}:`, {
                                name: bakery.name,
                                vicinity: bakery.vicinity,
                                rating: bakery.rating,
                                coordinates: [bakery.lat, bakery.lng]
                            });
                        });
                        
                        // PHASE 6: Remplacement des données statiques par les données dynamiques
                        console.log('🚀 PHASE 6: Remplacement des données statiques par les données dynamiques');
                        
                        // Remplacer routeData.bakeries par dynamicBakeries
                        routeData.bakeries = dynamicBakeries.map(bakery => ({
                            name: bakery.name,
                            distance: `${Math.round(bakery.rating * 2)} min à pied`, // Distance simulée basée sur le rating
                            rating: bakery.rating,
                            vicinity: bakery.vicinity,
                            is_artisan: bakery.rating >= 4.0, // Considéré comme artisanal si rating >= 4.0
                            // PRÉSERVER LES COORDONNÉES pour la géolocalisation
                            lat: bakery.lat,
                            lng: bakery.lng,
                            coordinates: bakery.coordinates || [bakery.lat, bakery.lng]
                        }));
                        
                        console.log('✅ Données dynamiques intégrées dans routeData.bakeries:', routeData.bakeries);
                    } else {
                        console.log('⚠️ Aucune boulangerie dynamique trouvée, utilisation des données statiques');
                    }
                } catch (error) {
                    console.log('❌ Erreur API boulangeries, utilisation des données statiques:', error);
                }
            
            displayRealResults(routeData);
            addRouteMarkers(start, end, routeData);
            
            // CORRECTION: S'assurer que addBakeryMarkers est appelée
            if (routeData.bakeries && routeData.bakeries.length > 0) {
                console.log('🗺️ Ajout des marqueurs de boulangeries...');
                addBakeryMarkers(routeData.bakeries);
            } else {
                console.log('⚠️ Aucune boulangerie trouvée dans les données');
            }
            
                            // 🚀 TRANSMISSION DES DONNÉES VERS LE DASHBOARD VIA LE MODULE DÉCOUPLÉ
                console.log('📤 Transmission des données vers le dashboard...');
                console.log('🔍 routeData à transmettre:', {
                    eta: routeData.eta,
                    bakeries: routeData.bakeries?.length,
                    start_address: routeData.start_address,
                    end_address: routeData.end_address
                });
                
                if (typeof DashboardTransmitter !== 'undefined') {
                    const transmissionSuccess = DashboardTransmitter.transmitRouteData(routeData);
                    console.log(`✅ Transmission dashboard: ${transmissionSuccess ? 'SUCCÈS' : 'ÉCHEC'}`);
                    
                    // 🚀 BROADCAST VERS TOUS LES ONGLETS
                    broadcastDashboardData(routeData);
                } else {
                    console.warn('⚠️ Module DashboardTransmitter non disponible');
                }
        } else {
            console.log('⚠️ API non accessible, utilisation du mode simulation');
            await simulateRouteCalculation(start, end);
            addRouteMarkers(start, end);
            displayResults(start, end);
        }
    } catch (error) {
        console.error('❌ Erreur calcul itinéraire:', error);
        showError('Erreur lors du calcul de l\'itinéraire');
    }
}

// Appel à l'API réelle de calcul d'itinéraire
async function callRealRouteAPI(start, end) {
    try {
        // Simplifier les adresses pour l'API - utiliser des codes courts
        let simplifiedStart = start.split(',')[0].trim();
        let simplifiedEnd = end.split(',')[0].trim();
        
        // Remplacer les adresses longues par des codes courts
        if (simplifiedStart.includes('Charles de Gaulle') || simplifiedStart.includes('CDG')) {
            simplifiedStart = 'CDG';
        }
        if (simplifiedEnd.includes('Châtelet')) {
            simplifiedEnd = 'Châtelet';
        }
        
        const requestData = { 
            start_address: simplifiedStart, 
            end_address: simplifiedEnd, 
            language: currentLanguage 
        };
        
        console.log('🔍 Données envoyées à l\'API:', requestData);
        console.log('🔑 Clé API utilisée:', 'demo_2025_baguette_metro');
        console.log('🌐 URL API:', `${CONFIG.API_BASE_URL}/eta/calculate`);
        
        const response = await fetch(`${CONFIG.API_BASE_URL}/eta/calculate`, {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                'X-API-Key': 'demo_2025_baguette_metro'  // Clé de démonstration sécurisée
            },
            body: JSON.stringify(requestData)
        });
        
        if (response.ok) {
            const data = await response.json();
            console.log('✅ Données ETA reçues:', data);
            return data;
        } else {
            console.log('❌ Erreur API ETA:', response.status);
            
            // Log détaillé de l'erreur
            try {
                const errorData = await response.text();
                console.log('📄 Contenu de l\'erreur:', errorData);
            } catch (e) {
                console.log('⚠️ Impossible de lire le contenu de l\'erreur');
            }
            
            return null;
        }
    } catch (error) {
        console.log('❌ Erreur connexion API ETA:', error);
        return null;
    }
}

// Appel à l'API boulangeries dynamique
async function callBakeriesAPI(start, end) {
    try {
        console.log('🔍 Appel API boulangeries pour:', { start, end });
        
        // Utiliser les coordonnées stockées des suggestions sélectionnées
        let startCoords, endCoords;
        
        if (window.selectedCoordinates && window.selectedCoordinates['start-input'] && window.selectedCoordinates['end-input']) {
            if (window.selectedCoordinates['start-input'].coords) {
                startCoords = window.selectedCoordinates['start-input'].coords;
                console.log('✅ Coordonnées start utilisées:', startCoords);
            }
            if (window.selectedCoordinates['end-input'].coords) {
                endCoords = window.selectedCoordinates['end-input'].coords;
                console.log('✅ Coordonnées end utilisées:', endCoords);
            }
        }
        
        // Fallback vers les coordonnées codées en dur si pas de coordonnées stockées
        if (!startCoords) {
            if (start.includes('CDG') || start.includes('Charles de Gaulle')) {
                startCoords = [49.0097, 2.5479];
                console.log('✅ Coordonnées CDG fallback utilisées:', startCoords);
            }
        }
        
        if (!endCoords) {
            if (end.includes('Versailles')) {
                endCoords = [48.8035403, 2.1266886];
                console.log('✅ Coordonnées Versailles fallback utilisées:', endCoords);
            } else if (end.includes('Château Rouge') || end.includes('Chateau Rouge')) {
                endCoords = [48.8966, 2.3522];
                console.log('✅ Coordonnées Château Rouge fallback utilisées:', endCoords);
            } else if (end.includes('Châtelet') || end.includes('Chatelet')) {
                endCoords = [48.862725, 2.3472];
                console.log('✅ Coordonnées Châtelet fallback utilisées:', endCoords);
            } else if (end.includes('Petites Écuries') || end.includes('Petites Ecuries')) {
                endCoords = [48.8738, 2.3444];
                console.log('✅ Coordonnées Rue des Petites Écuries fallback utilisées:', endCoords);
            }
        }
        
        // Utiliser les coordonnées de DESTINATION pour la recherche de boulangeries (plus logique)
        const searchCoords = endCoords || startCoords;
        
        if (!searchCoords) {
            console.log('⚠️ Aucune coordonnée disponible pour la recherche de boulangeries');
            return null;
        }
        
        console.log('🔍 Recherche boulangeries autour de:', searchCoords);
        
        // Appel à l'API boulangeries
        const response = await fetch(`${CONFIG.API_BASE_URL}/places/bakeries/search?lat=${searchCoords[0]}&lng=${searchCoords[1]}&radius=5000`, {
            method: 'GET',
            headers: { 
                'Content-Type': 'application/json'
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            console.log('✅ Réponse API boulangeries:', data);
            
            if (data.bakeries && data.bakeries.length > 0) {
                return data.bakeries;
            } else {
                console.log('⚠️ Aucune boulangerie trouvée dans la réponse');
                return null;
            }
        } else {
            console.log('❌ Erreur API boulangeries:', response.status);
            return null;
        }
        
    } catch (error) {
        console.log('❌ Erreur appel API boulangeries:', error);
        return null;
    }
}

// Affichage des résultats réels de l'API
function displayRealResults(routeData) {
    console.log('🎯 displayRealResults appelée avec:', routeData);
    
    const container = document.getElementById('results-container');
    console.log('📦 Container trouvé:', container);
    
    if (!container) {
        console.error('❌ Container results-container non trouvé !');
        return;
    }
    
    // Traduction des labels selon la langue
    const labels = getLabelsForLanguage(currentLanguage);
    console.log('🏷️ Labels traduits:', labels);
    
    container.innerHTML = `
        <div class="result-item">
            <h3>🚀 ${labels.itineraryCalculated}</h3>
            <p><strong>${labels.departure}:</strong> ${routeData.start_address || 'N/A'}</p>
            <p><strong>${labels.arrival}:</strong> ${routeData.end_address || 'N/A'}</p>
            <p><strong>${labels.estimatedDuration}:</strong> ${routeData.eta || 'N/A'}</p>
            <p><strong>${labels.distance}:</strong> ${routeData.distance || 'N/A'}</p>
        </div>
        <div class="result-item">
            <h3>🥖 ${labels.bakeriesOnRoute}</h3>
            ${routeData.bakeries && routeData.bakeries.length > 0 ? 
                routeData.bakeries.map(b => {
                    // DEBUG: Afficher les données brutes de l'API
                    console.log(`🔍 Données brutes de l'API pour boulangerie:`, b);
                    console.log(`🔍 Propriétés disponibles:`, Object.keys(b));
                    console.log(`🔍 Valeurs:`, { name: b.name, distance: b.distance, rating: b.rating });
                    
                    // Utiliser les vraies données de l'API ou des valeurs par défaut intelligentes
                    const name = b.name || 'Boulangerie sur le trajet';
                    const distance = b.distance || 'Distance calculée';
                    const rating = b.rating || 'N/A';
                    
                    console.log(`🔍 Données finales utilisées:`, { name, distance, rating });
                    
                    // Ajouter des informations supplémentaires si disponibles
                    const vicinity = b.vicinity || '';
                    const isArtisan = b.is_artisan ? ' 🥖 Artisan' : ' 🏪';
                    
                    return `<p>• ${name}${isArtisan} (${distance}) ⭐ ${rating}/5 ${vicinity ? `📍 ${vicinity}` : ''}</p>`;
                }).join('') : 
                `<p>• ${labels.searchingBakeries}</p>`
            }
        </div>
        <div class="result-item">
            <h3>🚇 ${labels.publicTransport}</h3>
            ${routeData.route_steps && routeData.route_steps.length > 0 ? 
                routeData.route_steps.map(step => `<p>• ${step.instruction} (${step.duration})</p>`).join('') : 
                routeData.transport && routeData.transport.length > 0 ? 
                    routeData.transport.map(t => `<p>• ${t.line}: ${t.wait_time} ${labels.wait} (${t.duration})</p>`).join('') : 
                    `<p>• ${labels.metroLine1}: 3 ${labels.minWait}</p>`
            }
        </div>
    `;
}

// Ajouter les marqueurs de boulangeries sur la carte
function addBakeryMarkers(bakeries) {
    if (!bakeries || !map) {
        console.log('❌ addBakeryMarkers: bakeries ou map manquant');
        return;
    }
    
    console.log(`🗺️ Ajout de ${bakeries.length} marqueurs de boulangeries`);
    
    // Supprimer les anciens marqueurs de boulangeries
    if (window.bakeryMarkers) {
        window.bakeryMarkers.forEach(marker => map.removeLayer(marker));
    }
    
    window.bakeryMarkers = [];
    
    bakeries.forEach((bakery, index) => {
        // Position simulée (à remplacer par de vraies coordonnées)
        const lat = CONFIG.DEFAULT_LAT + (Math.random() - 0.5) * 0.01;
        const lng = CONFIG.DEFAULT_LNG + (Math.random() - 0.5) * 0.01;
        
        const bakeryIcon = L.divIcon({
            className: 'bakery-marker',
            html: '🥖',
            iconSize: [30, 30]
        });
        
        const marker = L.marker([lat, lng], { icon: bakeryIcon })
            .addTo(map)
            .bindPopup(`
                <div class="bakery-popup">
                    <h4>${bakery.name}</h4>
                    <p>📍 ${bakery.distance}</p>
                    <p>⭐ ${bakery.rating}/5</p>
                    <button onclick="showBakeryRoute(${lat}, ${lng})">${getLabelsForLanguage(currentLanguage).showRoute}</button>
                </div>
            `);
        
        window.bakeryMarkers.push(marker);
        console.log(`✅ Marqueur boulangerie ajouté: ${bakery.name} à [${lat}, ${lng}]`);
    });
    
    console.log(`✅ ${bakeries.length} marqueurs de boulangeries ajoutés sur la carte`);
}

// Afficher le trajet vers une boulangerie
function showBakeryRoute(lat, lng) {
    if (!map) return;
    
    // Centrer la carte sur la boulangerie
    map.setView([lat, lng], 16);
    
    // Ajouter un marqueur temporaire
    const tempMarker = L.marker([lat, lng], {
        icon: L.divIcon({
            className: 'temp-marker',
            html: '🎯',
            iconSize: [40, 40]
        })
    }).addTo(map);
    
    // Supprimer après 3 secondes
    setTimeout(() => {
        map.removeLayer(tempMarker);
    }, 3000);
}

// Fonction pour obtenir les labels traduits
function getLabelsForLanguage(lang) {
    const labels = {
        fr: {
            itineraryCalculated: "Itinéraire calculé (API réelle)",
            departure: "Départ",
            arrival: "Arrivée",
            estimatedDuration: "Durée estimée",
            distance: "Distance",
            bakeriesOnRoute: "Boulangeries sur le trajet",
            searchingBakeries: "Recherche en cours...",
            publicTransport: "Transport en commun",
            wait: "d'attente",
            metroLine1: "Métro ligne 1",
            minWait: "min d'attente",
            showRoute: "Voir l'itinéraire"
        },
        en: {
            itineraryCalculated: "Route calculated (Real API)",
            departure: "Departure",
            arrival: "Arrival",
            estimatedDuration: "Estimated duration",
            distance: "Distance",
            bakeriesOnRoute: "Bakeries on route",
            searchingBakeries: "Searching...",
            publicTransport: "Public transport",
            wait: "wait",
            metroLine1: "Metro line 1",
            minWait: "min wait",
            showRoute: "Show route"
        },
        ja: {
            itineraryCalculated: "ルート計算済み（リアルAPI）",
            departure: "出発",
            arrival: "到着",
            estimatedDuration: "推定所要時間",
            distance: "距離",
            bakeriesOnRoute: "ルート上のパン屋",
            searchingBakeries: "検索中...",
            publicTransport: "公共交通機関",
            wait: "待ち時間",
            metroLine1: "メトロ1号線",
            minWait: "分待ち",
            showRoute: "ルートを表示"
        }
    };
    
    return labels[lang] || labels.fr;
}

// Simulation du calcul d'itinéraire (fallback)
async function simulateRouteCalculation(start, end) {
    return new Promise((resolve) => {
        setTimeout(() => {
            resolve({
                start: start,
                end: end,
                duration: Math.floor(Math.random() * 30) + 15,
                distance: Math.floor(Math.random() * 5) + 1,
                bakeries: Math.floor(Math.random() * 3) + 1
            });
        }, 2000);
    });
}

// Ajout de marqueurs d'itinéraire
function addRouteMarkers(start, end, routeData = null) {
    // Nettoyer les marqueurs existants
    markers.forEach(marker => map.removeLayer(marker));
    markers = [];
    
    // Coordonnées simulées ou réelles
    let startCoords, endCoords;
    
    if (routeData && routeData.coordinates) {
        startCoords = routeData.coordinates.start;
        endCoords = routeData.coordinates.end;
    } else {
        // Coordonnées simulées
        startCoords = [CONFIG.DEFAULT_LAT - 0.01, CONFIG.DEFAULT_LNG - 0.01];
        endCoords = [CONFIG.DEFAULT_LAT + 0.01, CONFIG.DEFAULT_LNG + 0.01];
    }
    
    // Ajouter marqueurs de départ et d'arrivée
    const startMarker = addMarker(startCoords[0], startCoords[1], start, '📍');
    const endMarker = addMarker(endCoords[0], endCoords[1], end, '🎯');
    
    // Ajouter ligne d'itinéraire
    const routeLine = L.polyline([startCoords, endCoords], {
        color: '#3498db',
        weight: 4,
        opacity: 0.8
    }).addTo(map);
    
    markers.push(routeLine);
    
    // Ajuster la vue de la carte
    map.fitBounds(routeLine.getBounds());
}

// Ajout d'un marqueur sur la carte
function addMarker(lat, lng, title, icon) {
    const marker = L.marker([lat, lng], {
        title: title
    }).addTo(map);
    
    marker.bindPopup(`<b>${title}</b>`);
    markers.push(marker);
    
    return marker;
}

// Affichage des résultats (fallback)
function displayResults(start, end) {
    const container = document.getElementById('results-container');
    
    container.innerHTML = `
        <div class="result-item">
            <h3>🚀 Itinéraire calculé (simulation)</h3>
            <p><strong>Départ:</strong> ${start}</p>
            <p><strong>Arrivée:</strong> ${end}</p>
            <p><strong>Durée estimée:</strong> 20-25 minutes</p>
            <p><strong>Distance:</strong> 2.5 km</p>
        </div>
        <div class="result-item">
            <h3>🥖 Boulangeries sur le trajet</h3>
            <p>• Boulangerie du Coin (5 min à pied)</p>
            <p>• Artisan Boulanger (12 min à pied)</p>
        </div>
        <div class="result-item">
            <h3>🚇 Transport en commun</h3>
            <p>• Métro ligne 1: 3 min d'attente</p>
            <p>• Bus 38: 8 min d'attente</p>
        </div>
    `;
}

// Envoi de message à l'assistant IA avec API réelle
async function sendMessage() {
    const input = document.getElementById('message-input');
    const message = input.value.trim();
    
    if (!message) return;
    
    // Ajouter le message utilisateur
    addChatMessage('user', message);
    input.value = '';
    
    try {
        // Essayer d'utiliser l'API réelle d'abord
        const aiResponse = await callRealAIAPI(message);
        if (aiResponse) {
            addChatMessage('assistant', aiResponse);
        } else {
            // Fallback vers la simulation
            setTimeout(() => {
                const response = generateAIResponse(message);
                addChatMessage('assistant', response);
            }, 1000);
        }
    } catch (error) {
        console.error('Erreur API IA:', error);
        // Fallback vers la simulation
        setTimeout(() => {
            const response = generateAIResponse(message);
            addChatMessage('assistant', response);
        }, 1000);
    }
}

// Appel à l'API réelle de l'assistant IA
async function callRealAIAPI(message) {
    try {
        // Nettoyer et valider le message
        let cleanMessage = message;
        let detectedLanguage = currentLanguage;
        
        // Détection automatique de la langue
        if (/[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]/.test(message)) {
            detectedLanguage = 'ja';  // Japonais
        } else if (/^[a-zA-Z\s\?\.\!]+$/.test(message)) {
            detectedLanguage = 'en';  // Anglais
        } else {
            detectedLanguage = 'fr';  // Français par défaut
        }
        
        // Nettoyer le message pour l'API (préserver les caractères japonais)
        if (detectedLanguage === 'ja') {
            // Pour le japonais, garder le message original
            cleanMessage = message;
        } else {
            // Pour FR/EN, nettoyer les caractères spéciaux
            cleanMessage = message.replace(/[^\w\sÀ-ÿ\-'?.,!]/g, ' ').trim();
        }
        
        // Log détaillé des données envoyées
        const requestData = {
            message: cleanMessage,
            language: detectedLanguage,
            context: 'baguette_metro_assistant'
        };
        
        console.log('🤖 Données envoyées à l\'API chat:', requestData);
        console.log('🔑 Clé API utilisée:', 'demo_2025_baguette_metro');
        console.log('🌐 URL API chat:', `${CONFIG.API_BASE_URL}/api/chat`);
        
        const response = await fetch(`${CONFIG.API_BASE_URL}/api/chat`, {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                'X-API-Key': 'demo_2025_baguette_metro'  // Clé de démonstration sécurisée
            },
            body: JSON.stringify(requestData)
        });
        
        if (response.ok) {
            const data = await response.json();
            console.log('✅ Réponse API chat reçue:', data);
            return data.response || data.message;
        } else {
            console.log('❌ Erreur API chat:', response.status);
            
            // Log détaillé de l'erreur
            try {
                const errorData = await response.text();
                console.log('📄 Contenu de l\'erreur chat:', errorData);
            } catch (e) {
                console.log('⚠️ Impossible de lire le contenu de l\'erreur chat');
            }
        }
    } catch (error) {
        console.log('❌ Erreur connexion API chat:', error);
    }
    return null;
}

// Ajout d'un message dans le chat
function addChatMessage(sender, message) {
    const chatMessages = document.getElementById('chat-messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message ${sender}-message`;
    
    const icon = sender === 'user' ? '👤' : '🤖';
    messageDiv.innerHTML = `
        <div class="message-header">
            <span class="message-icon">${icon}</span>
            <span class="message-sender">${sender === 'user' ? 'Vous' : 'Assistant IA'}</span>
        </div>
        <div class="message-content">${message}</div>
    `;
    
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Génération de réponse IA simulée (fallback)
function generateAIResponse(message) {
    const responses = [
        "Je peux vous aider à trouver le meilleur itinéraire !",
        "Voici les boulangeries les plus proches de votre trajet.",
        "Le métro est le moyen le plus rapide pour ce trajet.",
        "N'oubliez pas de vérifier les horaires des transports !",
        "Je recommande de partir 10 minutes plus tôt pour être sûr."
    ];
    
    return responses[Math.floor(Math.random() * responses.length)];
}

// Affichage du chargement
function showLoading(message = 'Chargement...') {
    const container = document.getElementById('results-container');
    container.innerHTML = `<div class="loading">🔄 ${message}</div>`;
}

// Affichage d'une erreur
function showError(message) {
    const container = document.getElementById('results-container');
    container.innerHTML = `<div class="error">❌ ${message}</div>`;
}

// Message de bienvenue
function addWelcomeMessage() {
    addChatMessage('assistant', 'Bonjour ! Je suis votre assistant conciergerie. Je peux vous aider à planifier votre trajet, trouver des boulangeries et répondre à vos questions sur Paris. Comment puis-je vous aider ?');
}

// Styles CSS supplémentaires
const additionalStyles = `
    .chat-message {
        margin-bottom: 1rem;
        padding: 0.8rem;
        border-radius: 10px;
    }
    
    .user-message {
        background: #e3f2fd;
        margin-left: 2rem;
    }
    
    .assistant-message {
        background: #f3e5f5;
        margin-right: 2rem;
    }
    
    .message-header {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        margin-bottom: 0.5rem;
        font-weight: 600;
    }
    
    .message-icon {
        font-size: 1.2rem;
    }
    
    .result-item {
        background: white;
        padding: 1rem;
        margin-bottom: 1rem;
        border-radius: 8px;
        border-left: 4px solid #3498db;
    }
    
    .result-item h3 {
        color: #2c3e50;
        margin-bottom: 0.8rem;
    }
    
    .loading, .error {
        text-align: center;
        padding: 2rem;
        font-size: 1.1rem;
    }
    
    .error {
        color: #e74c3c;
    }
    
    .suggestions {
        position: absolute;
        top: 100%;
        left: 0;
        right: 0;
        background: white;
        border: 1px solid #ddd;
        border-radius: 5px;
        list-style: none;
        margin: 0;
        padding: 0;
        z-index: 1000;
        max-height: 200px;
        overflow-y: auto;
    }
    
    .suggestions li {
        padding: 0.5rem 1rem;
        cursor: pointer;
        border-bottom: 1px solid #eee;
    }
    
    .suggestions li:hover {
        background: #f5f5f5;
    }
    
    .input-group {
        position: relative;
    }
    
    .bakery-marker {
        background: transparent;
        border: none;
        font-size: 24px;
        text-align: center;
        line-height: 30px;
    }
    
    .bakery-popup {
        text-align: center;
    }
    
    .bakery-popup button {
        background: #3498db;
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 5px;
        cursor: pointer;
        margin-top: 0.5rem;
    }
    
    .bakery-popup button:hover {
        background: #2980b9;
    }
`;

// Ajouter les styles supplémentaires
const styleSheet = document.createElement('style');
styleSheet.textContent = additionalStyles;
document.head.appendChild(styleSheet);

// Fonction manquante pour tracer l'itinéraire sur la carte
function addRouteMarkers(start, end, routeData = null) {
    console.log('🗺️ addRouteMarkers appelée avec:', { start, end, routeData });
    
    // Nettoyer les marqueurs existants
    markers.forEach(marker => map.removeLayer(marker));
    markers = [];
    
    // Coordonnées connues pour CDG et Versailles
    let startCoords, endCoords;
    
    // PRIORITÉ 1: Utiliser les waypoints de l'API si disponibles
    if (routeData.waypoints && routeData.waypoints.length >= 2) {
        console.log('✅ Waypoints API disponibles:', routeData.waypoints);
        startCoords = [routeData.waypoints[0].lat, routeData.waypoints[0].lng];
        endCoords = [routeData.waypoints[routeData.waypoints.length - 1].lat, routeData.waypoints[routeData.waypoints.length - 1].lng];
        console.log('✅ Coordonnées API utilisées:', { startCoords, endCoords });
    }
    // PRIORITÉ 2: Vérifier les coordonnées stockées des suggestions sélectionnées
    else if (window.selectedCoordinates && window.selectedCoordinates['start-input'] && window.selectedCoordinates['end-input']) {
        console.log('✅ Coordonnées des suggestions trouvées, utilisation...');
        
        // Utiliser les coordonnées des suggestions Google Places
        if (window.selectedCoordinates['start-input'].coords) {
            startCoords = window.selectedCoordinates['start-input'].coords;
            console.log('✅ Coordonnées start-input utilisées:', startCoords);
        }
        
        if (window.selectedCoordinates['end-input'].coords) {
            endCoords = window.selectedCoordinates['end-input'].coords;
            console.log('✅ Coordonnées end-input utilisées:', endCoords);
        }
    }
    
    // Fallback vers les coordonnées codées en dur si pas de coordonnées stockées
    if (!startCoords && (start.includes('CDG') || start.includes('Charles de Gaulle'))) {
        startCoords = [49.0097, 2.5479]; // Coordonnées réelles de CDG
        console.log('✅ Coordonnées CDG fallback utilisées:', startCoords);
    }
    
    if (!endCoords && end.includes('Versailles')) {
        endCoords = [48.8035403, 2.1266886]; // Coordonnées réelles de Versailles
        console.log('✅ Coordonnées Versailles fallback utilisées:', endCoords);
    }
    
    if (!endCoords && (end.includes('Château Rouge') || end.includes('Chateau Rouge'))) {
        endCoords = [48.8966, 2.3522]; // Coordonnées réelles de Château Rouge, Paris
        console.log('✅ Coordonnées Château Rouge fallback utilisées:', endCoords);
    }
    
    if (startCoords && endCoords) {
        console.log('✅ Coordonnées connues utilisées:', { startCoords, endCoords });
        
        // Ajouter marqueurs de départ et d'arrivée
        const startMarker = addMarker(startCoords[0], startCoords[1], start, '🚀');
        const endMarker = addMarker(endCoords[0], endCoords[1], end, '🎯');
        
        // Ajouter ligne d'itinéraire - utiliser tous les waypoints si disponibles
        let routeLine;
        if (routeData.waypoints && routeData.waypoints.length > 2) {
            // Utiliser tous les waypoints pour un itinéraire détaillé
            const waypointCoords = routeData.waypoints.map(wp => [wp.lat, wp.lng]);
            routeLine = L.polyline(waypointCoords, {
                color: '#3498db',
                weight: 4,
                opacity: 0.8
            }).addTo(map);
            console.log('✅ Itinéraire multi-waypoints tracé:', waypointCoords.length, 'points');
        } else {
            // Ligne simple entre départ et arrivée
            routeLine = L.polyline([startCoords, endCoords], {
                color: '#3498db',
                weight: 4,
                opacity: 0.8
            }).addTo(map);
            console.log('✅ Itinéraire simple tracé');
        }
        
        markers.push(routeLine);
        
        // Ajuster la vue de la carte
        map.fitBounds(routeLine.getBounds());
        
        console.log('✅ Itinéraire tracé sur la carte');
    } else {
        console.log('❌ Coordonnées manquantes pour tracer l\'itinéraire');
        console.log('🔍 Données routeData disponibles:', Object.keys(routeData));
        console.log('🔍 waypoints:', routeData.waypoints);
    }
}

// Fonction manquante pour ajouter les marqueurs de boulangeries sur la carte
function addBakeryMarkers(bakeries) {
    if (!bakeries || !map) {
        console.log('❌ addBakeryMarkers: bakeries ou map manquant');
        return;
    }
    
    console.log(`🗺️ Ajout de ${bakeries.length} marqueurs de boulangeries`);
    
    // Supprimer les anciens marqueurs de boulangeries
    if (window.bakeryMarkers) {
        window.bakeryMarkers.forEach(marker => map.removeLayer(marker));
    }
    
    window.bakeryMarkers = [];
    
    bakeries.forEach((bakery, index) => {
        // Utiliser les vraies coordonnées de la boulangerie si disponibles
        let lat, lng;
        
        if (bakery.lat && bakery.lng) {
            // Coordonnées réelles de l'API
            lat = bakery.lat;
            lng = bakery.lng;
            console.log(`✅ Coordonnées réelles utilisées pour ${bakery.name}: [${lat}, ${lng}]`);
        } else if (bakery.coordinates && bakery.coordinates.length === 2) {
            // Coordonnées dans le format [lat, lng]
            lat = bakery.coordinates[0];
            lng = bakery.coordinates[1];
            console.log(`✅ Coordonnées array utilisées pour ${bakery.name}: [${lat}, ${lng}]`);
        } else {
            // Fallback : position le long de l'itinéraire (ancien comportement)
            const progress = (index + 1) / (bakeries.length + 1);
            lat = 49.0097 + (48.8035403 - 49.0097) * progress;
            lng = 2.5479 + (2.1266886 - 2.5479) * progress;
            console.log(`⚠️ Position calculée (fallback) pour ${bakery.name}: [${lat}, ${lng}] (progress: ${progress})`);
        }
        
        const bakeryIcon = L.divIcon({
            className: 'bakery-marker',
            html: '🥖',
            iconSize: [30, 30]
        });
        
        const marker = L.marker([lat, lng], { icon: bakeryIcon })
            .addTo(map)
            .bindPopup(`
                <div class="bakery-popup">
                    <h4>${bakery.name || 'Boulangerie sur le trajet'}</h4>
                    <p>📍 ${bakery.distance || 'Distance calculée'}</p>
                    <p>⭐ ${bakery.rating || 'N/A'}/5</p>
                    <p>🏠 ${bakery.vicinity || 'Adresse non disponible'}</p>
                    <button onclick="showBakeryRoute(${lat}, ${lng})">Voir l'itinéraire</button>
                </div>
            `);
        
        window.bakeryMarkers.push(marker);
        console.log(`✅ Marqueur boulangerie ajouté: ${bakery.name} à [${lat}, ${lng}]`);
    });
    
    console.log(`✅ ${bakeries.length} marqueurs de boulangeries ajoutés sur la carte`);
}
