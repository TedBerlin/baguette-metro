#!/usr/bin/env python3
"""
Collecteur de données de trafic RATP
Utilise l'API RATP de Pierre Grimaud pour récupérer les données de trafic
"""

import asyncio
import aiohttp
import sqlite3
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path
import time
import random
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class TrafficInfo:
    """Information de trafic RATP"""
    line: str
    slug: str
    title: str
    message: str
    timestamp: datetime

@dataclass
class SimulatedVehicle:
    """Véhicule simulé basé sur les données de trafic"""
    vehicle_id: str
    line_id: str
    latitude: float
    longitude: float
    speed: float
    status: str
    timestamp: datetime

class RATPTrafficCollector:
    """Collecteur de données de trafic RATP"""
    
    def __init__(self):
        self.base_url = "https://api-ratp.pierre-grimaud.fr/v4"
        self.db_path = Path("data/ratp_data.db")
        self._init_database()
        
        # Configuration
        self.update_interval = 60  # secondes
        self.cache_ttl = 300  # secondes (5 minutes)
        
        # Coordonnées des lignes de métro (approximatives)
        self.line_coordinates = {
            "1": [(48.8566, 2.3522), (48.8584, 2.2945)],  # Centre Paris
            "4": [(48.8606, 2.3376), (48.8738, 2.2950)],  # Louvre à Arc de Triomphe
            "6": [(48.8867, 2.3431), (48.8517, 2.3452)],  # Sacré-Cœur à Centre
            "9": [(48.8681, 2.2943), (48.8769, 2.3437)],  # Tour Eiffel à Montmartre
            "14": [(48.8517, 2.3452), (48.8784, 2.3430)]  # Centre à Nord
        }
        
        logger.info("RATP Traffic Collector initialisé")
    
    def _init_database(self):
        """Initialise la base de données pour le trafic"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Table pour les données de trafic
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ratp_traffic (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    line_id TEXT NOT NULL,
                    slug TEXT,
                    title TEXT,
                    message TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(line_id, timestamp)
                )
            """)
            
            # Table pour les véhicules simulés
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS simulated_vehicles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    vehicle_id TEXT NOT NULL,
                    line_id TEXT,
                    latitude REAL,
                    longitude REAL,
                    speed REAL,
                    status TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Index pour les performances
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_traffic_line_time ON ratp_traffic(line_id, timestamp)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_vehicles_line_time ON simulated_vehicles(line_id, timestamp)")
            
            conn.commit()
            conn.close()
            logger.info("Base de données trafic initialisée")
            
        except Exception as e:
            logger.error(f"Erreur initialisation base trafic: {e}")
    
    async def fetch_traffic_data(self) -> Optional[Dict]:
        """Récupère les données de trafic depuis l'API RATP"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/traffic/metros", timeout=30) as response:
                    if response.status == 200:
                        data = await response.json()
                        logger.info(f"Données trafic récupérées: {len(data.get('result', {}).get('metros', []))} lignes")
                        return data
                    else:
                        logger.warning(f"Erreur API trafic: {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"Erreur récupération trafic: {e}")
            return None
    
    def parse_traffic_data(self, data: Dict) -> List[TrafficInfo]:
        """Parse les données de trafic"""
        traffic_info = []
        
        try:
            metros = data.get('result', {}).get('metros', [])
            
            for metro in metros:
                traffic = TrafficInfo(
                    line=metro.get('line', ''),
                    slug=metro.get('slug', ''),
                    title=metro.get('title', ''),
                    message=metro.get('message', ''),
                    timestamp=datetime.now()
                )
                traffic_info.append(traffic)
            
            logger.info(f"Parsé {len(traffic_info)} informations de trafic")
            return traffic_info
            
        except Exception as e:
            logger.error(f"Erreur parsing trafic: {e}")
            return []
    
    def simulate_vehicles_from_traffic(self, traffic_data: List[TrafficInfo]) -> List[SimulatedVehicle]:
        """Simule des véhicules basés sur les données de trafic"""
        vehicles = []
        
        try:
            for traffic in traffic_data:
                line_id = traffic.line
                if line_id in self.line_coordinates:
                    coords = self.line_coordinates[line_id]
                    
                    # Simuler 3-5 véhicules par ligne selon le trafic
                    vehicle_count = 3 if traffic.slug == "normal" else 5
                    
                    for i in range(vehicle_count):
                        # Position aléatoire le long de la ligne
                        progress = random.uniform(0, 1)
                        start_lat, start_lng = coords[0]
                        end_lat, end_lng = coords[1]
                        
                        lat = start_lat + (end_lat - start_lat) * progress
                        lng = start_lng + (end_lng - start_lng) * progress
                        
                        # Vitesse basée sur le statut de trafic
                        if traffic.slug == "normal":
                            speed = random.uniform(20, 40)
                        elif traffic.slug == "perturbe":
                            speed = random.uniform(5, 15)
                        else:
                            speed = random.uniform(10, 25)
                        
                        vehicle = SimulatedVehicle(
                            vehicle_id=f"RATP_{line_id}_{i+1:03d}",
                            line_id=line_id,
                            latitude=lat + random.uniform(-0.005, 0.005),
                            longitude=lng + random.uniform(-0.005, 0.005),
                            speed=speed,
                            status=traffic.slug,
                            timestamp=datetime.now()
                        )
                        vehicles.append(vehicle)
            
            logger.info(f"Simulé {len(vehicles)} véhicules basés sur le trafic")
            return vehicles
            
        except Exception as e:
            logger.error(f"Erreur simulation véhicules: {e}")
            return []
    
    def save_traffic_data(self, traffic_data: List[TrafficInfo]) -> int:
        """Sauvegarde les données de trafic"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            saved_count = 0
            
            for traffic in traffic_data:
                try:
                    cursor.execute("""
                        INSERT OR IGNORE INTO ratp_traffic 
                        (line_id, slug, title, message, timestamp)
                        VALUES (?, ?, ?, ?, ?)
                    """, (
                        traffic.line, traffic.slug, traffic.title,
                        traffic.message, traffic.timestamp
                    ))
                    
                    if cursor.rowcount > 0:
                        saved_count += 1
                        
                except Exception as e:
                    logger.error(f"Erreur sauvegarde trafic ligne {traffic.line}: {e}")
            
            conn.commit()
            conn.close()
            
            logger.info(f"Sauvegardé {saved_count} données de trafic")
            return saved_count
            
        except Exception as e:
            logger.error(f"Erreur sauvegarde trafic: {e}")
            return 0
    
    def save_simulated_vehicles(self, vehicles: List[SimulatedVehicle]) -> int:
        """Sauvegarde les véhicules simulés"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            saved_count = 0
            
            for vehicle in vehicles:
                try:
                    cursor.execute("""
                        INSERT OR IGNORE INTO simulated_vehicles 
                        (vehicle_id, line_id, latitude, longitude, speed, status, timestamp)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        vehicle.vehicle_id, vehicle.line_id, vehicle.latitude,
                        vehicle.longitude, vehicle.speed, vehicle.status, vehicle.timestamp
                    ))
                    
                    if cursor.rowcount > 0:
                        saved_count += 1
                        
                except Exception as e:
                    logger.error(f"Erreur sauvegarde véhicule {vehicle.vehicle_id}: {e}")
            
            conn.commit()
            conn.close()
            
            logger.info(f"Sauvegardé {saved_count} véhicules simulés")
            return saved_count
            
        except Exception as e:
            logger.error(f"Erreur sauvegarde véhicules: {e}")
            return 0
    
    async def collect_once(self) -> Dict:
        """Effectue une collecte unique de données"""
        start_time = time.time()
        
        try:
            # Récupération des données de trafic
            traffic_data = await self.fetch_traffic_data()
            if not traffic_data:
                return {"success": False, "error": "Aucune donnée de trafic récupérée"}
            
            # Parsing des données
            traffic_info = self.parse_traffic_data(traffic_data)
            if not traffic_info:
                return {"success": False, "error": "Aucune information de trafic parsée"}
            
            # Sauvegarde des données de trafic
            traffic_saved = self.save_traffic_data(traffic_info)
            
            # Simulation des véhicules
            vehicles = self.simulate_vehicles_from_traffic(traffic_info)
            vehicles_saved = self.save_simulated_vehicles(vehicles)
            
            duration = time.time() - start_time
            
            return {
                "success": True,
                "traffic_lines": len(traffic_info),
                "traffic_saved": traffic_saved,
                "vehicles_simulated": len(vehicles),
                "vehicles_saved": vehicles_saved,
                "duration_seconds": round(duration, 2),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erreur collecte trafic: {e}")
            return {"success": False, "error": str(e)}
    
    async def start_collection_loop(self, duration_minutes: int = 60):
        """Démarre la boucle de collecte continue"""
        logger.info(f"Démarrage collecte trafic RATP pour {duration_minutes} minutes")
        
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)
        
        collection_count = 0
        total_traffic = 0
        total_vehicles = 0
        
        while time.time() < end_time:
            try:
                result = await self.collect_once()
                collection_count += 1
                
                if result["success"]:
                    total_traffic += result["traffic_saved"]
                    total_vehicles += result["vehicles_saved"]
                    logger.info(f"Collecte #{collection_count}: {result['traffic_saved']} trafic, {result['vehicles_saved']} véhicules en {result['duration_seconds']}s")
                else:
                    logger.warning(f"Collecte #{collection_count} échouée: {result['error']}")
                
                # Attendre avant la prochaine collecte
                await asyncio.sleep(self.update_interval)
                
            except KeyboardInterrupt:
                logger.info("Collecte interrompue par l'utilisateur")
                break
            except Exception as e:
                logger.error(f"Erreur boucle de collecte: {e}")
                await asyncio.sleep(10)
        
        logger.info(f"Collecte terminée: {collection_count} cycles, {total_traffic} trafic, {total_vehicles} véhicules total")
        return {
            "collections": collection_count,
            "total_traffic": total_traffic,
            "total_vehicles": total_vehicles,
            "duration_minutes": duration_minutes
        }

def create_traffic_collector() -> RATPTrafficCollector:
    """Factory pour créer un collecteur de trafic"""
    return RATPTrafficCollector()

# Fonction utilitaire pour test rapide
async def test_traffic_collection():
    """Test rapide de la collecte de trafic"""
    print("🧪 Test collecte trafic RATP...")
    
    collector = RATPTrafficCollector()
    result = await collector.collect_once()
    
    if result["success"]:
        print(f"✅ Collecte réussie: {result['traffic_saved']} trafic, {result['vehicles_saved']} véhicules")
    else:
        print(f"❌ Collecte échouée: {result['error']}")
    
    return result

if __name__ == "__main__":
    # Test de la collecte
    asyncio.run(test_traffic_collection())





