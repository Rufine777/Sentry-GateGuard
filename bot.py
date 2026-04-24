import discord
import gspread
import os
import asyncio

from dotenv import load_dotenv
from google.oauth2.service_account import Credentials
from discord.ext import commands, tasks

# ---------------------------
# LOAD ENV
# ---------------------------
load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
LOG_CHANNEL_ID = int(os.getenv("LOG_CHANNEL_ID"))
SHEET_NAME = os.getenv("SHEET_NAME")

RUFINE_ID = 1395441864152318193
SAHARSH_ID = 1074144319486836786

# ---------------------------
# GOOGLE SHEETS
# ---------------------------
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds = Credentials.from_service_account_file(
    "credentials.json",
    scopes=SCOPES
)

client = gspread.authorize(creds)
sheet = client.open(SHEET_NAME).sheet1

# ---------------------------
# DISCORD SETUP
# ---------------------------
intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# prevent duplicate processing
processed_users = set()

# ---------------------------
# HELPERS
# ---------------------------

def normalize_id(val):
    return str(val).strip().replace(".0", "")

async def safe_add_role(member, role):
    if role and role not in member.roles:
        await member.add_roles(role)

async def safe_remove_role(member, role):
    if role and role in member.roles:
        await member.remove_roles(role)

def get_member_data():
    rows = sheet.get_all_records()
    cleaned = []

    for r in rows:
        if "discord_id" in r and "year" in r:
            cleaned.append({
                "discord_id": normalize_id(r["discord_id"]),
                "year": str(r["year"]).strip().upper()
            })

    return cleaned

# ---------------------------
# SYNC LOOP (ONLY UPGRADES)
# ---------------------------

@tasks.loop(minutes=2)
async def sync_users():

    await bot.wait_until_ready()

    try:
        data = get_member_data()
    except Exception as e:
        print("Sheet error:", e)
        return

    for guild in bot.guilds:

        unverified = discord.utils.get(guild.roles, name="Unverified")
        s1_role = discord.utils.get(guild.roles, name="New-Generation")
        s3_role = discord.utils.get(guild.roles, name="Worst-Generation")

        faction_roles = [
            discord.utils.get(guild.roles, name="rock-pirates"),
            discord.utils.get(guild.roles, name="roger-pirates"),
            discord.utils.get(guild.roles, name="whitebeard-pirates"),
            discord.utils.get(guild.roles, name="redhair-pirates"),
            discord.utils.get(guild.roles, name="blackbeard-pirates"),
            discord.utils.get(guild.roles, name="straw_hat-pirates"),
            discord.utils.get(guild.roles, name="seraphim"),
            discord.utils.get(guild.roles, name="cross-guild"),
            discord.utils.get(guild.roles, name="germa-66"),
            discord.utils.get(guild.roles, name="cipher-pol"),
            discord.utils.get(guild.roles, name="sword"),
            discord.utils.get(guild.roles, name="pacifista"),
            discord.utils.get(guild.roles, name="heart-pirates"),
            discord.utils.get(guild.roles, name="kid-pirates"),
        ]

        faction_roles = [r for r in faction_roles if r is not None]

        log = guild.get_channel(LOG_CHANNEL_ID)

        for member in guild.members:

            if member.bot:
                continue

            # ONLY process users who already have Unverified
            if not unverified or unverified not in member.roles:
                continue

            match = next(
                (r for r in data if r["discord_id"] == normalize_id(member.id)),
                None
            )

            if not match:
                continue

            # ---------------------------
            # UPGRADE USER
            # ---------------------------
            await safe_remove_role(member, unverified)

            year = match["year"]

            if year == "S1":
                await safe_add_role(member, s1_role)

                # assign faction ONLY for S1
                existing_faction = next(
                    (r for r in member.roles if r in faction_roles),
                    None
                )

                if not existing_faction and faction_roles:
                    sizes = [len(r.members) for r in faction_roles]
                    chosen = faction_roles[sizes.index(min(sizes))]
                    await safe_add_role(member, chosen)

            elif year == "S3":
                await safe_add_role(member, s3_role)

            if log:
                await log.send(f"🔄 Sync verified: {member.name}")

# ---------------------------
# READY
# ---------------------------

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    sync_users.start()

# ---------------------------
# JOIN EVENT (ONLY ENTRY POINT)
# ---------------------------

@bot.event
async def on_member_join(member):

    if member.bot:
        return

    if member.id in processed_users:
        return

    guild = member.guild

    unverified = discord.utils.get(guild.roles, name="Unverified")
    s1_role = discord.utils.get(guild.roles, name="New-Generation")
    s3_role = discord.utils.get(guild.roles, name="Worst-Generation")

    faction_roles = [
        discord.utils.get(guild.roles, name="rock-pirates"),
        discord.utils.get(guild.roles, name="roger-pirates"),
        discord.utils.get(guild.roles, name="whitebeard-pirates"),
        discord.utils.get(guild.roles, name="redhair-pirates"),
        discord.utils.get(guild.roles, name="blackbeard-pirates"),
        discord.utils.get(guild.roles, name="straw_hat-pirates"),
        discord.utils.get(guild.roles, name="seraphim"),
        discord.utils.get(guild.roles, name="cross-guild"),
        discord.utils.get(guild.roles, name="germa-66"),
        discord.utils.get(guild.roles, name="cipher-pol"),
        discord.utils.get(guild.roles, name="sword"),
        discord.utils.get(guild.roles, name="pacifista"),
        discord.utils.get(guild.roles, name="heart-pirates"),
        discord.utils.get(guild.roles, name="kid-pirates"),
    ]

    faction_roles = [r for r in faction_roles if r is not None]

    log = guild.get_channel(LOG_CHANNEL_ID)

    data = get_member_data()

    match = next(
        (r for r in data if r["discord_id"] == normalize_id(member.id)),
        None
    )

    # ---------------------------
    # NOT REGISTERED
    # ---------------------------
    if not match:

        await safe_add_role(member, unverified)

        try:
            await member.send(
f"""🏴‍☠️ Ahoy, Wanderer!

We couldn’t find your AMFOSS registration ⚓

📜 Fill form → Leave → Rejoin

Contact:
<@{RUFINE_ID}> / <@{SAHARSH_ID}>"""
            )
        except:
            pass

        if log:
            await log.send(f"⚠️ Not registered: {member.name}")

        return

    # ---------------------------
    # REGISTERED
    # ---------------------------

    await safe_remove_role(member, unverified)

    year = match["year"]

    if year == "S1":
        await safe_add_role(member, s1_role)

        sizes = [len(r.members) for r in faction_roles]
        chosen = faction_roles[sizes.index(min(sizes))]
        await safe_add_role(member, chosen)

        faction_name = chosen.name

    elif year == "S3":
        await safe_add_role(member, s3_role)
        faction_name = "Worst-Generation (S3)"

    processed_users.add(member.id)

    try:
        await member.send(
f"""🏴‍☠️ Ahoy, Crew Member!

Your AMFOSS registration is verified ⚓

You’ve been assigned to **{faction_name}** ⚔️

🔥 Your journey begins!

Contact:
<@{RUFINE_ID}> / <@{SAHARSH_ID}>"""
        )
    except:
        pass

    if log:
        await log.send(f"✅ Verified: {member.name} → {faction_name}")

# ---------------------------
# RUN
# ---------------------------
bot.run(TOKEN)