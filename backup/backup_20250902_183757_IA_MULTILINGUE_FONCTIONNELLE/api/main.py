from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
from dotenv import load_dotenv

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
            "/chat"
        ]
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
    """Endpoint chat avec IA OpenRouter connectée et fallback intelligent"""
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
        
        # APPEL IA AVEC FALLBACK INTELLIGENT : Mistral → OpenRouter → Local
        ai_response, source = await call_ai_with_fallback(message, requested_lang)
        
        return {
            "response": ai_response,
            "language": requested_lang,
            "source": source
        }
        
    except Exception as e:
        return {"error": str(e), "source": "error"}

@app.get("/dashboard")
async def get_dashboard_data():
    """Endpoint pour récupérer les données du dashboard temps réel"""
    try:
        from datetime import datetime
        # Simuler les métriques temps réel (en attendant l'intégration complète)
        dashboard_data = {
            "overview": {
                "total_vehicles": 25,
                "active_lines": 5,
                "average_speed": 21.7,
                "system_health": "excellent",
                "last_update": datetime.now().isoformat()
            },
            "performance": {
                "peak_hours": {
                    "morning": {"7h-9h": 85, "17h-19h": 78},
                    "off_peak": {"9h-17h": 45, "19h-23h": 32}
                },
                "line_performance": {
                    "line_1": {"punctuality": 94, "congestion": "low"},
                    "line_4": {"punctuality": 91, "congestion": "medium"},
                    "line_6": {"punctuality": 89, "congestion": "low"},
                    "line_9": {"punctuality": 92, "congestion": "medium"},
                    "line_14": {"punctuality": 96, "congestion": "low"}
                }
            },
            "analytics": {
                "total_delays_today": 12,
                "average_delay": 3.2,
                "stations_with_prim": 280,
                "user_satisfaction": 4.6
            },
            "citymapper_comparison": {
                "ratp_accuracy": 94.2,
                "citymapper_accuracy": 91.8,
                "advantage": "RATP +2.4%",
                "last_updated": datetime.now().isoformat()
            }
        }
        
        return {
            "status": "success",
            "data": dashboard_data,
            "source": "simulated_realtime"
        }
        
    except Exception as e:
        return {"error": str(e), "source": "error"}

@app.get("/dashboard/ratp/vehicles")
async def get_ratp_vehicles():
    """Endpoint pour les véhicules RATP en temps réel"""
    try:
        import numpy as np
        from datetime import datetime
        # Simuler les données des véhicules
        vehicles = []
        for i in range(25):
            vehicles.append({
                "vehicle_id": f"RATP_{i+1:03d}",
                "line_id": f"line_{np.random.choice([1, 4, 6, 9, 14])}",
                "latitude": 48.8566 + np.random.uniform(-0.01, 0.01),
                "longitude": 2.3522 + np.random.uniform(-0.01, 0.01),
                "speed": np.random.uniform(15, 30),
                "congestion": np.random.choice(["low", "medium", "high"]),
                "timestamp": datetime.now().isoformat()
            })
        
        return {
            "status": "success",
            "vehicles": vehicles,
            "count": len(vehicles),
            "source": "simulated_realtime"
        }
        
    except Exception as e:
        return {"error": str(e), "source": "error"}

@app.get("/dashboard/ratp/analytics")
async def get_ratp_analytics():
    """Endpoint pour les analytics RATP"""
    try:
        analytics = {
            "vehicle_count": 25,
            "average_speed": 21.7,
            "lines_performance": {
                "line_1": {"punctuality": 94, "congestion": "low", "passengers": 12500},
                "line_4": {"punctuality": 91, "congestion": "medium", "passengers": 9800},
                "line_6": {"punctuality": 89, "congestion": "low", "passengers": 11200},
                "line_9": {"punctuality": 92, "congestion": "medium", "passengers": 8900},
                "line_14": {"punctuality": 96, "congestion": "low", "passengers": 15600}
            },
            "stations_congestion": {
                "Châtelet": "high",
                "Gare de Lyon": "medium",
                "République": "low",
                "Montparnasse": "medium",
                "Saint-Lazare": "high"
            },
            "delays": {
                "total_today": 12,
                "average_minutes": 3.2,
                "most_affected_line": "line_4"
            }
        }
        
        return {
            "status": "success",
            "analytics": analytics,
            "source": "simulated_realtime"
        }
        
    except Exception as e:
        return {"error": str(e), "source": "error"}

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
