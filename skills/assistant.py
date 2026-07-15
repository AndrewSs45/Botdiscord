"""Asistente conversacional con IA vía NVIDIA API.

Maneja el historial de conversación por usuario, realiza llamadas
a modelos de lenguaje con streaming y fallback automático entre
múltiples modelos en caso de error.
"""
import asyncio
import json
import logging

from openai import AsyncOpenAI

import config
from utils.helpers import limpiar_menciones_discord

log = logging.getLogger("assistant")


_SAFETY_KEYS = {"User Safety", "Response Safety", "user_safety", "response_safety"}


def _es_respuesta_safety(texto: str) -> bool:
    try:
        parsed = json.loads(texto)
        if isinstance(parsed, dict) and _SAFETY_KEYS & set(parsed.keys()):
            log.warning("Respuesta safety detectada y descartada: %s", texto[:120])
            return True
    except (json.JSONDecodeError, ValueError):
        pass
    return False


_MAX_HISTORY = 10
_STREAM_TIMEOUT = 30
_CHUNK_TIMEOUT = 10


class AIAssistant:
    """Cliente de IA conversacional con streaming y failover entre modelos.

    Mantiene un historial por usuario (hasta ``_MAX_HISTORY`` mensajes)
    e intenta modelos en orden de prioridad ante fallos.
    """

    def __init__(self):
        self.conversation_history: dict[int, list[dict]] = {}
        self.modelo_actual = config.AI_MODEL

    async def obtener_respuesta(self, mensaje: str, user_id: int, contexto: str = "") -> str:
        """Obtiene una respuesta de IA para un mensaje de usuario.

        Args:
            mensaje: Texto del mensaje (se limpian menciones internamente).
            user_id: ID de Discord para mantener el historial separado.
            contexto: Información adicional (canal, etc.) para el prompt de sistema.

        Returns:
            Texto de la respuesta generada, o mensaje de error si falla todo.
        """
        try:
            mensaje_limpio = limpiar_menciones_discord(mensaje)
            history = self.conversation_history.setdefault(user_id, [])
            history.append({"role": "user", "content": mensaje_limpio})

            if len(history) > _MAX_HISTORY:
                self.conversation_history[user_id] = history[-_MAX_HISTORY:]

            system_prompt = (
                "Eres un asistente IA amigable y útil en Discord.\n"
                "Puedes ayudar respondiendo preguntas, dando información, "
                "manteniendo conversaciones y entreteniendo.\n"
                "Sé conciso pero informativo.\n"
                f"Contexto: {contexto or 'Sin contexto adicional'}"
            )

            mensajes = [{"role": "system", "content": system_prompt}]
            mensajes.extend(self.conversation_history[user_id])

            modelos = [self.modelo_actual] + config.AI_MODELS_FALLBACK

            for intento, modelo in enumerate(modelos, 1):
                respuesta = await self._intentar_modelo(modelo, mensajes, intento, len(modelos))
                if respuesta:
                    self.modelo_actual = modelo
                    self.conversation_history[user_id].append(
                        {"role": "assistant", "content": respuesta}
                    )
                    if len(respuesta) > 1990:
                        respuesta = respuesta[:1990] + "..."
                    return respuesta

            return "No se pudo obtener respuesta de IA. Intenta de nuevo."

        except Exception as e:
            log.error("Error general en AIAssistant: %s: %s", type(e).__name__, e)
            return "Ocurrió un error al procesar tu mensaje. Intenta de nuevo."

    async def _intentar_modelo(self, modelo: str, mensajes: list, intento: int, total: int) -> str | None:
        """Intenta obtener respuesta de un modelo específico con streaming.

        Args:
            modelo: Nombre del modelo en la API de NVIDIA.
            mensajes: Lista de mensajes del historial (formato OpenAI).
            intento: Número de intento actual (para logging).
            total: Total de intentos (para logging).

        Returns:
            Texto completo de la respuesta, o None si falla.
        """
        try:
            api_key = config.NVIDIA_API_KEY
            if "nemotron" in modelo.lower():
                api_key = config.NEMOTRON_API_KEY or config.NVIDIA_API_KEY

            client = AsyncOpenAI(base_url=config.NVIDIA_BASE_URL, api_key=api_key)

            completion = await asyncio.wait_for(
                client.chat.completions.create(
                    model=modelo,
                    messages=mensajes,
                    temperature=config.AI_TEMPERATURE,
                    top_p=config.AI_TOP_P,
                    max_tokens=config.AI_MAX_TOKENS,
                    stream=True,
                ),
                timeout=_STREAM_TIMEOUT,
            )

            respuesta = []
            async for chunk in completion:
                if not chunk.choices:
                    continue
                content = chunk.choices[0].delta.content
                if content:
                    respuesta.append(content)

            texto = "".join(respuesta)
            if texto and not _es_respuesta_safety(texto):
                return texto

        except asyncio.TimeoutError:
            log.warning("Timeout en modelo %s (%s/%s)", modelo, intento, total)
        except (openai.APIError, openai.APIConnectionError, openai.RateLimitError, openai.APITimeoutError) as e:
            log.error("Error en modelo %s (%s/%s): %s: %s", modelo, intento, total, type(e).__name__, e)
            if "DEGRADED" not in str(e):
                await asyncio.sleep(config.REINTENTO_DELAY)

        return None

    _DANGEROUS_PATTERNS = [
        "make a bomb", "how to kill", "how to harm",
        "bomb making", "explosive device",
    ]

    @classmethod
    def _safety_filter(cls, text: str) -> bool:
        text_lower = text.lower()
        for pattern in cls._DANGEROUS_PATTERNS:
            if pattern in text_lower:
                return True
        return _es_respuesta_safety(text)

    def limpiar_historial_usuario(self, user_id: int):
        """Elimina el historial de conversación de un usuario.

        Args:
            user_id: ID de Discord del usuario.
        """
        self.conversation_history.pop(user_id, None)
