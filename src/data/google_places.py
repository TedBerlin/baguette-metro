#!/usr/bin/env python3
"""
Service Google Places API avec cache pour optimiser les performances
"""

import os
import logging
import googlemaps
from typing import List, Dict, Optional, Tuple
import time

logger = logging.getLogger(__name__)

def get_api_key(key_name: str) -> str:
    """Récupère la clé API depuis les secrets Streamlit ou les variables d'environnement"""
    try:
        import streamlit as st
        # Essayer de récupérer depuis les secrets Streamlit
        if hasattr(st, 'secrets') and hasattr(st.secrets, key_name):
            return st.secrets[key_name]
    except ImportError:
        pass
    
    # Fallback vers les variables d'environnement
    return os.getenv(key_name, '')

class GooglePlacesClient:
    """Client Google Places avec cache pour optimiser les performances"""
    
    def __init__(self):
        self.api_key = get_api_key('GOOGLE_PLACES_API_KEY')
        if not self.api_key or self.api_key == 'your_google_places_api_key_here':
            logger.warning("Google Places API key not found or invalid. Using mock data.")
            self.gmaps = None
        else:
            try:
            self.gmaps = googlemaps.Client(key=self.api_key)
            logger.info("Google Places client initialized successfully")
            except Exception as e:
                logger.warning(f"Invalid Google Places API key: {e}. Using mock data.")
                self.gmaps = None
        
        # Cache simple pour optimiser les performances
        self._cache = {}
        self._cache_ttl = 300  # 5 minutes
        self._cache_timestamps = {}
    
    def _get_cache_key(self, query: str, language: str = "fr") -> str:
        """Génère une clé de cache"""
        return f"{query.lower()}_{language}"
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Vérifie si le cache est encore valide"""
        if cache_key not in self._cache_timestamps:
            return False
        return time.time() - self._cache_timestamps[cache_key] < self._cache_ttl
    
    def _get_from_cache(self, cache_key: str) -> Optional[List[Dict]]:
        """Récupère les données du cache"""
        if cache_key in self._cache and self._is_cache_valid(cache_key):
            logger.debug(f"Cache hit for: {cache_key}")
            return self._cache[cache_key]
        return None
    
    def _save_to_cache(self, cache_key: str, data: List[Dict]):
        """Sauvegarde les données dans le cache"""
        self._cache[cache_key] = data
        self._cache_timestamps[cache_key] = time.time()
        logger.debug(f"Cached data for: {cache_key}")
    
    def autocomplete_address(self, query: str, language: str = "fr") -> List[Dict]:
        """Autocomplétion d'adresse avec cache pour optimiser les performances"""
        if not query or len(query) < 2:
            return []
        
        # Vérifier le cache d'abord
        cache_key = self._get_cache_key(query, language)
        cached_result = self._get_from_cache(cache_key)
        if cached_result:
            return cached_result
        
        # Si pas de client Google Maps, utiliser les données mock
        if not self.gmaps:
            mock_result = self._get_mock_addresses(query, language)
            self._save_to_cache(cache_key, mock_result)
            return mock_result
        
        try:
            # Test simple d'abord pour éviter le bug de la bibliothèque
            try:
                # Test avec des paramètres minimaux
                autocomplete_result = self.gmaps.places_autocomplete(
                    input_text=query,
                    language=language
                )
                
                # Si ça marche, on ajoute les paramètres progressivement
                if isinstance(autocomplete_result, list) and len(autocomplete_result) > 0:
                    # Test avec plus de paramètres
                    autocomplete_result = self.gmaps.places_autocomplete(
                        input_text=query,
                        language=language,
                        components=['country:fr']
                    )
                    
                    if isinstance(autocomplete_result, list) and len(autocomplete_result) > 0:
                        # Test complet
                        autocomplete_result = self.gmaps.places_autocomplete(
                            input_text=query,
                            language=language,
                            components=['country:fr'],
                            types=['establishment', 'geocode'],
                            location=(48.8566, 2.3522),
                            radius=50000
                        )
                
            except Exception as simple_error:
                logger.warning(f"Simple autocomplete failed, trying minimal: {simple_error}")
                # Fallback vers autocomplétion minimale
                autocomplete_result = self.gmaps.places_autocomplete(query)
            
            # Traitement des résultats
            if not isinstance(autocomplete_result, list):
                logger.warning("Invalid autocomplete result format")
                mock_result = self._get_mock_addresses(query, language)
                self._save_to_cache(cache_key, mock_result)
                return mock_result
            
            results = []
            for prediction in autocomplete_result:
                if isinstance(prediction, dict) and 'place_id' in prediction:
                    results.append({
                        'place_id': prediction['place_id'],
                        'description': prediction.get('description', ''),
                        'structured_formatting': prediction.get('structured_formatting', {})
                    })
            
            # Limiter à 5 résultats pour optimiser les performances
            results = results[:5]
            
            # Sauvegarder dans le cache
            self._save_to_cache(cache_key, results)
            
            return results

        except Exception as e:
            logger.error(f"Google Places Autocomplete API error: {e}")
            mock_result = self._get_mock_addresses(query, language)
            self._save_to_cache(cache_key, mock_result)
            return mock_result
    
    def get_address_coordinates(self, place_id: str) -> Optional[Tuple[float, float]]:
        """Récupère les coordonnées d'une adresse par place_id avec cache"""
        # Vérifier le cache d'abord
        cache_key = f"coords_{place_id}"
        cached_result = self._get_from_cache(cache_key)
        if cached_result:
            return cached_result
        
        # Si pas de client Google Maps, utiliser les données mock
        if not self.gmaps:
            mock_coords = self._get_mock_coordinates(place_id)
            if mock_coords:
                self._save_to_cache(cache_key, mock_coords)
            return mock_coords
        
        try:
            place_result = self.gmaps.place(place_id, fields=['geometry'])
            
            if place_result and 'result' in place_result:
                location = place_result['result']['geometry']['location']
                coords = (location['lat'], location['lng'])
                
                # Sauvegarder dans le cache
                self._save_to_cache(cache_key, coords)
                
                return coords
            else:
                logger.warning(f"No coordinates found for place_id: {place_id}")
                return None

        except Exception as e:
            logger.error(f"Error getting coordinates for place_id {place_id}: {e}")
            mock_coords = self._get_mock_coordinates(place_id)
            if mock_coords:
                self._save_to_cache(cache_key, mock_coords)
            return mock_coords
    
    def _get_mock_addresses(self, query: str, language: str = "fr") -> List[Dict]:
        """Données mock pour l'autocomplétion avec support multilingue"""
        query_lower = query.lower()
        
        # Données mock multilingues
        mock_data = {
            "fr": {
                "cdg": [
                    {"place_id": "mock_cdg", "description": "Aéroport Charles de Gaulle (CDG), Roissy-en-France, France", "structured_formatting": {"main_text": "Aéroport Charles de Gaulle", "secondary_text": "Roissy-en-France, France"}},
                    {"place_id": "mock_cdg_terminal", "description": "Terminal 2E, Aéroport Charles de Gaulle, Roissy-en-France", "structured_formatting": {"main_text": "Terminal 2E", "secondary_text": "Aéroport Charles de Gaulle"}}
                ],
                "tour eiffel": [
                    {"place_id": "mock_eiffel", "description": "Tour Eiffel, Champ de Mars, Paris, France", "structured_formatting": {"main_text": "Tour Eiffel", "secondary_text": "Champ de Mars, Paris"}},
                    {"place_id": "mock_eiffel_metro", "description": "Station Bir-Hakeim, Métro ligne 6, Paris", "structured_formatting": {"main_text": "Station Bir-Hakeim", "secondary_text": "Métro ligne 6, Paris"}}
                ],
                "louvre": [
                    {"place_id": "mock_louvre", "description": "Musée du Louvre, Paris, France", "structured_formatting": {"main_text": "Musée du Louvre", "secondary_text": "Paris, France"}},
                    {"place_id": "mock_louvre_metro", "description": "Station Palais Royal-Musée du Louvre, Métro lignes 1 et 7", "structured_formatting": {"main_text": "Station Palais Royal-Musée du Louvre", "secondary_text": "Métro lignes 1 et 7"}}
                ]
            },
            "en": {
                "cdg": [
                    {"place_id": "mock_cdg", "description": "Charles de Gaulle Airport (CDG), Roissy-en-France, France", "structured_formatting": {"main_text": "Charles de Gaulle Airport", "secondary_text": "Roissy-en-France, France"}},
                    {"place_id": "mock_cdg_terminal", "description": "Terminal 2E, Charles de Gaulle Airport, Roissy-en-France", "structured_formatting": {"main_text": "Terminal 2E", "secondary_text": "Charles de Gaulle Airport"}}
                ],
                "eiffel tower": [
                    {"place_id": "mock_eiffel", "description": "Eiffel Tower, Champ de Mars, Paris, France", "structured_formatting": {"main_text": "Eiffel Tower", "secondary_text": "Champ de Mars, Paris"}},
                    {"place_id": "mock_eiffel_metro", "description": "Bir-Hakeim Station, Metro line 6, Paris", "structured_formatting": {"main_text": "Bir-Hakeim Station", "secondary_text": "Metro line 6, Paris"}}
                ],
                "louvre": [
                    {"place_id": "mock_louvre", "description": "Louvre Museum, Paris, France", "structured_formatting": {"main_text": "Louvre Museum", "secondary_text": "Paris, France"}},
                    {"place_id": "mock_louvre_metro", "description": "Palais Royal-Musée du Louvre Station, Metro lines 1 and 7", "structured_formatting": {"main_text": "Palais Royal-Musée du Louvre Station", "secondary_text": "Metro lines 1 and 7"}}
                ]
            },
            "ja": {
                "cdg": [
                    {"place_id": "mock_cdg", "description": "シャルル・ド・ゴール空港（CDG）、ロワシー・アン・フランス、フランス", "structured_formatting": {"main_text": "シャルル・ド・ゴール空港", "secondary_text": "ロワシー・アン・フランス、フランス"}},
                    {"place_id": "mock_cdg_terminal", "description": "ターミナル2E、シャルル・ド・ゴール空港、ロワシー・アン・フランス", "structured_formatting": {"main_text": "ターミナル2E", "secondary_text": "シャルル・ド・ゴール空港"}}
                ],
                "エッフェル塔": [
                    {"place_id": "mock_eiffel", "description": "エッフェル塔、シャン・ド・マルス、パリ、フランス", "structured_formatting": {"main_text": "エッフェル塔", "secondary_text": "シャン・ド・マルス、パリ"}},
                    {"place_id": "mock_eiffel_metro", "description": "ビル・アケム駅、メトロ6号線、パリ", "structured_formatting": {"main_text": "ビル・アケム駅", "secondary_text": "メトロ6号線、パリ"}}
                ],
                "ルーヴル": [
                    {"place_id": "mock_louvre", "description": "ルーヴル美術館、パリ、フランス", "structured_formatting": {"main_text": "ルーヴル美術館", "secondary_text": "パリ、フランス"}},
                    {"place_id": "mock_louvre_metro", "description": "パレ・ロワイヤル・ルーヴル美術館駅、メトロ1号線・7号線", "structured_formatting": {"main_text": "パレ・ロワイヤル・ルーヴル美術館駅", "secondary_text": "メトロ1号線・7号線"}}
                ]
            }
        }
        
        # Recherche dans les données mock
        lang_data = mock_data.get(language, mock_data["fr"])
        
        for key, addresses in lang_data.items():
            if key in query_lower:
                return addresses
        
        # Fallback générique
        return [
            {"place_id": "mock_generic", "description": f"Résultat pour '{query}'", "structured_formatting": {"main_text": query, "secondary_text": "Paris, France"}}
        ]
    
    def _get_mock_coordinates(self, place_id: str) -> Optional[Tuple[float, float]]:
        """Coordonnées mock pour les place_id"""
        mock_coords = {
            "mock_cdg": (49.0097, 2.5479),
            "mock_cdg_terminal": (49.0097, 2.5479),
            "mock_eiffel": (48.8584, 2.2945),
            "mock_eiffel_metro": (48.8584, 2.2945),
            "mock_louvre": (48.8606, 2.3376),
            "mock_louvre_metro": (48.8606, 2.3376),
            "mock_generic": (48.8566, 2.3522),  # Paris centre
        }
        
        return mock_coords.get(place_id)
    
    def clear_cache(self):
        """Vide le cache (utile pour les tests)"""
        self._cache.clear()
        self._cache_timestamps.clear()
        logger.info("Google Places cache cleared")

# Instance globale pour optimiser les performances
_google_places_client = None

def get_google_places_client() -> GooglePlacesClient:
    """Retourne l'instance globale du client Google Places (singleton pattern)"""
    global _google_places_client
    if _google_places_client is None:
        _google_places_client = GooglePlacesClient()
    return _google_places_client

