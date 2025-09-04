#!/usr/bin/env python3
"""
Schémas Pydantic pour l'API FastAPI
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class ETARequest(BaseModel):
    """Schéma pour la requête ETA"""
    start_lat: float = Field(..., description="Latitude du point de départ")
    start_lon: float = Field(..., description="Longitude du point de départ")
    end_lat: float = Field(..., description="Latitude du point d'arrivée")
    end_lon: float = Field(..., description="Longitude du point d'arrivée")
    include_bakery: bool = Field(True, description="Inclure un arrêt boulangerie")
    language: str = Field("fr", description="Langue de la réponse")


class ETAResponse(BaseModel):
    """Schéma pour la réponse ETA"""
    base_eta: float = Field(..., description="Temps de trajet direct en minutes")
    bakery_eta: Optional[float] = Field(None, description="Temps avec arrêt boulangerie")
    time_saved: float = Field(..., description="Temps gagné/perdu en minutes")
    recommendation: str = Field(..., description="Recommandation de trajet")
    bakery: Optional[Dict[str, Any]] = Field(None, description="Informations sur la boulangerie")
    route_details: Dict[str, Any] = Field(..., description="Détails du trajet")
    optimization_tips: List[str] = Field(..., description="Conseils d'optimisation")
    language: str = Field(..., description="Langue de la réponse")


class ChatRequest(BaseModel):
    """Schéma pour la requête de chat"""
    message: str = Field(..., description="Message de l'utilisateur")
    language: str = Field("fr", description="Langue cible")
    context: Optional[str] = Field("default", description="Contexte de la conversation")


class ChatResponse(BaseModel):
    """Schéma pour la réponse de chat"""
    response: str = Field(..., description="Réponse de l'assistant")
    language: str = Field(..., description="Langue de la réponse")


class QuickResponseRequest(BaseModel):
    """Schéma pour les réponses rapides"""
    response_type: str = Field(..., description="Type de réponse rapide")
    language: str = Field("fr", description="Langue de la réponse")


class QuickResponseResponse(BaseModel):
    """Schéma pour les réponses rapides"""
    response: str = Field(..., description="Réponse prédéfinie")
    language: str = Field(..., description="Langue de la réponse")


class SessionStatsRequest(BaseModel):
    """Schéma pour les statistiques de session"""
    session_id: str = Field(..., description="ID de session")


class SessionStatsResponse(BaseModel):
    """Schéma pour les statistiques de session"""
    session_id: str = Field(..., description="ID de session")
    message_count: int = Field(..., description="Nombre de messages")
    created_at: str = Field(..., description="Date de création")


class HealthResponse(BaseModel):
    """Schéma pour la réponse de santé"""
    status: str = Field(..., description="Statut du service")
    timestamp: str = Field(..., description="Horodatage")
    version: str = Field(..., description="Version de l'API")
    services: Dict[str, str] = Field(..., description="Statut des services")


class ErrorResponse(BaseModel):
    """Schéma pour les erreurs"""
    error: str = Field(..., description="Message d'erreur")
    detail: Optional[str] = Field(None, description="Détails de l'erreur")
    timestamp: str = Field(..., description="Horodatage de l'erreur")


# Schémas pour les données de transport
class TransportData(BaseModel):
    """Schéma pour les données de transport"""
    line_code: str = Field(..., description="Code de la ligne")
    direction: str = Field(..., description="Direction")
    destination: str = Field(..., description="Destination")
    eta: List[str] = Field(..., description="Horaires d'arrivée")
    message: str = Field(..., description="Message d'information")


class BakeryData(BaseModel):
    """Schéma pour les données de boulangerie"""
    name: str = Field(..., description="Nom de la boulangerie")
    address: str = Field(..., description="Adresse")
    latitude: float = Field(..., description="Latitude")
    longitude: float = Field(..., description="Longitude")
    rating: float = Field(..., description="Note moyenne")
    distance: str = Field(..., description="Distance depuis le point de référence")

