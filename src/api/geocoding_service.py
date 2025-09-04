#!/usr/bin/env python3
"""
Service de géocodage alternatif pour Baguette & Métro
Utilise OpenStreetMap comme fallback pour Google Places
"""

import aiohttp
import json
from typing import List, Dict, Optional

class GeocodingService:
    def __init__(self):
        self.nominatim_url = "https://nominatim.openstreetmap.org"
        self.user_agent = "BaguetteMetro/1.0"
        
    async def autocomplete_address(self, query: str, limit: int = 5) -> List[Dict]:
        """Auto-complétion des adresses via OpenStreetMap"""
        try:
            params = {
                'q': query,
                'format': 'json',
                'limit': limit,
                'countrycodes': 'fr',  # Limiter à la France
                'addressdetails': 1,
                'accept-language': 'fr'
            }
            
            headers = {
                'User-Agent': self.user_agent
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.nominatim_url}/search",
                    params=params,
                    headers=headers
                ) as response:
                    if response.status != 200:
                        raise Exception(f"Erreur Nominatim: {response.status}")
                    
                    data = await response.json()
                    
                    return [
                        {
                            'place_id': str(item.get('place_id', '')),
                            'description': item.get('display_name', ''),
                            'lat': float(item.get('lat', 0)),
                            'lon': float(item.get('lon', 0)),
                            'type': item.get('type', ''),
                            'importance': item.get('importance', 0)
                        }
                        for item in data
                    ]
                    
        except Exception as e:
            print(f"Erreur géocodage autocomplete: {str(e)}")
            return []
    
    async def search_bakeries(self, location: str, radius: int = 1000) -> List[Dict]:
        """Recherche de boulangeries via Overpass API (OpenStreetMap)"""
        try:
            # D'abord géocoder l'endroit
            geocode_result = await self.geocode_address(location)
            if not geocode_result:
                return []
            
            lat = geocode_result['lat']
            lon = geocode_result['lon']
            
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
                    data=overpass_query,
                    headers={'Content-Type': 'application/x-www-form-urlencoded'}
                ) as response:
                    if response.status != 200:
                        raise Exception(f"Erreur Overpass API: {response.status}")
                    
                    data = await response.json()
                    elements = data.get('elements', [])
                    
                    bakeries = []
                    for element in elements:
                        if element.get('type') == 'node' and 'tags' in element:
                            tags = element['tags']
                            if tags.get('shop') == 'bakery':
                                bakeries.append({
                                    'place_id': str(element.get('id', '')),
                                    'name': tags.get('name', 'Boulangerie'),
                                    'lat': float(element.get('lat', 0)),
                                    'lon': float(element.get('lon', 0)),
                                    'address': tags.get('addr:street', ''),
                                    'city': tags.get('addr:city', ''),
                                    'postcode': tags.get('addr:postcode', '')
                                })
                    
                    return bakeries
                    
        except Exception as e:
            print(f"Erreur recherche boulangeries: {str(e)}")
            return []
    
    async def geocode_address(self, address: str) -> Optional[Dict]:
        """Géocodage d'une adresse en coordonnées GPS"""
        try:
            params = {
                'q': address,
                'format': 'json',
                'limit': 1,
                'countrycodes': 'fr',
                'addressdetails': 1
            }
            
            headers = {
                'User-Agent': self.user_agent
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.nominatim_url}/search",
                    params=params,
                    headers=headers
                ) as response:
                    if response.status != 200:
                        raise Exception(f"Erreur Nominatim: {response.status}")
                    
                    data = await response.json()
                    
                    if data:
                        item = data[0]
                        return {
                            'lat': float(item.get('lat', 0)),
                            'lon': float(item.get('lon', 0)),
                            'formatted_address': item.get('display_name', ''),
                            'type': item.get('type', ''),
                            'importance': item.get('importance', 0)
                        }
                    
                    return None
                    
        except Exception as e:
            print(f"Erreur géocodage: {str(e)}")
            return None
    
    async def reverse_geocode(self, lat: float, lon: float) -> Optional[Dict]:
        """Géocodage inverse : coordonnées vers adresse"""
        try:
            params = {
                'lat': lat,
                'lon': lon,
                'format': 'json',
                'addressdetails': 1,
                'accept-language': 'fr'
            }
            
            headers = {
                'User-Agent': self.user_agent
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.nominatim_url}/reverse",
                    params=params,
                    headers=headers
                ) as response:
                    if response.status != 200:
                        raise Exception(f"Erreur Nominatim reverse: {response.status}")
                    
                    data = await response.json()
                    
                    if 'display_name' in data:
                        return {
                            'formatted_address': data.get('display_name', ''),
                            'lat': float(data.get('lat', 0)),
                            'lon': float(data.get('lon', 0)),
                            'address': data.get('address', {})
                        }
                    
                    return None
                    
        except Exception as e:
            print(f"Erreur géocodage inverse: {str(e)}")
            return None

# Instance globale du service
geocoding_service = GeocodingService()

