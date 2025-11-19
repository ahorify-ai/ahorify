# core/database.py
import sqlite3
import os
import logging
from contextlib import contextmanager
from typing import Generator, List, Optional, Dict, Any, Tuple
from datetime import datetime, date, timedelta
from pathlib import Path

logger = logging.getLogger(__name__)

class Database:
    """
    Sistema de base de datos robusto para Ahorify con:
    - Migraciones automáticas de esquema
    - Manejo de errores mejorado
    - Optimizaciones de performance
    - Backup automático
    """
    
    _instance = None
    _SCHEMA_VERSION = 4  # Incrementar cuando haya cambios en el esquema
    
    # Esquema completo definido centralmente
    SCHEMA = {
        'user_preferences': '''
            CREATE TABLE user_preferences (
                user_id TEXT PRIMARY KEY DEFAULT 'default_user',
                onboarding_complete BOOLEAN DEFAULT FALSE,
                primary_goal TEXT,
                currency TEXT DEFAULT '€',
                notifications_enabled BOOLEAN DEFAULT TRUE,
                weekly_reports_enabled BOOLEAN DEFAULT TRUE,
                theme TEXT DEFAULT 'Automático',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''',
        'transactions': '''
            CREATE TABLE transactions (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL DEFAULT 'default_user',
                amount REAL NOT NULL CHECK (amount > 0),
                type TEXT NOT NULL CHECK (type IN ('expense', 'income')),
                category TEXT NOT NULL,
                emotion TEXT NOT NULL CHECK (emotion IN ('neutral', 'happy', 'impulsive', 'stress', 'investment')), 
                description TEXT DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''',
        'user_stats': '''
            CREATE TABLE user_stats (
                user_id TEXT PRIMARY KEY DEFAULT 'default_user',
                current_streak INTEGER DEFAULT 0 CHECK (current_streak >= 0),
                longest_streak INTEGER DEFAULT 0 CHECK (longest_streak >= 0),
                total_points INTEGER DEFAULT 0 CHECK (total_points >= 0),
                total_streak_days INTEGER DEFAULT 0 CHECK (total_streak_days >= 0),
                last_activity_date TEXT,
                freeze_used_this_week BOOLEAN DEFAULT FALSE,
                recovery_used_this_month BOOLEAN DEFAULT FALSE,
                streak_protection_used BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''',
        'streak_milestones': '''
            CREATE TABLE streak_milestones (
                user_id TEXT NOT NULL DEFAULT 'default_user',
                milestone_days INTEGER NOT NULL,
                achieved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                reward_claimed BOOLEAN DEFAULT FALSE,
                PRIMARY KEY (user_id, milestone_days)
            )
        ''',
        'user_categories': '''
            CREATE TABLE user_categories (
                user_id TEXT NOT NULL DEFAULT 'default_user',
                category_name TEXT NOT NULL,
                usage_count INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (user_id, category_name)
            )
        ''',
        'daily_engagement': '''
            CREATE TABLE daily_engagement (
                user_id TEXT NOT NULL DEFAULT 'default_user',
                activity_date TEXT NOT NULL,
                actions_count INTEGER DEFAULT 1,
                actions_types TEXT DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (user_id, activity_date)
            )
        ''',
        'schema_info': '''
            CREATE TABLE schema_info (
                version INTEGER PRIMARY KEY,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        '''
    }
    
    # Índices para optimización
    INDEXES = [
        'CREATE INDEX IF NOT EXISTS idx_user_preferences_user ON user_preferences(user_id)',
        'CREATE INDEX IF NOT EXISTS idx_transactions_user_id ON transactions(user_id)',
        'CREATE INDEX IF NOT EXISTS idx_transactions_created_at ON transactions(created_at)',
        'CREATE INDEX IF NOT EXISTS idx_transactions_type ON transactions(type)',
        'CREATE INDEX IF NOT EXISTS idx_user_categories_user ON user_categories(user_id)',
        'CREATE INDEX IF NOT EXISTS idx_daily_engagement_user_date ON daily_engagement(user_id, activity_date)',
        'CREATE INDEX IF NOT EXISTS idx_streak_milestones_user ON streak_milestones(user_id)',
        'CREATE INDEX IF NOT EXISTS idx_user_stats_user ON user_stats(user_id)'
    ]
    
    # Datos iniciales
    DEFAULT_CATEGORIES = [
        "🍔 Comida", "🚗 Transporte", "🎮 Ocio", "🏠 Vivienda",
        "👗 Ropa", "💊 Salud", "📚 Educación", "✈️ Viajes",
        "🎁 Regalos", "📱 Tecnología", "💡 Servicios", "💰 Ahorros",
        "💼 Ingresos", "❓ Otros"
    ]

    def __new__(cls, db_path: str = "data/ahorify.db"):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
            cls._instance.db_path = db_path
            cls._instance._initialize_database()
        return cls._instance

    def _initialize_database(self):
        """Inicialización completa de la base de datos con migraciones"""
        try:
            self._ensure_data_directory()
            self._create_backup()
            
            with self.get_connection() as conn:
                # Verificar versión actual del esquema
                current_version = self._get_schema_version(conn)
                
                if current_version == 0:
                    # Base de datos nueva - crear esquema completo
                    self._create_full_schema(conn)
                    self._insert_initial_data(conn)
                    logger.info("✅ Esquema de base de datos creado exitosamente")
                elif current_version < self._SCHEMA_VERSION:
                    # Migrar de versión antigua
                    self._migrate_schema(conn, current_version)
                    logger.info(f"✅ Esquema migrado de v{current_version} a v{self._SCHEMA_VERSION}")
                else:
                    logger.info("✅ Esquema de base de datos actualizado")
                    
        except Exception as e:
            logger.error(f"❌ Error inicializando base de datos: {e}")
            raise

    def _ensure_data_directory(self):
        """Asegura que el directorio data/ existe"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

    def _create_backup(self):
        """Crea backup de la base de datos existente"""
        if os.path.exists(self.db_path):
            backup_path = f"{self.db_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            import shutil
            shutil.copy2(self.db_path, backup_path)
            logger.info(f"📦 Backup creado: {backup_path}")

    def _get_schema_version(self, conn: sqlite3.Connection) -> int:
        """Obtiene la versión actual del esquema"""
        try:
            cursor = conn.execute("SELECT version FROM schema_info ORDER BY version DESC LIMIT 1")
            result = cursor.fetchone()
            return result[0] if result else 0
        except sqlite3.OperationalError:
            return 0  # Tabla schema_info no existe

    def _create_full_schema(self, conn: sqlite3.Connection):
        """Crea el esquema completo desde cero"""
        # Crear tablas
        for table_name, schema in self.SCHEMA.items():
            conn.execute(schema)
        
        # Crear índices
        for index_sql in self.INDEXES:
            conn.execute(index_sql)
        
        # Establecer versión del esquema
        conn.execute("INSERT INTO schema_info (version) VALUES (?)", (self._SCHEMA_VERSION,))
        conn.commit()

    def _migrate_schema(self, conn: sqlite3.Connection, from_version: int):
        """Migra el esquema desde una versión anterior"""
        migrations = {
            1: self._migrate_v1_to_v2,
            2: self._migrate_v2_to_v3,
            3: self._migrate_v3_to_v4,
        }
        
        current_version = from_version
        while current_version < self._SCHEMA_VERSION:
            next_version = current_version + 1
            if next_version in migrations:
                migrations[next_version](conn)
                logger.info(f"🔄 Aplicada migración v{current_version} -> v{next_version}")
            else:
                # Migración genérica - recrear esquema completo
                self._recreate_schema(conn)
                break
            
            current_version = next_version
        
        # Actualizar versión del esquema
        conn.execute("UPDATE schema_info SET version = ?", (self._SCHEMA_VERSION,))
        conn.commit()

    def _migrate_v1_to_v2(self, conn: sqlite3.Connection):
        """Migración de v1 a v2 - Agregar sistema de rachas completo"""
        # Agregar columnas faltantes a user_stats
        new_columns = [
            ('longest_streak', 'INTEGER DEFAULT 0'),
            ('total_streak_days', 'INTEGER DEFAULT 0'),
            ('freeze_used_this_week', 'BOOLEAN DEFAULT FALSE'),
            ('recovery_used_this_month', 'BOOLEAN DEFAULT FALSE'),
            ('streak_protection_used', 'BOOLEAN DEFAULT FALSE')
        ]
        
        for column_name, column_type in new_columns:
            try:
                conn.execute(f'ALTER TABLE user_stats ADD COLUMN {column_name} {column_type}')
            except sqlite3.OperationalError as e:
                if "duplicate column name" not in str(e):
                    raise
        
        # Crear tablas nuevas si no existen
        new_tables = ['streak_milestones', 'daily_engagement']
        for table_name in new_tables:
            if not self._table_exists(conn, table_name):
                conn.execute(self.SCHEMA[table_name])
        
        # Crear índices nuevos
        for index_sql in self.INDEXES:
            if 'streak_milestones' in index_sql or 'daily_engagement' in index_sql:
                try:
                    conn.execute(index_sql)
                except sqlite3.OperationalError:
                    pass  # Índice ya existe

    def _migrate_v2_to_v3(self, conn: sqlite3.Connection):
        """Migración v2 a v3 - Agregar tabla user_preferences"""
        # Crear tabla de preferencias si no existe
        if not self._table_exists(conn, 'user_preferences'):
           conn.execute(self.SCHEMA['user_preferences'])
    
        # Crear índice
        conn.execute('CREATE INDEX IF NOT EXISTS idx_user_preferences_user ON user_preferences(user_id)')
    
        # Migrar datos existentes si es posible
        try:
            # Si hay user_stats, podemos inferir que el onboarding estaba completo
            if self._table_exists(conn, 'user_stats'):
                cursor = conn.execute("SELECT user_id FROM user_stats WHERE user_id = 'default_user'")
                if cursor.fetchone():
                    # Usuario existente - marcar onboarding como completo
                    conn.execute('''
                        INSERT OR REPLACE INTO user_preferences 
                        (user_id, onboarding_complete, currency, notifications_enabled, weekly_reports_enabled, theme)
                        VALUES ('default_user', TRUE, '€', TRUE, TRUE, 'Automático')
                    ''')
        except Exception as e:
            logger.warning(f"Error en migración v2->v3: {e}")

    def _migrate_v3_to_v4(self, conn: sqlite3.Connection):
        """Migración v3 a v4 - Agregar columna emotion a transactions"""
        # Agregar columna emotion si no existe
        try:
            cursor = conn.execute("PRAGMA table_info(transactions)")
            columns = [column[1] for column in cursor.fetchall()]
        
            if 'emotion' not in columns:
                # Agregar la columna emotion con valor por defecto
                conn.execute('ALTER TABLE transactions ADD COLUMN emotion TEXT NOT NULL DEFAULT "neutral"')
                logger.info("✅ Columna 'emotion' agregada a transactions")
            else:
                logger.info("✅ Columna 'emotion' ya existe en transactions")
            
        except Exception as e:
            logger.error(f"❌ Error en migración v3->v4: {e}")
            raise

    def _recreate_schema(self, conn: sqlite3.Connection):
        """Recrea el esquema completo (último recurso)"""
        # Backup de datos existentes
        self._backup_existing_data(conn)
        
        # Eliminar y recrear tablas
        tables = ['transactions', 'user_stats', 'user_categories', 'streak_milestones', 'daily_engagement']
        for table in tables:
            conn.execute(f'DROP TABLE IF EXISTS {table}')
        
        # Crear esquema nuevo
        self._create_full_schema(conn)
        
        # Restaurar datos si es posible
        self._restore_backup_data(conn)

    def _backup_existing_data(self, conn: sqlite3.Connection):
        """Backup de datos existentes antes de migración"""
        try:
            conn.execute("CREATE TABLE IF NOT EXISTS backup_transactions AS SELECT * FROM transactions")
            conn.execute("CREATE TABLE IF NOT EXISTS backup_user_stats AS SELECT * FROM user_stats")
        except Exception as e:
            logger.warning(f"No se pudo crear backup: {e}")

    def _restore_backup_data(self, conn: sqlite3.Connection):
        """Restaura datos desde backup después de migración"""
        try:
            # Restaurar transacciones si existen
            if self._table_exists(conn, 'backup_transactions'):
                conn.execute('''
                    INSERT INTO transactions (id, user_id, amount, type, category, description, created_at)
                    SELECT id, user_id, amount, type, category, description, created_at 
                    FROM backup_transactions
                ''')
                conn.execute('DROP TABLE backup_transactions')
            
            # Restaurar user_stats si existen
            if self._table_exists(conn, 'backup_user_stats'):
                conn.execute('''
                    INSERT INTO user_stats (user_id, current_streak, total_points, last_activity_date)
                    SELECT user_id, current_streak, total_points, last_activity_date 
                    FROM backup_user_stats
                ''')
                conn.execute('DROP TABLE backup_user_stats')
                
        except Exception as e:
            logger.warning(f"No se pudo restaurar backup: {e}")

    def _table_exists(self, conn: sqlite3.Connection, table_name: str) -> bool:
        """Verifica si una tabla existe"""
        try:
            conn.execute(f"SELECT 1 FROM {table_name} LIMIT 1")
            return True
        except sqlite3.OperationalError:
            return False

    def _insert_initial_data(self, conn: sqlite3.Connection):
        """Inserta datos iniciales en la base de datos"""
        # Usuario por defecto
        conn.execute('''
            INSERT OR IGNORE INTO user_stats 
            (user_id, current_streak, longest_streak, total_points, total_streak_days) 
            VALUES ('default_user', 0, 0, 0, 0)
        ''')
        
        # Categorías por defecto
        for category in self.DEFAULT_CATEGORIES:
            conn.execute('''
                INSERT OR IGNORE INTO user_categories (user_id, category_name, usage_count)
                VALUES ('default_user', ?, 1)
            ''', (category,))

    @contextmanager
    def get_connection(self) -> Generator[sqlite3.Connection, None, None]:
        """
        Context manager optimizado para conexiones a la base de datos
        con manejo de errores mejorado
        """
        conn = None
        try:
            conn = sqlite3.connect(self.db_path, timeout=30.0)
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA foreign_keys = ON")
        
            yield conn
            conn.commit()
        
        except sqlite3.Error as e:
            if conn:
                conn.rollback()
            print(f"❌ Error de base de datos: {e}")
            raise
        finally:
            if conn:
                conn.close()

    # 🔥 MÉTODOS CRÍTICOS - AHORA RETORNAN DICT EN LUGAR DE ROW
    def get_user_stats(self, user_id: str = "default_user") -> Optional[Dict]:
        """Obtiene stats del usuario - RETORNA DICT"""
        with self.get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM user_stats WHERE user_id = ?",
                (user_id,)
            )
            row = cursor.fetchone()
            return dict(row) if row else None

    def get_user_engagement_stats(self, user_id: str) -> Dict:
        """Obtiene estadísticas de engagement - RETORNA DICT"""
        with self.get_connection() as conn:
            # Total días activos
            cursor = conn.execute(
                "SELECT COUNT(DISTINCT activity_date) as total_days FROM daily_engagement WHERE user_id = ?",
                (user_id,)
            )
            result = cursor.fetchone()
            total_days = result['total_days'] if result else 0
            
            # Días activos últimos 30 días
            thirty_days_ago = (date.today() - timedelta(days=30)).isoformat()
            cursor = conn.execute(
                "SELECT COUNT(DISTINCT activity_date) as recent_days FROM daily_engagement WHERE user_id = ? AND activity_date >= ?",
                (user_id, thirty_days_ago)
            )
            result_recent = cursor.fetchone()
            recent_days = result_recent['recent_days'] if result_recent else 0   
            
            engagement_rate = (recent_days / 30 * 100) if recent_days > 0 else 0
            
            return {
                "total_active_days": total_days,
                "recent_active_days": recent_days,
                "engagement_rate": min(engagement_rate, 100)
            }

    def get_user_transactions(self, user_id: str = "default_user", limit: int = 100) -> List[Dict]:
        """Obtiene transacciones - RETORNA LIST[DICT]"""
        with self.get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM transactions WHERE user_id = ? ORDER BY created_at DESC LIMIT ?",
                (user_id, limit)
            )
            return [dict(row) for row in cursor.fetchall()]

    def get_category_totals(self, user_id: str = "default_user") -> List[Dict]:
        """Obtiene totales por categoría - RETORNA LIST[DICT]"""
        with self.get_connection() as conn:
            cursor = conn.execute('''
                SELECT category, SUM(amount) as total 
                FROM transactions 
                WHERE user_id = ? AND type = 'expense' 
                GROUP BY category 
                ORDER BY total DESC
            ''', (user_id,))
            return [dict(row) for row in cursor.fetchall()]

    def get_totals_by_type(self, user_id: str = "default_user") -> dict:
        """Obtiene totales optimizado con una sola consulta"""
        with self.get_connection() as conn:
            cursor = conn.execute('''
                SELECT 
                    COALESCE(SUM(CASE WHEN type = 'expense' THEN amount ELSE 0 END), 0) as total_expenses,
                    COALESCE(SUM(CASE WHEN type = 'income' THEN amount ELSE 0 END), 0) as total_income
                FROM transactions 
                WHERE user_id = ?
            ''', (user_id,))
            result = cursor.fetchone()
            return {
                'expense': result['total_expenses'],
                'income': result['total_income']
            }

    # 💾 MÉTODOS DE ESCRITURA
    def save_transaction(self, transaction_data: dict) -> bool:
        """Guarda transacción con validación"""
        with self.get_connection() as conn:
            # Validar datos requeridos
            required_fields = ['id', 'user_id', 'amount', 'type', 'category', 'emotion'] 
            for field in required_fields:
                if field not in transaction_data or not transaction_data[field]:
                    raise ValueError(f"Campo requerido faltante: {field}")
                
            created_at = transaction_data.get('created_at')
            if created_at is None:
                created_at = datetime.now().isoformat()
            elif isinstance(created_at, datetime):
                created_at = created_at.isoformat()
            
            # Insertar transacción
            conn.execute('''
                INSERT INTO transactions 
                (id, user_id, amount, type, category, emotion, description, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                transaction_data['id'],
                transaction_data['user_id'],
                transaction_data['amount'],
                transaction_data['type'],
                transaction_data['category'],
                transaction_data['emotion'],
                transaction_data.get('description', ''),
                created_at
            ))
            
            # Actualizar contador de categoría
            conn.execute('''
                INSERT INTO user_categories (user_id, category_name, usage_count)
                VALUES (?, ?, 1)
                ON CONFLICT(user_id, category_name) 
                DO UPDATE SET usage_count = usage_count + 1
            ''', (transaction_data['user_id'], transaction_data['category']))
            
            return True

    def update_user_stats(self, stats_data: dict) -> bool:
        """Actualiza stats del usuario con validación"""
        with self.get_connection() as conn:
            required_fields = ['user_id', 'current_streak', 'longest_streak', 'total_points']
            for field in required_fields:
                if field not in stats_data:
                    raise ValueError(f"Campo requerido faltante: {field}")
                
            last_activity_date = stats_data.get('last_activity_date')
            if last_activity_date is None:
                last_activity_date = None  # Mantener como None
            elif isinstance(last_activity_date, datetime):
                last_activity_date = last_activity_date.isoformat()
            
            conn.execute('''
                UPDATE user_stats 
                SET current_streak = ?, longest_streak = ?, total_points = ?, 
                    total_streak_days = ?, last_activity_date = ?, 
                    freeze_used_this_week = ?, recovery_used_this_month = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE user_id = ?
            ''', (
                stats_data['current_streak'],
                stats_data['longest_streak'],
                stats_data['total_points'],
                stats_data.get('total_streak_days', 0),
                last_activity_date,
                stats_data.get('freeze_used_this_week', False),
                stats_data.get('recovery_used_this_month', False),
                stats_data['user_id']
            ))
            return True

    def record_daily_engagement(self, user_id: str, action_type: str) -> bool:
        """Registra engagement del usuario"""
        today = date.today().isoformat()
        with self.get_connection() as conn:
            conn.execute('''
                INSERT INTO daily_engagement (user_id, activity_date, actions_types)
                VALUES (?, ?, ?)
                ON CONFLICT(user_id, activity_date) 
                DO UPDATE SET 
                    actions_count = actions_count + 1,
                    actions_types = actions_types || ',' || excluded.actions_types
            ''', (user_id, today, action_type))
            return True

    def get_user_categories(self, user_id: str = "default_user") -> List[str]:
        """Obtiene las categorías del usuario"""
        with self.get_connection() as conn:
            cursor = conn.execute(
                "SELECT category_name FROM user_categories WHERE user_id = ? ORDER BY usage_count DESC",
                (user_id,)
            )
            return [row['category_name'] for row in cursor.fetchall()]

    def get_transactions_by_date_range(self, user_id: str, start_date: str, end_date: str) -> List[Dict]:
        """Obtiene transacciones dentro de un rango de fechas"""
        with self.get_connection() as conn:
            cursor = conn.execute('''
                SELECT * FROM transactions 
                WHERE user_id = ? AND date(created_at) BETWEEN ? AND ?
                ORDER BY created_at DESC
            ''', (user_id, start_date, end_date))
            return [dict(row) for row in cursor.fetchall()]

    def add_streak_milestone(self, user_id: str, milestone_days: int) -> bool:
        """Registra un hito de racha alcanzado"""
        with self.get_connection() as conn:
            conn.execute('''
                INSERT OR REPLACE INTO streak_milestones 
                (user_id, milestone_days, achieved_at, reward_claimed)
                VALUES (?, ?, CURRENT_TIMESTAMP, TRUE)
            ''', (user_id, milestone_days))
            return True

    # 📊 MÉTODOS ADICIONALES
    def get_weekly_comparison(self, user_id: str, weeks: int = 4) -> Dict:
        """Obtiene comparativa semanal de gastos"""
        comparisons = []
        today = date.today()
        
        for i in range(weeks):
            week_end = today - timedelta(weeks=i)
            week_start = week_end - timedelta(days=6)
            
            transactions = self.get_transactions_by_date_range(
                user_id, week_start.isoformat(), week_end.isoformat()
            )
            
            week_expenses = sum(row['amount'] for row in transactions if row['type'] == 'expense')
            week_income = sum(row['amount'] for row in transactions if row['type'] == 'income')
            
            comparisons.append({
                "week_label": f"Semana {weeks - i}",
                "period": f"{week_start.strftime('%d/%m')} - {week_end.strftime('%d/%m')}",
                "expenses": week_expenses,
                "income": week_income,
                "balance": week_income - week_expenses
            })
        
        return {
            "comparisons": comparisons,
            "average_expenses": sum(c['expenses'] for c in comparisons) / len(comparisons) if comparisons else 0,
            "average_income": sum(c['income'] for c in comparisons) / len(comparisons) if comparisons else 0
        }

    def get_streak_milestones(self, user_id: str) -> List[Dict]:
        """Obtiene hitos de racha alcanzados"""
        with self.get_connection() as conn:
            cursor = conn.execute(
                "SELECT milestone_days, achieved_at FROM streak_milestones WHERE user_id = ? ORDER BY milestone_days",
                (user_id,)
            )
            return [dict(row) for row in cursor.fetchall()]

    # 🛠️ MÉTODOS DE MANTENIMIENTO
    def vacuum_database(self):
        """Optimiza y limpia la base de datos"""
        with self.get_connection() as conn:
            conn.execute("VACUUM")
            logger.info("✅ Base de datos optimizada")

    def get_database_stats(self) -> Dict[str, Any]:
        """Estadísticas de la base de datos"""
        with self.get_connection() as conn:
            stats = {}
            
            # Tamaño de tablas
            cursor = conn.execute('''
                SELECT name, (pgsize/1024.0/1024.0) as size_mb
                FROM dbstat 
                WHERE aggregate = TRUE
            ''')
            stats['table_sizes'] = {row['name']: row['size_mb'] for row in cursor.fetchall()}
            
            # Conteo de registros
            tables = ['transactions', 'user_stats', 'user_categories', 'streak_milestones', 'daily_engagement']
            for table in tables:
                cursor = conn.execute(f'SELECT COUNT(*) as count FROM {table}')
                stats[f'{table}_count'] = cursor.fetchone()['count']
            
            return stats

# Instancia global con manejo de errores
try:
    db = Database()
    logger.info("✅ Base de datos inicializada correctamente")
except Exception as e:
    logger.critical(f"❌ Error crítico inicializando base de datos: {e}")
    # Fallback - recrear base de datos
    import shutil
    if os.path.exists("data/ahorify.db"):
        shutil.move("data/ahorify.db", f"data/ahorify.db.error_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    db = Database()  # Reintentar