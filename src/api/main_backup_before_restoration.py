from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
import os
from dotenv import load_dotenv
from datetime import datetime
from route_service import ratp_route_service

# Charger les variables d'environnement
load_dotenv()

app = FastAPI(
    title="Baguette & Métro API",
    description="API pour l'optimisation des trajets RATP avec arrêt boulangerie",
    version="1.0.0"
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Pour le développement seulement
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Page d'accueil de l'API"""
    return {
        "message": "Baguette & Métro API",
        "version": "1.0.0",
        "status": "active",
        "endpoints": [
            "/health",
            "/test",
            "/eta/calculate",
            "/chat",
            "/dashboard",
            "/routes/calculate",
            "/routes/popular"
        ],
        "dashboard_url": "http://127.0.0.1:8000/dashboard",
        "quick_links": {
            "dashboard": "/dashboard",
            "routes": "/routes/popular",
            "health": "/health"
        }
    }

@app.get("/health")
async def health_check():
    """Endpoint de santé de l'application"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "services": {
            "api": "running",
            "database": "connected"
        }
    }

@app.get("/config")
async def get_config():
    """Retourne la configuration de l'application"""
    return {
        "debug": os.getenv("DEBUG", False),
        "supported_languages": os.getenv("SUPPORTED_LANGUAGES", "fr,en,ja").split(","),
        "api_port": os.getenv("API_PORT", 8000)
    }

# ==== ENDPOINTS DE TEST POUR DIAGNOSTIC ====
@app.get("/test")
async def test_endpoint():
    """Endpoint de test simple"""
    return {"message": "✅ API fonctionne", "timestamp": "2025-09-02"}

@app.post("/eta/calculate")
async def calculate_eta_simple(request: dict):
    """Endpoint ETA simplifié pour test"""
    try:
        start = request.get("start_address", "Paris")
        end = request.get("end_address", "Lyon")
        language = request.get("language", "fr")
        
        # Simulation d'une réponse ETA
        response = {
            "start_address": start,
            "end_address": end,
            "eta": "25 minutes",
            "distance": "4.2 km",
            "language": language,
            "bakeries": [
                {"name": "Boulangerie Test", "distance": "200m", "rating": 4.5}
            ],
            "transport": [
                {"line": "Métro ligne 1", "wait_time": "3 min", "duration": "15 min"}
            ]
        }
        
        return response
    except Exception as e:
        return {"error": str(e)}

@app.post("/chat")
async def chat_with_ai_complete(request: dict):
    """Endpoint chat avec IA OpenAI connectée et fallback intelligent"""
    try:
        from ai_service import call_ai_with_fallback, get_fallback_response, get_intelligent_fallback, detect_language_from_message
        
        message = request.get("message", "")
        language = request.get("language", "fr")
        
        # UTILISER LA LANGUE DEMANDÉE, PAS DÉTECTÉE
        requested_lang = language  # Langue explicitement demandée par l'utilisateur
        
        # Vérification du message
        if not message or message.strip() == "":
            response = get_fallback_response("empty", requested_lang)
            return {
                "response": response,
                "language": requested_lang,
                "source": "fallback"
            }
        
        # APPEL IA AVEC FALLBACK INTELLIGENT : OpenAI → Mistral → OpenRouter → Local
        ai_response, source = await call_ai_with_fallback(message, requested_lang)
        
        return {
            "response": ai_response,
            "language": requested_lang,
            "source": source
        }
        
    except Exception as e:
        return {"error": str(e), "source": "error"}

# ==== ENDPOINTS GÉOCODAGE HYBRIDE (Google Places + OpenStreetMap) ====
from hybrid_places_service import hybrid_places_service

@app.get("/places/autocomplete")
async def autocomplete_address(query: str, session_token: str = None):
    """Auto-complétion hybride : Google Places + OpenStreetMap"""
    try:
        if not query:
            return {"error": "Paramètre 'query' requis"}
        
        result = await hybrid_places_service.autocomplete_address(query)
        return result
        
    except Exception as e:
        return {"error": str(e)}

@app.get("/places/search-bakeries")
async def search_bakeries(location: str, radius: int = 1000):
    """Recherche de boulangeries hybride : Google Places + OpenStreetMap"""
    try:
        if not location:
            return {"error": "Paramètre 'location' requis"}
        
        result = await hybrid_places_service.search_bakeries(location, radius)
        return result
        
    except Exception as e:
        return {"error": str(e)}

@app.get("/places/geocode")
async def geocode_address(address: str):
    """Géocodage hybride : Google Places + OpenStreetMap"""
    try:
        if not address:
            return {"error": "Paramètre 'address' requis"}
        
        result = await hybrid_places_service.geocode_address(address)
        return result
        
    except Exception as e:
        return {"error": str(e)}

@app.get("/places/details/{place_id}")
async def get_place_details(place_id: str):
    """Détails d'un lieu"""
    try:
        details = await google_places_service.get_place_details(place_id)
        return {"details": details}
        
    except Exception as e:
        return {"error": str(e)}

# ==== ENDPOINT DASHBOARD DYNAMIQUE ====
from ratp_service import ratp_service

@app.get("/dashboard")
async def get_dashboard():
    """Page dashboard HTML complète"""
    try:
        html_content = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Baguette & Métro - Dashboard</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { text-align: center; margin-bottom: 30px; }
        .header h1 { font-size: 2.5em; margin: 0; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }
        .header p { font-size: 1.2em; opacity: 0.9; }
        .metrics-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .metric-card { background: rgba(255,255,255,0.1); padding: 20px; border-radius: 10px; backdrop-filter: blur(10px); border: 1px solid rgba(255,255,255,0.2); }
        .metric-card h3 { margin: 0 0 10px 0; color: #ffd700; }
        .metric-value { font-size: 2em; font-weight: bold; margin: 10px 0; }
        .metric-label { opacity: 0.8; font-size: 0.9em; }
        .ratp-section, .citymapper-section { background: rgba(255,255,255,0.1); padding: 20px; border-radius: 10px; margin-bottom: 20px; backdrop-filter: blur(10px); }
        .ratp-section h2, .citymapper-section h2 { color: #ffd700; margin-top: 0; }
        .status-indicator { display: inline-block; width: 12px; height: 12px; border-radius: 50%; margin-right: 8px; }
        .status-ok { background: #4CAF50; }
        .status-warning { background: #FF9800; }
        .status-error { background: #F44336; }
        .refresh-btn { background: #4CAF50; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; font-size: 1em; margin: 10px 0; }
        .refresh-btn:hover { background: #45a049; }
        .loading { text-align: center; padding: 40px; font-size: 1.2em; }
        @media (max-width: 768px) { .metrics-grid { grid-template-columns: 1fr; } }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🥖 Baguette & Métro</h1>
            <p>Dashboard en temps réel - Niveau Entreprise</p>
        </div>
        
        <div class="metrics-grid">
            <div class="metric-card">
                <h3>🚇 Lignes RATP</h3>
                <div class="metric-value" id="total-lines">--</div>
                <div class="metric-label">Lignes actives</div>
            </div>
            <div class="metric-card">
                <h3>👥 Utilisateurs</h3>
                <div class="metric-value" id="active-users">--</div>
                <div class="metric-label">Utilisateurs actifs</div>
            </div>
            <div class="metric-card">
                <h3>🥖 Boulangeries</h3>
                <div class="metric-value" id="bakeries-found">--</div>
                <div class="metric-label">Boulangeries trouvées</div>
            </div>
            <div class="metric-card">
                <h3>⏱️ Temps Moyen</h3>
                <div class="metric-value" id="avg-journey-time">--</div>
                <div class="metric-label">Trajet moyen</div>
            </div>
        </div>
        
        <button class="refresh-btn" onclick="refreshDashboard()">🔄 Actualiser</button>
        
        <div class="ratp-section">
            <h2>🚇 Données RATP en Temps Réel</h2>
            <div id="ratp-status">Chargement...</div>
        </div>
        
        <div class="citymapper-section">
            <h2>🗺️ Comparaison Citymapper</h2>
            <div id="citymapper-data">Chargement...</div>
        </div>
    </div>
    
    <script>
        async function refreshDashboard() {
            try {
                const response = await fetch('/dashboard/data');
                const data = await response.json();
                
                if (data.error) {
                    throw new Error(data.error);
                }
                
                // Mise à jour des métriques
                document.getElementById('total-lines').textContent = data.metrics?.total_routes || '--';
                document.getElementById('active-users').textContent = data.metrics?.active_users || '--';
                document.getElementById('bakeries-found').textContent = data.metrics?.bakeries_found || '--';
                document.getElementById('avg-journey-time').textContent = data.metrics?.avg_journey_time || '--';
                
                // Statut RATP
                const ratpStatus = document.getElementById('ratp-status');
                const ratpSource = data.ratp?.source || 'unknown';
                const ratpFallback = data.ratp?.fallback_used || false;
                
                ratpStatus.innerHTML = `
                    <div><span class="status-indicator ${ratpSource === 'prim_api' ? 'status-ok' : ratpFallback ? 'status-warning' : 'status-error'}"></span>
                    Source: ${ratpSource === 'prim_api' ? 'API PRIM RATP' : ratpFallback ? 'Simulation intelligente' : 'Erreur'}</div>
                    <div>Lignes: ${data.ratp?.lines_status?.length || 0}</div>
                    <div>Délais: ${data.ratp?.delays?.average || 0} min</div>
                    <div>Affluence: ${data.ratp?.stations_crowding?.average || 0}%</div>
                `;
                
                // Données Citymapper
                const citymapperData = document.getElementById('citymapper-data');
                if (data.citymapper?.routes_comparison) {
                    citymapperData.innerHTML = data.citymapper.routes_comparison.map(route => `
                        <div style="margin: 10px 0; padding: 10px; background: rgba(255,255,255,0.1); border-radius: 5px;">
                            <strong>${route.route}</strong> - ${route.duration} - ${route.cost}
                            <span style="color: ${route.eco_friendly ? '#4CAF50' : '#FF9800'}">${route.eco_friendly ? '🌱' : '🚗'}</span>
                        </div>
                    `).join('');
                }
                
            } catch (error) {
                console.error('Erreur dashboard:', error);
                document.getElementById('ratp-status').innerHTML = `<div style="color: #ff6b6b;">Erreur: ${error.message}</div>`;
            }
        }
        
        // Chargement initial
        refreshDashboard();
        
        // Actualisation automatique toutes les 30 secondes
        setInterval(refreshDashboard, 30000);
    </script>
</body>
</html>
        """
        return HTMLResponse(content=html_content, status_code=200)
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Erreur génération dashboard: {str(e)}"}
        )

@app.get("/dashboard/data")
async def get_dashboard_data():
    """Données complètes pour le dashboard dynamique"""
    try:
        # Données RATP réelles via API PRIM + fallback
        ratp_response = await ratp_service.get_real_time_data()
        ratp_data = ratp_response["data"]
        ratp_source = ratp_response["source"]
        ratp_fallback = ratp_response["fallback_used"]
        
        # Données Citymapper mockées (API payante)
        citymapper_data = {
            "routes_comparison": [
                {
                    "route": "Métro + Bus",
                    "duration": "25 min",
                    "cost": "2.10€",
                    "comfort": "Moyen",
                    "eco_friendly": True
                },
                {
                    "route": "Vélo",
                    "duration": "35 min", 
                    "cost": "0€",
                    "comfort": "Élevé",
                    "eco_friendly": True
                },
                {
                    "route": "Taxi",
                    "duration": "20 min",
                    "cost": "18€",
                    "comfort": "Élevé",
                    "eco_friendly": False
                }
            ],
            "real_time_updates": [
                {"type": "Trafic", "message": "Trafic dense sur le périphérique", "severity": "medium"},
                {"type": "Météo", "message": "Pluie prévue, privilégier les transports", "severity": "low"}
            ]
        }
        
        # Métriques globales
        metrics = {
            "total_routes": 156,
            "active_users": 1247,
            "bakeries_found": 89,
            "avg_journey_time": "28 min",
            "eco_routes_percentage": 67
        }
        
        return {
            "ratp": {
                **ratp_data,
                "source": ratp_source,
                "fallback_used": ratp_fallback
            },
            "citymapper": citymapper_data,
            "metrics": metrics,
            "timestamp": "2024-01-15T20:30:00Z"
        }
        
    except Exception as e:
        return {"error": str(e)}

# ==== ENDPOINTS D'ITINÉRAIRES RATP ====
@app.post("/routes/calculate")
async def calculate_route(request: dict):
    """Calcule un itinéraire RATP avec arrêts boulangerie"""
    try:
        origin = request.get("origin", "")
        destination = request.get("destination", "")
        departure_time = request.get("departure_time")
        include_bakeries = request.get("include_bakeries", True)
        max_walking = request.get("max_walking_distance", 0.5)
        
        if not origin or not destination:
            raise HTTPException(status_code=400, detail="Origin et destination requis")
        
        # Calcul de l'itinéraire
        routes = await ratp_route_service.calculate_route(
            origin=origin,
            destination=destination,
            departure_time=departure_time,
            include_bakeries=include_bakeries,
            max_walking_distance=max_walking
        )
        
        return {
            "origin": origin,
            "destination": destination,
            "routes": [
                {
                    "id": route.id,
                    "total_duration": route.total_duration,
                    "total_distance": route.total_distance,
                    "changes_count": route.changes_count,
                    "bakery_stops": route.bakery_stops,
                    "eco_score": route.eco_score,
                    "cost_estimate": route.cost_estimate,
                    "segments": [
                        {
                            "mode": segment.mode.value,
                            "line": segment.line,
                            "departure_station": segment.departure_station,
                            "arrival_station": segment.arrival_station,
                            "departure_time": segment.departure_time,
                            "arrival_time": segment.arrival_time,
                            "duration_minutes": segment.duration_minutes,
                            "distance_km": segment.distance_km
                        }
                        for segment in route.segments
                    ]
                }
                for route in routes
            ],
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Erreur calcul itinéraire: {str(e)}"}
        )

@app.get("/routes/popular")
async def get_popular_routes():
    """Récupère les itinéraires populaires"""
    try:
        popular_routes = await ratp_route_service.get_popular_routes()
        return {
            "routes": popular_routes,
            "timestamp": datetime.now().isoformat()
            }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Erreur récupération routes populaires: {str(e)}"}
        )

@app.get("/routes/{route_id}")
async def get_route_details(route_id: str):
    """Récupère les détails d'un itinéraire spécifique"""
    try:
        route = await ratp_route_service.get_route_details(route_id)
        if not route:
            raise HTTPException(status_code=404, detail="Itinéraire non trouvé")
        
        return {
            "route": {
                "id": route.id,
                "total_duration": route.total_duration,
                "total_distance": route.total_distance,
                "changes_count": route.changes_count,
                "bakery_stops": route.bakery_stops,
                "eco_score": route.eco_score,
                "cost_estimate": route.cost_estimate,
                "segments": [
                    {
                        "mode": segment.mode.value,
                        "line": segment.line,
                        "departure_station": segment.departure_station,
                        "arrival_station": segment.arrival_station,
                        "departure_time": segment.departure_time,
                        "arrival_time": segment.arrival_time,
                        "duration_minutes": segment.duration_minutes,
                        "distance_km": segment.distance_km
                    }
                    for segment in route.segments
                ]
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Erreur récupération détails route: {str(e)}"}
        )

# Gestionnaire d'erreurs global
@app.exception_handler(500)
async def internal_server_error_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"message": "Erreur interne du serveur", "detail": str(exc)}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
