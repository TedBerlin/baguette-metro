#!/usr/bin/env python3
"""
Service Mapbox pour Baguette & Métro
Géocodage ultra-rapide et précis avec API gratuite
"""

import aiohttp
import logging
import time
import os
from typing import List, Dict, Optional
from urllib.parse import quote

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MapboxService:
    """Service de géocodage Mapbox avec cache intelligent"""
    
    def __init__(self):
        # Clé API Mapbox (gratuite : 50,000 requêtes/mois)
        self.api_key = os.getenv("MAPBOX_API_KEY", "pk.eyJ1IjoiYmFndWV0dGVtZXRybyIsImEiOiJjbXh4eHh4eHh4eHh4In0.example")
        
        # URLs des APIs Mapbox
        self.base_url = "https://api.mapbox.com"
        self.geocoding_url = f"{self.base_url}/geocoding/v5/mapbox.places"
        self.directions_url = f"{self.base_url}/directions/v5/mapbox/driving"
        
        # Cache intelligent avec TTL
        self.cache = {}
        self.cache_ttl = 3600  # 1 heure (plus long car Mapbox est stable)
        
        # Statistiques et métriques
        self.stats = {
            'total_requests': 0,
            'cache_hits': 0,
            'response_times': [],
            'success_rate': 1.0,
            'last_request': None
        }
        
        # Configuration des limites
        self.limit = 5
        self.country = "FR"
        self.language = "fr"
        
        logger.info(f"🚀 Service Mapbox initialisé avec clé: {self.api_key[:20]}...")
    
    async def autocomplete_address(self, query: str, limit: int = 5) -> List[Dict]:
        """Auto-complétion ultra-rapide avec Mapbox"""
        start_time = time.time()
        self.stats['total_requests'] += 1
        self.stats['last_request'] = time.time()
        
        # Vérifier le cache d'abord
        cache_key = f"mapbox:{query.lower()}:{limit}"
        if cache_key in self.cache:
            cache_entry = self.cache[cache_key]
            if time.time() - cache_entry['timestamp'] < self.cache_ttl:
                self.stats['cache_hits'] += 1
                logger.info(f"🚀 Cache hit Mapbox pour '{query}' (temps: {time.time() - start_time:.3f}s)")
                return cache_entry['data']
        
        try:
            logger.info(f"🔄 Appel Mapbox pour '{query}'")
            
            # Paramètres optimisés pour Paris
            params = {
                'q': query,
                'access_token': self.api_key,
                'limit': limit,
                'country': self.country,
                'language': self.language,
                'types': 'poi,address,neighborhood,place',
                'bbox': '2.2241,48.8156,2.4699,48.9021',  # Paris intra-muros
                'autocomplete': 'true',
                'routing': 'true'
            }
            
            # Headers optimisés
            headers = {
                'User-Agent': 'BaguetteMetro/1.0 (https://baguette-metro.app)',
                'Accept': 'application/json',
                'Accept-Language': 'fr-FR,fr;q=0.9,en;q=0.8'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    self.geocoding_url,
                    params=params,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=2)  # Timeout très court
                ) as response:
                    
                    if response.status != 200:
                        raise Exception(f"HTTP {response.status}: {await response.text()}")
                    
                    data = await response.json()
                    
                    # Traitement des résultats
                    results = self._process_mapbox_results(data, query)
                    
                    if results:
                        # Mettre en cache
                        self.cache[cache_key] = {
                            'data': results,
                            'timestamp': time.time(),
                            'source': 'mapbox'
                        }
                        
                        # Mettre à jour les statistiques
                        response_time = time.time() - start_time
                        self.stats['response_times'].append(response_time)
                        self.stats['success_rate'] = 1.0
                        
                        logger.info(f"✅ Mapbox réussi: {len(results)} résultats (temps: {response_time:.3f}s)")
                        return results
                    else:
                        logger.warning(f"⚠️ Mapbox: aucun résultat pour '{query}'")
                        return []
                        
        except Exception as e:
            logger.error(f"❌ Erreur Mapbox pour '{query}': {str(e)}")
            self.stats['success_rate'] = 0.8  # Réduire le taux de succès
            return []
    
    def _process_mapbox_results(self, data: Dict, query: str) -> List[Dict]:
        """Traitement intelligent des résultats Mapbox"""
        features = data.get('features', [])
        results = []
        
        for feature in features:
            # Extraire les informations
            place_name = feature.get('place_name', '')
            center = feature.get('center', [0, 0])
            bbox = feature.get('bbox', [])
            relevance = feature.get('relevance', 0)
            place_type = feature.get('place_type', [])
            
            # Score de qualité intelligent
            quality_score = self._calculate_quality_score(feature, query)
            
            # Filtrer par qualité minimale
            if quality_score >= 0.6:
                result = {
                    'place_id': feature.get('id', ''),
                    'description': place_name,
                    'lat': float(center[1]),
                    'lon': float(center[0]),
                    'type': place_type[0] if place_type else 'unknown',
                    'relevance': relevance,
                    'source': 'mapbox',
                    'quality_score': quality_score,
                    'bbox': bbox,
                    'context': self._extract_context(feature)
                }
                results.append(result)
        
        # Trier par score de qualité et pertinence
        results.sort(key=lambda x: (x['quality_score'], x['relevance']), reverse=True)
        
        return results[:self.limit]
    
    def _calculate_quality_score(self, feature: Dict, query: str) -> float:
        """Calcul du score de qualité d'un résultat Mapbox"""
        score = 0.0
        
        # Pertinence Mapbox (0-1)
        relevance = float(feature.get('relevance', 0))
        score += relevance * 0.4
        
        # Type de lieu
        place_type = feature.get('place_type', [])
        if 'poi' in place_type:
            score += 0.3  # Point d'intérêt
        elif 'address' in place_type:
            score += 0.25  # Adresse
        elif 'neighborhood' in place_type:
            score += 0.2  # Quartier
        elif 'place' in place_type:
            score += 0.15  # Lieu
        
        # Localisation en France/Paris
        context = feature.get('context', [])
        country = next((ctx for ctx in context if ctx.get('id', '').startswith('country')), None)
        if country and country.get('text', '').lower() == 'france':
            score += 0.2
        
        # Code postal Paris
        postcode = next((ctx for ctx in context if ctx.get('id', '').startswith('postcode')), None)
        if postcode and '750' in postcode.get('text', ''):
            score += 0.15
        
        # Nombre de caractères (éviter les résultats trop courts)
        place_name = feature.get('place_name', '')
        if len(place_name) > 10:
            score += 0.1
        
        return min(score, 1.0)
    
    def _extract_context(self, feature: Dict) -> Dict:
        """Extraction du contexte géographique"""
        context = feature.get('context', [])
        context_info = {}
        
        for ctx in context:
            ctx_id = ctx.get('id', '')
            if ctx_id.startswith('country'):
                context_info['country'] = ctx.get('text', '')
            elif ctx_id.startswith('region'):
                context_info['region'] = ctx.get('text', '')
            elif ctx_id.startswith('postcode'):
                context_info['postcode'] = ctx.get('text', '')
            elif ctx_id.startswith('place'):
                context_info['city'] = ctx.get('text', '')
            elif ctx_id.startswith('neighborhood'):
                context_info['neighborhood'] = ctx.get('text', '')
        
        return context_info
    
    async def get_directions(self, start: Dict, end: Dict, profile: str = 'driving') -> Dict:
        """Calcul d'itinéraire avec Mapbox"""
        try:
            # Coordonnées au format Mapbox
            start_coords = f"{start['lon']},{start['lat']}"
            end_coords = f"{end['lon']},{end['lat']}"
            
            params = {
                'access_token': self.api_key,
                'geometries': 'geojson',
                'overview': 'full',
                'steps': 'true',
                'annotations': 'duration,distance',
                'language': self.language
            }
            
            url = f"{self.directions_url}/{start_coords};{end_coords}"
            
            headers = {
                'User-Agent': 'BaguetteMetro/1.0',
                'Accept': 'application/json'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url,
                    params=params,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=3)
                ) as response:
                    
                    if response.status != 200:
                        raise Exception(f"HTTP {response.status}")
                    
                    data = await response.json()
                    return self._process_directions(data)
                    
        except Exception as e:
            logger.error(f"❌ Erreur directions Mapbox: {str(e)}")
            return None
    
    def _process_directions(self, data: Dict) -> Dict:
        """Traitement des résultats d'itinéraire"""
        routes = data.get('routes', [])
        if not routes:
            return None
        
        route = routes[0]  # Meilleur itinéraire
        
        return {
            'duration': route.get('duration', 0),  # secondes
            'distance': route.get('distance', 0),  # mètres
            'geometry': route.get('geometry', {}),
            'legs': route.get('legs', []),
            'steps': self._extract_steps(route.get('legs', [])),
            'source': 'mapbox'
        }
    
    def _extract_steps(self, legs: List) -> List[Dict]:
        """Extraction des étapes de l'itinéraire"""
        steps = []
        for leg in legs:
            leg_steps = leg.get('steps', [])
            for step in leg_steps:
                steps.append({
                    'instruction': step.get('maneuver', {}).get('instruction', ''),
                    'duration': step.get('duration', 0),
                    'distance': step.get('distance', 0),
                    'way_name': step.get('name', ''),
                    'maneuver': step.get('maneuver', {})
                })
        return steps
    
    def get_stats(self) -> Dict:
        """Retourne les statistiques d'utilisation"""
        avg_response_time = 0
        if self.stats['response_times']:
            avg_response_time = sum(self.stats['response_times']) / len(self.stats['response_times'])
        
        return {
            **self.stats,
            'cache_size': len(self.cache),
            'cache_hit_rate': self.stats['cache_hits'] / max(self.stats['total_requests'], 1),
            'avg_response_time': avg_response_time,
            'api_key_status': 'active' if self.api_key and not self.api_key.endswith('example') else 'demo'
        }
    
    def clear_cache(self):
        """Vide le cache"""
        self.cache.clear()
        logger.info("Cache Mapbox vidé")
    
    def is_api_key_valid(self) -> bool:
        """Vérifie si la clé API est valide"""
        return self.api_key and not self.api_key.endswith('example')

# Instance globale du service
# mapbox_service = MapboxService()  # DÉSACTIVÉ - Remplacé par Google Places

