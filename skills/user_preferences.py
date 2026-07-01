"""Gestión de preferencias de usuario con persistencia.

Actualmente soporta la configuración de zona horaria por usuario,
pero está diseñado para extenderse a otras preferencias.
Los datos se almacenan en el archivo JSON compartido del bot.
"""
from datetime import datetime
from zoneinfo import available_timezones, ZoneInfo
import logging

from utils.persistence import AsyncPersistence


log = logging.getLogger("user_prefs")

_VALID_TIMEZONES: set[str] | None = None


def _list_timezones() -> set[str]:
    """Retorna el conjunto completo de zonas horarias válidas (cacheado)."""
    global _VALID_TIMEZONES
    if _VALID_TIMEZONES is None:
        _VALID_TIMEZONES = available_timezones()
    return _VALID_TIMEZONES


class UserPreferences:
    """Administra preferencias persistentes por usuario (ej. zona horaria).

    Los datos se guardan en el almacenamiento JSON compartido bajo la
    clave ``timezones``, con el ID de usuario como subclave.

    Args:
        persistence: Instancia de AsyncPersistence para leer/escribir datos.
    """

    TZ_PATH = "timezones"

    def __init__(self, persistence: AsyncPersistence):
        self._store = persistence

    def _timezones(self) -> dict[str, str]:
        return self._store.data.setdefault(self.TZ_PATH, {})

    def set_timezone(self, user_id: int, timezone_str: str) -> str:
        """Guarda la zona horaria de un usuario con validación.

        Args:
            user_id: ID de Discord del usuario.
            timezone_str: Nombre de zona horaria (ej. "America/Argentina/Buenos_Aires").

        Returns:
            Mensaje de confirmación o error, incluyendo sugerencias si el
            nombre ingresado es similar a uno válido.
        """
        tz_list = _list_timezones()
        if timezone_str not in tz_list:
            similar = [tz for tz in tz_list if timezone_str.lower() in tz.lower()][:3]
            msg = f"Zona horaria '{timezone_str}' no válida."
            if similar:
                msg += f" Quizás quisiste decir: {', '.join(similar)}"
            return msg

        uid = str(user_id)
        self._timezones()[uid] = timezone_str
        self._store.mark_dirty()
        log.info("Timezone set for user %s: %s", uid, timezone_str)
        return f"Zona horaria guardada: **{timezone_str}**"

    def get_timezone(self, user_id: int) -> str | None:
        """Obtiene la zona horaria guardada de un usuario.

        Args:
            user_id: ID de Discord del usuario.

        Returns:
            Nombre de la zona horaria o None si no está configurada.
        """
        uid = str(user_id)
        return self._timezones().get(uid)

    def get_current_time_for(self, user_id: int) -> str | None:
        """Obtiene la hora actual en la zona horaria del usuario.

        Args:
            user_id: ID de Discord del usuario.

        Returns:
            Cadena con hora y fecha formateadas, o None si no tiene zona.
        """
        tz_str = self.get_timezone(user_id)
        if not tz_str:
            return None
        tz = ZoneInfo(tz_str)
        now = datetime.now(tz)
        return now.strftime("%H:%M:%S - %d/%m/%Y")

    def get_time_in(self, timezone_str: str) -> tuple[str, str] | None:
        """Obtiene hora y fecha actual en una zona horaria arbitraria.

        Args:
            timezone_str: Nombre de zona horaria válido.

        Returns:
            Tupla (hora, fecha) o None si la zona no es válida.
        """
        tz_list = _list_timezones()
        if timezone_str not in tz_list:
            return None
        tz = ZoneInfo(timezone_str)
        now = datetime.now(tz)
        return now.strftime("%H:%M:%S"), now.strftime("%d/%m/%Y")
