"""
🧩 UI Components - Componentes Reutilizables

Sistema de componentes modulares y reutilizables para
construir interfaces consistentes en toda la aplicación.
"""
from .quick_entry import QuickEntryForm
from .level_badge import LevelBadge, render_level_badge
from .streak_display import StreakDisplay, render_streak_display
from .progress_bars import ProgressBars, render_level_progress, render_savings_goal
from .charts import FinancialCharts, render_category_chart, render_quick_dashboard

__all__ = [
    # Componentes principales
    'QuickEntryForm',
    'LevelBadge', 
    'StreakDisplay',
    'ProgressBars',
    'FinancialCharts',
    
    # Funciones de utilidad rápidas
    'render_level_badge',
    'render_streak_display', 
    'render_level_progress',
    'render_savings_goal',
    'render_category_chart',
    'render_quick_dashboard'
]