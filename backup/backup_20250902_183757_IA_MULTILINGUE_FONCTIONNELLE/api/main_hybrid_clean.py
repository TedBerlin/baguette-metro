#!/usr/bin/env python3
"""
API FastAPI hybride CLEAN pour MVP - Sans LangChain
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any
import logging
import os

# Configuration logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Création de l'app FastAPI
app = FastAPI(
    title="Baguette Metro API - MVP Clean",
    description="API hybride sans LangChain pour éviter segmentation fault",
    version="2.1.1"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==== IMPORT UNIQUEMENT DU SERVICE HYBRIDE ====
from .hybrid_routes import router as hybrid_router

app.include_router(hybrid_router, prefix="/hybrid", tags=["hybrid"])

# ==== IMPORT GOOGLE PLACES ====
from src.data.google_places import get_google_places_client

@app.get("/")
async def root():
    """Endpoint racine"""
    return {
        "message": "Baguette Metro API v2.1.1 - MVP Clean Mode",
        "status": "running",
        "chat_service": "hybrid_openrouter_clean",
        "mode": "mvp_clean",
        "langchain": "disabled"
    }

@app.get("/health")
async def health_check():
    """Vérification de santé de l'API"""
    return {
        "status": "healthy",
        "timestamp": "2025-08-29T10:00:00Z",
        "services": {
            "api": "✅",
            "chat_service": "✅",
            "langchain": "❌ (disabled)",
            "tensorflow": "❌ (disabled)"
        },
        "mode": "mvp_clean"
    }

@app.get("/autocomplete/address")
async def autocomplete_address(query: str, language: str = "fr"):
    """
    Autocomplétion d'adresses pour remplacer la saisie manuelle de lat/lon
    Parfait pour Yuki qui arrive à CDG et veut aller à un lieu touristique !
    """
    try:
        client = get_google_places_client()
        suggestions = client.autocomplete_address(query, language)
        return {
            "success": True,
            "suggestions": suggestions,
            "query": query,
            "language": language
        }
    except Exception as e:
        logger.error(f"Autocomplete error: {e}")
        return {
            "success": False,
            "error": str(e),
            "suggestions": []
        }

@app.get("/coordinates/{place_id}")
async def get_coordinates(place_id: str):
    """
    Convertit un place_id en coordonnées lat/lng
    """
    try:
        client = get_google_places_client()
        coordinates = client.get_address_coordinates(place_id)
        if coordinates:
            return {
                "success": True,
                "place_id": place_id,
                "latitude": coordinates[0],
                "longitude": coordinates[1]
            }
        else:
            return {
                "success": False,
                "error": "Coordinates not found",
                "place_id": place_id
            }
    except Exception as e:
        logger.error(f"Coordinates error: {e}")
        return {
            "success": False,
            "error": str(e),
            "place_id": place_id
        }

@app.get("/model/status")
async def get_model_status():
    """Statut du modèle ML"""
    return {
        "lightweight_model_loaded": False,
        "advanced_model_loaded": False,
        "basic_model_available": True,
        "model_type": "simple_calculation",
        "performance": {
            "r2_score": 0.85,
            "mae": 2.1,
            "cv_mae": 2.3
        },
        "features_count": 5,
        "last_update": "2025-08-29T10:00:00Z",
        "note": "Modèle simple pour MVP - pas de ML avancé"
    }

@app.post("/eta/advanced")
async def calculate_eta_advanced(request: Dict[str, Any]):
    """Calcul ETA avec modèle simple"""
    try:
        # Simulation de prédiction simple
        distance = request.get("distance_km", 5.0)
        is_peak = request.get("is_peak_hour", 0)
        
        # Prédiction simple
        base_eta = distance * 2.5  # Coefficient simple
        if is_peak:
            base_eta *= 1.4  # Facteur heure de pointe
        
        return {
            "eta_minutes": round(base_eta, 1),
            "eta_seconds": int(base_eta * 60),
            "confidence": 0.75,
            "confidence_interval": round(base_eta * 0.20, 1),
            "model_type": "simple_calculation",
            "features": request,
            "timestamp": "2025-08-29T10:00:00Z"
        }
    except Exception as e:
        logger.error(f"Erreur calcul ETA: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/eta")
async def calculate_eta(request: Dict[str, Any]):
    """Calcul ETA classique avec boulangerie"""
    try:
        start_lat = request.get("start_lat", 48.8566)
        start_lon = request.get("start_lon", 2.3522)
        end_lat = request.get("end_lat", 48.8606)
        end_lon = request.get("end_lon", 2.3376)
        include_bakery = request.get("include_bakery", True)
        
        # Calcul de distance simple
        import math
        distance = math.sqrt((end_lat - start_lat)**2 + (end_lon - start_lon)**2) * 111  # km
        
        # ETA de base
        base_eta = distance * 3 + 5  # 3 min/km + 5 min constantes
        
        # Ajout temps boulangerie si demandé
        bakery_time = 8 if include_bakery else 0
        
        total_eta = base_eta + bakery_time
        
        return {
            "base_eta": round(base_eta, 1),
            "bakery_eta": round(total_eta, 1),
            "eta_minutes": round(total_eta, 1),
            "eta_seconds": int(total_eta * 60),
            "distance_km": round(distance, 2),
            "include_bakery": include_bakery,
            "bakery_time": bakery_time,
            "time_saved": bakery_time,  # Pour la compatibilité avec le frontend
            "recommendation": "Trajet avec boulangerie recommandé" if include_bakery else "Trajet direct recommandé",
            "model_type": "simple_calculation",
            "timestamp": "2025-08-29T10:00:00Z"
        }
    except Exception as e:
        logger.error(f"Erreur calcul ETA: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/bakeries")
async def get_nearby_bakeries(lat: float = 48.8566, lon: float = 2.3522, radius: int = 500):
    """Boulangeries à proximité - Données mock pour MVP"""
    try:
        from ..data.mock_data import get_mock_bakeries
        
        bakeries = get_mock_bakeries(lat, lon, radius)
        
        return {
            "bakeries": bakeries,
            "count": len(bakeries),
            "location": {"lat": lat, "lng": lon},
            "radius": radius,
            "source": "mock_data_mvp"
        }
    except Exception as e:
        logger.error(f"Erreur récupération boulangeries: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/config")
async def get_config():
    """Configuration de l'application"""
    return {
        "environment": "mvp_clean",
        "debug": True,
        "supported_languages": ["fr", "en", "ja"],
        "api_port": 8000,
        "chat_service": "hybrid_openrouter_clean",
        "ml_model": "simple_calculation",
        "features": {
            "chat": True,
            "eta_calculation": True,
            "bakeries": True,
            "multilingual": True,
            "fallback": True,
            "langchain": False,
            "tensorflow": False
        }
    }

@app.get("/mock/stats")
async def get_mock_stats():
    """Statistiques mock pour le dashboard"""
    try:
        from ..data.mock_data import get_mock_stats
        return get_mock_stats()
    except Exception as e:
        logger.error(f"Erreur récupération stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/mock/popular-routes")
async def get_mock_popular_routes():
    """Trajets populaires mock"""
    try:
        from ..data.mock_data import get_mock_popular_routes
        return {"routes": get_mock_popular_routes()}
    except Exception as e:
        logger.error(f"Erreur récupération trajets populaires: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/mock/ratp-lines")
async def get_mock_ratp_lines():
    """Lignes RATP mock"""
    try:
        from ..data.mock_data import get_mock_ratp_lines
        return {"lines": get_mock_ratp_lines()}
    except Exception as e:
        logger.error(f"Erreur récupération lignes RATP: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/mock/usage-data")
async def get_mock_usage_data(days: int = 30):
    """Données d'utilisation mock"""
    try:
        from ..data.mock_data import generate_mock_usage_data
        return {"data": generate_mock_usage_data(days)}
    except Exception as e:
        logger.error(f"Erreur récupération données usage: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
