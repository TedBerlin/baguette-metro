#!/usr/bin/env python3
"""
Module d'intégration des données RATP
GTFS-RT (positions temps réel) + PRIM (fréquentation) + Retards historiques
"""

import os
import asyncio
import aiohttp
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import logging
import json
import sqlite3
from pathlib import Path
import requests
from dataclasses import dataclass
import hashlib

logger = logging.getLogger(__name__)

@dataclass
class GTFSVehicle:
    """Représente un véhicule GTFS-RT"""
    vehicle_id: str
    trip_id: str
    route_id: str
    latitude: float
    longitude: float
    bearing: float
    speed: float
    timestamp: int
    congestion_level: str = "UNKNOWN_CONGESTION_LEVEL"
    occupancy_status: str = "EMPTY"

@dataclass
class PRIMStation:
    """Représente les données PRIM d'une station"""
    station_id: str
    station_name: str
    line_id: str
    passenger_count: int
    timestamp: datetime
    direction: str
    period: str  # "peak", "off_peak", "night"

@dataclass
class HistoricalDelay:
    """Représente un retard historique"""
    line_id: str
    station_id: str
    delay_minutes: int
    date: datetime
    cause: str
    impact_level: str  # "low", "medium", "high"

class RATPDataIntegration:
    """Système d'intégration des données RATP"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("RATP_API_KEY")
        self.base_url = "https://api-ratp.pierre-grimaud.fr/v4"
        self.gtfs_rt_url = "https://api-ratp.pierre-grimaud.fr/v4/gtfs/rt"
        self.prim_url = "https://api-ratp.pierre-grimaud.fr/v4/prim"
        
        # Cache local pour les données
        self.cache_dir = Path("data/cache/ratp")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Base de données locale
        self.db_path = Path("data/ratp_data.db")
        self._init_database()
        
        # Configuration des métriques
        self.update_interval = 30  # secondes
        self.cache_ttl = 300  # secondes (5 minutes)
        
        logger.info("RATP Data Integration initialisé")
    
    def _init_database(self):
        """Initialise la base de données SQLite"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Table pour les véhicules GTFS-RT
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS gtfs_vehicles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    vehicle_id TEXT,
                    trip_id TEXT,
                    route_id TEXT,
                    latitude REAL,
                    longitude REAL,
                    bearing REAL,
                    speed REAL,
                    timestamp INTEGER,
                    congestion_level TEXT,
                    occupancy_status TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Table pour les données PRIM
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS prim_stations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    station_id TEXT,
                    station_name TEXT,
                    line_id TEXT,
                    passenger_count INTEGER,
                    timestamp TIMESTAMP,
                    direction TEXT,
                    period TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Table pour les retards historiques
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS historical_delays (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    line_id TEXT,
                    station_id TEXT,
                    delay_minutes INTEGER,
                    date TIMESTAMP,
                    cause TEXT,
                    impact_level TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Index pour optimiser les requêtes
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_gtfs_vehicle_id ON gtfs_vehicles(vehicle_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_gtfs_timestamp ON gtfs_vehicles(timestamp)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_prim_station_id ON prim_stations(station_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_prim_timestamp ON prim_stations(timestamp)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_delays_line_id ON historical_delays(line_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_delays_date ON historical_delays(date)")
            
            conn.commit()
            conn.close()
            
            logger.info("Base de données RATP initialisée")
            
        except Exception as e:
            logger.error(f"Erreur initialisation base de données: {e}")
    
    async def fetch_gtfs_rt_data(self) -> List[GTFSVehicle]:
        """Récupère les données GTFS-RT (positions temps réel)"""
        
        try:
            async with aiohttp.ClientSession() as session:
                # Endpoints GTFS-RT
                endpoints = [
                    f"{self.gtfs_rt_url}/metro/positions",
                    f"{self.gtfs_rt_url}/bus/positions",
                    f"{self.gtfs_rt_url}/tram/positions"
                ]
                
                vehicles = []
                
                for endpoint in endpoints:
                    try:
                        async with session.get(endpoint, timeout=10) as response:
                            if response.status == 200:
                                data = await response.json()
                                vehicles.extend(self._parse_gtfs_rt_response(data))
                            else:
                                logger.warning(f"Erreur {response.status} pour {endpoint}")
                    except Exception as e:
                        logger.error(f"Erreur récupération {endpoint}: {e}")
                
                # Sauvegarde en cache
                self._save_gtfs_cache(vehicles)
                
                # Sauvegarde en base
                self._save_gtfs_to_db(vehicles)
                
                logger.info(f"GTFS-RT: {len(vehicles)} véhicules récupérés")
                return vehicles
                
        except Exception as e:
            logger.error(f"Erreur récupération GTFS-RT: {e}")
            return []
    
    def _parse_gtfs_rt_response(self, data: Dict) -> List[GTFSVehicle]:
        """Parse la réponse GTFS-RT"""
        vehicles = []
        
        try:
            if "entity" in data:
                for entity in data["entity"]:
                    if "vehicle" in entity:
                        vehicle_data = entity["vehicle"]
                        vehicle = GTFSVehicle(
                            vehicle_id=vehicle_data.get("vehicle", {}).get("id", ""),
                            trip_id=vehicle_data.get("trip", {}).get("trip_id", ""),
                            route_id=vehicle_data.get("trip", {}).get("route_id", ""),
                            latitude=vehicle_data.get("position", {}).get("latitude", 0.0),
                            longitude=vehicle_data.get("position", {}).get("longitude", 0.0),
                            bearing=vehicle_data.get("position", {}).get("bearing", 0.0),
                            speed=vehicle_data.get("position", {}).get("speed", 0.0),
                            timestamp=vehicle_data.get("timestamp", 0),
                            congestion_level=vehicle_data.get("congestion_level", "UNKNOWN_CONGESTION_LEVEL"),
                            occupancy_status=vehicle_data.get("occupancy_status", "EMPTY")
                        )
                        vehicles.append(vehicle)
        except Exception as e:
            logger.error(f"Erreur parsing GTFS-RT: {e}")
        
        return vehicles
    
    async def fetch_prim_data(self) -> List[PRIMStation]:
        """Récupère les données PRIM (fréquentation des stations)"""
        
        try:
            async with aiohttp.ClientSession() as session:
                # Endpoints PRIM
                endpoints = [
                    f"{self.prim_url}/metro/stations",
                    f"{self.prim_url}/bus/stations",
                    f"{self.prim_url}/tram/stations"
                ]
                
                stations = []
                
                for endpoint in endpoints:
                    try:
                        async with session.get(endpoint, timeout=10) as response:
                            if response.status == 200:
                                data = await response.json()
                                stations.extend(self._parse_prim_response(data))
                            else:
                                logger.warning(f"Erreur {response.status} pour {endpoint}")
                    except Exception as e:
                        logger.error(f"Erreur récupération {endpoint}: {e}")
                
                # Sauvegarde en cache
                self._save_prim_cache(stations)
                
                # Sauvegarde en base
                self._save_prim_to_db(stations)
                
                logger.info(f"PRIM: {len(stations)} stations récupérées")
                return stations
                
        except Exception as e:
            logger.error(f"Erreur récupération PRIM: {e}")
            return []
    
    def _parse_prim_response(self, data: Dict) -> List[PRIMStation]:
        """Parse la réponse PRIM"""
        stations = []
        
        try:
            if "stations" in data:
                for station_data in data["stations"]:
                    station = PRIMStation(
                        station_id=station_data.get("id", ""),
                        station_name=station_data.get("name", ""),
                        line_id=station_data.get("line_id", ""),
                        passenger_count=station_data.get("passenger_count", 0),
                        timestamp=datetime.fromisoformat(station_data.get("timestamp", "")),
                        direction=station_data.get("direction", ""),
                        period=self._determine_period(station_data.get("timestamp", ""))
                    )
                    stations.append(station)
        except Exception as e:
            logger.error(f"Erreur parsing PRIM: {e}")
        
        return stations
    
    def _determine_period(self, timestamp_str: str) -> str:
        """Détermine la période (peak/off_peak/night)"""
        try:
            dt = datetime.fromisoformat(timestamp_str)
            hour = dt.hour
            
            if 7 <= hour <= 9 or 17 <= hour <= 19:
                return "peak"
            elif 22 <= hour or hour <= 6:
                return "night"
            else:
                return "off_peak"
        except:
            return "off_peak"
    
    def load_historical_delays(self) -> List[HistoricalDelay]:
        """Charge les retards historiques (simulation)"""
        
        # Simulation de données historiques
        delays = []
        
        # Lignes de métro principales
        lines = ["1", "4", "6", "9", "14"]
        stations = ["Chatelet", "Gare de Lyon", "Montparnasse", "Saint-Lazare", "Gare du Nord"]
        causes = ["Incident technique", "Affluence", "Maintenance", "Météo", "Grève"]
        
        # Génération de données historiques sur 30 jours
        for i in range(30):
            date = datetime.now() - timedelta(days=i)
            
            for _ in range(np.random.randint(5, 15)):  # 5-15 retards par jour
                delay = HistoricalDelay(
                    line_id=np.random.choice(lines),
                    station_id=np.random.choice(stations),
                    delay_minutes=np.random.randint(2, 30),
                    date=date,
                    cause=np.random.choice(causes),
                    impact_level=np.random.choice(["low", "medium", "high"])
                )
                delays.append(delay)
        
        # Sauvegarde en base
        self._save_delays_to_db(delays)
        
        logger.info(f"Retards historiques: {len(delays)} entrées chargées")
        return delays
    
    def _save_gtfs_cache(self, vehicles: List[GTFSVehicle]):
        """Sauvegarde les données GTFS en cache"""
        try:
            cache_file = self.cache_dir / "gtfs_rt_cache.json"
            data = {
                "timestamp": datetime.now().isoformat(),
                "vehicles": [
                    {
                        "vehicle_id": v.vehicle_id,
                        "trip_id": v.trip_id,
                        "route_id": v.route_id,
                        "latitude": v.latitude,
                        "longitude": v.longitude,
                        "bearing": v.bearing,
                        "speed": v.speed,
                        "timestamp": v.timestamp,
                        "congestion_level": v.congestion_level,
                        "occupancy_status": v.occupancy_status
                    }
                    for v in vehicles
                ]
            }
            
            with open(cache_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Erreur sauvegarde cache GTFS: {e}")
    
    def _save_prim_cache(self, stations: List[PRIMStation]):
        """Sauvegarde les données PRIM en cache"""
        try:
            cache_file = self.cache_dir / "prim_cache.json"
            data = {
                "timestamp": datetime.now().isoformat(),
                "stations": [
                    {
                        "station_id": s.station_id,
                        "station_name": s.station_name,
                        "line_id": s.line_id,
                        "passenger_count": s.passenger_count,
                        "timestamp": s.timestamp.isoformat(),
                        "direction": s.direction,
                        "period": s.period
                    }
                    for s in stations
                ]
            }
            
            with open(cache_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Erreur sauvegarde cache PRIM: {e}")
    
    def _save_gtfs_to_db(self, vehicles: List[GTFSVehicle]):
        """Sauvegarde les données GTFS en base"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            for vehicle in vehicles:
                cursor.execute("""
                    INSERT INTO gtfs_vehicles 
                    (vehicle_id, trip_id, route_id, latitude, longitude, bearing, speed, timestamp, congestion_level, occupancy_status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    vehicle.vehicle_id, vehicle.trip_id, vehicle.route_id,
                    vehicle.latitude, vehicle.longitude, vehicle.bearing,
                    vehicle.speed, vehicle.timestamp, vehicle.congestion_level,
                    vehicle.occupancy_status
                ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Erreur sauvegarde GTFS en base: {e}")
    
    def _save_prim_to_db(self, stations: List[PRIMStation]):
        """Sauvegarde les données PRIM en base"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            for station in stations:
                cursor.execute("""
                    INSERT INTO prim_stations 
                    (station_id, station_name, line_id, passenger_count, timestamp, direction, period)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    station.station_id, station.station_name, station.line_id,
                    station.passenger_count, station.timestamp, station.direction,
                    station.period
                ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Erreur sauvegarde PRIM en base: {e}")
    
    def _save_delays_to_db(self, delays: List[HistoricalDelay]):
        """Sauvegarde les retards en base"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            for delay in delays:
                cursor.execute("""
                    INSERT INTO historical_delays 
                    (line_id, station_id, delay_minutes, date, cause, impact_level)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    delay.line_id, delay.station_id, delay.delay_minutes,
                    delay.date, delay.cause, delay.impact_level
                ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Erreur sauvegarde retards en base: {e}")
    
    def get_vehicle_positions(self, route_id: Optional[str] = None) -> List[Dict]:
        """Récupère les positions des véhicules"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            if route_id:
                query = """
                    SELECT * FROM gtfs_vehicles 
                    WHERE route_id = ? 
                    ORDER BY timestamp DESC 
                    LIMIT 100
                """
                df = pd.read_sql_query(query, conn, params=[route_id])
            else:
                query = """
                    SELECT * FROM gtfs_vehicles 
                    ORDER BY timestamp DESC 
                    LIMIT 1000
                """
                df = pd.read_sql_query(query, conn)
            
            conn.close()
            
            return df.to_dict('records')
            
        except Exception as e:
            logger.error(f"Erreur récupération positions: {e}")
            return []
    
    def get_station_congestion(self, station_id: str) -> Dict:
        """Récupère la congestion d'une station"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            # Données PRIM récentes
            query = """
                SELECT AVG(passenger_count) as avg_passengers,
                       MAX(passenger_count) as max_passengers,
                       COUNT(*) as data_points
                FROM prim_stations 
                WHERE station_id = ? 
                AND timestamp > datetime('now', '-1 hour')
            """
            
            cursor = conn.cursor()
            cursor.execute(query, [station_id])
            result = cursor.fetchone()
            
            # Retards récents
            delay_query = """
                SELECT AVG(delay_minutes) as avg_delay,
                       COUNT(*) as delay_count
                FROM historical_delays 
                WHERE station_id = ? 
                AND date > datetime('now', '-7 days')
            """
            
            cursor.execute(delay_query, [station_id])
            delay_result = cursor.fetchone()
            
            conn.close()
            
            if result and delay_result:
                avg_passengers, max_passengers, data_points = result
                avg_delay, delay_count = delay_result
                
                # Calcul du niveau de congestion
                if avg_passengers and avg_passengers > 0:
                    if avg_passengers > 1000:
                        congestion_level = "HIGH"
                    elif avg_passengers > 500:
                        congestion_level = "MEDIUM"
                    else:
                        congestion_level = "LOW"
                else:
                    congestion_level = "UNKNOWN"
                
                return {
                    "station_id": station_id,
                    "congestion_level": congestion_level,
                    "avg_passengers": avg_passengers or 0,
                    "max_passengers": max_passengers or 0,
                    "data_points": data_points or 0,
                    "avg_delay_minutes": avg_delay or 0,
                    "delay_count": delay_count or 0,
                    "last_updated": datetime.now().isoformat()
                }
            
            return {"station_id": station_id, "congestion_level": "UNKNOWN"}
            
        except Exception as e:
            logger.error(f"Erreur récupération congestion: {e}")
            return {"station_id": station_id, "congestion_level": "ERROR"}
    
    def get_line_performance(self, line_id: str) -> Dict:
        """Récupère les performances d'une ligne"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            # Retards récents
            delay_query = """
                SELECT AVG(delay_minutes) as avg_delay,
                       COUNT(*) as total_delays,
                       COUNT(CASE WHEN impact_level = 'high' THEN 1 END) as high_impact_delays
                FROM historical_delays 
                WHERE line_id = ? 
                AND date > datetime('now', '-30 days')
            """
            
            cursor = conn.cursor()
            cursor.execute(delay_query, [line_id])
            result = cursor.fetchone()
            
            # Véhicules actifs
            vehicle_query = """
                SELECT COUNT(DISTINCT vehicle_id) as active_vehicles
                FROM gtfs_vehicles 
                WHERE route_id LIKE ? 
                AND timestamp > ?
            """
            
            current_time = int(datetime.now().timestamp())
            cursor.execute(vehicle_query, [f"%{line_id}%", current_time - 300])  # 5 minutes
            vehicle_result = cursor.fetchone()
            
            conn.close()
            
            if result and vehicle_result:
                avg_delay, total_delays, high_impact_delays = result
                active_vehicles = vehicle_result[0]
                
                # Calcul de la performance
                if avg_delay and avg_delay > 0:
                    if avg_delay < 5:
                        performance = "EXCELLENT"
                    elif avg_delay < 10:
                        performance = "GOOD"
                    elif avg_delay < 15:
                        performance = "FAIR"
                    else:
                        performance = "POOR"
                else:
                    performance = "UNKNOWN"
                
                return {
                    "line_id": line_id,
                    "performance": performance,
                    "avg_delay_minutes": avg_delay or 0,
                    "total_delays": total_delays or 0,
                    "high_impact_delays": high_impact_delays or 0,
                    "active_vehicles": active_vehicles or 0,
                    "last_updated": datetime.now().isoformat()
                }
            
            return {"line_id": line_id, "performance": "UNKNOWN"}
            
        except Exception as e:
            logger.error(f"Erreur récupération performance: {e}")
            return {"line_id": line_id, "performance": "ERROR"}
    
    async def start_data_collection(self):
        """Démarre la collecte continue de données"""
        logger.info("Démarrage de la collecte de données RATP")
        
        while True:
            try:
                # Collecte GTFS-RT
                await self.fetch_gtfs_rt_data()
                
                # Collecte PRIM
                await self.fetch_prim_data()
                
                # Attente avant prochaine collecte
                await asyncio.sleep(self.update_interval)
                
            except Exception as e:
                logger.error(f"Erreur collecte données: {e}")
                await asyncio.sleep(60)  # Attente plus longue en cas d'erreur

# Fonction utilitaire pour initialiser les données
def initialize_ratp_data():
    """Initialise les données RATP"""
    integration = RATPDataIntegration()
    
    # Charge les retards historiques
    integration.load_historical_delays()
    
    logger.info("Données RATP initialisées")
    return integration

if __name__ == "__main__":
    # Test du module
    async def test_ratp_integration():
        integration = RATPDataIntegration()
        
        print("🚇 Test intégration données RATP")
        print("=" * 40)
        
        # Test GTFS-RT
        print("📡 Récupération données GTFS-RT...")
        vehicles = await integration.fetch_gtfs_rt_data()
        print(f"   ✅ {len(vehicles)} véhicules récupérés")
        
        # Test PRIM
        print("👥 Récupération données PRIM...")
        stations = await integration.fetch_prim_data()
        print(f"   ✅ {len(stations)} stations récupérées")
        
        # Test retards historiques
        print("📊 Chargement retards historiques...")
        delays = integration.load_historical_delays()
        print(f"   ✅ {len(delays)} retards chargés")
        
        # Test performances
        print("📈 Test performances ligne 1...")
        performance = integration.get_line_performance("1")
        print(f"   ✅ Performance: {performance['performance']}")
        
        print("🎉 Tests terminés avec succès !")
    
    asyncio.run(test_ratp_integration())




