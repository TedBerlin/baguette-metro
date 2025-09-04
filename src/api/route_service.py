#!/usr/bin/env python3
"""
Service d'itinéraires RATP pour Baguette & Métro
Calcul d'itinéraires optimisés avec arrêts boulangerie
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import aiohttp
from dataclasses import dataclass
from enum import Enum

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TransportMode(Enum):
    """Modes de transport disponibles"""
    METRO = "metro"
    RER = "rer"
    BUS = "bus"
    TRAM = "tram"
    WALK = "walk"

@dataclass
class RouteSegment:
    """Segment d'un itinéraire"""
    mode: TransportMode
    line: str
    departure_station: str
    arrival_station: str
    departure_time: str
    arrival_time: str
    duration_minutes: int
    distance_km: float
    platform: Optional[str] = None
    direction: Optional[str] = None

@dataclass
class RouteOption:
    """Option d'itinéraire complète"""
    id: str
    segments: List[RouteSegment]
    total_duration: int
    total_distance: float
    changes_count: int
    bakery_stops: List[Dict[str, Any]]
    eco_score: float
    cost_estimate: float

class RATPRouteService:
    """Service de calcul d'itinéraires RATP avec intégration boulangeries"""
    
    def __init__(self):
        self.base_url = "https://api-ratp.pierre-grimaud.fr/v4"
        self.api_key = None  # À configurer via .env
        self.cache = {}
        self.cache_ttl = 300  # 5 minutes
        
    async def calculate_route(self, 
                            origin: str, 
                            destination: str, 
                            departure_time: Optional[str] = None,
                            include_bakeries: bool = True,
                            max_walking_distance: float = 0.5) -> List[RouteOption]:
        """
        Calcule les itinéraires optimaux avec arrêts boulangerie
        
        Args:
            origin: Point de départ (adresse ou station)
            destination: Point d'arrivée (adresse ou station)
            departure_time: Heure de départ (optionnel)
            include_bakeries: Inclure les arrêts boulangerie
            max_walking_distance: Distance max de marche (km)
        """
        try:
            # 1. Géocodage des adresses
            origin_coords = await self._geocode_address(origin)
            dest_coords = await self._geocode_address(destination)
            
            if not origin_coords or not dest_coords:
                raise ValueError("Impossible de géocoder les adresses")
            
            # 2. Recherche des stations RATP proches
            origin_stations = await self._find_nearby_stations(origin_coords, max_walking_distance)
            dest_stations = await self._find_nearby_stations(dest_coords, max_walking_distance)
            
            # 3. Calcul des itinéraires RATP
            routes = await self._calculate_ratp_routes(origin_stations, dest_stations, departure_time)
            
            # 4. Intégration des boulangeries si demandé
            if include_bakeries:
                routes = await self._integrate_bakery_stops(routes, max_walking_distance)
            
            # 5. Optimisation et tri
            optimized_routes = self._optimize_routes(routes)
            
            return optimized_routes
            
        except Exception as e:
            logger.error(f"Erreur calcul itinéraire: {e}")
            return []
    
    async def _geocode_address(self, address: str) -> Optional[Tuple[float, float]]:
        """Géocodage d'une adresse"""
        try:
            # Utilisation du service hybride existant
            from .hybrid_places_service import hybrid_places_service
            
            result = await hybrid_places_service.geocode_address(address)
            if result and "lat" in result and "lng" in result:
                return (result["lat"], result["lng"])
            return None
            
        except Exception as e:
            logger.error(f"Erreur géocodage {address}: {e}")
            return None
    
    async def _find_nearby_stations(self, coords: Tuple[float, float], max_distance: float) -> List[Dict[str, Any]]:
        """Trouve les stations RATP proches"""
        try:
            # Simulation des stations proches (à remplacer par vraie API RATP)
            stations = [
                {
                    "id": "metro_1",
                    "name": "Station Métro Proche",
                    "mode": TransportMode.METRO,
                    "lines": ["1", "4"],
                    "distance": 0.2,
                    "coordinates": coords
                },
                {
                    "id": "rer_1", 
                    "name": "Station RER Proche",
                    "mode": TransportMode.RER,
                    "lines": ["A", "B"],
                    "distance": 0.3,
                    "coordinates": coords
                }
            ]
            
            # Filtrer par distance
            return [s for s in stations if s["distance"] <= max_distance]
            
        except Exception as e:
            logger.error(f"Erreur recherche stations: {e}")
            return []
    
    async def _calculate_ratp_routes(self, 
                                   origin_stations: List[Dict], 
                                   dest_stations: List[Dict],
                                   departure_time: Optional[str]) -> List[RouteOption]:
        """Calcule les itinéraires RATP entre stations"""
        try:
            routes = []
            
            for origin_station in origin_stations:
                for dest_station in dest_stations:
                    # Calcul d'itinéraire entre deux stations
                    route = await self._calculate_station_to_station_route(
                        origin_station, dest_station, departure_time
                    )
                    if route:
                        routes.append(route)
            
            return routes
            
        except Exception as e:
            logger.error(f"Erreur calcul routes RATP: {e}")
            return []
    
    async def _calculate_station_to_station_route(self, 
                                                origin: Dict, 
                                                destination: Dict,
                                                departure_time: Optional[str]) -> Optional[RouteOption]:
        """Calcule un itinéraire entre deux stations"""
        try:
            # Simulation d'un itinéraire (à remplacer par vraie API RATP)
            segments = []
            
            # Segment 1: Métro
            if origin["mode"] == TransportMode.METRO:
                segments.append(RouteSegment(
                    mode=TransportMode.METRO,
                    line="1",
                    departure_station=origin["name"],
                    arrival_station="Station Intermédiaire",
                    departure_time="10:00",
                    arrival_time="10:05",
                    duration_minutes=5,
                    distance_km=2.0
                ))
                
                # Segment 2: Correspondance
                segments.append(RouteSegment(
                    mode=TransportMode.METRO,
                    line="4",
                    departure_station="Station Intermédiaire",
                    arrival_station=destination["name"],
                    departure_time="10:07",
                    arrival_time="10:12",
                    duration_minutes=5,
                    distance_km=1.5
                ))
            
            # Calcul des totaux
            total_duration = sum(s.duration_minutes for s in segments)
            total_distance = sum(s.distance_km for s in segments)
            changes_count = len(segments) - 1
            
            return RouteOption(
                id=f"route_{origin['id']}_{destination['id']}",
                segments=segments,
                total_duration=total_duration,
                total_distance=total_distance,
                changes_count=changes_count,
                bakery_stops=[],
                eco_score=0.9,
                cost_estimate=2.10
            )
            
        except Exception as e:
            logger.error(f"Erreur calcul segment: {e}")
            return None
    
    async def _integrate_bakery_stops(self, routes: List[RouteOption], max_walking_distance: float) -> List[RouteOption]:
        """Intègre les arrêts boulangerie dans les itinéraires"""
        try:
            from .hybrid_places_service import hybrid_places_service
            
            for route in routes:
                bakery_stops = []
                
                # Recherche de boulangeries le long du trajet
                for segment in route.segments:
                    # Point intermédiaire du segment
                    mid_point = self._calculate_midpoint(segment)
                    
                    # Recherche de boulangeries proches
                    bakeries = await hybrid_places_service.search_bakeries(
                        location=f"{mid_point[0]},{mid_point[1]}",
                        radius=500  # 500m
                    )
                    
                    if bakeries and "results" in bakeries:
                        # Sélection de la meilleure boulangerie
                        best_bakery = self._select_best_bakery(bakeries["results"])
                        if best_bakery:
                            bakery_stops.append({
                                "name": best_bakery.get("name", "Boulangerie"),
                                "address": best_bakery.get("formatted_address", ""),
                                "rating": best_bakery.get("rating", 0),
                                "location": best_bakery.get("geometry", {}).get("location", {}),
                                "segment_index": route.segments.index(segment),
                                "walking_distance": 0.2  # Estimation
                            })
                
                route.bakery_stops = bakery_stops
                
                # Ajustement du temps total avec arrêts boulangerie
                if bakery_stops:
                    route.total_duration += len(bakery_stops) * 10  # 10 min par arrêt
            
            return routes
            
        except Exception as e:
            logger.error(f"Erreur intégration boulangeries: {e}")
            return routes
    
    def _calculate_midpoint(self, segment: RouteSegment) -> Tuple[float, float]:
        """Calcule le point milieu d'un segment (simulation)"""
        # Simulation - à remplacer par vraie géométrie
        return (48.8566, 2.3522)  # Paris centre
    
    def _select_best_bakery(self, bakeries: List[Dict]) -> Optional[Dict]:
        """Sélectionne la meilleure boulangerie selon les critères"""
        if not bakeries:
            return None
        
        # Tri par note et popularité
        sorted_bakeries = sorted(
            bakeries,
            key=lambda x: (
                x.get("rating", 0),
                x.get("user_ratings_total", 0)
            ),
            reverse=True
        )
        
        return sorted_bakeries[0] if sorted_bakeries else None
    
    def _optimize_routes(self, routes: List[RouteOption]) -> List[RouteOption]:
        """Optimise et trie les itinéraires"""
        try:
            # Tri par critères multiples
            def route_score(route: RouteOption) -> float:
                # Score basé sur durée, changements, et boulangeries
                duration_score = 1.0 / (route.total_duration + 1)
                changes_penalty = route.changes_count * 0.1
                bakery_bonus = len(route.bakery_stops) * 0.05
                eco_bonus = route.eco_score * 0.1
                
                return duration_score - changes_penalty + bakery_bonus + eco_bonus
            
            # Tri par score décroissant
            sorted_routes = sorted(routes, key=route_score, reverse=True)
            
            # Limiter à 5 meilleures options
            return sorted_routes[:5]
            
        except Exception as e:
            logger.error(f"Erreur optimisation routes: {e}")
            return routes
    
    async def get_route_details(self, route_id: str) -> Optional[RouteOption]:
        """Récupère les détails d'un itinéraire"""
        try:
            # Recherche dans le cache
            if route_id in self.cache:
                cache_entry = self.cache[route_id]
                if datetime.now() < cache_entry["expiry"]:
                    return cache_entry["route"]
                else:
                    del self.cache[route_id]
            
            # Si pas en cache, recalculer
            # (implémentation à compléter selon l'architecture)
            return None
            
        except Exception as e:
            logger.error(f"Erreur récupération route {route_id}: {e}")
            return None
    
    async def get_popular_routes(self) -> List[Dict[str, Any]]:
        """Récupère les itinéraires populaires"""
        try:
            popular_routes = [
                {
                    "name": "Châtelet → République",
                    "description": "Trajet métro classique via Châtelet",
                    "origin": "Châtelet",
                    "destination": "République",
                    "estimated_duration": "15 min",
                    "lines": ["1", "4"],
                    "popularity_score": 0.9
                },
                {
                    "name": "CDG → Centre Paris",
                    "description": "Liaison aéroport RER + Métro",
                    "origin": "Aéroport Charles de Gaulle",
                    "destination": "Châtelet",
                    "estimated_duration": "45 min",
                    "lines": ["RER B", "1"],
                    "popularity_score": 0.8
                },
                {
                    "name": "Montmartre → Louvre",
                    "description": "Découverte culturelle avec arrêt boulangerie",
                    "origin": "Abbesses",
                    "destination": "Palais Royal",
                    "estimated_duration": "25 min",
                    "lines": ["2", "1"],
                    "popularity_score": 0.7
                }
            ]
            
            return popular_routes
            
        except Exception as e:
            logger.error(f"Erreur récupération routes populaires: {e}")
            return []

# Instance globale du service d'itinéraires
ratp_route_service = RATPRouteService()

