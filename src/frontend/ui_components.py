#!/usr/bin/env python3
"""
Composants UI optimisés pour Baguette & Métro
"""

import streamlit as st
from typing import Optional, Dict, Any
import time

def create_loading_indicator(message: str = "Chargement...", key: str = None):
    """Indicateur de chargement optimisé"""
    return st.spinner(f"⏳ {message}")

def create_success_message(message: str, key: str = None):
    """Message de succès avec animation"""
    st.success(f"✅ {message}")

def create_error_message(message: str, key: str = None):
    """Message d'erreur avec style"""
    st.error(f"❌ {message}")

def create_info_box(title: str, content: str, icon: str = "ℹ️"):
    """Boîte d'information stylisée"""
    with st.container():
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 1rem;
            border-radius: 10px;
            color: white;
            margin: 1rem 0;
        ">
            <h4 style="margin: 0 0 0.5rem 0; display: flex; align-items: center;">
                {icon} {title}
            </h4>
            <p style="margin: 0; opacity: 0.9;">{content}</p>
        </div>
        """, unsafe_allow_html=True)

def create_metric_card(title: str, value: str, delta: Optional[str] = None, icon: str = "📊"):
    """Carte de métrique stylisée"""
    with st.container():
        st.markdown(f"""
        <div style="
            background: white;
            padding: 1.5rem;
            border-radius: 15px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            border: 1px solid #e0e0e0;
            margin: 0.5rem 0;
        ">
            <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                <span style="font-size: 1.5rem; margin-right: 0.5rem;">{icon}</span>
                <h3 style="margin: 0; color: #333;">{title}</h3>
            </div>
            <div style="font-size: 2rem; font-weight: bold; color: #1f77b4; margin-bottom: 0.5rem;">
                {value}
            </div>
            {f'<div style="color: #28a745; font-size: 0.9rem;">{delta}</div>' if delta else ''}
        </div>
        """, unsafe_allow_html=True)

def create_action_button(text: str, key: str, disabled: bool = False, primary: bool = True):
    """Bouton d'action optimisé"""
    if primary:
        return st.button(
            text,
            key=key,
            disabled=disabled,
            use_container_width=True,
            type="primary"
        )
    else:
        return st.button(
            text,
            key=key,
            disabled=disabled,
            use_container_width=True
        )

def create_address_input(label: str, placeholder: str, key: str, value: str = ""):
    """Champ de saisie d'adresse optimisé"""
    return st.text_input(
        label,
        placeholder=placeholder,
        key=key,
        value=value,
        help=f"Saisissez votre {label.lower()} pour obtenir des suggestions"
    )

def create_language_selector():
    """Sélecteur de langue optimisé"""
    languages = {
        "🇫🇷 Français": "fr",
        "🇬🇧 English": "en", 
        "🇯🇵 日本語": "ja"
    }
    
    selected = st.selectbox(
        "🌍 Langue / Language / 言語",
        list(languages.keys()),
        index=0,
        key="language_selector"
    )
    
    return languages[selected]

def create_navigation_tabs():
    """Navigation par onglets optimisée"""
    tabs = st.tabs([
        "🏠 Accueil",
        "🗺️ Trajet", 
        "📊 Dashboard",
        "🤖 Assistant IA",
        "ℹ️ À propos"
    ])
    return tabs

def create_progress_bar(progress: float, message: str = "Progression"):
    """Barre de progression stylisée"""
    st.progress(progress, text=f"📈 {message}")

def create_chat_message(message: str, is_user: bool = True, timestamp: str = None):
    """Message de chat stylisé"""
    if is_user:
        st.markdown(f"""
        <div style="
            background: #007bff;
            color: white;
            padding: 0.75rem;
            border-radius: 15px 15px 5px 15px;
            margin: 0.5rem 0;
            text-align: right;
            max-width: 80%;
            margin-left: auto;
        ">
            {message}
            {f'<br><small style="opacity: 0.7;">{timestamp}</small>' if timestamp else ''}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style="
            background: #f8f9fa;
            color: #333;
            padding: 0.75rem;
            border-radius: 15px 15px 15px 5px;
            margin: 0.5rem 0;
            max-width: 80%;
            border: 1px solid #e0e0e0;
        ">
            {message}
            {f'<br><small style="opacity: 0.7;">{timestamp}</small>' if timestamp else ''}
        </div>
        """, unsafe_allow_html=True)

def create_comparison_table(data: Dict[str, Any]):
    """Tableau de comparaison stylisé"""
    st.markdown("""
    <style>
    .comparison-table {
        background: white;
        border-radius: 10px;
        padding: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="comparison-table">', unsafe_allow_html=True)
        st.markdown("### 📊 Comparaison")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Baguette & Métro**")
            for key, value in data.get("baguette_metro", {}).items():
                st.markdown(f"- **{key}:** {value}")
        
        with col2:
            st.markdown("**Citymapper**")
            for key, value in data.get("citymapper", {}).items():
                st.markdown(f"- **{key}:** {value}")
        
        st.markdown('</div>', unsafe_allow_html=True)

def create_map_placeholder():
    """Placeholder pour carte interactive"""
    st.markdown("""
    <div style="
        background: #f0f0f0;
        height: 300px;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        border: 2px dashed #ccc;
        margin: 1rem 0;
    ">
        <div style="text-align: center; color: #666;">
            <h3>🗺️ Carte Interactive</h3>
            <p>Affichage du trajet et des boulangeries</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

def create_mobile_optimized_layout():
    """Layout optimisé pour mobile"""
    st.markdown("""
    <style>
    @media (max-width: 768px) {
        .stButton > button {
            width: 100%;
            height: 3rem;
            font-size: 1.1rem;
        }
        .stTextInput > div > div > input {
            font-size: 1rem;
            padding: 0.75rem;
        }
        .stSelectbox > div > div > select {
            font-size: 1rem;
            padding: 0.5rem;
        }
    }
    </style>
    """, unsafe_allow_html=True)

def create_animated_title(title: str, subtitle: str = None):
    """Titre animé avec gradient"""
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    ">
        <h1 style="
            color: white;
            margin: 0;
            font-size: 2.5rem;
            font-weight: bold;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        ">
            {title}
        </h1>
        {f'<p style="color: rgba(255,255,255,0.9); margin: 1rem 0 0 0; font-size: 1.2rem;">{subtitle}</p>' if subtitle else ''}
    </div>
    """, unsafe_allow_html=True)

def create_feature_card(title: str, description: str, icon: str, color: str = "#667eea"):
    """Carte de fonctionnalité stylisée"""
    st.markdown(f"""
    <div style="
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        border-left: 4px solid {color};
        margin: 1rem 0;
        transition: transform 0.2s;
    ">
        <div style="display: flex; align-items: center; margin-bottom: 1rem;">
            <span style="font-size: 2rem; margin-right: 1rem;">{icon}</span>
            <h3 style="margin: 0; color: #333;">{title}</h3>
        </div>
        <p style="margin: 0; color: #666; line-height: 1.6;">{description}</p>
    </div>
    """, unsafe_allow_html=True)





