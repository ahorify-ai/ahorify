from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Tuple
from core.database import db
import logging

logger = logging.getLogger(__name__)

class GamificationService:
    """
    Servicio de gamificación optimizado - Duolingo-style mejorado
    Principios SOLID + Mejor manejo de errores + Más testable
    """
    
    # Configuración centralizada
    POINTS_CONFIG = {
        "transaction_added": 10,
        "dashboard_viewed": 5,
        "goal_checked": 3,
        "weekly_review_completed": 25,
        "category_analysis_viewed": 15,
    }
    
    STREAK_MILESTONES = {
        3: {"points": 25, "message": "🌟 ¡3 días seguidos!"},
        7: {"points": 50, "message": "🚀 ¡1 semana completa!"},
        14: {"points": 100, "message": "💫 ¡2 semanas!"},
        30: {"points": 250, "message": "🏆 ¡1 MES!"},
        90: {"points": 500, "message": "👑 ¡3 MESES!"}
    }
    
    LEVELS = [
        {"points": 0, "name": "Recién Llegado 💰", "badge": "💰"},
        {"points": 100, "name": "Operador Junior 📈", "badge": "📈"},
        {"points": 300, "name": "Analista Senior 💼", "badge": "💼"},
        {"points": 600, "name": "Fund Manager 🏦", "badge": "🏦"},
        {"points": 1000, "name": "Tiburón de Wall Street 🦈", "badge": "🦈"},
        {"points": 1500, "name": "Magnate Financiero 💎", "badge": "💎"},
        {"points": 2100, "name": "Visionario Global 🌐", "badge": "🌐"},
        {"points": 2800, "name": "Leyenda Viva 🏆", "badge": "🏆"},
        {"points": 3600, "name": "Oráculo Financiero 🔮", "badge": "🔮"},
        {"points": 4500, "name": "Emperador del Capital 👑", "badge": "👑"}
    ]
    
    def __init__(self, user_id: str = "default_user"):
        self.user_id = user_id
        self._ensure_user_initialized()
    
    def _ensure_user_initialized(self):
        """Garantiza que el usuario tenga stats iniciales de forma segura"""
        try:
            user_stats = db.get_user_stats(self.user_id)
            if not user_stats:
                self._create_initial_user_stats()
        except Exception as e:
            logger.error(f"Error inicializando usuario {self.user_id}: {e}")
            raise
    
    def _create_initial_user_stats(self):
        """Crea stats iniciales para nuevo usuario"""
        stats_data = {
            "user_id": self.user_id,
            "current_streak": 0,
            "longest_streak": 0,
            "total_points": 0,
            "total_streak_days": 0,
            "last_activity_date": None,
            "freeze_used_this_week": False,
            "recovery_used_this_month": False
        }
        db.update_user_stats(stats_data)

    # 🎯 MÉTODO PRINCIPAL MEJORADO
    def record_engagement(self, action_type: str, metadata: Dict = None) -> Dict:
        """
        Registra engagement del usuario - Versión optimizada
        Retorna resultado consolidado
        """
        try:
            # 1. Validar acción
            if not self._is_valid_action(action_type):
                return self._error_response(f"Acción no válida: {action_type}")
            
            # 2. Registrar en daily_engagement
            db.record_daily_engagement(self.user_id, action_type)
            
            # 3. Procesar racha
            streak_result = self._process_streak_update()
            
            # 4. Calcular puntos
            points_result = self._calculate_points(action_type, metadata)
            
            # 5. Verificar hitos
            milestone_result = self._check_milestones(streak_result["current_streak"])
            
            # 6. Verificar nivel
            level_result = self._check_level_progression()
            
            # 7. Consolidar resultados
            return self._consolidate_results(
                action_type, streak_result, points_result, milestone_result, level_result
            )
            
        except Exception as e:
            logger.error(f"Error en record_engagement: {e}")
            return self._error_response("Error procesando engagement")

    # 🔥 NÚCLEO DEL SISTEMA DE RACHAS - MEJORADO
    def _process_streak_update(self) -> Dict:
        """Procesa actualización de racha de forma robusta"""
        user_stats = db.get_user_stats(self.user_id)
        today = date.today()
        
        if not user_stats or not user_stats.get('last_activity_date'):
            return self._start_new_streak(today)
        
        last_active = self._parse_date(user_stats.get('last_activity_date'))
        days_since_last = (today - last_active).days
        
        if days_since_last == 0:
            return self._maintain_streak(user_stats)
        elif days_since_last == 1:
            return self._increment_streak(user_stats, today)
        else:
            return self._handle_streak_break(user_stats, today, days_since_last)

    def _start_new_streak(self, today: date) -> Dict:
        """Inicia nueva racha con validación"""
        try:
            stats_data = {
                "user_id": self.user_id,
                "current_streak": 1,
                "longest_streak": 1,
                "total_points": 10,
                "total_streak_days": 1,
                "last_activity_date": today.isoformat()
            }
            db.update_user_stats(stats_data)
            
            return {
                "streak_updated": True,
                "current_streak": 1,
                "message": "🎉 ¡Comienza tu racha financiera!"
            }
        except Exception as e:
            logger.error(f"Error iniciando racha: {e}")
            return {"streak_updated": False, "current_streak": 0, "message": "Error iniciando racha"}

    def _increment_streak(self, user_stats: Dict, today: date) -> Dict:
        """Incrementa racha con cálculo de bonus"""
        try:
            new_streak = user_stats.get('current_streak', 0) + 1
            longest_streak = max(user_stats.get('longest_streak', 0), new_streak)
            
            # Bonus por racha progresivo
            streak_bonus = 10 + (min(new_streak, 7) * 2)  # +2 puntos por día hasta 7
            
            stats_data = {
                "user_id": self.user_id,
                "current_streak": new_streak,
                "longest_streak": longest_streak,
                "total_points": user_stats.get('total_points', 0) + streak_bonus,
                "total_streak_days": user_stats.get('total_streak_days', 0) + 1,
                "last_activity_date": today.isoformat()
            }
            db.update_user_stats(stats_data)
            
            return {
                "streak_updated": True,
                "current_streak": new_streak,
                "message": f"🔥 ¡Racha de {new_streak} días! +{streak_bonus} puntos"
            }
        except Exception as e:
            logger.error(f"Error incrementando racha: {e}")
            return {"streak_updated": False, "current_streak": user_stats.get('current_streak', 0), "message": "Error actualizando racha"}

    # 🎮 SISTEMA DE PUNTOS MEJORADO
    def _calculate_points(self, action_type: str, metadata: Dict) -> Dict:
        """Calcula puntos con bonus contextuales"""
        base_points = self.POINTS_CONFIG.get(action_type, 5)
        
        # Bonus contextuales
        bonuses = self._calculate_bonuses(metadata)
        total_points = base_points + bonuses
        
        # Actualizar en BD
        self._add_points(total_points)
        
        return {
            "base_points": base_points,
            "bonuses": bonuses,
            "total_points": total_points
        }

    def _calculate_bonuses(self, metadata: Dict) -> int:
        """Calcula bonus basados en contexto"""
        bonuses = 0
        
        if metadata:
            # Bonus por primera vez
            if metadata.get("first_time", False):
                bonuses += 10
            
            # Bonus por consistencia
            if metadata.get("consistent_week", False):
                bonuses += 20
            
            # Bonus por fin de semana
            if datetime.today().weekday() >= 5:  # Sábado o domingo
                bonuses += 5
        
        return bonuses

    def _add_points(self, points: int):
        """Añade puntos de forma segura"""
        try:
            user_stats = db.get_user_stats(self.user_id)
            if user_stats:
                stats_data = {
                    "user_id": self.user_id,
                    "total_points": user_stats.get('total_points', 0) + points,
                    "current_streak": user_stats.get('current_streak', 0),
                    "longest_streak": user_stats.get('longest_streak', 0),
                    "total_streak_days": user_stats.get('total_streak_days', 0),
                    "last_activity_date": user_stats.get('last_activity_date')
                }
                db.update_user_stats(stats_data)
        except Exception as e:
            logger.error(f"Error añadiendo puntos: {e}")

    # 🏆 SISTEMA DE NIVELES OPTIMIZADO
    def _check_level_progression(self) -> Dict:
        """Verifica progresión de nivel"""
        current_points = self._get_current_points()
        current_level = self._calculate_level(current_points)
        previous_level = self._get_previous_level(current_points)
        
        level_up = current_level > previous_level
        
        return {
            "level_up": level_up,
            "current_level": current_level,
            "previous_level": previous_level,
            "level_info": self._get_level_info(current_level)
        }

    def _calculate_level(self, points: int) -> int:
        """Calcula nivel basado en puntos - VERSIÓN CORREGIDA DEFINITIVA"""
        # ✅ CORRECCIÓN: Buscar el nivel MÁS ALTO que cumple con los puntos
        level = 0
        for i, level_info in enumerate(self.LEVELS):
            if points >= level_info["points"]:
                level = i
            else:
                break
        return level

    def _get_previous_level(self, current_points: int) -> int:
        """Obtiene nivel anterior"""
        return self._calculate_level(max(0, current_points - 10))

    # 📊 MÉTODOS DE UTILIDAD MEJORADOS
    def _is_valid_action(self, action_type: str) -> bool:
        """Valida que la acción sea reconocida"""
        return action_type in self.POINTS_CONFIG or action_type.startswith("custom_")

    def _parse_date(self, date_str: str) -> date:
        """Parsea fecha de forma segura"""
        try:
            return datetime.strptime(date_str, '%Y-%m-%d').date()
        except:
            return date.today()  # fallback

    def _get_current_points(self) -> int:
        """Obtiene puntos actuales de forma segura"""
        try:
            user_stats = db.get_user_stats(self.user_id)
            return user_stats.get('total_points', 0) if user_stats else 0
        except:
            return 0

    def _get_level_info(self, level: int) -> Dict:
        """Obtiene info de nivel de forma segura - VERSIÓN CORREGIDA"""
        # ✅ CORRECCIÓN: Los niveles van de 0 a 9, no de 1 a 10
        if 0 <= level < len(self.LEVELS):
            return self.LEVELS[level]
        return self.LEVELS[0]  # Nivel inicial como fallbackk

    def _consolidate_results(self, action_type: str, streak_result: Dict, 
                           points_result: Dict, milestone_result: Dict, level_result: Dict) -> Dict:
        """Consolida todos los resultados en una respuesta unificada"""
        return {
            "success": True,
            "action": action_type,
            "streak": {
                "updated": streak_result["streak_updated"],
                "current": streak_result["current_streak"],
                "message": streak_result.get("message", "")
            },
            "points": {
                "earned": points_result["total_points"],
                "base": points_result["base_points"],
                "bonuses": points_result["bonuses"],
                "total": self._get_current_points()
            },
            "milestone": milestone_result,
            "level": level_result,
            "timestamp": datetime.now().isoformat()
        }

    def _error_response(self, message: str) -> Dict:
        """Respuesta de error estandarizada"""
        return {
            "success": False,
            "error": message,
            "timestamp": datetime.now().isoformat()
        }

    # 🎯 INTERFAZ PÚBLICA MEJORADA - VERSIÓN CORREGIDA
    def get_user_progress(self) -> Dict:
        """Obtiene progreso completo del usuario - VERSIÓN DEFINITIVA CORREGIDA"""
        try:
            # ✅ Obtener stats del usuario
            user_stats = db.get_user_stats(self.user_id)
            if not user_stats:
                return self._get_default_progress()
            
            # ✅ Obtener engagement stats con manejo de errores
            engagement_stats = {}
            try:
                engagement_stats = db.get_user_engagement_stats(self.user_id)
            except Exception as e:
                print(f"⚠️ Error obteniendo engagement: {e}")
                engagement_stats = {"total_active_days": 0, "engagement_rate": 0}
            
            # ✅ CALCULAR NIVEL Y PROGRESO CORREGIDO
            current_points = user_stats.get('total_points', 0)
            current_level = self._calculate_level(current_points)
            level_info = self._get_level_info(current_level)

            # 🔥 CORRECCIÓN CRÍTICA: Lógica de siguiente nivel
            next_level_index = current_level  # El siguiente nivel es current_level + 1, pero usamos current_level para puntos
            if next_level_index < len(self.LEVELS) - 1:
                next_level_points = self.LEVELS[next_level_index + 1]["points"]
            else:
                next_level_points = self.LEVELS[next_level_index]["points"]  # Nivel máximo

            # 🔥 CORRECCIÓN: Evitar división por cero y calcular progreso correctamente
            current_level_points = self.LEVELS[current_level]["points"]
            points_in_current_level = current_points - current_level_points
            points_needed_for_next = next_level_points - current_level_points
            
            if points_needed_for_next > 0:
                progress_percentage = (points_in_current_level / points_needed_for_next) * 100
            else:
                progress_percentage = 100.0  # Nivel máximo

            # ✅ Asegurar que el porcentaje esté entre 0-100
            progress_percentage = max(0, min(100, progress_percentage))

            return {
                "level": current_level,
                "level_info": level_info,
                "points": current_points,
                "next_level_points": next_level_points,
                "progress_percentage": round(progress_percentage, 1),
                "streak": {
                    "current": user_stats.get('current_streak', 0),
                    "longest": user_stats.get('longest_streak', 0),
                    "total_days": user_stats.get('total_streak_days', 0)
                },
                "engagement": engagement_stats,
                "protections": {
                    "freeze_available": not user_stats.get('freeze_used_this_week', False),
                    "recovery_available": not user_stats.get('recovery_used_this_month', False)
                }
            }
            
        except Exception as e:
            print(f"❌ Error crítico en get_user_progress: {e}")
            return self._get_default_progress()

    def _get_default_progress(self) -> Dict:
        """Progreso por defecto en caso de error"""
        return {
            "level": 0,
            "level_info": self.LEVELS[0],
            "points": 0,
            "next_level_points": 100,
            "progress_percentage": 0,
            "streak": {"current": 0, "longest": 0, "total_days": 0},
            "engagement": {"total_active_days": 0, "engagement_rate": 0},
            "protections": {"freeze_available": True, "recovery_available": True}
        }

    # 🔥 MÉTODO FALTANTE - CORREGIDO
    def _check_milestones(self, current_streak: int) -> Dict:
        """
        Verifica si se han alcanzado hitos de racha y otorga recompensas.
        """
        try:
            milestone_result = {
                "achieved": False,
                "milestone_days": None,
                "message": "",
                "points_earned": 0
            }
            
            # Verificar hitos de racha
            for milestone_days, milestone_info in self.STREAK_MILESTONES.items():
                if current_streak == milestone_days:
                    # ¡Hito alcanzado!
                    points_earned = milestone_info["points"]
                    
                    # Otorgar puntos
                    self._add_points(points_earned)
                    
                    # Registrar en base de datos
                    try:
                        db.add_streak_milestone(self.user_id, milestone_days)
                    except Exception as e:
                        logger.warning(f"No se pudo registrar hito en BD: {e}")
                    
                    milestone_result = {
                        "achieved": True,
                        "milestone_days": milestone_days,
                        "message": milestone_info["message"],
                        "points_earned": points_earned
                    }
                    break
            
            return milestone_result
            
        except Exception as e:
            logger.error(f"Error en _check_milestones: {e}")
            return {
                "achieved": False,
                "milestone_days": None,
                "message": "",
                "points_earned": 0
            }

    # 🔧 MÉTODOS FALTANTES PARA COMPLETAR LA CLASE
    def _maintain_streak(self, user_stats: Dict) -> Dict:
        """Mantiene la racha actual sin cambios"""
        return {
            "streak_updated": False,
            "current_streak": user_stats.get('current_streak', 0),
            "message": "Racha mantenida - ya activo hoy"
        }

    def _handle_streak_break(self, user_stats: Dict, today: date, days_since_last: int) -> Dict:
        """Maneja la ruptura de racha"""
        try:
            stats_data = {
                "user_id": self.user_id,
                "current_streak": 0,
                "longest_streak": user_stats.get('longest_streak', 0),
                "total_points": user_stats.get('total_points', 0),
                "total_streak_days": user_stats.get('total_streak_days', 0),
                "last_activity_date": today.isoformat()
            }
            db.update_user_stats(stats_data)
            
            return {
                "streak_updated": True,
                "current_streak": 0,
                "message": f"💔 Racha rota después de {days_since_last} días de inactividad"
            }
        except Exception as e:
            logger.error(f"Error manejando ruptura de racha: {e}")
            return {"streak_updated": False, "current_streak": 0, "message": "Error actualizando racha"}

    def _check_streak_protection(self, user_stats: Dict) -> bool:
        """Verifica si hay protecciones de racha disponibles"""
        return not user_stats.get('freeze_used_this_week', False)

# Instancia global mejorada
gamification_service = GamificationService()