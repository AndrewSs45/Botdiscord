"""Configuración centralizada del bot.

Todas las constantes se cargan desde variables de entorno (archivo .env)
con valores por defecto sensatos. Valida que las claves obligatorias
(DISCORD_TOKEN, NVIDIA_API_KEY) estén presentes al importar.
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Discord
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
BOT_PREFIX = os.getenv("BOT_PREFIX", "!")
BOT_NAME = os.getenv("BOT_NAME", "AssistentIA")

# NVIDIA / OpenAI
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")
NVIDIA_BASE_URL = "https://integrate.api.nvidia.com/v1"
AI_MODEL = os.getenv("AI_MODEL", "mistralai/mixtral-8x7b-instruct-v0.1")
AI_MODELS_FALLBACK = [
    "meta-llama/llama-3-70b-instruct",
]

# AI params
AI_TEMPERATURE = float(os.getenv("AI_TEMPERATURE", 1))
AI_TOP_P = float(os.getenv("AI_TOP_P", 0.95))
AI_MAX_TOKENS = int(os.getenv("AI_MAX_TOKENS", 16384))
AI_THINKING = os.getenv("AI_THINKING", "False").lower() == "true"
MAX_REINTENTOS = 3
REINTENTO_DELAY = 2

# Persistence
PERSISTENCE_INTERVAL = 30

# External APIs (optional)
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
SERPER_API_KEY = os.getenv("SERPER_API_KEY")
GOOGLE_SEARCH_API_KEY = os.getenv("GOOGLE_SEARCH_API_KEY")
NEMOTRON_API_KEY = os.getenv("NEMOTRON_API_KEY")

# Music
MUSIC_VOLUME_DEFAULT = 50

# Validations
if not DISCORD_TOKEN:
    raise ValueError("DISCORD_TOKEN no configurado en .env")
if not NVIDIA_API_KEY:
    raise ValueError("NVIDIA_API_KEY no configurado en .env")
