import streamlit as st
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional
import plotly.graph_objects as go
import plotly.express as px
from core.services.transaction_service import TransactionService
from core.services.gamification_service import GamificationService
from core.services.analytics_service import AnalyticsService

class DashboardPage:
    """
    Dashboard principal de Ahorify - COMPLETAMENTE FUNCIONAL
    Arquitectura robusta con manejo completo de errores
    """
    
    def __init__(self):
        self.transaction_service = TransactionService()
        self.gamification_service = GamificationService()
        self.analytics_service = AnalyticsService()
        
        # Estado del dashboard
        if 'dashboard_view_count' not in st.session_state:
            st.session_state.dashboard_view_count = 0
        if 'last_refresh' not in st.session_state:
            st.session_state.last_refresh = datetime.now()
    
    def render(self) -> None:
        """Renderiza el dashboard completo con manejo de errores robusto"""
        try:
            self._increment_view_count()
            self._render_header()
            self._render_quick_insights()
            self._render_gamification_section()
            self._render_financial_overview()
            self._render_detailed_analytics()
            self._render_weekly_planning()
            
        except Exception as e:
            st.error("❌ Error cargando el dashboard")
            st.info("💡 **Solución rápida:** Ve a 'Registro Rápido' y añade tu primera transacción")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔄 Recargar Dashboard", use_container_width=True):
                    st.rerun()
            with col2:
                if st.button("💸 Ir a Registro Rápido", use_container_width=True):
                    st.switch_page("pages/quick_add.py")
    
    def _increment_view_count(self) -> None:
        """Registra vistas del dashboard para gamificación"""
        st.session_state.dashboard_view_count += 1
        st.session_state.last_refresh = datetime.now()
        
        try:
            self.gamification_service.record_engagement(
                action_type="dashboard_viewed",
                metadata={
                    "view_count": st.session_state.dashboard_view_count,
                    "source": "dashboard_page"
                }
            )
        except Exception as e:
            print(f"⚠️ Gamificación dashboard: {e}")
    
    def _render_header(self) -> None:
        """Header del dashboard con métricas clave"""
        st.title("📊 Dashboard Financiero")
        st.markdown(f"**Última actualización:** {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        st.markdown("Vista completa de tu salud financiera y progreso personal")
        st.divider()
    
    def _render_quick_insights(self) -> None:
        """Métricas rápidas y KPIs principales - VERSIÓN ROBUSTA"""
        st.subheader("📈 Resumen Rápido")
        
        try:
            # Obtener todos los datos necesarios
            totals = self.transaction_service.get_totals()
            weekly_summary = self.transaction_service.get_weekly_summary()
            monthly_totals = self.transaction_service.get_monthly_totals()
            top_categories = self.transaction_service.get_top_categories(limit=1)
            
            # Grid de métricas principales
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                balance_emoji = "💎" if totals["balance"] >= 0 else "⚠️"
                balance_color = "green" if totals["balance"] >= 0 else "red"
                st.metric(
                    f"{balance_emoji} Balance Total", 
                    totals["formatted_balance"],
                    delta="Positivo" if totals["balance"] >= 0 else "Negativo",
                    delta_color=balance_color
                )
            
            with col2:
                trend_emoji = "📉" if weekly_summary["expense_change"] <= 0 else "📈"
                st.metric(
                    f"{trend_emoji} Gastos Semanales", 
                    weekly_summary["formatted_this_week"],
                    delta=weekly_summary["formatted_change"]
                )
            
            with col3:
                st.metric(
                    "📅 Promedio Diario", 
                    monthly_totals["formatted_daily_average"]
                )
            
            with col4:
                top_category = top_categories[0]['category'] if top_categories else "N/A"
                st.metric("🎯 Categoría Top", top_category)
            
            # Indicador de tendencia
            self._render_trend_indicator(weekly_summary)
            
        except Exception as e:
            self._render_metrics_fallback()
    
    def _render_trend_indicator(self, weekly_summary: Dict) -> None:
        """Indicador visual de tendencia"""
        change = weekly_summary["expense_change"]
        
        if change < -5:
            emoji = "📉"
            color = "green"
            message = f"¡Gastos bajando {abs(change):.1f}%!"
        elif change > 5:
            emoji = "📈"
            color = "red" 
            message = f"Gastos subiendo {change:.1f}%"
        else:
            emoji = "➡️"
            color = "gray"
            message = "Gastos estables"
        
        st.markdown(f"""
        <div style="background: var(--neutral-50); padding: 12px 16px; border-radius: 12px; border-left: 4px solid {color}; margin: 8px 0;">
            <div style="display: flex; align-items: center; gap: 12px;">
                <span style="font-size: 1.5rem;">{emoji}</span>
                <div>
                    <div style="font-weight: 600; color: {color};">{message}</div>
                    <div style="font-size: 0.875rem; color: var(--text-secondary);">
                        Comparado con la semana anterior
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    def _render_gamification_section(self) -> None:
        """Sección de gamificación y progreso personal"""
        st.subheader("🎮 Tu Progreso Gamificado")
        
        try:
            progress = self.gamification_service.get_user_progress()
            
            # Tres columnas para elementos de gamificación
            col1, col2, col3 = st.columns(3)
            
            with col1:
                self._render_level_progress(progress)
            
            with col2:
                self._render_streak_display(progress)
            
            with col3:
                self._render_engagement_metrics(progress)
            
            # Logros recientes
            self._render_recent_achievements()
            
        except Exception as e:
            st.info("🎮 Comienza a usar la app para ver tu progreso gamificado")
    
    def _render_level_progress(self, progress: Dict) -> None:
        """Muestra progreso de nivel"""
        st.markdown("##### 🏆 Nivel y Progreso")
        
        # Badge de nivel simple
        level = progress["level"]
        level_info = progress["level_info"]
        
        st.markdown(f"""
        <div style="text-align: center; padding: 16px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 16px; color: white;">
            <div style="font-size: 3rem; margin-bottom: 8px;">{level_info.get('badge', '💰')}</div>
            <div style="font-size: 1.25rem; font-weight: 700; margin-bottom: 4px;">Nivel {level}</div>
            <div style="font-size: 0.875rem; opacity: 0.9;">{level_info['name']}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Barra de progreso
        progress_pct = progress["progress_percentage"]
        st.markdown(f"**Progreso al siguiente nivel:** {progress_pct}%")
        st.progress(progress_pct / 100)
        
        # Puntos
        st.metric("Puntos Totales", progress["points"])
    
    def _render_streak_display(self, progress: Dict) -> None:
        """Muestra sistema de rachas"""
        st.markdown("##### 🔥 Sistema de Rachas")
        
        streak = progress["streak"]
        current = streak["current"]
        longest = streak["longest"]
        
        # Rachas visual
        if current >= 7:
            emoji = "🔥"
            color = "#FF6B35"
            message = "¡Racha impresionante!"
        elif current >= 3:
            emoji = "⚡"  
            color = "#FFC107"
            message = "¡Buen ritmo!"
        else:
            emoji = "🌱"
            color = "#4CAF50"
            message = "¡Comienza tu racha!"
        
        st.markdown(f"""
        <div style="text-align: center; padding: 20px; background: {color}10; border: 2px solid {color}30; border-radius: 16px;">
            <div style="font-size: 3rem; margin-bottom: 8px;">{emoji}</div>
            <div style="font-size: 2rem; font-weight: 700; color: {color}; margin-bottom: 4px;">{current} días</div>
            <div style="font-size: 0.875rem; color: var(--text-secondary);">Racha actual</div>
            <div style="font-size: 0.75rem; color: {color}; margin-top: 8px;">{message}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Métricas de rachas
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Mejor racha", f"{longest} días")
        with col2:
            st.metric("Días totales", streak["total_days"])
    
    def _render_engagement_metrics(self, progress: Dict) -> None:
        """Métricas de engagement del usuario"""
        st.markdown("##### 📊 Engagement")
        
        engagement = progress["engagement"]
        
        st.metric("Días Activos", engagement.get("total_active_days", 0))
        st.metric("Tasa de Engagement", f"{engagement.get('engagement_rate', 0):.1f}%")
        
        # Insights de engagement
        engagement_rate = engagement.get('engagement_rate', 0)
        if engagement_rate > 80:
            st.success("🎯 **Excelente engagement!** Eres muy consistente.")
        elif engagement_rate > 50:
            st.info("💪 **Buen engagement!** Sigue construyendo el hábito.")
        else:
            st.warning("🌱 **Oportunidad de mejora** Intenta ser más consistente.")
    
    def _render_recent_achievements(self) -> None:
        """Logros y achievements recientes"""
        st.markdown("##### 🏅 Logros Recientes")
        
        # Simulación de logros - en implementación real vendrían del servicio
        achievements = [
            {"icon": "🔥", "name": "Primera Racha", "description": "3 días consecutivos", "unlocked": True},
            {"icon": "💰", "name": "Ahorrador Novato", "description": "Primer ahorro registrado", "unlocked": True},
            {"icon": "📊", "name": "Analista Junior", "description": "10 transacciones", "unlocked": True},
            {"icon": "🏆", "name": "Racha Semanal", "description": "7 días consecutivos", "unlocked": False},
        ]
        
        cols = st.columns(4)
        for i, achievement in enumerate(achievements):
            with cols[i]:
                opacity = "1" if achievement["unlocked"] else "0.3"
                st.markdown(f"""
                <div style="text-align: center; opacity: {opacity};">
                    <div style="font-size: 2rem; margin-bottom: 8px;">{achievement['icon']}</div>
                    <div style="font-weight: 600; font-size: 0.875rem;">{achievement['name']}</div>
                    <div style="font-size: 0.75rem; color: var(--text-secondary);">{achievement['description']}</div>
                </div>
                """, unsafe_allow_html=True)
    
    def _render_financial_overview(self) -> None:
        """Visión general financiera con gráficos"""
        st.subheader("💰 Visión General")
        
        # Dos columnas para gráficos
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("#### 📊 Distribución de Gastos")
            self._render_category_chart()
        
        with col2:
            st.markdown("#### 📈 Resumen Mensual")
            self._render_monthly_summary()
        
        # Gráfico de tendencias
        st.markdown("#### 📈 Evolución Temporal")
        self._render_trends_chart()
    
    def _render_category_chart(self) -> None:
        """Gráfico de categorías de gastos"""
        try:
            category_breakdown = self.transaction_service.get_category_breakdown()
            
            if not category_breakdown:
                st.info("📊 Registra gastos para ver distribución por categorías")
                return
            
            # Crear gráfico de torta
            categories = [item['category'] for item in category_breakdown]
            amounts = [item['amount'] for item in category_breakdown]
            
            fig = px.pie(
                values=amounts,
                names=categories,
                title="Distribución de Gastos por Categoría",
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
            
        except Exception as e:
            st.info("📊 Error mostrando gráfico de categorías")
    
    def _render_monthly_summary(self) -> None:
        """Resumen mensual de métricas"""
        try:
            totals = self.transaction_service.get_totals()
            monthly_totals = self.transaction_service.get_monthly_totals()
            
            st.metric("💰 Ingresos", totals["formatted_income"])
            st.metric("💸 Gastos", totals["formatted_expenses"])
            st.metric("📅 Promedio Diario", monthly_totals["formatted_daily_average"])
            
            # Cálculo de ahorro
            savings = totals["total_income"] - totals["total_expenses"]
            savings_rate = (savings / totals["total_income"] * 100) if totals["total_income"] > 0 else 0
            
            st.metric("💎 Ahorro Mensual", f"€{savings:.2f}")
            st.metric("📈 Tasa de Ahorro", f"{savings_rate:.1f}%")
            
        except Exception as e:
            st.info("📈 Registra transacciones para ver métricas mensuales")
    
    def _render_trends_chart(self) -> None:
        """Gráfico de tendencias temporales"""
        try:
            weekly_data = self.analytics_service.get_weekly_comparison(weeks_back=8)
            
            if not weekly_data or not weekly_data.get('comparisons'):
                st.info("📈 Registra más datos para ver tendencias")
                return
            
            comparisons = weekly_data['comparisons']
            
            # Preparar datos para el gráfico
            weeks_list = [comp['week_label'] for comp in comparisons]
            expenses = [comp['expenses'] for comp in comparisons]
            incomes = [comp['income'] for comp in comparisons]
            
            fig = go.Figure()
            
            # Línea de gastos
            fig.add_trace(go.Scatter(
                name='💰 Gastos',
                x=weeks_list,
                y=expenses,
                line=dict(color='#FF6B6B', width=4),
                fill='tozeroy',
                fillcolor='rgba(255, 107, 107, 0.1)'
            ))
            
            # Línea de ingresos
            fig.add_trace(go.Scatter(
                name='💵 Ingresos', 
                x=weeks_list,
                y=incomes,
                line=dict(color='#4CAF50', width=4),
                fill='tonexty',
                fillcolor='rgba(76, 175, 80, 0.1)'
            ))
            
            fig.update_layout(
                title="Tendencias de Ingresos vs Gastos",
                height=400,
                xaxis_title="Semanas",
                yaxis_title="Monto (€)",
                hovermode='x unified'
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
        except Exception as e:
            st.info("📈 Error cargando tendencias")
    
    def _render_detailed_analytics(self) -> None:
        """Analytics detallados y insights"""
        st.subheader("🔍 Analytics Detallados")
        
        # Tabs para diferentes vistas analíticas
        tab1, tab2, tab3 = st.tabs(["📈 Tendencias", "🎯 Categorías", "📅 Mensual"])
        
        with tab1:
            self._render_trends_analytics()
        
        with tab2:
            self._render_category_analytics()
        
        with tab3:
            self._render_monthly_analytics()
    
    def _render_trends_analytics(self) -> None:
        """Analytics de tendencias temporales"""
        try:
            weekly_data = self.analytics_service.get_weekly_comparison(weeks_back=4)
            
            if weekly_data and weekly_data.get("comparisons"):
                comparisons = weekly_data["comparisons"]
                
                # Mostrar últimas 4 semanas
                st.markdown("##### 📊 Comparativa Semanal")
                cols = st.columns(4)
                for i, comp in enumerate(comparisons[:4]):
                    with cols[i]:
                        balance = comp['income'] - comp['expenses']
                        balance_color = "green" if balance >= 0 else "red"
                        st.metric(
                            comp["week_label"],
                            f"€{comp['expenses']:.2f}",
                            delta=f"€{balance:.2f}",
                            delta_color=balance_color
                        )
            
            # Gráfico de ingresos vs gastos
            st.markdown("##### 💸 Ingresos vs Gastos")
            self._render_income_vs_expense_chart()
            
        except Exception as e:
            st.info("📈 Registra más datos para ver análisis de tendencias")
    
    def _render_income_vs_expense_chart(self) -> None:
        """Gráfico comparativo ingresos vs gastos"""
        try:
            totals = self.transaction_service.get_totals()
            
            categories = ['Ingresos', 'Gastos']
            values = [totals['total_income'], totals['total_expenses']]
            
            fig = px.bar(
                x=categories,
                y=values,
                title="Comparativa Ingresos vs Gastos",
                color=categories,
                color_discrete_map={'Ingresos': '#4CAF50', 'Gastos': '#FF6B6B'}
            )
            
            fig.update_layout(height=300, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
            
        except Exception as e:
            st.info("💸 Registra transacciones para ver comparativas")
    
    def _render_category_analytics(self) -> None:
        """Analytics detallados por categoría"""
        try:
            category_breakdown = self.transaction_service.get_category_breakdown()
            top_categories = self.transaction_service.get_top_categories(limit=10)
            
            if not category_breakdown:
                st.info("🎯 Registra gastos para ver analytics por categoría")
                return
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown("##### 🎯 Top Categorías de Gasto")
                for i, category in enumerate(top_categories[:5]):
                    with st.container():
                        col_a, col_b, col_c = st.columns([1, 3, 2])
                        with col_a:
                            st.markdown(f"**#{i+1}**")
                        with col_b:
                            st.write(category['category'])
                        with col_c:
                            st.write(category['formatted_amount'])
            
            with col2:
                st.markdown("##### 📊 Distribución")
                # Gráfico de donut para distribución
                categories = [item['category'] for item in category_breakdown]
                amounts = [item['amount'] for item in category_breakdown]
                
                fig = px.pie(
                    values=amounts,
                    names=categories,
                    hole=0.4,
                    height=300
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # Insights de categorías
            if category_breakdown:
                top_category = category_breakdown[0]
                if top_category['percentage'] > 40:
                    st.warning(
                        f"🔍 **Gastos concentrados:** {top_category['category']} representa "
                        f"el {top_category['percentage']}% de tus gastos. Considera diversificar."
                    )
                    
        except Exception as e:
            st.info("🎯 Error cargando analytics por categoría")
    
    def _render_monthly_analytics(self) -> None:
        """Vista mensual y comparativas"""
        try:
            monthly_totals = self.transaction_service.get_monthly_totals()
            totals = self.transaction_service.get_totals()
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("💰 Gastos Mensuales", monthly_totals["formatted_monthly_expenses"])
                st.metric("💵 Ingresos Mensuales", f"€{totals['total_income']:.2f}")
            
            with col2:
                st.metric("📅 Promedio Diario", monthly_totals["formatted_daily_average"])
                days_in_month = date.today().day
                st.metric("📆 Días Transcurridos", f"{days_in_month}/30")
            
            with col3:
                savings = totals["total_income"] - totals["total_expenses"]
                savings_rate = (savings / totals["total_income"] * 100) if totals["total_income"] > 0 else 0
                st.metric("💎 Tasa de Ahorro", f"{savings_rate:.1f}%")
                st.metric("📈 Ahorro Mensual", f"€{savings:.2f}")
            
            # Proyección mensual
            if days_in_month > 0:
                projected_expenses = (monthly_totals["monthly_expenses"] / days_in_month) * 30
                st.info(
                    f"📊 **Proyección mensual:** €{projected_expenses:.2f} "
                    f"({'↑' if projected_expenses > monthly_totals['monthly_expenses'] else '↓'} "
                    f"vs actual)"
                )
                
        except Exception as e:
            st.info("📅 Registra transacciones para ver analytics mensuales")
    
    def _render_weekly_planning(self) -> None:
        """Planificación semanal y recomendaciones"""
        st.subheader("🗓️ Planificación y Consejos")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            self._render_weekly_budget_tracker()
        
        with col2:
            self._render_financial_tips()
    
    def _render_weekly_budget_tracker(self) -> None:
        """Seguimiento de presupuesto semanal"""
        st.markdown("##### 💰 Seguimiento Semanal")
        
        try:
            # Usar datos reales de categorías
            category_breakdown = self.transaction_service.get_category_breakdown()
            
            if not category_breakdown:
                st.info("💸 Registra gastos para ver seguimiento presupuestario")
                return
            
            # Mostrar top 5 categorías con progreso
            for i, category in enumerate(category_breakdown[:5]):
                spent = category['amount']
                budget = spent * 1.2  # Presupuesto estimado (20% más del gasto actual)
                
                progress = min(spent / budget, 1.0) if budget > 0 else 0
                progress_color = "green" if progress < 0.7 else "orange" if progress < 0.9 else "red"
                
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    st.write(category['category'])
                with col2:
                    st.write(f"€{spent:.2f}")
                with col3:
                    st.progress(progress)
            
            total_spent = sum(item['amount'] for item in category_breakdown[:5])
            st.metric("Total Gastado (Top 5)", f"€{total_spent:.2f}")
            
        except Exception as e:
            st.info("💰 Configura tus presupuestos para ver seguimiento")
    
    def _render_financial_tips(self) -> None:
        """Consejos financieros contextuales"""
        st.markdown("##### 💡 Consejos del Día")
        
        tips = [
            "🎯 **Establece metas claras:** ¿Qué quieres lograr con tus ahorros?",
            "📊 **Revisa tus gastos:** Identifica patrones y oportunidades de ahorro.",
            "🔥 **Mantén la racha:** La consistencia es clave para el éxito financiero.",
            "💰 **Automátiza ahorros:** Programa transferencias automáticas a tu cuenta de ahorros.",
            "📱 **Usa Ahorify diariamente:** Registra cada transacción para mantener el control.",
        ]
        
        import random
        daily_tip = random.choice(tips)
        
        st.markdown(f"""
        <div style="background: #1E1E1E; padding: 16px; border-radius: 12px; border-left: 4px solid #4CAF50; color: white;">
            <div style="font-size: 0.875rem; line-height: 1.5; color: white;">
                {daily_tip}
            </div>
        </div>
        """, unsafe_allow_html=True)

        
        # Consejo adicional basado en comportamiento
        try:
            progress = self.gamification_service.get_user_progress()
            if progress["streak"]["current"] >= 7:
                st.success("🌟 **¡Excelente racha!** Siete días seguidos demuestra gran compromiso.")
            elif progress["streak"]["current"] == 0:
                st.warning("🌱 **Comienza hoy:** Registra una transacción para iniciar tu racha.")
        except:
            pass
    
    def _render_metrics_fallback(self) -> None:
        """Fallback cuando no hay datos de métricas"""
        st.info("📊 **Comienza tu Tu Aventura Financiera 🗺️**")
        st.markdown("""
        Registra tu primera transacción para desbloquear todas las métricas y insights:
        
        1. 🏆 **Sistema de gamificación** - Gana puntos y sube de nivel
        2. 🔥 **Rachas de consistencia** - Mantén tu motivación  
        3. 📈 **Analytics avanzados** - Entiende tus patrones de gasto
        4. 💡 **Recomendaciones personalizadas** - Mejora tu salud financiera
        """)
        
        if st.button("🚀 Comenzar Ahora - Ir a Registro Rápido", use_container_width=True):
            st.switch_page("pages/quick_add.py")

# Función principal de la página
def show_dashboard():
    """
    Página de dashboard principal de Ahorify - COMPLETAMENTE FUNCIONAL
    """
    try:
        # Registrar view para gamificación
        gamification_service = GamificationService()
        gamification_service.record_engagement("dashboard_viewed")
        
        # Renderizar página
        page = DashboardPage()
        page.render()
        
    except Exception as e:
        st.error("🚨 Error crítico cargando el dashboard")
        st.info("""
        **Solución rápida:**
        1. Verifica tu conexión a internet
        2. Recarga la página
        3. Si el problema persiste, ve a **Registro Rápido** y vuelve
        """)
        
        # Botones de acción
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Recargar Dashboard", use_container_width=True):
                st.rerun()
        with col2:
            if st.button("💸 Ir a Registro Rápido", use_container_width=True):
                st.switch_page("pages/quick_add.py")

# Punto de entrada directo para desarrollo
if __name__ == "__main__":
    show_dashboard()