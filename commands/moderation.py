"""Comandos de moderación: kick, ban, mute, warn, cleanup y registro de infracciones.

Inspirado en la funcionalidad del cog ``mod`` de Red-DiscordBot.
Usa el sistema de persistencia AsyncPersistence del bot para el mod-log.
"""
import asyncio
import logging
from datetime import datetime, timezone
from typing import Optional

import discord
from discord.ext import commands

from utils.persistence import AsyncPersistence, now_iso

log = logging.getLogger("mod")

_MUTED_ROLE_NAME = "Muted"


class Moderation(commands.Cog):
    """Herramientas de moderación para administradores y moderadores.

    Comandos: kick, ban, softban, hackban, unban, mute, unmute,
    clean, warn, infractions, modlog.
    """

    def __init__(self, bot):
        self.bot = bot

    # -- Helpers --

    def _mod_log(self) -> dict:
        return self.bot.persistence.data.setdefault("mod_log", [])

    def _add_log_entry(self, action: str, moderator: int, target: int, reason: str, duration: str = ""):
        entry = {
            "action": action,
            "moderator": moderator,
            "target": target,
            "reason": reason,
            "duration": duration,
            "ts": now_iso(),
        }
        log_data = self._mod_log()
        log_data.append(entry)
        if len(log_data) > 1000:
            self.bot.persistence.data["mod_log"] = log_data[-1000:]
        self.bot.persistence.mark_dirty()

    def _warns(self) -> dict:
        return self.bot.persistence.data.setdefault("warns", {})

    @staticmethod
    async def _try_dm(user: discord.User, content: str):
        try:
            await user.send(content)
        except (discord.Forbidden, discord.HTTPException):
            pass

    @staticmethod
    def _check_perms(ctx: commands.Context, target: discord.Member) -> bool:
        if ctx.author == target:
            return False
        if ctx.author.top_role <= target.top_role and ctx.author != ctx.guild.owner:
            return False
        return True

    # -- Kick --

    @commands.command(name="kick")
    @commands.has_permissions(kick_members=True)
    @commands.bot_has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason: str = ""):
        """Expulsa a un miembro del servidor.

        Ejemplo: !kick @usuario Spam en el chat
        """
        if not self._check_perms(ctx, member):
            await ctx.send("No puedes expulsar a ese usuario (rango superior o tú mismo).")
            return

        reason = reason or "No especificada"
        await self._try_dm(member, f"Has sido expulsado de **{ctx.guild.name}**.\nRazón: {reason}")
        await member.kick(reason=f"{ctx.author}: {reason}")
        self._add_log_entry("kick", ctx.author.id, member.id, reason)
        await ctx.send(f"{member} ha sido expulsado. Razón: {reason}")

    # -- Ban / Softban / Hackban / Unban --

    @commands.command(name="ban")
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, days: int = 0, *, reason: str = ""):
        """Banea a un miembro del servidor.

        Opcional: días de mensajes a eliminar (0-7).
        Ejemplo: !ban @usuario 2 Spam repetido
        """
        if not self._check_perms(ctx, member):
            await ctx.send("No puedes banear a ese usuario.")
            return

        reason = reason or "No especificada"
        days = max(0, min(7, days))
        await self._try_dm(member, f"Has sido baneado de **{ctx.guild.name}**.\nRazón: {reason}")
        await member.ban(reason=f"{ctx.author}: {reason}", delete_message_days=days)
        self._add_log_entry("ban", ctx.author.id, member.id, reason)
        await ctx.send(f"{member} ha sido baneado. Razón: {reason}")

    @commands.command(name="softban")
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def softban(self, ctx, member: discord.Member, *, reason: str = ""):
        """Banea y desbanea inmediatamente (borra mensajes).

        Útil para limpiar mensajes de un usuario sin expulsarlo permanentemente.
        """
        if not self._check_perms(ctx, member):
            await ctx.send("No puedes aplicar softban a ese usuario.")
            return

        reason = reason or "Sin razón"
        await member.ban(reason=f"{ctx.author}: Softban - {reason}", delete_message_days=1)
        await ctx.guild.unban(member, reason=f"{ctx.author}: Softban - Desbaneo automático")
        self._add_log_entry("softban", ctx.author.id, member.id, reason)
        await ctx.send(f"Softban aplicado a {member}. Mensajes eliminados.")

    @commands.command(name="hackban")
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def hackban(self, ctx, user_id: int, *, reason: str = ""):
        """Banea a un usuario que no está en el servidor por su ID.

        Ejemplo: !hackban 123456789 Spammer conocido
        """
        reason = reason or "No especificada"
        try:
            user = await self.bot.fetch_user(user_id)
            await ctx.guild.ban(discord.Object(id=user_id), reason=f"{ctx.author}: {reason}")
            self._add_log_entry("hackban", ctx.author.id, user_id, reason)
            await ctx.send(f"{user} (ID: {user_id}) ha sido baneado externamente.")
        except discord.NotFound:
            await ctx.send(f"No se encontró un usuario con ID {user_id}.")
        except discord.Forbidden:
            await ctx.send("No tengo permisos para banear a ese usuario.")

    @commands.command(name="unban")
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def unban(self, ctx, user_id: int, *, reason: str = ""):
        """Desbanea a un usuario por su ID.

        Ejemplo: !unban 123456789
        """
        reason = reason or "No especificada"
        try:
            user = await self.bot.fetch_user(user_id)
            await ctx.guild.unban(discord.Object(id=user_id), reason=f"{ctx.author}: {reason}")
            self._add_log_entry("unban", ctx.author.id, user_id, reason)
            await ctx.send(f"{user} (ID: {user_id}) ha sido desbaneado.")
        except discord.NotFound:
            await ctx.send(f"No se encontró un usuario con ID {user_id}.")
        except discord.Forbidden:
            await ctx.send("No tengo permisos para desbanear.")

    # -- Mute / Unmute --

    async def _get_mute_role(self, guild: discord.Guild) -> discord.Role:
        role = discord.utils.get(guild.roles, name=_MUTED_ROLE_NAME)
        if role is None:
            role = await guild.create_role(
                name=_MUTED_ROLE_NAME,
                reason="Rol de mute automático para el bot",
            )
            for channel in guild.channels:
                await channel.set_permissions(
                    role,
                    send_messages=False,
                    add_reactions=False,
                    speak=False,
                )
        return role

    @commands.command(name="mute")
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def mute(self, ctx, member: discord.Member, *, reason: str = ""):
        """Silencia a un miembro (rol Muted).

        Ejemplo: !mute @usuario Comportamiento inapropiado
        """
        if not self._check_perms(ctx, member):
            await ctx.send("No puedes silenciar a ese usuario.")
            return

        role = await self._get_mute_role(ctx.guild)
        if role in member.roles:
            await ctx.send(f"{member} ya está silenciado.")
            return

        reason = reason or "No especificada"
        await member.add_roles(role, reason=f"{ctx.author}: {reason}")
        self._add_log_entry("mute", ctx.author.id, member.id, reason)
        await self._try_dm(member, f"Has sido silenciado en **{ctx.guild.name}**.\nRazón: {reason}")
        await ctx.send(f"{member} ha sido silenciado. Razón: {reason}")

    @commands.command(name="unmute")
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def unmute(self, ctx, member: discord.Member):
        """Quita el silencio a un miembro.

        Ejemplo: !unmute @usuario
        """
        role = discord.utils.get(ctx.guild.roles, name=_MUTED_ROLE_NAME)
        if role is None or role not in member.roles:
            await ctx.send(f"{member} no está silenciado.")
            return

        await member.remove_roles(role, reason=f"{ctx.author}: Desmuteado")
        self._add_log_entry("unmute", ctx.author.id, member.id, "Desmuteado")
        await ctx.send(f"{member} ya no está silenciado.")

    # -- Warn / Infractions --

    @commands.command(name="warn")
    @commands.has_permissions(manage_messages=True)
    async def warn(self, ctx, member: discord.Member, *, reason: str = ""):
        """Aplica una advertencia a un miembro.

        Las advertencias se guardan y pueden consultarse con !infractions.
        Ejemplo: !warn @usuario Lenguaje inapropiado
        """
        if not self._check_perms(ctx, member):
            await ctx.send("No puedes advertir a ese usuario.")
            return

        reason = reason or "No especificada"
        warns = self._warns()
        uid = str(member.id)
        user_warns = warns.setdefault(uid, [])
        user_warns.append({
            "moderator": ctx.author.id,
            "reason": reason,
            "ts": now_iso(),
        })
        self.bot.persistence.mark_dirty()

        count = len(user_warns)
        self._add_log_entry("warn", ctx.author.id, member.id, reason)
        await self._try_dm(member, f"Has recibido una advertencia en **{ctx.guild.name}**.\nRazón: {reason}")
        await ctx.send(f"{member} ha sido advertido ({count}.a advertencia).")

    @commands.command(name="infractions", aliases=["warns", "advertencias"])
    @commands.has_permissions(manage_messages=True)
    async def infractions(self, ctx, member: discord.Member):
        """Muestra las advertencias de un miembro.

        Ejemplo: !infractions @usuario
        """
        warns = self._warns().get(str(member.id), [])
        if not warns:
            await ctx.send(f"{member} no tiene advertencias.")
            return

        lines = [f"**Advertencias de {member.display_name}** ({len(warns)} total):"]
        for i, w in enumerate(warns, 1):
            mod_name = f"<@{w['moderator']}>"
            lines.append(f"{i}. {w['reason']} — por {mod_name} ({w['ts']})")

        for chunk in (lines[j:j+10] for j in range(0, len(lines), 10)):
            await ctx.send("\n".join(chunk))

    @commands.command(name="clear_warns")
    @commands.has_permissions(administrator=True)
    async def clear_warns(self, ctx, member: discord.Member):
        """Limpia todas las advertencias de un miembro."""
        warns = self._warns()
        uid = str(member.id)
        if uid in warns:
            del warns[uid]
            self.bot.persistence.mark_dirty()
        await ctx.send(f"Advertencias de {member} eliminadas.")

    # -- Clean --

    @commands.command(name="clean", aliases=["purge"])
    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_messages=True)
    async def clean(self, ctx, limit: int = 10):
        """Elimina mensajes recientes del canal actual.

        Máximo 100 mensajes. Ejemplo: !clean 20
        """
        limit = max(1, min(100, limit))
        deleted = await ctx.channel.purge(limit=limit, before=ctx.message)
        self._add_log_entry("clean", ctx.author.id, 0, f"{len(deleted)} mensajes")
        msg = await ctx.send(f"Eliminados {len(deleted)} mensajes.", delete_after=5)
        await asyncio.sleep(5)
        await msg.delete()

    # -- Mod Log --

    @commands.command(name="modlog", aliases=["logs"])
    @commands.has_permissions(administrator=True)
    async def modlog(self, ctx, limit: int = 10):
        """Muestra el registro de acciones de moderación.

        Ejemplo: !modlog 20
        """
        log_data = self._mod_log()
        if not log_data:
            await ctx.send("No hay registros de moderación.")
            return

        limit = max(1, min(50, limit))
        entries = log_data[-limit:]

        lines = [f"**Últimas {len(entries)} acciones de moderación:**"]
        for e in reversed(entries):
            action = e["action"].upper()
            mod = f"<@{e['moderator']}>"
            target = f"<@{e['target']}>" if e["target"] else "—"
            lines.append(f"[{e['ts']}] **{action}** | Mod: {mod} | Objetivo: {target} | {e['reason']}")

        for chunk in (lines[j:j+15] for j in range(0, len(lines), 15)):
            await ctx.send("\n".join(chunk))

    @commands.command(name="modstats", aliases=["mod_stats"])
    @commands.has_permissions(administrator=True)
    async def modstats(self, ctx):
        """Muestra estadísticas de moderación."""
        log_data = self._mod_log()
        if not log_data:
            await ctx.send("No hay registros de moderación.")
            return

        action_counts = {}
        for e in log_data:
            action = e["action"]
            action_counts[action] = action_counts.get(action, 0) + 1

        lines = ["**Estadísticas de Moderación:**"]
        for action, count in sorted(action_counts.items(), key=lambda x: -x[1]):
            lines.append(f"- {action}: {count}")

        total = len(log_data)
        embed = discord.Embed(
            title="Estadísticas de Moderación",
            description="\n".join(lines),
            color=discord.Color.red(),
        )
        embed.set_footer(text=f"Total: {total} acciones registradas")
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Moderation(bot))
