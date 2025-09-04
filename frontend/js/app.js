// Configuration de l'application
const CONFIG = {
    API_BASE_URL: 'http://localhost:8000',
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
        noResults: 'Aucun résultat trouvé'
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
        noResults: 'No results found'
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
        noResults: '結果が見つかりません'
    }
};

// Initialisation de l'application
document.addEventListener('DOMContentLoaded', function() {
    initializeMap();
    setupEventListeners();
    setupLanguageSelector();
    addWelcomeMessage();
});

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

// Calcul d'itinéraire
async function calculateRoute() {
    const start = document.getElementById('start-input').value;
    const end = document.getElementById('end-input').value;
    
    if (!start || !end) {
        showError('Veuillez remplir les champs de départ et de destination');
        return;
    }
    
    showLoading();
    
    try {
        // Simulation d'un calcul d'itinéraire
        await simulateRouteCalculation(start, end);
        
        // Ajouter des marqueurs sur la carte
        addRouteMarkers(start, end);
        
        // Afficher les résultats
        displayResults(start, end);
        
    } catch (error) {
        showError('Erreur lors du calcul de l\'itinéraire');
        console.error(error);
    }
}

// Simulation du calcul d'itinéraire
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
function addRouteMarkers(start, end) {
    // Nettoyer les marqueurs existants
    markers.forEach(marker => map.removeLayer(marker));
    markers = [];
    
    // Coordonnées simulées
    const startCoords = [CONFIG.DEFAULT_LAT - 0.01, CONFIG.DEFAULT_LNG - 0.01];
    const endCoords = [CONFIG.DEFAULT_LAT + 0.01, CONFIG.DEFAULT_LNG + 0.01];
    
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

// Affichage des résultats
function displayResults(start, end) {
    const container = document.getElementById('results-container');
    
    container.innerHTML = `
        <div class="result-item">
            <h3>🚀 Itinéraire calculé</h3>
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

// Envoi de message à l'assistant IA
async function sendMessage() {
    const input = document.getElementById('message-input');
    const message = input.value.trim();
    
    if (!message) return;
    
    // Ajouter le message utilisateur
    addChatMessage('user', message);
    input.value = '';
    
    // Simuler une réponse de l'IA
    setTimeout(() => {
        const response = generateAIResponse(message);
        addChatMessage('assistant', response);
    }, 1000);
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

// Génération de réponse IA simulée
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
function showLoading() {
    const container = document.getElementById('results-container');
    container.innerHTML = '<div class="loading">🔄 Calcul en cours...</div>';
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

// Styles CSS supplémentaires pour les messages
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
`;

// Ajouter les styles supplémentaires
const styleSheet = document.createElement('style');
styleSheet.textContent = additionalStyles;
document.head.appendChild(styleSheet);


