import discord
from discord import app_commands
import os
import json

TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

DATA_FILE = "scores.json"

def load_scores():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_scores(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

scores = load_scores()
leaderboard_message_id = None

@tree.command(name="score", description="Add or update a player's score")
async def score(interaction: discord.Interaction, name: str, points: int):
    global scores
    scores[name] = points
    save_scores(scores)

    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    leaderboard_text = "🏆 **Leaderboard** 🏆\n\n"

    medals = ["🥇", "🥈", "🥉"]

    for index, (player, pts) in enumerate(sorted_scores):
        medal = medals[index] if index < 3 else f"{index+1}."
        leaderboard_text += f"{medal} {player} — {pts}\n"

    await interaction.response.send_message("Leaderboard updated!", ephemeral=True)

    channel = interaction.channel

    global leaderboard_message_id
    if leaderboard_message_id:
        try:
            msg = await channel.fetch_message(leaderboard_message_id)
            await msg.edit(content=leaderboard_text)
            return
        except:
            pass

    msg = await channel.send(leaderboard_text)
    leaderboard_message_id = msg.id

@client.event
async def on_ready():
    await tree.sync()
    print(f"Logged in as {client.user}")

client.run(TOKEN)
