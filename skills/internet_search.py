"""Skill de búsqueda en Internet.

Delega la consulta a la función :func:`utils.helpers.buscar_en_internet`
que utiliza la API de Serper para obtener resultados de Google.
"""
from utils.helpers import buscar_en_internet


class InternetSearchSkill:
    """Skill para buscar información en Internet vía Serper API."""

    def __init__(self):
        self.nombre = "Internet Search"
        self.descripcion = "Busca información en Internet"

    async def ejecutar(self, query: str) -> str:
        """Ejecuta una búsqueda en Google y retorna resultados formateados.

        Args:
            query: Término de búsqueda.

        Returns:
            Cadena con resultados (título, snippet, URL) o mensaje de error.
        """
        return await buscar_en_internet(query)
