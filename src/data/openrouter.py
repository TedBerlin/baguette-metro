#!/usr/bin/env python3
"""
Module OpenRouter pour identifier les boulangeries près des stations
"""

import os
import asyncio
import logging
from typing import Dict, List, Optional, Any
import aiohttp
import json
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class OpenRouterBakeryClient:
    """Client OpenRouter pour la recherche de boulangeries"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('OPENROUTER_API_KEY')
        self.base_url = "https://openrouter.ai/api/v1"
        self.session = None
        self.cache = {}
        self.cache_duration = timedelta(hours=1)
        
    async def __aenter__(self):
        """Contexte manager pour la session HTTP"""
        self.session = aiohttp.ClientSession(
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Fermeture de la session"""
        if self.session:
            await self.session.close()
    
    async def find_bakeries_near_station(self, station_lat: float, station_lon: float, 
                                       radius_meters: int = 500) -> List[Dict[str, Any]]:
        """
        Trouve les boulangeries près d'une station
        
        Args:
            station_lat, station_lon: Coordonnées de la station
            radius_meters: Rayon de recherche en mètres
            
        Returns:
            Liste des boulangeries trouvées
        """
        try:
            # Vérification du cache
            cache_key = f"{station_lat:.4f}_{station_lon:.4f}_{radius_meters}"
            if cache_key in self.cache:
                cached_data, cached_time = self.cache[cache_key]
                if datetime.now() - cached_time < self.cache_duration:
                    logger.info(f"📋 Utilisation du cache pour {cache_key}")
                    return cached_data
            
            # Prompt pour OpenRouter
            prompt = self._build_bakery_search_prompt(station_lat, station_lon, radius_meters)
            
            # Appel à OpenRouter
            response = await self._call_openrouter(prompt)
            
            if not response:
                logger.warning("Aucune réponse d'OpenRouter")
                return self._get_mock_bakeries(station_lat, station_lon)
            
            # Parsing de la réponse
            bakeries = self._parse_bakery_response(response, station_lat, station_lon)
            
            # Mise en cache
            self.cache[cache_key] = (bakeries, datetime.now())
            
            logger.info(f"🥖 {len(bakeries)} boulangeries trouvées près de ({station_lat}, {station_lon})")
            return bakeries
            
        except Exception as e:
            logger.error(f"❌ Erreur recherche boulangeries: {e}")
            return self._get_mock_bakeries(station_lat, station_lon)
    
    async def get_bakery_details(self, bakery_name: str, lat: float, lon: float) -> Dict[str, Any]:
        """
        Obtient les détails d'une boulangerie
        
        Args:
            bakery_name: Nom de la boulangerie
            lat, lon: Coordonnées
            
        Returns:
            Détails de la boulangerie
        """
        try:
            prompt = self._build_bakery_details_prompt(bakery_name, lat, lon)
            response = await self._call_openrouter(prompt)
            
            if response:
                return self._parse_bakery_details(response)
            else:
                return self._get_mock_bakery_details(bakery_name, lat, lon)
                
        except Exception as e:
            logger.error(f"❌ Erreur détails boulangerie: {e}")
            return self._get_mock_bakery_details(bakery_name, lat, lon)
    
    async def find_optimal_bakery_route(self, start_lat: float, start_lon: float,
                                      end_lat: float, end_lon: float) -> Dict[str, Any]:
        """
        Trouve la boulangerie optimale sur un trajet
        
        Args:
            start_lat, start_lon: Point de départ
            end_lat, end_lon: Point d'arrivée
            
        Returns:
            Informations sur la boulangerie optimale
        """
        try:
            prompt = self._build_optimal_route_prompt(start_lat, start_lon, end_lat, end_lon)
            response = await self._call_openrouter(prompt)
            
            if response:
                return self._parse_optimal_route(response)
            else:
                return self._get_mock_optimal_bakery(start_lat, start_lon, end_lat, end_lon)
                
        except Exception as e:
            logger.error(f"❌ Erreur recherche boulangerie optimale: {e}")
            return self._get_mock_optimal_bakery(start_lat, start_lon, end_lat, end_lon)
    
    async def _call_openrouter(self, prompt: str) -> Optional[str]:
        """Appelle l'API OpenRouter"""
        if not self.api_key:
            logger.warning("Clé API OpenRouter manquante")
            return None
        
        try:
            payload = {
                "model": "anthropic/claude-3.5-sonnet",
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "max_tokens": 2000,
                "temperature": 0.1
            }
            
            async with self.session.post(f"{self.base_url}/chat/completions", json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    return data['choices'][0]['message']['content']
                else:
                    logger.error(f"Erreur API OpenRouter: {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"❌ Erreur appel OpenRouter: {e}")
            return None
    
    def _build_bakery_search_prompt(self, lat: float, lon: float, radius: int) -> str:
        """Construit le prompt pour la recherche de boulangeries"""
        return f"""
        Tu es un assistant spécialisé dans la recherche de boulangeries à Paris.
        
        Coordonnées: {lat}, {lon}
        Rayon de recherche: {radius} mètres
        
        Trouve les boulangeries les plus proches et retourne les résultats au format JSON:
        {{
            "bakeries": [
                {{
                    "name": "Nom de la boulangerie",
                    "address": "Adresse complète",
                    "latitude": 48.xxxx,
                    "longitude": 2.xxxx,
                    "rating": 4.5,
                    "distance_meters": 150,
                    "specialties": ["baguette", "croissants", "pain au chocolat"],
                    "opening_hours": "7h-19h",
                    "phone": "+33 1 xx xx xx xx"
                }}
            ]
        }}
        
        Inclus uniquement des boulangeries réelles et populaires à Paris.
        Limite à 5-8 boulangeries maximum.
        """
    
    def _build_bakery_details_prompt(self, name: str, lat: float, lon: float) -> str:
        """Construit le prompt pour les détails d'une boulangerie"""
        return f"""
        Donne des détails spécifiques sur la boulangerie "{name}" située à {lat}, {lon}.
        
        Retourne au format JSON:
        {{
            "name": "{name}",
            "address": "Adresse complète",
            "latitude": {lat},
            "longitude": {lon},
            "rating": 4.5,
            "reviews_count": 150,
            "specialties": ["baguette tradition", "croissants", "pain au chocolat"],
            "opening_hours": {{
                "monday": "7h-19h",
                "tuesday": "7h-19h",
                "wednesday": "7h-19h",
                "thursday": "7h-19h",
                "friday": "7h-19h",
                "saturday": "7h-19h",
                "sunday": "8h-13h"
            }},
            "phone": "+33 1 xx xx xx xx",
            "website": "https://...",
            "price_range": "€€",
            "features": ["bio", "sans gluten", "viennoiseries"],
            "popular_items": ["Baguette tradition", "Croissant", "Pain au chocolat"]
        }}
        """
    
    def _build_optimal_route_prompt(self, start_lat: float, start_lon: float,
                                  end_lat: float, end_lon: float) -> str:
        """Construit le prompt pour la boulangerie optimale sur un trajet"""
        return f"""
        Trouve la boulangerie optimale sur le trajet entre ({start_lat}, {start_lon}) et ({end_lat}, {end_lon}).
        
        Retourne au format JSON:
        {{
            "optimal_bakery": {{
                "name": "Nom de la boulangerie",
                "address": "Adresse",
                "latitude": 48.xxxx,
                "longitude": 2.xxxx,
                "rating": 4.5,
                "distance_from_start": 800,
                "distance_to_end": 1200,
                "detour_minutes": 5,
                "recommendation": "Recommandé - Détour minimal pour excellente qualité"
            }},
            "route_optimization": {{
                "total_distance_km": 2.5,
                "original_time_minutes": 15,
                "with_bakery_time_minutes": 18,
                "time_penalty_minutes": 3,
                "quality_score": 4.8
            }}
        }}
        
        Choisis une boulangerie réelle et populaire sur le trajet.
        """
    
    def _parse_bakery_response(self, response: str, lat: float, lon: float) -> List[Dict[str, Any]]:
        """Parse la réponse de recherche de boulangeries"""
        try:
            # Extraction du JSON de la réponse
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start == -1 or json_end == 0:
                logger.warning("Format JSON non trouvé dans la réponse")
                return self._get_mock_bakeries(lat, lon)
            
            json_str = response[json_start:json_end]
            data = json.loads(json_str)
            
            return data.get('bakeries', [])
            
        except Exception as e:
            logger.error(f"❌ Erreur parsing réponse boulangeries: {e}")
            return self._get_mock_bakeries(lat, lon)
    
    def _parse_bakery_details(self, response: str) -> Dict[str, Any]:
        """Parse la réponse de détails de boulangerie"""
        try:
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start == -1 or json_end == 0:
                return self._get_mock_bakery_details("Boulangerie", 48.8566, 2.3522)
            
            json_str = response[json_start:json_end]
            return json.loads(json_str)
            
        except Exception as e:
            logger.error(f"❌ Erreur parsing détails boulangerie: {e}")
            return self._get_mock_bakery_details("Boulangerie", 48.8566, 2.3522)
    
    def _parse_optimal_route(self, response: str) -> Dict[str, Any]:
        """Parse la réponse de route optimale"""
        try:
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start == -1 or json_end == 0:
                return self._get_mock_optimal_bakery(48.8566, 2.3522, 48.8606, 2.3376)
            
            json_str = response[json_start:json_end]
            return json.loads(json_str)
            
        except Exception as e:
            logger.error(f"❌ Erreur parsing route optimale: {e}")
            return self._get_mock_optimal_bakery(48.8566, 2.3522, 48.8606, 2.3376)
    
    def _get_mock_bakeries(self, lat: float, lon: float) -> List[Dict[str, Any]]:
        """Données mock pour les boulangeries"""
        import random
        
        mock_bakeries = [
            {
                "name": "Boulangerie du Marais",
                "address": "15 rue de Rivoli, 75004 Paris",
                "latitude": lat + random.uniform(-0.01, 0.01),
                "longitude": lon + random.uniform(-0.01, 0.01),
                "rating": 4.6,
                "distance_meters": random.randint(100, 500),
                "specialties": ["baguette tradition", "croissants", "pain au chocolat"],
                "opening_hours": "7h-19h",
                "phone": "+33 1 42 78 12 34"
            },
            {
                "name": "Boulangerie Saint-Michel",
                "address": "8 boulevard Saint-Michel, 75006 Paris",
                "latitude": lat + random.uniform(-0.01, 0.01),
                "longitude": lon + random.uniform(-0.01, 0.01),
                "rating": 4.4,
                "distance_meters": random.randint(200, 600),
                "specialties": ["baguette", "viennoiseries", "pâtisseries"],
                "opening_hours": "6h30-20h",
                "phone": "+33 1 43 25 67 89"
            },
            {
                "name": "Boulangerie de la Tour",
                "address": "12 rue de la Tour, 75016 Paris",
                "latitude": lat + random.uniform(-0.01, 0.01),
                "longitude": lon + random.uniform(-0.01, 0.01),
                "rating": 4.7,
                "distance_meters": random.randint(150, 450),
                "specialties": ["pain bio", "croissants", "chocolatines"],
                "opening_hours": "7h-19h30",
                "phone": "+33 1 45 67 89 12"
            }
        ]
        
        return mock_bakeries
    
    def _get_mock_bakery_details(self, name: str, lat: float, lon: float) -> Dict[str, Any]:
        """Détails mock pour une boulangerie"""
        return {
            "name": name,
            "address": f"Adresse de {name}",
            "latitude": lat,
            "longitude": lon,
            "rating": 4.5,
            "reviews_count": 120,
            "specialties": ["baguette tradition", "croissants", "pain au chocolat"],
            "opening_hours": {
                "monday": "7h-19h",
                "tuesday": "7h-19h",
                "wednesday": "7h-19h",
                "thursday": "7h-19h",
                "friday": "7h-19h",
                "saturday": "7h-19h",
                "sunday": "8h-13h"
            },
            "phone": "+33 1 42 78 12 34",
            "website": "https://example.com",
            "price_range": "€€",
            "features": ["bio", "sans gluten"],
            "popular_items": ["Baguette tradition", "Croissant", "Pain au chocolat"]
        }
    
    def _get_mock_optimal_bakery(self, start_lat: float, start_lon: float,
                               end_lat: float, end_lon: float) -> Dict[str, Any]:
        """Boulangerie optimale mock"""
        mid_lat = (start_lat + end_lat) / 2
        mid_lon = (start_lon + end_lon) / 2
        
        return {
            "optimal_bakery": {
                "name": "Boulangerie Optimale",
                "address": "Adresse optimale",
                "latitude": mid_lat,
                "longitude": mid_lon,
                "rating": 4.6,
                "distance_from_start": 800,
                "distance_to_end": 1200,
                "detour_minutes": 5,
                "recommendation": "Recommandé - Détour minimal"
            },
            "route_optimization": {
                "total_distance_km": 2.5,
                "original_time_minutes": 15,
                "with_bakery_time_minutes": 18,
                "time_penalty_minutes": 3,
                "quality_score": 4.8
            }
        }


# Instance globale
openrouter_bakery_client = OpenRouterBakeryClient()


async def test_openrouter_bakery():
    """Test du client OpenRouter boulangerie"""
    logger.info("🧪 Test du client OpenRouter boulangerie")
    
    async with openrouter_bakery_client as client:
        # Test recherche boulangeries
        bakeries = await client.find_bakeries_near_station(48.8566, 2.3522, 500)
        print(f"🥖 Boulangeries trouvées: {len(bakeries)}")
        
        # Test détails boulangerie
        if bakeries:
            details = await client.get_bakery_details(bakeries[0]['name'], 
                                                    bakeries[0]['latitude'], 
                                                    bakeries[0]['longitude'])
            print(f"📋 Détails: {details['name']} - {details['rating']}⭐")
        
        # Test route optimale
        optimal = await client.find_optimal_bakery_route(48.8566, 2.3522, 48.8606, 2.3376)
        print(f"🎯 Boulangerie optimale: {optimal['optimal_bakery']['name']}")
    
    logger.info("✅ Test OpenRouter terminé")


if __name__ == "__main__":
    # Test du client
    asyncio.run(test_openrouter_bakery())





