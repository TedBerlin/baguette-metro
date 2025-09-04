#!/usr/bin/env python3
"""
Configuration Mistral AI pour activation immédiate
MISSION CRITIQUE : Activation de l'assistant IA stratégique
"""
import os

# ============================================================================
# 🔑 CONFIGURATION MISTRAL AI - MISSION CRITIQUE
# ============================================================================

# Clé API Mistral AI (OBLIGATOIRE pour l'activation)
MISTRAL_API_KEY = "pHNgLRN6EgngKlXeq2Ml8MQj96Q6as6Z"  # ✅ CLÉ MISTRAL AI CONFIGURÉE

# ============================================================================
# 🚀 ACTIVATION AUTOMATIQUE
# ============================================================================

def activate_mistral_ai():
    """Active Mistral AI en configurant la variable d'environnement"""
    if MISTRAL_API_KEY != "mistral_api_key_here":
        os.environ['MISTRAL_API_KEY'] = MISTRAL_API_KEY
        print("✅ MISTRAL AI ACTIVÉ - Clé API configurée")
        return True
    else:
        print("❌ MISTRAL AI NON ACTIVÉ - Configurez votre clé API")
        return False

# ============================================================================
# 📋 INSTRUCTIONS D'ACTIVATION
# ============================================================================

if __name__ == "__main__":
    print("🔑 CONFIGURATION MISTRAL AI - MISSION CRITIQUE")
    print("=" * 50)
    print("1. Obtenez votre clé sur : https://console.mistral.ai/")
    print("2. Remplacez 'mistral_api_key_here' par votre vraie clé")
    print("3. Redémarrez le serveur")
    print("4. Mistral AI sera automatiquement activé !")
    print("=" * 50)
    
    if activate_mistral_ai():
        print("🎯 MISTRAL AI PRÊT POUR L'ACTIVATION !")
    else:
        print("⚠️ CONFIGURATION REQUISE AVANT ACTIVATION")
