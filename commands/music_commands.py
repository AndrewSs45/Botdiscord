"""Comandos de reproducción de música en canales de voz.

Cog que permite reproducir audio desde YouTube con cola,
control de loop, shuffle y volumen.
"""
import asyncio

import discord
from discord.ext import commands

from skills.music import MusicPlayer


_players: dict[int, MusicPlayer] = {}


def _get_player(guild_id: int) -> MusicPlayer:
    """Obtiene o crea un MusicPlayer para un servidor específico."""
    if guild_id not in _players:
        _players[guild_id] = MusicPlayer()
    return _players[guild_id]


class MusicCommands(commands.Cog):
    """Comandos de música: reproducir, pausar, saltar, cola y control de reproducción."""

    def __init__(self, bot):
        self.bot = bot

    def _player(self, ctx) -> MusicPlayer:
        return _get_player(ctx.guild.id)

    async def _ensure_voice(self, ctx) -> bool:
        if not ctx.author.voice or not ctx.author.voice.channel:
            await ctx.send("Debes estar en un canal de voz.")
            return False
        player = self._player(ctx)
        ok = await player.join(ctx.author.voice.channel)
        if not ok:
            await ctx.send("No pude conectarme al canal de voz.")
        return ok

    @commands.command(name="play")
    async def play(self, ctx, *, query: str):
        """Reproduce una canción desde YouTube (nombre o URL).

        Si ya hay música sonando, agrega la canción a la cola.
        Ejemplo: !play never gonna give you up
        """
        if not await self._ensure_voice(ctx):
            return

        status = await ctx.send("Buscando en YouTube...")

        try:
            player = self._player(ctx)
            msg = await asyncio.wait_for(
                player.play(query, ctx.author.id, ctx.channel),
                timeout=45.0,
            )
            await status.edit(content=msg)
        except asyncio.TimeoutError:
            await status.edit(content="La busqueda tardó demasiado. Intenta de nuevo.")

    @commands.command(name="skip")
    async def skip(self, ctx):
        """Salta a la siguiente canción en la cola."""
        player = self._player(ctx)
        if not player.is_playing:
            await ctx.send("No hay nada reproduciendose.")
            return
        old = await player.skip()
        await ctx.send(f"**Saltado:** {old.title}" if old else "Saltado.")

    @commands.command(name="stop")
    async def stop(self, ctx):
        """Detiene la música, limpia la cola y desconecta del canal de voz."""
        player = self._player(ctx)
        await player.leave()
        await ctx.send("Desconectado del canal de voz.")

    @commands.command(name="pause")
    async def pause(self, ctx):
        """Pausa la reproducción actual."""
        player = self._player(ctx)
        if player.toggle_pause():
            await ctx.send("Pausado.")
        else:
            await ctx.send("Reanudado.")

    @commands.command(name="resume")
    async def resume(self, ctx):
        """Reanuda la reproducción pausada."""
        player = self._player(ctx)
        if player.is_paused:
            player.toggle_pause()
            await ctx.send("Reanudado.")
        else:
            await ctx.send("No hay nada pausado.")

    @commands.command(name="queue", aliases=["cola"])
    async def queue(self, ctx):
        """Muestra la cola de reproducción actual."""
        player = self._player(ctx)
        items = player.queue
        if not items and not player.current:
            await ctx.send("La cola esta vacia.")
            return

        embed = discord.Embed(
            title="Cola de Reproduccion",
            color=discord.Color.blue(),
        )

        if player.current:
            embed.add_field(
                name="**Reproduciendo ahora:**",
                value=f"{player.current.title} (`{player.current.duration_str}`)",
                inline=False,
            )

        if items:
            lines = []
            for i, s in enumerate(items[:10], 1):
                lines.append(f"{i}. {s.title} (`{s.duration_str}`)")
            embed.add_field(
                name=f"Siguientes ({len(items)} canciones):",
                value="\n".join(lines),
                inline=False,
            )

        await ctx.send(embed=embed)

    @commands.command(name="nowplaying", aliases=["np"])
    async def nowplaying(self, ctx):
        """Muestra la canción que se está reproduciendo actualmente."""
        player = self._player(ctx)
        if not player.current:
            await ctx.send("No hay nada reproduciendose.")
            return
        await ctx.send(f"**Reproduciendo:** {player.current.title} (`{player.current.duration_str}`)")

    @commands.command(name="loop")
    async def loop(self, ctx, mode: str = ""):
        """Cambia el modo de loop: off (0), one (1), all (2).

        Ejemplos:
          !loop off  - desactiva loop
          !loop one  - repite una canción
          !loop all  - repite toda la cola
        """
        modes = {"off": 0, "one": 1, "all": 2, "0": 0, "1": 1, "2": 2}
        value = modes.get(mode.lower()) if mode else None
        if value is None:
            await ctx.send("Usa: `!loop off|one|all` o `!loop 0|1|2`")
            return
        player = self._player(ctx)
        player.set_loop(value)
        labels = {0: "desactivado", 1: "una cancion", 2: "toda la cola"}
        await ctx.send(f"Loop: **{labels[value]}**")

    @commands.command(name="shuffle")
    async def shuffle(self, ctx):
        """Aleatoriza el orden de la cola de reproducción."""
        player = self._player(ctx)
        player.shuffle()
        await ctx.send("Cola aleatorizada.")

    @commands.command(name="volume", aliases=["vol"])
    async def volume(self, ctx, vol: int):
        """Ajusta el volumen de reproducción (0-100).

        Ejemplo: !volume 75
        """
        player = self._player(ctx)
        player.set_volume(vol)
        await ctx.send(f"Volumen: **{player.volume}%**")


async def setup(bot):
    """Función de carga requerida por discord.py para Cogs."""
    await bot.add_cog(MusicCommands(bot))
