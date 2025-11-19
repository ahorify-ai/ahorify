# ui/components/progress_bars.py
import streamlit as st
import plotly.graph_objects as go
from typing import Dict, List, Optional, Tuple
from core.services.gamification_service import GamificationService
from core.services.transaction_service import TransactionService

class ProgressBars:
    """
    Sistema de barras de progreso visual para metas financieras.
    Diseño mobile-first y gamificado.
    """
    
    def __init__(self):
        self.gamification_service = GamificationService()
        self.transaction_service = TransactionService()
    
    def render_level_progress(self, user_id: str = "default_user") -> None:
        """Barra de progreso principal para nivel actual"""
        try:
            progress = self.gamification_service.get_user_progress()
            
            if not progress:
                self._render_fallback_progress()
                return
            
            current_level = progress["level"]
            level_info = progress["level_info"]
            progress_pct = progress["progress_percentage"]
            current_points = progress["points"]
            next_level_points = progress["next_level_points"]
            
            # Header con emojis dinámicos
            st.write(f"**{level_info['name']}**")

            # Barra de progreso principal
            st.progress(progress_pct / 100)
            
            col1, col2 = st.columns(2)
            with col1:
                st.caption(f"Progreso: {progress_pct:.1f}%")
            with col2:
                points_needed = max(0, next_level_points - current_points)
                st.caption(f"Siguiente: {points_needed} pts")

            next_level_index = min(current_level, len(self.gamification_service.LEVELS) - 1)
            next_level_info = self.gamification_service.LEVELS[next_level_index]
            st.caption(f"🎯 **Siguiente:** {next_level_info['name']} ({next_level_points} puntos)")
            
        except Exception as e:
            st.error("❌ Error cargando progreso de nivel")
    
    def render_savings_progress(self, goal_amount: float, current_amount: float, 
                              goal_name: str = "Meta de Ahorro") -> None:
        """Barra de progreso para metas de ahorro"""
        if goal_amount <= 0:
            st.warning("🎯 Establece una meta de ahorro para ver tu progreso")
            return
        
        progress_pct = min((current_amount / goal_amount) * 100, 100)
        remaining = max(goal_amount - current_amount, 0)
        
        st.markdown(f"### 🎯 {goal_name}")
        
        # Barras dobles: porcentaje + monto
        col1, col2 = st.columns([3, 1])
        
        with col1:
            self._render_enhanced_progress_bar(
                progress_pct,
                f"${current_amount:,.0f} / ${goal_amount:,.0f}",
                "success"
            )
        
        with col2:
            st.metric(
                "Completado", 
                f"{progress_pct:.1f}%",
                delta=f"${remaining:,.0f}" if remaining > 0 else "¡Completado!"
            )
        
        # Insights de ahorro
        if progress_pct < 25:
            st.info("💡 **Comienza fuerte:** Establece un hábito de ahorro constante.")
        elif progress_pct < 50:
            st.success("🚀 **Buen progreso:** ¡Vas por buen camino! Sigue así.")
        elif progress_pct < 75:
            st.success("🌟 **Más de la mitad:** ¡Impresionante! El objetivo está cerca.")
        elif progress_pct < 100:
            st.success("🎉 **Casi listo:** ¡Estás a punto de lograr tu meta!")
        else:
            st.balloons()
            st.success("🏆 **¡Meta alcanzada!** ¡Eres una super estrella del ahorro!")
    
    def render_category_budget(self, category: str, spent: float, 
                             budget: float, show_insights: bool = True) -> None:
        """Barra de progreso para presupuestos por categoría"""
        if budget <= 0:
            return
        
        progress_pct = min((spent / budget) * 100, 100)
        remaining = max(budget - spent, 0)
        
        # Determinar color basado en uso del presupuesto
        if progress_pct < 70:
            color = "success"
            emoji = "✅"
        elif progress_pct < 90:
            color = "warning" 
            emoji = "⚠️"
        else:
            color = "danger"
            emoji = "🚨"
        
        # Layout compacto para categorías
        col1, col2, col3 = st.columns([2, 2, 1])
        
        with col1:
            st.markdown(f"**{category}**")
        
        with col2:
            self._render_compact_progress_bar(progress_pct, color)
        
        with col3:
            st.markdown(f"{emoji} **{progress_pct:.0f}%**")
        
        # Tooltip con detalles
        if show_insights:
            with st.expander("📊 Detalles", expanded=False):
                col_a, col_b = st.columns(2)
                with col_a:
                    st.metric("Gastado", f"${spent:.2f}")
                with col_b:
                    st.metric("Restante", f"${remaining:.2f}")
                
                # Alertas contextuales
                if progress_pct >= 90:
                    st.error(f"⚠️ **Alerta:** Has usado el {progress_pct:.0f}% del presupuesto de {category}")
                elif progress_pct >= 70:
                    st.warning(f"🔔 **Aviso:** Has usado el {progress_pct:.0f}% del presupuesto de {category}")
    
    def render_weekly_expense_trend(self, current_week: float, 
                                  last_week: float, days_in_week: int = 7) -> None:
        """Barra de tendencia semanal de gastos"""
        if last_week == 0:
            change_pct = 0
        else:
            change_pct = ((current_week - last_week) / last_week) * 100
        
        # Calcular promedio diario
        current_daily = current_week / days_in_week if days_in_week > 0 else 0
        last_daily = last_week / days_in_week if days_in_week > 0 else 0
        
        st.markdown("### 📈 Tendencia Semanal")
        
        # Barras comparativas
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            name='Semana Actual',
            x=['Gastos'],
            y=[current_week],
            marker_color='#4CAF50' if current_week <= last_week else '#FF6B6B',
            text=[f'${current_week:.2f}'],
            textposition='auto',
        ))
        
        fig.add_trace(go.Bar(
            name='Semana Pasada',
            x=['Gastos'],
            y=[last_week],
            marker_color='#B0BEC5',
            text=[f'${last_week:.2f}'],
            textposition='auto',
        ))
        
        fig.update_layout(
            height=200,
            showlegend=True,
            margin=dict(l=20, r=20, t=30, b=20),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Métricas de tendencia
        col1, col2, col3 = st.columns(3)
        
        with col1:
            trend_emoji = "📉" if change_pct <= 0 else "📈"
            trend_color = "normal" if change_pct <= 0 else "inverse"
            st.metric(
                "Cambio Semanal", 
                f"${current_week:.2f}",
                delta=f"{change_pct:+.1f}% {trend_emoji}",
                delta_color=trend_color
            )
        
        with col2:
            st.metric("Promedio Diario", f"${current_daily:.2f}")
        
        with col3:
            daily_change = current_daily - last_daily
            daily_trend = "Mejor" if daily_change <= 0 else "Peor"
            st.metric("Tendencia Diaria", daily_trend)
    
    def render_quick_metrics(self, user_id: str = "default_user") -> None:
        """Métricas rápidas en formato de barras compactas"""
        try:
            totals = self.transaction_service.get_totals()
            weekly_summary = self.transaction_service.get_weekly_summary()
            
            st.markdown("### 📊 Resumen Rápido")
            
            # 3 métricas clave
            col1, col2, col3 = st.columns(3)
            
            with col1:
                balance = totals["balance"]
                balance_color = "normal" if balance >= 0 else "inverse"
                st.metric(
                    "Balance Total", 
                    totals["formatted_balance"],
                    delta_color=balance_color
                )
            
            with col2:
                st.metric(
                    "Gastos Semanales", 
                    weekly_summary["formatted_this_week"],
                    delta=weekly_summary["formatted_change"],
                    delta_color="inverse" if weekly_summary["expense_change"] > 0 else "normal"
                )
            
            with col3:
                monthly_totals = self.transaction_service.get_monthly_totals()
                st.metric(
                    "Promedio Diario", 
                    monthly_totals["formatted_daily_average"]
                )
            
            # Barras de distribución gastos/ingresos
            self._render_income_expense_distribution(totals)
            
        except Exception as e:
            st.error("❌ Error cargando métricas rápidas")
    
    def _render_enhanced_progress_bar(self, percentage: float, label: str, 
                                    color: str = "primary") -> None:
        """Barra de progreso visualmente mejorada"""
        # Mapeo de colores
        color_map = {
            "primary": "#4CAF50",
            "success": "#4CAF50", 
            "warning": "#FFC107",
            "danger": "#F44336",
            "info": "#2196F3"
        }
        
        bar_color = color_map.get(color, "#4CAF50")
        
        # Barra con HTML personalizado para mejor visual
        st.markdown(f"""
        <div style="background: #f0f0f0; border-radius: 10px; padding: 3px; margin: 5px 0;">
            <div style="background: {bar_color}; 
                       width: {percentage}%; 
                       height: 20px; 
                       border-radius: 8px; 
                       display: flex; 
                       align-items: center; 
                       justify-content: center;
                       color: white;
                       font-weight: bold;
                       font-size: 12px;
                       transition: width 0.5s ease;">
                {label if percentage > 20 else ""}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Etiqueta para porcentajes pequeños
        if percentage <= 20:
            st.caption(f"{label}")
    
    def _render_compact_progress_bar(self, percentage: float, color: str) -> None:
        """Barra de progreso compacta para espacios reducidos"""
        color_map = {
            "success": "#4CAF50",
            "warning": "#FFC107", 
            "danger": "#F44336"
        }
        
        bar_color = color_map.get(color, "#4CAF50")
        
        st.markdown(f"""
        <div style="background: #f0f0f0; border-radius: 5px; height: 8px; margin: 8px 0;">
            <div style="background: {bar_color}; 
                       width: {percentage}%; 
                       height: 8px; 
                       border-radius: 5px;">
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    def _render_income_expense_distribution(self, totals: Dict) -> None:
        """Gráfico de distribución ingresos vs gastos"""
        expenses = totals["total_expenses"]
        income = totals["total_income"]
        
        if income == 0:
            return
        
        savings_rate = ((income - expenses) / income) * 100 if income > 0 else 0
        
        fig = go.Figure()
        
        # Gastos
        fig.add_trace(go.Bar(
            name='Gastos',
            x=['Distribución'],
            y=[expenses],
            marker_color='#FF6B6B',
            text=[f'${expenses:.2f}'],
            textposition='auto',
        ))
        
        # Ahorro (si hay)
        if savings_rate > 0:
            fig.add_trace(go.Bar(
                name='Ahorro',
                x=['Distribución'],
                y=[income - expenses],
                marker_color='#4CAF50',
                text=[f'${income - expenses:.2f}'],
                textposition='auto',
            ))
        
        fig.update_layout(
            height=150,
            barmode='stack',
            showlegend=True,
            margin=dict(l=20, r=20, t=10, b=20),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Métrica de tasa de ahorro
        if savings_rate > 0:
            st.success(f"💰 **Tasa de ahorro:** {savings_rate:.1f}%")
        else:
            st.warning("💡 **Consejo:** Intenta gastar menos de lo que ganas para crear ahorros")
    
    def _render_fallback_progress(self) -> None:
        """Estado fallback cuando no hay datos"""
        st.markdown("### 🎯 Tu Progreso")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.progress(0)
            st.caption("Nivel 1 - Recién Llegado 💰")
        
        with col2:
            st.metric("Puntos", "0")
        
        st.info("💡 Comienza registrando transacciones para subir de nivel y ganar puntos!")

# Funciones de utilidad para uso rápido
def render_level_progress(user_id: str = "default_user") -> None:
    """Render rápido de progreso de nivel"""
    progress_bars = ProgressBars()
    progress_bars.render_level_progress(user_id)

def render_savings_goal(goal_amount: float, current_amount: float, goal_name: str = "Meta de Ahorro") -> None:
    """Render rápido de progreso de ahorro"""
    progress_bars = ProgressBars()
    progress_bars.render_savings_progress(goal_amount, current_amount, goal_name)

def render_quick_financial_metrics(user_id: str = "default_user") -> None:
    """Render rápido de métricas financieras"""
    progress_bars = ProgressBars()
    progress_bars.render_quick_metrics(user_id)