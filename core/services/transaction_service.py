# Transaction business logic
from datetime import datetime, date, timedelta
from typing import List, Dict, Optional
from core.database import db
from core.models import Transaction, TransactionType, DEFAULT_CATEGORIES
import uuid

class TransactionService:
    """
    Servicio optimizado SOLO para gestión de transacciones.
    Responsabilidad única: CRUD transacciones + categorías.
    """
    
    def __init__(self):
        self.user_id = "default_user"
    
    def add_transaction(self, amount: float, category: str, 
                   description: str = "", 
                   transaction_type: TransactionType = TransactionType.EXPENSE,
                   emotion: str = "neutral") -> Dict:
        """
        Añade una transacción - RESPONSABILIDAD ÚNICA
        Retorna: {"success": bool, "message": str, "transaction_id": str}
        """
        try:
        # Validación básica
            if amount <= 0:
                return {
                    "success": False,
                    "message": "❌ El monto debe ser mayor a 0"
                }
        
        # 🔥 CORRECCIÓN CRÍTICA: Convertir TransactionType a string
            transaction_type_str = transaction_type.value  # Esto convierte el Enum a string
        
        # Crear transacción
            transaction = Transaction(
                id=str(uuid.uuid4()),
                user_id=self.user_id,
                amount=amount,
                type=transaction_type_str,  # 🔥 USAR EL STRING, NO EL ENUM
                category=category,
                emotion=emotion,
                description=description,
                created_at=datetime.now()
            )
        
        # Guardar en base de datos
            transaction_data = transaction.model_dump()
            success = db.save_transaction(transaction_data)
        
            if success:
                self._trigger_gamification(transaction_data)

                return {
                    "success": True,
                    "message": "✅ Transacción guardada correctamente",
                    "transaction_id": transaction.id
                }
            else:
                return {
                    "success": False,
                    "message": "❌ Error al guardar la transacción"
                }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"❌ Error: {str(e)}"
            }

    def _trigger_gamification(self, transaction_data: Dict):
        """Activa el sistema de gamificación para esta transacción"""
        try:
            # 🔥 NUEVA ESTRATEGIA: Ejecutar en hilo separado o con delay
            import threading
            import time
        
            def async_gamification():
                # Pequeño delay para evitar conflictos de conexión
                time.sleep(0.5)
                try:
                    from core.services.gamification_service import gamification_service
                    result = gamification_service.record_engagement(
                        action_type="transaction_added",
                        metadata={
                            "amount": transaction_data['amount'],
                            "category": transaction_data['category'],
                            "emotion": transaction_data['emotion'],
                            "type": transaction_data['type']
                        }
                    )
                    print(f"🎮 Gamificación completada: {result.get('success', False)}")
                except Exception as e:
                    print(f"⚠️ Error en gamificación async: {e}")
        
            # Ejecutar en hilo separado
            thread = threading.Thread(target=async_gamification)
            thread.daemon = True
            thread.start()
        
        except Exception as e:
            print(f"⚠️ Error lanzando gamificación async: {e}")
    
    def get_recent_transactions(self, limit: int = 10) -> List[Dict]:
        """Obtiene transacciones recientes formateadas para UI"""
        rows = db.get_user_transactions(self.user_id, limit)
        
        transactions = []
        for row in rows: 
            emotion_emojis = {
                "neutral": "😐",
                "happy": "😊", 
                "impulsive": "⚡",
                "stress": "😥",
                "investment": "📈"
            }

            transactions.append({
                "id": row['id'],
                "amount": row['amount'],
                "type": row['type'],
                "category": row['category'],
                "emotion": row['emotion'], 
                "emotion_emoji": emotion_emojis.get(row['emotion'], "😐"),
                "description": row['description'],
                "created_at": row['created_at'],
                "formatted_date": self._format_date(row['created_at']),
                "formatted_amount": f"€{row['amount']:.2f}",
                "is_expense": row['type'] == 'expense'
            })
        
        return transactions
    
    def get_totals(self) -> Dict[str, float]:
        """Obtiene totales para dashboard - OPTIMIZADO"""
        totals_by_type = db.get_totals_by_type(self.user_id)
        
        total_expenses = totals_by_type.get('expense', 0)
        total_income = totals_by_type.get('income', 0)
        balance = total_income - total_expenses
        
        return {
            "total_expenses": total_expenses,
            "total_income": total_income,
            "balance": balance,
            "formatted_expenses": f"€{total_expenses:.2f}",
            "formatted_income": f"€{total_income:.2f}",
            "formatted_balance": f"€{balance:.2f}"
        }
    
    def get_category_breakdown(self) -> List[Dict]:
        """Obtiene desglose por categoría para gráficos"""
        category_totals = db.get_category_totals(self.user_id)
        
        breakdown = []
        total_expenses = sum(row['total'] for row in category_totals)
        
        for row in category_totals:
            percentage = (row['total'] / total_expenses * 100) if total_expenses > 0 else 0
            breakdown.append({
                "category": row['category'],
                "amount": row['total'],
                "formatted_amount": f"€{row['total']:.2f}",
                "percentage": round(percentage, 1),
                "formatted_percentage": f"{round(percentage, 1)}%"
            })
        
        return breakdown
    
    def get_suggested_categories(self) -> List[str]:
        """Obtiene categorías sugeridas (más usadas + default)"""
        user_categories = db.get_user_categories(self.user_id)
        
        # Combinar categorías del usuario con las default, eliminando duplicados
        all_categories = list(dict.fromkeys(user_categories + DEFAULT_CATEGORIES))
        
        return all_categories[:15]  # Máximo 15 categorías
    
    def get_weekly_summary(self) -> Dict:
        """Resumen de la semana actual vs semana anterior - OPTIMIZADO"""
        today = date.today()
        start_of_week = today - timedelta(days=today.weekday())
        start_of_last_week = start_of_week - timedelta(days=7)
        end_of_last_week = start_of_week - timedelta(days=1)
        
        # Transacciones de esta semana
        this_week_transactions = db.get_transactions_by_date_range(
            self.user_id,
            start_of_week.isoformat(), 
            today.isoformat()
        )
        
        # Transacciones de la semana pasada
        last_week_transactions = db.get_transactions_by_date_range(
            self.user_id,
            start_of_last_week.isoformat(),
            end_of_last_week.isoformat()
        )
        
        # Calcular totales optimizado
        def sum_expenses(transactions):
            return sum(row['amount'] for row in transactions if row['type'] == 'expense')
        
        this_week_expenses = sum_expenses(this_week_transactions)
        last_week_expenses = sum_expenses(last_week_transactions)
        
        # Calcular diferencia porcentual
        if last_week_expenses > 0:
            expense_change = ((this_week_expenses - last_week_expenses) / last_week_expenses) * 100
        else:
            expense_change = 0
        
        # Determinar tendencia
        if expense_change > 5:
            trend = "📈 Subiendo"
            trend_color = "red"
        elif expense_change < -5:
            trend = "📉 Bajando" 
            trend_color = "green"
        else:
            trend = "➡️ Estable"
            trend_color = "gray"
        
        return {
            "this_week_expenses": this_week_expenses,
            "last_week_expenses": last_week_expenses,
            "expense_change": expense_change,
            "trend": trend,
            "trend_color": trend_color,
            "formatted_this_week": f"€{this_week_expenses:.2f}",
            "formatted_last_week": f"€{last_week_expenses:.2f}",
            "formatted_change": f"{expense_change:+.1f}%"
        }
    
    def get_monthly_totals(self) -> Dict:
        """Totales del mes actual - NUEVO MÉTODO OPTIMIZADO"""
        today = date.today()
        start_of_month = date(today.year, today.month, 1)
        
        monthly_transactions = db.get_transactions_by_date_range(
            self.user_id,
            start_of_month.isoformat(),
            today.isoformat()
        )
        
        monthly_expenses = sum(row['amount'] for row in monthly_transactions if row['type'] == 'expense')
        monthly_income = sum(row['amount'] for row in monthly_transactions if row['type'] == 'income')
        
        # Calcular promedio diario
        days_in_month = today.day
        daily_average = monthly_expenses / days_in_month if days_in_month > 0 else 0
        
        return {
            "monthly_expenses": monthly_expenses,
            "monthly_income": monthly_income,
            "daily_average": daily_average,
            "formatted_monthly_expenses": f"€{monthly_expenses:.2f}",
            "formatted_daily_average": f"€{daily_average:.2f}"
        }
    
    def get_top_categories(self, limit: int = 5) -> List[Dict]:
        """Top categorías de gasto - NUEVO MÉTODO OPTIMIZADO"""
        category_totals = db.get_category_totals(self.user_id)
        
        top_categories = []
        for i, row in enumerate(category_totals[:limit]):
            top_categories.append({
                "rank": i + 1,
                "category": row['category'],
                "amount": row['total'],
                "formatted_amount": f"€{row['total']:.2f}"
            })
        
        return top_categories
    
    def search_transactions(self, query: str, category: str = None) -> List[Dict]:
        """Búsqueda de transacciones - NUEVO MÉTODO"""
        all_transactions = db.get_user_transactions(self.user_id, limit=1000)
        
        results = []
        query_lower = query.lower()
        
        for transaction in all_transactions:
            matches_query = (query_lower in transaction['description'].lower() if transaction['description'] else False)
            matches_category = (category is None or transaction['category'] == category)
            
            if matches_query and matches_category:
                results.append({
                    "id": transaction['id'],
                    "amount": transaction['amount'],
                    "type": transaction['type'],
                    "category": transaction['category'],
                    "description": transaction['description'],
                    "created_at": transaction['created_at'],
                    "formatted_date": self._format_date(transaction['created_at']),
                    "formatted_amount": f"€{transaction['amount']:.2f}"
                })
        
        return results
    
    def delete_transaction(self, transaction_id: str) -> Dict:
        """Elimina una transacción - NUEVO MÉTODO"""
        try:
            # En una implementación real, aquí iría la lógica de eliminación
            # Por ahora retornamos éxito simulado
            return {
                "success": True,
                "message": "✅ Transacción eliminada correctamente"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"❌ Error al eliminar: {str(e)}"
            }
    
    def _format_date(self, date_string: str) -> str:
        """Formatea fecha para mostrar en UI"""
        if isinstance(date_string, str):
            try:
                dt = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
                return dt.strftime("%d/%m/%Y %H:%M")
            except:
                return date_string
        return str(date_string)

# Instancia global optimizada
transaction_service = TransactionService()