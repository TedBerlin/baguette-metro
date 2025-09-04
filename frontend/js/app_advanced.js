/**
 * Application JavaScript Avancée - Baguette & Métro
 * Interface Enterprise avec carte interactive et données temps réel
 */

class BaguetteMetroApp {
    constructor() {
        this.map = null;
        this.currentLanguage = 'fr';
        this.markers = [];
        this.routePolyline = null;
        this.apiKey = 'demo_2025_baguette_metro';
        this.baseUrl = 'http://127.0.0.1:8000';
        
        this.init();
    }

    init() {
        this.initMap();
        this.initEventListeners();
        this.initLanguageSelector();
        this.initAutocomplete();
    }

    initMap() {
        // Initialisation de la carte Leaflet centrée sur Paris
        this.map = L.map('map').setView([48.8566, 2.3522], 12);
        
        // Ajout de la couche OpenStreetMap
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors'
        }).addTo(this.map);

        console.log('🗺️ Carte initialisée');
    }

    initEventListeners() {
        // Formulaire de calcul d'itinéraire
        const form = document.getElementById('routeForm');
        form.addEventListener('submit', (e) => {
            e.preventDefault();
            this.calculateRoute();
        });

        // Gestion des suggestions d'adresses
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.search-suggestions')) {
                this.hideAllSuggestions();
            }
        });
    }

    initLanguageSelector() {
        const langButtons = document.querySelectorAll('.lang-btn');
        langButtons.forEach(btn => {
            btn.addEventListener('click', () => {
                this.setLanguage(btn.dataset.lang);
                
                // Mise à jour visuelle
                langButtons.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
            });
        });
    }

    setLanguage(lang) {
        this.currentLanguage = lang;
        console.log(`🌍 Langue changée: ${lang}`);
        
        // Mise à jour des labels selon la langue
        this.updateLabels();
    }

    updateLabels() {
        const labels = {
            'fr': {
                startAddress: 'Adresse de départ',
                endAddress: 'Adresse d\'arrivée',
                calculateBtn: 'Calculer l\'Itinéraire',
                loading: 'Calcul en cours...',
                routeInfo: 'Informations du Trajet',
                transportDetails: 'Détails du Transport',
                bakeries: 'Boulangeries Artisanales',
                aiAdvice: 'Conseils IA'
            },
            'en': {
                startAddress: 'Start Address',
                endAddress: 'End Address',
                calculateBtn: 'Calculate Route',
                loading: 'Calculating...',
                routeInfo: 'Route Information',
                transportDetails: 'Transport Details',
                bakeries: 'Artisanal Bakeries',
                aiAdvice: 'AI Advice'
            },
            'ja': {
                startAddress: '出発地',
                endAddress: '到着地',
                calculateBtn: 'ルート計算',
                loading: '計算中...',
                routeInfo: 'ルート情報',
                transportDetails: '交通詳細',
                bakeries: '職人ベーカリー',
                aiAdvice: 'AIアドバイス'
            }
        };

        const currentLabels = labels[this.currentLanguage];
        
        // Mise à jour des labels
        document.querySelector('label[for="startAddress"]').textContent = currentLabels.startAddress;
        document.querySelector('label[for="endAddress"]').textContent = currentLabels.endAddress;
        document.getElementById('calculateBtn').innerHTML = `<i class="fas fa-route"></i> ${currentLabels.calculateBtn}`;
        document.querySelector('#loading p').textContent = currentLabels.loading;
    }

    initAutocomplete() {
        const startInput = document.getElementById('startAddress');
        const endInput = document.getElementById('endAddress');

        // Autocomplétion pour l'adresse de départ
        startInput.addEventListener('input', (e) => {
            this.handleAutocomplete(e.target.value, 'startSuggestions');
        });

        // Autocomplétion pour l'adresse d'arrivée
        endInput.addEventListener('input', (e) => {
            this.handleAutocomplete(e.target.value, 'endSuggestions');
        });
    }

    async handleAutocomplete(query, suggestionsId) {
        if (query.length < 2) {
            this.hideSuggestions(suggestionsId);
            return;
        }

        try {
            const response = await fetch(`${this.baseUrl}/places/autocomplete?query=${encodeURIComponent(query)}&limit=5`);
            const data = await response.json();

            if (data.success && data.predictions) {
                this.displaySuggestions(data.predictions, suggestionsId);
            }
        } catch (error) {
            console.error('❌ Erreur autocomplétion:', error);
        }
    }

    displaySuggestions(predictions, suggestionsId) {
        const suggestionsDiv = document.getElementById(suggestionsId);
        const input = suggestionsDiv.previousElementSibling;

        suggestionsDiv.innerHTML = '';
        suggestionsDiv.style.display = 'block';

        predictions.forEach(prediction => {
            const item = document.createElement('div');
            item.className = 'suggestion-item';
            item.textContent = prediction.description;
            
            item.addEventListener('click', () => {
                input.value = prediction.description;
                this.hideSuggestions(suggestionsId);
            });

            suggestionsDiv.appendChild(item);
        });
    }

    hideSuggestions(suggestionsId) {
        document.getElementById(suggestionsId).style.display = 'none';
    }

    hideAllSuggestions() {
        document.querySelectorAll('.search-suggestions').forEach(div => {
            div.style.display = 'none';
        });
    }

    async calculateRoute() {
        const startAddress = document.getElementById('startAddress').value.trim();
        const endAddress = document.getElementById('endAddress').value.trim();

        if (!startAddress || !endAddress) {
            this.showError('Veuillez saisir les adresses de départ et d\'arrivée');
            return;
        }

        this.showLoading(true);
        this.clearMap();
        this.hideResults();

        try {
            const response = await fetch(`${this.baseUrl}/eta/calculate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-API-Key': this.apiKey
                },
                body: JSON.stringify({
                    start_address: startAddress,
                    end_address: endAddress,
                    language: this.currentLanguage
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            this.displayResults(data);
            this.displayRouteOnMap(data);

        } catch (error) {
            console.error('❌ Erreur calcul itinéraire:', error);
            this.showError(`Erreur lors du calcul: ${error.message}`);
        } finally {
            this.showLoading(false);
        }
    }

    displayResults(data) {
        const resultsPanel = document.getElementById('resultsPanel');
        resultsPanel.style.display = 'block';

        // Informations du trajet
        this.displayRouteInfo(data);

        // Détails du transport
        this.displayTransportDetails(data);

        // Boulangeries
        this.displayBakeries(data);

        // Conseils IA
        this.displayAIAdvice(data);

        // Scroll vers les résultats
        resultsPanel.scrollIntoView({ behavior: 'smooth' });
    }

    displayRouteInfo(data) {
        const routeInfo = document.getElementById('routeInfo');
        
        routeInfo.innerHTML = `
            <div class="info-card">
                <h3>Durée</h3>
                <div class="value">${data.eta || 'N/A'}</div>
            </div>
            <div class="info-card">
                <h3>Distance</h3>
                <div class="value">${data.distance || 'N/A'}</div>
            </div>
            <div class="info-card">
                <h3>Source</h3>
                <div class="value">${data.source || 'N/A'}</div>
            </div>
            <div class="info-card">
                <h3>Niveau Sécurité</h3>
                <div class="value">${data.security_level || 'N/A'}</div>
            </div>
        `;
    }

    displayTransportDetails(data) {
        const transportSteps = document.getElementById('transportSteps');
        
        if (data.transport && data.transport.length > 0) {
            transportSteps.innerHTML = data.transport.map(step => `
                <div class="transport-step">
                    <div class="transport-icon">
                        <i class="fas fa-subway"></i>
                    </div>
                    <div class="step-details">
                        <h4>${step.line}</h4>
                        <p>Temps d'attente: ${step.wait_time} | Durée: ${step.duration} | Statut: ${step.status}</p>
                        <p>De: ${step.departure_stop} → À: ${step.arrival_stop}</p>
                    </div>
                </div>
            `).join('');
        } else {
            transportSteps.innerHTML = '<p>Aucune information de transport disponible</p>';
        }
    }

    displayBakeries(data) {
        const bakeriesList = document.getElementById('bakeriesList');
        
        if (data.bakeries && data.bakeries.length > 0) {
            bakeriesList.innerHTML = data.bakeries.map(bakery => `
                <div class="bakery-card">
                    <div class="bakery-header">
                        <div class="bakery-name">${bakery.name}</div>
                        <div class="bakery-rating">
                            <div class="stars">
                                ${this.generateStars(bakery.rating)}
                            </div>
                            <span>${bakery.rating}/5</span>
                        </div>
                    </div>
                    <div class="bakery-details">
                        <div class="detail-item">
                            <i class="fas fa-map-marker-alt"></i>
                            <span>${bakery.vicinity}</span>
                        </div>
                        <div class="detail-item">
                            <i class="fas fa-ruler"></i>
                            <span>${bakery.distance}</span>
                        </div>
                        <div class="detail-item">
                            <i class="fas fa-users"></i>
                            <span>${bakery.user_ratings_total} avis</span>
                        </div>
                        <div class="detail-item">
                            <i class="fas fa-clock"></i>
                            <span>${bakery.opening_hours ? 'Ouvert' : 'Fermé'}</span>
                        </div>
                    </div>
                </div>
            `).join('');
        } else {
            bakeriesList.innerHTML = '<p>Aucune boulangerie trouvée sur cet itinéraire</p>';
        }
    }

    displayAIAdvice(data) {
        const aiContent = document.getElementById('aiContent');
        
        if (data.ai_advice && data.ai_advice.ai_advice) {
            aiContent.innerHTML = `
                <div class="ai-content">
                    <p><strong>Source:</strong> ${data.ai_source || 'N/A'}</p>
                    <div style="margin-top: 15px; white-space: pre-line;">
                        ${data.ai_advice.ai_advice}
                    </div>
                </div>
            `;
        } else {
            aiContent.innerHTML = '<p>Aucun conseil IA disponible</p>';
        }
    }

    generateStars(rating) {
        const fullStars = Math.floor(rating);
        const hasHalfStar = rating % 1 >= 0.5;
        let stars = '';

        for (let i = 0; i < fullStars; i++) {
            stars += '<i class="fas fa-star"></i>';
        }

        if (hasHalfStar) {
            stars += '<i class="fas fa-star-half-alt"></i>';
        }

        const emptyStars = 5 - fullStars - (hasHalfStar ? 1 : 0);
        for (let i = 0; i < emptyStars; i++) {
            stars += '<i class="far fa-star"></i>';
        }

        return stars;
    }

    displayRouteOnMap(data) {
        if (!data.route_coordinates || !Array.isArray(data.route_coordinates)) {
            console.warn('⚠️ Coordonnées de route non disponibles');
            return;
        }

        // Ajout des marqueurs de départ et d'arrivée
        if (data.route_coordinates.length >= 2) {
            const start = data.route_coordinates[0];
            const end = data.route_coordinates[data.route_coordinates.length - 1];

            // Marqueur de départ
            const startMarker = L.marker([start.lat, start.lng], {
                icon: L.divIcon({
                    className: 'custom-div-icon',
                    html: '<div style="background-color: #28a745; width: 20px; height: 20px; border-radius: 50%; border: 3px solid white; box-shadow: 0 2px 4px rgba(0,0,0,0.3);"></div>',
                    iconSize: [20, 20],
                    iconAnchor: [10, 10]
                })
            }).addTo(this.map);

            startMarker.bindPopup('<b>Départ</b><br>' + (data.start_address || 'N/A'));
            this.markers.push(startMarker);

            // Marqueur d'arrivée
            const endMarker = L.marker([end.lat, end.lng], {
                icon: L.divIcon({
                    className: 'custom-div-icon',
                    html: '<div style="background-color: #dc3545; width: 20px; height: 20px; border-radius: 50%; border: 3px solid white; box-shadow: 0 2px 4px rgba(0,0,0,0.3);"></div>',
                    iconSize: [20, 20],
                    iconAnchor: [10, 10]
                })
            }).addTo(this.map);

            endMarker.bindPopup('<b>Arrivée</b><br>' + (data.end_address || 'N/A'));
            this.markers.push(endMarker);

            // Ligne de l'itinéraire
            const routeCoords = data.route_coordinates.map(coord => [coord.lat, coord.lng]);
            this.routePolyline = L.polyline(routeCoords, {
                color: '#667eea',
                weight: 6,
                opacity: 0.8
            }).addTo(this.map);

            // Ajuster la vue de la carte
            this.map.fitBounds(this.routePolyline.getBounds(), { padding: [20, 20] });
        }

        // Ajout des marqueurs des boulangeries
        if (data.bakeries && Array.isArray(data.bakeries)) {
            data.bakeries.forEach(bakery => {
                if (bakery.geometry && bakery.geometry.location) {
                    const bakeryMarker = L.marker([bakery.geometry.location.lat, bakery.geometry.location.lng], {
                        icon: L.divIcon({
                            className: 'custom-div-icon',
                            html: '<div style="background-color: #ffc107; width: 16px; height: 16px; border-radius: 50%; border: 2px solid white; box-shadow: 0 2px 4px rgba(0,0,0,0.3);"><i class="fas fa-bread-slice" style="color: white; font-size: 10px; position: absolute; top: 2px; left: 3px;"></i></div>',
                            iconSize: [16, 16],
                            iconAnchor: [8, 8]
                        })
                    }).addTo(this.map);

                    const popupContent = `
                        <div style="min-width: 200px;">
                            <h4 style="margin: 0 0 10px 0; color: #2c3e50;">${bakery.name}</h4>
                            <p style="margin: 5px 0; color: #7f8c8d;">
                                <i class="fas fa-star" style="color: #ffc107;"></i> ${bakery.rating}/5 (${bakery.user_ratings_total} avis)
                            </p>
                            <p style="margin: 5px 0; color: #7f8c8d;">
                                <i class="fas fa-map-marker-alt"></i> ${bakery.vicinity}
                            </p>
                            <p style="margin: 5px 0; color: #7f8c8d;">
                                <i class="fas fa-ruler"></i> ${bakery.distance}
                            </p>
                        </div>
                    `;

                    bakeryMarker.bindPopup(popupContent);
                    this.markers.push(bakeryMarker);
                }
            });
        }

        console.log('🗺️ Itinéraire affiché sur la carte');
    }

    clearMap() {
        // Supprimer tous les marqueurs
        this.markers.forEach(marker => this.map.removeLayer(marker));
        this.markers = [];

        // Supprimer la ligne d'itinéraire
        if (this.routePolyline) {
            this.map.removeLayer(this.routePolyline);
            this.routePolyline = null;
        }
    }

    hideResults() {
        document.getElementById('resultsPanel').style.display = 'none';
    }

    showLoading(show) {
        const loading = document.getElementById('loading');
        const calculateBtn = document.getElementById('calculateBtn');
        
        if (show) {
            loading.style.display = 'block';
            calculateBtn.disabled = true;
            calculateBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Calcul...';
        } else {
            loading.style.display = 'none';
            calculateBtn.disabled = false;
            this.updateLabels(); // Restaure le texte original
        }
    }

    showError(message) {
        const resultsPanel = document.getElementById('resultsPanel');
        resultsPanel.style.display = 'block';
        
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.innerHTML = `<i class="fas fa-exclamation-triangle"></i> ${message}`;
        
        resultsPanel.insertBefore(errorDiv, resultsPanel.firstChild);
        
        // Auto-suppression après 5 secondes
        setTimeout(() => {
            if (errorDiv.parentNode) {
                errorDiv.parentNode.removeChild(errorDiv);
            }
        }, 5000);
    }

    showSuccess(message) {
        const resultsPanel = document.getElementById('resultsPanel');
        resultsPanel.style.display = 'block';
        
        const successDiv = document.createElement('div');
        successDiv.className = 'success-message';
        successDiv.innerHTML = `<i class="fas fa-check-circle"></i> ${message}`;
        
        resultsPanel.insertBefore(successDiv, resultsPanel.firstChild);
        
        // Auto-suppression après 5 secondes
        setTimeout(() => {
            if (successDiv.parentNode) {
                successDiv.parentNode.removeChild(successDiv);
            }
        }, 5000);
    }
}

// Initialisation de l'application quand le DOM est chargé
document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 Initialisation de Baguette & Métro Advanced');
    window.baguetteMetroApp = new BaguetteMetroApp();
});


