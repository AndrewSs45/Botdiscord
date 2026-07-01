# Guia Rapida - Bot IA Discord

Pon el bot en funcionamiento en menos de 5 minutos.

## Requisitos previos

- Python 3.10+
- ffmpeg (solo para musica)
- Un servidor de Discord donde tengas permisos para invitar bots

## Paso 1: Obtener credenciales (2 min)

### Token de Discord
1. Abre https://discord.com/developers/applications
2. "New Application" -> ponle nombre -> "Create"
3. "Bot" -> "Add Bot" -> "Copy" (copia el token)
4. "OAuth2" > "URL Generator":
   - Scopes: `bot`
   - Permissions: `Send Messages`, `Read Messages/View Channels`, `Connect`, `Speak`
   - Abre la URL generada e invita el bot a tu servidor

### NVIDIA API Key
1. Abre https://build.nvidia.com/
2. Registrate o inicia sesion
3. Tu perfil > "Keys" > copia la API Key

## Paso 2: Configurar el proyecto (1 min)

```bash
cd Botdiscord

# Con el instalador automatico (Linux/Mac):
bash install.sh

# O manualmente:
python3 -m venv venv
source venv/bin/activate          # Linux/Mac
# venv\Scripts\activate           # Windows
pip install -r requirements.txt
```

## Paso 3: Editar .env (1 min)

Asegurate de que `.env` tenga tus claves:

```env
DISCORD_TOKEN=tu_token_de_discord
NVIDIA_API_KEY=tu_api_key_de_nvidia
```

## Paso 4: Ejecutar (1 min)

```bash
source venv/bin/activate   # si no lo esta
python main.py
```

Veras:
```
Bot conectado como TuBot#1234
Sirviendo en 1 servidores
```

## Que hacer en Discord

| Accion | Como |
|--------|------|
| Saludar al bot | Escribe `hola` (responde automaticamente) |
| Hablar con IA | Mencionalo: `@TuBot que clima hace?` |
| Buscar en internet | `!buscar <termino>` |
| Clima | `!clima <ciudad>` |
| Guardar zona horaria | `!mi_zona America/Argentina/Buenos_Aires` |
| Musica | Unete a un canal de voz y escribe `!play <cancion>` |
| Ayuda | `!ayuda` |

## Si algo falla

**Token invalido** -> Revisa `DISCORD_TOKEN` en `.env`
**API Key invalida** -> Revisa `NVIDIA_API_KEY`
**No responde** -> El bot tiene permisos de lectura/escritura en el canal?
**Comando no encontrado** -> Usa `!ayuda` para ver la lista completa

Mas detalles en [README.md](README.md).
