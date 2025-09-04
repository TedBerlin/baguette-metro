"""
Module d'orchestration pour Baguette Metro
Offre 3 approches d'orchestration : Classique, Agentic, et MCP
"""

from .main_orchestrator import MainOrchestrator, OrchestrationMode, main_orchestrator
from .agentic_planner import AgenticPlanner, orchestrator as agentic_orchestrator
from .mcp_orchestrator import MCPOrchestrator, mcp_orchestrator

__all__ = [
    "MainOrchestrator",
    "OrchestrationMode", 
    "main_orchestrator",
    "AgenticPlanner",
    "agentic_orchestrator",
    "MCPOrchestrator",
    "mcp_orchestrator"
]

__version__ = "1.0.0"
__author__ = "Baguette Metro Team"
__description__ = "Orchestration moderne pour applications distribuées"





