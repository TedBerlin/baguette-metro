#!/usr/bin/env python3
"""
Package frontend pour Baguette Metro
Contient l'interface utilisateur et les composants dynamiques
"""

# Version du package
__version__ = "1.0.0"

# Imports publics
try:
    from .dynamic_metrics import DynamicMetricsManager, metrics_manager
    from .dynamic_dashboard import render_dynamic_dashboard
except ImportError:
    # Fallback pour les imports
    pass

__all__ = [
    'DynamicMetricsManager',
    'metrics_manager', 
    'render_dynamic_dashboard'
]





