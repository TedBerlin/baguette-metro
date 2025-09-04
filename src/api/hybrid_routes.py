#!/usr/bin/env python3
"""
Routes API pour le service de chat hybride - MVP
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, Optional
import logging
from pydantic import BaseModel

from .hybrid_chat_service import hybrid_chat_service

logger = logging.getLogger(__name__)
router = APIRouter()


class ChatRequest(BaseModel):
    question: str
    session_id: Optional[str] = None
    language: Optional[str] = None


class QuickResponseRequest(BaseModel):
    response_type: str
    language: str = "fr"


class ChatResponse(BaseModel):
    response: str
    language: str
    model: str
    metadata: Dict[str, Any]


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Endpoint de chat principal pour le MVP
    """
    try:
        logger.info(f"Chat request received: {request.question[:50]}...")
        
        # Appel au service de chat hybride
        result = await hybrid_chat_service.chat_completion(
            message=request.question,
            language=request.language
        )
        
        logger.info(f"Chat response generated successfully")
        return ChatResponse(**result)
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur lors du chat: {str(e)}")


@router.post("/chat/quick", response_model=ChatResponse)
async def quick_response_endpoint(request: QuickResponseRequest):
    """
    Endpoint pour les réponses rapides (boutons d'action)
    """
    try:
        logger.info(f"Quick response request: {request.response_type}")
        
        # Appel au service de réponses rapides
        result = await hybrid_chat_service.quick_response(
            response_type=request.response_type,
            language=request.language
        )
        
        logger.info(f"Quick response generated successfully")
        return ChatResponse(**result)
        
    except Exception as e:
        logger.error(f"Error in quick response endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de la réponse rapide: {str(e)}")


@router.get("/chat/health")
async def chat_health_check():
    """
    Vérification de santé du service de chat
    """
    try:
        # Test simple du service
        test_result = await hybrid_chat_service.quick_response("comment_ca_marche", "fr")
        
        return {
            "status": "healthy",
            "service": "hybrid_chat",
            "model": "openai/gpt-4o-mini",
            "fallback": "available",
            "timestamp": test_result["metadata"]["timestamp"]
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "degraded",
            "service": "hybrid_chat",
            "error": str(e),
            "fallback": "available"
        }


@router.get("/chat/info")
async def chat_info():
    """
    Informations sur le service de chat
    """
    return {
        "service": "Hybrid Chat Service",
        "version": "1.0.0",
        "model": "openai/gpt-4o-mini",
        "features": [
            "Chat multilingue (FR/EN/JP)",
            "Détection automatique de langue",
            "Réponses rapides",
            "Fallback en cas d'erreur",
            "Prompts spécialisés RATP + Boulangeries"
        ],
        "supported_languages": ["fr", "en", "ja"],
        "quick_responses": [
            "comment_ca_marche",
            "meilleures_boulangeries", 
            "optimiser_trajet"
        ]
    }





