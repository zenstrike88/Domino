import discord
from discord.ext import commands
import os
import random
import shutil
import asyncio
from discord import FFmpegOpusAudio
from dotenv import load_dotenv
from keep_alive import keep_alive

load_dotenv()  # charge le fichier .env en local (ignore si absent, ex: sur Render)


# Define the intents your bot will use
intents = discord.Intents.default()

# Add the necessary intents
intents.typing = True
intents.presences = True

# Add the message content intent
intents.message_content = True

# Initialize the bot with intents
bot = commands.Bot(command_prefix="!", intents=intents)

# Path to the "Download" folder containing photos
download_folder_path = "Download"

# Read the initial scores from Domino.txt
initial_scores = {}
with open("Domino.txt", "r") as file:
    for line in file:
        parts = line.strip().split()
        if len(parts) == 2:
            name, score = parts
            initial_scores[name] = int(score)
        else:
            print(f"Skipped line in Domino.txt: {line.strip()} (format is invalid)")


# Event handler for when the bot is ready
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")

# Function to calculate the Happy_point based on Point_Domino
def calculate_happy_point(losing_players, winners, initial_scores):
    # Check if the Domino point of the losing group is under 10
    if all(point_domino < 10 for _, point_domino in losing_players):
        happy_point_winner = 6
        happy_point_loser = -6
    
    else:
        happy_point_winner = 3
        happy_point_loser = -3

    return happy_point_winner, happy_point_loser


# Command to update Domino scores
@bot.command()
async def update(ctx, *player_info):
    
        # Check if the author is "hani"
    if ctx.author.name != "wembly10":
        await ctx.send("You are not authorized to use this command.")
        return
    
    print("Received input:", player_info)
    
    # Check the number of player entries
    if len(player_info) != 8:
        await ctx.send("You should provide information for exactly 4 players in the format 'name DominoPoint'.")
        return

    # Input player information
    players = []

    for i in range(0, len(player_info), 2):
        try:
            name, point_domino = player_info[i], player_info[i + 1]
            point_domino = int(point_domino)
            players.append((name, point_domino))
        except (ValueError, IndexError):
            await ctx.send("Invalid input format. Please use 'name DominoPoint' for each player.")
            return

    # Separate players into winners and losers
    winners = []
    losers = []

    for name, point_domino in players:
        if point_domino >= 100:
            winners.append((name, point_domino))
        else:
            losers.append((name, point_domino))

    # Check if all players' names exist in Domino.txt
    for name, _ in players:
        if name not in initial_scores:
            await ctx.send(f"Player '{name}' does not exist in Domino.txt. Please make sure all players exist.")
            return

    # Check if the Domino points for players in the same group are the same
    winner_domino_points = {point_domino for _, point_domino in winners}
    loser_domino_points = {point_domino for _, point_domino in losers}

    if len(winner_domino_points) > 1:
        await ctx.send("Domino points for the winning group are not the same. Please make sure they have the same points.")
        return

    if len(loser_domino_points) > 1:
        await ctx.send("Domino points for the losing group are not the same. Please make sure they have the same points.")
        return

    # Calculate and update scores
    happy_point_winner, happy_point_loser = calculate_happy_point(losers, winners, initial_scores)

    for winner, point_domino in winners:
        initial_scores[winner] = max(0, initial_scores[winner] + happy_point_winner)

    for loser, point_domino in losers:
        initial_scores[loser] = max(0, initial_scores[loser] + happy_point_loser)


    # Update Domino.txt with the new scores
    with open("Domino.txt", "w") as file:
        for name, score in initial_scores.items():
            file.write(f"{name} {score}\n")

    # Send the updated scores to the Discord channel
    scores_message = "\n".join([f"{name} {score}" for name, score in initial_scores.items()])
    await ctx.send("Updated Domino scores:\n" + scores_message)






# Modify the existing set_score command
@bot.command()
async def set_score(ctx, *score_info):
    
    # Check if the author is "hani"
    if ctx.author.name != "Makelél":
        await ctx.send("You are not authorized to use this command.")
        return
    
    
    if len(score_info) % 2 != 0:
        await ctx.send("Invalid input format. Please use 'name score' for each player.")
        return

    # Create a dictionary to store the new scores
    new_scores = {}

    for i in range(0, len(score_info), 2):
        name, new_score = score_info[i], int(score_info[i + 1])
        new_scores[name] = new_score

    # Update Domino.txt with the new scores
    with open("Domino.txt", "w") as file:
        for name, score in new_scores.items():
            file.write(f"{name} {score}\n")

    # Send the updated scores to the Discord channel
    scores_message = "\n".join([f"{name} {score}" for name, score in new_scores.items()])
    await ctx.send("Updated Domino scores:\n" + scores_message)

    # Update the initial_scores dictionary with the new scores
    for name, score in new_scores.items():
        initial_scores[name] = score


# Update the existing score command
@bot.command()
async def score(ctx):
    # Sort players by score in descending order
    sorted_scores = sorted(initial_scores.items(), key=lambda item: item[1], reverse=True)
    
    scores_message = "\n".join([f"{name}: {score}" for name, score in sorted_scores])
    await ctx.send("Final Domino scores (sorted by score):\n" + scores_message)

   

# Command to display an arbitrary photo from the "Download" folder
@bot.command()
async def tom(ctx):
    # Get a list of all files in the "Download" folder
    files = os.listdir(download_folder_path)

    # Filter for image files (you can modify the extensions as needed)
    image_files = [file for file in files if file.endswith((".jpg", ".jpeg", ".png", ".gif"))]

    if not image_files:
        await ctx.send("No images found in the 'Download' folder.")
        return

    # Select a random image file
    random_image = random.choice(image_files)

    # Send the selected image
    with open(os.path.join(download_folder_path, random_image), "rb") as file:
        await ctx.send(file=discord.File(file))



ffmpeg_path = shutil.which("ffmpeg")

@bot.command()
async def p(ctx, mp3_name: str = None):
    if mp3_name is None:
        # Get a list of all MP3 files in the "Documents" folder
        mp3_files = [file for file in os.listdir("Documents") if file.endswith(".mp3")]

        if not mp3_files:
            await ctx.send("No MP3 files found in the 'Documents' folder.")
            return

        # Select a random MP3 file
        file_name = random.choice(mp3_files)

    else:
        # Allow commands such as "!p 33" without requiring ".mp3".
        file_name = mp3_name.strip()
        if not file_name.lower().endswith(".mp3"):
            file_name += ".mp3"

    mp3_path = os.path.join("Documents", file_name)
    # Check if the MP3 file exists
    if not os.path.isfile(mp3_path):
        await ctx.send(f"MP3 file '{file_name}' not found.")
        return

    if ffmpeg_path is None:
        await ctx.send("FFmpeg is not installed, so I cannot play audio.")
        return

    # Play the selected MP3 file
    vc = ctx.voice_client
    if vc is None or not vc.is_connected():
        await ctx.send("You are not in a voice channel. Join a voice channel to use this command.")
        return

    try:
        if vc.is_playing():
            vc.stop()
        # Let FFmpeg encode Opus so a system libopus installation is not required.
        vc.play(FFmpegOpusAudio(executable=ffmpeg_path, source=mp3_path))
    except (discord.ClientException, OSError) as error:
        print(f"Audio playback failed: {error}")
        await ctx.send("I could not start audio playback. Please try `!join` again.")


@bot.command()
async def join(ctx):
    if ctx.author.voice is None or ctx.author.voice.channel is None:
        await ctx.send("Join a voice channel first.")
        return

    channel = ctx.author.voice.channel
    voice_client = ctx.voice_client

    try:
        if voice_client is not None and voice_client.is_connected():
            if voice_client.channel.id == channel.id:
                await ctx.send("I am already in this voice channel.")
            else:
                await voice_client.move_to(channel)
                await ctx.send(f"Moved to {channel.name}.")
            return

        # A failed handshake can leave a stale VoiceClient behind.
        if voice_client is not None:
            await voice_client.disconnect(force=True)

        await channel.connect(timeout=60, reconnect=True)
        await ctx.send(f"Joined {channel.name}.")
    except (asyncio.TimeoutError, discord.ClientException, OSError, RuntimeError) as error:
        print(f"Voice connection failed: {error}")
        await ctx.send("I could not connect to voice. Please try `!join` again.")


@bot.command()
async def leave(ctx):
    voice_client = ctx.voice_client
    if voice_client is not None and voice_client.is_connected():
        await voice_client.disconnect()
        await ctx.send("Left the voice channel.")
    else:
        await ctx.send("I am not in a voice channel.")


@bot.command(name="hello")
async def hello(ctx):
    await ctx.send("Hello, world!")

# Liste commune des phrases
phrases = [
    "Hani rah ykhassrek matal3abch m3ah 'mwassak!'",
    "tiro tjorlou 4 ydirha 3/3 w mba3ad ygolk lhhjar mahomch hleh!",
    "Mridh M7arbech yakl dwa",
    "khamaj lfrissa",
    "nta bnadam wella hajra",
    "habibou assmahli bsh nta ****",
    "domino rah contri, mayachtinich"
]

# Commande dynamique pour toutes les personnes
@bot.command()
async def hani(ctx):
    response = random.choice(phrases)
    await ctx.send(response)

@bot.command()
async def yahia(ctx):
    response = random.choice(phrases)
    await ctx.send(response)

@bot.command()
async def tiro(ctx):
    response = random.choice(phrases)
    await ctx.send(response)

@bot.command()
async def chiha(ctx):
    response = random.choice(phrases)
    await ctx.send(response)

@bot.command()
async def habibo(ctx):
    response = random.choice(phrases)
    await ctx.send(response)
    
@bot.command()
async def s1(ctx):
    try:
        # Ouvre le fichier en mode lecture
        with open("Season_1.txt", "r") as file:
            content = file.read()  # Lire tout le contenu du fichier

        # Envoie le contenu du fichier dans le chat
        await ctx.send(content)
    except FileNotFoundError:
        await ctx.send("Le fichier 'Season_1.txt' n'a pas été trouvé.")
    except Exception as e:
        await ctx.send(f"Une erreur s'est produite : {e}")

@bot.command()
async def s2(ctx):
    try:
        # Ouvre le fichier en mode lecture
        with open("Season_2.txt", "r") as file:
            content = file.read()  # Lire tout le contenu du fichier

        # Envoie le contenu du fichier dans le chat
        await ctx.send(content)
    except FileNotFoundError:
        await ctx.send("Le fichier 'Season_1.txt' n'a pas été trouvé.")
    except Exception as e:
        await ctx.send(f"Une erreur s'est produite : {e}")

# Run the bot with the token from an environment variable (never hardcode it!)
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
if not DISCORD_TOKEN:
    raise RuntimeError(
        "DISCORD_TOKEN introuvable. Ajoute-le comme variable d'environnement "
        "(fichier .env en local, ou 'Environment Variable' sur ton hebergeur)."
    )

keep_alive()  # lance le petit serveur web pour rester en vie sur un hebergeur gratuit
bot.run(DISCORD_TOKEN)

#https://discord.com/api/oauth2/authorize?client_id=1169980574631469107&permissions=70368744177655&scope=bot
