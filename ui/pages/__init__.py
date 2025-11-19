"""
📄 App Pages - Páginas de la Aplicación

Páginas principales de Ahorify optimizadas para mobile-first
y experiencia de usuario gamificada.
"""
from .quick_add import show_quick_add
from .dashboard import show_dashboard
from .import_csv import show_import_csv

__all__ = [
    'show_quick_add',    # 🏠 Página principal - Registro rápido
    'show_dashboard',    # 📊 Dashboard con métricas
    'show_import_csv'    # 📥 Importación de datos
]