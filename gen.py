import discord
from discord.ext import commands
import asyncio

intents = discord.Intents.default()
intents.guilds = True
intents.guild_messages = True
intents.guild_reactions = True
intents.message_content = True

client = commands.Bot(command_prefix='!', intents=intents)

def print_add(message):
    print(f'\033[92m[+]\033[0m {message}')

def print_delete(message):
    print(f'\033[91m[-]\033[0m {message}')

def print_warning(message):
    print(f'\033[91m[WARNING]\033[0m {message}')

def print_error(message):
    print(f'\033[91m[ERROR]\033[0m {message}')

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
        roles = roles[::-1]
        for role in roles:
            try:
                await guild_to.create_role(
                    name=role.name,
                    permissions=role.permissions,
                    colour=role.colour,
                    hoist=role.hoist,
                    mentionable=role.mentionable
                )
                print_add(f"Created Role {role.name}")
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
                print_error(f"Unable To Delete Channel: {channel.name}")

    @staticmethod
    async def categories_create(guild_to: discord.Guild, guild_from: discord.Guild):
        channels = guild_from.categories
        for channel in channels:
            try:
                overwrites_to = {discord.utils.get(guild_to.roles, name=key.name): value for key, value in channel.overwrites.items()}
                new_channel = await guild_to.create_category(
                    name=channel.name,
                    overwrites=overwrites_to)
                await new_channel.edit(position=channel.position)
                print_add(f"Created Category: {channel.name}")
            except discord.Forbidden:
                print_error(f"Error While Creating Category: {channel.name}")
            except discord.HTTPException:
                print_error(f"Unable To Create Category: {channel.name}")

    @staticmethod
    async def channels_create(guild_to: discord.Guild, guild_from: discord.Guild):
        for channel_text in guild_from.text_channels:
            try:
                category = next((cat for cat in guild_to.categories if cat.name == channel_text.category.name), None)
                overwrites_to = {discord.utils.get(guild_to.roles, name=key.name): value for key, value in channel_text.overwrites.items()}
                new_channel = await guild_to.create_text_channel(
                    name=channel_text.name,
                    overwrites=overwrites_to,
                    position=channel_text.position,
                    topic=channel_text.topic,
                    slowmode_delay=channel_text.slowmode_delay,
                    nsfw=channel_text.nsfw
                )
                if category:
                    await new_channel.edit(category=category)
                print_add(f"Created Text Channel: {channel_text.name}")
            except discord.Forbidden:
                print_error(f"Error While Creating Text Channel: {channel_text.name}")
            except discord.HTTPException:
                print_error(f"Unable To Create Text Channel: {channel_text.name}")

        for channel_voice in guild_from.voice_channels:
            try:
                category = next((cat for cat in guild_to.categories if cat.name == channel_voice.category.name), None)
                overwrites_to = {discord.utils.get(guild_to.roles, name=key.name): value for key, value in channel_voice.overwrites.items()}
                new_channel = await guild_to.create_voice_channel(
                    name=channel_voice.name,
                    overwrites=overwrites_to,
                    position=channel_voice.position,
                    bitrate=channel_voice.bitrate,
                    user_limit=channel_voice.user_limit
                )
                if category:
                    await new_channel.edit(category=category)
                print_add(f"Created Voice Channel: {channel_voice.name}")
            except discord.Forbidden:
                print_error(f"Error While Creating Voice Channel: {channel_voice.name}")
            except discord.HTTPException:
                print_error(f"Unable To Create Voice Channel: {channel_voice.name}")

    @staticmethod
    async def emojis_delete(guild_to: discord.Guild):
        for emoji in guild_to.emojis:
            try:
                await emoji.delete()
                print_delete(f"Deleted Emoji: {emoji.name}")
            except discord.Forbidden:
                print_error(f"Error While Deleting Emoji: {emoji.name}")
            except discord.HTTPException:
                print_error(f"Unable To Delete Emoji: {emoji.name}")

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
                print_error(f"Unable To Create Emoji: {emoji.name}")

    @staticmethod
    async def guild_edit(guild_to: discord.Guild, guild_from: discord.Guild):
        try:
            icon_image = await guild_from.icon_url.read()
            await guild_to.edit(name=f'{guild_from.name}')
            if icon_image:
                await guild_to.edit(icon=icon_image)
                print_add(f"Guild Icon Changed: {guild_to.name}")
        except discord.Forbidden:
            print_error(f"Error While Changing Guild Icon: {guild_to.name}")
        except discord.errors.DiscordException:
            print_error(f"Can't read icon image from {guild_from.name}")

@client.event
async def on_ready():
    print_add(f'Logged in as {client.user.name}')

    token = input("Enter your Discord Bot Token: ")
    target_invite = input("Enter the target server invite link: ")
    destination_invite = input("Enter the destination server invite link: ")

    try:
        target_guild = await client.fetch_guild(target_invite)
        destination_guild = await client.fetch_guild(destination_invite)

        print_add("Cloning roles...")
        await Clone.roles_delete(destination_guild)
        await Clone.roles_create(destination_guild, target_guild)

        print_add("Cloning channels...")
        await Clone.channels_delete(destination_guild)
        await Clone.categories_create(destination_guild, target_guild)
        await Clone.channels_create(destination_guild, target_guild)

        print_add("Cloning emojis...")
        await Clone.emojis_delete(destination_guild)
        await Clone.emojis_create(destination_guild, target_guild)

        print_add("Cloning completed.")
    except Exception as e:
        print_error(f"An error occurred: {e}")

client.run(token)
