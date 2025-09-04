#!/usr/bin/env python3
"""
Service GTFS-RT pour l'API RATP
Gère la collecte et l'exposition des données temps réel
"""

import asyncio
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import sqlite3
from pathlib import Path

logger = logging.getLogger(__name__)

class GTFSRTService:
    """Service pour les données GTFS-RT"""
    
    def __init__(self, db_path: str = "data/ratp_data.db"):
        self.db_path = Path(db_path)
        self.is_collecting = False
        self.collection_task = None
        
        logger.info("GTFS-RT Service initialisé")
    
    def get_vehicle_positions(self, route_id: Optional[str] = None, limit: int = 100) -> List[Dict]:
        """Récupère les positions des véhicules"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            query = """
                SELECT vehicle_id, trip_id, route_id, latitude, longitude, 
                       bearing, speed, timestamp, congestion_level, occupancy_status,
                       direction_id, start_time, schedule_relationship, collected_at
                FROM gtfs_vehicles
            """
            params = []
            
            if route_id:
                query += " WHERE route_id = ?"
                params.append(route_id)
            
            query += " ORDER BY collected_at DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            vehicles = []
            for row in rows:
                vehicle = {
                    "vehicle_id": row[0],
                    "trip_id": row[1],
                    "route_id": row[2],
                    "latitude": row[3],
                    "longitude": row[4],
                    "bearing": row[5],
                    "speed": row[6],
                    "timestamp": row[7],
                    "congestion_level": row[8],
                    "occupancy_status": row[9],
                    "direction_id": row[10],
                    "start_time": row[11],
                    "schedule_relationship": row[12],
                    "collected_at": row[13]
                }
                vehicles.append(vehicle)
            
            conn.close()
            return vehicles
            
        except Exception as e:
            logger.error(f"Erreur récupération positions véhicules: {e}")
            return []
    
    def get_vehicle_count(self, route_id: Optional[str] = None) -> int:
        """Compte le nombre de véhicules"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            query = "SELECT COUNT(*) FROM gtfs_vehicles"
            params = []
            
            if route_id:
                query += " WHERE route_id = ?"
                params.append(route_id)
            
            cursor.execute(query, params)
            count = cursor.fetchone()[0]
            
            conn.close()
            return count
            
        except Exception as e:
            logger.error(f"Erreur comptage véhicules: {e}")
            return 0
    
    def get_line_vehicles(self, line_id: str) -> List[Dict]:
        """Récupère les véhicules d'une ligne spécifique"""
        return self.get_vehicle_positions(route_id=line_id)
    
    def get_recent_vehicles(self, minutes: int = 30) -> List[Dict]:
        """Récupère les véhicules récents"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cutoff_time = datetime.now() - timedelta(minutes=minutes)
            
            cursor.execute("""
                SELECT vehicle_id, trip_id, route_id, latitude, longitude, 
                       bearing, speed, timestamp, congestion_level, occupancy_status,
                       direction_id, start_time, schedule_relationship, collected_at
                FROM gtfs_vehicles
                WHERE collected_at > ?
                ORDER BY collected_at DESC
            """, (cutoff_time,))
            
            rows = cursor.fetchall()
            
            vehicles = []
            for row in rows:
                vehicle = {
                    "vehicle_id": row[0],
                    "trip_id": row[1],
                    "route_id": row[2],
                    "latitude": row[3],
                    "longitude": row[4],
                    "bearing": row[5],
                    "speed": row[6],
                    "timestamp": row[7],
                    "congestion_level": row[8],
                    "occupancy_status": row[9],
                    "direction_id": row[10],
                    "start_time": row[11],
                    "schedule_relationship": row[12],
                    "collected_at": row[13]
                }
                vehicles.append(vehicle)
            
            conn.close()
            return vehicles
            
        except Exception as e:
            logger.error(f"Erreur récupération véhicules récents: {e}")
            return []
    
    def get_vehicle_statistics(self) -> Dict:
        """Récupère les statistiques des véhicules"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Total véhicules
            cursor.execute("SELECT COUNT(*) FROM gtfs_vehicles")
            total_vehicles = cursor.fetchone()[0]
            
            # Par ligne
            cursor.execute("""
                SELECT route_id, COUNT(*) as count
                FROM gtfs_vehicles 
                GROUP BY route_id 
                ORDER BY count DESC
            """)
            line_stats = cursor.fetchall()
            
            # Véhicules récents (30 minutes)
            cutoff_time = datetime.now() - timedelta(minutes=30)
            cursor.execute("SELECT COUNT(*) FROM gtfs_vehicles WHERE collected_at > ?", (cutoff_time,))
            recent_vehicles = cursor.fetchone()[0]
            
            # Vitesse moyenne
            cursor.execute("SELECT AVG(speed) FROM gtfs_vehicles WHERE speed > 0")
            avg_speed = cursor.fetchone()[0] or 0
            
            conn.close()
            
            return {
                "total_vehicles": total_vehicles,
                "recent_vehicles": recent_vehicles,
                "average_speed": round(avg_speed, 1),
                "lines": {line[0]: line[1] for line in line_stats},
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erreur statistiques véhicules: {e}")
            return {
                "total_vehicles": 0,
                "recent_vehicles": 0,
                "average_speed": 0,
                "lines": {},
                "last_updated": datetime.now().isoformat()
            }
    
    def start_collection(self):
        """Démarre la collecte en arrière-plan"""
        if not self.is_collecting:
            self.is_collecting = True
            logger.info("Démarrage collecte GTFS-RT en arrière-plan")
            # Note: La collecte réelle nécessiterait une vraie clé API RATP
    
    def stop_collection(self):
        """Arrête la collecte"""
        if self.is_collecting:
            self.is_collecting = False
            logger.info("Arrêt collecte GTFS-RT")
    
    def get_status(self) -> Dict:
        """Retourne le statut du service"""
        return {
            "service": "GTFS-RT",
            "status": "running" if self.is_collecting else "stopped",
            "vehicle_count": self.get_vehicle_count(),
            "recent_vehicles": len(self.get_recent_vehicles()),
            "last_updated": datetime.now().isoformat()
        }

# Instance globale du service
gtfs_service = GTFSRTService()

def get_gtfs_service() -> GTFSRTService:
    """Retourne l'instance du service GTFS-RT"""
    return gtfs_service




