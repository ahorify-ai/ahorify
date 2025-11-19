# config.py
"""
Global configuration + CSS mobile-first premium.
Design System: Mint Green + White Minimal + Gamification accents.
Mobile-first, dark-mode ready, accessibility focused.
"""

import streamlit as st
from typing import Dict, Any

# ==================== DESIGN SYSTEM TOKENS ====================
class DesignSystem:
    """Sistema de diseño centralizado para Ahorify"""
    
    # Palette Principal - Mint Green + Accents gamificados
    PRIMARY = "#10B981"          # Verde principal - Confianza
    PRIMARY_LIGHT = "#34D399"    # Verde claro - Acciones positivas
    PRIMARY_DARK = "#059669"     # Verde oscuro - Hover states
    
    ACCENT_GAMIFICATION = "#EB43DD"  # Rosa - Elementos gamificación
    ACCENT_WARNING = "#F59E0B"       # Amber - Alertas
    ACCENT_ERROR = "#EF4444"         # Rojo - Errores
    ACCENT_SUCCESS = "#10B981"       # Verde - Éxito
    
    # Neutral Scale - Accesibilidad AAA compliant
    NEUTRAL_50 = "#F8FAFC"
    NEUTRAL_100 = "#F1F5F9"
    NEUTRAL_200 = "#E2E8F0"
    NEUTRAL_300 = "#CBD5E1"
    NEUTRAL_400 = "#94A3B8"
    NEUTRAL_500 = "#64748B"
    NEUTRAL_600 = "#475569"
    NEUTRAL_700 = "#334155"
    NEUTRAL_800 = "#1E293B"
    NEUTRAL_900 = "#0F172A"
    
    # Backgrounds
    BG_PRIMARY = "#FFFFFF"
    BG_SECONDARY = "#F8FAFC"
    BG_CARD = "#FFFFFF"
    
    # Semantic Colors
    TEXT_PRIMARY = "#0F172A"
    TEXT_SECONDARY = "#475569"
    TEXT_DISABLED = "#94A3B8"
    
    # Gradients
    GRADIENT_PRIMARY = "linear-gradient(135deg, #10B981 0%, #059669 100%)"
    GRADIENT_SUCCESS = "linear-gradient(135deg, #10B981 0%, #34D399 100%)"
    GRADIENT_PREMIUM = "linear-gradient(135deg, #8B5CF6 0%, #EC4899 100%)"
    
    # Shadows - Depth system
    SHADOW_SM = "0 1px 2px 0 rgba(2, 6, 23, 0.05)"
    SHADOW_MD = "0 4px 6px -1px rgba(2, 6, 23, 0.1), 0 2px 4px -1px rgba(2, 6, 23, 0.06)"
    SHADOW_LG = "0 10px 15px -3px rgba(2, 6, 23, 0.1), 0 4px 6px -2px rgba(2, 6, 23, 0.05)"
    SHADOW_XL = "0 20px 25px -5px rgba(2, 6, 23, 0.1), 0 10px 10px -5px rgba(2, 6, 23, 0.04)"
    
    # Border Radius
    RADIUS_SM = "8px"
    RADIUS_MD = "12px"
    RADIUS_LG = "16px"
    RADIUS_XL = "24px"
    RADIUS_FULL = "9999px"
    
    # Spacing Scale
    SPACE_XS = "4px"
    SPACE_SM = "8px"
    SPACE_MD = "12px"
    SPACE_LG = "16px"
    SPACE_XL = "24px"
    SPACE_2XL = "32px"
    
    # Typography Scale
    FONT_FAMILY = "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif"
    FONT_SIZE_XS = "0.75rem"    # 12px
    FONT_SIZE_SM = "0.875rem"   # 14px
    FONT_SIZE_BASE = "1rem"     # 16px
    FONT_SIZE_LG = "1.125rem"   # 18px
    FONT_SIZE_XL = "1.25rem"    # 20px
    FONT_SIZE_2XL = "1.5rem"    # 24px
    FONT_SIZE_3XL = "1.875rem"  # 30px
    
    # Animations
    TRANSITION_FAST = "all 0.15s ease-in-out"
    TRANSITION_NORMAL = "all 0.25s ease-in-out"
    TRANSITION_SLOW = "all 0.35s ease-in-out"

DS = DesignSystem()

# ==================== PAGE CONFIGURATION ====================
def setup_page(
    title: str = "Ahorify - Tu Aventura Financiera 🗺️",
    layout: str = "centered",
    initial_sidebar_state: str = "collapsed",
    menu_items: Dict[str, Any] = None
):
    """
    Configuración premium de página Streamlit.
    """
    
    default_menu_items = {
        'Get Help': 'https://github.com/tu-repo/ahorify',
        'Report a bug': 'https://github.com/tu-repo/ahorify/issues',
        'About': "Ahorify - Transforma tus finanzas con gamificación 🎮"
    }
    
    st.set_page_config(
        page_title=title,
        page_icon="https://i.ibb.co/mCrhxktz/ahorify-icon.png", 
        layout=layout,
        initial_sidebar_state=initial_sidebar_state,
        menu_items=menu_items or default_menu_items
    )


# ==================== PREMIUM CSS INJECTION ====================
def inject_premium_css():
    """
    CSS mobile-first premium con:
    - Design system consistente
    - Animaciones sutiles
    - Estados de hover/focus
    - Modo oscuro preparado
    - Accesibilidad AAA
    """
    
    css = f"""
    <style>
    /* ===== CSS CUSTOM PROPERTIES ===== */
    :root {{
        /* Colors */
        --primary: {DS.PRIMARY};
        --primary-light: {DS.PRIMARY_LIGHT};
        --primary-dark: {DS.PRIMARY_DARK};
        --accent-gamification: {DS.ACCENT_GAMIFICATION};
        --accent-warning: {DS.ACCENT_WARNING};
        --accent-error: {DS.ACCENT_ERROR};
        --accent-success: {DS.ACCENT_SUCCESS};
        
        /* Neutrals */
        --neutral-50: {DS.NEUTRAL_50};
        --neutral-100: {DS.NEUTRAL_100};
        --neutral-200: {DS.NEUTRAL_200};
        --neutral-300: {DS.NEUTRAL_300};
        --neutral-400: {DS.NEUTRAL_400};
        --neutral-500: {DS.NEUTRAL_500};
        --neutral-600: {DS.NEUTRAL_600};
        --neutral-700: {DS.NEUTRAL_700};
        --neutral-800: {DS.NEUTRAL_800};
        --neutral-900: {DS.NEUTRAL_900};
        
        /* Backgrounds */
        --bg-primary: {DS.BG_PRIMARY};
        --bg-secondary: {DS.BG_SECONDARY};
        --bg-card: {DS.BG_CARD};
        
        /* Text */
        --text-primary: {DS.TEXT_PRIMARY};
        --text-secondary: {DS.TEXT_SECONDARY};
        --text-disabled: {DS.TEXT_DISABLED};
        
        /* Gradients */
        --gradient-primary: {DS.GRADIENT_PRIMARY};
        --gradient-success: {DS.GRADIENT_SUCCESS};
        --gradient-premium: {DS.GRADIENT_PREMIUM};
        
        /* Shadows */
        --shadow-sm: {DS.SHADOW_SM};
        --shadow-md: {DS.SHADOW_MD};
        --shadow-lg: {DS.SHADOW_LG};
        --shadow-xl: {DS.SHADOW_XL};
        
        /* Border Radius */
        --radius-sm: {DS.RADIUS_SM};
        --radius-md: {DS.RADIUS_MD};
        --radius-lg: {DS.RADIUS_LG};
        --radius-xl: {DS.RADIUS_XL};
        --radius-full: {DS.RADIUS_FULL};
        
        /* Spacing */
        --space-xs: {DS.SPACE_XS};
        --space-sm: {DS.SPACE_SM};
        --space-md: {DS.SPACE_MD};
        --space-lg: {DS.SPACE_LG};
        --space-xl: {DS.SPACE_XL};
        --space-2xl: {DS.SPACE_2XL};
        
        /* Typography */
        --font-family: {DS.FONT_FAMILY};
        --font-size-xs: {DS.FONT_SIZE_XS};
        --font-size-sm: {DS.FONT_SIZE_SM};
        --font-size-base: {DS.FONT_SIZE_BASE};
        --font-size-lg: {DS.FONT_SIZE_LG};
        --font-size-xl: {DS.FONT_SIZE_XL};
        --font-size-2xl: {DS.FONT_SIZE_2XL};
        --font-size-3xl: {DS.FONT_SIZE_3XL};
        
        /* Transitions */
        --transition-fast: {DS.TRANSITION_FAST};
        --transition-normal: {DS.TRANSITION_NORMAL};
        --transition-slow: {DS.TRANSITION_SLOW};
    }}

    /* ===== BASE STYLES ===== */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    * {{
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }}
    
    html, body, [class*="css-"] {{
        font-family: var(--font-family);
        color: var(--text-primary);
        background-color: var(--bg-primary);
        line-height: 1.5;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
    }}

    /* ===== LAYOUT COMPONENTS ===== */
    .ah-container {{
        max-width: 100%;
        margin: 0 auto;
        padding: var(--space-md);
    }}
    
    .ah-section {{
        margin-bottom: var(--space-2xl);
    }}
    
    .ah-section-title {{
        font-size: var(--font-size-2xl);
        font-weight: 700;
        color: var(--text-primary);
        margin-bottom: var(--space-lg);
        background: var(--gradient-primary);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }}

    /* ===== CARD SYSTEM ===== */
    .ah-card {{
        background: var(--bg-card);
        border-radius: var(--radius-lg);
        padding: var(--space-lg);
        box-shadow: var(--shadow-md);
        border: 1px solid var(--neutral-200);
        transition: var(--transition-normal);
        margin-bottom: var(--space-md);
    }}
    
    .ah-card:hover {{
        box-shadow: var(--shadow-lg);
        transform: translateY(-2px);
    }}
    
    .ah-card-gamified {{
        background: var(--gradient-primary);
        color: white;
        border: none;
    }}
    
    .ah-card-gamified .ah-card-title {{
        color: white;
    }}
    
    .ah-card-premium {{
        background: var(--gradient-premium);
        color: white;
        border: none;
    }}

    /* ===== TYPOGRAPHY ENHANCEMENTS ===== */
    .ah-title {{
        font-size: var(--font-size-3xl);
        font-weight: 800;
        background: var(--gradient-primary);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: var(--space-sm);
        line-height: 1.2;
    }}
    
    .ah-subtitle {{
        font-size: var(--font-size-lg);
        color: var(--text-secondary);
        font-weight: 500;
        margin-bottom: var(--space-lg);
    }}
    
    .ah-label {{
        font-size: var(--font-size-sm);
        font-weight: 600;
        color: var(--text-secondary);
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: var(--space-xs);
        display: block;
    }}

    /* ===== DATA VISUALIZATION ===== */
    .ah-metric-card {{
        background: var(--bg-card);
        border-radius: var(--radius-md);
        padding: var(--space-lg);
        text-align: center;
        box-shadow: var(--shadow-sm);
        border-left: 4px solid var(--primary);
        transition: var(--transition-fast);
    }}
    
    .ah-metric-card:hover {{
        box-shadow: var(--shadow-md);
        border-left-color: var(--primary-light);
    }}
    
    .ah-metric-value {{
        font-size: var(--font-size-2xl);
        font-weight: 700;
        color: var(--text-primary);
        line-height: 1;
        margin-bottom: var(--space-xs);
    }}
    
    .ah-metric-label {{
        font-size: var(--font-size-sm);
        color: var(--text-secondary);
        font-weight: 500;
    }}
    
    .ah-metric-trend-positive {{
        color: var(--accent-success);
        font-weight: 600;
    }}
    
    .ah-metric-trend-negative {{
        color: var(--accent-error);
        font-weight: 600;
    }}

    /* ===== BADGE SYSTEM ===== */
    .ah-badge {{
        display: inline-flex;
        align-items: center;
        padding: var(--space-xs) var(--space-sm);
        border-radius: var(--radius-full);
        font-size: var(--font-size-xs);
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-right: var(--space-xs);
        margin-bottom: var(--space-xs);
        transition: var(--transition-fast);
    }}
    
    .ah-badge-primary {{
        background: rgba(16, 185, 129, 0.12);
        color: var(--primary-dark);
        border: 1px solid rgba(16, 185, 129, 0.2);
    }}
    
    .ah-badge-gamification {{
        background: rgba(235, 67, 221, 0.12);
        color: var(--accent-gamification);
        border: 1px solid rgba(235, 67, 221, 0.2);
    }}
    
    .ah-badge-success {{
        background: rgba(16, 185, 129, 0.12);
        color: var(--accent-success);
        border: 1px solid rgba(16, 185, 129, 0.2);
    }}
    
    .ah-badge-warning {{
        background: rgba(245, 158, 11, 0.12);
        color: var(--accent-warning);
        border: 1px solid rgba(245, 158, 11, 0.2);
    }}
    
    .ah-badge-error {{
        background: rgba(239, 68, 68, 0.12);
        color: var(--accent-error);
        border: 1px solid rgba(239, 68, 68, 0.2);
    }}

    /* ===== BUTTON ENHANCEMENTS ===== */
    .stButton > button {{
        border-radius: var(--radius-md);
        font-weight: 600;
        transition: var(--transition-fast);
        border: none;
    }}
    
    .stButton > button:focus {{
        box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.2);
    }}
    
    /* Primary Button */
    .stButton > button:first-child {{
        background: var(--gradient-primary);
    }}
    
    .stButton > button:first-child:hover {{
        background: var(--primary-dark);
        transform: translateY(-1px);
        box-shadow: var(--shadow-lg);
    }}

    /* ===== FORM ENHANCEMENTS ===== */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > select {{
        border-radius: var(--radius-md);
        border: 1px solid var(--neutral-300);
        transition: var(--transition-fast);
    }}
    
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus,
    .stSelectbox > div > div > select:focus {{
        border-color: var(--primary);
        box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.2);
    }}
    
    /* ===== PROGRESS & LOADING ===== */
    .ah-progress-container {{
        background: var(--neutral-200);
        border-radius: var(--radius-full);
        overflow: hidden;
        height: 8px;
        margin: var(--space-sm) 0;
    }}
    
    .ah-progress-bar {{
        height: 100%;
        background: var(--gradient-primary);
        border-radius: var(--radius-full);
        transition: width 0.5s ease-in-out;
    }}
    
    .ah-progress-bar-gamified {{
        background: var(--gradient-premium);
    }}

    /* ===== STREAK & GAMIFICATION ===== */
    .ah-streak-counter {{
        display: inline-flex;
        align-items: center;
        background: rgba(245, 158, 11, 0.1);
        color: var(--accent-warning);
        padding: var(--space-xs) var(--space-sm);
        border-radius: var(--radius-full);
        font-weight: 700;
        font-size: var(--font-size-sm);
    }}
    
    .ah-level-badge {{
        display: inline-flex;
        align-items: center;
        background: var(--gradient-primary);
        color: white;
        padding: var(--space-xs) var(--space-md);
        border-radius: var(--radius-full);
        font-weight: 700;
        font-size: var(--font-size-sm);
        box-shadow: var(--shadow-md);
    }}

    /* ===== RESPONSIVE GRID SYSTEM ===== */
    .ah-grid {{
        display: grid;
        gap: var(--space-md);
        width: 100%;
    }}
    
    /* Mobile First - 1 column */
    .ah-grid-cols-1 {{ grid-template-columns: 1fr; }}
    
    /* Tablet - 2 columns */
    @media (min-width: 768px) {{
        .ah-grid-cols-2 {{ grid-template-columns: repeat(2, 1fr); }}
        .ah-grid-cols-3 {{ grid-template-columns: repeat(3, 1fr); }}
    }}
    
    /* Desktop - 3+ columns */
    @media (min-width: 1024px) {{
        .ah-grid-cols-4 {{ grid-template-columns: repeat(4, 1fr); }}
        .ah-container {{ max-width: 1200px; }}
    }}

    /* ===== STREAMLIT OVERRIDES ===== */
    /* Hide menu and footer for cleaner mobile experience */
    #MainMenu {{ visibility: hidden; }}
    footer {{ visibility: hidden; }}
    
    /* Improve sidebar */
    .css-1d391kg {{ 
        background: var(--bg-secondary);
        border-right: 1px solid var(--neutral-200);
    }}
    
    /* Loading spinner color */
    .stSpinner > div > div {{
        border-top-color: var(--primary) !important;
    }}

    /* ===== DARK MODE PREPARATION ===== */
    @media (prefers-color-scheme: dark) {{
        :root {{
            --bg-primary: #0F172A;
            --bg-secondary: #1E293B;
            --bg-card: #1E293B;
            --text-primary: #F1F5F9;
            --text-secondary: #CBD5E1;
            --neutral-200: #334155;
            --neutral-300: #475569;
        }}
    }}
    </style>
    """
    
    st.markdown(css, unsafe_allow_html=True)

# ==================== UTILITY FUNCTIONS ====================
def get_color_scheme() -> Dict[str, str]:
    """Devuelve el esquema de colores para uso en gráficos"""
    return {
        "primary": DS.PRIMARY,
        "success": DS.ACCENT_SUCCESS,
        "warning": DS.ACCENT_WARNING,
        "error": DS.ACCENT_ERROR,
        "gamification": DS.ACCENT_GAMIFICATION,
    }

def get_spacing(level: str) -> str:
    """Devuelve el spacing consistente con el design system"""
    spacing_map = {
        "xs": DS.SPACE_XS,
        "sm": DS.SPACE_SM,
        "md": DS.SPACE_MD,
        "lg": DS.SPACE_LG,
        "xl": DS.SPACE_XL,
        "2xl": DS.SPACE_2XL,
    }
    return spacing_map.get(level, DS.SPACE_MD)

# ==================== INITIALIZATION ====================
def initialize_app():
    """Inicialización completa de la aplicación"""
    setup_page()
    inject_premium_css()
    
    # Configuración adicional de Streamlit
    st.markdown(
        """
        <script>
        // Smooth scrolling para mejor UX móvil
        document.addEventListener('DOMContentLoaded', function() {
            document.documentElement.style.scrollBehavior = 'smooth';
        });
        </script>
        """,
        unsafe_allow_html=True
    )