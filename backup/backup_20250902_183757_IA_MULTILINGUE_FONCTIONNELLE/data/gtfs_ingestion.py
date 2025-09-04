#!/usr/bin/env python3
"""
Module d'ingestion GTFS-RT avec stockage Parquet
"""

import os
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from pathlib import Path
import json

from .gtfs_realtime import RATPGTFSClient

logger = logging.getLogger(__name__)


class GTFSIngestionManager:
    """Gestionnaire d'ingestion des données GTFS-RT"""
    
    def __init__(self, data_dir: str = "data/processed"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Sous-dossiers par type de données
        self.metro_dir = self.data_dir / "metro"
        self.rer_dir = self.data_dir / "rer"
        self.bus_dir = self.data_dir / "bus"
        self.tram_dir = self.data_dir / "tram"
        
        for dir_path in [self.metro_dir, self.rer_dir, self.bus_dir, self.tram_dir]:
            dir_path.mkdir(exist_ok=True)
        
        self.gtfs_client = RATPGTFSClient()
        
    async def ingest_realtime_data(self, route_type: str = "metros") -> Dict[str, Any]:
        """
        Ingère les données temps réel et les stocke en Parquet
        
        Args:
            route_type: Type de transport ('metros', 'rers', 'tramways', 'bus')
            
        Returns:
            Dict avec métadonnées de l'ingestion
        """
        try:
            logger.info(f"🚇 Ingestion des données {route_type}...")
            
            # Récupération des données temps réel
            async with self.gtfs_client as client:
                realtime_data = await client.get_realtime_data(route_type)
            
            if not realtime_data:
                logger.warning(f"Aucune donnée récupérée pour {route_type}")
                return self._get_ingestion_metadata(route_type, success=False)
            
            # Conversion en DataFrame
            df = self._convert_to_dataframe(realtime_data, route_type)
            
            # Stockage en Parquet
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{route_type}_{timestamp}.parquet"
            
            if route_type == "metros":
                filepath = self.metro_dir / filename
            elif route_type == "rers":
                filepath = self.rer_dir / filename
            elif route_type == "tramways":
                filepath = self.tram_dir / filename
            else:
                filepath = self.bus_dir / filename
            
            # Sauvegarde Parquet avec compression
            df.to_parquet(filepath, compression='snappy', index=False)
            
            # Métadonnées
            metadata = self._get_ingestion_metadata(route_type, success=True, filepath=filepath, df=df)
            
            logger.info(f"✅ Données {route_type} ingérées: {len(df)} enregistrements")
            return metadata
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'ingestion {route_type}: {e}")
            return self._get_ingestion_metadata(route_type, success=False, error=str(e))
    
    def _convert_to_dataframe(self, data: Dict[str, Any], route_type: str) -> pd.DataFrame:
        """Convertit les données GTFS-RT en DataFrame"""
        records = []
        timestamp = datetime.now()
        
        # Extraction des données selon le type de transport
        if route_type == "metros":
            records = self._extract_metro_data(data, timestamp)
        elif route_type == "rers":
            records = self._extract_rer_data(data, timestamp)
        elif route_type == "tramways":
            records = self._extract_tram_data(data, timestamp)
        else:
            records = self._extract_bus_data(data, timestamp)
        
        return pd.DataFrame(records)
    
    def _extract_metro_data(self, data: Dict[str, Any], timestamp: datetime) -> List[Dict]:
        """Extrait les données métro"""
        records = []
        
        try:
            # Gestion du cas où data est une liste (données mock)
            if isinstance(data, list):
                for item in data:
                    if isinstance(item, dict):
                        record = {
                            'timestamp': timestamp,
                            'line_code': item.get('line_code', ''),
                            'direction': item.get('direction', ''),
                            'destination': item.get('destination', ''),
                            'message': item.get('message', ''),
                            'type': 'metro'
                        }
                        
                        # Ajout des horaires
                        schedules = item.get('schedules', [])
                        for i, time_info in enumerate(schedules[:5]):  # Max 5 horaires
                            if isinstance(time_info, dict):
                                record[f'eta_{i+1}'] = time_info.get('time', '')
                            else:
                                record[f'eta_{i+1}'] = str(time_info)
                        
                        records.append(record)
            else:
                # Structure des données métro RATP (dictionnaire)
                for line_code, line_data in data.items():
                    if isinstance(line_data, dict) and 'schedules' in line_data:
                        for direction, schedules in line_data['schedules'].items():
                            for schedule in schedules:
                                record = {
                                    'timestamp': timestamp,
                                    'line_code': line_code,
                                    'direction': direction,
                                    'destination': schedule.get('destination', ''),
                                    'message': schedule.get('message', ''),
                                    'type': 'metro'
                                }
                                
                                # Ajout des horaires
                                if 'schedules' in schedule:
                                    for i, time_info in enumerate(schedule['schedules']):
                                        record[f'eta_{i+1}'] = time_info.get('time', '')
                                
                                records.append(record)
        except Exception as e:
            logger.error(f"Erreur extraction métro: {e}")
        
        return records
    
    def _extract_rer_data(self, data: Dict[str, Any], timestamp: datetime) -> List[Dict]:
        """Extrait les données RER"""
        records = []
        
        try:
            # Gestion du cas où data est une liste (données mock)
            if isinstance(data, list):
                for item in data:
                    if isinstance(item, dict):
                        record = {
                            'timestamp': timestamp,
                            'line_code': item.get('line_code', ''),
                            'direction': item.get('direction', ''),
                            'destination': item.get('destination', ''),
                            'message': item.get('message', ''),
                            'type': 'rer'
                        }
                        
                        # Ajout des horaires
                        schedules = item.get('schedules', [])
                        for i, time_info in enumerate(schedules[:5]):  # Max 5 horaires
                            if isinstance(time_info, dict):
                                record[f'eta_{i+1}'] = time_info.get('time', '')
                            else:
                                record[f'eta_{i+1}'] = str(time_info)
                        
                        records.append(record)
            else:
                # Structure des données RER RATP (dictionnaire)
                for line_code, line_data in data.items():
                    if isinstance(line_data, dict) and 'schedules' in line_data:
                        for direction, schedules in line_data['schedules'].items():
                            for schedule in schedules:
                                record = {
                                    'timestamp': timestamp,
                                    'line_code': line_code,
                                    'direction': direction,
                                    'destination': schedule.get('destination', ''),
                                    'message': schedule.get('message', ''),
                                    'type': 'rer'
                                }
                                
                                if 'schedules' in schedule:
                                    for i, time_info in enumerate(schedule['schedules']):
                                        record[f'eta_{i+1}'] = time_info.get('time', '')
                                
                                records.append(record)
        except Exception as e:
            logger.error(f"Erreur extraction RER: {e}")
        
        return records
    
    def _extract_tram_data(self, data: Dict[str, Any], timestamp: datetime) -> List[Dict]:
        """Extrait les données tramway"""
        records = []
        
        try:
            # Gestion du cas où data est une liste (données mock)
            if isinstance(data, list):
                for item in data:
                    if isinstance(item, dict):
                        record = {
                            'timestamp': timestamp,
                            'line_code': item.get('line_code', ''),
                            'direction': item.get('direction', ''),
                            'destination': item.get('destination', ''),
                            'message': item.get('message', ''),
                            'type': 'tram'
                        }
                        
                        # Ajout des horaires
                        schedules = item.get('schedules', [])
                        for i, time_info in enumerate(schedules[:5]):  # Max 5 horaires
                            if isinstance(time_info, dict):
                                record[f'eta_{i+1}'] = time_info.get('time', '')
                            else:
                                record[f'eta_{i+1}'] = str(time_info)
                        
                        records.append(record)
            else:
                # Structure des données tram RATP (dictionnaire)
                for line_code, line_data in data.items():
                    if isinstance(line_data, dict) and 'schedules' in line_data:
                        for direction, schedules in line_data['schedules'].items():
                            for schedule in schedules:
                                record = {
                                    'timestamp': timestamp,
                                    'line_code': line_code,
                                    'direction': direction,
                                    'destination': schedule.get('destination', ''),
                                    'message': schedule.get('message', ''),
                                    'type': 'tram'
                                }
                                
                                if 'schedules' in schedule:
                                    for i, time_info in enumerate(schedule['schedules']):
                                        record[f'eta_{i+1}'] = time_info.get('time', '')
                                
                                records.append(record)
        except Exception as e:
            logger.error(f"Erreur extraction tram: {e}")
        
        return records
    
    def _extract_bus_data(self, data: Dict[str, Any], timestamp: datetime) -> List[Dict]:
        """Extrait les données bus"""
        records = []
        
        try:
            # Gestion du cas où data est une liste (données mock)
            if isinstance(data, list):
                for item in data:
                    if isinstance(item, dict):
                        record = {
                            'timestamp': timestamp,
                            'line_code': item.get('line_code', ''),
                            'direction': item.get('direction', ''),
                            'destination': item.get('destination', ''),
                            'message': item.get('message', ''),
                            'type': 'bus'
                        }
                        
                        # Ajout des horaires
                        schedules = item.get('schedules', [])
                        for i, time_info in enumerate(schedules[:5]):  # Max 5 horaires
                            if isinstance(time_info, dict):
                                record[f'eta_{i+1}'] = time_info.get('time', '')
                            else:
                                record[f'eta_{i+1}'] = str(time_info)
                        
                        records.append(record)
            else:
                # Structure des données bus RATP (dictionnaire)
                for line_code, line_data in data.items():
                    if isinstance(line_data, dict) and 'schedules' in line_data:
                        for direction, schedules in line_data['schedules'].items():
                            for schedule in schedules:
                                record = {
                                    'timestamp': timestamp,
                                    'line_code': line_code,
                                    'direction': direction,
                                    'destination': schedule.get('destination', ''),
                                    'message': schedule.get('message', ''),
                                    'type': 'bus'
                                }
                                
                                if 'schedules' in schedule:
                                    for i, time_info in enumerate(schedule['schedules']):
                                        record[f'eta_{i+1}'] = time_info.get('time', '')
                                
                                records.append(record)
        except Exception as e:
            logger.error(f"Erreur extraction bus: {e}")
        
        return records
    
    def _get_ingestion_metadata(self, route_type: str, success: bool, 
                               filepath: Optional[Path] = None, 
                               df: Optional[pd.DataFrame] = None,
                               error: Optional[str] = None) -> Dict[str, Any]:
        """Génère les métadonnées d'ingestion"""
        metadata = {
            'route_type': route_type,
            'timestamp': datetime.now().isoformat(),
            'success': success,
            'filepath': str(filepath) if filepath else None,
            'record_count': len(df) if df is not None else 0,
            'error': error
        }
        
        # Sauvegarde des métadonnées
        metadata_file = self.data_dir / f"ingestion_metadata_{route_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2, default=str)
        
        return metadata
    
    async def ingest_all_transport_types(self) -> Dict[str, Any]:
        """Ingère tous les types de transport"""
        transport_types = ['metros', 'rers', 'tramways', 'bus']
        results = {}
        
        for transport_type in transport_types:
            results[transport_type] = await self.ingest_realtime_data(transport_type)
            await asyncio.sleep(1)  # Pause entre les requêtes
        
        return results
    
    def get_latest_data(self, route_type: str, limit: int = 100) -> pd.DataFrame:
        """Récupère les dernières données ingérées"""
        if route_type == "metros":
            data_dir = self.metro_dir
        elif route_type == "rers":
            data_dir = self.rer_dir
        elif route_type == "tramways":
            data_dir = self.tram_dir
        else:
            data_dir = self.bus_dir
        
        # Liste des fichiers Parquet
        parquet_files = list(data_dir.glob("*.parquet"))
        if not parquet_files:
            return pd.DataFrame()
        
        # Tri par date de modification
        parquet_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        # Lecture du fichier le plus récent
        latest_file = parquet_files[0]
        df = pd.read_parquet(latest_file)
        
        return df.head(limit)
    
    def get_data_summary(self) -> Dict[str, Any]:
        """Génère un résumé des données ingérées"""
        summary = {
            'total_files': 0,
            'total_records': 0,
            'transport_types': {},
            'last_ingestion': None
        }
        
        for transport_type, data_dir in [
            ('metros', self.metro_dir),
            ('rers', self.rer_dir),
            ('tramways', self.tram_dir),
            ('bus', self.bus_dir)
        ]:
            parquet_files = list(data_dir.glob("*.parquet"))
            if parquet_files:
                # Fichier le plus récent
                latest_file = max(parquet_files, key=lambda x: x.stat().st_mtime)
                df = pd.read_parquet(latest_file)
                
                summary['transport_types'][transport_type] = {
                    'file_count': len(parquet_files),
                    'latest_records': len(df),
                    'latest_file': latest_file.name,
                    'latest_timestamp': datetime.fromtimestamp(latest_file.stat().st_mtime).isoformat()
                }
                
                summary['total_files'] += len(parquet_files)
                summary['total_records'] += len(df)
                
                # Mise à jour de la dernière ingestion
                file_time = datetime.fromtimestamp(latest_file.stat().st_mtime)
                if summary['last_ingestion'] is None or file_time > datetime.fromisoformat(summary['last_ingestion']):
                    summary['last_ingestion'] = file_time.isoformat()
        
        return summary


# Instance globale
ingestion_manager = GTFSIngestionManager()


async def run_ingestion_pipeline():
    """Pipeline d'ingestion complet"""
    logger.info("🚀 Démarrage du pipeline d'ingestion GTFS-RT")
    
    try:
        # Ingestion de tous les types de transport
        results = await ingestion_manager.ingest_all_transport_types()
        
        # Résumé
        summary = ingestion_manager.get_data_summary()
        
        logger.info("✅ Pipeline d'ingestion terminé")
        logger.info(f"📊 Résumé: {summary['total_files']} fichiers, {summary['total_records']} enregistrements")
        
        return results, summary
        
    except Exception as e:
        logger.error(f"❌ Erreur pipeline d'ingestion: {e}")
        return None, None


if __name__ == "__main__":
    # Test du pipeline
    asyncio.run(run_ingestion_pipeline())

