"""Configuración de logging con salida a stdout.

Proporciona una función factory para crear loggers con formato
consistente (timestamp, nivel, nombre del módulo).
"""
import logging
import sys

_LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
_LOG_DATE = "%H:%M:%S"


def setup_logger(name: str = "bot", level: int = logging.DEBUG) -> logging.Logger:
    """Crea y configura un logger con salida a stdout.

    Args:
        name: Nombre del logger (default "bot").
        level: Nivel de logging (default DEBUG).

    Returns:
        Instancia de logging.Logger configurada.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.handlers.clear()

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)
    handler.setFormatter(logging.Formatter(_LOG_FORMAT, _LOG_DATE))
    logger.addHandler(handler)

    return logger
