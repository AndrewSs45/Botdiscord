"""Sistema de aprendizaje y estadísticas de uso.

Registra temas de conversación populares y usuarios frecuentes
para ofrecer estadísticas y personalización.
"""
from utils.persistence import AsyncPersistence


class LearningSystem:
    """Registra métricas de uso: temas populares y usuarios activos.

    Los datos se persisten en el almacenamiento JSON compartido bajo
    las claves ``temas_favoritos`` y ``usuarios_frecuentes``.
    """

    def __init__(self, persistence: AsyncPersistence):
        self._store = persistence

    def registrar_tema(self, tema: str, user_id: int):
        """Incrementa el contador de un tema asociado a un usuario.

        Args:
            tema: Texto del tema (primeras palabras del mensaje).
            user_id: ID de Discord del usuario que mencionó el tema.
        """
        temas = self._store.data.setdefault("temas_favoritos", {})
        temas[tema] = temas.get(tema, 0) + 1
        self._store.mark_dirty()

    def registrar_usuario(self, user_id: int, mensajes: int = 1):
        """Registra actividad de un usuario.

        Args:
            user_id: ID de Discord del usuario.
            mensajes: Cantidad de mensajes a contabilizar (default 1).
        """
        uid = str(user_id)
        usuarios = self._store.data.setdefault("usuarios_frecuentes", {})
        usuarios[uid] = usuarios.get(uid, 0) + mensajes
        self._store.mark_dirty()

    def obtener_estadisticas(self) -> str:
        """Genera un resumen de estadísticas del bot.

        Returns:
            Cadena formateada con temas populares y cantidad de usuarios activos.
        """
        datos = self._store.data
        lineas = ["**Estadisticas del Bot**"]

        temas = datos.get("temas_favoritos", {})
        if temas:
            lineas.append("\n**Temas populares:**")
            for tema, count in sorted(temas.items(), key=lambda x: -x[1])[:5]:
                lineas.append(f"- {tema}: {count} menciones")

        usuarios = datos.get("usuarios_frecuentes", {})
        if usuarios:
            lineas.append(f"\n**Usuarios activos:** {len(usuarios)}")

        return "\n".join(lineas)
