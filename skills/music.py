"""Reproductor de música desde YouTube con cola y control de reproducción.

Utiliza yt-dlp para extraer audio de YouTube y discord.py para
reproducirlo en canales de voz. Soporta cola, loop, shuffle y
control de volumen.
"""
import asyncio
import logging
import random
import re

import discord
import yt_dlp

import config
from utils.logger import setup_logger


log = setup_logger("music")


_YTDL_OPTS = {
    "format": "bestaudio[ext=m4a]/bestaudio/best",
    "quiet": True,
    "no_warnings": True,
    "default_search": "ytsearch",
    "source_address": "0.0.0.0",
    "extract_flat": False,
    "ignoreerrors": True,
}

_FFMPEG_OPTS = {
    "before_options": (
        "-reconnect 1 "
        "-reconnect_streamed 1 "
        "-reconnect_delay_max 5 "
        "-timeout 15000000"
    ),
    "options": "-vn -loglevel fatal",
}

_YT_URL_RE = re.compile(r"(https?://)?(www\.)?(youtube\.com|youtu\.be)/")
_SEARCH_RE = re.compile(r".+")


class Track:
    """Representa una canción individual con sus metadatos.

    Attributes:
        title: Título de la canción.
        webpage_url: URL de YouTube.
        duration: Duración en segundos.
        thumbnail: URL de la miniatura.
        requester: ID de Discord del usuario que solicitó la canción.
    """

    def __init__(self, title: str, webpage_url: str, duration: int, thumbnail: str, requester: int):
        self.title = title
        self.webpage_url = webpage_url
        self.duration = duration
        self.thumbnail = thumbnail
        self.requester = requester

    @property
    def duration_str(self) -> str:
        """Duración formateada como MM:SS."""
        m, s = divmod(self.duration, 60)
        return f"{m}:{s:02d}"


class MusicPlayer:
    """Reproductor de música con cola, loop y control de volumen por servidor.

    Maneja la conexión al canal de voz, la extracción de audio desde
    YouTube, la cola de reproducción y los modos de loop (off/one/all).
    """

    def __init__(self):
        self._queue: list[Track] = []
        self._current: Track | None = None
        self._vc: discord.VoiceClient | None = None
        self._loop_mode = 0
        self._volume = config.MUSIC_VOLUME_DEFAULT
        self._stopped = False
        self._guild_id: int | None = None
        self._play_task: asyncio.Task | None = None
        log.debug("MusicPlayer creado")

    @property
    def is_playing(self) -> bool:
        """Indica si hay audio reproduciéndose actualmente."""
        return self._vc is not None and self._vc.is_playing()

    @property
    def is_paused(self) -> bool:
        """Indica si la reproducción está en pausa."""
        return self._vc is not None and self._vc.is_paused()

    @property
    def current(self) -> Track | None:
        """Canción que se está reproduciendo ahora, o None."""
        return self._current

    @property
    def queue(self) -> list[Track]:
        """Copia de la cola de reproducción."""
        return list(self._queue)

    @property
    def loop_mode(self) -> int:
        """Modo de loop: 0=off, 1=one, 2=all."""
        return self._loop_mode

    @property
    def volume(self) -> int:
        """Volumen actual (0-100)."""
        return self._volume

    async def _cleanup_vc(self):
        old = self._vc
        self._vc = None
        if old:
            try:
                if old.is_connected():
                    await old.disconnect(force=True)
                    log.debug("VoiceClient anterior desconectado")
            except Exception as e:
                log.debug("Error limpiando VoiceClient anterior: %s", e)

    async def _connect_voice(self, channel: discord.VoiceChannel) -> bool:
        try:
            log.debug("Iniciando channel.connect() para: %s", channel.name)
            vc = await asyncio.wait_for(
                channel.connect(timeout=20.0, reconnect=True),
                timeout=60.0,
            )
        except asyncio.TimeoutError:
            log.error("Timeout conectando al canal de voz (60s): %s", channel.name)
            return False
        except discord.ClientException as e:
            log.error("ClientException conectando a %s: %s", channel.name, e)
            if "Already connected" in str(e):
                log.warning("Already connected - forzando limpieza y reintento")
                return "retry"
            return False
        except discord.Forbidden:
            log.error("Sin permisos para unirme a: %s", channel.name)
            return False
        except Exception as e:
            log.error("Error inesperado conectando a %s: %s", channel.name, e, exc_info=True)
            return False
        else:
            self._vc = vc
            log.info("Conectado al canal de voz: %s", channel.name)
            return True

    async def join(self, channel: discord.VoiceChannel) -> bool:
        """Conecta o mueve el bot a un canal de voz.

        Si ya está conectado al mismo canal, retorna True.
        Si está en otro canal, se mueve. Si el VoiceClient está obsoleto,
        lo limpia y reconecta.

        Args:
            channel: Canal de voz destino.

        Returns:
            True si la conexión fue exitosa.
        """
        self._guild_id = channel.guild.id
        log.info("Intentando unirse al canal de voz: %s (guild: %s)", channel.name, channel.guild.id)

        if self._vc and self._vc.is_connected():
            if self._vc.channel.id == channel.id:
                log.debug("Ya conectado al canal %s", channel.name)
                return True
            log.debug("Moviendo al canal %s", channel.name)
            try:
                await self._vc.move_to(channel)
                return True
            except Exception as e:
                log.error("Error moviendo de canal: %s", e)
                await self._cleanup_vc()

        if self._vc and not self._vc.is_connected():
            log.warning("VoiceClient stale detectado, limpiando...")
            await self._cleanup_vc()

        result = await self._connect_voice(channel)
        if result == "retry":
            await self._cleanup_vc()
            result = await self._connect_voice(channel)

        return bool(result)

    async def leave(self):
        """Desconecta del canal de voz, limpia la cola y detiene la reproducción."""
        log.info("Desconectando del canal de voz (guild: %s)", self._guild_id)
        self._stopped = True
        if self._play_task and not self._play_task.done():
            self._play_task.cancel()
            self._play_task = None
        self._queue.clear()
        self._current = None
        await self._cleanup_vc()

    async def play(self, query: str, requester: int, text_channel: discord.TextChannel) -> str:
        """Busca y reproduce (o encola) una canción desde YouTube.

        Args:
            query: Término de búsqueda o URL de YouTube.
            requester: ID de Discord del usuario que solicita.
            text_channel: Canal de texto para enviar notificaciones.

        Returns:
            Mensaje indicando qué canción se está reproduciendo o se agregó a la cola.
        """
        log.info("Solicitud de reproduccion: '%s' de user %s", query, requester)

        track_data = await self._fetch_track(query)
        if not track_data:
            log.warning("No se encontraron resultados para: %s", query)
            return "No se encontraron resultados."

        track = Track(requester=requester, **track_data)
        log.info("Track encontrado: %s (%s)", track.title, track.duration_str)

        self._queue.append(track)

        if self._play_task and not self._play_task.done() and self.is_playing:
            pos = len(self._queue)
            log.debug("Track agregado a cola (pos %s)", pos)
            return f"**Agregado:** {track.title} (`{track.duration_str}`) | Posicion: {pos}"

        if self._play_task and not self._play_task.done():
            self._play_task.cancel()

        self._stopped = False
        self._play_task = asyncio.create_task(self._play_loop())
        log.debug("Iniciando _play_loop en background")
        return f"**Reproduciendo:** {track.title} (`{track.duration_str}`)"

    async def skip(self) -> Track | None:
        """Salta la canción actual.

        Returns:
            El Track saltado, o None si no había reproducción.
        """
        old = self._current
        log.info("Saltando cancion: %s", old.title if old else "None")
        if self._vc and self._vc.is_playing():
            self._vc.stop()
        if self._loop_mode == 1 and old:
            self._queue.insert(0, old)
        return old

    def toggle_pause(self) -> bool:
        """Alterna entre pausa y reanudación.

        Returns:
            True si se pausó, False si se reanudó.
        """
        if not self._vc:
            return False
        if self._vc.is_paused():
            self._vc.resume()
            log.debug("Reproduccion reanudada")
            return False
        self._vc.pause()
        log.debug("Reproduccion pausada")
        return True

    def set_volume(self, vol: int):
        """Ajusta el volumen (0-100). Se recorta automáticamente al rango válido."""
        self._volume = max(0, min(100, vol))
        log.debug("Volumen ajustado a %s", self._volume)

    def set_loop(self, mode: int):
        """Cambia el modo de loop: 0=off, 1=one, 2=all."""
        self._loop_mode = mode % 3
        log.debug("Loop mode: %s", self._loop_mode)

    def shuffle(self):
        """Aleatoriza el orden de los elementos en la cola."""
        random.shuffle(self._queue)
        log.debug("Cola aleatorizada (%s items)", len(self._queue))

    def clear_queue(self):
        """Elimina todos los elementos de la cola de reproducción."""
        self._queue.clear()
        log.debug("Cola limpiada")

    # -- Audio extraction --

    async def _fetch_track(self, query: str) -> dict | None:
        search_query = f"ytsearch:{query}" if not _YT_URL_RE.match(query) else query
        log.debug("Extrayendo info: %s", search_query)

        def extract():
            with yt_dlp.YoutubeDL(_YTDL_OPTS) as ydl:
                return ydl.extract_info(search_query, download=False)

        try:
            raw = await asyncio.wait_for(
                asyncio.get_running_loop().run_in_executor(None, extract),
                timeout=30.0,
            )
        except asyncio.TimeoutError:
            log.warning("Timeout en extraccion de YouTube (30s): %s", search_query)
            return None
        except Exception as e:
            log.error("Error en extraccion de YouTube: %s", e)
            return None

        log.debug("Extraccion completada, procesando entrada")
        entry = raw if "entries" not in raw else (
            (raw.get("entries") or [None])[0]
        )

        if not entry:
            log.warning("Entry vacio para: %s", query)
            return None

        return {
            "title": entry.get("title", "Desconocido"),
            "webpage_url": entry.get("webpage_url") or entry.get("url", ""),
            "duration": entry.get("duration", 0) or 0,
            "thumbnail": entry.get("thumbnail", ""),
        }

    async def _get_audio_url(self, track: Track) -> str | None:
        log.debug("Obteniendo URL de audio para: %s", track.title)

        def extract():
            with yt_dlp.YoutubeDL(_YTDL_OPTS) as ydl:
                info = ydl.extract_info(track.webpage_url, download=False)
                return info.get("url", "")

        try:
            url = await asyncio.wait_for(
                asyncio.get_running_loop().run_in_executor(None, extract),
                timeout=20.0,
            )
            log.debug("URL de audio obtenida (%s chars)", len(url))
            return url
        except Exception as e:
            log.error("Error obteniendo URL de audio para %s: %s", track.title, e)
            return None

    # -- Playback loop --

    async def _play_loop(self):
        log.info("_play_loop iniciado")

        try:
            while not self._stopped:
                if not self._vc or not self._vc.is_connected():
                    log.warning("Conexion de voz perdida en _play_loop, saliendo")
                    self._stopped = True
                    break

                if self._loop_mode == 2 and self._current:
                    log.debug("Loop mode 2: re-agregando track actual a cola")
                    self._queue.append(self._current)

                if not self._queue:
                    self._current = None
                    log.info("Cola vacia, _play_loop finalizado")
                    break

                self._current = self._queue.pop(0)
                log.info("Reproduciendo: %s", self._current.title)
                ok = await self._play_track(self._current)
                if not ok:
                    log.warning("Fallo reproduccion de: %s, saltando...", self._current.title)
                    self._current = None
                    continue
        except asyncio.CancelledError:
            log.info("_play_loop cancelado")
        except Exception as e:
            log.error("Error en loop de reproduccion: %s", e, exc_info=True)

        log.info("_play_loop terminado (stopped=%s)", self._stopped)

    async def _play_track(self, track: Track) -> bool:
        if not self._vc or not self._vc.is_connected():
            log.warning("No hay conexion de voz para reproducir %s", track.title)
            return False

        audio_url = await self._get_audio_url(track)
        if not audio_url:
            log.error("No se pudo obtener URL de audio para: %s", track.title)
            return False

        try:
            log.debug("Creando FFmpegPCMAudio para: %s", track.title)
            source = discord.FFmpegPCMAudio(audio_url, **_FFMPEG_OPTS)
            source = discord.PCMVolumeTransformer(source, volume=self._volume / 100)
        except Exception as e:
            log.error("Error creando fuente de audio para %s: %s", track.title, e)
            return False

        play_done = asyncio.get_running_loop().create_future()

        def _on_finish(err):
            if err:
                log.error("Playback error para %s: %s", track.title, err)
            else:
                log.info("Playback finalizado: %s", track.title)
            if not play_done.done():
                play_done.set_result(None)

        log.info("Iniciando playback: %s", track.title)
        self._vc.play(source, after=_on_finish)

        try:
            await asyncio.wait_for(play_done, timeout=None)
        except asyncio.CancelledError:
            if self._vc and self._vc.is_playing():
                self._vc.stop()
            raise

        log.debug("_play_track retornando True para: %s", track.title)
        return True
