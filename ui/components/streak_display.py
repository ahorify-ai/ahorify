# ui/components/streak_display.py
import streamlit as st
import plotly.graph_objects as go
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional
from core.services.gamification_service import GamificationService

class StreakDisplay:
    """
    Componente visual optimizado para mostrar rachas Duolingo-style.
    Integrado con GamificationService - Sistema de engagement core.
    """
    
    def __init__(self):
        self.gamification_service = GamificationService()
    
    def render(self, user_id: str = "default_user", compact: bool = False) -> None:
        """
        Renderiza el display de rachas.
        
        Args:
            user_id: ID del usuario
            compact: Si True, versión simplificada para espacios reducidos
        """
        if compact:
            self._render_compact_streak(user_id)
        else:
            self._render_full_streak(user_id)
    
    def _render_full_streak(self, user_id: str) -> None:
        """Versión completa con calendario visual y analytics"""
        try:
            progress = self.gamification_service.get_user_progress()
            
            if not progress:
                self._render_streak_fallback()
                return
            
            streak_data = progress["streak"]
            engagement_data = progress["engagement"]
            
            # Header principal
            st.markdown("### 🔥 Tu Racha de Consistencia")
            
            # Stats principales
            col1, col2, col3 = st.columns(3)
            
            with col1:
                self._render_current_streak(streak_data["current"])
            
            with col2:
                self._render_longest_streak(streak_data["longest"])
            
            with col3:
                self._render_streak_calendar(streak_data["current"])
            
            # Progreso hacia hitos
            st.markdown("#### 🎯 Próximos Hitos")
            self._render_streak_milestones(streak_data["current"])
            
            # Insights y motivación
            st.markdown("#### 💡 Tu Momentum")
            self._render_streak_insights(streak_data, engagement_data)
            
        except Exception as e:
            st.error("❌ Error cargando datos de racha")
    
    def _render_compact_streak(self, user_id: str) -> None:
        """Versión compacta para sidebar o cards"""
        try:
            progress = self.gamification_service.get_user_progress()
            
            if not progress:
                return
            
            streak_data = progress["streak"]
            current_streak = streak_data["current"]
            
            # Mini visualización de racha
            st.markdown("#### 🔥 Racha Actual")
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                streak_emoji = self._get_streak_emoji(current_streak)
                st.markdown(f"### {streak_emoji} **{current_streak} días**")
                
                # Mini progreso
                next_milestone = self._get_next_milestone(current_streak)
                if next_milestone:
                    days_left = next_milestone - current_streak
                    progress_pct = (current_streak / next_milestone) * 100
                    st.progress(progress_pct / 100)
                    st.caption(f"{days_left} días para {next_milestone}")
            
            with col2:
                st.metric(
                    "Mejor Racha", 
                    f"{streak_data['longest']}",
                    delta=None
                )
            
            # Mensaje motivacional rápido
            st.caption(f"💬 {self._get_motivational_message(current_streak)}")
            
        except Exception:
            # Fallback silencioso en compacto
            pass
    
    def _render_current_streak(self, current_streak: int) -> None:
        """Renderiza la racha actual con visual impactante"""
        streak_emoji = self._get_streak_emoji(current_streak)
        
        st.metric(
            label="Racha Actual",
            value=f"{streak_emoji} {current_streak} días",
            delta=None,
            help="Días consecutivos usando Ahorify"
        )
        
        # Badge de nivel de racha
        streak_level = self._get_streak_level(current_streak)
        st.caption(f"**{streak_level}**")
    
    def _render_longest_streak(self, longest_streak: int) -> None:
        """Renderiza la mejor racha histórica"""
        st.metric(
            label="Mejor Racha",
            value=f"🏆 {longest_streak} días",
            delta=None,
            help="Tu récord personal de consistencia"
        )
        
        # Porcentaje vs actual
        if longest_streak > 0:
            st.caption(f"**{longest_streak}** días de récord")
    
    def _render_streak_calendar(self, current_streak: int) -> None:
        """Renderiza calendario visual de rachas de 7 días"""
        st.metric(
            label="Días Activos",
            value=f"📅 {self._calculate_active_days(current_streak)}",
            delta=None,
            help="Días con actividad esta semana"
        )
        
        # Mini calendario de esta semana
        self._render_week_calendar()
    
    def _render_week_calendar(self) -> None:
        """Mini calendario de la semana actual"""
        days = ["L", "M", "X", "J", "V", "S", "D"]
        today = datetime.today().weekday()
        
        cols = st.columns(7)
        for i, col in enumerate(cols):
            with col:
                if i <= today:
                    # Días pasados y hoy - asumimos activos por simplicidad
                    # En implementación real, verificaríamos daily_engagement
                    st.markdown(f"<div style='text-align: center; background: #4CAF50; color: white; border-radius: 50%; width: 30px; height: 30px; line-height: 30px; margin: 0 auto;'>✓</div>", 
                              unsafe_allow_html=True)
                else:
                    # Días futuros
                    st.markdown(f"<div style='text-align: center; background: #f0f0f0; border-radius: 50%; width: 30px; height: 30px; line-height: 30px; margin: 0 auto;'>{days[i]}</div>", 
                              unsafe_allow_html=True)
                st.caption(days[i])
    
    def _render_streak_milestones(self, current_streak: int) -> None:
        """Renderiza hitos de racha y progreso"""
        milestones = [3, 7, 14, 30, 60, 90]
        
        for milestone in milestones:
            col1, col2, col3 = st.columns([1, 3, 1])
            
            with col1:
                if current_streak >= milestone:
                    st.success("✅")
                else:
                    st.info(f"{milestone}d")
            
            with col2:
                if current_streak >= milestone:
                    st.progress(1.0)
                    st.caption(f"**{milestone} días** - ¡Hito alcanzado! 🎉")
                else:
                    progress = min(current_streak / milestone, 1.0)
                    days_left = milestone - current_streak
                    st.progress(progress)
                    st.caption(f"**{milestone} días** - {days_left} días restantes")
            
            with col3:
                reward = self._get_milestone_reward(milestone)
                st.caption(f"+{reward} pts")
    
    def _render_streak_insights(self, streak_data: Dict, engagement_data: Dict) -> None:
        """Renderiza insights personalizados basados en rachas"""
        current_streak = streak_data["current"]
        longest_streak = streak_data["longest"]
        engagement_rate = engagement_data["engagement_rate"]
        
        # Insights basados en datos
        insights = []
        
        if current_streak == 0:
            insights.append("**¡Comienza hoy!** Registra tu primera transacción para iniciar tu racha.")
        
        elif current_streak < 3:
            insights.append(f"**¡Vas por {current_streak} día(s)!** La consistencia es clave - sigue así!")
        
        elif current_streak < 7:
            insights.append(f"**¡{current_streak} días seguidos!** Estás construyendo un hábito sólido. 🚀")
        
        elif current_streak < 14:
            insights.append(f"**¡1 semana completa!** Tu consistencia está dando resultados. 💫")
        
        else:
            insights.append(f"**¡{current_streak} días!** Eres un ejemplo de disciplina financiera. 🏆")
        
        # Insight sobre récord
        if current_streak == longest_streak and current_streak > 0:
            insights.append("**¡Estás en tu mejor racha histórica!** Mantén este momentum. 🌟")
        
        # Insight sobre engagement
        if engagement_rate > 80:
            insights.append("**Tasa de engagement excelente.** Tu compromiso es admirable. 💎")
        
        # Mostrar insights
        for insight in insights[:3]:  # Máximo 3 insights
            st.info(insight)
        
        # Próximo hito destacado
        next_milestone = self._get_next_milestone(current_streak)
        if next_milestone:
            days_to_go = next_milestone - current_streak
            st.success(f"**Próximo hito:** {next_milestone} días - {days_to_go} por delante 💪")
    
    def _render_streak_fallback(self) -> None:
        """Renderizado cuando no hay datos de racha"""
        st.warning("🚀 Inicia tu Aventura Financiera")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Racha Actual", "0 días")
            st.progress(0)
        
        with col2:
            st.metric("Mejor Racha", "0 días")
        
        st.info("""
        **💡 Comienza tu racha hoy:**
        - Registra tu primera transacción
        - Vuelve mañana para mantenerla
        - La consistencia construye hábitos poderosos
        """)
    
    def _get_streak_emoji(self, streak_days: int) -> str:
        """Devuelve emoji contextual para la racha"""
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
    
    def _get_streak_level(self, streak_days: int) -> str:
        """Nivel de racha basado en días consecutivos"""
        if streak_days == 0:
            return "Principiante"
        elif streak_days < 3:
            return "En Marcha"
        elif streak_days < 7:
            return "Consistente"
        elif streak_days < 14:
            return "Comprometido"
        elif streak_days < 30:
            return "Experto"
        else:
            return "Leyenda"
    
    def _calculate_active_days(self, current_streak: int) -> int:
        """Calcula días activos esta semana (simplificado)"""
        return min(current_streak, 7)  # En implementación real, usaría daily_engagement
    
    def _get_next_milestone(self, current_streak: int) -> Optional[int]:
        """Encuentra el próximo hito de racha"""
        milestones = [3, 7, 14, 30, 60, 90]
        for milestone in milestones:
            if current_streak < milestone:
                return milestone
        return None
    
    def _get_milestone_reward(self, milestone: int) -> int:
        """Puntos de recompensa por hito"""
        rewards = {
            3: 25,
            7: 50, 
            14: 100,
            30: 250,
            60: 400,
            90: 500
        }
        return rewards.get(milestone, 50)
    
    def _get_motivational_message(self, current_streak: int) -> str:
        """Mensaje motivacional contextual"""
        messages = {
            0: "Cada gran racha comienza con un primer paso!",
            1: "Buen comienzo! Mañana vuelve para mantener la racha.",
            2: "Vas por buen camino! La consistencia es clave.",
            3: "¡3 días! Estás construyendo un hábito sólido.",
            7: "¡1 semana completa! Tu disciplina es admirable.",
            14: "¡2 semanas! Eres un ejemplo de consistencia.",
            30: "¡1 MES! Eres una leyenda de la disciplina financiera."
        }
        
        # Encontrar el mensaje más cercano
        for streak in sorted(messages.keys(), reverse=True):
            if current_streak >= streak:
                return messages[streak]
        
        return "¡Sigue construyendo tu futuro financiero!"

# Función de utilidad para uso rápido
def render_streak_display(compact: bool = False, user_id: str = "default_user") -> None:
    """
    Función rápida para renderizar el display de rachas.
    
    Args:
        compact: Si True, versión compacta para sidebar
        user_id: ID del usuario
    """
    streak = StreakDisplay()
    streak.render(compact=compact, user_id=user_id)