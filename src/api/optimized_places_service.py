#!/usr/bin/env python3
"""
Service de géocodage optimisé pour Baguette & Métro
Utilise plusieurs sources avec cache intelligent et fallback
"""

import aiohttp
import logging
import time
import asyncio
from typing import List, Dict, Optional
from urllib.parse import quote

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OptimizedPlacesService:
    """Service de géocodage optimisé avec cache et fallback intelligent"""
    
    def __init__(self):
        # Sources de géocodage
        self.sources = [
            {
                'name': 'nominatim_optimized',
                'url': 'https://nominatim.openstreetmap.org',
                'priority': 1,
                'timeout': 3,
                'enabled': True
            },
            {
                'name': 'photon_api',
                'url': 'https://photon.komoot.io',
                'priority': 2,
                'timeout': 4,
                'enabled': True
            },
            {
                'name': 'geocode_xyz',
                'url': 'https://geocode.xyz',
                'priority': 3,
                'timeout': 5,
                'enabled': True
            }
        ]
        
        # Cache intelligent avec TTL
        self.cache = {}
        self.cache_ttl = 1800  # 30 minutes
        
        # Statistiques et métriques
        self.stats = {
            'total_requests': 0,
            'cache_hits': 0,
            'source_usage': {},
            'response_times': {},
            'success_rate': {}
        }
        
        # Initialiser les statistiques
        for source in self.sources:
            self.stats['source_usage'][source['name']] = 0
            self.stats['response_times'][source['name']] = []
            self.stats['success_rate'][source['name']] = 1.0
    
    async def autocomplete_address(self, query: str, limit: int = 5) -> List[Dict]:
        """Auto-complétion optimisée avec fallback intelligent"""
        start_time = time.time()
        self.stats['total_requests'] += 1
        
        # Vérifier le cache d'abord
        cache_key = f"autocomplete:{query.lower()}:{limit}"
        if cache_key in self.cache:
            cache_entry = self.cache[cache_key]
            if time.time() - cache_entry['timestamp'] < self.cache_ttl:
                self.stats['cache_hits'] += 1
                logger.info(f"🚀 Cache hit pour '{query}' (temps: {time.time() - start_time:.3f}s)")
                return cache_entry['data']
        
        # Essayer les sources par ordre de priorité
        for source in sorted(self.sources, key=lambda x: x['priority']):
            if not source['enabled']:
                continue
                
            try:
                logger.info(f"🔄 Tentative {source['name']} pour '{query}'")
                results = await self._call_source(source, query, limit)
                
                if results and len(results) > 0:
                    # Mettre en cache
                    self.cache[cache_key] = {
                        'data': results,
                        'timestamp': time.time(),
                        'source': source['name']
                    }
                    
                    # Mettre à jour les statistiques
                    self.stats['source_usage'][source['name']] += 1
                    response_time = time.time() - start_time
                    self.stats['response_times'][source['name']].append(response_time)
                    
                    logger.info(f"✅ {source['name']} réussi: {len(results)} résultats (temps: {response_time:.3f}s)")
                    return results
                    
            except Exception as e:
                logger.warning(f"⚠️ {source['name']} échoué: {str(e)}")
                # Désactiver temporairement la source si elle échoue trop
                self._update_source_reliability(source, False)
        
        logger.warning(f"❌ Aucun résultat pour '{query}' (temps: {time.time() - start_time:.3f}s)")
        return []
    
    async def _call_source(self, source: Dict, query: str, limit: int) -> List[Dict]:
        """Appel à une source spécifique avec gestion d'erreur"""
        if source['name'] == 'nominatim_optimized':
            return await self._call_nominatim_optimized(query, limit)
        elif source['name'] == 'photon_api':
            return await self._call_photon_api(query, limit)
        elif source['name'] == 'geocode_xyz':
            return await self._call_geocode_xyz(query, limit)
        else:
            raise ValueError(f"Source inconnue: {source['name']}")
    
    async def _call_nominatim_optimized(self, query: str, limit: int) -> List[Dict]:
        """Appel optimisé à Nominatim"""
        params = {
            'q': query,
            'format': 'json',
            'limit': limit * 2,  # Demander plus pour filtrer
            'addressdetails': 1,
            'countrycodes': 'fr',
            'accept-language': 'fr,en',
            'dedupe': 1,
            'extratags': 1
        }
        
        headers = {
            'User-Agent': 'BaguetteMetro/1.0 (https://baguette-metro.app)',
            'Accept': 'application/json'
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.sources[0]['url']}/search",
                params=params,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=3)
            ) as response:
                
                if response.status != 200:
                    raise Exception(f"HTTP {response.status}")
                
                data = await response.json()
                
                # Filtrage intelligent des résultats
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
                    
                    # Filtrage par pertinence
                    if self._is_high_quality_result(item):
                        results.append({
                            'place_id': str(item.get('place_id', '')),
                            'description': item.get('display_name', ''),
                            'lat': float(item.get('lat', 0)),
                            'lon': float(item.get('lon', 0)),
                            'type': item.get('type', ''),
                            'importance': float(item.get('importance', 0)),
                            'source': 'nominatim_optimized',
                            'quality_score': self._calculate_quality_score(item)
                        })
                
                # Trier par score de qualité
                results.sort(key=lambda x: x.get('quality_score', 0), reverse=True)
                return results[:limit]
    
    async def _call_photon_api(self, query: str, limit: int) -> List[Dict]:
        """Appel à l'API Photon (Komoot)"""
        params = {
            'q': query,
            'limit': limit,
            'lang': 'fr',
            'lat': 48.8566,  # Paris
            'lon': 2.3522,
            'radius': 50000  # 50km autour de Paris
        }
        
        headers = {
            'User-Agent': 'BaguetteMetro/1.0',
            'Accept': 'application/json'
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.sources[1]['url']}/api",
                params=params,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=4)
            ) as response:
                
                if response.status != 200:
                    raise Exception(f"HTTP {response.status}")
                
                data = await response.json()
                
                results = []
                for feature in data.get('features', [])[:limit]:
                    props = feature.get('properties', {})
                    geom = feature.get('geometry', {})
                    
                    if geom.get('type') == 'Point':
                        coords = geom.get('coordinates', [0, 0])
                        results.append({
                            'place_id': str(props.get('osm_id', '')),
                            'description': props.get('name', '') + ', ' + props.get('city', ''),
                            'lat': float(coords[1]),
                            'lon': float(coords[0]),
                            'type': 'point',
                            'importance': 0.8,
                            'source': 'photon_api',
                            'quality_score': 0.8
                        })
                
                return results
    
    async def _call_geocode_xyz(self, query: str, limit: int) -> List[Dict]:
        """Appel à Geocode.xyz (fallback)"""
        params = {
            'q': query,
            'limit': limit,
            'format': 'json'
        }
        
        headers = {
            'User-Agent': 'BaguetteMetro/1.0',
            'Accept': 'application/json'
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.sources[2]['url']}/search",
                params=params,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=5)
            ) as response:
                
                if response.status != 200:
                    raise Exception(f"HTTP {response.status}")
                
                data = await response.json()
                
                results = []
                for item in data.get('features', [])[:limit]:
                    props = item.get('properties', {})
                    geom = item.get('geometry', {})
                    
                    if geom.get('type') == 'Point':
                        coords = geom.get('coordinates', [0, 0])
                        results.append({
                            'place_id': str(props.get('osm_id', '')),
                            'description': props.get('display_name', ''),
                            'lat': float(coords[1]),
                            'lon': float(coords[0]),
                            'type': 'point',
                            'importance': 0.7,
                            'source': 'geocode_xyz',
                            'quality_score': 0.7
                        })
                
                return results
    
    def _is_high_quality_result(self, item: Dict) -> bool:
        """Filtrage intelligent des résultats Nominatim"""
        # Score de qualité basé sur plusieurs critères
        importance = float(item.get('importance', 0))
        display_name = item.get('display_name', '').lower()
        
        # Critères de qualité
        quality_score = 0
        
        # Importance élevée
        if importance > 0.5:
            quality_score += 3
        elif importance > 0.3:
            quality_score += 2
        elif importance > 0.1:
            quality_score += 1
        
        # Localisation en France/Paris
        if 'france' in display_name:
            quality_score += 2
        if 'paris' in display_name:
            quality_score += 3
        if '750' in display_name:  # Code postal Paris
            quality_score += 2
        
        # Type de lieu pertinent
        place_type = item.get('type', '')
        if place_type in ['administrative', 'city', 'suburb', 'neighbourhood']:
            quality_score += 2
        
        return quality_score >= 3
    
    def _calculate_quality_score(self, item: Dict) -> float:
        """Calcul du score de qualité d'un résultat"""
        importance = float(item.get('importance', 0))
        display_name = item.get('display_name', '').lower()
        
        score = importance * 10
        
        # Bonus pour Paris
        if 'paris' in display_name:
            score += 5
        if '750' in display_name:
            score += 3
        
        return min(score, 10.0)
    
    def _update_source_reliability(self, source: Dict, success: bool):
        """Mise à jour de la fiabilité d'une source"""
        if not success:
            # Désactiver temporairement si trop d'échecs
            source['enabled'] = False
            logger.warning(f"⚠️ Source {source['name']} désactivée temporairement")
            
            # Réactiver après 5 minutes
            asyncio.create_task(self._reactivate_source(source, 300))
    
    async def _reactivate_source(self, source: Dict, delay: int):
        """Réactivation d'une source après un délai"""
        await asyncio.sleep(delay)
        source['enabled'] = True
        logger.info(f"✅ Source {source['name']} réactivée")
    
    def get_stats(self) -> Dict:
        """Retourne les statistiques d'utilisation"""
        return {
            **self.stats,
            'cache_size': len(self.cache),
            'cache_hit_rate': self.stats['cache_hits'] / max(self.stats['total_requests'], 1),
            'active_sources': [s['name'] for s in self.sources if s['enabled']]
        }
    
    def clear_cache(self):
        """Vide le cache"""
        self.cache.clear()
        logger.info("Cache vidé")

# Instance globale du service
optimized_places_service = OptimizedPlacesService()

