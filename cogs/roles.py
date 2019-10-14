import discord
import utils.globals as GG

from discord.ext import commands
from utils import logger
from DBService import DBService

log = logger.logger

def getGuild(self, payload):
    guild = self.bot.get_guild(payload.guild_id)
    return guild

class Roles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def addRole(self, ctx, channelId, messageId, roleId, emoji):
        channel = await self.bot.fetch_channel(channelId)
        message = await channel.fetch_message(messageId)
        try:
            await message.add_reaction(emoji)
        except:
            await ctx.send("Unknown Emoji, please only use default emoji's or emoji's from this server.")
        else:
            DBService.exec(
                "INSERT INTO ReactionRoles (GuildId, MessageId, RoleId, Emoji) VALUES (" + str(
                    ctx.guild.id) + "," + str(messageId) + "," + str(roleId) + ",'" + str(emoji) + "')")
            GG.reloadReactionRoles()


    @commands.command()
    async def removeRole(self, ctx, channelId, messageId, roleId, emoji):
        channel = await self.bot.fetch_channel(channelId)
        message = await channel.fetch_message(messageId)
        try:
            reactions = message.reactions
            for x in reactions:
                if x.emoji == emoji:
                    users = await x.users().flatten()
                    for y in users:
                        await message.remove_reaction(emoji, y)
        except:
            await ctx.send("Unknown Emoji, please check if this emoji is still present as a reaction on the message you supplied.")
        else:
            DBService.exec(
                "DELETE FROM ReactionRoles WHERE GuildId = " + str(
                    ctx.guild.id) + " AND MessageId = " + str(messageId) + " AND RoleId = " + str(roleId) + " AND Emoji = '" + str(emoji) + "'")
            GG.reloadReactionRoles()

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.message_id in GG.REACTIONROLES:
            emoji = payload.emoji
            reaction = GG.REACTIONROLES[payload.message_id][1]
            if emoji.name == reaction:
                roleId = GG.REACTIONROLES[payload.message_id][0]
                userId = payload.user_id
                guildId = payload.guild_id
                guild = await self.bot.fetch_guild(guildId)
                Role = guild.get_role(roleId)
                Member = await guild.fetch_member(userId)
                await Member.add_roles(Role)


    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        if payload.message_id in GG.REACTIONROLES:
            emoji = payload.emoji
            reaction = GG.REACTIONROLES[payload.message_id][1]
            if emoji.name == reaction:
                roleId = GG.REACTIONROLES[payload.message_id][0]
                userId = payload.user_id
                guildId = payload.guild_id
                guild = await self.bot.fetch_guild(guildId)
                Role = guild.get_role(roleId)
                Member = await guild.fetch_member(userId)
                await Member.remove_roles(Role)

def setup(bot):
    log.info("Loading Roles Cog...")
    bot.add_cog(Roles(bot))
