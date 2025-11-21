"""
🚀 AHORIFY - Tu Aventura Financiera 🗺️
Punto de entrada principal - Arquitectura mobile-first con onboarding PERSISTENTE
"""

import streamlit as st
from config import initialize_app, DesignSystem
from core.services.gamification_service import GamificationService
from core.database import db 
from functools import lru_cache
import base64
import os
from pathlib import Path

# Importar páginas
from ui.pages.quick_add import show_quick_add
from ui.pages.dashboard import show_dashboard
from ui.pages.import_csv import show_import_csv

class AhorifyApp:
    """
    Aplicación principal Ahorify - Mobile-first con onboarding inteligente PERSISTENTE
    """
    
    def __init__(self):
        self.gamification_service = GamificationService()
        self.setup_persistent_state()

    @lru_cache(maxsize=1)
    def _get_logo_base64(self) -> str:
        """Obtiene el logo en base64 con cache - VERSIÓN MEJORADA"""
        # 🔼 BUSQUEDA MÁS ROBUSTA CON PATHLIB
        possible_paths = [
            Path("static/ahorify_logo.png"),
            Path("assets/ahorify_logo.png"),
            Path("ahorify_logo.png"),
            Path("ui/static/ahorify_logo.png"),
            Path("ui/assets/ahorify_logo.png"),
            Path("../static/ahorify_logo.png"),
            Path("../assets/ahorify_logo.png"),
        ]
        
        for logo_path in possible_paths:
            if logo_path.exists():
                try:
                    with open(logo_path, "rb") as img_file:
                        return base64.b64encode(img_file.read()).decode()
                except Exception as e:
                    print(f"⚠️ Error cargando logo en {logo_path}: {e}")
                    continue
        
        raise FileNotFoundError(f"Logo no encontrado. Rutas probadas: {[str(p) for p in possible_paths]}")

    def _load_logo_html(self) -> str:
        """Carga el logo con manejo robusto de errores - VERSIÓN OPTIMIZADA"""
        try:
            logo_data = self._get_logo_base64()
            
            return f"""
            <div style="text-align: center; margin-bottom: 2rem;">
                <div style="margin-bottom: 0.5rem;">
                    <img src="data:image/png;base64,{logo_data}" 
                         style="height: 60px; width: auto; border-radius: 12px; 
                                box-shadow: {DesignSystem.SHADOW_MD};
                                transition: transform 0.2s ease;"
                         onmouseover="this.style.transform='scale(1.05)'"
                         onmouseout="this.style.transform='scale(1)'"
                         alt="Ahorify Logo">
                </div>
                <h2 style="background: {DesignSystem.GRADIENT_PRIMARY}; 
                          -webkit-background-clip: text; 
                          -webkit-text-fill-color: transparent; 
                          background-clip: text; 
                          margin: 0; 
                          font-size: 1.5rem; 
                          font-weight: 700;">
                    Ahorify
                </h2>
                <p style="color: {DesignSystem.TEXT_SECONDARY}; 
                         font-size: 0.8rem; 
                         margin: 2px 0 0 0; 
                         font-weight: 500;">
                    Tu Aventura Financiera 🗺️
                </p>
            </div>
            """
            
        except FileNotFoundError as e:
            print(f"🎯 Fallback a emoji: {e}")
            # 🔼 FALLBACK ELEGANTE
            return f"""
            <div style="text-align: center; margin-bottom: 2rem;">
                <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">💰</div>
                <h2 style="background: {DesignSystem.GRADIENT_PRIMARY}; 
                          -webkit-background-clip: text; 
                          -webkit-text-fill-color: transparent; 
                          background-clip: text; 
                          margin: 0;">
                    Ahorify
                </h2>
                <p style="color: {DesignSystem.TEXT_SECONDARY}; 
                         font-size: 0.875rem; 
                         margin: 0;">
                    Tu Aventura Financiera 🗺️
                </p>
            </div>
            """
    
    def setup_persistent_state(self):
        """Inicializa el estado de la sesión con persistencia en BD"""
        # Estado CRÍTICO que debe persistir entre sesiones
        critical_states = [
            'onboarding_complete', 
            'first_visit',
            'user_preferences'
        ]
        
        # Solo inicializar si no existen (preservar entre recargas)
        if 'first_visit' not in st.session_state:
            # Verificar en BD si el onboarding ya se completó
            onboarding_complete = self._check_onboarding_status()
            st.session_state.first_visit = not onboarding_complete
        
        if 'onboarding_complete' not in st.session_state:
            st.session_state.onboarding_complete = self._check_onboarding_status()
        
        if 'user_preferences' not in st.session_state:
            st.session_state.user_preferences = self._load_user_preferences()
        
        # Estado temporal (se resetea entre sesiones)
        if 'current_page' not in st.session_state:
            st.session_state.current_page = "quick_add"
            
        if 'onboarding_step' not in st.session_state:
            st.session_state.onboarding_step = 0
            
        if 'show_onboarding' not in st.session_state:
            st.session_state.show_onboarding = False
    
    def _check_onboarding_status(self) -> bool:
        """Verifica en BD si el onboarding ya fue completado - VERSIÓN CORREGIDA"""
        try:
           with db.get_connection() as conn:
                cursor = conn.execute(
                    "SELECT onboarding_complete FROM user_preferences WHERE user_id = ?",
                    ("default_user",)
                )
                result = cursor.fetchone()
            
                # 🔼 LÓGICA CRÍTICA: Si no existe registro = usuario NUEVO
                if result is None:
                    return False  # Usuario NUEVO debe hacer onboarding
                else:
                    return bool(result['onboarding_complete'])  # Usuario existente
                
        except Exception as e:
            print(f"Error checking onboarding status: {e}")
            return False  # En caso de error, usuario NUEVO

    def _load_user_preferences(self) -> dict:
        """Carga preferencias desde BD - VERSIÓN CORREGIDA"""
        try:
            with db.get_connection() as conn:
                cursor = conn.execute(
                    "SELECT * FROM user_preferences WHERE user_id = ?",
                    ("default_user",)
                )
                result = cursor.fetchone()
            
                if result:
                    # ✅ Usuario EXISTENTE
                    return {
                        "primary_goal": result['primary_goal'],
                        "currency": result['currency'] or '€',
                        "notifications": bool(result['notifications_enabled']),
                        "weekly_report": bool(result['weekly_reports_enabled']),
                        "theme": result['theme'] or 'Automático'
                    }
        except Exception as e:
            print(f"Error loading user preferences: {e}")
    
        # ❌ Usuario NUEVO o error
        return {
            "primary_goal": None,
            "currency": '€',
            "notifications": True,
            "weekly_report": True,
            "theme": 'Automático'
        }
    
    def _save_onboarding_completion(self):
        """Guarda en BD que el onboarding fue completado"""
        try:
            with db.get_connection() as conn:
                # Usar UPSERT para insertar o actualizar
                conn.execute('''
                    INSERT OR REPLACE INTO user_preferences 
                    (user_id, onboarding_complete, primary_goal, currency, 
                     notifications_enabled, weekly_reports_enabled, theme, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ''', (
                    "default_user",
                    True,
                    st.session_state.user_preferences.get('primary_goal'),
                    st.session_state.user_preferences.get('currency', '€'),
                    st.session_state.user_preferences.get('notifications', True),
                    st.session_state.user_preferences.get('weekly_report', True),
                    st.session_state.user_preferences.get('theme', 'Automático')
                ))
                return True
        except Exception as e:
            print(f"Error guardando onboarding: {e}")
            return False
    
    def _ensure_preferences_table(self):
        """Asegura que la tabla user_preferences existe"""
        try:
            with db.get_connection() as conn:
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS user_preferences (
                        user_id TEXT PRIMARY KEY,
                        onboarding_complete BOOLEAN DEFAULT FALSE,
                        primary_goal TEXT,
                        currency TEXT DEFAULT '€',
                        notifications_enabled BOOLEAN DEFAULT TRUE,
                        weekly_reports_enabled BOOLEAN DEFAULT TRUE,
                        theme TEXT DEFAULT 'Automático',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
        except Exception as e:
            print(f"Error creando tabla preferences: {e}")
    
    def run(self):
        """Ejecuta la aplicación principal con flujo corregido"""
        # Inicializar BD y estado
        initialize_app()
        self._ensure_preferences_table()

        try:
            self.gamification_service.record_engagement("app_loaded")
        except Exception as e:
            print(f"⚠️ Error en gamificación inicial: {e}")
        
        # 🔄 FLUJO DECISIVO CORREGIDO - SIN AMBIGÜEDADES
        if st.session_state.first_visit:
            self.show_welcome_screen()
            return
        
        if not st.session_state.onboarding_complete or st.session_state.show_onboarding:
            self.show_onboarding()
            return
        
        # ✅ Onboarding COMPLETADO y PERSISTIDO - App principal
        self.render_main_app()
    
    def show_welcome_screen(self):
        """Pantalla de bienvenida inicial - SOLO primera vez"""
        st.markdown(f"""
        <div style="text-align: center; padding: 2rem 1rem;">
            <div style="font-size: 4rem; margin-bottom: 1rem;">💰</div>
            <h1 style="background: {DesignSystem.GRADIENT_PRIMARY}; -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; font-size: 3rem; font-weight: 800; margin-bottom: 1rem;">
                Ahorify
            </h1>
            <p style="font-size: 1.25rem; color: {DesignSystem.TEXT_SECONDARY}; margin-bottom: 2rem;">
                Transforma tus finanzas en una aventura gamificada
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Tarjetas de características
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <div class="ah-card" style="text-align: center;">
                <div style="font-size: 2rem;">🎮</div>
                <h3>Gamificación</h3>
                <p style="color: {DesignSystem.TEXT_SECONDARY}; font-size: 0.875rem;">
                    Niveles, puntos y rachas como en Duolingo
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="ah-card" style="text-align: center;">
                <div style="font-size: 2rem;">📱</div>
                <h3>Mobile-First</h3>
                <p style="color: {DesignSystem.TEXT_SECONDARY}; font-size: 0.875rem;">
                    Diseñado para usar en tu móvil
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="ah-card" style="text-align: center;">
                <div style="font-size: 2rem;">🚀</div>
                <h3>Rápido</h3>
                <p style="color: {DesignSystem.TEXT_SECONDARY}; font-size: 0.875rem;">
                    Registro en segundos - 1 tap
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        # Botón de comenzar
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🎯 Comenzar Mi Aventura", use_container_width=True, type="primary"):
                # Marcar primera visita como completada e ir al onboarding
                st.session_state.first_visit = False
                st.session_state.show_onboarding = True
                st.rerun()
    
    def show_onboarding(self):
        """Sistema de onboarding paso a paso"""
        onboarding_steps = [
            {
                "title": "¡Bienvenido a Ahorify!",
                "description": "Vamos a configurar tu aventura financiera en 3 pasos rápidos",
                "emoji": "👋",
                "progress": 0
            },
            {
                "title": "Tu Primer Objetivo",
                "description": "¿Qué te gustaría lograr con tus finanzas?",
                "emoji": "🎯",
                "progress": 33
            },
            {
                "title": "Configuración Rápida", 
                "description": "Personaliza tu experiencia",
                "emoji": "⚙️",
                "progress": 66
            },
            {
                "title": "¡Listo para Comenzar!",
                "description": "Tu aventura financiera está por empezar",
                "emoji": "🚀",
                "progress": 100
            }
        ]
        
        current_step = st.session_state.onboarding_step
        step_data = onboarding_steps[current_step]
        
        # Header del onboarding
        st.markdown(f"""
        <div style="text-align: center; padding: 1rem;">
            <div style="font-size: 3rem; margin-bottom: 1rem;">{step_data['emoji']}</div>
            <h2>{step_data['title']}</h2>
            <p style="color: {DesignSystem.TEXT_SECONDARY};">{step_data['description']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Barra de progreso
        st.progress(step_data['progress'] / 100)
        st.caption(f"Paso {current_step + 1} de {len(onboarding_steps)}")
        
        # Contenido específico por paso
        if current_step == 0:
            self._onboarding_step_welcome()
        elif current_step == 1:
            self._onboarding_step_goals()
        elif current_step == 2:
            self._onboarding_step_preferences()
        else:
            self._onboarding_step_complete()
    
    def _onboarding_step_welcome(self):
        """Paso 1 del onboarding - Bienvenida"""
        st.markdown("""
        <div class="ah-card">
            <h4>🎮 Tu Aventura Gamificada</h4>
            <p>En Ahorify transformamos las finanzas aburridas en una aventura:</p>
            <ul>
                <li><strong>Niveles y puntos</strong> por tus logros financieros</li>
                <li><strong>Rachas Duolingo-style</strong> para mantener la consistencia</li>
                <li><strong>Metas visuales</strong> que te motivan a seguir</li>
                <li><strong>Insights inteligentes</strong> para mejorar tus finanzas</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("✅ Entendido, ¡siguiente!", use_container_width=True):
            st.session_state.onboarding_step = 1
            st.rerun()
    
    def _onboarding_step_goals(self):
        """Paso 2 del onboarding - Establecer objetivos"""
        st.markdown("""
        <div class="ah-card">
            <h4>🎯 Define Tu Primer Objetivo</h4>
            <p>Selecciona lo que más te motiva:</p>
        </div>
        """, unsafe_allow_html=True)
        
        goals = [
            {"emoji": "💰", "title": "Controlar Gastos", "description": "Saber en qué gasto y optimizar"},
            {"emoji": "🏠", "title": "Ahorrar para un Objetivo", "description": "Viaje, coche, entrada..."},
            {"emoji": "📈", "title": "Crear Hábitos Financieros", "description": "Construir disciplina financiera"},
            {"emoji": "🎓", "title": "Aprender de Mis Finanzas", "description": "Entender mis patrones de gasto"}
        ]
        
        selected_goal = st.radio(
            "Selecciona tu objetivo principal:",
            options=[goal["title"] for goal in goals],
            format_func=lambda x: next(
                f"{goal['emoji']} {goal['title']} - {goal['description']}" 
                for goal in goals if goal["title"] == x
            )
        )
        
        st.session_state.user_preferences["primary_goal"] = selected_goal
        
        if st.button("🎯 Guardar Objetivo", use_container_width=True):
            st.session_state.onboarding_step = 2
            st.rerun()
    
    def _onboarding_step_preferences(self):
        """Paso 3 del onboarding - Preferencias"""
        st.markdown("""
        <div class="ah-card">
            <h4>⚙️ Personaliza Tu Experiencia</h4>
            <p>Configura Ahorify a tu gusto:</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.session_state.user_preferences["notifications"] = st.toggle(
                "Notificaciones de rachas",
                value=True,
                help="Recuerda mantener tu racha diaria"
            )
            
            currency = st.selectbox(
                "Moneda preferida",
                options=["€ Euro", "$ Dólar", "£ Libra", "Otro"],
                index=0
            )
            st.session_state.user_preferences["currency"] = currency[0]
        
        with col2:
            st.session_state.user_preferences["weekly_report"] = st.toggle(
                "Resumen semanal",
                value=True,
                help="Recibe insights de tu semana financiera"
            )
            
            st.session_state.user_preferences["theme"] = st.selectbox(
                "Tema de color",
                options=["Claro", "Oscuro", "Automático"],
                index=2
            )
        
        if st.button("🚀 Completar Configuración", use_container_width=True, type="primary"):
            st.session_state.onboarding_step = 3
            st.rerun()
    
    def _onboarding_step_complete(self):
        """Paso final del onboarding - GUARDADO PERSISTENTE"""
        st.balloons()
        
        # 🔼 GUARDAR EN BASE DE DATOS DE FORMA PERMANENTE
        success = self._save_onboarding_completion()
        
        if success:
            st.markdown(f"""
            <div class="ah-card ah-card-gamified">
                <div style="text-align: center;">
                    <div style="font-size: 4rem;">🎉</div>
                    <h2>¡Configuración Guardada Permanentemente!</h2>
                    <p>Tu onboarding está completo y no volverá a aparecer</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Resumen de configuración
            st.markdown("""
            <div class="ah-card">
                <h4>📋 Tu Configuración Guardada</h4>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Objetivo:** {st.session_state.user_preferences.get('primary_goal', 'No definido')}")
                st.write(f"**Moneda:** {st.session_state.user_preferences.get('currency', '€')}")
            
            with col2:
                notifications = "✅ Activadas" if st.session_state.user_preferences.get("notifications") else "❌ Desactivadas"
                st.write(f"**Notificaciones:** {notifications}")
                st.write(f"**Tema:** {st.session_state.user_preferences.get('theme', 'Automático')}")
            
            if st.button("🗺️ Comenzar Mi Aventura Financiero", use_container_width=True, type="primary"):
                # 🔼 ESTADO FINAL DEFINITIVO
                st.session_state.onboarding_complete = True
                st.session_state.show_onboarding = False
                st.session_state.onboarding_step = 0
                st.session_state.current_page = "quick_add"
                st.rerun()
        else:
            st.error("""
            ❌ Error guardando configuración permanente. 
            Tu progreso podría perderse al recargar.
            """)
    
    def render_main_app(self):
        """Aplicación principal - SOLO cuando onboarding está COMPLETO"""
        # Sidebar con navegación y progreso
        with st.sidebar:
            self.render_sidebar()
        
        # Navegación móvil
        self.render_mobile_navigation()
        
        # Contenido principal
        self.render_page_content()
    
    def render_sidebar(self):
        """Sidebar con navegación - VERSIÓN CON LOGO"""
        # 🔼 USAR EL LOGO EN LUGAR DEL EMOJI
        st.markdown(self._load_logo_html(), unsafe_allow_html=True)
        
        # Progreso del usuario
        try:
            from ui.components.level_badge import LevelBadge
            level_badge = LevelBadge()
            level_badge.render_compact()
        except Exception as e:
            st.info("🎯 Comienza registrando transacciones")
        
        st.markdown("---")
        
        # Navegación principal (se mantiene igual)
        st.markdown("### 🧭 Navegación")
        
        pages = {
            "quick_add": {"emoji": "💸", "name": "Registro Rápido"},
            "dashboard": {"emoji": "📊", "name": "Dashboard"},
            "import_csv": {"emoji": "📤", "name": "Importar CSV"}
        }
        
        for page_id, page_info in pages.items():
            if st.button(
                f"{page_info['emoji']} {page_info['name']}",
                key=f"nav_{page_id}",
                use_container_width=True,
                type="primary" if st.session_state.current_page == page_id else "secondary"
            ):
                st.session_state.current_page = page_id
                st.rerun()
        
        st.markdown("---")
        
        # Información adicional
        self.render_sidebar_footer()
    
    def render_sidebar_footer(self):
        """Footer del sidebar"""
        st.markdown("### 💡 Tips Rápidos")
        
        tips = [
            "💸 **Registra cada gasto** para mantener tu racha",
            "📊 **Revisa tu dashboard** semanalmente", 
            "🎯 **Mantén tu objetivo** en mente",
            "🔥 **No rompas la racha** - vuelve cada día"
        ]
        
        import random
        st.info(random.choice(tips))
        
        st.markdown("---")
        
        st.markdown("#### 🔗 Accesos Directos")
        
        if st.button("🔄 Reiniciar Onboarding", use_container_width=True):
            # Resetear en BD también
            try:
                with db.get_connection() as conn:
                    conn.execute(
                        "UPDATE user_preferences SET onboarding_complete = FALSE WHERE user_id = ?",
                        ("default_user",)
                    )
            except:
                pass
            
            st.session_state.onboarding_complete = False
            st.session_state.first_visit = True
            st.session_state.show_onboarding = True
            st.session_state.onboarding_step = 0
            st.rerun()
    
    def render_mobile_navigation(self):
        """Navegación móvil optimizada"""
        # (código igual al anterior - manteniendo por brevedad)
        pass
    
    def render_page_content(self):
        """Renderiza el contenido de la página actual"""
        st.markdown("""
        <style>
        @media (max-width: 768px) {
            .main-content {
                padding-bottom: 80px;
            }
        }
        </style>
        <div class="main-content">
        """, unsafe_allow_html=True)
        
        try:
            if st.session_state.current_page == "quick_add":
                show_quick_add()
            elif st.session_state.current_page == "dashboard":
                show_dashboard()
            elif st.session_state.current_page == "import_csv":
                show_import_csv()
            else:
                show_quick_add()
        except Exception as e:
            self.show_error_page(e)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    def show_error_page(self, error):
        """Página de error elegante"""
        st.error("🚨 ¡Vaya! Algo salió mal")
        
        st.markdown(f"""
        <div class="ah-card">
            <h3>🔧 Solución Rápida</h3>
            <p>Intenta una de estas soluciones:</p>
            <ul>
                <li><strong>Recarga la página</strong> (F5 o pull-to-refresh)</li>
                <li><strong>Ve a Registro Rápido</strong> y vuelve</li>
                <li><strong>Limpia el cache</strong> del navegador</li>
            </ul>
            <p style="color: {DesignSystem.TEXT_SECONDARY}; font-size: 0.875rem;">
                Error técnico: {str(error)}
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔄 Recargar Página", use_container_width=True):
                st.rerun()
        
        with col2:
            if st.button("🏠 Ir a Inicio", use_container_width=True):
                st.session_state.current_page = "quick_add"
                st.rerun()

def main():
    """Función principal de la aplicación"""
    try:
        app = AhorifyApp()
        app.run()
    except Exception as e:
        st.error("❌ Error crítico en la aplicación")
        st.info("Por favor, recarga la página.")
        
        if st.button("🔄 Reiniciar Aplicación"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

if __name__ == "__main__":
    main()
## activar venv:    source venv_env/bin/activate
## activar st:      streamlit run main.py