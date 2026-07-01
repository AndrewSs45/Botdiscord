"""Seguimiento de uso de comandos.

Registra cada comando ejecutado, con historial cronológico
y estadísticas agregadas por comando y por usuario.
"""
from utils.persistence import AsyncPersistence, now_iso
import config


_MAX_HISTORIAL = 200


class CommandTracker:
    """Lleva el registro de todos los comandos ejecutados en el bot.

    Almacena datos en el JSON compartido bajo las claves ``comandos``
    (estadísticas agregadas) e ``historial`` (lista cronológica).
    """

    def __init__(self, persistence: AsyncPersistence):
        self._store = persistence

    def registrar_comando(self, comando: str, usuario_id: int, canal: str = ""):
        """Registra la ejecución de un comando.

        Args:
            comando: Nombre del comando ejecutado.
            usuario_id: ID de Discord del usuario que lo ejecutó.
            canal: Nombre del canal donde se ejecutó.
        """
        datos = self._store.data

        cmd_data = datos.setdefault("comandos", {}).setdefault(comando, {"total": 0, "por_usuario": {}})
        cmd_data["total"] += 1
        uid = str(usuario_id)
        cmd_data["por_usuario"][uid] = cmd_data["por_usuario"].get(uid, 0) + 1

        historial = datos.setdefault("historial", [])
        historial.append({
            "comando": comando,
            "usuario": uid,
            "canal": canal,
            "ts": now_iso(),
        })

        if len(historial) > _MAX_HISTORIAL:
            datos["historial"] = historial[-_MAX_HISTORIAL:]

        self._store.mark_dirty()

    def obtener_stats(self) -> str:
        """Genera estadísticas de comandos más usados.

        Returns:
            Cadena formateada con total de comandos y top 5.
        """
        comandos = self._store.data.get("comandos", {})
        if not comandos:
            return ""

        sorted_cmds = sorted(comandos.items(), key=lambda x: -x[1]["total"])
        total = sum(c["total"] for c in comandos.values())

        lineas = [f"\n**Comandos ejecutados:** {total} total"]
        for nombre, info in sorted_cmds[:5]:
            lineas.append(f"- **{config.BOT_PREFIX}{nombre}**: {info['total']} veces")

        return "\n".join(lineas)
