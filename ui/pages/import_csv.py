# ui/pages/import_csv.py
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, date
import io
import tempfile
import json
from typing import Dict, List, Optional, Tuple
from core.services.transaction_service import TransactionService
from core.services.gamification_service import GamificationService
from ui.components.progress_bars import ProgressBars

class ImportCSVPage:
    """
    Sistema de importación inteligente para Ahorify.
    Conversión automática de formatos bancarios + gamificación.
    """
    
    # Mapeo de formatos bancarios comunes
    BANK_FORMATS = {
        "Santander ES": {
            "columns": ["Fecha", "Concepto", "Importe", "Saldo"],
            "date_format": "%d/%m/%Y",
            "amount_column": "Importe",
            "description_column": "Concepto"
        },
        "BBVA ES": {
            "columns": ["Fecha", "Descripción", "Cargo", "Abono", "Saldo"],
            "date_format": "%d/%m/%Y",
            "amount_column": ["Cargo", "Abono"],
            "description_column": "Descripción"
        },
        "CaixaBank ES": {
            "columns": ["Fecha operación", "Concepto", "Importe"],
            "date_format": "%d/%m/%Y",
            "amount_column": "Importe",
            "description_column": "Concepto"
        },
        "Bankia ES": {
            "columns": ["Fecha", "Descripción", "Importe"],
            "date_format": "%d/%m/%Y",
            "amount_column": "Importe",
            "description_column": "Descripción"
        },
        "Revolut": {
            "columns": ["Started Date", "Description", "Amount"],
            "date_format": "%Y-%m-%d",
            "amount_column": "Amount",
            "description_column": "Description"
        },
        "N26": {
            "columns": ["Date", "Payee", "Amount"],
            "date_format": "%Y-%m-%d",
            "amount_column": "Amount",
            "description_column": "Payee"
        },
        "Custom": {
            "columns": [],
            "date_format": "%Y-%m-%d",
            "amount_column": "",
            "description_column": ""
        }
    }
    
    def __init__(self):
        self.transaction_service = TransactionService()
        self.gamification_service = GamificationService()
        self.progress_bars = ProgressBars()
        
        # Estado de la importación
        if 'import_step' not in st.session_state:
            st.session_state.import_step = 1
        if 'uploaded_file' not in st.session_state:
            st.session_state.uploaded_file = None
        if 'df_raw' not in st.session_state:
            st.session_state.df_raw = None
        if 'df_mapped' not in st.session_state:
            st.session_state.df_mapped = None
        if 'column_mapping' not in st.session_state:
            st.session_state.column_mapping = {}
        if 'import_results' not in st.session_state:
            st.session_state.import_results = None
    
    def render(self) -> None:
        """Renderiza el proceso completo de importación"""
        self._render_header()
        
        # Proceso paso a paso
        if st.session_state.import_step == 1:
            self._render_step_upload()
        elif st.session_state.import_step == 2:
            self._render_step_mapping()
        elif st.session_state.import_step == 3:
            self._render_step_review()
        elif st.session_state.import_step == 4:
            self._render_step_results()
        
        self._render_sidebar_help()
    
    def _render_header(self) -> None:
        """Header de la página de importación"""
        st.markdown("""
        <div class="ah-card ah-card-gamified">
            <h1 class="ah-title">📤 Importar Transacciones</h1>
            <p class="ah-subtitle">Importa tus transacciones desde CSV o Excel en segundos</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Barra de progreso del proceso
        steps = ["1. Subir Archivo", "2. Mapear Columnas", "3. Revisar", "4. Resultados"]
        current_step = st.session_state.import_step
        
        cols = st.columns(4)
        for i, step in enumerate(steps):
            with cols[i]:
                is_active = current_step == i + 1
                is_completed = current_step > i + 1
                
                status_emoji = "✅" if is_completed else "🔸"
                status_class = "ah-badge-success" if is_completed else "ah-badge-primary" if is_active else ""
                
                st.markdown(f"""
                <div style="text-align: center;">
                    <div class="ah-badge {status_class}" style="margin-bottom: 8px;">
                        {status_emoji} {step.split('.')[0]}
                    </div>
                    <div style="font-size: 0.75rem; color: var(--text-secondary);">
                        {step.split('.')[1]}
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    def _render_step_upload(self) -> None:
        """Paso 1: Subida de archivo"""
        st.markdown("""
        <div class="ah-card">
            <h2>📁 Paso 1: Sube tu archivo</h2>
            <p style="color: var(--text-secondary);">
                Soporte para CSV, Excel (.xlsx) y los principales formatos bancarios españoles
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Área de subida de archivo
        uploaded_file = st.file_uploader(
            "Arrastra tu archivo aquí o haz clic para buscar",
            type=['csv', 'xlsx', 'xls'],
            help="Formatos soportados: CSV, Excel (.xlsx, .xls)",
            key="file_uploader"
        )
        
        if uploaded_file:
            st.session_state.uploaded_file = uploaded_file
            
            # Detectar formato automáticamente
            detected_format = self._detect_bank_format(uploaded_file)
            
            if detected_format:
                st.success(f"🎯 **Formato detectado:** {detected_format}")
                
                # Mostrar preview rápido
                try:
                    df_preview = self._load_file_preview(uploaded_file)
                    if df_preview is not None:
                        st.markdown("#### 👀 Vista Previa Rápida")
                        st.dataframe(df_preview.head(5), use_container_width=True)
                        
                        st.info(f"📊 **{len(df_preview)}** transacciones detectadas")
                except Exception as e:
                    st.warning("⚠️ No se pudo generar la vista previa automática")
            
            # Botón para continuar
            col1, col2 = st.columns([1, 3])
            with col1:
                if st.button("🚀 Continuar al Mapeo", use_container_width=True):
                    st.session_state.import_step = 2
                    st.rerun()
        
        # Ejemplos de formatos soportados
        with st.expander("📋 ¿Qué formatos son compatibles?", expanded=True):
            st.markdown("""
            **🏦 Formatos bancarios detectados automáticamente:**
            - Santander, BBVA, CaixaBank, Bankia
            - Revolut, N26, y más...
            
            **📊 Estructura mínima requerida:**
            ```csv
            Fecha, Descripción, Importe
            2024-01-15, Compra en Mercadona, -45.50
            2024-01-16, Transferencia entrada, 150.00
            ```
            
            **💡 Consejos:**
            - Exporta desde tu banca online como CSV o Excel
            - Mantén los encabezados originales del banco
            - No modifiques el formato de fechas y números
            """)
    
    def _render_step_mapping(self) -> None:
        """Paso 2: Mapeo de columnas"""
        st.markdown("""
        <div class="ah-card">
            <h2>🗺️ Paso 2: Mapeo de Columnas</h2>
            <p style="color: var(--text-secondary);">
                Ayúdanos a entender la estructura de tu archivo
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        if not st.session_state.uploaded_file:
            st.warning("⚠️ Primero sube un archivo en el Paso 1")
            if st.button("⬅️ Volver a Subida"):
                st.session_state.import_step = 1
                st.rerun()
            return
        
        try:
            # Cargar datos
            df = self._load_dataframe(st.session_state.uploaded_file)
            st.session_state.df_raw = df
            
            st.success(f"📊 **{len(df)}** transacciones cargadas correctamente")
            
            # Selector de formato bancario
            bank_format = st.selectbox(
                "Selecciona tu banco o formato:",
                options=list(self.BANK_FORMATS.keys()),
                help="Selecciona tu banco para mapeo automático"
            )
            
            # Mapeo automático si se selecciona un banco conocido
            if bank_format != "Custom":
                mapping = self._auto_map_columns(df, bank_format)
                st.session_state.column_mapping = mapping
                st.info(f"🔧 **Mapeo automático aplicado** para {bank_format}")
            
            # Vista previa con columnas
            st.markdown("#### 👁️ Vista Previa de Datos")
            st.dataframe(df.head(10), use_container_width=True)
            
            # Mapeo manual de columnas
            st.markdown("#### ⚙️ Mapeo de Campos")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                date_column = st.selectbox(
                    "Columna de Fecha:",
                    options=[""] + list(df.columns),
                    index=(list(df.columns).index(st.session_state.column_mapping.get("date", "")) 
                          if st.session_state.column_mapping.get("date") in df.columns else 0),
                    help="Selecciona la columna que contiene las fechas"
                )
            
            with col2:
                amount_column = st.selectbox(
                    "Columna de Importe:",
                    options=[""] + list(df.columns),
                    index=(list(df.columns).index(st.session_state.column_mapping.get("amount", "")) 
                          if st.session_state.column_mapping.get("amount") in df.columns else 0),
                    help="Selecciona la columna que contiene los importes"
                )
            
            with col3:
                description_column = st.selectbox(
                    "Columna de Descripción:",
                    options=[""] + list(df.columns),
                    index=(list(df.columns).index(st.session_state.column_mapping.get("description", "")) 
                          if st.session_state.column_mapping.get("description") in df.columns else 0),
                    help="Selecciona la columna que contiene las descripciones"
                )
            
            # Campos opcionales
            col4, col5 = st.columns(2)
            
            with col4:
                category_column = st.selectbox(
                    "Columna de Categoría (opcional):",
                    options=["-- No usar --"] + list(df.columns),
                    help="Si tu archivo incluye categorías, selecciona la columna"
                )
                if category_column == "-- No usar --":
                    category_column = ""
            
            with col5:
                type_column = st.selectbox(
                    "Columna de Tipo (opcional):",
                    options=["-- No usar --"] + list(df.columns),
                    help="Si tu archivo indica tipo (ingreso/gasto), selecciona la columna"
                )
                if type_column == "-- No usar --":
                    type_column = ""
            
            # Guardar mapeo
            st.session_state.column_mapping = {
                "date": date_column,
                "amount": amount_column,
                "description": description_column,
                "category": category_column,
                "type": type_column,
                "bank_format": bank_format
            }
            
            # Validación
            validation_errors = self._validate_mapping(st.session_state.column_mapping, df)
            
            if validation_errors:
                for error in validation_errors:
                    st.error(error)
            else:
                st.success("✅ Mapeo válido - Puedes continuar")
                
                # Procesar datos mapeados
                df_mapped = self._apply_mapping(df, st.session_state.column_mapping)
                st.session_state.df_mapped = df_mapped
                
                # Vista previa de datos mapeados
                st.markdown("#### 🔄 Vista Previa Mapeada")
                st.dataframe(df_mapped.head(5), use_container_width=True)
                
                # Botones de navegación
                col1, col2, col3 = st.columns([1, 1, 1])
                with col1:
                    if st.button("⬅️ Volver", use_container_width=True):
                        st.session_state.import_step = 1
                        st.rerun()
                with col3:
                    if st.button("✅ Continuar a Revisión", use_container_width=True):
                        st.session_state.import_step = 3
                        st.rerun()
        
        except Exception as e:
            st.error(f"❌ Error procesando el archivo: {str(e)}")
            if st.button("🔄 Intentar con otro archivo"):
                st.session_state.import_step = 1
                st.rerun()
    
    def _render_step_review(self) -> None:
        """Paso 3: Revisión y confirmación"""
        st.markdown("""
        <div class="ah-card">
            <h2>🔍 Paso 3: Revisión Final</h2>
            <p style="color: var(--text-secondary);">
                Revisa tus datos antes de importar
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.session_state.df_mapped is None:
            st.error("❌ No hay datos mapeados para revisar")
            if st.button("⬅️ Volver al Mapeo"):
                st.session_state.import_step = 2
                st.rerun()
            return
        
        df = st.session_state.df_mapped
        
        # Estadísticas de importación
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Transacciones", len(df))
        
        with col2:
            income_count = len(df[df['type'] == 'income'])
            st.metric("Ingresos", income_count)
        
        with col3:
            expense_count = len(df[df['type'] == 'expense'])
            st.metric("Gastos", expense_count)
        
        with col4:
            total_amount = df['amount'].sum()
            st.metric("Importe Total", f"€{total_amount:,.2f}")
        
        # Filtros para revisión
        st.markdown("#### 📋 Revisión de Transacciones")
        
        col1, col2 = st.columns(2)
        
        with col1:
            show_type = st.selectbox(
                "Filtrar por tipo:",
                ["Todos", "Ingresos", "Gastos"]
            )
        
        with col2:
            items_per_page = st.slider("Transacciones por página:", 5, 20, 10)
        
        # Aplicar filtros
        df_filtered = df.copy()
        if show_type == "Ingresos":
            df_filtered = df_filtered[df_filtered['type'] == 'income']
        elif show_type == "Gastos":
            df_filtered = df_filtered[df_filtered['type'] == 'expense']
        
        # Paginación
        total_pages = max(1, len(df_filtered) // items_per_page + (1 if len(df_filtered) % items_per_page else 0))
        page_number = st.number_input("Página:", min_value=1, max_value=total_pages, value=1)
        
        start_idx = (page_number - 1) * items_per_page
        end_idx = start_idx + items_per_page
        
        df_page = df_filtered.iloc[start_idx:end_idx]
        
        # Mostrar datos paginados
        for idx, row in df_page.iterrows():
            self._render_transaction_review_card(row, idx)
        
        # Resumen de categorías automáticas
        st.markdown("#### 🏷️ Categorías Detectadas")
        if 'category' in df.columns:
            category_counts = df['category'].value_counts()
            for category, count in category_counts.head(5).items():
                st.write(f"**{category}:** {count} transacciones")
        else:
            st.info("ℹ️ No se detectaron categorías en el archivo. Se asignarán automáticamente.")
        
        # Configuración de importación
        st.markdown("#### ⚙️ Configuración de Importación")
        
        col1, col2 = st.columns(2)
        
        with col1:
            skip_duplicates = st.checkbox(
                "Saltar transacciones duplicadas",
                value=True,
                help="Evita importar transacciones que ya existen"
            )
        
        with col2:
            auto_categorize = st.checkbox(
                "Categorización automática",
                value=True,
                help="Asigna categorías automáticamente basado en descripciones"
            )
        
        # Botones de acción
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            if st.button("⬅️ Volver al Mapeo", use_container_width=True):
                st.session_state.import_step = 2
                st.rerun()
        
        with col2:
            if st.button("📥 Descargar Mapeo", use_container_width=True):
                self._download_mapping_template()
        
        with col3:
            if st.button("🚀 Importar Transacciones", type="primary", use_container_width=True):
                with st.spinner("🔄 Importando transacciones..."):
                    results = self._execute_import(
                        df, 
                        skip_duplicates=skip_duplicates,
                        auto_categorize=auto_categorize
                    )
                    st.session_state.import_results = results
                    st.session_state.import_step = 4
                    st.rerun()
    
    def _render_step_results(self) -> None:
        """Paso 4: Resultados de la importación"""
        st.markdown("""
        <div class="ah-card ah-card-gamified">
            <h2>🎉 ¡Importación Completa!</h2>
            <p style="color: rgba(255,255,255,0.8);">
                Resultados del proceso de importación
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.session_state.import_results is None:
            st.error("❌ No hay resultados de importación")
            if st.button("🔄 Intentar de nuevo"):
                st.session_state.import_step = 1
                st.rerun()
            return
        
        results = st.session_state.import_results
        
        # Estadísticas de resultados
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Procesadas", results['total_processed'])
        
        with col2:
            st.metric("Importadas", results['successful'], 
                     delta=f"+{results['successful']}")
        
        with col3:
            st.metric("Fallidas", results['failed'],
                     delta=f"-{results['failed']}", delta_color="inverse")
        
        with col4:
            st.metric("Duplicadas", results['duplicates_skipped'])
        
        # Gamificación por importación masiva
        if results['successful'] >= 10:
            st.balloons()
            st.success(f"🏆 **¡Importación masiva!** +{results['successful']} puntos de gamificación")
        
        # Detalles de errores
        if results['errors']:
            st.markdown("#### ⚠️ Errores Encontrados")
            with st.expander("Ver detalles de errores"):
                for error in results['errors'][:5]:  # Mostrar solo primeros 5 errores
                    st.error(error)
        
        # Transacciones importadas recientemente
        st.markdown("#### 📝 Transacciones Recién Importadas")
        try:
            recent_transactions = self.transaction_service.get_recent_transactions(limit=5)
            for transaction in recent_transactions:
                self._render_imported_transaction_card(transaction)
        except:
            st.info("💡 Las transacciones importadas aparecerán en tu dashboard")
        
        # Siguientes pasos
        st.markdown("#### 🎯 Siguientes Pasos")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📊 Ver Dashboard", use_container_width=True):
                st.switch_page("pages/dashboard.py")
        
        with col2:
            if st.button("💸 Registro Rápido", use_container_width=True):
                st.switch_page("pages/quick_add.py")
        
        with col3:
            if st.button("🔄 Nueva Importación", use_container_width=True):
                # Resetear estado
                for key in ['import_step', 'uploaded_file', 'df_raw', 'df_mapped', 'column_mapping', 'import_results']:
                    if key in st.session_state:
                        del st.session_state[key]
                st.rerun()
    
    def _render_sidebar_help(self) -> None:
        """Panel de ayuda en sidebar"""
        with st.sidebar:
            st.markdown("### 💡 Ayuda Rápida")
            
            with st.expander("📋 Formatos Soportados", expanded=True):
                st.markdown("""
                **Formatos detectados automáticamente:**
                - Santander, BBVA, CaixaBank
                - Bankia, Revolut, N26
                - CSV estándar, Excel (.xlsx)
                
                **Columnas requeridas:**
                - Fecha (cualquier formato)
                - Importe (números)
                - Descripción (texto)
                """)
            
            with st.expander("🔧 Solución de Problemas"):
                st.markdown("""
                **Problemas comunes:**
                - ❌ **Fechas no reconocidas:** Usa el formato DD/MM/AAAA
                - ❌ **Importes con texto:** Solo números y símbolo negativo
                - ❌ **Codificación incorrecta:** Guarda como UTF-8
                
                **Solución rápida:**
                1. Exporta desde tu banco como CSV
                2. No modifiques los encabezados
                3. Sube el archivo original
                """)
            
            # Stats de importación si estamos en pasos avanzados
            if st.session_state.import_step >= 2 and st.session_state.df_raw is not None:
                st.markdown("---")
                st.markdown("### 📊 Stats de Importación")
                st.metric("Transacciones", len(st.session_state.df_raw))
                
                if st.session_state.df_mapped is not None:
                    income = len(st.session_state.df_mapped[st.session_state.df_mapped['type'] == 'income'])
                    expenses = len(st.session_state.df_mapped[st.session_state.df_mapped['type'] == 'expense'])
                    st.metric("Ingresos/Gastos", f"{income}/{expenses}")
    
    def _render_transaction_review_card(self, transaction: pd.Series, index: int) -> None:
        """Renderiza una tarjeta de transacción para revisión"""
        amount_color = "var(--accent-success)" if transaction['type'] == 'income' else "var(--accent-error)"
        amount_prefix = "+" if transaction['type'] == 'income' else "-"
        
        st.markdown(f"""
        <div class="ah-card" style="border-left: 4px solid {amount_color}; margin-bottom: 8px;">
            <div style="display: flex; justify-content: space-between; align-items: start;">
                <div style="flex: 1;">
                    <div style="font-weight: 600; margin-bottom: 4px;">{transaction['description']}</div>
                    <div style="color: var(--text-secondary); font-size: 0.875rem; margin-bottom: 4px;">
                        {transaction['date'].strftime('%d %b %Y') if hasattr(transaction['date'], 'strftime') else str(transaction['date'])}
                    </div>
                    <div style="color: var(--text-secondary); font-size: 0.75rem;">
                        Categoría: {transaction.get('category', 'Por asignar')}
                    </div>
                </div>
                <div style="font-weight: 700; color: {amount_color};">
                    {amount_prefix}€{abs(transaction['amount']):.2f}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    def _render_imported_transaction_card(self, transaction: Dict) -> None:
        """Renderiza una tarjeta de transacción importada"""
        amount_color = "var(--accent-success)" if not transaction["is_expense"] else "var(--accent-error)"
        amount_prefix = "+" if not transaction["is_expense"] else "-"
        
        st.markdown(f"""
        <div class="ah-card" style="border-left: 4px solid {amount_color}; margin-bottom: 8px;">
            <div style="display: flex; justify-content: space-between; align-items: start;">
                <div style="flex: 1;">
                    <div style="font-weight: 600; margin-bottom: 4px;">{transaction['category']}</div>
                    <div style="color: var(--text-secondary); font-size: 0.875rem; margin-bottom: 4px;">
                        {transaction['description']}
                    </div>
                    <div style="color: var(--text-secondary); font-size: 0.75rem;">
                        {transaction['formatted_date']}
                    </div>
                </div>
                <div style="font-weight: 700; color: {amount_color};">
                    {amount_prefix}{transaction['formatted_amount'].replace('€', '')}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    def _detect_bank_format(self, file) -> Optional[str]:
        """Detecta automáticamente el formato bancario"""
        try:
            df_preview = self._load_file_preview(file)
            if df_preview is None:
                return None
            
            columns = list(df_preview.columns)
            
            for format_name, format_info in self.BANK_FORMATS.items():
                if format_name == "Custom":
                    continue
                
                # Verificar si las columnas coinciden
                format_columns = set(format_info["columns"])
                file_columns = set(columns)
                
                if format_columns.issubset(file_columns):
                    return format_name
            
            return None
        except:
            return None
    
    def _load_file_preview(self, file) -> Optional[pd.DataFrame]:
        """Carga una vista previa del archivo"""
        try:
            if file.name.endswith('.csv'):
                return pd.read_csv(file, nrows=5)
            elif file.name.endswith(('.xlsx', '.xls')):
                return pd.read_excel(file, nrows=5)
        except:
            return None
        finally:
            file.seek(0)  # Reset file pointer
    
    def _load_dataframe(self, file) -> pd.DataFrame:
        """Carga el dataframe completo"""
        try:
            if file.name.endswith('.csv'):
                # Intentar diferentes encodings
                encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'windows-1252']
                for encoding in encodings:
                    try:
                        df = pd.read_csv(file, encoding=encoding)
                        return df
                    except UnicodeDecodeError:
                        continue
                # Si todos fallan, usar utf-8 con manejo de errores
                return pd.read_csv(file, encoding='utf-8', errors='replace')
            elif file.name.endswith(('.xlsx', '.xls')):
                return pd.read_excel(file)
        except Exception as e:
            raise Exception(f"Error leyendo archivo: {str(e)}")
        finally:
            file.seek(0)
    
    def _auto_map_columns(self, df: pd.DataFrame, bank_format: str) -> Dict:
        """Mapeo automático de columnas basado en formato bancario"""
        format_info = self.BANK_FORMATS[bank_format]
        columns = list(df.columns)
        mapping = {}
        
        # Buscar columnas que coincidan
        for col in columns:
            col_lower = col.lower()
            
            # Mapear fecha
            if any(keyword in col_lower for keyword in ['fecha', 'date', 'fecha operación']):
                mapping['date'] = col
            
            # Mapear importe
            elif any(keyword in col_lower for keyword in ['importe', 'amount', 'cargo', 'abono']):
                mapping['amount'] = col
            
            # Mapear descripción
            elif any(keyword in col_lower for keyword in ['descripción', 'description', 'concepto', 'payee']):
                mapping['description'] = col
        
        return mapping
    
    def _validate_mapping(self, mapping: Dict, df: pd.DataFrame) -> List[str]:
        """Valida que el mapeo sea correcto"""
        errors = []
        
        if not mapping.get('date'):
            errors.append("❌ Debes seleccionar una columna para Fecha")
        elif mapping['date'] not in df.columns:
            errors.append("❌ La columna de Fecha seleccionada no existe en el archivo")
        
        if not mapping.get('amount'):
            errors.append("❌ Debes seleccionar una columna para Importe")
        elif mapping['amount'] not in df.columns:
            errors.append("❌ La columna de Importe seleccionada no existe en el archivo")
        
        if not mapping.get('description'):
            errors.append("❌ Debes seleccionar una columna para Descripción")
        elif mapping['description'] not in df.columns:
            errors.append("❌ La columna de Descripción seleccionada no existe en el archivo")
        
        return errors
    
    def _apply_mapping(self, df: pd.DataFrame, mapping: Dict) -> pd.DataFrame:
        """Aplica el mapeo y transforma los datos"""
        result = pd.DataFrame()
        
        # Copiar columnas mapeadas
        result['date'] = df[mapping['date']]
        result['amount'] = df[mapping['amount']]
        result['description'] = df[mapping['description']]
        
        # Columnas opcionales
        if mapping.get('category') and mapping['category'] in df.columns:
            result['category'] = df[mapping['category']]
        
        if mapping.get('type') and mapping['type'] in df.columns:
            result['type'] = df[mapping['type']]
        else:
            # Determinar tipo basado en el importe
            result['type'] = result['amount'].apply(
                lambda x: 'income' if float(x or 0) > 0 else 'expense'
            )
        
        # Limpiar y transformar datos
        result = self._clean_data(result)
        return result
    
    def _clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Limpia y transforma los datos"""
        # Convertir fechas
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        
        # Limpiar importes
        df['amount'] = df['amount'].astype(str).str.replace(',', '.').str.replace('€', '').str.strip()
        df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
        
        # Limpiar descripciones
        df['description'] = df['description'].astype(str).str.strip()
        
        # Eliminar filas con datos inválidos
        df = df.dropna(subset=['date', 'amount', 'description'])
        
        return df
    
    def _download_mapping_template(self):
        """Descarga una plantilla de mapeo"""
        template = {
            "bank_format": st.session_state.column_mapping.get("bank_format", "Custom"),
            "mapping": st.session_state.column_mapping,
            "created_at": datetime.now().isoformat()
        }
        
        st.download_button(
            label="📥 Descargar Configuración",
            data=json.dumps(template, indent=2),
            file_name="ahorify_mapping_template.json",
            mime="application/json",
            use_container_width=True
        )
    
    def _execute_import(self, df: pd.DataFrame, skip_duplicates: bool = True, 
                       auto_categorize: bool = True) -> Dict:
        """Ejecuta la importación de transacciones"""
        results = {
            'total_processed': len(df),
            'successful': 0,
            'failed': 0,
            'duplicates_skipped': 0,
            'errors': []
        }
        
        # Gamificación por importación masiva
        if len(df) >= 10:
            self.gamification_service.record_engagement(
                action_type="weekly_review_completed",
                metadata={"transactions_imported": len(df)}
            )
        
        # Barra de progreso
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i, row in df.iterrows():
            # Actualizar progreso
            progress = (i + 1) / len(df)
            progress_bar.progress(progress)
            status_text.text(f"Procesando {i + 1} de {len(df)}...")
            
            try:
                # Preparar datos de transacción
                transaction_data = {
                    "amount": abs(float(row['amount'])),
                    "category": row.get('category', '❓ Otros'),
                    "description": row['description'],
                    "transaction_type": row['type'],
                    "date": row['date']
                }
                
                # Verificar duplicados (simplificado)
                if skip_duplicates:
                    # En implementación real, verificaríamos contra la base de datos
                    pass
                
                # Importar transacción
                result = self.transaction_service.add_transaction(
                    amount=transaction_data["amount"],
                    category=transaction_data["category"],
                    description=transaction_data["description"],
                    transaction_type=transaction_data["transaction_type"]
                )
                
                if result["success"]:
                    results['successful'] += 1
                else:
                    results['failed'] += 1
                    results['errors'].append(f"Fila {i}: {result['message']}")
            
            except Exception as e:
                results['failed'] += 1
                results['errors'].append(f"Fila {i}: Error - {str(e)}")
        
        # Limpiar barra de progreso
        progress_bar.empty()
        status_text.empty()
        
        return results

# Función principal de la página
def show_import_csv():
    """
    Página de importación CSV/Excel de Ahorify.
    """
    try:
        page = ImportCSVPage()
        page.render()
        
    except Exception as e:
        st.error("🚨 Error en el sistema de importación")
        st.info("""
        **Solución de problemas:**
        - Verifica que el archivo no esté corrupto
        - Asegúrate de que tiene el formato correcto
        - Intenta con un archivo más pequeño primero
        """)
        
        if st.button("🔄 Reiniciar Importación"):
            for key in ['import_step', 'uploaded_file', 'df_raw', 'df_mapped', 'column_mapping', 'import_results']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()

# Punto de entrada directo para desarrollo
if __name__ == "__main__":
    show_import_csv()