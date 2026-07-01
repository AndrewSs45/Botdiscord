"""Skill de hora y fecha con soporte de zonas horarias.

Permite consultar la hora actual del sistema o la hora en cualquier
zona horaria válida del estándar IANA (ej. "America/Mexico_City").
"""
from datetime import datetime
from zoneinfo import ZoneInfo

from utils.helpers import obtener_hora_actual, obtener_fecha_actual


class TimeSkill:
    """Skill para obtener la hora y fecha actual, opcionalmente en una zona horaria específica."""

    def __init__(self):
        self.nombre = "Time"
        self.descripcion = "Obtiene la hora y fecha actual"

    async def ejecutar(self, timezone: str | None = None) -> str:
        """Obtiene la hora y fecha actual.

        Args:
            timezone: Zona horaria IANA opcional (ej. "Europe/Madrid").
                      Si es None, usa la hora local del servidor.

        Returns:
            Cadena formateada con hora y fecha.
        """
        if timezone:
            try:
                tz = ZoneInfo(timezone)
                now = datetime.now(tz)
                hora = now.strftime("%H:%M:%S")
                fecha = now.strftime("%d/%m/%Y")
                return f"⏰ **Hora en {timezone}:** {hora}\n📅 **Fecha:** {fecha}"
            except (KeyError, ValueError):
                return f"Zona horaria '{timezone}' no válida."

        hora = obtener_hora_actual()
        fecha = obtener_fecha_actual()
        return f"⏰ **Hora actual:** {hora}\n📅 **Fecha:** {fecha}"
