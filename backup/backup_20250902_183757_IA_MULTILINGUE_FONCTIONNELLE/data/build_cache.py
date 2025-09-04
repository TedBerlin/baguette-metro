#!/usr/bin/env python3
"""
Module de cache DuckDB pour optimiser les requêtes
"""

import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import duckdb
import pandas as pd
from pathlib import Path
import json

from .gtfs_ingestion import ingestion_manager
from .openrouter_client import openrouter_client

logger = logging.getLogger(__name__)


class DuckDBCacheManager:
    """Gestionnaire de cache DuckDB pour les données RATP et boulangeries"""
    
    def __init__(self, cache_dir: str = "data/cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Base de données DuckDB
        self.db_path = self.cache_dir / "ratp_cache.duckdb"
        self.conn = duckdb.connect(str(self.db_path))
        
        # Initialisation des tables
        self._init_tables()
        
    def _init_tables(self):
        """Initialise les tables de cache"""
        try:
            # Table des données temps réel
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS realtime_data (
                    id INTEGER PRIMARY KEY,
                    timestamp TIMESTAMP,
                    line_code VARCHAR,
                    direction VARCHAR,
                    destination VARCHAR,
                    message VARCHAR,
                    transport_type VARCHAR,
                    eta_1 VARCHAR,
                    eta_2 VARCHAR,
                    eta_3 VARCHAR,
                    eta_4 VARCHAR,
                    eta_5 VARCHAR,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Table des boulangeries
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS bakeries (
                    id INTEGER PRIMARY KEY,
                    name VARCHAR,
                    address VARCHAR,
                    latitude DOUBLE,
                    longitude DOUBLE,
                    rating DOUBLE,
                    place_id VARCHAR,
                    types TEXT,
                    vicinity VARCHAR,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Table des métadonnées
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS metadata (
                    id INTEGER PRIMARY KEY,
                    table_name VARCHAR,
                    last_update TIMESTAMP,
                    record_count INTEGER,
                    file_path VARCHAR,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Index pour optimiser les requêtes
            self.conn.execute("CREATE INDEX IF NOT EXISTS idx_realtime_timestamp ON realtime_data(timestamp)")
            self.conn.execute("CREATE INDEX IF NOT EXISTS idx_realtime_line ON realtime_data(line_code)")
            self.conn.execute("CREATE INDEX IF NOT EXISTS idx_bakeries_location ON bakeries(latitude, longitude)")
            
            logger.info("✅ Tables DuckDB initialisées")
            
        except Exception as e:
            logger.error(f"❌ Erreur initialisation tables: {e}")
    
    def cache_realtime_data(self, route_type: str = "metros") -> Dict[str, Any]:
        """
        Met en cache les données temps réel
        
        Args:
            route_type: Type de transport
            
        Returns:
            Dict avec métadonnées du cache
        """
        try:
            logger.info(f"🔄 Mise en cache des données {route_type}...")
            
            # Récupération des dernières données
            df = ingestion_manager.get_latest_data(route_type)
            
            if df.empty:
                logger.warning(f"Aucune donnée à mettre en cache pour {route_type}")
                return self._get_cache_metadata(route_type, success=False)
            
            # Suppression des anciennes données (plus de 24h)
            cutoff_time = datetime.now() - timedelta(hours=24)
            self.conn.execute(
                "DELETE FROM realtime_data WHERE timestamp < ? AND transport_type = ?",
                [cutoff_time, route_type]
            )
            
            # Insertion des nouvelles données
            df['transport_type'] = route_type
            
            # Suppression des anciennes données pour ce type de transport
            self.conn.execute("DELETE FROM realtime_data WHERE transport_type = ?", [route_type])
            
            # Insertion ligne par ligne pour éviter les problèmes de colonnes
            # Récupération du dernier ID pour éviter les doublons
            last_id_result = self.conn.execute("SELECT MAX(id) FROM realtime_data").fetchone()
            last_id = last_id_result[0] if last_id_result[0] is not None else 0
            
            for i, (_, row) in enumerate(df.iterrows()):
                self.conn.execute("""
                    INSERT INTO realtime_data (
                        id, timestamp, line_code, direction, destination, message, 
                        transport_type, eta_1, eta_2, eta_3, eta_4, eta_5
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, [
                    last_id + i + 1,  # ID incrémental
                    row.get('timestamp'),
                    row.get('line_code', ''),
                    row.get('direction', ''),
                    row.get('destination', ''),
                    row.get('message', ''),
                    row.get('transport_type', ''),
                    row.get('eta_1', ''),
                    row.get('eta_2', ''),
                    row.get('eta_3', ''),
                    row.get('eta_4', ''),
                    row.get('eta_5', '')
                ])
            
            # Mise à jour des métadonnées
            metadata = self._get_cache_metadata(route_type, success=True, record_count=len(df))
            self._update_metadata('realtime_data', metadata)
            
            logger.info(f"✅ Données {route_type} mises en cache: {len(df)} enregistrements")
            return metadata
            
        except Exception as e:
            logger.error(f"❌ Erreur mise en cache {route_type}: {e}")
            return self._get_cache_metadata(route_type, success=False, error=str(e))
    
    def cache_bakeries_data(self, lat: float, lon: float, radius: int = 1000) -> Dict[str, Any]:
        """
        Met en cache les données de boulangeries
        
        Args:
            lat, lon: Coordonnées centrales
            radius: Rayon de recherche en mètres
            
        Returns:
            Dict avec métadonnées du cache
        """
        try:
            logger.info(f"🥖 Mise en cache des boulangeries ({lat}, {lon})...")
            
            # Récupération des boulangeries via OpenRouter
            bakeries = openrouter_client.get_nearby_bakeries(lat, lon, radius)
            
            if not bakeries:
                logger.warning("Aucune boulangerie trouvée")
                return self._get_cache_metadata('bakeries', success=False)
            
            # Conversion en DataFrame
            df = pd.DataFrame(bakeries)
            
            # Suppression des anciennes données pour cette zone
            self.conn.execute("DELETE FROM bakeries WHERE latitude BETWEEN ? AND ? AND longitude BETWEEN ? AND ?",
                            [lat - 0.1, lat + 0.1, lon - 0.1, lon + 0.1])
            
            # Insertion ligne par ligne pour éviter les problèmes de colonnes
            # Récupération du dernier ID pour éviter les doublons
            last_id_result = self.conn.execute("SELECT MAX(id) FROM bakeries").fetchone()
            last_id = last_id_result[0] if last_id_result[0] is not None else 0
            
            for i, (_, row) in enumerate(df.iterrows()):
                self.conn.execute("""
                    INSERT INTO bakeries (
                        id, name, address, latitude, longitude, rating, 
                        place_id, types, vicinity
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, [
                    last_id + i + 1,  # ID incrémental
                    row.get('name', ''),
                    row.get('address', ''),
                    row.get('latitude', 0.0),
                    row.get('longitude', 0.0),
                    row.get('rating', 0.0),
                    row.get('place_id', ''),
                    str(row.get('types', [])),
                    row.get('vicinity', '')
                ])
            
            # Mise à jour des métadonnées
            metadata = self._get_cache_metadata('bakeries', success=True, record_count=len(df))
            self._update_metadata('bakeries', metadata)
            
            logger.info(f"✅ Boulangeries mises en cache: {len(df)} enregistrements")
            return metadata
            
        except Exception as e:
            logger.error(f"❌ Erreur mise en cache boulangeries: {e}")
            return self._get_cache_metadata('bakeries', success=False, error=str(e))
    
    def get_cached_realtime_data(self, line_code: Optional[str] = None, 
                               transport_type: str = "metros",
                               limit: int = 100) -> pd.DataFrame:
        """
        Récupère les données temps réel en cache
        
        Args:
            line_code: Code de ligne spécifique (optionnel)
            transport_type: Type de transport
            limit: Nombre maximum d'enregistrements
            
        Returns:
            DataFrame avec les données
        """
        try:
            query = """
                SELECT * FROM realtime_data 
                WHERE transport_type = ?
            """
            params = [transport_type]
            
            if line_code:
                query += " AND line_code = ?"
                params.append(line_code)
            
            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)
            
            result = self.conn.execute(query, params).df()
            return result
            
        except Exception as e:
            logger.error(f"❌ Erreur récupération cache temps réel: {e}")
            return pd.DataFrame()
    
    def get_cached_bakeries(self, lat: float, lon: float, radius_km: float = 1.0) -> pd.DataFrame:
        """
        Récupère les boulangeries en cache
        
        Args:
            lat, lon: Coordonnées centrales
            radius_km: Rayon de recherche en km
            
        Returns:
            DataFrame avec les boulangeries
        """
        try:
            # Calcul des bornes (approximation)
            lat_min, lat_max = lat - radius_km/111, lat + radius_km/111
            lon_min, lon_max = lon - radius_km/(111 * abs(lat)), lon + radius_km/(111 * abs(lat))
            
            query = """
                SELECT *, 
                       SQRT(POW(latitude - ?, 2) + POW(longitude - ?, 2)) * 111 as distance_km
                FROM bakeries 
                WHERE latitude BETWEEN ? AND ? 
                  AND longitude BETWEEN ? AND ?
                ORDER BY distance_km
            """
            
            result = self.conn.execute(query, [lat, lon, lat_min, lat_max, lon_min, lon_max]).df()
            return result
            
        except Exception as e:
            logger.error(f"❌ Erreur récupération cache boulangeries: {e}")
            return pd.DataFrame()
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Récupère les statistiques du cache"""
        try:
            stats = {
                'realtime_data': {},
                'bakeries': {},
                'metadata': {},
                'total_size_mb': 0
            }
            
            # Statistiques temps réel
            realtime_stats = self.conn.execute("""
                SELECT transport_type, COUNT(*) as count, 
                       MIN(timestamp) as oldest, MAX(timestamp) as newest
                FROM realtime_data 
                GROUP BY transport_type
            """).df()
            
            for _, row in realtime_stats.iterrows():
                stats['realtime_data'][row['transport_type']] = {
                    'count': row['count'],
                    'oldest': row['oldest'],
                    'newest': row['newest']
                }
            
            # Statistiques boulangeries
            bakery_count = self.conn.execute("SELECT COUNT(*) as count FROM bakeries").fetchone()[0]
            stats['bakeries']['total_count'] = bakery_count
            
            # Métadonnées
            metadata = self.conn.execute("SELECT * FROM metadata ORDER BY last_update DESC").df()
            stats['metadata'] = metadata.to_dict('records')
            
            # Taille du cache
            if self.db_path.exists():
                stats['total_size_mb'] = self.db_path.stat().st_size / (1024 * 1024)
            
            return stats
            
        except Exception as e:
            logger.error(f"❌ Erreur récupération stats cache: {e}")
            return {}
    
    def _get_cache_metadata(self, table_name: str, success: bool, 
                           record_count: int = 0, error: Optional[str] = None) -> Dict[str, Any]:
        """Génère les métadonnées de cache"""
        return {
            'table_name': table_name,
            'timestamp': datetime.now().isoformat(),
            'success': success,
            'record_count': record_count,
            'error': error
        }
    
    def _update_metadata(self, table_name: str, metadata: Dict[str, Any]):
        """Met à jour les métadonnées"""
        try:
            # Récupération du dernier ID pour éviter les doublons
            last_id_result = self.conn.execute("SELECT MAX(id) FROM metadata").fetchone()
            last_id = last_id_result[0] if last_id_result[0] is not None else 0
            
            self.conn.execute("""
                INSERT INTO metadata (id, table_name, last_update, record_count, file_path)
                VALUES (?, ?, ?, ?, ?)
            """, [
                last_id + 1,  # ID incrémental
                table_name,
                datetime.now(),
                metadata.get('record_count', 0),
                metadata.get('filepath', '')
            ])
        except Exception as e:
            logger.error(f"❌ Erreur mise à jour métadonnées: {e}")
    
    def clear_old_cache(self, days: int = 7):
        """Nettoie le cache ancien"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            # Suppression des anciennes données temps réel
            self.conn.execute("DELETE FROM realtime_data WHERE timestamp < ?", [cutoff_date])
            
            # Suppression des anciennes métadonnées
            self.conn.execute("DELETE FROM metadata WHERE last_update < ?", [cutoff_date])
            
            # Optimisation de la base
            self.conn.execute("VACUUM")
            
            logger.info(f"✅ Cache nettoyé (données > {days} jours supprimées)")
            
        except Exception as e:
            logger.error(f"❌ Erreur nettoyage cache: {e}")
    
    def close(self):
        """Ferme la connexion DuckDB"""
        if self.conn:
            self.conn.close()


# Instance globale
cache_manager = DuckDBCacheManager()


def build_complete_cache():
    """Construit le cache complet"""
    logger.info("🚀 Construction du cache complet")
    
    try:
        # Cache des données temps réel
        transport_types = ['metros', 'rers', 'tramways', 'bus']
        for transport_type in transport_types:
            cache_manager.cache_realtime_data(transport_type)
        
        # Cache des boulangeries (Paris centre)
        cache_manager.cache_bakeries_data(48.8566, 2.3522, 2000)
        
        # Statistiques
        stats = cache_manager.get_cache_stats()
        
        logger.info("✅ Cache complet construit")
        logger.info(f"📊 Statistiques: {stats}")
        
        return stats
        
    except Exception as e:
        logger.error(f"❌ Erreur construction cache: {e}")
        return None


if __name__ == "__main__":
    # Test du cache
    build_complete_cache()
