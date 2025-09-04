#!/usr/bin/env python3
"""
API FastAPI simplifiée pour MVP - Version fonctionnelle immédiate
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any, List
import logging
import os
import requests
import json
from datetime import datetime

# Configuration logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Création de l'app FastAPI
app = FastAPI(
    title="Baguette Metro API - MVP Simple",
    description="API simplifiée pour MVP bootcamp",
    version="2.1.2"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Endpoint racine"""
    return {
        "message": "Baguette Metro API v2.1.2 - MVP Simple Mode",
        "status": "running",
        "mode": "mvp_simple"
    }

@app.get("/health")
async def health_check():
    """Vérification de santé de l'API"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "api": "✅",
            "chat_service": "✅",
            "autocomplete": "✅"
        },
        "mode": "mvp_simple"
    }

@app.get("/autocomplete/address")
async def autocomplete_address(query: str, language: str = "fr"):
    """Autocomplétion d'adresses - Mock data pour MVP"""
    try:
        # Mock data pour différentes langues
        mock_addresses = {
            "fr": [
                f"{query} - Paris, France",
                f"{query} - Lyon, France", 
                f"{query} - Marseille, France"
            ],
            "en": [
                f"{query} - Paris, France",
                f"{query} - London, UK",
                f"{query} - New York, USA"
            ],
            "ja": [
                f"{query} - パリ, フランス",
                f"{query} - 東京, 日本",
                f"{query} - 大阪, 日本"
            ]
        }
        
        suggestions = mock_addresses.get(language, mock_addresses["fr"])
        
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
    """Convertit un place_id en coordonnées lat/lng - Mock data"""
    try:
        # Mock coordinates basées sur le place_id
        mock_coords = {
            "paris": (48.8566, 2.3522),
            "lyon": (45.7578, 4.8320),
            "marseille": (43.2965, 5.3698),
            "london": (51.5074, -0.1278),
            "newyork": (40.7128, -74.0060),
            "tokyo": (35.6762, 139.6503),
            "osaka": (34.6937, 135.5023)
        }
        
        # Extraire la ville du place_id
        city = place_id.lower().split(" - ")[-1].split(",")[0].lower()
        if "paris" in city:
            lat, lng = mock_coords["paris"]
        elif "lyon" in city:
            lat, lng = mock_coords["lyon"]
        elif "marseille" in city:
            lat, lng = mock_coords["marseille"]
        elif "london" in city:
            lat, lng = mock_coords["london"]
        elif "new york" in city or "newyork" in city:
            lat, lng = mock_coords["newyork"]
        elif "tokyo" in city:
            lat, lng = mock_coords["tokyo"]
        elif "osaka" in city:
            lat, lng = mock_coords["osaka"]
        else:
            lat, lng = mock_coords["paris"]  # Default
        
        return {
            "success": True,
            "place_id": place_id,
            "latitude": lat,
            "longitude": lng
        }
    except Exception as e:
        logger.error(f"Coordinates error: {e}")
        return {
            "success": False,
            "error": str(e)
        }

@app.post("/hybrid/chat")
async def hybrid_chat(request: Dict[str, Any]):
    """Chat hybride avec OpenRouter - Fallback pour MVP"""
    try:
        question = request.get("question", "")
        language = request.get("language", "fr")
        
        # Réponses prédéfinies selon la langue
        responses = {
            "fr": {
                "default": "Bonjour ! Je suis l'assistant IA de Baguette & Métro. Je peux vous aider à optimiser vos trajets RATP avec des arrêts boulangerie.",
                "trajet": "Pour optimiser votre trajet, entrez vos coordonnées de départ et d'arrivée. Je vous recommanderai les meilleures boulangeries sur votre route.",
                "boulangerie": "Les boulangeries sont sélectionnées selon leur qualité, leur proximité avec les stations RATP, et les avis utilisateurs.",
                "temps": "Le calcul prend en compte le temps de trajet RATP, l'arrêt boulangerie, et optimise votre temps total."
            },
            "en": {
                "default": "Hello! I'm the AI assistant for Baguette & Métro. I can help you optimize your RATP journeys with bakery stops.",
                "route": "To optimize your route, enter your departure and arrival coordinates. I'll recommend the best bakeries on your route.",
                "bakery": "Bakeries are selected based on quality, proximity to RATP stations, and user reviews.",
                "time": "The calculation takes into account RATP travel time, bakery stop, and optimizes your total time."
            },
            "ja": {
                "default": "こんにちは！バゲット＆メトロのAIアシスタントです。パン屋での立ち寄りでRATPの旅を最適化するお手伝いができます。",
                "route": "ルートを最適化するには、出発地と到着地の座標を入力してください。ルート上の最高のパン屋をお勧めします。",
                "bakery": "パン屋は品質、RATP駅への近さ、ユーザーレビューに基づいて選択されます。",
                "time": "計算にはRATP移動時間、パン屋での立ち寄りが含まれ、総時間を最適化します。"
            }
        }
        
        # Logique simple pour choisir la réponse
        question_lower = question.lower()
        lang_responses = responses.get(language, responses["fr"])
        
        if any(word in question_lower for word in ["trajet", "route", "ルート"]):
            response = lang_responses.get("trajet", lang_responses["default"])
        elif any(word in question_lower for word in ["boulangerie", "bakery", "パン屋"]):
            response = lang_responses.get("boulangerie", lang_responses["default"])
        elif any(word in question_lower for word in ["temps", "time", "時間"]):
            response = lang_responses.get("temps", lang_responses["default"])
        else:
            response = lang_responses["default"]
        
        return {
            "success": True,
            "response": response,
            "model": "fallback_mvp",
            "language": language,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Chat error: {e}")
        return {
            "success": False,
            "error": str(e),
            "response": "Désolé, je ne peux pas traiter votre demande pour le moment."
        }

@app.get("/hybrid/chat/health")
async def chat_health():
    """Santé du service de chat"""
    return {
        "status": "healthy",
        "service": "hybrid_chat_fallback",
        "mode": "mvp_simple"
    }

@app.get("/eta")
async def calculate_eta(
    lat1: float = 48.8566, 
    lon1: float = 2.3522, 
    lat2: float = 48.8606, 
    lon2: float = 2.3376,
    include_bakery: bool = True
):
    """Calcul ETA avec boulangerie - Mock data pour MVP"""
    try:
        # Calcul simple de distance
        import math
        distance = math.sqrt((lat2 - lat1)**2 + (lon2 - lon1)**2) * 111  # km
        
        # Temps de base (métro)
        base_eta = distance * 3  # 3 min/km
        
        # Temps avec boulangerie
        bakery_time = 7 if include_bakery else 0  # 7 min d'arrêt
        total_eta = base_eta + bakery_time
        
        return {
            "success": True,
            "base_eta": round(base_eta, 1),
            "bakery_eta": round(total_eta, 1),
            "distance_km": round(distance, 2),
            "include_bakery": include_bakery,
            "bakery_time": bakery_time,
            "recommendation": "Trajet avec boulangerie recommandé" if include_bakery else "Trajet direct recommandé",
            "model_type": "simple_calculation_mvp"
        }
    except Exception as e:
        logger.error(f"ETA calculation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/config")
async def get_config():
    """Configuration de l'application"""
    return {
        "environment": "mvp_simple",
        "debug": True,
        "supported_languages": ["fr", "en", "ja"],
        "api_port": 8000,
        "chat_service": "hybrid_fallback_mvp",
        "features": {
            "chat": True,
            "eta_calculation": True,
            "autocomplete": True,
            "multilingual": True,
            "fallback": True
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
