# ui/components/level_badge.py - VERSIÓN CORREGIDA
import streamlit as st
import plotly.graph_objects as go
from typing import Dict, Any, Optional
from core.services.gamification_service import GamificationService

class LevelBadge:
    """
    Componente optimizado para mostrar nivel y progreso del usuario.
    Integrado con GamificationService - Duolingo-style.
    """
    
    def __init__(self):
        self.gamification_service = GamificationService()
    
    def render_compact(self, user_id: str = "default_user") -> None:
        """Versión compacta para sidebar o headers"""
        try:
            progress = self.gamification_service.get_user_progress()
            
            if not progress:
                self._render_fallback()
                return
            
            # ✅ CORREGIDO: Usar columnas más balancedas
            col1, col2, col3 = st.columns([3, 2, 2])
            
            with col1:
                level = progress["level"]
                progress_pct = progress["progress_percentage"]
                
                st.markdown(f"**Nivel {level}**")
                # ✅ CORREGIDO: Asegurar que progress_pct esté entre 0-100
                safe_progress = max(0, min(100, progress_pct))
                st.progress(safe_progress / 100.0)
                st.caption(f"{safe_progress:.0f}%")
            
            with col2:
                streak = progress["streak"]["current"]
                streak_emoji = self._get_streak_emoji(streak)
                st.markdown(f"{streak_emoji} **{streak}**")
                st.caption("días")
            
            with col3:
                points = progress["points"]
                st.markdown(f"⭐ **{points}**")
                st.caption("puntos")
                
        except Exception as e:
            st.error("❌ Error cargando progreso")
            # Fallback mínimo
            st.progress(0)
            st.caption("Nivel 1 - 0%")
    
    def render_detailed(self, user_id: str = "default_user") -> None:
        """Versión detallada para dashboard principal"""
        try:
            progress = self.gamification_service.get_user_progress()
            
            if not progress:
                self._render_fallback()
                return
            
            # Header principal
            st.markdown("### 🏆 Tu Progreso")
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                self._render_level_gauge(progress)
            
            with col2:
                self._render_quick_stats(progress)
            
            # Stats detalladas
            self._render_detailed_stats(progress)
            
        except Exception as e:
            st.error("❌ Error cargando progreso detallado")
            self._render_fallback()
    
    def _render_level_gauge(self, progress: Dict[str, Any]) -> None:
        """Renderiza gauge de nivel con Plotly - VERSIÓN CORREGIDA"""
        try:
            level = progress["level"]
            level_info = progress["level_info"]
            progress_pct = progress["progress_percentage"]
            next_level_points = progress["next_level_points"]
            current_points = progress["points"]
            
            # ✅ CORREGIDO: Asegurar valores válidos
            safe_progress = max(0, min(100, progress_pct))
            points_to_next = max(0, next_level_points - current_points)
            
            # Crear gauge
            fig = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=safe_progress,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={
                    'text': f"{level_info['name']}",
                    'font': {'size': 16, 'color': '#2E86AB'}
                },
                delta={'reference': 0},
                gauge={
                    'axis': {'range': [None, 100], 'tickwidth': 1},
                    'bar': {'color': "#4CAF50"},
                    'bgcolor': "white",
                    'borderwidth': 2,
                    'bordercolor': "gray",
                    'steps': [
                        {'range': [0, 33], 'color': '#FFE66D'},
                        {'range': [33, 66], 'color': '#6A8EAE'},
                        {'range': [66, 100], 'color': '#4CAF50'}
                    ],
                },
                number={
                    'font': {'size': 24},
                    'suffix': '%'
                }
            ))
            
            fig.update_layout(
                height=250,
                margin=dict(l=20, r=20, t=50, b=20),
                paper_bgcolor='rgba(0,0,0,0)',
                font={'family': "Arial, sans-serif"}
            )
            
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
            
            # Info de progreso
            cols = st.columns(3)
            with cols[0]:
                st.metric("Nivel Actual", level)
            with cols[1]:
                st.metric("Progreso", f"{safe_progress:.1f}%")
            with cols[2]:
                st.metric("Siguiente", f"{points_to_next} pts")
                
        except Exception as e:
            # Fallback simple si Plotly falla
            st.warning("📊 Cargando medidor de progreso...")
            progress_pct = progress.get("progress_percentage", 0)
            st.progress(progress_pct / 100.0)
            st.caption(f"Progreso: {progress_pct:.1f}%")
    
    def _render_quick_stats(self, progress: Dict[str, Any]) -> None:
        """Renderiza stats rápidas en tarjeta lateral"""
        try:
            streak = progress["streak"]
            engagement = progress["engagement"]
            
            st.markdown("### 📊 Stats Rápidas")
            
            # Tarjeta de rachas
            with st.container():
                st.markdown("#### 🔥 Rachas")
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric(
                        "Actual", 
                        f"{streak['current']}",
                        help="Días consecutivos activo"
                    )
                
                with col2:
                    st.metric(
                        "Récord", 
                        f"{streak['longest']}",
                        delta=None,
                        help="Tu mejor racha histórica"
                    )
            
            st.markdown("---")
            
            # Tarjeta de engagement
            with st.container():
                st.markdown("#### 📈 Engagement")
                
                st.metric(
                    "Días Activos",
                    f"{engagement.get('total_active_days', 0)}",
                    help="Total de días con actividad"
                )
                
                engagement_rate = engagement.get('engagement_rate', 0)
                st.metric(
                    "Tasa Engagement",
                    f"{engagement_rate:.1f}%",
                    help="Actividad últimos 30 días"
                )
                
        except Exception as e:
            st.error("Error cargando stats rápidas")
    
    def _render_detailed_stats(self, progress: Dict[str, Any]) -> None:
        """Renderiza estadísticas detalladas expandibles"""
        try:
            with st.expander("📈 Estadísticas Detalladas", expanded=False):
                streak = progress["streak"]
                protections = progress["protections"]
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown("**🎯 Progreso**")
                    st.write(f"Puntos Totales: **{progress['points']}**")
                    st.write(f"Días de Rachas: **{streak.get('total_days', 0)}**")
                    st.write(f"Próximo Nivel: **{progress['next_level_points']} pts**")
                
                with col2:
                    st.markdown("**🛡️ Protecciones**")
                    freeze_status = "✅ Disponible" if protections.get("freeze_available", True) else "❌ Usada"
                    recovery_status = "✅ Disponible" if protections.get("recovery_available", True) else "❌ Usada"
                    
                    st.write(f"Congelar Rachas: {freeze_status}")
                    st.write(f"Recuperar Rachas: {recovery_status}")
                
                with col3:
                    st.markdown("**📊 Engagement**")
                    st.write(f"Racha Actual: **{streak['current']} días**")
                    st.write(f"Mejor Racha: **{streak['longest']} días**")
                    engagement_rate = progress["engagement"].get("engagement_rate", 0)
                    st.write(f"Tasa: **{engagement_rate:.1f}%**")
                    
        except Exception as e:
            st.error("Error cargando stats detalladas")
    
    def _get_streak_emoji(self, streak_days: int) -> str:
        """Devuelve emoji contextual basado en racha"""
        if streak_days == 0:
            return "💤"
        elif streak_days < 3:
            return "🔥"
        elif streak_days < 7:
            return "🚀"
        elif streak_days < 14:
            return "⚡"
        elif streak_days < 30:
            return "🌟"
        else:
            return "🏆"
    
    def _render_fallback(self) -> None:
        """Renderizado fallback cuando hay errores"""
        st.warning("🚀 Comienza tu journey financiero!")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Nivel", "1")
            st.progress(0)
            st.caption("0%")
        
        with col2:
            st.metric("Racha", "0 días")
        
        with col3:
            st.metric("Puntos", "0")
        
        st.info("💡 Registra tu primera transacción para desbloquear stats!")

# Función de utilidad para uso rápido
def render_level_badge(compact: bool = True, user_id: str = "default_user") -> None:
    """
    Función rápida para renderizar el badge de nivel.
    
    Args:
        compact: Si True, versión compacta para sidebar
        user_id: ID del usuario (default para MVP)
    """
    badge = LevelBadge()
    
    if compact:
        badge.render_compact(user_id)
    else:
        badge.render_detailed(user_id)