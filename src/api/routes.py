from fastapi import APIRouter, HTTPException, Depends
from typing import Optional, List, Dict, Any
from datetime import datetime
import logging

from .schemas import (
    ETARequest, ETAResponse, ChatRequest, ChatResponse, 
    QuickResponseRequest, QuickResponseResponse, SessionStatsRequest, 
    SessionStatsResponse, HealthResponse, ErrorResponse
)
from .chat_service import chat_service
from src.data.openrouter_client import openrouter_client
from src.data.gtfs_realtime import gtfs_client, get_realtime_eta
from src.models.eta_advanced import calculate_eta_advanced
from src.models.advanced_eta_predictor import get_advanced_predictor

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/eta", response_model=ETAResponse)
async def calculate_eta(request: ETARequest):
    """
    Calcule l'ETA avancé avec ML et optimisation boulangerie
    """
    try:
        # Utilisation du nouveau système ETA avancé
        result = calculate_eta_advanced(
            start_lat=request.start_lat,
            start_lon=request.start_lon,
            end_lat=request.end_lat,
            end_lon=request.end_lon,
            include_bakery=request.include_bakery
        )
        
        # Ajout des informations de langue
        if request.language == "en":
            result["recommendation"] = result["recommendation"].replace(
                "Trajet avec boulangerie recommandé", "Route with bakery recommended"
            ).replace(
                "Trajet direct recommandé", "Direct route recommended"
            )
        elif request.language == "ja":
            result["recommendation"] = result["recommendation"].replace(
                "Trajet avec boulangerie recommandé", "パン屋経由ルート推奨"
            ).replace(
                "Trajet direct recommandé", "直行ルート推奨"
            )
        
        # Ajout de la langue dans la réponse
        result["language"] = request.language
        
        return ETAResponse(**result)

    except Exception as e:
        logger.error(f"Erreur de calcul ETA: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur de calcul ETA: {str(e)}")


@router.get("/bakeries")
async def get_nearby_bakeries(lat: float, lon: float, radius: int = 500):
    """
    Retourne les boulangeries à proximité
    """
    try:
        bakeries = openrouter_client.get_nearby_bakeries(lat, lon, radius)
        return {"bakeries": bakeries}
    except Exception as e:
        logger.error(f"Erreur récupération boulangeries: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur récupération boulangeries: {str(e)}")


@router.post("/eta/advanced", response_model=ETAResponse)
async def calculate_eta_advanced_ml(request: ETARequest):
    """
    Calcule l'ETA avec le modèle ML avancé (LSTM/Transformer)
    """
    try:
        advanced_predictor = get_advanced_predictor()
        
        # Prédiction avec le modèle avancé
        result = advanced_predictor.predict_eta(
            start_lat=request.start_lat,
            start_lon=request.start_lon,
            end_lat=request.end_lat,
            end_lon=request.end_lon
        )
        
        # Ajout des informations de langue
        if request.language == "en":
            result["recommendation"] = "Advanced ML model prediction"
        elif request.language == "ja":
            result["recommendation"] = "高度なMLモデル予測"
        else:
            result["recommendation"] = "Prédiction modèle ML avancé"
        
        # Ajout de la langue dans la réponse
        result["language"] = request.language
        
        return ETAResponse(**result)

    except Exception as e:
        logger.error(f"Erreur de calcul ETA avancé: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur de calcul ETA avancé: {str(e)}")


@router.get("/model/status")
async def get_model_status():
    """
    Retourne le statut du modèle ML
    """
    try:
        advanced_predictor = get_advanced_predictor()
        status = advanced_predictor.get_model_status()
        return status
    except Exception as e:
        logger.error(f"Erreur récupération statut modèle: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur récupération statut modèle: {str(e)}")


@router.post("/model/retrain")
async def retrain_model(num_samples: int = 50000):
    """
    Réentraîne le modèle ML avec de nouvelles données
    """
    try:
        advanced_predictor = get_advanced_predictor()
        result = advanced_predictor.retrain_model(num_samples=num_samples)
        return result
    except Exception as e:
        logger.error(f"Erreur réentraînement modèle: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur réentraînement modèle: {str(e)}")


@router.post("/chat", response_model=ChatResponse)
async def chat_with_ai(request: ChatRequest):
    """
    Endpoint de chat avec IA intelligente et fallback contextuel
    """
    try:
        # Détection automatique du contexte basée sur le message
        context = _detect_context_from_message(request.message)
        
        response = await chat_service.get_chat_response(
            message=request.message,
            language=request.language,
            context=context
        )
        
        return ChatResponse(
            response=response,
            language=request.language
        )
        
    except Exception as e:
        logger.error(f"Erreur chat AI: {str(e)}")
        # Fallback en cas d'erreur
        fallback_response = chat_service._get_fallback_response(
            request.message, 
            request.language, 
            "default"
        )
        return ChatResponse(
            response=fallback_response,
            language=request.language
        )

def _detect_context_from_message(message: str) -> str:
    """Détecte automatiquement le contexte du message"""
    message_lower = message.lower()
    
    # Détection des scénarios
    if any(word in message_lower for word in ['jour 1', 'day 1', '初日', 'première fois', 'first time']):
        return "jour1"
    elif any(word in message_lower for word in ['jour 7', 'day 7', '7日目', 'semaine', 'week']):
        return "jour7"
    elif any(word in message_lower for word in ['comment', 'how', 'どう', 'fonctionne', 'work']):
        return "default"
    else:
        return "default"


@router.post("/chat/quick", response_model=QuickResponseResponse)
async def get_quick_response(request: QuickResponseRequest):
    """
    Récupère une réponse rapide prédéfinie
    """
    try:
        quick_responses = chat_service.get_quick_responses(request.language)
        response = quick_responses.get(request.response_type, "Réponse non trouvée")
        
        return QuickResponseResponse(
            response=response,
            language=request.language
        )
        
    except Exception as e:
        logger.error(f"Erreur réponse rapide: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur réponse rapide: {str(e)}")


@router.get("/chat/session/{session_id}", response_model=SessionStatsResponse)
async def get_session_stats(session_id: str):
    """
    Récupère les statistiques d'une session de chat
    """
    try:
        stats = chat_service.get_session_stats(session_id)
        
        if "error" in stats:
            raise HTTPException(status_code=404, detail="Session non trouvée")
        
        return SessionStatsResponse(**stats)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur statistiques session: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur statistiques session: {str(e)}")


@router.delete("/chat/session/{session_id}")
async def clear_session(session_id: str):
    """
    Efface la mémoire d'une session de chat
    """
    try:
        chat_service.clear_session(session_id)
        return {"message": f"Session {session_id} effacée"}
        
    except Exception as e:
        logger.error(f"Erreur effacement session: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur effacement session: {str(e)}")


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Vérifie le statut des services
    """
    try:
        # Statut du service de chat
        chat_status = chat_service.get_service_status()
        
        # Statut général
        services = {
            "chat_service": chat_status["status"],
            "eta_model": "healthy",  # À améliorer avec un vrai check
            "openrouter": "healthy"  # À améliorer avec un vrai check
        }
        
        return HealthResponse(
            status="healthy" if all(s == "healthy" for s in services.values()) else "degraded",
            timestamp=datetime.now().isoformat(),
            version="1.0.0",
            services=services
        )
        
    except Exception as e:
        logger.error(f"Erreur health check: {str(e)}")
        return HealthResponse(
            status="unhealthy",
            timestamp=datetime.now().isoformat(),
            version="1.0.0",
            services={"error": str(e)}
        )