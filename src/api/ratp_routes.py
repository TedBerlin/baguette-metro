#!/usr/bin/env python3
"""
Routes API pour les données RATP
GTFS-RT, PRIM, et retards historiques
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Optional
import asyncio
import logging
from datetime import datetime, timedelta

from ..data.ratp_data_integration import RATPDataIntegration, initialize_ratp_data

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ratp", tags=["RATP Data"])

# Instance globale de l'intégration RATP
ratp_integration: Optional[RATPDataIntegration] = None

@router.on_event("startup")
async def startup_ratp():
    """Initialise l'intégration RATP au démarrage"""
    global ratp_integration
    try:
        ratp_integration = initialize_ratp_data()
        logger.info("Intégration RATP initialisée")
    except Exception as e:
        logger.error(f"Erreur initialisation RATP: {e}")
        ratp_integration = None

@router.get("/health")
async def ratp_health():
    """Vérifie la santé de l'intégration RATP"""
    if not ratp_integration:
        raise HTTPException(status_code=503, detail="Intégration RATP non disponible")
    
    return {
        "status": "healthy",
        "service": "RATP Data Integration",
        "timestamp": datetime.now().isoformat(),
        "features": [
            "GTFS-RT (positions temps réel)",
            "PRIM (fréquentation stations)",
            "Retards historiques",
            "Analyses de performance"
        ]
    }

@router.get("/vehicles")
async def get_vehicle_positions(
    route_id: Optional[str] = Query(None, description="ID de la ligne (ex: '1', '4')"),
    limit: int = Query(100, ge=1, le=1000, description="Nombre maximum de véhicules")
):
    """Récupère les positions des véhicules en temps réel"""
    
    if not ratp_integration:
        raise HTTPException(status_code=503, detail="Intégration RATP non disponible")
    
    try:
        vehicles = ratp_integration.get_vehicle_positions(route_id)
        
        # Limite les résultats
        vehicles = vehicles[:limit]
        
        return {
            "timestamp": datetime.now().isoformat(),
            "route_id": route_id,
            "vehicle_count": len(vehicles),
            "vehicles": vehicles
        }
        
    except Exception as e:
        logger.error(f"Erreur récupération véhicules: {e}")
        raise HTTPException(status_code=500, detail="Erreur récupération données véhicules")

@router.get("/stations/{station_id}/congestion")
async def get_station_congestion(station_id: str):
    """Récupère le niveau de congestion d'une station"""
    
    if not ratp_integration:
        raise HTTPException(status_code=503, detail="Intégration RATP non disponible")
    
    try:
        congestion = ratp_integration.get_station_congestion(station_id)
        
        return {
            "station_id": station_id,
            "congestion": congestion,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Erreur récupération congestion station {station_id}: {e}")
        raise HTTPException(status_code=500, detail="Erreur récupération données congestion")

@router.get("/lines/{line_id}/performance")
async def get_line_performance(line_id: str):
    """Récupère les performances d'une ligne"""
    
    if not ratp_integration:
        raise HTTPException(status_code=503, detail="Intégration RATP non disponible")
    
    try:
        performance = ratp_integration.get_line_performance(line_id)
        
        return {
            "line_id": line_id,
            "performance": performance,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Erreur récupération performance ligne {line_id}: {e}")
        raise HTTPException(status_code=500, detail="Erreur récupération données performance")

@router.get("/delays")
async def get_recent_delays(
    line_id: Optional[str] = Query(None, description="ID de la ligne"),
    station_id: Optional[str] = Query(None, description="ID de la station"),
    days: int = Query(7, ge=1, le=30, description="Nombre de jours à analyser")
):
    """Récupère les retards récents"""
    
    if not ratp_integration:
        raise HTTPException(status_code=503, detail="Intégration RATP non disponible")
    
    try:
        # Connexion à la base de données
        import sqlite3
        conn = sqlite3.connect(ratp_integration.db_path)
        
        # Construction de la requête
        query = """
            SELECT line_id, station_id, delay_minutes, date, cause, impact_level
            FROM historical_delays 
            WHERE date > datetime('now', '-{} days')
        """.format(days)
        
        params = []
        if line_id:
            query += " AND line_id = ?"
            params.append(line_id)
        
        if station_id:
            query += " AND station_id = ?"
            params.append(station_id)
        
        query += " ORDER BY date DESC LIMIT 100"
        
        cursor = conn.cursor()
        cursor.execute(query, params)
        results = cursor.fetchall()
        
        delays = []
        for row in results:
            delays.append({
                "line_id": row[0],
                "station_id": row[1],
                "delay_minutes": row[2],
                "date": row[3],
                "cause": row[4],
                "impact_level": row[5]
            })
        
        conn.close()
        
        return {
            "timestamp": datetime.now().isoformat(),
            "days_analyzed": days,
            "line_id": line_id,
            "station_id": station_id,
            "delay_count": len(delays),
            "delays": delays
        }
        
    except Exception as e:
        logger.error(f"Erreur récupération retards: {e}")
        raise HTTPException(status_code=500, detail="Erreur récupération données retards")

@router.get("/analytics/summary")
async def get_analytics_summary():
    """Récupère un résumé analytique des données RATP"""
    
    if not ratp_integration:
        raise HTTPException(status_code=503, detail="Intégration RATP non disponible")
    
    try:
        import sqlite3
        conn = sqlite3.connect(ratp_integration.db_path)
        cursor = conn.cursor()
        
        # Statistiques générales
        stats = {}
        
        # Nombre de véhicules actifs
        cursor.execute("""
            SELECT COUNT(DISTINCT vehicle_id) 
            FROM gtfs_vehicles 
            WHERE timestamp > ?
        """, [int((datetime.now() - timedelta(minutes=5)).timestamp())])
        stats["active_vehicles"] = cursor.fetchone()[0] or 0
        
        # Nombre de stations avec données PRIM
        cursor.execute("""
            SELECT COUNT(DISTINCT station_id) 
            FROM prim_stations 
            WHERE timestamp > datetime('now', '-1 hour')
        """)
        stats["stations_with_prim"] = cursor.fetchone()[0] or 0
        
        # Retards aujourd'hui
        cursor.execute("""
            SELECT COUNT(*), AVG(delay_minutes)
            FROM historical_delays 
            WHERE date > datetime('now', '-1 day')
        """)
        delay_result = cursor.fetchone()
        stats["delays_today"] = delay_result[0] or 0
        stats["avg_delay_today"] = round(delay_result[1] or 0, 1)
        
        # Lignes les plus performantes
        cursor.execute("""
            SELECT line_id, AVG(delay_minutes) as avg_delay
            FROM historical_delays 
            WHERE date > datetime('now', '-7 days')
            GROUP BY line_id
            ORDER BY avg_delay ASC
            LIMIT 5
        """)
        best_lines = [{"line_id": row[0], "avg_delay": round(row[1], 1)} for row in cursor.fetchall()]
        
        # Stations les plus fréquentées
        cursor.execute("""
            SELECT station_id, AVG(passenger_count) as avg_passengers
            FROM prim_stations 
            WHERE timestamp > datetime('now', '-1 day')
            GROUP BY station_id
            ORDER BY avg_passengers DESC
            LIMIT 5
        """)
        busy_stations = [{"station_id": row[0], "avg_passengers": round(row[1], 0)} for row in cursor.fetchall()]
        
        conn.close()
        
        return {
            "timestamp": datetime.now().isoformat(),
            "summary": stats,
            "best_performing_lines": best_lines,
            "busiest_stations": busy_stations
        }
        
    except Exception as e:
        logger.error(f"Erreur récupération analytics: {e}")
        raise HTTPException(status_code=500, detail="Erreur récupération analytics")

@router.post("/refresh")
async def refresh_ratp_data():
    """Force le rafraîchissement des données RATP"""
    
    if not ratp_integration:
        raise HTTPException(status_code=503, detail="Intégration RATP non disponible")
    
    try:
        # Collecte asynchrone des données
        vehicles = await ratp_integration.fetch_gtfs_rt_data()
        stations = await ratp_integration.fetch_prim_data()
        
        return {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "vehicles_collected": len(vehicles),
            "stations_collected": len(stations),
            "message": "Données RATP rafraîchies avec succès"
        }
        
    except Exception as e:
        logger.error(f"Erreur rafraîchissement données RATP: {e}")
        raise HTTPException(status_code=500, detail="Erreur rafraîchissement données")

@router.get("/cache/status")
async def get_cache_status():
    """Récupère le statut du cache RATP"""
    
    if not ratp_integration:
        raise HTTPException(status_code=503, detail="Intégration RATP non disponible")
    
    try:
        import os
        from pathlib import Path
        
        cache_files = {
            "gtfs_rt": ratp_integration.cache_dir / "gtfs_rt_cache.json",
            "prim": ratp_integration.cache_dir / "prim_cache.json"
        }
        
        status = {}
        for name, file_path in cache_files.items():
            if file_path.exists():
                stat = file_path.stat()
                status[name] = {
                    "exists": True,
                    "size_bytes": stat.st_size,
                    "last_modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    "age_seconds": (datetime.now() - datetime.fromtimestamp(stat.st_mtime)).total_seconds()
                }
            else:
                status[name] = {"exists": False}
        
        return {
            "timestamp": datetime.now().isoformat(),
            "cache_status": status,
            "cache_dir": str(ratp_integration.cache_dir),
            "db_path": str(ratp_integration.db_path)
        }
        
    except Exception as e:
        logger.error(f"Erreur récupération statut cache: {e}")
        raise HTTPException(status_code=500, detail="Erreur récupération statut cache")





