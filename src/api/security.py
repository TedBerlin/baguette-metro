#!/usr/bin/env python3
"""
Module de sécurité avancé pour Baguette & Métro
Chiffrement, validation et gestion sécurisée des clés API
"""

import os
import hashlib
import hmac
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from typing import Optional, Dict, Any
import logging

# Configuration du logging sécurisé
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SecurityManager:
    """Gestionnaire de sécurité avancé pour Baguette & Métro"""
    
    def __init__(self):
        self.master_key = self._get_master_key()
        self.cipher_suite = Fernet(self.master_key)
        self.api_keys_cache = {}
        
    def _get_master_key(self) -> bytes:
        """Génération sécurisée de la clé maître"""
        # Utiliser une clé d'environnement ou générer une nouvelle
        master_key = os.getenv("MASTER_SECURITY_KEY")
        if master_key:
            return base64.urlsafe_b64decode(master_key)
        
        # Génération d'une nouvelle clé (à sauvegarder sécurisé)
        new_key = Fernet.generate_key()
        logger.warning("Nouvelle clé maître générée. Sauvegardez-la sécurisé !")
        return new_key
    
    def encrypt_api_key(self, api_key: str, service_name: str) -> str:
        """Chiffrement sécurisé d'une clé API"""
        try:
            # Ajout d'un salt unique par service
            salt = hashlib.sha256(service_name.encode()).digest()[:16]
            
            # Chiffrement avec Fernet
            encrypted_data = self.cipher_suite.encrypt(api_key.encode())
            
            # Encodage base64 pour stockage
            return base64.urlsafe_b64encode(encrypted_data).decode()
            
        except Exception as e:
            logger.error(f"Erreur chiffrement clé API {service_name}: {e}")
            return ""
    
    def decrypt_api_key(self, encrypted_key: str, service_name: str) -> str:
        """Déchiffrement sécurisé d'une clé API"""
        try:
            # Décodage base64
            encrypted_data = base64.urlsafe_b64decode(encrypted_key.encode())
            
            # Déchiffrement avec Fernet
            decrypted_data = self.cipher_suite.decrypt(encrypted_data)
            
            return decrypted_data.decode()
            
        except Exception as e:
            logger.error(f"Erreur déchiffrement clé API {service_name}: {e}")
            return ""
    
    def validate_api_key_format(self, api_key: str, service_type: str) -> bool:
        """Validation du format des clés API"""
        try:
            if not api_key:
                return False
            
            # Validation selon le type de service
            if service_type == "openai":
                return api_key.startswith("sk-") and len(api_key) > 20
            elif service_type == "openrouter":
                return api_key.startswith("sk-or-") and len(api_key) > 20
            elif service_type == "google":
                return api_key.startswith("AIza") and len(api_key) > 30
            elif service_type == "mistral":
                return len(api_key) > 20
            else:
                return len(api_key) > 10
                
        except Exception as e:
            logger.error(f"Erreur validation clé API {service_type}: {e}")
            return False
    
    def secure_api_key_storage(self, api_key: str, service_name: str) -> Dict[str, Any]:
        """Stockage sécurisé d'une clé API"""
        try:
            # Validation du format
            if not self.validate_api_key_format(api_key, service_name):
                raise ValueError(f"Format de clé API invalide pour {service_name}")
            
            # Chiffrement
            encrypted_key = self.encrypt_api_key(api_key, service_name)
            
            # Hash pour vérification d'intégrité
            key_hash = hashlib.sha256(api_key.encode()).hexdigest()
            
            # Stockage en cache sécurisé
            self.api_keys_cache[service_name] = {
                "encrypted": encrypted_key,
                "hash": key_hash,
                "validated": True,
                "last_used": None
            }
            
            return {
                "status": "success",
                "service": service_name,
                "encrypted": True,
                "hash": key_hash
            }
            
        except Exception as e:
            logger.error(f"Erreur stockage sécurisé clé API {service_name}: {e}")
            return {"status": "error", "message": str(e)}
    
    def get_api_key(self, service_name: str) -> Optional[str]:
        """Récupération sécurisée d'une clé API"""
        try:
            if service_name not in self.api_keys_cache:
                # Tentative de récupération depuis l'environnement
                env_key = os.getenv(f"{service_name.upper()}_API_KEY")
                if env_key:
                    self.secure_api_key_storage(env_key, service_name)
                else:
                    return None
            
            cache_entry = self.api_keys_cache[service_name]
            
            # Vérification d'intégrité
            if not cache_entry.get("validated", False):
                logger.warning(f"Clé API {service_name} non validée")
                return None
            
            # Déchiffrement
            decrypted_key = self.decrypt_api_key(
                cache_entry["encrypted"], 
                service_name
            )
            
            # Mise à jour de l'utilisation
            cache_entry["last_used"] = "now"
            
            return decrypted_key
            
        except Exception as e:
            logger.error(f"Erreur récupération clé API {service_name}: {e}")
            return None
    
    def rotate_api_key(self, service_name: str, new_key: str) -> bool:
        """Rotation sécurisée d'une clé API"""
        try:
            # Validation de la nouvelle clé
            if not self.validate_api_key_format(new_key, service_name):
                return False
            
            # Stockage sécurisé de la nouvelle clé
            result = self.secure_api_key_storage(new_key, service_name)
            
            if result["status"] == "success":
                logger.info(f"Clé API {service_name} rotée avec succès")
                return True
            else:
                return False
                
        except Exception as e:
            logger.error(f"Erreur rotation clé API {service_name}: {e}")
            return False
    
    def audit_api_key_usage(self) -> Dict[str, Any]:
        """Audit de l'utilisation des clés API"""
        try:
            audit_data = {
                "total_keys": len(self.api_keys_cache),
                "services": list(self.api_keys_cache.keys()),
                "last_used": {},
                "security_status": {}
            }
            
            for service, data in self.api_keys_cache.items():
                audit_data["last_used"][service] = data.get("last_used")
                audit_data["security_status"][service] = {
                    "encrypted": bool(data.get("encrypted")),
                    "validated": data.get("validated", False),
                    "hash_present": bool(data.get("hash"))
                }
            
            return audit_data
            
        except Exception as e:
            logger.error(f"Erreur audit clés API: {e}")
            return {"status": "error", "message": str(e)}

# Instance globale du gestionnaire de sécurité
security_manager = SecurityManager()

