"""
ahorify/
├── 🚀 main.py                          # Punto de entrada - Streamlit App
├── ⚙️ config.py                        # Configuración, CSS, Design System
├── 🔧 requirements.txt                 # Dependencias
├── 📋 README.md                        # Documentación
│ 
├── 📊 core/                           # LÓGICA DE NEGOCIO
│   ├── __init__.py
│   ├── models.py                      # Transaction, UserStats, TransactionEmotion
│   ├── database.py                    # SQLite connection & queries  
│   └── services/                      # SERVICIOS DE NEGOCIO
│       ├── __init__.py
│       ├── transaction_service.py     # Gestión transacciones + categorías
│       ├── gamification_service.py    # Sistema niveles + puntos + rachas
│       └── analytics_service.py       # Cálculos para dashboard
│
├── 🎨 ui/                             # CAPA DE PRESENTACIÓN
│   ├── __init__.py
│   ├── components/                    # COMPONENTES REUSABLES
│   │   ├── __init__.py
│   │   ├── quick_entry.py            # Formulario con emociones ✅
│   │   ├── level_badge.py            # Badge nivel usuario
│   │   ├── streak_display.py         # Rachas visuales  
│   │   ├── progress_bars.py          # Barras progreso
│   │   └── charts.py                 # Gráficos reusables
│   └── pages/                        # PÁGINAS DE LA APP
│       ├── __init__.py
│       ├── quick_add.py              # Página principal - Registro rápido ✅
│       ├── dashboard.py              # Dashboard visual + métricas
│       └── import_csv.py             # Importación archivos
│
├── 📁 data/                          # DATOS PERSISTENTES
│   └── ahorify.db                    # Base de datos SQLite
│
└── 🗑️ venv/                          # ENTORNO VIRTUAL (si existe)
"""