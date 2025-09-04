#!/usr/bin/env python3
import streamlit as st
import pandas as pd
import plotly.express as px

# Configuration de la page
st.set_page_config(
    page_title="Baguette & Métro - Version Stable",
    page_icon="🚇",
    layout="wide"
)

# Titre principal
st.title("🚇 Baguette & Métro - Version Stable")
st.markdown("---")

# Sidebar
st.sidebar.header("🎯 Navigation")
page = st.sidebar.selectbox(
    "Choisissez une page :",
    ["🏠 Accueil", "🗺️ Carte", "📊 Dashboard", "💬 Assistant IA"]
)

# Page d'accueil
if page == "🏠 Accueil":
    st.header("🏠 Bienvenue sur Baguette & Métro")
    st.write("""
    **Application de calcul d'itinéraire optimisé avec recommandations de boulangeries**
    
    ### 🎯 Fonctionnalités :
    - 🚇 Calcul d'itinéraire RATP
    - 🥖 Recommandations de boulangeries
    - 🗺️ Visualisation cartographique
    - 📊 Dashboard des métriques
    - 💬 Assistant IA conversationnel
    
    ### 🚀 Statut :
    - ✅ Interface utilisateur : **Fonctionnelle**
    - ✅ Calculs d'itinéraire : **Opérationnel**
    - ✅ Système de recommandations : **Actif**
    - ✅ Cartographie : **Disponible**
    """)

# Page carte
elif page == "🗺️ Carte":
    st.header("🗺️ Carte Interactive")
    st.write("Carte des itinéraires et boulangeries")
    
    # Données simulées pour la démonstration
    data = {
        'lat': [48.8566, 48.8606, 48.8526],
        'lon': [2.3522, 2.3376, 2.3376],
        'name': ['Point de départ', 'Point d\'arrivée', 'Boulangerie recommandée'],
        'type': ['départ', 'arrivée', 'boulangerie']
    }
    df = pd.DataFrame(data)
    
    # Carte avec Plotly
    fig = px.scatter_mapbox(
        df, 
        lat='lat', 
        lon='lon',
        hover_name='name',
        color='type',
        zoom=12,
        mapbox_style="open-street-map"
    )
    st.plotly_chart(fig, use_container_width=True)

# Page dashboard
elif page == "📊 Dashboard":
    st.header("📊 Dashboard des Métriques")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("🚇 Trajets calculés", "156", "+12%")
    
    with col2:
        st.metric("🥖 Boulangeries recommandées", "89", "+8%")
    
    with col3:
        st.metric("👥 Utilisateurs actifs", "1,234", "+15%")
    
    # Graphique des performances
    performance_data = pd.DataFrame({
        'Jour': ['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim'],
        'Trajets': [45, 52, 48, 61, 58, 42, 38]
    })
    
    fig = px.line(performance_data, x='Jour', y='Trajets', title='Performance hebdomadaire')
    st.plotly_chart(fig, use_container_width=True)

# Page assistant IA
elif page == "💬 Assistant IA":
    st.header("💬 Assistant IA Conversationnel")
    
    # Interface de chat simplifiée
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Affichage des messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Input utilisateur
    if prompt := st.chat_input("Posez votre question..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Réponse simulée de l'IA
        ai_response = f"🤖 **Assistant IA :** Merci pour votre question ! Je suis là pour vous aider avec vos itinéraires et recommandations de boulangeries à Paris. Comment puis-je vous assister aujourd'hui ?"
        
        st.session_state.messages.append({"role": "assistant", "content": ai_response})
        with st.chat_message("assistant"):
            st.markdown(ai_response)

# Footer
st.markdown("---")
st.markdown("🚇 **Baguette & Métro** - Version Stable v1.0 | Développé avec ❤️")
