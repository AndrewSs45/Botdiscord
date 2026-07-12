# Discord AI Bot

Advanced Discord bot with conversational artificial intelligence, Internet search, weather, time zones, music playback and more.

## Features

- **Conversational AI** — Chat with AI via NVIDIA API with streaming and automatic fallback between models.
- **Auto Greeting** — Detects greetings ("hello", "hi", "hey") and responds with the user's name without needing to mention the bot.
- **Internet Search** — Search real-time information using Serper API (Google).
- **Weather** — Temperature and wind for any city using Open-Meteo (no API key required).
- **Time Zones** — Check local time or time anywhere in the world. Each user can save their preferred timezone.
- **User Preferences** — Per-user timezone persistence.
- **Music** — Play audio from YouTube with queue, loop (off/one/all), shuffle and volume control. *(audio only, does not play videos)*
- **Moderation** — Kick, ban, softban, hackban, mute, warn, message cleanup and infraction logging.
- **Learning System** — Tracks popular topics and active users.
- **Command Tracking** — Usage statistics per command and per user.
- **Interaction with other bots** — Can converse with other bots on Discord.
- **Extensible** — Modular skill and command system (Cogs).

## Requirements

- **Python 3.10+** (for `zoneinfo` and `str | None` support)
- **ffmpeg** (for music playback)
- Discord account with a created bot
- NVIDIA API Key (for conversational AI)

## Installation

### 1. Clone the project

```bash
git clone <repo-url>
cd Botdiscord
```

### 2. Create and activate virtual environment

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Copy the example file and edit it:

```bash
cp .env.example .env
```

Edit `.env` with your credentials (see credentials section below):

```env
DISCORD_TOKEN=your_discord_token_here
NVIDIA_API_KEY=your_nvidia_api_key_here
BOT_PREFIX=!
```

### 5. Get credentials

#### Discord Token
1. Go to [Discord Developer Portal](https://discord.com/developers/applications).
2. Create a new application and go to the "Bot" section.
3. Click "Add Bot" and copy the token.
4. In OAuth2 > URL Generator, select:
   - Scopes: `bot`
   - Permissions: `Send Messages`, `Read Messages/View Channels`, `Connect`, `Speak` (for music)
5. Use the generated URL to invite the bot to your server.

#### NVIDIA API Key
1. Go to [NVIDIA API](https://build.nvidia.com/) and register.
2. Go to your profile > "Keys" and copy your API Key.

#### Serper API Key (optional, for web search)
1. Go to [Serper.dev](https://serper.dev/) and register.
2. Copy your API key into `SERPER_API_KEY` in `.env`.

### 6. Run the bot

```bash
python main.py
```

If everything works, you will see:
```
Bot connected as YourBot#1234
Serving in 1 servers
```

## Commands

### AI Conversation
| Command | Description |
|---------|-------------|
| `@Bot <message>` | Talk to the AI by mentioning the bot |
| `hello` / `hi` / etc. | Auto greeting (responds without mention) |
| `!clear_chat` | Clears conversation history |

### Search and Weather
| Command | Description |
|---------|-------------|
| `!search <term>` | Search Google for information |
| `!weather <city>` | Current weather for a city |

### Time and Timezone
| Command | Description |
|---------|-------------|
| `!time` | Current time (uses saved timezone if set) |
| `!time <zone>` | Time in a specific zone, e.g. `!time Europe/London` |
| `!my_zone` | Shows your saved timezone |
| `!my_zone <zone>` | Saves your timezone, e.g. `!my_zone America/New_York` |
| `!time_in <zone>` | Current time in any zone, e.g. `!time_in Asia/Tokyo` |

### Music
| Command | Description |
|---------|-------------|
| `!play <song>` | Play or queue a song from YouTube (audio only) |
| `!skip` | Skip to the next song |
| `!stop` | Stop music and disconnect |
| `!pause` | Pause playback |
| `!resume` | Resume playback |
| `!queue` | Show the playback queue |
| `!nowplaying` | Show current song |
| `!loop off/one/all` | Change loop mode |
| `!shuffle` | Shuffle the queue |
| `!volume <0-100>` | Adjust volume |

### Moderation
| Command | Description | Permissions |
|---------|-------------|-------------|
| `!kick @user [reason]` | Kick a member | `kick_members` |
| `!ban @user [days] [reason]` | Ban with optional message deletion | `ban_members` |
| `!softban @user [reason]` | Ban and unban (deletes messages) | `ban_members` |
| `!hackban <id> [reason]` | Ban by ID (user not in server) | `ban_members` |
| `!unban <id> [reason]` | Unban by ID | `ban_members` |
| `!mute @user [reason]` | Mute a member (auto-creates Muted role) | `manage_roles` |
| `!unmute @user` | Unmute a member | `manage_roles` |
| `!warn @user [reason]` | Warn a member (persistent) | `manage_messages` |
| `!infractions @user` | Show user warnings | `manage_messages` |
| `!clear_warns @user` | Clear warnings (admin only) | `administrator` |
| `!clean [amount]` | Delete channel messages (max 100) | `manage_messages` |
| `!modlog [amount]` | Moderation action log | `administrator` |
| `!modstats` | Moderation statistics | `administrator` |

### Utility
| Command | Description |
|---------|-------------|
| `!stats` | Bot statistics |
| `!ping` | Bot latency |
| `!help` | Full command list |

## Environment Variables

### Required
| Variable | Description |
|----------|-------------|
| `DISCORD_TOKEN` | Discord bot token |
| `NVIDIA_API_KEY` | NVIDIA API Key for AI models |

### Optional
| Variable | Description | Default |
|----------|-------------|---------|
| `BOT_PREFIX` | Command prefix | `!` |
| `BOT_NAME` | Bot name | `AssistentIA` |
| `AI_MODEL` | Main AI model | `mistralai/mixtral-8x7b-instruct-v0.1` |
| `AI_TEMPERATURE` | Model temperature (0-2) | `1` |
| `AI_TOP_P` | Top-p sampling | `0.95` |
| `AI_MAX_TOKENS` | Max tokens per response | `16384` |
| `AI_THINKING` | Enable thinking mode | `False` |
| `SERPER_API_KEY` | API Key for web search | — |
| `WEATHER_API_KEY` | (reserved) Weather API Key | — |
| `GOOGLE_SEARCH_API_KEY` | (reserved) Google API Key | — |
| `NEMOTRON_API_KEY` | Alternative API Key for Nemotron | — |
| `PERSISTENCE_INTERVAL` | Seconds between auto-saves | `30` |
| `MUSIC_VOLUME_DEFAULT` | Default volume (0-100) | `50` |

## Project Structure

```
Botdiscord/
├── main.py                    # Entry point, events, global commands
├── config.py                  # Configuration from environment variables
├── requirements.txt           # Dependencies
├── .env.example               # Environment variable template
├── .env                       # Environment variables (DO NOT commit)
├── bot_learning.json          # Persistence: learning, preferences, stats
├── install.sh                 # Quick installation script
│
├── skills/                    # Skills module (SRP)
│   ├── __init__.py
│   ├── assistant.py           # Conversational AI (NVIDIA API, streaming)
│   ├── greeting.py            # Auto greeting detection
│   ├── weather.py             # Weather (Open-Meteo, no API key)
│   ├── time_skill.py          # Time and date with timezone support
│   ├── internet_search.py     # Web search (Serper API)
│   ├── user_preferences.py    # Per-user preferences (timezone)
│   ├── learning.py            # Learning system (topics, users)
│   ├── command_tracker.py     # Command tracking
│   └── music.py               # Music player (YouTube, queue, loop)
│
├── commands/                  # Commands module (Cogs)
│   ├── __init__.py
│   ├── utility.py             # Utility: search, weather, time, zones, stats
│   └── music_commands.py      # Music: play, skip, queue, loop, volume
│
└── utils/                     # Utilities
    ├── __init__.py
    ├── persistence.py         # Async JSON persistence with auto-save
    ├── helpers.py             # Helpers: web search, time, text cleaning
    └── logger.py              # stdout logging
```

## Customization

### Adding a new skill

1. Create a file in `skills/` with a class that has an `async ejecutar(...) -> str` method.
2. Import and use the skill from a command in `commands/`.

### Changing the AI model

In `.env`:
```env
AI_MODEL=nvidia/llama-3.1-nemotron-safety-guard-8b-v3
```

### Adjusting AI parameters

```env
AI_TEMPERATURE=0.7    # Lower = more deterministic
AI_TOP_P=0.9          # Response diversity
AI_MAX_TOKENS=8192    # Maximum length
```

## Debugging

Run the bot with detailed logging:

```bash
python main.py
```

Logs are displayed on stdout with format:
```
HH:MM:SS [LEVEL] module: message
```

### Common issues

**"Invalid token"** — Verify that `DISCORD_TOKEN` in `.env` is correct and that the bot is invited to the server.

**"Invalid API Key"** — Verify `NVIDIA_API_KEY`. The API key must be active on build.nvidia.com.

**Bot not responding** — Check that the bot has "Read Messages" and "Send Messages" permissions in the channel. Make sure `intents.message_content = True` in `main.py`.

**Music not working** — Make sure `ffmpeg` is installed on the system. Verify the bot has `Connect` and `Speak` permissions.

**Note about video playback**: The bot plays only **audio** from YouTube. It cannot play video since Discord does not natively support it. If you need to send videos, use `!search` to find links.

## Security

- Never share your `.env` file.
- The `.gitignore` already excludes `.env`, `bot_learning.json` and `__pycache__/`.
- Regenerate credentials if you suspect they have been compromised.
- API keys in the code are examples; replace them with your own.

## License

Free to use. Modify as needed.
