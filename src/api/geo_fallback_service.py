#!/usr/bin/env python3
"""
Service de géocodage de fallback pour Baguette & Métro
Utilise OpenStreetMap (Nominatim) comme alternative à Google Places
"""

import aiohttp
import logging
from typing import List, Dict, Optional
from urllib.parse import quote

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GeoFallbackService:
    """Service de géocodage de fallback avec OpenStreetMap"""
    
    def __init__(self):
        self.base_url = "https://nominatim.openstreetmap.org"
        self.user_agent = "BaguetteMetro/1.0"
    
    async def autocomplete_address(self, query: str, limit: int = 5) -> List[Dict]:
        """Auto-complétion avec OpenStreetMap Nominatim"""
        try:
            # Encoder la requête pour l'URL
            encoded_query = quote(query)
            
            # Paramètres de recherche
            params = {
                'q': query,
                'format': 'json',
                'limit': limit,
                'addressdetails': 1,
                'countrycodes': 'fr',  # Priorité France
                'accept-language': 'fr,en'
            }
            
            headers = {
                'User-Agent': self.user_agent,
                'Accept': 'application/json'
            }
            
            # Appel à l'API Nominatim
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/search",
                    params=params,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    
                    if response.status != 200:
                        logger.error(f"Erreur Nominatim: {response.status}")
                        return []
                    
                    data = await response.json()
                    
                    # Formatage des résultats
                    results = []
                    for item in data[:limit]:
                        results.append({
                            'place_id': str(item.get('place_id', '')),
                            'description': item.get('display_name', ''),
                            'lat': float(item.get('lat', 0)),
                            'lon': float(item.get('lon', 0)),
                            'type': item.get('type', ''),
                            'importance': float(item.get('importance', 0))
                        })
                    
                    logger.info(f"Auto-complétion réussie: {len(results)} résultats pour '{query}'")
                    return results
                    
        except Exception as e:
            logger.error(f"Erreur auto-complétion: {str(e)}")
            return []
    
    async def geocode_address(self, address: str) -> Optional[Dict]:
        """Géocodage d'une adresse avec OpenStreetMap"""
        try:
            # Utiliser l'auto-complétion avec limite 1
            results = await self.autocomplete_address(address, limit=1)
            
            if results:
                result = results[0]
                return {
                    'lat': result['lat'],
                    'lon': result['lon'],
                    'formatted_address': result['description'],
                    'place_id': result['place_id']
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Erreur géocodage: {str(e)}")
            return None
    
    async def search_bakeries(self, location: str, radius: int = 1000) -> List[Dict]:
        """Recherche de boulangeries avec OpenStreetMap Overpass"""
        try:
            # D'abord géocoder la localisation
            coords = await self.geocode_address(location)
            if not coords:
                return []
            
            lat, lon = coords['lat'], coords['lon']
            
            # Requête Overpass pour les boulangeries
            overpass_query = f"""
            [out:json][timeout:25];
            (
              node["shop"="bakery"](around:{radius},{lat},{lon});
              way["shop"="bakery"](around:{radius},{lat},{lon});
              relation["shop"="bakery"](around:{radius},{lat},{lon});
            );
            out body;
            >;
            out skel qt;
            """
            
            overpass_url = "https://overpass-api.de/api/interpreter"
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    overpass_url,
                    data={'data': overpass_query},
                    headers={'Content-Type': 'application/x-www-form-urlencoded'},
                    timeout=aiohttp.ClientTimeout(total=15)
                ) as response:
                    
                    if response.status != 200:
                        logger.error(f"Erreur Overpass: {response.status}")
                        return []
                    
                    data = await response.json()
                    
                    # Formatage des résultats
                    bakeries = []
                    for element in data.get('elements', []):
                        if element.get('type') == 'node' and 'tags' in element:
                            tags = element['tags']
                            bakeries.append({
                                'name': tags.get('name', 'Boulangerie'),
                                'address': tags.get('addr:street', ''),
                                'place_id': str(element.get('id', '')),
                                'lat': float(element.get('lat', 0)),
                                'lon': float(element.get('lon', 0)),
                                'rating': 4.0,  # Note par défaut
                                'vicinity': tags.get('addr:city', 'Paris')
                            })
                    
                    logger.info(f"Recherche boulangeries réussie: {len(bakeries)} résultats")
                    return bakeries
                    
        except Exception as e:
            logger.error(f"Erreur recherche boulangeries: {str(e)}")
            return []

# Instance globale du service
geo_fallback_service = GeoFallbackService()

