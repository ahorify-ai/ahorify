from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional, Literal
from enum import Enum
import uuid

class TransactionType(str, Enum):
    """Tipos de transacción soportados"""
    EXPENSE = "expense"
    INCOME = "income"

class TransactionEmotion(str, Enum):
    """Emociones soportadas para transacciones - PARA UI"""
    NEUTRAL = "neutral"
    HAPPY = "happy" 
    IMPULSIVE = "impulsive"
    STRESS = "stress"
    INVESTMENT = "investment"

# Alias para compatibilidad
EmotionType = TransactionEmotion

class Transaction(BaseModel):
    """
    Modelo de transacción con validación completa
    Compatible con la migración v4 de la base de datos
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = Field(default="default_user")
    amount: float = Field(..., gt=0, description="El monto debe ser positivo")
    type: TransactionType
    category: str
    emotion: str = Field(default="neutral")
    description: str = Field(default="")
    created_at: datetime = Field(default_factory=datetime.now)

    @validator('emotion')
    def validate_emotion(cls, v):
        """Valida que la emoción sea una de las soportadas"""
        valid_emotions = [e.value for e in TransactionEmotion]
        if v not in valid_emotions:
            raise ValueError(f'Emoción debe ser una de: {valid_emotions}')
        return v

    @validator('amount')
    def validate_amount(cls, v):
        """Valida que el monto sea positivo"""
        if v <= 0:
            raise ValueError('El monto debe ser mayor a 0')
        return round(v, 2)  # Redondear a 2 decimales

    @validator('category')
    def validate_category(cls, v):
        """Valida que la categoría no esté vacía"""
        if not v or not v.strip():
            raise ValueError('La categoría no puede estar vacía')
        return v.strip()

    def model_dump(self, **kwargs):
        """Override para asegurar compatibilidad con diferentes versiones de Pydantic"""
        data = super().model_dump(**kwargs)
        # Asegurar que los datetime se conviertan a string ISO
        if 'created_at' in data and isinstance(data['created_at'], datetime):
            data['created_at'] = data['created_at'].isoformat()
        return data

class UserPreferences(BaseModel):
    """
    Preferencias de usuario para personalización
    """
    user_id: str = Field(default="default_user")
    onboarding_complete: bool = Field(default=False)
    primary_goal: Optional[str] = Field(default=None)
    currency: str = Field(default="€")
    notifications_enabled: bool = Field(default=True)
    weekly_reports_enabled: bool = Field(default=True)
    theme: str = Field(default="Automático")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    @validator('currency')
    def validate_currency(cls, v):
        """Valida el símbolo de moneda"""
        if not v or len(v) > 3:
            raise ValueError('Símbolo de moneda inválido')
        return v

    @validator('theme')
    def validate_theme(cls, v):
        """Valida el tema seleccionado"""
        valid_themes = ['Automático', 'Claro', 'Oscuro']
        if v not in valid_themes:
            raise ValueError(f'Tema debe ser uno de: {valid_themes}')
        return v

class UserStats(BaseModel):
    """
    Estadísticas de usuario para gamificación
    """
    user_id: str = Field(default="default_user")
    current_streak: int = Field(default=0, ge=0)
    longest_streak: int = Field(default=0, ge=0)
    total_points: int = Field(default=0, ge=0)
    total_streak_days: int = Field(default=0, ge=0)
    last_activity_date: Optional[str] = Field(default=None)
    freeze_used_this_week: bool = Field(default=False)
    recovery_used_this_month: bool = Field(default=False)
    streak_protection_used: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    @validator('current_streak', 'longest_streak', 'total_points', 'total_streak_days')
    def validate_non_negative(cls, v):
        """Valida que los valores numéricos no sean negativos"""
        if v < 0:
            raise ValueError('El valor no puede ser negativo')
        return v

class StreakMilestone(BaseModel):
    """
    Hitos de racha alcanzados por el usuario
    """
    user_id: str = Field(default="default_user")
    milestone_days: int = Field(..., ge=1)
    achieved_at: datetime = Field(default_factory=datetime.now)
    reward_claimed: bool = Field(default=False)

class DailyEngagement(BaseModel):
    """
    Registro de engagement diario del usuario
    """
    user_id: str = Field(default="default_user")
    activity_date: str  # Formato YYYY-MM-DD
    actions_count: int = Field(default=1, ge=1)
    actions_types: str = Field(default="")
    created_at: datetime = Field(default_factory=datetime.now)

    @validator('activity_date')
    def validate_date_format(cls, v):
        """Valida el formato de fecha YYYY-MM-DD"""
        try:
            datetime.strptime(v, '%Y-%m-%d')
            return v
        except ValueError:
            raise ValueError('La fecha debe estar en formato YYYY-MM-DD')

# Categorías por defecto para la aplicación
DEFAULT_CATEGORIES = [
    "🍔 Comida", "🚗 Transporte", "🎮 Ocio", "🏠 Vivienda",
    "👗 Ropa", "💊 Salud", "📚 Educación", "✈️ Viajes",
    "🎁 Regalos", "📱 Tecnología", "💡 Servicios", "💰 Ahorros",
    "💼 Ingresos", "❓ Otros"
]

# Mapeo de emociones a emojis para la UI
EMOTION_EMOJIS = {
    TransactionEmotion.NEUTRAL: "😐",
    TransactionEmotion.HAPPY: "😊",
    TransactionEmotion.IMPULSIVE: "⚡", 
    TransactionEmotion.STRESS: "😥",
    TransactionEmotion.INVESTMENT: "📈"
}

# Exportar todos los modelos y enums
__all__ = [
    'TransactionType',
    'TransactionEmotion',  # ✅ AGREGADO PARA EL ERROR
    'EmotionType',
    'Transaction',
    'UserPreferences', 
    'UserStats',
    'StreakMilestone',
    'DailyEngagement',
    'DEFAULT_CATEGORIES',
    'EMOTION_EMOJIS'
]