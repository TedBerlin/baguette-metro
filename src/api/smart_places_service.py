#!/usr/bin/env python3
"""
Service de géocodage intelligent pour Baguette & Métro
Utilise Google Places avec fallback optimisé vers OpenStreetMap
"""

import aiohttp
import logging
import asyncio
from typing import List, Dict, Optional
from urllib.parse import quote
import time

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SmartPlacesService:
    """Service de géocodage intelligent avec cache et optimisation"""
    
    def __init__(self):
        self.google_api_key = "AIzaSyAkduNd1Rgwqaw8l5uODMZ8R2KIbLsE3aU"
        self.google_base_url = "https://maps.googleapis.com/maps/api/place"
        self.nominatim_url = "https://nominatim.openstreetmap.org"
        
        # Cache simple en mémoire pour optimiser les performances
        self.cache = {}
        self.cache_ttl = 3600  # 1 heure
        
        # Statistiques d'utilisation
        self.stats = {
            'google_requests': 0,
            'nominatim_requests': 0,
            'cache_hits': 0,
            'total_requests': 0
        }
    
    async def autocomplete_address(self, query: str, limit: int = 5) -> List[Dict]:
        """Auto-complétion intelligente avec fallback optimisé"""
        start_time = time.time()
        
        # Vérifier le cache d'abord
        cache_key = f"autocomplete:{query.lower()}:{limit}"
        if cache_key in self.cache:
            cache_entry = self.cache[cache_key]
            if time.time() - cache_entry['timestamp'] < self.cache_ttl:
                self.stats['cache_hits'] += 1
                logger.info(f"Cache hit pour '{query}' (temps: {time.time() - start_time:.3f}s)")
                return cache_entry['data']
        
        self.stats['total_requests'] += 1
        
        try:
            # Essayer Google Places d'abord (plus rapide et pertinent)
            logger.info(f"🔄 Tentative Google Places pour '{query}'")
            google_results = await self._call_google_places(query, limit)
            
            if google_results and len(google_results) > 0:
                self.stats['google_requests'] += 1
                logger.info(f"✅ Google Places réussi: {len(google_results)} résultats (temps: {time.time() - start_time:.3f}s)")
                
                # Mettre en cache
                self.cache[cache_key] = {
                    'data': google_results,
                    'timestamp': time.time(),
                    'source': 'google'
                }
                
                return google_results
            
        except Exception as e:
            logger.warning(f"⚠️ Google Places échoué: {str(e)}")
        
        # Fallback vers OpenStreetMap avec optimisation
        try:
            logger.info(f"🔄 Fallback OpenStreetMap pour '{query}'")
            nominatim_results = await self._call_nominatim(query, limit)
            
            if nominatim_results and len(nominatim_results) > 0:
                self.stats['nominatim_requests'] += 1
                logger.info(f"✅ OpenStreetMap réussi: {len(nominatim_results)} résultats (temps: {time.time() - start_time:.3f}s)")
                
                # Mettre en cache
                self.cache[cache_key] = {
                    'data': nominatim_results,
                    'timestamp': time.time(),
                    'source': 'nominatim'
                }
                
                return nominatim_results
                
        except Exception as e:
            logger.error(f"❌ OpenStreetMap échoué: {str(e)}")
        
        # Aucun résultat
        logger.warning(f"❌ Aucun résultat pour '{query}' (temps: {time.time() - start_time:.3f}s)")
        return []
    
    async def _call_google_places(self, query: str, limit: int) -> List[Dict]:
        """Appel à l'API Google Places avec gestion d'erreur"""
        try:
            # Paramètres optimisés pour Google Places
            params = {
                'input': query,
                'key': self.google_api_key,
                'types': 'geocode',
                'language': 'fr',
                'components': 'country:fr'
            }
            
            headers = {
                'User-Agent': 'BaguetteMetro/1.0',
                'Accept': 'application/json',
                'Referer': 'https://baguette-metro.app'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.google_base_url}/autocomplete/json",
                    params=params,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    
                    if response.status != 200:
                        logger.warning(f"Google Places HTTP {response.status}")
                        return []
                    
                    data = await response.json()
                    
                    if data.get('status') != 'OK':
                        logger.warning(f"Google Places status: {data.get('status')} - {data.get('error_message', 'Unknown error')}")
                        return []
                    
                    # Formatage des résultats Google Places
                    results = []
                    for prediction in data.get('predictions', [])[:limit]:
                        results.append({
                            'place_id': prediction.get('place_id', ''),
                            'description': prediction.get('description', ''),
                            'structured_formatting': prediction.get('structured_formatting', {}),
                            'types': prediction.get('types', []),
                            'source': 'google_places'
                        })
                    
                    return results
                    
        except Exception as e:
            logger.error(f"Erreur Google Places: {str(e)}")
            return []
    
    async def _call_nominatim(self, query: str, limit: int) -> List[Dict]:
        """Appel à l'API Nominatim avec optimisation"""
        try:
            # Paramètres optimisés pour Nominatim
            params = {
                'q': query,
                'format': 'json',
                'limit': limit,
                'addressdetails': 1,
                'countrycodes': 'fr',
                'accept-language': 'fr,en',
                'dedupe': 1  # Éviter les doublons
            }
            
            headers = {
                'User-Agent': 'BaguetteMetro/1.0',
                'Accept': 'application/json'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.nominatim_url}/search",
                    params=params,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=8)
                ) as response:
                    
                    if response.status != 200:
                        logger.warning(f"Nominatim HTTP {response.status}")
                        return []
                    
                    data = await response.json()
                    
                    # Formatage et filtrage des résultats Nominatim
                    results = []
                    seen_addresses = set()
                    
                    for item in data:
                        if len(results) >= limit:
                            break
                        
                        # Éviter les doublons
                        address_key = item.get('display_name', '').lower()
                        if address_key in seen_addresses:
                            continue
                        
                        seen_addresses.add(address_key)
                        
                        # Filtrer les résultats pertinents
                        if self._is_relevant_result(item):
                            results.append({
                                'place_id': str(item.get('place_id', '')),
                                'description': item.get('display_name', ''),
                                'lat': float(item.get('lat', 0)),
                                'lon': float(item.get('lon', 0)),
                                'type': item.get('type', ''),
                                'importance': float(item.get('importance', 0)),
                                'source': 'nominatim'
                            })
                    
                    return results
                    
        except Exception as e:
            logger.error(f"Erreur Nominatim: {str(e)}")
            return []
    
    def _is_relevant_result(self, item: Dict) -> bool:
        """Filtrage intelligent des résultats Nominatim"""
        # Prioriser les résultats avec une importance élevée
        importance = float(item.get('importance', 0))
        if importance < 0.3:
            return False
        
        # Prioriser les résultats en France
        display_name = item.get('display_name', '').lower()
        if 'france' not in display_name and 'paris' not in display_name:
            return False
        
        return True
    
    def get_stats(self) -> Dict:
        """Retourne les statistiques d'utilisation"""
        return {
            **self.stats,
            'cache_size': len(self.cache),
            'cache_hit_rate': self.stats['cache_hits'] / max(self.stats['total_requests'], 1)
        }
    
    def clear_cache(self):
        """Vide le cache"""
        self.cache.clear()
        logger.info("Cache vidé")

# Instance globale du service
smart_places_service = SmartPlacesService()

