#!/usr/bin/env python3
"""
Collecteur GTFS-RT pour les données temps réel RATP
Récupère les positions des véhicules en temps réel
"""

import asyncio
import aiohttp
import sqlite3
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from pathlib import Path
import time
import hashlib
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)

@dataclass
class GTFSVehiclePosition:
    """Position d'un véhicule GTFS-RT"""
    vehicle_id: str
    trip_id: str
    route_id: str
    latitude: float
    longitude: float
    bearing: float
    speed: float
    timestamp: int
    congestion_level: str = "UNKNOWN"
    occupancy_status: str = "EMPTY"
    direction_id: int = 0
    start_time: str = ""
    schedule_relationship: str = "SCHEDULED"

class GTFSRTCollector:
    """Collecteur de données GTFS-RT RATP"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.base_url = "https://api-ratp.pierre-grimaud.fr/v4"
        self.gtfs_rt_url = f"{self.base_url}/gtfs/rt"
        
        # Configuration
        self.update_interval = 30  # secondes
        self.cache_ttl = 300  # secondes (5 minutes)
        self.max_retries = 3
        self.retry_delay = 5  # secondes
        
        # Base de données
        self.db_path = Path("data/ratp_data.db")
        self._init_database()
        
        # Cache pour éviter les doublons
        self.last_vehicle_positions = {}
        
        logger.info("GTFS-RT Collector initialisé")
    
    def _init_database(self):
        """Initialise la base de données pour GTFS-RT"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Table pour les positions GTFS-RT
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS gtfs_vehicles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    vehicle_id TEXT NOT NULL,
                    trip_id TEXT,
                    route_id TEXT,
                    latitude REAL,
                    longitude REAL,
                    bearing REAL,
                    speed REAL,
                    timestamp INTEGER,
                    congestion_level TEXT,
                    occupancy_status TEXT,
                    direction_id INTEGER,
                    start_time TEXT,
                    schedule_relationship TEXT,
                    collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(vehicle_id, timestamp)
                )
            """)
            
            # Index pour les performances
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_gtfs_vehicle_time ON gtfs_vehicles(vehicle_id, timestamp)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_gtfs_route_time ON gtfs_vehicles(route_id, timestamp)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_gtfs_collected_at ON gtfs_vehicles(collected_at)")
            
            conn.commit()
            conn.close()
            logger.info("Base de données GTFS-RT initialisée")
            
        except Exception as e:
            logger.error(f"Erreur initialisation base GTFS-RT: {e}")
    
    async def fetch_gtfs_rt_data(self) -> Optional[Dict]:
        """Récupère les données GTFS-RT depuis l'API RATP"""
        try:
            headers = {}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(self.gtfs_rt_url, headers=headers, timeout=30) as response:
                    if response.status == 200:
                        data = await response.json()
                        logger.info(f"Données GTFS-RT récupérées: {len(data.get('entity', []))} véhicules")
                        return data
                    else:
                        logger.warning(f"Erreur API GTFS-RT: {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"Erreur récupération GTFS-RT: {e}")
            return None
    
    def parse_gtfs_rt_data(self, data: Dict) -> List[GTFSVehiclePosition]:
        """Parse les données GTFS-RT en objets véhicules"""
        vehicles = []
        
        try:
            entities = data.get('entity', [])
            
            for entity in entities:
                vehicle = entity.get('vehicle', {})
                trip = vehicle.get('trip', {})
                position = vehicle.get('position', {})
                
                if not position.get('latitude') or not position.get('longitude'):
                    continue
                
                vehicle_pos = GTFSVehiclePosition(
                    vehicle_id=vehicle.get('vehicle', {}).get('id', ''),
                    trip_id=trip.get('trip_id', ''),
                    route_id=trip.get('route_id', ''),
                    latitude=position.get('latitude', 0.0),
                    longitude=position.get('longitude', 0.0),
                    bearing=position.get('bearing', 0.0),
                    speed=position.get('speed', 0.0),
                    timestamp=vehicle.get('timestamp', int(time.time())),
                    congestion_level=vehicle.get('congestion_level', 'UNKNOWN'),
                    occupancy_status=vehicle.get('occupancy_status', 'EMPTY'),
                    direction_id=trip.get('direction_id', 0),
                    start_time=trip.get('start_time', ''),
                    schedule_relationship=trip.get('schedule_relationship', 'SCHEDULED')
                )
                
                vehicles.append(vehicle_pos)
            
            logger.info(f"Parsé {len(vehicles)} positions véhicules")
            return vehicles
            
        except Exception as e:
            logger.error(f"Erreur parsing GTFS-RT: {e}")
            return []
    
    def save_vehicle_positions(self, vehicles: List[GTFSVehiclePosition]) -> int:
        """Sauvegarde les positions des véhicules en base"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            saved_count = 0
            
            for vehicle in vehicles:
                # Vérifier si la position a changé
                vehicle_key = f"{vehicle.vehicle_id}_{vehicle.timestamp}"
                if vehicle_key in self.last_vehicle_positions:
                    continue
                
                try:
                    cursor.execute("""
                        INSERT OR IGNORE INTO gtfs_vehicles 
                        (vehicle_id, trip_id, route_id, latitude, longitude, bearing, speed, 
                         timestamp, congestion_level, occupancy_status, direction_id, 
                         start_time, schedule_relationship)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        vehicle.vehicle_id, vehicle.trip_id, vehicle.route_id,
                        vehicle.latitude, vehicle.longitude, vehicle.bearing, vehicle.speed,
                        vehicle.timestamp, vehicle.congestion_level, vehicle.occupancy_status,
                        vehicle.direction_id, vehicle.start_time, vehicle.schedule_relationship
                    ))
                    
                    if cursor.rowcount > 0:
                        saved_count += 1
                        self.last_vehicle_positions[vehicle_key] = True
                        
                except Exception as e:
                    logger.error(f"Erreur sauvegarde véhicule {vehicle.vehicle_id}: {e}")
            
            conn.commit()
            conn.close()
            
            logger.info(f"Sauvegardé {saved_count} nouvelles positions")
            return saved_count
            
        except Exception as e:
            logger.error(f"Erreur sauvegarde positions: {e}")
            return 0
    
    def cleanup_old_data(self, hours: int = 24):
        """Nettoie les anciennes données GTFS-RT"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            cursor.execute("""
                DELETE FROM gtfs_vehicles 
                WHERE collected_at < ?
            """, (cutoff_time,))
            
            deleted_count = cursor.rowcount
            conn.commit()
            conn.close()
            
            logger.info(f"Nettoyé {deleted_count} anciennes positions")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Erreur nettoyage données: {e}")
            return 0
    
    async def collect_once(self) -> Dict:
        """Effectue une collecte unique de données GTFS-RT"""
        start_time = time.time()
        
        try:
            # Récupération des données
            data = await self.fetch_gtfs_rt_data()
            if not data:
                return {"success": False, "error": "Aucune donnée récupérée"}
            
            # Parsing des données
            vehicles = self.parse_gtfs_rt_data(data)
            if not vehicles:
                return {"success": False, "error": "Aucun véhicule parsé"}
            
            # Sauvegarde en base
            saved_count = self.save_vehicle_positions(vehicles)
            
            # Nettoyage des anciennes données (une fois par heure)
            if datetime.now().minute == 0:
                self.cleanup_old_data()
            
            duration = time.time() - start_time
            
            return {
                "success": True,
                "vehicles_fetched": len(vehicles),
                "vehicles_saved": saved_count,
                "duration_seconds": round(duration, 2),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erreur collecte GTFS-RT: {e}")
            return {"success": False, "error": str(e)}
    
    async def start_collection_loop(self, duration_minutes: int = 60):
        """Démarre la boucle de collecte continue"""
        logger.info(f"Démarrage collecte GTFS-RT pour {duration_minutes} minutes")
        
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)
        
        collection_count = 0
        total_vehicles = 0
        
        while time.time() < end_time:
            try:
                result = await self.collect_once()
                collection_count += 1
                
                if result["success"]:
                    total_vehicles += result["vehicles_saved"]
                    logger.info(f"Collecte #{collection_count}: {result['vehicles_saved']} véhicules en {result['duration_seconds']}s")
                else:
                    logger.warning(f"Collecte #{collection_count} échouée: {result['error']}")
                
                # Attendre avant la prochaine collecte
                await asyncio.sleep(self.update_interval)
                
            except KeyboardInterrupt:
                logger.info("Collecte interrompue par l'utilisateur")
                break
            except Exception as e:
                logger.error(f"Erreur boucle de collecte: {e}")
                await asyncio.sleep(self.retry_delay)
        
        logger.info(f"Collecte terminée: {collection_count} cycles, {total_vehicles} véhicules total")
        return {
            "collections": collection_count,
            "total_vehicles": total_vehicles,
            "duration_minutes": duration_minutes
        }

def create_gtfs_collector(api_key: Optional[str] = None) -> GTFSRTCollector:
    """Factory pour créer un collecteur GTFS-RT"""
    return GTFSRTCollector(api_key)

# Fonction utilitaire pour test rapide
async def test_gtfs_collection():
    """Test rapide de la collecte GTFS-RT"""
    print("🧪 Test collecte GTFS-RT...")
    
    collector = GTFSRTCollector()
    result = await collector.collect_once()
    
    if result["success"]:
        print(f"✅ Collecte réussie: {result['vehicles_saved']} véhicules")
    else:
        print(f"❌ Collecte échouée: {result['error']}")
    
    return result

if __name__ == "__main__":
    # Test de la collecte
    asyncio.run(test_gtfs_collection())




