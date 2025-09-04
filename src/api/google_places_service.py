#!/usr/bin/env python3
"""
Service Google Places pour Baguette & Métro
Auto-complétion des adresses et recherche de boulangeries
"""

import requests
import os
import logging
from typing import Dict, List, Optional
import time

# Configuration du logging
logger = logging.getLogger(__name__)

class GooglePlacesService:
    def __init__(self):
        self.api_key = os.getenv('GOOGLE_PLACES_API_KEY')
        self.base_url = "https://maps.googleapis.com/maps/api"
        self.max_requests_per_minute = 10
        self.request_timestamps = []
        
        if not self.api_key:
            logger.warning("⚠️ Clé Google Places API non configurée")
        else:
            logger.info("✅ Service Google Places initialisé")
    
    def _check_rate_limit(self) -> bool:
        """Vérification du rate limiting"""
        now = time.time()
        # Nettoyer les anciennes requêtes
        self.request_timestamps = [ts for ts in self.request_timestamps if now - ts < 60]
        
        if len(self.request_timestamps) >= self.max_requests_per_minute:
            logger.warning("🚨 Rate limit Google Places dépassé")
            return False
        
        self.request_timestamps.append(now)
        return True
    
    def autocomplete_address(self, input_text: str, session_token: str = None) -> list:
        """Auto-complétion des adresses"""
        if not self.api_key:
            logger.error("Clé API Google Places non configurée pour l'autocomplétion")
            return []
        
        if not self._check_rate_limit():
            return []

        try:
            params = {
                'input': input_text,
                'key': self.api_key,
                'types': 'geocode',
                'components': 'country:fr',  # Limiter à la France
                'language': 'fr'
            }
            
            if session_token:
                params['sessiontoken'] = session_token
            
            # Headers avec referer pour contourner la restriction
            headers = {
                'User-Agent': 'BaguetteMetro/1.0',
                'Referer': 'http://127.0.0.1:8000',
                'Origin': 'http://127.0.0.1:8000'
            }
            
            response = requests.get(
                f"{self.base_url}/autocomplete/json",
                params=params,
                headers=headers,
                timeout=10
            )
            
            if response.status_code != 200:
                logger.error(f"Erreur API Google Places pour l'autocomplétion: {response.status_code}")
                return []
            
            data = response.json()
            predictions = data.get('predictions', [])
            
            return [
                {
                    'place_id': pred['place_id'],
                    'description': pred['description'],
                    'structured_formatting': pred.get('structured_formatting', {})
                }
                for pred in predictions
            ]
            
        except Exception as e:
            logger.error(f"Erreur Google Places autocomplete: {str(e)}")
            return []
    
    def search_bakeries(self, location: str, radius: int = 1000) -> list:
        """Recherche de boulangeries près d'un endroit"""
        if not self.api_key:
            logger.error("Clé API Google Places non configurée pour la recherche de boulangeries")
            return []
        
        if not self._check_rate_limit():
            return []

        try:
            # D'abord géocoder l'endroit
            geocode_result = self.geocode_address(location)
            if not geocode_result:
                return []
            
            lat = geocode_result['lat']
            lng = geocode_result['lng']
            
            # Recherche de boulangeries
            params = {
                'location': f"{lat},{lng}",
                'radius': radius,
                'type': 'bakery',
                'keyword': 'boulangerie',
                'key': self.api_key,
                'language': 'fr'
            }
            
            # Headers avec referer
            headers = {
                'User-Agent': 'BaguetteMetro/1.0',
                'Referer': 'http://127.0.0.1:8000',
                'Origin': 'http://127.0.0.1:8000'
            }
            
            response = requests.get(
                f"{self.base_url}/place/nearbysearch/json",
                params=params,
                headers=headers,
                timeout=15
            )
            
            if response.status_code != 200:
                logger.error(f"Erreur API Google Places pour la recherche de boulangeries: {response.status_code}")
                return []
            
            data = response.json()
            results = data.get('results', [])
            
            return [
                {
                    'place_id': place['place_id'],
                    'name': place['name'],
                    'rating': place.get('rating', 0),
                    'vicinity': place.get('vicinity', ''),
                    'geometry': place.get('geometry', {}),
                    'opening_hours': place.get('opening_hours', {}),
                    'photos': place.get('photos', [])
                }
                for place in results
            ]
            
        except Exception as e:
            logger.error(f"Erreur Google Places search bakeries: {str(e)}")
            return []
    
    def geocode_address(self, address: str) -> Optional[Dict]:
        """Géocode une adresse via Google Geocoding API"""
        if not self.api_key:
            logger.error("Clé API Google Places non configurée pour le géocodage")
            return None
        
        if not self._check_rate_limit():
            return None

        try:
            params = {
                'address': address,
                'key': self.api_key,
                'components': 'country:fr',
                'language': 'fr'
            }
            
            # Headers avec referer
            headers = {
                'User-Agent': 'BaguetteMetro/1.0',
                'Referer': 'http://127.0.0.1:8000',
                'Origin': 'http://127.0.0.1:8000'
            }
            
            response = requests.get(
                f"{self.base_url}/geocode/json",
                params=params,
                headers=headers,
                timeout=10
            )
            
            if response.status_code != 200:
                logger.error(f"Erreur API Google Places pour le géocodage: {response.status_code}")
                return None
            
            data = response.json()
            results = data.get('results', [])
            
            if results:
                location = results[0]['geometry']['location']
                return {
                    'lat': location['lat'],
                    'lng': location['lng'],
                    'formatted_address': results[0]['formatted_address']
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Erreur Google Places geocode: {str(e)}")
            return None
    
    def get_place_details(self, place_id: str) -> dict:
        """Récupération des détails d'un lieu"""
        if not self.api_key:
            logger.error("Clé API Google Places non configurée pour les détails du lieu")
            return {}
        
        if not self._check_rate_limit():
            return {}

        try:
            params = {
                'place_id': place_id,
                'key': self.api_key,
                'language': 'fr'
            }
            
            headers = {
                'User-Agent': 'BaguetteMetro/1.0',
                'Referer': 'http://127.0.0.1:8000',
                'Origin': 'http://127.0.0.1:8000'
            }
            
            response = requests.get(
                f"{self.base_url}/place/details/json",
                params=params,
                headers=headers,
                timeout=10
            )
            
            if response.status_code != 200:
                logger.error(f"Erreur API Google Places pour les détails du lieu: {response.status_code}")
                return {}
            
            data = response.json()
            result = data.get('result', {})
            
            return {
                'name': result.get('name', ''),
                'formatted_address': result.get('formatted_address', ''),
                'geometry': result.get('geometry', {}),
                'rating': result.get('rating', 0),
                'opening_hours': result.get('opening_hours', {}),
                'website': result.get('website', ''),
                'formatted_phone_number': result.get('formatted_phone_number', '')
            }
            
        except Exception as e:
            logger.error(f"Erreur Google Places details: {str(e)}")
            return {}
    
    def search_bakeries_along_route(self, origin: str, destination: str, max_distance: int = 2000) -> list:
        """
        Recherche de boulangeries le long d'un itinéraire
        
        Args:
            origin: Adresse de départ
            destination: Adresse d'arrivée
            max_distance: Distance maximale en mètres depuis l'itinéraire
        
        Returns:
            Liste des boulangeries trouvées avec critères de qualité
        """
        try:
            if not self.api_key:
                logger.warning("⚠️ Clé API Google Places non configurée")
                return []
            
            if not self._check_rate_limit():
                logger.warning("⚠️ Rate limit dépassé, utilisation du fallback")
                return []
            
            logger.info(f"🥖 Recherche boulangeries le long de l'itinéraire: {origin} → {destination}")
            
            # Géocoder les deux points
            origin_geo = self.geocode_address(origin)
            dest_geo = self.geocode_address(destination)
            
            if not origin_geo or not dest_geo:
                logger.warning("⚠️ Impossible de géocoder les adresses")
                return []
            
            # Calculer le point central de l'itinéraire
            center_lat = (origin_geo['lat'] + dest_geo['lat']) / 2
            center_lng = (origin_geo['lng'] + dest_geo['lng']) / 2
            
            # Calculer la distance totale de l'itinéraire
            route_distance = self._calculate_distance(
                origin_geo['lat'], origin_geo['lng'],
                dest_geo['lat'], dest_geo['lng']
            )
            
            # Ajuster le rayon de recherche selon la distance de l'itinéraire
            search_radius = min(max_distance, max(1000, route_distance * 0.3))
            
            # Recherche de boulangeries autour du centre
            params = {
                'location': f"{center_lat},{center_lng}",
                'radius': search_radius,
                'type': 'bakery',
                'keyword': 'boulangerie artisanale',
                'key': self.api_key,
                'language': 'fr',
                'rankby': 'rating'  # Trier par note
            }
            
            headers = {
                'User-Agent': 'BaguetteMetro/1.0 (Enterprise)',
                'Referer': 'http://127.0.0.1:8000',
                'Origin': 'http://127.0.0.1:8000'
            }
            
            response = requests.get(
                f"{self.base_url}/place/nearbysearch/json",
                params=params,
                headers=headers,
                timeout=15
            )
            
            if response.status_code != 200:
                logger.warning(f"⚠️ Erreur API Google Places: {response.status_code}")
                return []
            
            data = response.json()
            results = data.get('results', [])
            
            if not results:
                logger.info("ℹ️ Aucune boulangerie trouvée")
                return []
            
            # Filtrer avec critères de qualité stricts
            quality_bakeries = []
            for result in results:
                rating = result.get('rating', 0)
                user_ratings = result.get('user_ratings_total', 0)
                
                # Critères de qualité : note > 4.0 et au moins 10 avis
                if rating >= 4.0 and user_ratings >= 10:
                    # Vérifier que c'est bien une boulangerie artisanale
                    name = result.get('name', '').lower()
                    
                    # Filtrer les chaînes et fast-food
                    if any(word in name for word in ['paul', 'brioche', 'kayser', 'chain', 'super']):
                        continue
                    
                    # Prioriser les vrais artisans
                    is_artisan = 'artisan' in name or 'artisanale' in name
                    if is_artisan:
                        rating += 0.3  # Bonus pour les artisans
                    
                    bakery = {
                        'place_id': result['place_id'],
                        'name': result['name'],
                        'rating': round(rating, 1),
                        'user_ratings_total': user_ratings,
                        'vicinity': result.get('vicinity', ''),
                        'geometry': result.get('geometry', {}),
                        'types': result.get('types', []),
                        'price_level': result.get('price_level', 0),
                        'opening_hours': result.get('opening_hours', {}).get('open_now', True),
                        'is_artisan': is_artisan
                    }
                    
                    # Calculer la distance depuis l'itinéraire
                    if 'geometry' in result and 'location' in result['geometry']:
                        loc = result['geometry']['location']
                        distance = self._calculate_distance(
                            center_lat, center_lng, loc['lat'], loc['lng']
                        )
                        bakery['distance'] = f"{distance:.0f}m"
                        bakery['distance_meters'] = distance
                        
                        # Vérifier que c'est dans la zone de l'itinéraire
                        if distance <= max_distance:
                            quality_bakeries.append(bakery)
            
            # Trier par note (avec bonus artisan) puis par distance
            quality_bakeries.sort(key=lambda x: (x['rating'], x['distance_meters']))
            
            logger.info(f"✅ {len(quality_bakeries)} boulangeries de qualité trouvées")
            return quality_bakeries[:5]  # Retourner les 5 meilleures
                
        except Exception as e:
            logger.error(f"❌ Erreur recherche boulangeries: {e}")
            return []
    
    def _calculate_distance(self, lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        """Calcule la distance en mètres entre deux points géographiques"""
        from math import radians, cos, sin, asin, sqrt
        
        # Convertir en radians
        lat1, lng1, lat2, lng2 = map(radians, [lat1, lng1, lat2, lng2])
        
        # Différences
        dlat = lat2 - lat1
        dlng = lng2 - lng1
        
        # Formule de Haversine
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlng/2)**2
        c = 2 * asin(sqrt(a))
        
        # Rayon de la Terre en mètres
        r = 6371000
        
        return c * r

# Instance globale du service
google_places_service = GooglePlacesService()
