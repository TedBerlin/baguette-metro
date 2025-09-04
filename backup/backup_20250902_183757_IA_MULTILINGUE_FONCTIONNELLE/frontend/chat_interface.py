import streamlit as st
import openai
import json
from typing import Dict, List, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class ChatAssistant:
    """Assistant de chat IA pour Baguette & Métro"""
    
    def __init__(self):
        self.openai_client = None
        self.conversation_history = []
        self.system_prompt = self._get_system_prompt()
        
    def _get_system_prompt(self) -> str:
        """Retourne le prompt système pour l'assistant"""
        return """Tu es l'assistant virtuel de Baguette & Métro, une application qui optimise les trajets RATP avec des arrêts boulangerie.

RÔLE :
- Aide les utilisateurs à planifier leurs trajets
- Suggère les meilleures boulangeries sur le trajet
- Explique les fonctionnalités de l'application
- Répond aux questions sur les transports parisiens

CONNAISSANCES :
- Réseau RATP (métro, RER, bus, tramway)
- Boulangeries parisiennes et leurs spécialités
- Optimisation de trajets urbains
- Fonctionnalités de l'application Baguette & Métro

RÈGLES :
- Sois toujours aimable et serviable
- Donne des réponses précises et utiles
- Suggère des trajets optimisés quand possible
- Recommande des boulangeries selon les préférences
- Utilise le français par défaut, mais peux répondre en anglais si demandé

FONCTIONNALITÉS DISPONIBLES :
- Calcul d'ETA avec et sans arrêt boulangerie
- Recherche de boulangeries à proximité
- Optimisation de trajets RATP
- Support multilingue (FR, EN, JA)
- Données temps réel des transports

EXEMPLES DE RÉPONSES :
- "Je peux vous aider à optimiser votre trajet ! D'où partez-vous et où allez-vous ?"
- "Voici les meilleures boulangeries sur votre trajet : [liste]"
- "Avec un arrêt boulangerie, votre trajet prendra X minutes de plus, mais vous pourrez déguster [spécialité]"
- "L'application utilise l'IA pour calculer les trajets optimaux en temps réel"

N'oublie pas : tu es là pour rendre les trajets parisiens plus agréables avec une pause boulangerie ! 🥖🚇"""
    
    def initialize_client(self, api_key: str):
        """Initialise le client OpenAI"""
        try:
            self.openai_client = openai.OpenAI(
                api_key=api_key,
                base_url="https://openrouter.ai/api/v1"
            )
            return True
        except Exception as e:
            logger.error(f"Erreur d'initialisation du client OpenAI: {e}")
            return False
    
    def get_response(self, user_message: str, context: Optional[Dict] = None) -> str:
        """
        Obtient une réponse de l'assistant IA
        
        Args:
            user_message: Message de l'utilisateur
            context: Contexte supplémentaire (trajet, boulangeries, etc.)
            
        Returns:
            Réponse de l'assistant
        """
        if not self.openai_client:
            return self._get_fallback_response(user_message)
        
        try:
            # Construire le message avec contexte
            full_message = user_message
            if context:
                context_str = json.dumps(context, ensure_ascii=False)
                full_message = f"Contexte: {context_str}\n\nQuestion: {user_message}"
            
            # Ajouter l'historique de conversation
            messages = [{"role": "system", "content": self.system_prompt}]
            
            # Ajouter les 5 derniers messages de l'historique
            for msg in self.conversation_history[-10:]:
                messages.append(msg)
            
            # Ajouter le message actuel
            messages.append({"role": "user", "content": full_message})
            
            # Appel à l'API
            response = self.openai_client.chat.completions.create(
                model="anthropic/claude-3.5-sonnet",
                messages=messages,
                temperature=0.7,
                max_tokens=500
            )
            
            assistant_response = response.choices[0].message.content
            
            # Mettre à jour l'historique
            self.conversation_history.append({"role": "user", "content": user_message})
            self.conversation_history.append({"role": "assistant", "content": assistant_response})
            
            # Limiter l'historique à 20 messages
            if len(self.conversation_history) > 20:
                self.conversation_history = self.conversation_history[-20:]
            
            return assistant_response
            
        except Exception as e:
            logger.error(f"Erreur lors de l'appel à l'API: {e}")
            return self._get_fallback_response(user_message)
    
    def _get_fallback_response(self, user_message: str) -> str:
        """Réponse de fallback quand l'API n'est pas disponible"""
        user_message_lower = user_message.lower()
        
        # Réponses prédéfinies basées sur les mots-clés
        if any(word in user_message_lower for word in ['bonjour', 'hello', 'salut']):
            return "Bonjour ! Je suis l'assistant de Baguette & Métro. Je peux vous aider à optimiser vos trajets RATP avec des arrêts boulangerie. Comment puis-je vous aider ? 🥖🚇"
        
        elif any(word in user_message_lower for word in ['trajet', 'itinéraire', 'route']):
            return "Pour calculer un trajet optimisé, utilisez l'onglet 'Trajet' de l'application. Entrez votre point de départ et d'arrivée, et je vous suggérerai les meilleures boulangeries sur le chemin !"
        
        elif any(word in user_message_lower for word in ['boulangerie', 'pain', 'viennoiserie']):
            return "Les boulangeries sont automatiquement détectées près de votre trajet. L'application vous montrera les meilleures options avec leurs notes et spécialités !"
        
        elif any(word in user_message_lower for word in ['temps', 'durée', 'eta']):
            return "L'application calcule automatiquement les temps de trajet avec et sans arrêt boulangerie. Vous pourrez comparer et choisir l'option qui vous convient le mieux !"
        
        elif any(word in user_message_lower for word in ['aide', 'help', 'comment']):
            return "Voici comment utiliser l'application :\n1. Allez dans l'onglet 'Trajet'\n2. Entrez vos coordonnées de départ et d'arrivée\n3. Cliquez sur 'Calculer le trajet optimal'\n4. Comparez les résultats et choisissez votre option !"
        
        else:
            return "Je suis l'assistant Baguette & Métro ! 🥖🚇\n\nJe peux vous aider avec :\n• Les trajets RATP optimisés\n• Les meilleures boulangeries\n• Les temps de trajet\n• L'utilisation de l'application\n\nPosez-moi une question spécifique ou utilisez les boutons d'action rapide ci-dessous !"


def render_chat_interface():
    """Rend l'interface de chat dans Streamlit"""
    
    # Initialisation de la session
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    if "chat_assistant" not in st.session_state:
        st.session_state.chat_assistant = ChatAssistant()
    
    # Titre de l'interface (pas de doublon car déjà dans l'app principal)
    st.markdown("Posez vos questions sur les trajets et les boulangeries !")
    
    # Message informatif sur l'état de l'IA
    try:
        api_key = st.secrets.get("OPENROUTER_API_KEY", "")
        if api_key and api_key != "your_openrouter_api_key_here":
            st.info("🤖 Assistant IA connecté - Réponses intelligentes disponibles")
        else:
            st.info("🤖 Assistant IA en mode local - Réponses guidées disponibles")
    except Exception:
        st.info("🤖 Assistant IA en mode local - Réponses guidées disponibles")
    
    # Zone de chat
    chat_container = st.container()
    
    with chat_container:
        # Affichage de l'historique
        for message in st.session_state.chat_history:
            if message["role"] == "user":
                with st.chat_message("user"):
                    st.write(message["content"])
            else:
                with st.chat_message("assistant"):
                    st.write(message["content"])
    
    # Zone de saisie
    if prompt := st.chat_input("Posez votre question..."):
        # Ajouter le message utilisateur
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.write(prompt)
        
        # Obtenir la réponse de l'assistant
        with st.chat_message("assistant"):
            with st.spinner("L'assistant réfléchit..."):
                # Initialiser le client si nécessaire
                try:
                    api_key = st.secrets.get("OPENROUTER_API_KEY", "")
                except Exception:
                    api_key = ""
                
                if api_key and api_key != "your_openrouter_api_key_here" and not st.session_state.chat_assistant.openai_client:
                    st.session_state.chat_assistant.initialize_client(api_key)
                
                # Obtenir la réponse
                response = st.session_state.chat_assistant.get_response(prompt)
                st.write(response)
        
        # Ajouter la réponse à l'historique
        st.session_state.chat_history.append({"role": "assistant", "content": response})
    
    # Boutons d'action rapide
    st.markdown("### 🚀 Actions rapides")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("💡 Comment ça marche ?"):
            st.session_state.chat_history.append({"role": "user", "content": "Comment ça marche ?"})
            response = st.session_state.chat_assistant.get_response("Comment ça marche ?")
            st.session_state.chat_history.append({"role": "assistant", "content": response})
            st.rerun()
    
    with col2:
        if st.button("🥖 Meilleures boulangeries"):
            st.session_state.chat_history.append({"role": "user", "content": "Quelles sont les meilleures boulangeries ?"})
            response = st.session_state.chat_assistant.get_response("Quelles sont les meilleures boulangeries ?")
            st.session_state.chat_history.append({"role": "assistant", "content": response})
            st.rerun()
    
    with col3:
        if st.button("🚇 Optimiser trajet"):
            st.session_state.chat_history.append({"role": "user", "content": "Comment optimiser mon trajet ?"})
            response = st.session_state.chat_assistant.get_response("Comment optimiser mon trajet ?")
            st.session_state.chat_history.append({"role": "assistant", "content": response})
            st.rerun()
    
    # Statistiques du chat
    if st.session_state.chat_history:
        st.markdown("---")
        st.markdown(f"**💬 {len(st.session_state.chat_history)} messages échangés**")
        
        # Bouton pour effacer l'historique
        if st.button("🗑️ Effacer l'historique"):
            st.session_state.chat_history = []
            st.rerun()


def get_chat_suggestions() -> List[str]:
    """Retourne des suggestions de questions pour le chat"""
    return [
        "Comment optimiser mon trajet avec une pause boulangerie ?",
        "Quelles sont les meilleures boulangeries près de la Tour Eiffel ?",
        "Combien de temps prend un trajet avec arrêt boulangerie ?",
        "Comment fonctionne l'application Baguette & Métro ?",
        "Quelles sont les spécialités des boulangeries parisiennes ?",
        "Puis-je planifier un trajet pour demain ?",
        "Comment l'IA calcule-t-elle les trajets optimaux ?",
        "Quelles sont les heures de pointe à éviter ?"
    ]
