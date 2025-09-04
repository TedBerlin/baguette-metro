#!/bin/bash

# Script de démarrage robuste pour l'API Baguette & Métro
echo "🚀 Démarrage de l'API Baguette & Métro..."

# Activation de l'environnement virtuel
source ".venv/bin/activate"

# Configuration automatique du PYTHONPATH
export PYTHONPATH="/Users/teddan/Desktop/PSTB/Overview/baguette-metro 2/src/api:$PYTHONPATH"

# Arrêt des processus existants
echo "🧹 Nettoyage des processus existants..."
pkill -f uvicorn 2>/dev/null
sleep 3

# Démarrage de l'API avec configuration robuste
echo "🚀 Démarrage de l'API sur le port 8000..."
cd src/api
uvicorn main:app --host 127.0.0.1 --port 8000 --reload --log-level info &

# Attente du démarrage
echo "⏳ Attente du démarrage..."
sleep 5

# Test de l'API
echo "🧪 Test de l'API..."
if curl -s http://0.0.0.0:8000/health > /dev/null; then
    echo "✅ API démarrée avec succès sur http://0.0.0.0:8000"
    echo "📊 Dashboard: http://0.0.0.0:8000/docs"
else
    echo "❌ Erreur au démarrage de l'API"
    exit 1
fi

echo "🎯 API prête pour le développement !"

