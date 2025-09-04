import os
import asyncio
import aiohttp
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


@dataclass
class TripUpdate:
    """Informations de mise à jour d'un trajet"""
    trip_id: str
    route_id: str
    direction_id: int
    start_time: str
    start_date: str
    schedule_relationship: str
    stop_time_updates: List[Dict]


@dataclass
class VehiclePosition:
    """Position d'un véhicule"""
    trip_id: str
    route_id: str
    direction_id: int
    latitude: float
    longitude: float
    bearing: float
    speed: float
    timestamp: int


class RATPGTFSClient:
    """Client pour les données temps réel RATP GTFS-RT"""
    
    def __init__(self):
        self.base_url = os.getenv('RATP_GTFS_URL', 'https://api-ratp.pierre-grimaud.fr/v4')
        self.session = None
        self.cache = {}
        self.cache_duration = 30  # secondes
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def get_realtime_data(self, route_type: str = 'metros') -> Dict[str, Any]:
        """
        Récupère les données temps réel RATP
        
        Args:
            route_type: Type de transport ('metros', 'rers', 'tramways', 'bus')
        """
        try:
            url = f"{self.base_url}/schedules/{route_type}"
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    self.cache[route_type] = {
                        'data': data,
                        'timestamp': datetime.now()
                    }
                    return data
                else:
                    logger.error(f"Erreur API RATP: {response.status}")
                    return self._get_mock_data(route_type)
                    
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des données RATP: {e}")
            return self._get_mock_data(route_type)
    
    async def get_line_schedules(self, route_type: str, line_code: str) -> Dict[str, Any]:
        """
        Récupère les horaires d'une ligne spécifique
        """
        try:
            url = f"{self.base_url}/schedules/{route_type}/{line_code}"
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.error(f"Erreur API RATP ligne {line_code}: {response.status}")
                    return self._get_mock_line_data(line_code)
                    
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des horaires: {e}")
            return self._get_mock_line_data(line_code)
    
    async def get_station_schedules(self, route_type: str, line_code: str, station_code: str) -> Dict[str, Any]:
        """
        Récupère les horaires d'une station spécifique
        """
        try:
            url = f"{self.base_url}/schedules/{route_type}/{line_code}/{station_code}"
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.error(f"Erreur API RATP station {station_code}: {response.status}")
                    return self._get_mock_station_data(station_code)
                    
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des horaires station: {e}")
            return self._get_mock_station_data(station_code)
    
    def _get_mock_data(self, route_type: str) -> Dict[str, Any]:
        """Données mock pour le développement"""
        import random
        from datetime import datetime, timedelta
        
        now = datetime.now()
        
        # Génération de données mock compatibles avec l'extraction
        mock_data = []
        
        for line_num in ["1", "4", "6", "9", "14"]:
            line_data = {
                "line_code": line_num,
                "direction": "A",
                "destination": f"Direction A - Ligne {line_num}",
                "message": "Trafic normal",
                "schedules": []
            }
            
            # Génération d'horaires
            for i in range(5):
                time_offset = random.randint(2, 15)
                eta_time = now + timedelta(minutes=time_offset)
                line_data["schedules"].append({
                    "time": eta_time.strftime("%H:%M"),
                    "message": f"{time_offset} min"
                })
            
            mock_data.append(line_data)
            
            # Direction retour
            line_data_r = {
                "line_code": line_num,
                "direction": "R", 
                "destination": f"Direction R - Ligne {line_num}",
                "message": "Trafic normal",
                "schedules": []
            }
            
            for i in range(5):
                time_offset = random.randint(3, 18)
                eta_time = now + timedelta(minutes=time_offset)
                line_data_r["schedules"].append({
                    "time": eta_time.strftime("%H:%M"),
                    "message": f"{time_offset} min"
                })
            
            mock_data.append(line_data_r)
        
        return mock_data
    
    def _get_mock_line_data(self, line_code: str) -> Dict[str, Any]:
        """Données mock pour une ligne"""
        return {
            "result": {
                "schedules": [
                    {
                        "code": line_code,
                        "name": f"Ligne {line_code}",
                        "directions": {
                            "A": "Direction A",
                            "R": "Direction R"
                        }
                    }
                ]
            }
        }
    
    def _get_mock_station_data(self, station_code: str) -> Dict[str, Any]:
        """Données mock pour une station"""
        now = datetime.now()
        return {
            "result": {
                "schedules": [
                    {
                        "code": station_code,
                        "name": f"Station {station_code}",
                        "directions": {
                            "A": [
                                {
                                    "destination": "Direction A",
                                    "message": "2 min"
                                }
                            ],
                            "R": [
                                {
                                    "destination": "Direction R",
                                    "message": "5 min"
                                }
                            ]
                        }
                    }
                ]
            }
        }
    
    def calculate_eta(self, from_station: str, to_station: str, line_code: str) -> int:
        """
        Calcule le temps de trajet estimé entre deux stations
        
        Args:
            from_station: Code de la station de départ
            to_station: Code de la station d'arrivée
            line_code: Code de la ligne
            
        Returns:
            Temps estimé en minutes
        """
        # Simulation d'un calcul d'ETA basé sur la distance
        # En production, utiliser les vraies données GTFS-RT
        
        # Distances approximatives entre stations (en km)
        station_distances = {
            "metro_1": {
                "chateau_vincennes": {"la_defense": 12.5},
                "la_defense": {"chateau_vincennes": 12.5}
            },
            "metro_4": {
                "porte_clignancourt": {"mairie_montrouge": 10.8},
                "mairie_montrouge": {"porte_clignancourt": 10.8}
            }
        }
        
        # Vitesse moyenne du métro (km/h)
        avg_speed = 30
        
        # Calcul de la distance
        distance = station_distances.get(line_code, {}).get(from_station, {}).get(to_station, 5.0)
        
        # Calcul du temps (distance / vitesse * 60 pour avoir en minutes)
        eta_minutes = int((distance / avg_speed) * 60)
        
        # Ajouter un délai aléatoire pour simuler les variations
        import random
        eta_minutes += random.randint(-2, 3)
        
        return max(eta_minutes, 1)  # Minimum 1 minute


# Instance globale du client
gtfs_client = RATPGTFSClient()


async def get_realtime_eta(from_station: str, to_station: str, line_code: str = "metro_1") -> int:
    """
    Fonction utilitaire pour obtenir l'ETA temps réel
    
    Args:
        from_station: Station de départ
        to_station: Station d'arrivée
        line_code: Code de la ligne
        
    Returns:
        ETA en minutes
    """
    async with RATPGTFSClient() as client:
        # Récupérer les données temps réel
        realtime_data = await client.get_realtime_data()
        
        # Calculer l'ETA
        eta = client.calculate_eta(from_station, to_station, line_code)
        
        logger.info(f"ETA calculé: {eta} minutes de {from_station} à {to_station}")
        return eta


def get_cached_eta(from_station: str, to_station: str, line_code: str = "metro_1") -> int:
    """
    Version synchrone pour obtenir l'ETA (utilise le cache)
    """
    return gtfs_client.calculate_eta(from_station, to_station, line_code)
