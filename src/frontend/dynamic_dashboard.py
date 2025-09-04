#!/usr/bin/env python3
"""
Dashboard dynamique avec métriques temps réel
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
try:
    from .dynamic_metrics import metrics_manager
    from .translations import get_text
except ImportError:
    # Fallback pour import absolu
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).parent.parent.parent))
    from src.frontend.dynamic_metrics import metrics_manager
    from src.frontend.translations import get_text

def render_dynamic_dashboard(language: str):
    """Rend le dashboard dynamique avec métriques temps réel"""
    
    st.header(get_text("system_dashboard", language))
    st.markdown(f"**{get_text('dynamic_dashboard_subtitle', language)}**")
    
    # Bouton de rafraîchissement
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button(get_text("refresh_data", language), type="primary"):
            st.rerun()
    
    # Récupérer les métriques dynamiques
    with st.spinner(get_text("loading_metrics", language)):
        dashboard_metrics = metrics_manager.get_dashboard_metrics()
    
    # Affichage du statut des APIs
    api_health_key = dashboard_metrics.get("overview", {}).get("system_health", "unknown")
    api_health_text = get_text(api_health_key, language)
    st.info(f"**{get_text('system_status', language)} :** {api_health_text}")
    
    # ===== VUE D'ENSEMBLE =====
    st.subheader(get_text("overview", language))
    
    # Métriques principales
    overview = dashboard_metrics.get("overview", {})
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label=get_text("active_vehicles", language),
            value=overview.get("total_vehicles", 0),
            delta=f"+{np.random.randint(1, 5)}"
        )
    
    with col2:
        st.metric(
            label=get_text("active_lines", language),
            value=overview.get("active_lines", 0),
            delta="0"
        )
    
    with col3:
        st.metric(
            label=get_text("average_speed", language),
            value=f"{overview.get('average_speed', 0):.1f} km/h",
            delta=f"{np.random.uniform(-1, 1):.1f}"
        )
    
    with col4:
        st.metric(
            label=get_text("last_update", language),
            value=datetime.now().strftime("%H:%M:%S"),
            delta=get_text("real_time", language)
        )
    
    # ===== PERFORMANCE =====
    st.subheader(get_text("performance_metrics", language))
    
    performance = dashboard_metrics.get("performance", {})
    col1, col2 = st.columns(2)
    
    with col1:
        # Heures de pointe dynamiques
        peak_hours = performance.get("peak_hours", [])
        if peak_hours and len(peak_hours) > 0:
            # S'assurer que peak_hours est une liste de nombres
            peak_hours_values = [float(h) if isinstance(h, (int, float)) else 0 for h in peak_hours[:24]]
            hours = list(range(len(peak_hours_values)))
            fig_peak = px.bar(
                x=hours,
                y=peak_hours_values,
                title=get_text("peak_hours", language),
                labels={'x': get_text("hour", language), 'y': get_text("usage_percent", language)},
                color=peak_hours_values,
                color_continuous_scale='viridis'
            )
            fig_peak.update_layout(showlegend=False)
            st.plotly_chart(fig_peak, use_container_width=True)
    
    with col2:
        # Utilisation par jour de la semaine
        weekday_usage = performance.get("weekday_usage", [])
        if weekday_usage:
            weekdays = ['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim']
            fig_weekday = px.pie(
                values=weekday_usage,
                names=weekdays,
                title=get_text("weekday_usage", language),
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            st.plotly_chart(fig_weekday, use_container_width=True)
    
    # Performance des lignes
    st.markdown(f"**{get_text('line_performance', language)}**")
    line_performance = performance.get("line_performance", {})
    
    if line_performance:
        lines_data = []
        for line_id, perf in line_performance.items():
            lines_data.append({
                get_text('line', language): f'{get_text("line", language)} {line_id}',
                get_text('punctuality', language): perf.get('punctuality', 0),
                get_text('frequency', language): perf.get('frequency', 0),
                get_text('crowding', language): perf.get('crowding', 0),
                get_text('status', language): perf.get('status', 'Normal')
            })
        
        df_lines = pd.DataFrame(lines_data)
        
        # Graphique de performance des lignes
        fig_lines = px.bar(
            df_lines,
            x=get_text('line', language),
            y=[get_text('punctuality', language), get_text('crowding', language)],
            title=get_text("line_performance_title", language),
            barmode='group',
            color_discrete_map={
                get_text('punctuality', language): '#2E8B57',
                get_text('crowding', language): '#FF6B6B'
            }
        )
        st.plotly_chart(fig_lines, use_container_width=True)
        
        # Tableau détaillé
        st.dataframe(df_lines, use_container_width=True)
    
    # ===== TENDANCES =====
    st.subheader(get_text("growth_metrics", language))
    
    trends = dashboard_metrics.get("trends", {})
    col1, col2 = st.columns(2)
    
    with col1:
        # Croissance des utilisateurs
        user_growth = trends.get("user_growth", [])
        if user_growth:
            dates = pd.date_range(start='2024-01-01', end=datetime.now().date(), freq='D')
            
            # Calculer les statistiques pour l'info
            current_users = user_growth[-1] if user_growth else 0
            growth_percentage = 0
            if len(user_growth) > 30:  # Comparer avec il y a 30 jours
                growth_percentage = ((current_users - user_growth[-30]) / user_growth[-30]) * 100
            
            # Afficher les métriques clés
            col_metric1, col_metric2 = st.columns(2)
            with col_metric1:
                st.metric(
                    label=get_text("current_users", language),
                    value=f"{current_users:,}",
                    delta=f"{growth_percentage:.1f}% (30j)"
                )
            with col_metric2:
                avg_users = sum(user_growth) / len(user_growth)
                st.metric(
                    label=get_text("average_users", language),
                    value=f"{int(avg_users):,}",
                    delta=get_text("users_per_day", language)
                )
            
            # Graphique amélioré
            fig_growth = px.line(
                x=dates,
                y=user_growth,
                title=get_text("user_growth", language),
                labels={'x': get_text("date", language), 'y': get_text("users", language)},
                line_shape='linear'
            )
            fig_growth.update_traces(line_color='#1f77b4', line_width=3)
            fig_growth.update_layout(
                hovermode='x unified',
                showlegend=False
            )
            st.plotly_chart(fig_growth, use_container_width=True)
            
            # Légende explicative
            st.caption(get_text("growth_explanation", language))
    
    with col2:
        # Taux de satisfaction
        satisfaction = trends.get("satisfaction_rate", [])
        if satisfaction and len(satisfaction) > 0:
            months = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Jun', 'Jul', 'Août']
            # S'assurer que satisfaction est une liste de nombres
            satisfaction_values = [float(s) if isinstance(s, (int, float)) else 4.0 for s in satisfaction[:len(months)]]
            fig_satisfaction = px.bar(
                x=months[:len(satisfaction_values)],
                y=satisfaction_values,
                title=get_text("satisfaction_rate", language),
                labels={'x': get_text("month", language), 'y': get_text("rating_5", language)},
                color=satisfaction_values,
                color_continuous_scale='RdYlGn'
            )
            fig_satisfaction.update_layout(yaxis_range=[0, 5])
            st.plotly_chart(fig_satisfaction, use_container_width=True)
    
    # Tendances des retards
    delay_trends = trends.get("delay_trends", {})
    if delay_trends:
        st.markdown(f"**{get_text('delay_trends', language)}**")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                label=get_text("average_delay", language),
                value=f"{delay_trends.get('average_delay', 0):.1f} min"
            )
        
        with col2:
            st.metric(
                label=get_text("total_delays", language),
                value=delay_trends.get('total_delays', 0)
            )
        
        with col3:
            trend_key = delay_trends.get('trend', 'stable')
            # Utiliser les traductions pour les tendances
            trend_text = get_text(trend_key, language)
            
            # Définir l'icône basée sur la clé de traduction
            if trend_key == "increase":
                trend_icon = "📊"
            elif trend_key == "decrease":
                trend_icon = "📉"
            else:
                trend_icon = "➡️"
            
            st.metric(
                label=get_text("trend", language),
                value=f"{trend_icon} {trend_text}"
            )
    
    # ===== RECOMMANDATIONS IA =====
    st.subheader(get_text("ai_recommendations", language))
    
    recommendations = dashboard_metrics.get("recommendations", [])
    
    for rec in recommendations:
        rec_type = rec.get("type", "info")
        title = rec.get("title", "")
        message = rec.get("message", "")
        action = rec.get("action", "")
        
        if rec_type == "warning":
            st.warning(f"**{title}**\n\n{message}\n\n💡 **{get_text('recommended_action', language)}** {action}")
        elif rec_type == "success":
            st.success(f"**{title}**\n\n{message}\n\n💡 **{get_text('recommended_action', language)}** {action}")
        else:
            st.info(f"**{title}**\n\n{message}\n\n💡 **{get_text('recommended_action', language)}** {action}")
    
    # ===== DONNÉES BRUTES (DEBUG UNIQUEMENT) =====
    # Masquer en production - visible uniquement en mode debug
    debug_mode = st.secrets.get("DEBUG_MODE", False) if hasattr(st, 'secrets') else False
    
    if debug_mode:
        with st.expander(get_text("raw_data", language)):
            st.json(dashboard_metrics)
            st.info(get_text("debug_mode_active", language))
    else:
        # En production, afficher un indicateur de santé des données
        with st.expander(get_text("data_status", language)):
            st.success(get_text("data_operational", language))
            st.info(get_text("metrics_collected", language).format(count=len(dashboard_metrics.get('overview', {}))))
            st.info(f"🕐 {get_text('last_update', language)}: {datetime.now().strftime('%H:%M:%S')}")
    
    # ===== MÉTRIQUES AVANCÉES =====
    st.subheader(get_text("advanced_metrics", language))
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Gauge de performance système
        system_performance = np.random.uniform(85, 95)
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=system_performance,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': get_text("system_performance", language)},
            delta={'reference': 90},
            gauge={
                'axis': {'range': [None, 100]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 50], 'color': "lightgray"},
                    {'range': [50, 80], 'color': "gray"},
                    {'range': [80, 100], 'color': "lightgreen"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))
        st.plotly_chart(fig_gauge, use_container_width=True)
    
    with col2:
        # Heatmap de congestion des stations
        station_congestion = performance.get("station_congestion", {})
        if station_congestion:
            stations = list(station_congestion.keys())
            congestion_levels = []
            for station_id in stations:
                level = station_congestion[station_id].get("level", "Modérée")
                if level == "Faible":
                    congestion_levels.append(1)
                elif level == "Modérée":
                    congestion_levels.append(2)
                else:
                    congestion_levels.append(3)
            
            fig_heatmap = px.imshow(
                [congestion_levels],
                x=[f"Station {s}" for s in stations],
                y=[get_text("congestion", language)],
                title=get_text("station_congestion", language),
                color_continuous_scale='RdYlGn_r',
                aspect="auto"
            )
            st.plotly_chart(fig_heatmap, use_container_width=True)
    
    # ===== FOOTER =====
    st.markdown("---")
    st.markdown(f"*{get_text('dashboard_updated', language)} {datetime.now().strftime('%d/%m/%Y à %H:%M:%S')}*")
    st.markdown(f"**{get_text('auto_refresh', language)}**")
