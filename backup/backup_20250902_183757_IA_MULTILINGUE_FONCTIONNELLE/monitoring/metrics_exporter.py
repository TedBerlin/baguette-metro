#!/usr/bin/env python3
"""
Exporteur de métriques pour Prometheus
"""

import time
import psutil
from prometheus_client import (
    Counter, Histogram, Gauge, Summary, 
    generate_latest, CONTENT_TYPE_LATEST,
    CollectorRegistry, multiprocess
)
from fastapi import Response
import logging

logger = logging.getLogger(__name__)

class MetricsExporter:
    """Exporteur de métriques système et applicatives"""
    
    def __init__(self):
        self.registry = CollectorRegistry()
        multiprocess.MultiProcessCollector(self.registry)
        
        # Métriques API
        self.api_requests_total = Counter(
            'api_requests_total',
            'Total des requêtes API',
            ['method', 'endpoint', 'status'],
            registry=self.registry
        )
        
        self.api_request_duration = Histogram(
            'api_request_duration_seconds',
            'Durée des requêtes API',
            ['method', 'endpoint'],
            registry=self.registry
        )
        
        # Métriques ML
        self.ml_predictions_total = Counter(
            'ml_predictions_total',
            'Total des prédictions ML',
            ['model_type', 'status'],
            registry=self.registry
        )
        
        self.ml_prediction_duration = Histogram(
            'ml_prediction_duration_seconds',
            'Durée des prédictions ML',
            ['model_type'],
            registry=self.registry
        )
        
        # Métriques système
        self.system_cpu_usage = Gauge(
            'system_cpu_usage_percent',
            'Utilisation CPU',
            registry=self.registry
        )
        
        self.system_memory_usage = Gauge(
            'system_memory_usage_bytes',
            'Utilisation mémoire',
            registry=self.registry
        )
        
        self.system_disk_usage = Gauge(
            'system_disk_usage_bytes',
            'Utilisation disque',
            ['mount_point'],
            registry=self.registry
        )
        
        # Métriques métier
        self.active_users = Gauge(
            'active_users_total',
            'Nombre d\'utilisateurs actifs',
            registry=self.registry
        )
        
        self.routes_calculated = Counter(
            'routes_calculated_total',
            'Total des trajets calculés',
            ['include_bakery'],
            registry=self.registry
        )
        
        self.chat_messages_total = Counter(
            'chat_messages_total',
            'Total des messages chat',
            ['language', 'type'],
            registry=self.registry
        )
        
        # Métriques de performance
        self.cache_hit_ratio = Gauge(
            'cache_hit_ratio',
            'Ratio de hits du cache',
            registry=self.registry
        )
        
        self.database_connections = Gauge(
            'database_connections_active',
            'Connexions actives à la base de données',
            registry=self.registry
        )
    
    def record_api_request(self, method: str, endpoint: str, status: int, duration: float):
        """Enregistre une requête API"""
        self.api_requests_total.labels(method=method, endpoint=endpoint, status=status).inc()
        self.api_request_duration.labels(method=method, endpoint=endpoint).observe(duration)
    
    def record_ml_prediction(self, model_type: str, status: str, duration: float):
        """Enregistre une prédiction ML"""
        self.ml_predictions_total.labels(model_type=model_type, status=status).inc()
        self.ml_prediction_duration.labels(model_type=model_type).observe(duration)
    
    def update_system_metrics(self):
        """Met à jour les métriques système"""
        try:
            # CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            self.system_cpu_usage.set(cpu_percent)
            
            # Mémoire
            memory = psutil.virtual_memory()
            self.system_memory_usage.set(memory.used)
            
            # Disque
            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    self.system_disk_usage.labels(mount_point=partition.mountpoint).set(usage.used)
                except PermissionError:
                    continue
                    
        except Exception as e:
            logger.error(f"Erreur mise à jour métriques système: {e}")
    
    def record_route_calculation(self, include_bakery: bool):
        """Enregistre un calcul de trajet"""
        self.routes_calculated.labels(include_bakery=str(include_bakery)).inc()
    
    def record_chat_message(self, language: str, message_type: str):
        """Enregistre un message chat"""
        self.chat_messages_total.labels(language=language, type=message_type).inc()
    
    def update_cache_metrics(self, hits: int, misses: int):
        """Met à jour les métriques de cache"""
        total = hits + misses
        if total > 0:
            ratio = hits / total
            self.cache_hit_ratio.set(ratio)
    
    def update_database_metrics(self, active_connections: int):
        """Met à jour les métriques de base de données"""
        self.database_connections.set(active_connections)
    
    def update_user_metrics(self, active_users: int):
        """Met à jour les métriques utilisateurs"""
        self.active_users.set(active_users)
    
    def get_metrics(self) -> Response:
        """Retourne les métriques au format Prometheus"""
        try:
            # Mise à jour des métriques système
            self.update_system_metrics()
            
            # Génération des métriques
            metrics = generate_latest(self.registry)
            
            return Response(
                content=metrics,
                media_type=CONTENT_TYPE_LATEST,
                headers={'Cache-Control': 'no-cache'}
            )
        except Exception as e:
            logger.error(f"Erreur génération métriques: {e}")
            return Response(
                content="# Erreur génération métriques\n",
                media_type=CONTENT_TYPE_LATEST,
                status_code=500
            )

# Instance globale
metrics_exporter = MetricsExporter()

def get_metrics_exporter() -> MetricsExporter:
    """Retourne l'instance de l'exporteur de métriques"""
    return metrics_exporter




