"""Punto de entrada del bot de Discord.

Configura los intents, crea la instancia del bot, inicializa todos
los sistemas (IA, aprendizaje, preferencias, tracking) y registra
los eventos principales: on_ready, on_message, on_command_error.

Comandos globales definidos aquí:
  - !limpiar_chat / !clear_chat
  - !ping
"""
import asyncio
import logging
from pathlib import Path

import discord
from discord.ext import commands

import config
from skills.assistant import AIAssistant
from skills.learning import LearningSystem
from skills.command_tracker import CommandTracker
from skills.greeting import detectar_saludo, obtener_respuesta_saludo
from skills.user_preferences import UserPreferences
from utils.logger import setup_logger
from utils.persistence import AsyncPersistence


setup_logger("bot", logging.DEBUG)
log = logging.getLogger("bot")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix=config.BOT_PREFIX, intents=intents, help_command=None)

ai_assistant = AIAssistant()

persistence = AsyncPersistence("bot_learning.json", {}, config.PERSISTENCE_INTERVAL)

learning_system = LearningSystem(persistence)
command_tracker = CommandTracker(persistence)
user_prefs = UserPreferences(persistence)

bot.learning = learning_system
bot.tracker = command_tracker
bot.user_prefs = user_prefs
bot.ai_assistant = ai_assistant
bot.persistence = persistence


@bot.event
async def on_ready():
    """Se ejecuta cuando el bot se conecta a Discord correctamente.

    Inicia el guardado automático de persistencia y actualiza el
    estado del bot (actividad "escuchando").
    """
    log.info("Bot conectado como %s", bot.user)
    log.info("Sirviendo en %s servidores", len(bot.guilds))
    persistence.start_auto_save()
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.listening,
            name=f"{config.BOT_PREFIX}ayuda | IA Activa",
        )
    )


@bot.event
async def on_message(message):
    """Maneja cada mensaje entrante en canales donde el bot tiene acceso.

    Flujo:
      1. Ignora mensajes del propio bot (evita loops).
      2. Registra al usuario en el sistema de aprendizaje.
      3. Procesa comandos con prefijo.
      4. Detecta saludos simples y responde automáticamente.
      5. Si el bot es mencionado, delega a la IA para respuesta.
    """
    if message.author == bot.user:
        return

    learning_system.registrar_usuario(message.author.id)
    await bot.process_commands(message)

    contenido = message.content.strip().lower()
    if detectar_saludo(contenido):
        nombre = message.author.display_name
        respuesta = obtener_respuesta_saludo(nombre, message.author.mention)
        await message.reply(respuesta, mention_author=False)
        return

    if not bot.user.mentioned_in(message):
        return

    if message.content.startswith(config.BOT_PREFIX):
        return

    log.debug("Mensaje de %s: %s...", message.author, message.content[:80])

    try:
        async with message.channel.typing():
            contexto = f"Canal: {message.channel.name}, Usuario: {message.author.name}"
            respuesta = await asyncio.wait_for(
                ai_assistant.obtener_respuesta(
                    mensaje=message.content,
                    user_id=message.author.id,
                    contexto=contexto,
                ),
                timeout=95.0,
            )

        if respuesta:
            for bloque in (respuesta[i:i+1990] for i in range(0, len(respuesta), 1990)):
                await message.reply(bloque, mention_author=False)
            log.info("Respuesta enviada (%s caracteres)", len(respuesta))

            palabras = message.content.split()
            if len(palabras) > 2:
                tema = " ".join(palabras[:3])
                learning_system.registrar_tema(tema, message.author.id)
        else:
            await message.reply("No pude generar una respuesta. Intenta de nuevo.", mention_author=False)

    except asyncio.TimeoutError:
        log.warning("Timeout esperando respuesta de IA")
        await message.reply("Tarde demasiado procesando. Intenta de nuevo.", mention_author=False)
    except Exception as e:
        log.error("Error procesando mensaje: %s: %s", type(e).__name__, e)
        await message.reply("Ocurrio un error al procesar tu mensaje.", mention_author=False)


@bot.event
async def on_command_error(ctx, error):
    """Maneja errores de ejecución de comandos con mensajes amigables.

    CommandNotFound se ignora silenciosamente.
    MissingRequiredArgument y BadArgument muestran ayuda contextual.
    Otros errores se loguean y muestran un mensaje genérico.
    """
    if isinstance(error, commands.CommandNotFound):
        return
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"Falta un argumento. Usa `{config.BOT_PREFIX}ayuda` para ver como usar el comando.")
        return
    if isinstance(error, commands.BadArgument):
        await ctx.send(f"Argumento invalido. Usa `{config.BOT_PREFIX}ayuda` para ver como usar el comando.")
        return
    log.error("Error en comando %s: %s: %s", ctx.command, type(error).__name__, error)
    await ctx.send("Ocurrio un error al ejecutar el comando.")


@bot.command(name="limpiar_chat", aliases=["clear_chat"])
async def limpiar_chat(ctx):
    """Limpia el historial de conversación con la IA para el usuario actual."""
    ai_assistant.limpiar_historial_usuario(ctx.author.id)
    await ctx.send("Chat limpiado correctamente.")


@bot.command(name="ping")
async def ping(ctx):
    """Muestra la latencia actual del bot en milisegundos."""
    latencia = round(bot.latency * 1000)
    await ctx.send(f"Pong! Latencia: {latencia}ms")


async def cargar_comandos():
    """Descubre y carga todos los Cogs en el directorio ``commands/``."""
    comandos_dir = Path("commands")
    for archivo_py in comandos_dir.glob("*.py"):
        if archivo_py.name.startswith("_"):
            continue
        try:
            await bot.load_extension(f"commands.{archivo_py.stem}")
            log.info("Comandos cargados: %s", archivo_py.stem)
        except Exception as e:
            log.error("Error cargando %s: %s", archivo_py.stem, e)


async def shutdown():
    """Guarda datos pendientes antes de detener el bot."""
    log.info("Guardando datos...")
    persistence.save()
    log.info("Datos guardados.")


async def main():
    """Función principal: carga módulos, conecta e inicia el bot."""
    try:
        await cargar_comandos()
        log.info("Iniciando bot...")
        async with bot:
            await bot.start(config.DISCORD_TOKEN)
    except discord.LoginFailure:
        log.error("Token de Discord invalido. Verifica tu .env")
    except Exception as e:
        log.error("Error: %s", e)
    finally:
        await shutdown()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log.info("Bot detenido por el usuario")
