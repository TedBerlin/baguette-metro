#!/usr/bin/env python3
"""
Orchestrateur Principal pour Baguette Metro
Peut choisir entre main.py classique, Agentic Planner, ou MCP
"""

import asyncio
import logging
import os
from typing import Dict, Any, Optional
from enum import Enum
import time

# Import des différents orchestrateurs
from .agentic_planner import AgenticPlanner, orchestrator as agentic_orchestrator
from .mcp_orchestrator import MCPOrchestrator, mcp_orchestrator

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OrchestrationMode(Enum):
    """Modes d'orchestration disponibles"""
    CLASSIC = "classic"  # main.py simple
    AGENTIC = "agentic"  # Planner intelligent
    MCP = "mcp"         # Model Context Protocol
    HYBRID = "hybrid"   # Combinaison des approches

class MainOrchestrator:
    """
    Orchestrateur principal qui peut choisir entre différentes approches
    """
    
    def __init__(self, mode: OrchestrationMode = None):
        self.mode = mode or self._detect_best_mode()
        self.agentic_planner: Optional[AgenticPlanner] = None
        self.mcp_orchestrator: Optional[MCPOrchestrator] = None
        self.classic_services: Dict[str, Any] = {}
        
        logger.info(f"🎯 Orchestrateur initialisé en mode: {self.mode.value}")
        
        # Initialiser selon le mode
        self._initialize_orchestrator()
    
    def _detect_best_mode(self) -> OrchestrationMode:
        """Détecte le meilleur mode d'orchestration"""
        # Vérifier les variables d'environnement
        env_mode = os.getenv("ORCHESTRATION_MODE", "").lower()
        
        if env_mode == "agentic":
            return OrchestrationMode.AGENTIC
        elif env_mode == "mcp":
            return OrchestrationMode.MCP
        elif env_mode == "hybrid":
            return OrchestrationMode.HYBRID
        else:
            # Détection automatique basée sur l'environnement
            if os.getenv("PRODUCTION", "false").lower() == "true":
                return OrchestrationMode.AGENTIC  # Plus robuste en production
            elif os.getenv("DEVELOPMENT", "false").lower() == "true":
                return OrchestrationMode.CLASSIC  # Plus simple en dev
            else:
                return OrchestrationMode.HYBRID  # Par défaut
    
    def _initialize_orchestrator(self):
        """Initialise l'orchestrateur selon le mode"""
        if self.mode in [OrchestrationMode.AGENTIC, OrchestrationMode.HYBRID]:
            self.agentic_planner = agentic_orchestrator
            logger.info("🤖 Agentic Planner initialisé")
        
        if self.mode in [OrchestrationMode.MCP, OrchestrationMode.HYBRID]:
            self.mcp_orchestrator = mcp_orchestrator
            logger.info("📡 MCP Orchestrator initialisé")
        
        if self.mode in [OrchestrationMode.CLASSIC, OrchestrationMode.HYBRID]:
            self._initialize_classic_services()
            logger.info("⚙️ Services classiques initialisés")
    
    def _initialize_classic_services(self):
        """Initialise les services classiques (main.py style)"""
        self.classic_services = {
            "api": {
                "name": "FastAPI",
                "port": 8000,
                "command": "uvicorn src.api.main:app --reload --port 8000",
                "health_endpoint": "/health"
            },
            "frontend": {
                "name": "Streamlit",
                "port": 8501,
                "command": "streamlit run src/frontend/app.py --server.port 8501",
                "health_endpoint": "/_stcore/health"
            },
            "ml_model": {
                "name": "ML Model",
                "port": None,
                "command": None,
                "health_endpoint": "/model/status"
            }
        }
    
    async def start(self):
        """Démarre l'orchestration selon le mode choisi"""
        logger.info(f"🚀 Démarrage de l'orchestration en mode {self.mode.value}")
        
        try:
            if self.mode == OrchestrationMode.CLASSIC:
                await self._start_classic_orchestration()
            elif self.mode == OrchestrationMode.AGENTIC:
                await self._start_agentic_orchestration()
            elif self.mode == OrchestrationMode.MCP:
                await self._start_mcp_orchestration()
            elif self.mode == OrchestrationMode.HYBRID:
                await self._start_hybrid_orchestration()
            
            logger.info("✅ Orchestration démarrée avec succès")
            
        except Exception as e:
            logger.error(f"❌ Erreur lors du démarrage de l'orchestration: {e}")
            raise
    
    async def _start_classic_orchestration(self):
        """Démarre l'orchestration classique (main.py style)"""
        logger.info("⚙️ Démarrage de l'orchestration classique")
        
        # Simulation du démarrage des services
        for service_name, config in self.classic_services.items():
            logger.info(f"🚀 Démarrage de {service_name} sur le port {config['port']}")
            await asyncio.sleep(1)  # Simulation
        
        logger.info("✅ Orchestration classique démarrée")
    
    async def _start_agentic_orchestration(self):
        """Démarre l'orchestration agentic"""
        logger.info("🤖 Démarrage de l'orchestration agentic")
        
        if self.agentic_planner:
            await self.agentic_planner.start_orchestration()
        else:
            raise RuntimeError("Agentic Planner non initialisé")
    
    async def _start_mcp_orchestration(self):
        """Démarre l'orchestration MCP"""
        logger.info("📡 Démarrage de l'orchestration MCP")
        
        if self.mcp_orchestrator:
            await self.mcp_orchestrator.start()
        else:
            raise RuntimeError("MCP Orchestrator non initialisé")
    
    async def _start_hybrid_orchestration(self):
        """Démarre l'orchestration hybride"""
        logger.info("🔄 Démarrage de l'orchestration hybride")
        
        # Démarrer les orchestrateurs en parallèle
        tasks = []
        
        if self.agentic_planner:
            tasks.append(self.agentic_planner.start_orchestration())
        
        if self.mcp_orchestrator:
            tasks.append(self.mcp_orchestrator.start())
        
        # Démarrer les services classiques
        tasks.append(self._start_classic_services_async())
        
        # Exécuter en parallèle
        await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _start_classic_services_async(self):
        """Démarre les services classiques de manière asynchrone"""
        logger.info("⚙️ Démarrage des services classiques")
        
        for service_name, config in self.classic_services.items():
            logger.info(f"🚀 Démarrage de {service_name}")
            await asyncio.sleep(0.5)  # Simulation
    
    async def stop(self):
        """Arrête l'orchestration"""
        logger.info(f"🛑 Arrêt de l'orchestration en mode {self.mode.value}")
        
        try:
            if self.agentic_planner:
                # Arrêter l'agentic planner
                logger.info("🛑 Arrêt de l'Agentic Planner")
            
            if self.mcp_orchestrator:
                # Arrêter le MCP orchestrator
                logger.info("🛑 Arrêt du MCP Orchestrator")
            
            logger.info("✅ Orchestration arrêtée")
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'arrêt: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Retourne le statut de l'orchestrateur"""
        status = {
            "orchestrator": {
                "mode": self.mode.value,
                "status": "running",
                "timestamp": time.time()
            }
        }
        
        # Ajouter les statuts des sous-orchestrateurs
        if self.agentic_planner:
            status["agentic"] = self.agentic_planner.get_status_report()
        
        if self.mcp_orchestrator:
            status["mcp"] = self.mcp_orchestrator.get_status()
        
        if self.classic_services:
            status["classic"] = {
                "services": list(self.classic_services.keys()),
                "count": len(self.classic_services)
            }
        
        return status
    
    async def health_check(self) -> Dict[str, Any]:
        """Vérifie la santé de l'orchestrateur"""
        health_status = {
            "orchestrator": "healthy",
            "mode": self.mode.value,
            "timestamp": time.time()
        }
        
        # Vérifier les sous-orchestrateurs
        if self.agentic_planner:
            try:
                agentic_status = self.agentic_planner.get_status_report()
                health_status["agentic"] = "healthy" if agentic_status else "unhealthy"
            except Exception as e:
                health_status["agentic"] = "error"
                health_status["agentic_error"] = str(e)
        
        if self.mcp_orchestrator:
            try:
                mcp_status = self.mcp_orchestrator.get_status()
                health_status["mcp"] = "healthy" if mcp_status else "unhealthy"
            except Exception as e:
                health_status["mcp"] = "error"
                health_status["mcp_error"] = str(e)
        
        return health_status
    
    def switch_mode(self, new_mode: OrchestrationMode):
        """Change le mode d'orchestration"""
        logger.info(f"🔄 Changement de mode: {self.mode.value} -> {new_mode.value}")
        
        # Arrêter l'orchestration actuelle
        asyncio.create_task(self.stop())
        
        # Changer le mode
        self.mode = new_mode
        
        # Réinitialiser
        self._initialize_orchestrator()
        
        # Redémarrer
        asyncio.create_task(self.start())

# Instance globale de l'orchestrateur principal
main_orchestrator = MainOrchestrator()

async def start_orchestration(mode: str = None):
    """Point d'entrée pour démarrer l'orchestration"""
    if mode:
        mode_enum = OrchestrationMode(mode.lower())
        orchestrator = MainOrchestrator(mode_enum)
    else:
        orchestrator = main_orchestrator
    
    await orchestrator.start()

def get_orchestration_status() -> Dict[str, Any]:
    """Retourne le statut de l'orchestration"""
    return main_orchestrator.get_status()

if __name__ == "__main__":
    import sys
    
    # Mode d'orchestration depuis les arguments
    mode = sys.argv[1] if len(sys.argv) > 1 else None
    
    asyncio.run(start_orchestration(mode))





