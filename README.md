# Bot IA Discord

Bot de Discord avanzado con inteligencia artificial conversacional, búsqueda en Internet, clima, zonas horarias, reproducción de música y más.

## Características

- **IA Conversacional** — Chat con IA vía NVIDIA API con streaming y fallback automático entre modelos.
- **Saludo Automático** — Detecta saludos ("hola", "buenas", "hey") y responde con el nombre del usuario sin necesidad de mencionar al bot.
- **Búsqueda en Internet** — Busca información en tiempo real usando la API de Serper (Google).
- **Clima** — Temperatura y viento de cualquier ciudad usando Open-Meteo (sin API key).
- **Zonas Horarias** — Consulta la hora local o en cualquier zona del mundo. Cada usuario puede guardar su zona preferida.
- **Preferencias de Usuario** — Persistencia de zona horaria por usuario.
- **Música** — Reproduce audio desde YouTube con cola, loop (off/one/all), shuffle y control de volumen.
- **Sistema de Aprendizaje** — Registra temas populares y usuarios activos.
- **Seguimiento de Comandos** — Estadísticas de uso por comando y por usuario.
- **Interacción con otros bots** — Puede conversar con otros bots en Discord.
- **Extensible** — Sistema modular de skills y comandos (Cogs).

## Requisitos

- **Python 3.10+** (por el uso de `zoneinfo` y `str | None`)
- **ffmpeg** (para reproducción de música)
- Cuenta de Discord con un bot creado
- API Key de NVIDIA (para la IA conversacional)

## Instalación

### 1. Clonar el proyecto

```bash
git clone <url-del-repo>
cd Botdiscord
```

### 2. Crear y activar entorno virtual

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

Copia el archivo de ejemplo y edítalo:

```bash
cp .env.example .env
```

Edita `.env` con tus credenciales (ver sección de credenciales abajo):

```env
DISCORD_TOKEN=tu_token_aqui
NVIDIA_API_KEY=tu_api_key_aqui
BOT_PREFIX=!
```

### 5. Obtener credenciales

#### Token de Discord
1. Ve a [Discord Developer Portal](https://discord.com/developers/applications).
2. Crea una nueva aplicación y ve a la sección "Bot".
3. Haz clic en "Add Bot" y copia el token.
4. En OAuth2 > URL Generator, selecciona:
   - Scopes: `bot`
   - Permissions: `Send Messages`, `Read Messages/View Channels`, `Connect`, `Speak` (para música)
5. Usa la URL generada para invitar el bot a tu servidor.

#### NVIDIA API Key
1. Ve a [NVIDIA API](https://build.nvidia.com/) y regístrate.
2. Ve a tu perfil > "Keys" y copia tu API Key.

#### Serper API Key (opcional, para búsqueda web)
1. Ve a [Serper.dev](https://serper.dev/) y regístrate.
2. Copia tu API key en `SERPER_API_KEY` en `.env`.

### 6. Ejecutar el bot

```bash
python main.py
```

Si todo funciona, verás:
```
Bot conectado como TuBot#1234
Sirviendo en 1 servidores
```

## Comandos

### Conversación con IA
| Comando | Descripción |
|---------|-------------|
| `@Bot <mensaje>` | Habla con la IA mencionando al bot |
| `hola` / `buenas` / etc. | Saludo automático (responde sin necesidad de mención) |
| `!limpiar_chat` | Limpia el historial de conversación |

### Búsqueda y Clima
| Comando | Descripción |
|---------|-------------|
| `!buscar <término>` | Busca información en Google |
| `!clima <ciudad>` | Clima actual de una ciudad |

### Hora y Zona Horaria
| Comando | Descripción |
|---------|-------------|
| `!hora` | Hora actual (usa tu zona guardada si existe) |
| `!hora <zona>` | Hora en una zona específica, ej: `!hora Europe/Madrid` |
| `!mi_zona` | Muestra tu zona horaria guardada |
| `!mi_zona <zona>` | Guarda tu zona horaria, ej: `!mi_zona America/Mexico_City` |
| `!hora_en <zona>` | Hora actual en cualquier zona, ej: `!hora_en Asia/Tokyo` |

### Música
| Comando | Descripción |
|---------|-------------|
| `!play <canción>` | Reproduce o encola una canción desde YouTube |
| `!skip` | Salta a la siguiente canción |
| `!stop` | Detiene la música y desconecta |
| `!pause` | Pausa la reproducción |
| `!resume` | Reanuda la reproducción |
| `!queue` | Muestra la cola de reproducción |
| `!nowplaying` | Muestra la canción actual |
| `!loop off/one/all` | Cambia modo de loop |
| `!shuffle` | Aleatoriza la cola |
| `!volume <0-100>` | Ajusta el volumen |

### Utilidad
| Comando | Descripción |
|---------|-------------|
| `!estadisticas` | Estadísticas del bot |
| `!ping` | Latencia del bot |
| `!ayuda` | Lista completa de comandos |

## Variables de Entorno

### Obligatorias
| Variable | Descripción |
|----------|-------------|
| `DISCORD_TOKEN` | Token del bot de Discord |
| `NVIDIA_API_KEY` | API Key de NVIDIA para modelos de IA |

### Opcionales
| Variable | Descripción | Defecto |
|----------|-------------|---------|
| `BOT_PREFIX` | Prefijo de comandos | `!` |
| `BOT_NAME` | Nombre del bot | `AssistentIA` |
| `AI_MODEL` | Modelo de IA principal | `mistralai/mixtral-8x7b-instruct-v0.1` |
| `AI_TEMPERATURE` | Temperatura del modelo (0-2) | `1` |
| `AI_TOP_P` | Top-p sampling | `0.95` |
| `AI_MAX_TOKENS` | Máximo de tokens por respuesta | `16384` |
| `AI_THINKING` | Activar modo thinking | `False` |
| `SERPER_API_KEY` | API Key para búsqueda web | — |
| `WEATHER_API_KEY` | (reservado) API Key de clima | — |
| `GOOGLE_SEARCH_API_KEY` | (reservado) API Key de Google | — |
| `NEMOTRON_API_KEY` | API Key alternativa para Nemotron | — |
| `PERSISTENCE_INTERVAL` | Segundos entre guardados automáticos | `30` |
| `MUSIC_VOLUME_DEFAULT` | Volumen por defecto (0-100) | `50` |

## Estructura del Proyecto

```
Botdiscord/
├── main.py                    # Punto de entrada, eventos, comandos globales
├── config.py                  # Configuración desde variables de entorno
├── requirements.txt           # Dependencias
├── .env.example               # Plantilla de variables de entorno
├── .env                       # Variables de entorno (NO incluir en git)
├── bot_learning.json          # Persistencia: aprendizaje, preferencias, estadísticas
├── install.sh                 # Script de instalación rápida
│
├── skills/                    # Módulo de habilidades (SRP)
│   ├── __init__.py
│   ├── assistant.py           # IA conversacional (NVIDIA API, streaming)
│   ├── greeting.py            # Detección automática de saludos
│   ├── weather.py             # Clima (Open-Meteo, sin API key)
│   ├── time_skill.py          # Hora y fecha con soporte de zonas horarias
│   ├── internet_search.py     # Búsqueda web (Serper API)
│   ├── user_preferences.py    # Preferencias por usuario (zona horaria)
│   ├── learning.py            # Sistema de aprendizaje (temas, usuarios)
│   ├── command_tracker.py     # Seguimiento de comandos
│   └── music.py               # Reproductor de música (YouTube, cola, loop)
│
├── commands/                  # Módulo de comandos (Cogs)
│   ├── __init__.py
│   ├── utility.py             # Utilidad: buscar, clima, hora, zonas, stats
│   └── music_commands.py      # Música: play, skip, queue, loop, volume
│
└── utils/                     # Utilidades
    ├── __init__.py
    ├── persistence.py         # Persistencia asíncrona JSON con auto-save
    ├── helpers.py             # Helpers: búsqueda web, hora, limpieza de texto
    └── logger.py              # Logging a stdout
```

## Personalización

### Agregar una nueva skill

1. Crea un archivo en `skills/` con una clase que tenga un método `async ejecutar(...) -> str`.
2. Importa y usa la skill desde un comando en `commands/`.

### Cambiar el modelo de IA

En `.env`:
```env
AI_MODEL=nvidia/llama-3.1-nemotron-safety-guard-8b-v3
```

### Ajustar parámetros de IA

```env
AI_TEMPERATURE=0.7    # Menor = más determinístico
AI_TOP_P=0.9          # Diversidad de respuestas
AI_MAX_TOKENS=8192    # Longitud máxima
```

## Debugging

Ejecuta el bot con logging detallado:

```bash
python main.py
```

Los logs se muestran en stdout con formato:
```
HH:MM:SS [LEVEL] módulo: mensaje
```

### Problemas comunes

**"Token inválido"** — Verifica que `DISCORD_TOKEN` en `.env` sea correcto y que el bot esté invitado al servidor.

**"API Key inválida"** — Verifica `NVIDIA_API_KEY`. La API key debe estar activa en build.nvidia.com.

**Bot no responde** — Verifica que el bot tenga permisos de "Leer mensajes" y "Enviar mensajes" en el canal. Asegúrate de que `intents.message_content = True` en `main.py`.

**La música no funciona** — Asegúrate de tener `ffmpeg` instalado en el sistema. Verifica que el bot tenga permisos `Connect` y `Speak`.

## Seguridad

- Nunca compartas tu archivo `.env`.
- El `.gitignore` ya excluye `.env`, `bot_learning.json` y `__pycache__/`.
- Regenera las credenciales si sospechas que fueron comprometidas.
- Las API keys en el código son de ejemplo; reemplázalas con las tuyas.

## Licencia

Uso libre. Modifica según tus necesidades.
