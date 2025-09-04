#!/bin/bash

# Script d'optimisation pour démarrer le serveur Baguette & Métro
# Évite les problèmes de port occupé et redémarre proprement

echo "🚀 Démarrage optimisé du serveur Baguette & Métro"

# 1. Tuer tous les processus Python liés au serveur
echo "🔄 Nettoyage des processus existants..."
pkill -f "python server_secure.py" 2>/dev/null
pkill -f "server_secure.py" 2>/dev/null

# 2. Libérer le port 8000
echo "🔓 Libération du port 8000..."
lsof -ti:8000 | xargs kill -9 2>/dev/null

# 3. Attendre que le port soit libéré
echo "⏳ Attente de libération du port..."
sleep 3

# 4. Vérifier que le port est libre
if lsof -i:8000 >/dev/null 2>&1; then
    echo "❌ Le port 8000 est encore occupé. Tentative de libération forcée..."
    sudo lsof -ti:8000 | xargs sudo kill -9 2>/dev/null
    sleep 2
fi

# 5. Démarrer le serveur
echo "🚀 Démarrage du serveur..."
python server_secure.py

echo "✅ Serveur démarré avec succès !"

