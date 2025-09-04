#!/usr/bin/env python3
"""
Orchestrateur MCP (Model Context Protocol) pour Baguette Metro
Utilise le protocole MCP pour une orchestration moderne et interopérable
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import time
from pathlib import Path

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MCPMessageType(Enum):
    """Types de messages MCP"""
    REQUEST = "request"
    RESPONSE = "response"
    NOTIFICATION = "notification"
    ERROR = "error"

class MCPResourceType(Enum):
    """Types de ressources MCP"""
    SERVICE = "service"
    TASK = "task"
    CONFIG = "config"
    METRIC = "metric"
    HEALTH = "health"

@dataclass
class MCPMessage:
    """Message MCP standardisé"""
    id: str
    type: MCPMessageType
    method: str
    params: Dict[str, Any]
    result: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None
    timestamp: float = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dictionnaire"""
        return {
            "id": self.id,
            "type": self.type.value,
            "method": self.method,
            "params": self.params,
            "result": self.result,
            "error": self.error,
            "timestamp": self.timestamp
        }

@dataclass
class MCPResource:
    """Ressource MCP"""
    uri: str
    name: str
    type: MCPResourceType
    content: Dict[str, Any]
    metadata: Dict[str, Any] = None

class MCPOrchestrator:
    """
    Orchestrateur basé sur MCP
    Utilise le protocole MCP pour une orchestration moderne
    """
    
    def __init__(self):
        self.resources: Dict[str, MCPResource] = {}
        self.handlers: Dict[str, Callable] = {}
        self.subscribers: Dict[str, List[Callable]] = {}
        self.message_queue: List[MCPMessage] = []
        self.service_registry: Dict[str, Dict[str, Any]] = {}
        
        # Enregistrer les handlers MCP
        self._register_mcp_handlers()
        
        # Initialiser les ressources
        self._initialize_resources()
    
    def _register_mcp_handlers(self):
        """Enregistre les handlers MCP"""
        self.handlers = {
            "service/start": self._handle_service_start,
            "service/stop": self._handle_service_stop,
            "service/restart": self._handle_service_restart,
            "service/status": self._handle_service_status,
            "config/get": self._handle_config_get,
            "config/set": self._handle_config_set,
            "health/check": self._handle_health_check,
            "metrics/get": self._handle_metrics_get,
            "orchestration/plan": self._handle_orchestration_plan,
            "orchestration/execute": self._handle_orchestration_execute
        }
    
    def _initialize_resources(self):
        """Initialise les ressources MCP"""
        # Ressources de services
        services = [
            {
                "uri": "mcp://baguette-metro/services/api",
                "name": "FastAPI Service",
                "type": MCPResourceType.SERVICE,
                "content": {
                    "port": 8000,
                    "health_endpoint": "/health",
                    "dependencies": [],
                    "priority": "critical"
                }
            },
            {
                "uri": "mcp://baguette-metro/services/frontend",
                "name": "Streamlit Frontend",
                "type": MCPResourceType.SERVICE,
                "content": {
                    "port": 8501,
                    "health_endpoint": "/_stcore/health",
                    "dependencies": ["api"],
                    "priority": "high"
                }
            },
            {
                "uri": "mcp://baguette-metro/services/ml",
                "name": "ML Model Service",
                "type": MCPResourceType.SERVICE,
                "content": {
                    "port": None,
                    "health_endpoint": "/model/status",
                    "dependencies": ["api"],
                    "priority": "medium"
                }
            }
        ]
        
        for service in services:
            resource = MCPResource(**service)
            self.resources[resource.uri] = resource
    
    async def start(self):
        """Démarre l'orchestrateur MCP"""
        logger.info("🚀 Démarrage de l'orchestrateur MCP")
        
        # Démarrer le processeur de messages
        await self._start_message_processor()
        
        # Publier l'événement de démarrage
        await self._publish_notification("orchestrator/started", {
            "timestamp": time.time(),
            "version": "1.0.0"
        })
    
    async def _start_message_processor(self):
        """Démarre le processeur de messages MCP"""
        logger.info("📨 Démarrage du processeur de messages MCP")
        
        while True:
            # Traiter les messages en attente
            await self._process_message_queue()
            
            # Attendre avant la prochaine itération
            await asyncio.sleep(1)
    
    async def _process_message_queue(self):
        """Traite la queue des messages MCP"""
        if not self.message_queue:
            return
        
        # Traiter les messages par ordre FIFO
        messages_to_process = self.message_queue[:]
        self.message_queue.clear()
        
        for message in messages_to_process:
            await self._handle_message(message)
    
    async def _handle_message(self, message: MCPMessage):
        """Traite un message MCP"""
        logger.info(f"📨 Traitement du message {message.id}: {message.method}")
        
        try:
            # Vérifier si le handler existe
            if message.method in self.handlers:
                handler = self.handlers[message.method]
                result = await handler(message.params)
                
                # Créer la réponse
                response = MCPMessage(
                    id=message.id,
                    type=MCPMessageType.RESPONSE,
                    method=message.method,
                    params=message.params,
                    result=result
                )
                
                # Publier la réponse
                await self._publish_response(response)
                
            else:
                # Handler non trouvé
                error_response = MCPMessage(
                    id=message.id,
                    type=MCPMessageType.ERROR,
                    method=message.method,
                    params=message.params,
                    error={
                        "code": "METHOD_NOT_FOUND",
                        "message": f"Handler '{message.method}' not found"
                    }
                )
                await self._publish_response(error_response)
                
        except Exception as e:
            logger.error(f"❌ Erreur lors du traitement de {message.id}: {e}")
            
            error_response = MCPMessage(
                id=message.id,
                type=MCPMessageType.ERROR,
                method=message.method,
                params=message.params,
                error={
                    "code": "INTERNAL_ERROR",
                    "message": str(e)
                }
            )
            await self._publish_response(error_response)
    
    async def _handle_service_start(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handler pour démarrer un service"""
        service_name = params.get("service")
        logger.info(f"🚀 Démarrage du service {service_name}")
        
        # Simulation du démarrage
        await asyncio.sleep(2)
        
        # Mettre à jour le registre
        self.service_registry[service_name] = {
            "status": "running",
            "started_at": time.time(),
            "port": params.get("port")
        }
        
        return {
            "service": service_name,
            "status": "started",
            "timestamp": time.time()
        }
    
    async def _handle_service_stop(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handler pour arrêter un service"""
        service_name = params.get("service")
        logger.info(f"🛑 Arrêt du service {service_name}")
        
        # Simulation de l'arrêt
        await asyncio.sleep(1)
        
        # Mettre à jour le registre
        if service_name in self.service_registry:
            self.service_registry[service_name]["status"] = "stopped"
        
        return {
            "service": service_name,
            "status": "stopped",
            "timestamp": time.time()
        }
    
    async def _handle_service_restart(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handler pour redémarrer un service"""
        service_name = params.get("service")
        logger.info(f"🔄 Redémarrage du service {service_name}")
        
        # Arrêter puis redémarrer
        await self._handle_service_stop({"service": service_name})
        await self._handle_service_start(params)
        
        return {
            "service": service_name,
            "status": "restarted",
            "timestamp": time.time()
        }
    
    async def _handle_service_status(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handler pour obtenir le statut d'un service"""
        service_name = params.get("service")
        
        if service_name in self.service_registry:
            return self.service_registry[service_name]
        else:
            return {
                "service": service_name,
                "status": "unknown",
                "timestamp": time.time()
            }
    
    async def _handle_config_get(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handler pour obtenir une configuration"""
        config_key = params.get("key")
        
        # Simuler la récupération de configuration
        configs = {
            "api": {"port": 8000, "debug": True},
            "frontend": {"port": 8501, "theme": "light"},
            "ml": {"model_path": "models/eta_model.pkl"}
        }
        
        return {
            "key": config_key,
            "value": configs.get(config_key, {}),
            "timestamp": time.time()
        }
    
    async def _handle_config_set(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handler pour définir une configuration"""
        config_key = params.get("key")
        config_value = params.get("value")
        
        logger.info(f"⚙️ Configuration mise à jour: {config_key} = {config_value}")
        
        return {
            "key": config_key,
            "value": config_value,
            "status": "updated",
            "timestamp": time.time()
        }
    
    async def _handle_health_check(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handler pour vérifier la santé des services"""
        service_name = params.get("service", "all")
        
        if service_name == "all":
            health_status = {}
            for service in self.service_registry:
                health_status[service] = {
                    "status": "healthy",
                    "response_time": 0.1,
                    "timestamp": time.time()
                }
            return health_status
        else:
            return {
                "service": service_name,
                "status": "healthy",
                "response_time": 0.1,
                "timestamp": time.time()
            }
    
    async def _handle_metrics_get(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handler pour obtenir les métriques"""
        return {
            "services_count": len(self.service_registry),
            "messages_processed": len(self.message_queue),
            "uptime": time.time(),
            "timestamp": time.time()
        }
    
    async def _handle_orchestration_plan(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handler pour planifier l'orchestration"""
        services = params.get("services", ["api", "frontend", "ml"])
        
        # Créer un plan d'orchestration
        plan = {
            "steps": [
                {"service": "api", "action": "start", "priority": 1},
                {"service": "ml", "action": "start", "priority": 2, "depends_on": ["api"]},
                {"service": "frontend", "action": "start", "priority": 3, "depends_on": ["api"]}
            ],
            "estimated_duration": 10,
            "timestamp": time.time()
        }
        
        return plan
    
    async def _handle_orchestration_execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handler pour exécuter un plan d'orchestration"""
        plan = params.get("plan")
        
        logger.info("🎯 Exécution du plan d'orchestration")
        
        results = []
        for step in plan.get("steps", []):
            service = step["service"]
            action = step["action"]
            
            # Exécuter l'action
            if action == "start":
                result = await self._handle_service_start({"service": service})
            elif action == "stop":
                result = await self._handle_service_stop({"service": service})
            elif action == "restart":
                result = await self._handle_service_restart({"service": service})
            
            results.append(result)
        
        return {
            "plan_executed": True,
            "results": results,
            "timestamp": time.time()
        }
    
    async def send_message(self, method: str, params: Dict[str, Any]) -> str:
        """Envoie un message MCP"""
        message_id = f"msg_{int(time.time() * 1000)}"
        
        message = MCPMessage(
            id=message_id,
            type=MCPMessageType.REQUEST,
            method=method,
            params=params
        )
        
        self.message_queue.append(message)
        return message_id
    
    async def _publish_response(self, response: MCPMessage):
        """Publie une réponse MCP"""
        # Simuler la publication
        logger.info(f"📤 Réponse publiée: {response.id}")
        
        # Notifier les subscribers
        if response.method in self.subscribers:
            for subscriber in self.subscribers[response.method]:
                try:
                    await subscriber(response)
                except Exception as e:
                    logger.error(f"Erreur subscriber {response.method}: {e}")
    
    async def _publish_notification(self, event: str, data: Dict[str, Any]):
        """Publie une notification MCP"""
        notification = MCPMessage(
            id=f"notif_{int(time.time() * 1000)}",
            type=MCPMessageType.NOTIFICATION,
            method=event,
            params=data
        )
        
        logger.info(f"📢 Notification: {event}")
        
        # Notifier les subscribers
        if event in self.subscribers:
            for subscriber in self.subscribers[event]:
                try:
                    await subscriber(notification)
                except Exception as e:
                    logger.error(f"Erreur subscriber {event}: {e}")
    
    def subscribe(self, event: str, callback: Callable):
        """S'abonne à un événement MCP"""
        if event not in self.subscribers:
            self.subscribers[event] = []
        self.subscribers[event].append(callback)
    
    def get_resources(self) -> List[Dict[str, Any]]:
        """Retourne toutes les ressources MCP"""
        return [asdict(resource) for resource in self.resources.values()]
    
    def get_status(self) -> Dict[str, Any]:
        """Retourne le statut de l'orchestrateur MCP"""
        return {
            "orchestrator": {
                "type": "mcp",
                "status": "running",
                "resources_count": len(self.resources),
                "services_count": len(self.service_registry),
                "messages_in_queue": len(self.message_queue)
            },
            "services": self.service_registry,
            "timestamp": time.time()
        }

# Instance globale de l'orchestrateur MCP
mcp_orchestrator = MCPOrchestrator()

async def start_mcp_orchestration():
    """Point d'entrée pour démarrer l'orchestration MCP"""
    await mcp_orchestrator.start()

if __name__ == "__main__":
    asyncio.run(start_mcp_orchestration())





