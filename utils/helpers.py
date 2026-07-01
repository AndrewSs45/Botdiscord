"""Funciones auxiliares de uso general.

Incluye búsqueda en Internet vía Serper API, formateo de hora/fecha
y limpieza de menciones de Discord de texto.
"""
import re
from datetime import datetime

import aiohttp

from config import SERPER_API_KEY

_MENCION_REGEX = re.compile(r"<@!?\d+>|<@&\d+>|<#\d+>")


async def buscar_en_internet(query: str, max_resultados: int = 3) -> str:
    """Realiza una búsqueda en Google usando la API de Serper.

    Args:
        query: Término de búsqueda.
        max_resultados: Cantidad máxima de resultados a retornar (default 3).

    Returns:
        Cadena con resultados formateados o mensaje de error.
    """
    if not SERPER_API_KEY:
        return "SERPER_API_KEY no configurada en .env"

    payload = {"q": query}
    headers = {
        "X-API-KEY": SERPER_API_KEY,
        "Content-Type": "application/json",
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://google.serper.dev/search",
                json=payload,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=15),
            ) as resp:
                if resp.status != 200:
                    return f"Error en búsqueda: HTTP {resp.status}"
                data = await resp.json()
    except (aiohttp.ClientError, TimeoutError) as e:
        return f"Error de conexión en búsqueda: {e}"

    resultados = []
    for result in (data.get("organic") or [])[:max_resultados]:
        titulo = result.get("title", "")
        snippet = result.get("snippet", "")
        url = result.get("link", "")
        if titulo and snippet:
            resultados.append(f"**{titulo}**\n{snippet}\n{url}")

    return "\n\n".join(resultados) if resultados else "No se encontraron resultados"


def obtener_hora_actual() -> str:
    """Retorna la hora actual del sistema en formato HH:MM:SS."""
    return datetime.now().strftime("%H:%M:%S")


def obtener_fecha_actual() -> str:
    """Retorna la fecha actual del sistema en formato DD/MM/AAAA."""
    return datetime.now().strftime("%d/%m/%Y")


def limpiar_menciones_discord(texto: str) -> str:
    """Elimina menciones de usuarios, roles y canales de un texto.

    Args:
        texto: Texto que puede contener menciones (<@123>, <#456>, etc.).

    Returns:
        Texto sin menciones, con espacios sobrantes recortados.
    """
    return _MENCION_REGEX.sub("", texto).strip()
