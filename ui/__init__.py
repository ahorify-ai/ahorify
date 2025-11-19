"""
🎨 UI Layer - Capa de Presentación

Módulo de interfaz de usuario mobile-first con componentes
reutilizables y páginas optimizadas para experiencia móvil.
"""
# Importaciones principales para acceso directo
from .pages import show_quick_add, show_dashboard, show_import_csv
from .components import (
    QuickEntryForm, LevelBadge, StreakDisplay, 
    ProgressBars, FinancialCharts
)

__all__ = [
    # Páginas principales
    'show_quick_add',
    'show_dashboard', 
    'show_import_csv',
    
    # Componentes reutilizables
    'QuickEntryForm',
    'LevelBadge',
    'StreakDisplay',
    'ProgressBars', 
    'FinancialCharts'
]