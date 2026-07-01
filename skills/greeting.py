"""Detección automática de saludos y generación de respuestas.

Este módulo permite al bot detectar cuando un usuario lo saluda
sin necesidad de mencionarlo explícitamente, y responde con un
mensaje personalizado usando el nombre de la persona.
"""
import re
import random


_GREETINGS = [
    "hola", "buenas", "buen[ao]s?", "hey", "hello", "hi",
    "que tal", "qué tal", "como estas?", "cómo estás?",
    "buen día", "buenos días", "buenas tardes", "buenas noches",
    "q[úu]e hay", "qui[úu]bole?", "saludos", "epale?", "epa",
]

_PATTERN = re.compile(
    r"^\s*(" + "|".join(_GREETINGS) + r")\s*[!\.]?\s*$",
    re.IGNORECASE,
)

_GREETING_RESPONSES = [
    "¡Hola {name}! ¿En qué puedo ayudarte?",
    "¡Hey {name}! ¿Cómo estás?",
    "¡Buenas {name}! ¿Todo bien?",
    "¡Hola {name}! Encantado de verte.",
    "¡Hola {name}! Cuéntame, ¿qué necesitas?",
    "¡Qué tal {name}! ¿En qué te ayudo?",
]


def detectar_saludo(mensaje: str) -> bool:
    """Verifica si un mensaje es un saludo.

    Args:
        mensaje: Texto del mensaje a analizar.

    Returns:
        True si el mensaje coincide con algún patrón de saludo.
    """
    return bool(_PATTERN.match(mensaje.strip()))


def obtener_respuesta_saludo(member_name: str, mention: str) -> str:
    """Genera una respuesta de saludo personalizada.

    Args:
        member_name: Nombre visible del usuario en el servidor.
        mention: Mención de Discord del usuario (ej. <@123456>).

    Returns:
        Frase de saludo con el nombre del usuario insertado.
    """
    frase = random.choice(_GREETING_RESPONSES)
    return frase.format(name=member_name)
