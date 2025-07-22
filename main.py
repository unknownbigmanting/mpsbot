import discord
from discord import app_commands
import datetime
import asyncio
import aiohttp

# Your bot token here (DO NOT share this publicly!)
TOKEN = "MTM2NTc0NTg0MzczNDQ0NjA5MA.GOeSeF.eO1Y3A57MAHwhSu5mfNPctkwZFelc7LlUjoZ2Q"

intents = discord.Intents.default()
bot = discord.Client(intents=intents)
tree = app_commands.CommandTree(bot)

# Configuration
AUDIT_CHANNEL_ID = 1365749594125762622
ROBLOX_GROUP_LINK = "https://www.roblox.com/communities/configure?id=17275620#!/members"
AUTHORIZED_ROLES = [1396530459063615699, 1365755304654147707]

async def status_task():
    statuses = [
        ("South London 2 Remastered", discord.ActivityType.playing),
        ("MET's Glory", discord.ActivityType.watching),
    ]
    while not bot.is_closed():
        for status, activity_type in statuses:
            await bot.change_presence(activity=discord.Activity(name=status, type=activity_type))
            await asyncio.sleep(60)

ACTION_CONFIG = {
    "promote": {"format": "promoted to the rank of **{rank}** on behalf of the **Metropolitan Police Service**", "color": 0x2ECC71, "requires_rank": True},
    "demote": {"format": "demoted to **{rank}** on behalf of the **Metropolitan Police Service**", "color": 0xE74C3C, "requires_rank": True},
    "exile": {"format": "exiled from the **Metropolitan Police Service**", "color": 0x992D22},
    "accept": {"format": "accepted into the **Metropolitan Police Service**", "color": 0x3498DB},
    "strike": {"format": "given a strike on behalf of the **Metropolitan Police Service**", "color": 0xF39C12},
    "AL": {"format": "placed on **Administrative Leave** on behalf of the **Metropolitan Police Service**", "color": 0xF1C40F},
    "AL_remove": {"format": "taken off **Administrative Leave** on behalf of the **Metropolitan Police Service**", "color": 0x2ECC71},
    "LOA": {"format": "placed on **Leave of Absence** on behalf of the **Metropolitan Police Service**", "color": 0x95A5A6},
    "blacklist": {"format": "blacklisted from the **Metropolitan Police Service**", "color": 0x000000},
    "strike_remove": {"format": "had their strike removed on behalf of the **Metropolitan Police Service**", "color": 0x2ECC71},
    "unblacklisted": {"format": "unblacklisted from the **Metropolitan Police Service**", "color": 0x3498DB},
    "reinstate": {"format": "reinstated to the rank of **{rank}** on behalf of the **Metropolitan Police Service**", "color": 0x1ABC9C, "requires_rank": True}
}

RANK_CHOICES = [
    app_commands.Choice(name="Community Support Officer", value="Community Support Officer"),
    app_commands.Choice(name="Constable", value="Constable"),
    app_commands.Choice(name="Sergeant", value="Sergeant"),
    app_commands.Choice(name="Inspector", value="Inspector"),
    app_commands.Choice(name="Chief Inspector", value="Chief Inspector"),
    app_commands.Choice(name="Superintendent", value="Superintendent"),
    app_commands.Choice(name="Chief Superintendent", value="Chief Superintendent"),
    app_commands.Choice(name="Commander", value="Commander"),
    app_commands.Choice(name="Assistant Chief Constable", value="Assistant Chief Constable"),
    app_commands.Choice(name="Deputy Chief Constable", value="Deputy Chief Constable"),
    app_commands.Choice(name="Chief Constable", value="Chief Constable"),
    app_commands.Choice(name="Deputy Assistant Commissioner", value="Deputy Assistant Commissioner"),
    app_commands.Choice(name="Assistant Commissioner", value="Assistant Commissioner"),
    app_commands.Choice(name="Deputy Commissioner", value="Deputy Commissioner"),
    app_commands.Choice(name="Commissioner", value="Commissioner")
]

async def fetch_roblox_thumbnail(username: str):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(
                "https://users.roblox.com/v1/usernames/users",
                json={"usernames": [username], "excludeBannedUsers": True},
                timeout=5
            ) as resp:
                user_data = await resp.json()
                if not user_data.get("data"):
                    return None
                user_id = user_data["data"][0]["id"]

            async with session.get(
                "https://thumbnails.roblox.com/v1/users/avatar-headshot",
                params={"userIds": user_id, "size": "150x150", "format": "Png"},
                timeout=5
            ) as resp:
                thumb_data = await resp.json()
                return thumb_data["data"][0]["imageUrl"] if thumb_data.get("data") else None
        except (aiohttp.ClientError, asyncio.TimeoutError):
            return None

async def send_audit_log(action_data: dict):
    if not any(role.id in AUTHORIZED_ROLES for role in action_data["initiator"].roles):
        return

    channel = bot.get_channel(AUDIT_CHANNEL_ID)
    if not channel:
        print("⚠️ Audit channel not found!")
        return

    embed = discord.Embed(
        title="MET - Audit Log",
        color=0x2F3136,
        timestamp=datetime.datetime.now()
    )

    action_text = ACTION_CONFIG[action_data["action"]]["format"]
    if action_data.get("rank"):
        action_text = action_text.format(rank=f"**{action_data['rank']}**")

    embed.description = (
        f"**{action_data['user']}** has been {action_text}\n"
        f"by {action_data['initiator'].mention}"
    )
    embed.add_field(name="", value=f"**Reason**\n{action_data['reason']}", inline=False)
    await channel.send(embed=embed)

@bot.event
async def on_ready():
    bot.loop.create_task(status_task())
    print(f"✅ MET Police Bot Online as {bot.user}")
    try:
        await tree.sync()
        print("🔄 Commands Synced Successfully")
    except Exception as e:
        print(f"⚠️ Command Sync Error: {e}")

@tree.command(name="action", description="Perform administrative action")
@app_commands.describe(
    user="Roblox username",
    action="Type of action",
    reason="Reason for action",
    rank="New rank (if applicable)"
)
@app_commands.choices(
    action=[
        app_commands.Choice(name="Promote", value="promote"),
        app_commands.Choice(name="Demote", value="demote"),
        app_commands.Choice(name="Exile", value="exile"),
        app_commands.Choice(name="Accept", value="accept"),
        app_commands.Choice(name="Strike", value="strike"),
        app_commands.Choice(name="Administrative Leave", value="AL"),
        app_commands.Choice(name="Remove Administrative Leave", value="AL_remove"),
        app_commands.Choice(name="Leave of Absence", value="LOA"),
        app_commands.Choice(name="Blacklist", value="blacklist"),
        app_commands.Choice(name="Remove Strike", value="strike_remove"),
        app_commands.Choice(name="Unblacklist", value="unblacklisted"),
        app_commands.Choice(name="Reinstate", value="reinstate")
    ],
    rank=RANK_CHOICES
)
async def action_command(interaction: discord.Interaction,
                         user: str,
                         action: str,
                         reason: str,
                         rank: str = None):

    if not any(role.id in AUTHORIZED_ROLES for role in interaction.user.roles):
        return await interaction.response.send_message(
            "❌ You do not have permission to use this command!",
            ephemeral=True
        )

    if ACTION_CONFIG[action].get("requires_rank") and not rank:
        return await interaction.response.send_message(
            "❌ You must specify a rank for this action!",
            ephemeral=True
        )

    timestamp = datetime.datetime.now().strftime("%d/%m/%Y at %H:%M")
    officer_name = interaction.user.nick or interaction.user.name
    config = ACTION_CONFIG[action]
    action_text = config["format"].format(rank=f"**{rank}**") if rank else config["format"]

    embed = discord.Embed(
        title="Administrative Action",
        description=f"**{user}** has been {action_text}",
        color=config["color"]
    )
    embed.add_field(name="Reason", value=reason, inline=False)
    embed.set_footer(text=f"{officer_name} | {timestamp}")

    if thumbnail_url := await fetch_roblox_thumbnail(user):
        embed.set_thumbnail(url=thumbnail_url)

    await interaction.response.send_message(embed=embed)

    await send_audit_log({
        "action": action,
        "user": user,
        "initiator": interaction.user,
        "reason": reason,
        "rank": rank
    })

    await interaction.followup.send(
        f"🔗 Make changes: {ROBLOX_GROUP_LINK}",
        ephemeral=True
    )

if __name__ == "__main__":
    if not TOKEN or TOKEN == "PASTE_YOUR_DISCORD_TOKEN_HERE":
        print("❌ FATAL: Token missing or not set.")
    else:
        bot.run(TOKEN)
