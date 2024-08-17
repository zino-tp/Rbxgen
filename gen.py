import discord
from discord.ext import commands
from colorama import Fore, init, Style
import asyncio

init()  # Initialisiere colorama

def print_add(message):
    print(f'{Fore.GREEN}[+]{Style.RESET_ALL} {message}')

def print_delete(message):
    print(f'{Fore.RED}[-]{Style.RESET_ALL} {message}')

def print_warning(message):
    print(f'{Fore.YELLOW}[WARNING]{Style.RESET_ALL} {message}')

def print_error(message):
    print(f'{Fore.RED}[ERROR]{Style.RESET_ALL} {message}')

class Clone:
    @staticmethod
    async def roles_delete(guild_to: discord.Guild):
        for role in guild_to.roles:
            try:
                if role.name != "@everyone":
                    await role.delete()
                    print_delete(f"Deleted Role: {role.name}")
            except discord.Forbidden:
                print_error(f"Error While Deleting Role: {role.name}")
            except discord.HTTPException:
                print_error(f"Unable to Delete Role: {role.name}")

    @staticmethod
    async def roles_create(guild_to: discord.Guild, guild_from: discord.Guild):
        roles = [role for role in guild_from.roles if role.name != "@everyone"]
        roles = roles[::-1]  # Reverse order to preserve hierarchy
        for role in roles:
            try:
                await guild_to.create_role(
                    name=role.name,
                    permissions=role.permissions,
                    colour=role.colour,
                    hoist=role.hoist,
                    mentionable=role.mentionable
                )
                print_add(f"Created Role: {role.name}")
            except discord.Forbidden:
                print_error(f"Error While Creating Role: {role.name}")
            except discord.HTTPException:
                print_error(f"Unable to Create Role: {role.name}")

    @staticmethod
    async def channels_delete(guild_to: discord.Guild):
        for channel in guild_to.channels:
            try:
                await channel.delete()
                print_delete(f"Deleted Channel: {channel.name}")
            except discord.Forbidden:
                print_error(f"Error While Deleting Channel: {channel.name}")
            except discord.HTTPException:
                print_error(f"Unable to Delete Channel: {channel.name}")

    @staticmethod
    async def categories_create(guild_to: discord.Guild, guild_from: discord.Guild):
        channels = guild_from.categories
        for channel in channels:
            try:
                overwrites_to = {}
                for key, value in channel.overwrites.items():
                    role = discord.utils.get(guild_to.roles, name=key.name)
                    if role:
                        overwrites_to[role] = value
                new_channel = await guild_to.create_category(
                    name=channel.name,
                    overwrites=overwrites_to
                )
                await new_channel.edit(position=channel.position)
                print_add(f"Created Category: {channel.name}")
            except discord.Forbidden:
                print_error(f"Error While Creating Category: {channel.name}")
            except discord.HTTPException:
                print_error(f"Unable to Create Category: {channel.name}")

    @staticmethod
    async def channels_create(guild_to: discord.Guild, guild_from: discord.Guild):
        for channel in guild_from.text_channels:
            try:
                category = discord.utils.get(guild_to.categories, name=channel.category.name) if channel.category else None
                overwrites_to = {}
                for key, value in channel.overwrites.items():
                    role = discord.utils.get(guild_to.roles, name=key.name)
                    if role:
                        overwrites_to[role] = value
                new_channel = await guild_to.create_text_channel(
                    name=channel.name,
                    overwrites=overwrites_to,
                    position=channel.position,
                    topic=channel.topic,
                    slowmode_delay=channel.slowmode_delay,
                    nsfw=channel.nsfw
                )
                if category:
                    await new_channel.edit(category=category)
                print_add(f"Created Text Channel: {channel.name}")
            except discord.Forbidden:
                print_error(f"Error While Creating Text Channel: {channel.name}")
            except discord.HTTPException:
                print_error(f"Unable to Create Text Channel: {channel.name}")

        for channel in guild_from.voice_channels:
            try:
                category = discord.utils.get(guild_to.categories, name=channel.category.name) if channel.category else None
                overwrites_to = {}
                for key, value in channel.overwrites.items():
                    role = discord.utils.get(guild_to.roles, name=key.name)
                    if role:
                        overwrites_to[role] = value
                new_channel = await guild_to.create_voice_channel(
                    name=channel.name,
                    overwrites=overwrites_to,
                    position=channel.position,
                    bitrate=channel.bitrate,
                    user_limit=channel.user_limit
                )
                if category:
                    await new_channel.edit(category=category)
                print_add(f"Created Voice Channel: {channel.name}")
            except discord.Forbidden:
                print_error(f"Error While Creating Voice Channel: {channel.name}")
            except discord.HTTPException:
                print_error(f"Unable to Create Voice Channel: {channel.name}")

    @staticmethod
    async def emojis_delete(guild_to: discord.Guild):
        for emoji in guild_to.emojis:
            try:
                await emoji.delete()
                print_delete(f"Deleted Emoji: {emoji.name}")
            except discord.Forbidden:
                print_error(f"Error While Deleting Emoji: {emoji.name}")
            except discord.HTTPException:
                print_error(f"Unable to Delete Emoji: {emoji.name}")

    @staticmethod
    async def emojis_create(guild_to: discord.Guild, guild_from: discord.Guild):
        for emoji in guild_from.emojis:
            try:
                emoji_image = await emoji.url.read()
                await guild_to.create_custom_emoji(
                    name=emoji.name,
                    image=emoji_image
                )
                print_add(f"Created Emoji: {emoji.name}")
            except discord.Forbidden:
                print_error(f"Error While Creating Emoji: {emoji.name}")
            except discord.HTTPException:
                print_error(f"Unable to Create Emoji: {emoji.name}")

    @staticmethod
    async def guild_edit(guild_to: discord.Guild, guild_from: discord.Guild):
        try:
            icon_image = await guild_from.icon_url.read()
            await guild_to.edit(name=guild_from.name)
            if icon_image:
                await guild_to.edit(icon=icon_image)
                print_add(f"Guild Icon Changed: {guild_to.name}")
        except discord.Forbidden:
            print_error(f"Error While Changing Guild Icon: {guild_to.name}")
        except discord.errors.DiscordException:
            print_error(f"Can't read icon image from {guild_from.name}")

intents = discord.Intents.default()
intents.guilds = True
intents.channels = True
intents.members = True
intents.roles = True
intents.emojis = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")

@bot.command()
async def clone(ctx, target_invite: str, destination_invite: str):
    target_guild_id = int(target_invite.split('/')[-1])
    destination_guild_id = int(destination_invite.split('/')[-1])
    
    target_guild = discord.utils.get(bot.guilds, id=target_guild_id)
    destination_guild = discord.utils.get(bot.guilds, id=destination_guild_id)

    if not target_guild:
        await ctx.send("Der Bot ist nicht im Zielserver (zu klonender Server).")
        return
    if not destination_guild:
        await ctx.send("Der Bot ist nicht im Zielserver (dein Server).")
        return

    await ctx.send(f"Beginne mit dem Klonen von {target_guild.name} nach {destination_guild.name}...")

    await Clone.roles_delete(destination_guild)
    await Clone.roles_create(destination_guild, target_guild)
    await Clone.channels_delete(destination_guild)
    await Clone.categories_create(destination_guild, target_guild)
    await Clone.channels_create(destination_guild, target_guild)
    await Clone.emojis_delete(destination_guild)
    await Clone.emojis_create(destination_guild, target_guild)
    await Clone.guild_edit(destination_guild, target_guild)

    await ctx.send(f"Server erfolgreich nach {destination_guild.name} geklont.")

def main():
    token = input("Bitte gib deinen Discord-Bot-Token ein: ")
    bot.run(token)

if __name__ == "__main__":
    main()
