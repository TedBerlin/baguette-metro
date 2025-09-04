#!/usr/bin/env python3
"""
Orchestrateur Agentic pour Baguette Metro
Utilise un système de planification intelligente pour orchestrer les services
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
import time
from pathlib import Path

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ServiceStatus(Enum):
    """Statuts des services"""
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    STOPPED = "stopped"
    ERROR = "error"
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"

class TaskPriority(Enum):
    """Priorités des tâches"""
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4

@dataclass
class ServiceConfig:
    """Configuration d'un service"""
    name: str
    port: int
    health_endpoint: str
    dependencies: List[str]
    priority: TaskPriority
    auto_restart: bool = True
    max_retries: int = 3
    timeout: int = 30

@dataclass
class OrchestrationTask:
    """Tâche d'orchestration"""
    id: str
    service: str
    action: str  # start, stop, restart, health_check
    priority: TaskPriority
    created_at: float
    dependencies: List[str] = None
    metadata: Dict[str, Any] = None

class AgenticPlanner:
    """
    Orchestrateur agentic intelligent
    Utilise la planification pour gérer les services de manière autonome
    """
    
    def __init__(self):
        self.services: Dict[str, ServiceConfig] = {}
        self.service_status: Dict[str, ServiceStatus] = {}
        self.task_queue: List[OrchestrationTask] = []
        self.running_tasks: Dict[str, OrchestrationTask] = {}
        self.health_checks: Dict[str, float] = {}
        self.metrics: Dict[str, Any] = {}
        
        # Configuration des services
        self._configure_services()
        
    def _configure_services(self):
        """Configure les services de l'application"""
        self.services = {
            "api": ServiceConfig(
                name="FastAPI",
                port=8000,
                health_endpoint="/health",
                dependencies=[],
                priority=TaskPriority.CRITICAL
            ),
            "frontend": ServiceConfig(
                name="Streamlit",
                port=8501,
                health_endpoint="/_stcore/health",
                dependencies=["api"],
                priority=TaskPriority.HIGH
            ),
            "ml_model": ServiceConfig(
                name="ML Model",
                port=None,
                health_endpoint="/model/status",
                dependencies=["api"],
                priority=TaskPriority.MEDIUM
            ),
            "database": ServiceConfig(
                name="PostgreSQL",
                port=5432,
                health_endpoint=None,
                dependencies=[],
                priority=TaskPriority.HIGH
            ),
            "cache": ServiceConfig(
                name="Redis",
                port=6379,
                health_endpoint=None,
                dependencies=[],
                priority=TaskPriority.MEDIUM
            ),
            "monitoring": ServiceConfig(
                name="Prometheus",
                port=9090,
                health_endpoint="/-/healthy",
                dependencies=[],
                priority=TaskPriority.LOW
            )
        }
        
        # Initialiser les statuts
        for service_name in self.services:
            self.service_status[service_name] = ServiceStatus.STOPPED
    
    async def start_orchestration(self):
        """Démarre l'orchestration complète"""
        logger.info("🚀 Démarrage de l'orchestrateur agentic")
        
        # Planifier le démarrage des services
        await self._plan_service_startup()
        
        # Démarrer le monitoring continu
        await self._start_continuous_monitoring()
        
        # Démarrer le gestionnaire de tâches
        await self._start_task_manager()
    
    async def _plan_service_startup(self):
        """Planifie le démarrage intelligent des services"""
        logger.info("📋 Planification du démarrage des services")
        
        # Créer les tâches de démarrage par priorité
        startup_tasks = []
        
        for service_name, config in self.services.items():
            task = OrchestrationTask(
                id=f"start_{service_name}_{int(time.time())}",
                service=service_name,
                action="start",
                priority=config.priority,
                created_at=time.time(),
                dependencies=config.dependencies
            )
            startup_tasks.append(task)
        
        # Trier par priorité
        startup_tasks.sort(key=lambda x: x.priority.value)
        
        # Ajouter à la queue
        self.task_queue.extend(startup_tasks)
        
        logger.info(f"✅ {len(startup_tasks)} tâches de démarrage planifiées")
    
    async def _start_continuous_monitoring(self):
        """Démarre le monitoring continu des services"""
        logger.info("📊 Démarrage du monitoring continu")
        
        # Créer des tâches de health check périodiques
        for service_name, config in self.services.items():
            if config.health_endpoint:
                task = OrchestrationTask(
                    id=f"health_{service_name}_{int(time.time())}",
                    service=service_name,
                    action="health_check",
                    priority=TaskPriority.MEDIUM,
                    created_at=time.time()
                )
                self.task_queue.append(task)
    
    async def _start_task_manager(self):
        """Gestionnaire de tâches asynchrone"""
        logger.info("⚙️ Démarrage du gestionnaire de tâches")
        
        while True:
            # Traiter les tâches en attente
            await self._process_task_queue()
            
            # Vérifier les services en cours d'exécution
            await self._check_running_services()
            
            # Attendre avant la prochaine itération
            await asyncio.sleep(5)
    
    async def _process_task_queue(self):
        """Traite la queue des tâches"""
        if not self.task_queue:
            return
        
        # Trier par priorité et timestamp
        self.task_queue.sort(key=lambda x: (x.priority.value, x.created_at))
        
        # Traiter les tâches disponibles
        tasks_to_process = []
        for task in self.task_queue[:]:
            if self._can_execute_task(task):
                tasks_to_process.append(task)
                self.task_queue.remove(task)
        
        # Exécuter les tâches
        for task in tasks_to_process:
            await self._execute_task(task)
    
    def _can_execute_task(self, task: OrchestrationTask) -> bool:
        """Vérifie si une tâche peut être exécutée"""
        # Vérifier les dépendances
        if task.dependencies:
            for dep in task.dependencies:
                if self.service_status.get(dep) != ServiceStatus.RUNNING:
                    return False
        
        # Vérifier si le service n'est pas déjà en cours de traitement
        if task.service in self.running_tasks:
            return False
        
        return True
    
    async def _execute_task(self, task: OrchestrationTask):
        """Exécute une tâche d'orchestration"""
        logger.info(f"🔄 Exécution de la tâche {task.id}: {task.action} sur {task.service}")
        
        self.running_tasks[task.service] = task
        
        try:
            if task.action == "start":
                await self._start_service(task.service)
            elif task.action == "stop":
                await self._stop_service(task.service)
            elif task.action == "restart":
                await self._restart_service(task.service)
            elif task.action == "health_check":
                await self._health_check_service(task.service)
            
            # Marquer la tâche comme terminée
            del self.running_tasks[task.service]
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'exécution de {task.id}: {e}")
            self.service_status[task.service] = ServiceStatus.ERROR
            del self.running_tasks[task.service]
    
    async def _start_service(self, service_name: str):
        """Démarre un service"""
        config = self.services[service_name]
        logger.info(f"🚀 Démarrage de {service_name} sur le port {config.port}")
        
        self.service_status[service_name] = ServiceStatus.STARTING
        
        # Simulation du démarrage (remplacer par la vraie logique)
        await asyncio.sleep(2)
        
        # Vérifier que le service est bien démarré
        if await self._check_service_health(service_name):
            self.service_status[service_name] = ServiceStatus.RUNNING
            logger.info(f"✅ {service_name} démarré avec succès")
        else:
            self.service_status[service_name] = ServiceStatus.ERROR
            logger.error(f"❌ Échec du démarrage de {service_name}")
    
    async def _stop_service(self, service_name: str):
        """Arrête un service"""
        logger.info(f"🛑 Arrêt de {service_name}")
        self.service_status[service_name] = ServiceStatus.STOPPING
        
        # Simulation de l'arrêt
        await asyncio.sleep(1)
        
        self.service_status[service_name] = ServiceStatus.STOPPED
        logger.info(f"✅ {service_name} arrêté")
    
    async def _restart_service(self, service_name: str):
        """Redémarre un service"""
        logger.info(f"🔄 Redémarrage de {service_name}")
        await self._stop_service(service_name)
        await self._start_service(service_name)
    
    async def _health_check_service(self, service_name: str):
        """Vérifie la santé d'un service"""
        config = self.services[service_name]
        
        if await self._check_service_health(service_name):
            self.service_status[service_name] = ServiceStatus.HEALTHY
            self.health_checks[service_name] = time.time()
        else:
            self.service_status[service_name] = ServiceStatus.UNHEALTHY
            logger.warning(f"⚠️ {service_name} en mauvaise santé")
    
    async def _check_service_health(self, service_name: str) -> bool:
        """Vérifie la santé d'un service spécifique"""
        config = self.services[service_name]
        
        if not config.health_endpoint:
            # Service sans endpoint de santé (ex: base de données)
            return True
        
        try:
            # Simulation de health check (remplacer par vraie requête HTTP)
            await asyncio.sleep(0.1)
            return True
        except Exception as e:
            logger.error(f"Erreur health check {service_name}: {e}")
            return False
    
    async def _check_running_services(self):
        """Vérifie les services en cours d'exécution"""
        for service_name, status in self.service_status.items():
            if status == ServiceStatus.RUNNING:
                # Vérifier périodiquement la santé
                last_check = self.health_checks.get(service_name, 0)
                if time.time() - last_check > 30:  # Check toutes les 30 secondes
                    await self._health_check_service(service_name)
    
    def get_status_report(self) -> Dict[str, Any]:
        """Génère un rapport de statut complet"""
        return {
            "orchestrator": {
                "status": "running",
                "services_count": len(self.services),
                "tasks_in_queue": len(self.task_queue),
                "running_tasks": len(self.running_tasks)
            },
            "services": {
                service: {
                    "status": status.value,
                    "config": {
                        "port": self.services[service].port,
                        "priority": self.services[service].priority.value,
                        "dependencies": self.services[service].dependencies
                    },
                    "last_health_check": self.health_checks.get(service)
                }
                for service, status in self.service_status.items()
            },
            "metrics": self.metrics
        }

# Instance globale de l'orchestrateur
orchestrator = AgenticPlanner()

async def start_orchestration():
    """Point d'entrée pour démarrer l'orchestration"""
    await orchestrator.start_orchestration()

if __name__ == "__main__":
    asyncio.run(start_orchestration())





