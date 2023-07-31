import discord
import asyncio
from discord.ext import commands

intents = discord.Intents.default()
bot = commands.Bot(command_prefix='!', intents=intents)

# Dictionary to store user factions and points
user_data = {}

# Role IDs
ADMIN_ROLE_ID = 1105826475636179064
ROMULIANS_ROLE_ID = 1135647230833983652
KLINGONS_ROLE_ID = 1135647515841138778
FEDERATION_ROLE_ID = 1090540548235993090


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')


@bot.command(name='joinfaction')
async def join_faction(ctx):
    if ctx.author.id not in user_data:
        user_data[ctx.author.id] = {
            'faction': None,
            'points': 0
        }

        factions = {
            '1': ROMULIANS_ROLE_ID,
            '2': KLINGONS_ROLE_ID,
            '3': FEDERATION_ROLE_ID
        }

        faction_choice_msg = (
            "Welcome to the server!\n"
            "Please choose your faction:\n"
            "1. The Romulians\n"
            "2. The Klingons\n"
            "3. The Federation"
        )
        await ctx.send(faction_choice_msg)

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel and m.content in factions

        try:
            faction_response = await bot.wait_for('message', check=check, timeout=60)
            faction_choice = factions[faction_response.content]
            user_data[ctx.author.id]['faction'] = faction_choice
            await ctx.author.add_roles(discord.utils.get(ctx.guild.roles, id=faction_choice))
            await ctx.send(f"You have joined the faction successfully!")
        except asyncio.TimeoutError:
            await ctx.send("Faction selection timed out.")
    else:
        await ctx.send("You have already joined a faction and cannot change factions.")


@bot.event
async def on_message(message):
    if not message.author.bot and message.author.id in user_data:
        user_data[message.author.id]['points'] += 1
    await bot.process_commands(message)


@bot.command(name='rankingfaction')
async def ranking_faction(ctx):
    if ctx.author.id not in user_data or user_data[ctx.author.id]['faction'] is None:
        await ctx.send("You need to join a faction first using the command !joinfaction.")
    else:
        faction_points = {}
        for user_id, data in user_data.items():
            faction_id = data['faction']
            points = data['points']
            if faction_id in faction_points:
                faction_points[faction_id] += points
            else:
                faction_points[faction_id] = points

        sorted_factions = sorted(faction_points.items(), key=lambda x: x[1], reverse=True)
        faction_ranking_msg = "Faction Rankings:\n"
        for rank, (faction_id, points) in enumerate(sorted_factions, start=1):
            faction_name = discord.utils.get(ctx.guild.roles, id=faction_id).name
            faction_ranking_msg += f"{rank}. {faction_name}: {points} points\n"

        top_3_members = sorted(user_data.items(), key=lambda x: x[1]['points'], reverse=True)[:3]
        member_ranking_msg = "Top 3 Commanders:\n"
        for rank, (user_id, data) in enumerate(top_3_members, start=1):
            user = bot.get_user(user_id)
            member_name = user.name if user else f"Unknown User ({user_id})"
            member_points = data['points']
            member_ranking_msg += f"{rank}. <@{user_id}> : {member_points} points\n"

        await ctx.send(f"{faction_ranking_msg}\n{member_ranking_msg}")


@bot.command(name='grantpoints')
async def grant_points(ctx, user: discord.Member, points: int):
    if ctx.author.id in user_data and discord.utils.get(ctx.author.roles, id=ADMIN_ROLE_ID):
        user_data[user.id]['points'] += points
        await ctx.send(f"{points} points have been granted to {user.name}.")
    else:
        await ctx.send("You don't have the permission to grant points or you are not an admin.")

bot.run('bottoken)
