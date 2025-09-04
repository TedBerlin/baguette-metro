#!/usr/bin/env python3
"""
Service Google Directions API pour calcul d'itinéraires réels
Niveau ENTREPRISE - Sécurité et éthique AI
"""

import os
import requests
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import time

# Configuration du logging
logger = logging.getLogger(__name__)

class GoogleDirectionsService:
    """Service Google Directions API pour calcul d'itinéraires"""
    
    def __init__(self):
        """Initialisation du service Google Directions"""
        self.api_key = os.getenv('GOOGLE_PLACES_API_KEY')
        self.base_url = "https://maps.googleapis.com/maps/api/directions/json"
        self.max_requests_per_minute = 10
        self.request_timestamps = []
        
        if not self.api_key:
            logger.warning("⚠️ Clé Google Directions API non configurée")
        else:
            logger.info("✅ Service Google Directions initialisé")
    
    def _check_rate_limit(self) -> bool:
        """Vérification du rate limiting"""
        now = time.time()
        # Nettoyer les anciennes requêtes
        self.request_timestamps = [ts for ts in self.request_timestamps if now - ts < 60]
        
        if len(self.request_timestamps) >= self.max_requests_per_minute:
            logger.warning("🚨 Rate limit Google Directions dépassé")
            return False
        
        self.request_timestamps.append(now)
        return True
    
    def calculate_route(self, 
                       origin: str, 
                       destination: str, 
                       mode: str = "transit",
                       language: str = "fr") -> Optional[Dict]:
        """
        Calcule un itinéraire réel via Google Directions API
        
        Args:
            origin: Adresse de départ
            destination: Adresse d'arrivée
            mode: Mode de transport (transit, driving, walking, bicycling)
            language: Langue des résultats (fr, en, ja)
        
        Returns:
            Dict avec les informations d'itinéraire ou None si erreur
        """
        if not self.api_key:
            logger.warning("⚠️ Clé API manquante pour Google Directions")
            return None
        
        if not self._check_rate_limit():
            logger.warning("⚠️ Rate limit dépassé, utilisation du fallback")
            return None
        
        try:
            logger.info(f"🔄 Calcul itinéraire Google: {origin} → {destination} ({mode})")
            
            params = {
                'origin': origin,
                'destination': destination,
                'mode': mode,
                'language': language,
                'key': self.api_key,
                'transit_mode': 'bus|subway|train|tram',
                'alternatives': 'true'
            }
            
            response = requests.get(
                self.base_url,
                params=params,
                timeout=15,
                headers={
                    'User-Agent': 'BaguetteMetro/1.0 (Enterprise)',
                    'Accept': 'application/json'
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('status') == 'OK':
                    logger.info("✅ Itinéraire Google Directions calculé avec succès")
                    return self._process_directions_response(data, origin, destination)
                else:
                    logger.warning(f"⚠️ Erreur Google Directions: {data.get('status')} - {data.get('error_message', 'N/A')}")
                    return None
            else:
                logger.error(f"❌ Erreur HTTP Google Directions: {response.status_code}")
                return None
                
        except requests.exceptions.Timeout:
            logger.error("❌ Timeout Google Directions API")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Erreur requête Google Directions: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Erreur inattendue Google Directions: {e}")
            return None
    
    def _process_directions_response(self, data: Dict, origin: str, destination: str) -> Dict:
        """Traite la réponse de l'API Google Directions"""
        try:
            routes = data.get('routes', [])
            if not routes:
                return None
            
            # Prendre la route optimale (première)
            best_route = routes[0]
            legs = best_route.get('legs', [])
            if not legs:
                return None
            
            leg = legs[0]
            
            # Extraction des informations principales
            route_info = {
                "origin": origin,
                "destination": destination,
                "total_distance": leg.get('distance', {}).get('text', 'N/A'),
                "total_duration": leg.get('duration', {}).get('text', 'N/A'),
                "total_duration_seconds": leg.get('duration', {}).get('value', 0),
                "steps": [],
                "transport_modes": set(),
                "waypoints": []
            }
            
            # Traitement des étapes
            steps = leg.get('steps', [])
            for step in steps:
                step_info = {
                    "instruction": step.get('html_instructions', 'N/A'),
                    "distance": step.get('distance', {}).get('text', 'N/A'),
                    "duration": step.get('duration', {}).get('text', 'N/A'),
                    "travel_mode": step.get('travel_mode', 'N/A'),
                    "transit_details": step.get('transit_details', {})
                }
                
                # Ajout des détails de transport
                if step.get('travel_mode') == 'TRANSIT':
                    transit = step.get('transit_details', {})
                    if transit:
                        line_info = transit.get('line', {})
                        step_info["line_name"] = line_info.get('name', 'N/A')
                        step_info["line_short_name"] = line_info.get('short_name', 'N/A')
                        step_info["departure_stop"] = transit.get('departure_stop', {}).get('name', 'N/A')
                        step_info["arrival_stop"] = transit.get('arrival_stop', {}).get('name', 'N/A')
                        step_info["departure_time"] = transit.get('departure_time', {}).get('text', 'N/A')
                        step_info["arrival_time"] = transit.get('arrival_time', {}).get('text', 'N/A')
                        
                        # Ajouter le mode de transport
                        route_info["transport_modes"].add(line_info.get('vehicle', {}).get('type', 'transit'))
                
                route_info["steps"].append(step_info)
                
                # Ajouter les waypoints pour la carte
                if step.get('start_location'):
                    start_loc = step['start_location']
                    route_info["waypoints"].append({
                        "lat": start_loc.get('lat'),
                        "lng": start_loc.get('lng'),
                        "type": "start"
                    })
                
                if step.get('end_location'):
                    end_loc = step['end_location']
                    route_info["waypoints"].append({
                        "lat": end_loc.get('lat'),
                        "lng": end_loc.get('lng'),
                        "type": "end"
                    })
            
            # Conversion des sets en listes pour la sérialisation JSON
            route_info["transport_modes"] = list(route_info["transport_modes"])
            
            logger.info(f"✅ Itinéraire traité: {len(route_info['steps'])} étapes, {route_info['total_distance']}, {route_info['total_duration']}")
            return route_info
            
        except Exception as e:
            logger.error(f"❌ Erreur traitement réponse Google Directions: {e}")
            return None
    
    def get_fallback_route(self, origin: str, destination: str, language: str = "fr") -> Dict:
        """Route de fallback intelligente avec données simulées"""
        logger.info(f"🔄 Utilisation du fallback pour: {origin} → {destination}")
        
        # Simulation d'un itinéraire RATP réaliste
        return {
            "origin": origin,
            "destination": destination,
            "total_distance": "3.2 km",
            "total_duration": "25-30 minutes",
            "total_duration_seconds": 1500,
            "steps": [
                {
                    "instruction": "Marcher vers la station de métro",
                    "distance": "200 m",
                    "duration": "3 min",
                    "travel_mode": "WALKING"
                },
                {
                    "instruction": "Prendre le RER B vers Paris",
                    "distance": "15 km",
                    "duration": "15 min",
                    "travel_mode": "TRANSIT",
                    "line_name": "RER B",
                    "line_short_name": "B",
                    "departure_stop": "Aéroport Charles de Gaulle 2",
                    "arrival_stop": "Gare du Nord"
                },
                {
                    "instruction": "Prendre le métro ligne 4",
                    "distance": "2 km",
                    "duration": "8 min",
                    "travel_mode": "TRANSIT",
                    "line_name": "Métro ligne 4",
                    "line_short_name": "4",
                    "departure_stop": "Gare du Nord",
                    "arrival_stop": "Châtelet"
                },
                {
                    "instruction": "Marcher vers la destination",
                    "distance": "500 m",
                    "duration": "6 min",
                    "travel_mode": "WALKING"
                }
            ],
            "transport_modes": ["transit", "walking"],
            "waypoints": [
                {"lat": 49.0097, "lng": 2.5479, "type": "start"},
                {"lat": 48.8809, "lng": 2.3553, "type": "end"}
            ],
            "source": "fallback_intelligent"
        }

# Instance globale du service
directions_service = GoogleDirectionsService()


