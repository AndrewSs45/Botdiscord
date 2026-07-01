"""Comandos de utilidad general del bot.

Cog que agrupa: búsqueda en Internet, clima, hora (con zonas horarias),
preferencias de usuario, estadísticas y ayuda interactiva.
"""
import discord
from discord.ext import commands

from skills.internet_search import InternetSearchSkill
from skills.weather import WeatherSkill
from skills.time_skill import TimeSkill
from skills.user_preferences import UserPreferences

import config


class UtilityCommands(commands.Cog):
    """Comandos de utilidad: búsqueda, clima, hora y preferencias de usuario."""

    def __init__(self, bot):
        self.bot = bot
        self.internet_search = InternetSearchSkill()
        self.weather_skill = WeatherSkill()
        self.time_skill = TimeSkill()

    async def cog_before_invoke(self, ctx):
        """Registra automáticamente cada comando ejecutado en el tracker."""
        tracker = self.bot.tracker
        if tracker:
            tracker.registrar_comando(
                ctx.command.qualified_name,
                ctx.author.id,
                ctx.channel.name,
            )

    @commands.command(name="buscar", aliases=["search"])
    async def buscar(self, ctx, *, query: str):
        """Busca información en Internet usando Serper API (Google).

        Ejemplo: !buscar clima en México
        """
        async with ctx.typing():
            resultado = await self.internet_search.ejecutar(query)
            embed = discord.Embed(
                title=f"Resultados para: {query}",
                description=resultado,
                color=discord.Color.blue(),
            )
            embed.set_footer(text=f"Solicitado por {ctx.author}")
            await ctx.send(embed=embed)
            self.bot.learning.registrar_tema(f"busqueda: {query}", ctx.author.id)

    @commands.command(name="clima", aliases=["weather"])
    async def clima(self, ctx, *, ciudad: str):
        """Muestra el clima actual de una ciudad.

        Ejemplo: !clima Madrid
        """
        async with ctx.typing():
            resultado = await self.weather_skill.ejecutar(ciudad)
            embed = discord.Embed(
                title="Informacion del Clima",
                description=resultado,
                color=discord.Color.green(),
            )
            await ctx.send(embed=embed)
            self.bot.learning.registrar_tema(f"clima: {ciudad}", ctx.author.id)

    @commands.command(name="hora", aliases=["time"])
    async def hora(self, ctx, *, timezone: str | None = None):
        """Muestra la hora actual. Si configuraste !mi_zona, usa tu zona.

        Opcionalmente puedes pasar una zona: !hora Europe/London

        Ejemplos:
          !hora
          !hora America/Mexico_City
        """
        user_prefs: UserPreferences = self.bot.user_prefs
        if timezone is None:
            tz = user_prefs.get_timezone(ctx.author.id)
            if tz:
                resultado = await self.time_skill.ejecutar(timezone=tz)
            else:
                resultado = await self.time_skill.ejecutar()
        else:
            resultado = await self.time_skill.ejecutar(timezone=timezone)
        embed = discord.Embed(description=resultado, color=discord.Color.purple())
        await ctx.send(embed=embed)

    @commands.command(name="mi_zona", aliases=["set_zone", "zona"])
    async def mi_zona(self, ctx, *, timezone: str | None = None):
        """Guarda tu zona horaria para usarla en !hora.

        Sin argumento, muestra la zona actual.
        Ejemplo: !mi_zona America/Argentina/Buenos_Aires
        """
        user_prefs: UserPreferences = self.bot.user_prefs
        if timezone is None:
            tz = user_prefs.get_timezone(ctx.author.id)
            if tz:
                await ctx.send(f"Tu zona horaria actual es: **{tz}**")
            else:
                await ctx.send("No has configurado una zona horaria. Usa `!mi_zona America/Argentina/Buenos_Aires`")
            return
        resultado = user_prefs.set_timezone(ctx.author.id, timezone)
        await ctx.send(resultado)

    @commands.command(name="hora_en", aliases=["time_in"])
    async def hora_en(self, ctx, *, timezone: str):
        """Muestra la hora actual en cualquier zona horaria del mundo.

        Ejemplo: !hora_en Asia/Tokyo
        """
        user_prefs: UserPreferences = self.bot.user_prefs
        tiempo = user_prefs.get_time_in(timezone)
        if tiempo is None:
            await ctx.send(f"Zona horaria '{timezone}' no válida.")
            return
        embed = discord.Embed(
            description=f"⏰ **Hora en {timezone}:** {tiempo[0]}\n📅 **Fecha:** {tiempo[1]}",
            color=discord.Color.purple(),
        )
        await ctx.send(embed=embed)

    @commands.command(name="estadisticas", aliases=["stats"])
    async def estadisticas(self, ctx):
        """Muestra estadísticas del bot: temas populares y comandos más usados."""
        stats = self.bot.learning.obtener_estadisticas()
        cmd_stats = self.bot.tracker.obtener_stats() if self.bot.tracker else ""

        embed = discord.Embed(
            description=stats + cmd_stats,
            color=discord.Color.gold(),
        )
        await ctx.send(embed=embed)

    @commands.command(name="ayuda", aliases=["help", "commands"])
    async def ayuda(self, ctx):
        """Muestra todos los comandos disponibles organizados por categoría."""
        embed = discord.Embed(
            title="Comandos Disponibles",
            description="Estos son todos los comandos que puedo ejecutar:",
            color=discord.Color.blurple(),
        )

        cogs = {}
        for cmd in self.bot.commands:
            cog_name = cmd.cog_name or "Otros"
            cogs.setdefault(cog_name, []).append(cmd)

        for cog_name, cmds in sorted(cogs.items()):
            lines = []
            for cmd in sorted(cmds, key=lambda c: c.name):
                signatura = f"`{config.BOT_PREFIX}{cmd.name}"
                if cmd.signature:
                    signatura += f" {cmd.signature}"
                signatura += "`"
                desc = (cmd.short_doc or "Sin descripcion").split("\n")[0]
                lines.append(f"{signatura} - {desc}")
            embed.add_field(name=cog_name, value="\n".join(lines), inline=False)

        embed.add_field(
            name="Tip",
            value="Puedes mencionarme en cualquier mensaje para hablar con la IA, "
                  "o simplemente saludarme y te responderé automáticamente.",
            inline=False,
        )
        embed.set_footer(text=f"Solicitado por {ctx.author}")
        await ctx.send(embed=embed)


async def setup(bot):
    """Función de carga requerida por discord.py para Cogs."""
    await bot.add_cog(UtilityCommands(bot))
