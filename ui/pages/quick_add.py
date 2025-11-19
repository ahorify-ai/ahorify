# ui/pages/quick_add.py
import streamlit as st
from datetime import datetime, date
from typing import Dict, Optional
from core.services.transaction_service import TransactionService
from core.services.gamification_service import GamificationService
from ui.components.quick_entry import QuickEntryForm
from ui.components.level_badge import LevelBadge
from ui.components.streak_display import StreakDisplay
from ui.components.progress_bars import ProgressBars
from ui.components.charts import FinancialCharts

class QuickAddPage:
    """
    Página principal de Ahorify - Registro rápido y dashboard minimal.
    Optimizada para móvil, máxima velocidad y engagement.
    """ 
    
    def __init__(self):
        self.transaction_service = TransactionService()
        self.gamification_service = GamificationService()
        self.quick_entry = QuickEntryForm()
        self.level_badge = LevelBadge()
        self.streak_display = StreakDisplay()
        self.progress_bars = ProgressBars()
        self.charts = FinancialCharts()
        
        # Estado de la sesión para persistencia
        if 'last_transaction' not in st.session_state:
            st.session_state.last_transaction = None
        if 'show_tour' not in st.session_state:
            st.session_state.show_tour = True
    
    def render(self) -> None:
        """Renderiza la página principal completa"""
        self._render_sidebar()
        self._render_main_content()
        self._render_bottom_navigation()
    
    def _render_sidebar(self) -> None:
        """Sidebar optimizado para progreso y navegación rápida"""
        with st.sidebar:
            # Header de la sidebar
            st.markdown("""
            <div class="ah-card">
                <h3>🎯 Tu Progreso</h3>
            </div>
            """, unsafe_allow_html=True)
            
            # Progreso principal compacto
            self.level_badge.render_compact()
            
            st.markdown("---")
            
            # Rachas en formato compacto
            self.streak_display.render(compact=True)
            
            st.markdown("---")
            
            # Navegación rápida
            self._render_quick_navigation()
            
            # Stats rápidas
            self._render_quick_stats()
    
    def _render_main_content(self) -> None:
        """Contenido principal MEJORADO - Versión profesional"""
        # Header principal ELEGANTE Y PROFESIONAL
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #1E293B 0%, #334155 100%); 
                    border-radius: 16px; padding: 2rem; margin-bottom: 1.5rem;
                    box-shadow: 0 10px 25px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
                    border: 1px solid rgba(255, 255, 255, 0.1);">
            <div style="text-align: center;">
                <h1 style="font-size: 2.5rem; margin: 0 0 0.5rem 0; 
                        font-weight: 700;">
                    <span style="background: linear-gradient(135deg, #FFFFFF 0%, #E2E8F0 100%); 
                        -webkit-background-clip: text; -webkit-text-fill-color: transparent; 
                        background-clip: text;">Ahorify</span>
                    <span style="color: #FFFFFF;"> 💎</span>
                </h1>
                <p style="font-size: 1.2rem; margin: 0; color: #CBD5E1; font-weight: 500;">
                    Transforma tus finanzas de forma divertida 🚀
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)    
        
        # Tour de bienvenida (solo primera vez)
        if st.session_state.show_tour:
            self._render_welcome_tour()
        
        # Grid principal: Formulario + Feedback
        col1, col2 = st.columns([2, 1])
        
        with col1:
            self._render_quick_entry_section()
        
        with col2:
            self._render_immediate_feedback()
        
        # Transacciones recientes (debajo del formulario)
        self._render_recent_transactions()
    
    def _render_quick_entry_section(self) -> None:
        """Sección de registro rápido optimizada"""
        st.markdown("""
        <div class="ah-card">
            <h2>💸 Registro Ultrarrápido</h2>
            <p style="color: var(--text-secondary); margin-bottom: 0;">
                Registra transacciones en segundos - 1 tap
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Formulario de entrada rápida
        self.quick_entry.render()
    
    def _render_immediate_feedback(self) -> None:
        """Panel de feedback inmediato y gamificación COMPLETO"""
        st.markdown("""
        <div class="ah-card">
            <h3>🚀 Tu Avance</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # 1. Progreso de nivel
        self.progress_bars.render_level_progress()
        
        # 2. Stats principales
        progress = self.gamification_service.get_user_progress()
        if progress:
            col1, col2 = st.columns(2)  # Solo 2 columnas para mejor layout
            
            with col1:
                st.metric(
                    "🔥 Rachas", 
                    f"{progress['streak']['current']}d",
                    help="Días consecutivos activo"
                )
            
            with col2:
                st.metric(
                    "🏆 Puntos", 
                    progress['points'],
                    help="Puntos totales ganados"
                )
        
        # 3. Insights contextuales
        self._render_progress_insights()
    
    # 4. Próximos logros
        self._render_upcoming_achievements()
    
    # 5. Estadísticas de engagement - SIN ANIDACIÓN
        progress = self.gamification_service.get_user_progress()
        if progress:
            engagement = progress.get('engagement', {})
            total_days = engagement.get('total_active_days', 0)
            engagement_rate = engagement.get('engagement_rate', 0)
        
            # if total_days > 0:
            # # 🔥 CORRECCIÓN: Columns directas
            #     engagement_col1, engagement_col2 = st.columns(2)
            #     with engagement_col1:
            #         st.metric("📅 Días activos", total_days)
            #     with engagement_col2:
            #         st.metric("📊 Tasa engagement", f"{engagement_rate:.1f}%")

    def _render_progress_insights(self):
        """Insights y motivación basados en el progreso"""
        progress = self.gamification_service.get_user_progress()
        if not progress:
            return
    
        streak = progress['streak']['current']
        points = progress['points']
    
        if streak == 0:
            st.info("💡 **Comienza tu racha:** Registra una transacción hoy")
        elif streak < 3:
            st.success(f"🚀 **¡Vas por {streak} día(s)!** Sigue así para construir el hábito")
        elif streak < 7:
            st.success(f"🔥 **¡{streak} días seguidos!** Tu consistencia es admirable")
        else:
            st.success(f"🏆 **¡{streak} días!** Eres un ejemplo de disciplina financiera")

    def _render_upcoming_achievements(self):
        """Próximos logros por desbloquear"""
        progress = self.gamification_service.get_user_progress()
        if not progress:
            return
    
        upcoming = []
        current_streak = progress['streak']['current']
        current_points = progress['points']
        current_level = progress['level']
        
        # Próximas rachas
        if current_streak < 3:
            upcoming.append(f"🔥 **Racha de 3 días** - {3 - current_streak} día(s) restante")
        elif current_streak < 7:
            upcoming.append(f"🚀 **Racha de 1 semana** - {7 - current_streak} día(s) restante")
        elif current_streak < 14:
            upcoming.append(f"⚡ **Racha de 2 semanas** - {14 - current_streak} día(s) restante")
        
        # Próximos niveles
        points_needed = progress['next_level_points'] - current_points
        if points_needed > 0:
            upcoming.append(f"⭐ **Nivel {current_level + 1}** - {points_needed} puntos restantes")
        
        # Próximos hitos de puntos
        if current_points < 100:
            upcoming.append(f"🏅 **Primeros 100 puntos** - {100 - current_points} restantes")
        elif current_points < 500:
            upcoming.append(f"🎯 **500 puntos** - {500 - current_points} restantes")
    
        if upcoming:
            with st.expander("🎯 Próximos Logros", expanded=True):
                for achievement in upcoming:
                    st.write(f"• {achievement}")

    # def _render_engagement_stats(self):
    #     """Estadísticas de uso y engagement"""
    #     progress = self.gamification_service.get_user_progress()
    #     if not progress:
    #         return
    
    #     engagement = progress.get('engagement', {})
    #     total_days = engagement.get('total_active_days', 0)
    #     engagement_rate = engagement.get('engagement_rate', 0)
        
    #     if total_days > 0:
    #         col1, col2 = st.columns(2)
    #         with col1:
    #             st.metric("📅 Días activos", total_days)
    #         with col2:
    #             st.metric("📊 Tasa engagement", f"{engagement_rate:.1f}%")

    def _render_daily_rewards(self):
        """Sistema de recompensas diarias"""
        progress = self.gamification_service.get_user_progress()
        if progress and progress['streak']['current'] > 0:
            st.info("""
            🎁 **Recompensa Diaria** 
            Vuelve mañana y gana +15 puntos por mantener tu racha
            """)
        else:
            st.info("""
            🎁 **Recompensa Diaria** 
            Comienza tu racha hoy y gana puntos extra cada día
            """)

    def _render_recent_transactions(self) -> None:
        """Lista de transacciones recientes optimizada"""
        recent_transactions = self.transaction_service.get_recent_transactions(limit=5)
        
        if not recent_transactions:
            st.info("📝 Aún no hay transacciones registradas")
            return
        
        st.markdown("""
        <div class="ah-card">
            <h3>📝 Actividad Reciente</h3>
        </div>
        """, unsafe_allow_html=True)
        
        for transaction in recent_transactions[:3]:
            self._render_transaction_card(transaction)
        
        # Ver más expandible
        if len(recent_transactions) > 3:
            with st.expander("Ver todas las transacciones recientes"):
                for transaction in recent_transactions[3:]:
                    self._render_transaction_card(transaction, compact=True)

    def _render_transaction_card(self, transaction: Dict, compact: bool = False) -> None:
        """SOLUCIÓN DEFINITIVA: Componentes nativos de Streamlit SIN HTML"""
        
        # Configuración de emociones
        emotion_options = {
            "neutral": {"emoji": "😐", "text": "Gasto Neutro"},
            "happy": {"emoji": "😊", "text": "Gasto Feliz"}, 
            "impulsive": {"emoji": "⚡", "text": "Gasto Impulsivo"},
            "stress": {"emoji": "😥", "text": "Gasto por Estrés"},
            "investment": {"emoji": "📈", "text": "Inversión"}
        }
        
        # Obtener datos
        emotion = transaction.get('emotion', 'neutral')
        emotion_data = emotion_options.get(emotion, emotion_options["neutral"])
        
        is_expense = transaction.get("is_expense", True)
        amount_color = "red" if is_expense else "green"
        amount_prefix = "-" if is_expense else "+"

        if compact:
            # Versión compacta
            col1, col2, col3 = st.columns([3, 2, 1])
        
            with col1:
                st.write(f"**{transaction.get('category', 'Sin categoría')}**")
                desc = transaction.get('description', '')
                truncated_desc = f"{desc[:30]}..." if len(desc) > 30 else desc
                st.caption(f"{emotion_data['emoji']} {truncated_desc}")
        
            with col2:
                st.caption(transaction.get('formatted_date', ''))
                st.caption(emotion_data['text'])
        
            with col3:
                st.markdown(
                    f":{amount_color}[**{amount_prefix}{transaction.get('formatted_amount', '0.00')}**]"
                )

        else:
            # SOLUCIÓN: Container nativo con columnas
            with st.container():
            # Layout principal en UNA sola capa
                main_col, amount_col = st.columns([3, 1])
            
            with main_col:
                # Categoría
                st.write(f"**{transaction.get('category', 'Sin categoría')}**")
                
                # Descripción
                desc = transaction.get('description', '')
                if desc and desc != 'Sin descripción':
                    st.caption(desc)
                
                # Emoción y fecha en UNA capa
                emotion_date_col1, emotion_date_col2 = st.columns([2, 1])
                with emotion_date_col1:
                    st.write(f"{emotion_data['emoji']} **{emotion_data['text']}**")
                with emotion_date_col2:
                    st.caption(transaction.get('formatted_date', ''))
            
            with amount_col:
                # Monto con borde visual usando HTML seguro
                border_color = "#EF4444" if is_expense else "#10B981"
                st.markdown(
                    f"""
                    <div style="border-left: 4px solid {border_color}; 
                                padding-left: 8px; height: 100%; 
                                display: flex; align-items: center;">
                        <span style="color: {border_color}; font-weight: bold;">
                            {amount_prefix}{transaction.get('formatted_amount', '0.00')}
                        </span>
                    </div>
                    """, 
                    unsafe_allow_html=True
                )
            
            # Separador nativo
            st.markdown("---")
    
    def _render_last_transaction_preview(self) -> None:
        """Preview última transacción - Versión nativa"""
        if st.session_state.last_transaction:
            transaction = st.session_state.last_transaction
            is_expense = transaction.get("type") == "expense"
            
            with st.container():
                st.caption("📌 Última transacción")
                st.write(f"**{transaction.get('category', 'Sin categoría')}**")
                
                desc = transaction.get('description', '')
                if desc and desc != 'Sin descripción':
                    short_desc = f"{desc[:22]}..." if len(desc) > 22 else desc
                    st.caption(short_desc)
                
                amount_color = "red" if is_expense else "green"
                st.markdown(
                    f":{amount_color}[**{transaction.get('formatted_amount', '0.00')}**]"
                )

    def _render_quick_navigation(self) -> None:
        """Navegación rápida en sidebar"""
        st.markdown("### 🧭 Navegación Rápida")
        
        nav_col1, nav_col2 = st.columns(2)
        
        with nav_col1:
            if st.button("📊 Dashboard", use_container_width=True):
                st.switch_page("pages/dashboard.py")
            
            if st.button("📈 Métricas", use_container_width=True):
                st.switch_page("pages/dashboard.py")
        
        with nav_col2:
            if st.button("📥 Importar", use_container_width=True):
                st.switch_page("pages/import_csv.py")
            
            if st.button("⚙️ Ajustes", use_container_width=True):
                st.info("🔜 Próximamente - Panel de configuración")
    
    def _render_quick_stats(self) -> None:
        """Stats financieras rápidas en sidebar"""
        totals = self.transaction_service.get_totals()
        weekly = self.transaction_service.get_weekly_summary()
        
        st.markdown("### 💰 Resumen Rápido")
        
        # Balance principal
        balance_color = "green" if totals["balance"] >= 0 else "red"
        with st.container():
            st.caption("Balance Total")
            st.markdown(f":{balance_color}[**{totals.get('formatted_balance', '0.00')}**]")
        
        # Métricas rápidas
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Ingresos", totals.get("formatted_income", "0.00"))
        
        with col2:
            st.metric("Gastos", totals.get("formatted_expenses", "0.00"))
        
        # Tendencias semanales
        trend_emoji = "📉" if weekly.get("expense_change", 0) <= 0 else "📈"
        trend_color = "normal" if weekly.get("expense_change", 0) <= 0 else "inverse"
        
        st.metric(
            "Gastos Semanales", 
            weekly.get("formatted_this_week", "0.00"),
            delta=f"{weekly.get('formatted_change', '0.00')} {trend_emoji}",
            delta_color=trend_color
        )
    
    def _render_welcome_tour(self) -> None:
        """Tour de bienvenida para nuevos usuarios"""
        st.markdown("""
        <div class="ah-card ah-card-gamified">
            <h3>🎉 ¡Bienvenido a Ahorify!</h3>
            <p style="margin-bottom: 16px;">
                <strong>🗺️ Tu Aventura Financiera Comienza Aquí:</strong>
            </p>
            <div style="display: grid; gap: 8px;">
                <div>✅ <strong>Registra rápido:</strong> Formulario 1-tap</div>
                <div>🎮 <strong>Gana puntos:</strong> Sube de nivel y mantén rachas</div>
                <div>📈 <strong>Visualiza progreso:</strong> Dashboard gamificado</div>
                <div>🔥 <strong>Mantén la racha:</strong> Vuelve cada día</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Botón para ocultar el tour
        if st.button("🎯 ¡Entendido, comenzar!", use_container_width=True):
            st.session_state.show_tour = False
            st.rerun()
    
    def _render_bottom_navigation(self) -> None:
        """Navegación inferior móvil-first"""
        st.markdown("---")
        
        current_page = st.session_state.get('current_page', 'quick_add')
        
        # Usar columns nativas de Streamlit
        nav_cols = st.columns(4)
        
        with nav_cols[0]:
            if st.button("🏠", 
                        key="mobile_home",
                        use_container_width=True, 
                        help="Inicio",
                        type="primary" if current_page == "quick_add" else "secondary"):
                st.session_state.current_page = "quick_add"
                st.rerun()
        
        with nav_cols[1]:
            if st.button("📊", 
                        key="mobile_dashboard",
                        use_container_width=True, 
                        help="Dashboard",
                        type="primary" if current_page == "dashboard" else "secondary"):
                st.session_state.current_page = "dashboard"
                st.rerun()
        
        with nav_cols[2]:
            if st.button("📈", 
                        key="mobile_charts",
                        use_container_width=True, 
                        help="Gráficos",
                        type="secondary"):
                st.session_state.current_page = "dashboard"
                st.rerun()

        with nav_cols[3]:
            if st.button("👤", 
                        key="mobile_profile",
                        use_container_width=True, 
                        help="Perfil",
                        type="secondary"):
                st.info("👤 Perfil en desarrollo - Próximamente")

# Función principal de la página
def show_quick_add():
    """
    Página principal de Ahorify - Registro rápido.
    """
    page = QuickAddPage()
    page.render()

# Punto de entrada directo para desarrollo
if __name__ == "__main__":
    show_quick_add()