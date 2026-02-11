import discord
from discord import app_commands
import os
import json

TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

DATA_FILE = "leaderboard.json"

def load_entries():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_entries(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

entries = load_entries()

@tree.command(name="addentry", description="Add a leaderboard entry with points and images")
async def addentry(interaction: discord.Interaction, points: int):
    global entries

    # Get attached images
    attachments = interaction.attachments
    image_urls = [att.url for att in attachments]

    if not image_urls:
        await interaction.response.send_message(
            "You must attach at least one image.",
            ephemeral=True
        )
        return

    # Add new entry
    new_entry = {
        "points": points,
        "images": image_urls
    }

    entries.append(new_entry)

    # Sort descending by points
    entries.sort(key=lambda x: x["points"], reverse=True)

    save_entries(entries)

    await interaction.response.send_message(
        "Entry added! Rebuilding leaderboard...",
        ephemeral=True
    )

    channel = interaction.channel

    # Delete all messages in channel (limit 200 for safety)
    async for msg in channel.history(limit=200):
        await msg.delete()

    medals = ["🥇", "🥈", "🥉"]

    # Repost sorted leaderboard
    for index, entry in enumerate(entries):
        medal = medals[index] if index < 3 else f"{index+1}."

        await channel.send(
            content=f"{medal} - {entry['points']}️⃣"
        )

        # Send images in batches of 10 (Discord limit)
        for i in range(0, len(entry["images"]), 10):
            batch = entry["images"][i:i+10]
            await channel.send("\n".join(batch))


@client.event
async def on_ready():
    await tree.sync()
    print(f"Logged in as {client.user}")

client.run(TOKEN)

