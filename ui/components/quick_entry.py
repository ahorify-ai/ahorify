# ui/components/quick_entry.py - SOLO MODIFICAR EL MÉTODO _handle_submission
import streamlit as st
from core.services.transaction_service import transaction_service
from core.models import TransactionType

class QuickEntryForm:
    """
    Formulario de entrada rápida - VERSIÓN CORREGIDA PARA INGRESOS
    """
    
    def __init__(self):
        self.transaction_service = transaction_service
    
    def render(self):
        """Renderiza el formulario SIN reset agresivo"""
        st.subheader("💸 Registro Rápido")
        
        with st.form("quick_entry_form", clear_on_submit=True):
            # FILA 1: Monto y Tipo
            col1, col2 = st.columns(2)
            
            with col1:
                amount = st.number_input(
                    "💰 Monto (€)", 
                    min_value=0.01, 
                    step=0.01,
                    value=0.01,
                    format="%.2f",
                    help="Ingresa el monto de la transacción"
                )
                
            with col2:
                transaction_type = st.selectbox(
                    "📊 Tipo",
                    options=[TransactionType.EXPENSE, TransactionType.INCOME],
                    format_func=lambda x: "💸 Gasto" if x == TransactionType.EXPENSE else "💰 Ingreso"
                )

            # FILA 2: CATEGORÍA Y EMOCIÓN
            col3, col4 = st.columns(2)
            
            with col3:
                categories = self.transaction_service.get_suggested_categories()
                category = st.selectbox(
                    "📂 Categoría",
                    options=categories,
                    help="Selecciona una categoría"
                )
            
            with col4:
                emotion = st.selectbox(
                    "🎭 Emoción",
                    options=["neutral", "happy", "impulsive", "stress", "investment"],
                    format_func=lambda x: {
                        "neutral": "😐 Neutral",
                        "happy": "😊 Feliz", 
                        "impulsive": "⚡ Impulsivo",
                        "stress": "😥 Estrés",
                        "investment": "📈 Inversión"
                    }[x]
                )
        
            # FILA 3: Descripción
            description = st.text_input(
                "📝 Descripción (opcional)",
                placeholder="Ej: Cena en restaurante, Salario mensual..."
            )
            
            # Botón de envío
            submitted = st.form_submit_button(
                "💾 Guardar Transacción",
                use_container_width=True,
                type="primary"
            )
            
            if submitted:
                self._handle_submission(amount, transaction_type, category, emotion, description)

    def _handle_submission(self, amount, transaction_type, category, emotion, description):
        """Maneja el envío del formulario - VERSIÓN CORREGIDA PARA INGRESOS"""
        try:
            # Validaciones básicas
            if amount <= 0:
                st.error("❌ El monto debe ser mayor a 0")
                return
                
            if not category:
                st.error("❌ Debes seleccionar una categoría")
                return
            
            # 🎯 DEBUG ESPECÍFICO PARA INGRESOS
            st.write(f"🔍 **Datos a guardar:**")
            st.write(f"- Categoría seleccionada: **{category}**")
            st.write(f"- Tipo de transacción: **{transaction_type}**")
            st.write(f"- Monto: **{amount}€**")
            st.write(f"- Descripción: **{description}**")
            st.write(f"- Emoción: **{emotion}**")
            
            # 🔥 CORRECCIÓN CRÍTICA: Forzar la categoría seleccionada
            # Asegurarnos de que NO se use una categoría por defecto
            final_category = category  # Usar EXACTAMENTE la categoría seleccionada
            
            # Si es un ingreso y la categoría seleccionada no es apropiada, sugerir cambio
            if transaction_type == TransactionType.INCOME and "ingreso" not in category.lower() and "💼" not in category:
                st.warning(f"⚠️ Estás registrando un INGRESO con categoría '{category}'. ¿Estás seguro?")
                # Pero igual usar la categoría seleccionada por el usuario
            
            # Llamada al servicio
            result = self.transaction_service.add_transaction(
                amount=amount,
                category=final_category,  # 🔥 USAR CATEGORÍA SELECCIONADA
                emotion=emotion,
                description=description,
                transaction_type=transaction_type
            )
            
            if result["success"]:
                st.success(f"✅ **¡Guardado correctamente!**")
                st.balloons()
                
                # 🔥 VERIFICACIÓN ESPECÍFICA PARA INGRESOS
                st.write("---")
                st.write("### 🔄 Verificación en tiempo real:")
                recent = self.transaction_service.get_recent_transactions(limit=1)
                if recent:
                    actual_transaction = recent[0]
                    st.write(f"**En base de datos:**")
                    st.write(f"- Categoría: **{actual_transaction['category']}**")
                    st.write(f"- Descripción: **{actual_transaction['description']}**")
                    st.write(f"- Tipo: **{actual_transaction['type']}**")
                    st.write(f"- Monto: **{actual_transaction['amount']}€**")
                    
                    if actual_transaction['category'] == final_category:
                        st.success("✅ **CONFIRMADO:** La categoría coincide con la seleccionada")
                    else:
                        st.error(f"❌ **DISCREPANCIA:** Esperaba '{final_category}' pero se guardó '{actual_transaction['category']}'")
                        
                        # 🔍 DIAGNÓSTICO ADICIONAL
                        st.write("### 🕵️ Diagnóstico del problema:")
                        st.write("Esto indica que el problema está en el **TransactionService** o **Database**")
                        st.write("Necesito ver estos archivos para solucionarlo:")
                        st.code("""
- core/services/transaction_service.py (método add_transaction)
- core/database.py (método save_transaction) 
                        """)
            else:
                st.error(f"❌ {result['message']}")
                
        except Exception as e:
            st.error(f"❌ Error inesperado: {str(e)}")

    def render_compact(self):
        """Versión compacta - SIN CAMBIOS"""
        with st.form("quick_entry_compact"):
            st.write("💸 **Añadir rápido**")
            
            col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
            
            with col1:
                amount = st.number_input(
                    "Monto",
                    min_value=0.01,
                    step=0.01,
                    value=0.01,
                    format="%.2f",
                    label_visibility="collapsed",
                    placeholder="0.00€"
                )
            
            with col2:
                categories = self.transaction_service.get_suggested_categories()
                category = st.selectbox(
                    "Categoría",
                    options=categories,
                    label_visibility="collapsed"
                )
            
            with col3:
                emotion = st.selectbox(
                    "Emoción",
                    options=["neutral", "happy", "impulsive"],
                    format_func=lambda x: {
                        "neutral": "😐",
                        "happy": "😊", 
                        "impulsive": "⚡"
                    }[x],
                    label_visibility="collapsed"
                )
            
            with col4:
                submitted = st.form_submit_button(
                    "💾",
                    use_container_width=True,
                    help="Guardar transacción"
                )
            
            if submitted:
                if amount <= 0:
                    st.error("Monto debe ser > 0")
                    return
                    
                result = self.transaction_service.add_transaction(
                    amount=amount,
                    category=category,
                    emotion=emotion,
                    description="",
                    transaction_type=TransactionType.EXPENSE
                )
                
                if result["success"]:
                    st.success("✅")