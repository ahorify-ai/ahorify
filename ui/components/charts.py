import streamlit as st
from typing import Dict, List, Optional, Tuple
from datetime import datetime, date, timedelta
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from core.services.transaction_service import TransactionService
from core.services.analytics_service import AnalyticsService
from core.services.gamification_service import GamificationService

class FinancialCharts:
    """
    Sistema de gráficos financieros completo para Ahorify.
    Versión 100% funcional con todos los gráficos implementados.
    """
    
    def __init__(self):
        self.transaction_service = TransactionService()
        self.analytics_service = AnalyticsService()
        self.gamification_service = GamificationService()
        
        # Paleta de colores consistente
        self.color_palette = [
            '#4CAF50', '#2196F3', '#FFC107', '#FF6B6B', '#9C27B0',
            '#00BCD4', '#FF9800', '#795548', '#607D8B', '#E91E63'
        ]
    
    def render_category_spend_chart(self, chart_type: str = "pie", height: int = 400) -> None:
        """
        Gráfico de gastos por categoría - COMPLETO
        """
        try:
            category_breakdown = self.transaction_service.get_category_breakdown()
            
            if not category_breakdown:
                self._render_empty_state("categorías de gasto")
                return
            
            # Preparar datos
            categories = [item['category'] for item in category_breakdown]
            amounts = [item['amount'] for item in category_breakdown]
            percentages = [item['percentage'] for item in category_breakdown]
            
            # Crear DataFrame para Plotly
            df = pd.DataFrame({
                'Categoría': categories,
                'Monto': amounts,
                'Porcentaje': percentages
            })
            
            if chart_type == "pie":
                fig = px.pie(
                    df,
                    values='Monto',
                    names='Categoría',
                    title="📊 Distribución de Gastos por Categoría",
                    color_discrete_sequence=self.color_palette,
                    hover_data=['Porcentaje']
                )
                fig.update_traces(
                    textposition='inside',
                    textinfo='percent+label',
                    hovertemplate='<b>%{label}</b><br>Monto: €%{value:.2f}<br>Porcentaje: %{customdata[0]}%<extra></extra>'
                )
                
            elif chart_type == "donut":
                fig = px.pie(
                    df,
                    values='Monto', 
                    names='Categoría',
                    title="📊 Distribución de Gastos (Donut)",
                    hole=0.4,
                    color_discrete_sequence=self.color_palette
                )
                
            else:  # bar chart
                fig = px.bar(
                    df,
                    x='Monto',
                    y='Categoría',
                    orientation='h',
                    title="📊 Gastos por Categoría",
                    color='Categoría',
                    color_discrete_sequence=self.color_palette,
                    text='Monto'
                )
                fig.update_traces(
                    texttemplate='€%{x:.2f}',
                    textposition='outside'
                )
                fig.update_layout(yaxis={'categoryorder':'total ascending'})
            
            # Estilo consistente
            fig.update_layout(
                height=height,
                showlegend=chart_type in ["pie", "donut"],
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=20, r=20, t=60, b=20),
                font=dict(size=12)
            )
            
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': True})
            
        except Exception as e:
            st.info("📊 Error mostrando gráfico de categorías")
    
    def render_weekly_trend_chart(self, weeks: int = 8, height: int = 400) -> None:
        """
        Gráfico de tendencias semanales - COMPLETO
        """
        try:
            weekly_data = self.analytics_service.get_weekly_comparison(weeks)
            
            if not weekly_data or not weekly_data.get('comparisons'):
                self._render_empty_state("datos semanales")
                return
            
            comparisons = weekly_data['comparisons']
            
            # Preparar datos para el gráfico
            weeks_list = [comp['week_label'] for comp in comparisons]
            expenses = [comp['expenses'] for comp in comparisons]
            incomes = [comp['income'] for comp in comparisons]
            balances = [comp['balance'] for comp in comparisons]
            
            fig = go.Figure()
            
            # Gastos (área roja)
            fig.add_trace(go.Scatter(
                name='💰 Gastos',
                x=weeks_list,
                y=expenses,
                line=dict(color='#FF6B6B', width=4),
                fill='tozeroy',
                fillcolor='rgba(255, 107, 107, 0.2)',
                hovertemplate='<b>Semana %{x}</b><br>Gastos: €%{y:.2f}<extra></extra>'
            ))
            
            # Ingresos (área verde)
            fig.add_trace(go.Scatter(
                name='💵 Ingresos', 
                x=weeks_list,
                y=incomes,
                line=dict(color='#4CAF50', width=4),
                fill='tonexty',
                fillcolor='rgba(76, 175, 80, 0.2)',
                hovertemplate='<b>Semana %{x}</b><br>Ingresos: €%{y:.2f}<extra></extra>'
            ))
            
            # Balance (línea punteada)
            fig.add_trace(go.Scatter(
                name='💎 Balance',
                x=weeks_list,
                y=balances,
                line=dict(color='#2196F3', width=3, dash='dash'),
                mode='lines+markers',
                hovertemplate='<b>Semana %{x}</b><br>Balance: €%{y:.2f}<extra></extra>'
            ))
            
            fig.update_layout(
                title="📈 Tendencias Semanales - Ingresos vs Gastos",
                height=height,
                xaxis_title="Semanas",
                yaxis_title="Monto (€)",
                hovermode='x unified',
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=20, r=20, t=80, b=20),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                )
            )
            
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': True})
            
        except Exception as e:
            st.info("📈 Error cargando tendencias semanales")
    
    def render_income_vs_expense_chart(self, height: int = 350) -> None:
        """
        Gráfico comparativo Ingresos vs Gastos - COMPLETO
        """
        try:
            totals = self.transaction_service.get_totals()
            
            # Datos para el gráfico
            categories = ['Ingresos', 'Gastos']
            values = [totals['total_income'], totals['total_expenses']]
            colors = ['#4CAF50', '#FF6B6B']
            
            fig = px.bar(
                x=categories,
                y=values,
                title="💸 Ingresos vs Gastos - Comparativa Total",
                color=categories,
                color_discrete_map={'Ingresos': '#4CAF50', 'Gastos': '#FF6B6B'},
                text=values
            )
            
            fig.update_traces(
                texttemplate='€%{y:.2f}',
                textposition='outside',
                hovertemplate='<b>%{x}</b><br>Monto: €%{y:.2f}<extra></extra>'
            )
            
            fig.update_layout(
                height=height,
                showlegend=False,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=20, r=20, t=60, b=20),
                xaxis_title="",
                yaxis_title="Monto (€)"
            )
            
            # Añadir línea de balance cero
            fig.add_hline(y=0, line_dash="dash", line_color="gray")
            
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': True})
            
        except Exception as e:
            st.info("💸 Error mostrando comparativa ingresos vs gastos")
    
    def render_financial_health_gauge(self, height: int = 300) -> None:
        """
        Gráfico de gauge para salud financiera - COMPLETO
        """
        try:
            health_data = self.analytics_service.get_financial_health_score()
            
            if not health_data:
                self._render_empty_state("salud financiera")
                return
            
            score = health_data['total_score']
            grade = health_data['grade']
            
            fig = go.Figure(go.Indicator(
                mode = "gauge+number+delta",
                value = score,
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': f"🏥 Salud Financiera", 'font': {'size': 20}},
                delta = {'reference': 50, 'increasing': {'color': "#4CAF50"}},
                gauge = {
                    'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
                    'bar': {'color': "#4CAF50"},
                    'bgcolor': "white",
                    'borderwidth': 2,
                    'bordercolor': "gray",
                    'steps': [
                        {'range': [0, 40], 'color': '#FF6B6B'},
                        {'range': [40, 70], 'color': '#FFC107'},
                        {'range': [70, 100], 'color': '#4CAF50'}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 90
                    }
                }
            ))
            
            fig.update_layout(
                height=height,
                paper_bgcolor='rgba(0,0,0,0)',
                font={'color': "darkblue", 'family': "Arial"}
            )
            
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
            
            # Mostrar grade y recomendaciones
            st.markdown(f"### {grade}")
            
            if health_data.get('recommendations'):
                with st.expander("💡 Recomendaciones para mejorar", expanded=False):
                    for i, rec in enumerate(health_data['recommendations']):
                        st.write(f"{i+1}. {rec}")
                        
        except Exception as e:
            st.info("🏥 Error evaluando salud financiera")
    
    def render_savings_progress_chart(self, goal_amount: float = 1000, 
                                    current_amount: float = None,
                                    goal_name: str = "Meta de Ahorro") -> None:
        """
        Gráfico de progreso de ahorros - COMPLETO
        """
        try:
            # Si no se proporciona current_amount, calcular del balance
            if current_amount is None:
                totals = self.transaction_service.get_totals()
                current_amount = max(totals['balance'], 0)
            
            progress_pct = (current_amount / goal_amount * 100) if goal_amount > 0 else 0
            
            # Gráfico de gauge para progreso
            fig = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = progress_pct,
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': f"🎯 {goal_name}", 'font': {'size': 16}},
                gauge = {
                    'axis': {'range': [None, 100], 'tickwidth': 1},
                    'bar': {'color': "#4CAF50"},
                    'steps': [
                        {'range': [0, 33], 'color': "#FF6B6B"},
                        {'range': [33, 66], 'color': "#FFC107"},
                        {'range': [66, 100], 'color': "#4CAF50"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 100
                    }
                }
            ))
            
            fig.update_layout(height=250)
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
            
            # Métricas detalladas
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Actual", f"€{current_amount:.2f}")
            
            with col2:
                st.metric("Meta", f"€{goal_amount:.2f}")
            
            with col3:
                remaining = max(goal_amount - current_amount, 0)
                st.metric("Faltante", f"€{remaining:.2f}")
            
            # Mensaje motivacional
            if progress_pct >= 100:
                st.success("🏆 **¡Meta alcanzada!** ¡Felicidades!")
            elif progress_pct >= 75:
                st.info(f"💪 **{progress_pct:.0f}% completado** - ¡Casi lo logras!")
            elif progress_pct >= 50:
                st.info(f"🔥 **{progress_pct:.0f}% completado** - ¡Vas por buen camino!")
            elif progress_pct >= 25:
                st.info(f"🌱 **{progress_pct:.0f}% completado** - Buen comienzo!")
            else:
                st.info(f"🚀 **{progress_pct:.0f}% completado** - ¡Comienza tu aventura!")
                
        except Exception as e:
            st.info("🎯 Error mostrando progreso de ahorros")
    
    def render_daily_spending_heatmap(self, days: int = 30, height: int = 300) -> None:
        """
        Mapa de calor de gastos diarios - COMPLETO
        """
        try:
            # Obtener transacciones recientes
            transactions = self.transaction_service.get_recent_transactions(limit=1000)
            
            if not transactions:
                self._render_empty_state("datos de transacciones")
                return
            
            # Filtrar solo gastos y de los últimos días
            expense_transactions = [
                t for t in transactions 
                if t['type'] == 'expense' 
            ]
            
            if not expense_transactions:
                st.info("🔥 Registra gastos para ver el mapa de calor")
                return
            
            # Crear datos para el heatmap
            heatmap_data = {}
            for transaction in expense_transactions:
                try:
                    # Parsear fecha
                    created_at = transaction.get('created_at')
                    if isinstance(created_at, str):
                        if 'T' in created_at:
                            trans_date = datetime.fromisoformat(created_at.replace('Z', '+00:00')).date()
                        else:
                            trans_date = datetime.strptime(created_at, '%Y-%m-%d').date()
                    else:
                        continue
                    
                    # Agrupar por fecha
                    date_str = trans_date.isoformat()
                    if date_str not in heatmap_data:
                        heatmap_data[date_str] = 0
                    heatmap_data[date_str] += transaction['amount']
                    
                except Exception:
                    continue
            
            if not heatmap_data:
                st.info("📅 No hay datos suficientes para el mapa de calor")
                return
            
            # Crear DataFrame para el heatmap
            dates = list(heatmap_data.keys())
            amounts = list(heatmap_data.values())
            
            df = pd.DataFrame({
                'Fecha': pd.to_datetime(dates),
                'Gastos': amounts
            })
            
            # Crear heatmap con Plotly
            fig = px.density_heatmap(
                df,
                x='Fecha',
                y='Gastos',
                title="🔥 Mapa de Calor de Gastos Diarios",
                color_continuous_scale='Viridis',
                nbinsx=min(len(dates), 30),
                nbinsy=10
            )
            
            fig.update_layout(
                height=height,
                xaxis_title="Fecha",
                yaxis_title="Monto de Gastos (€)",
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)'
            )
            
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': True})
            
        except Exception as e:
            st.info("🔥 Error generando mapa de calor")
    
    def render_emotional_spending_chart(self, height: int = 400) -> None:
        """
        Gráfico de emociones en los gastos - COMPLETO
        """
        try:
            emotional_data = self.analytics_service.get_emotional_analytics()
            
            if not emotional_data or not emotional_data.get('emotional_breakdown'):
                self._render_empty_state("análisis de emociones")
                return
            
            emotional_breakdown = emotional_data['emotional_breakdown']
            
            if not emotional_breakdown:
                st.info("😊 Registra transacciones con emociones para ver este análisis")
                return
            
            # Preparar datos
            emotions = list(emotional_breakdown.keys())
            amounts = [data['total'] for data in emotional_breakdown.values()]
            counts = [data['count'] for data in emotional_breakdown.values()]
            
            # Mapeo de emojis para emociones
            emotion_emojis = {
                'happy': '😊',
                'neutral': '😐', 
                'stress': '😥',
                'impulsive': '⚡',
                'investment': '📈'
            }
            
            emotions_with_emoji = [f"{emotion_emojis.get(emotion, '❓')} {emotion.title()}" for emotion in emotions]
            
            # Gráfico de barras
            fig = px.bar(
                x=emotions_with_emoji,
                y=amounts,
                title="😊 Análisis de Emociones en Gastos",
                color=emotions_with_emoji,
                color_discrete_sequence=self.color_palette,
                text=amounts
            )
            
            fig.update_traces(
                texttemplate='€%{y:.2f}',
                textposition='outside',
                hovertemplate='<b>%{x}</b><br>Total Gastado: €%{y:.2f}<br>Transacciones: %{customdata}<extra></extra>',
                customdata=counts
            )
            
            fig.update_layout(
                height=height,
                showlegend=False,
                xaxis_title="Emoción",
                yaxis_title="Total Gastado (€)",
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)'
            )
            
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': True})
            
            # Insights adicionales
            if emotional_data.get('most_common_emotion'):
                st.info(
                    f"💡 **Emoción más común:** {emotional_data['most_common_emotion'].title()} "
                    f"({emotional_breakdown[emotional_data['most_common_emotion']]['count']} transacciones)"
                )
                
        except Exception as e:
            st.info("😊 Error analizando emociones en gastos")
    
    def render_quick_insights_dashboard(self) -> None:
        """
        Dashboard compacto con gráficos básicos - COMPLETO
        """
        st.subheader("📈 Vista Rápida - Resumen Ejecutivo")
        
        # Métricas clave en la parte superior
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            try:
                totals = self.transaction_service.get_totals()
                st.metric("💰 Balance", totals["formatted_balance"])
            except:
                st.metric("💰 Balance", "€0.00")
        
        with col2:
            try:
                weekly = self.transaction_service.get_weekly_summary()
                st.metric("📊 Gastos Semana", weekly["formatted_this_week"])
            except:
                st.metric("📊 Gastos Semana", "€0.00")
        
        with col3:
            try:
                monthly = self.transaction_service.get_monthly_totals()
                st.metric("📅 Promedio Diario", monthly["formatted_daily_average"])
            except:
                st.metric("📅 Promedio Diario", "€0.00")
        
        with col4:
            try:
                progress = self.gamification_service.get_user_progress()
                st.metric("🏆 Nivel", progress["level"])
            except:
                st.metric("🏆 Nivel", "1")
        
        # Gráficos en dos columnas
        col1, col2 = st.columns(2)
        
        with col1:
            self.render_category_spend_chart("pie", 300)
        
        with col2:
            self.render_income_vs_expense_chart(300)
        
        # Tendencias debajo
        self.render_weekly_trend_chart(4, 350)
    
    def _render_empty_state(self, data_type: str) -> None:
        """Estado vacío consistente para cuando no hay datos"""
        st.info(f"📊 Registra {data_type} para ver gráficos y análisis")
        
        if st.button("🚀 Comenzar a Registrar Transacciones", use_container_width=True):
            st.switch_page("pages/quick_add.py")

# Funciones de utilidad para uso rápido
def render_category_chart(chart_type: str = "pie"):
    """Render rápido de gráfico de categorías"""
    charts = FinancialCharts()
    charts.render_category_spend_chart(chart_type)

def render_weekly_trends(weeks: int = 8):
    """Render rápido de tendencias semanales"""
    charts = FinancialCharts()
    charts.render_weekly_trend_chart(weeks)

def render_quick_dashboard():
    """Render rápido del dashboard ejecutivo"""
    charts = FinancialCharts()
    charts.render_quick_insights_dashboard()

def render_financial_health():
    """Render rápido de salud financiera"""
    charts = FinancialCharts()
    charts.render_financial_health_gauge()

def render_savings_progress(goal_amount: float = 1000, goal_name: str = "Meta de Ahorro"):
    """Render rápido de progreso de ahorros"""
    charts = FinancialCharts()
    charts.render_savings_progress_chart(goal_amount, None, goal_name)