import openai
import discord
import os
from dotenv import load_dotenv
from discord.ext import commands

# Load environment variables from .env file
try:
    load_dotenv()
except FileNotFoundError:
    print("Could not find .env file")

openai.api_key = os.getenv("API_KEY")

if openai.api_key is None:
    print("API key not set. Set the API key using openai.api_key = 'YOUR_API_KEY'")
else:
    print("Connected to OpenAI API key...")

# Create a bot object using the commands module
bot = commands.Bot(command_prefix="/", intents=discord.Intents.all())

# This function is used to get the list of movies from the logger (by reading from the movie-log.txt file)


def get_movie_list():
    movie_list = []
    try:
        with open("movie-log.txt", "r") as movie_log_file:
            for line in movie_log_file:
                movie_list.append(line.strip())
    except FileNotFoundError:
        return "movie-log.txt file not found"
    else:
        return "\n".join(movie_list)

# This function is used to search for movies in the logger (by searching the movie-log.txt file)


def search_movies(query):
    search_results = []
    try:
        with open("movie-log.txt", "r") as movie_log_file:
            for line in movie_log_file:
                if query.lower() in line.lower():
                    search_results.append(line.strip())
    except FileNotFoundError:
        return "movie-log.txt file not found"
    else:
        if not search_results:
            return "No results found"
        return "\n".join(search_results)

# This function is used to add a movie to the logger (by appending to the movie-log.txt file)


def add_movie(movie_details):
    if not movie_details:
        return
    # Check if the movie already exists in the logger
    if movie_details in search_movies(movie_details):
        return
    try:
        with open("movie-log.txt", "a") as movie_log_file:
            movie_log_file.write(f"{movie_details}\n")
    except FileNotFoundError:
        return "movie-log.txt file not found"

# This function is used to delete a movie from the logger (by overwriting the movie-log.txt file)


def delete_movie(movie_details):
    movie_list = get_movie_list()
    if movie_details not in movie_list:
        return "Movie not found"
    try:
        with open("movie-log.txt", "w") as movie_log_file:
            for movie in movie_list:
                if movie != movie_details:
                    movie_log_file.write(f"{movie}\n")
    except FileNotFoundError:
        return "movie-log.txt file not found"

# This function is used to handle errors


def handle_error(error):
    try:
        return f"Error of type {type(error)} occurred: {error}"
    except Exception as e:
        return "Unable to create error message"


# Debug intents
debug_guild = int(os.getenv("DEBUG_GUILD"))
debug_channel = int(os.getenv("DEBUG_CHANNEL"))

# Define the on_ready event handler
@bot.event
async def on_ready():
    print("Bot is up and running...")
    # Set the bot's status
    await bot.change_presence(activity=discord.Game(name="/help for commands"))
    # Send a message to the server
    await bot.get_channel(debug_channel).send("Slash commands are ready to use")


# Define the /add command using the command decorator
@bot.command()
async def add(ctx, *, movie_details: str):
    # Use the Davinci-003 model to parse the natural language input and extract the movie details
    try:
        response = openai.Completion.create(
            engine="davinci-003",
            prompt=f"/add {movie_details}",
            max_tokens=1024,
            temperature=0.5,
        )
    except Exception as e:
        # Handle any errors that occurred
        await ctx.send(handle_error(e))
    else:
        # Add the movie to the logger
        result = add_movie(response.text.strip())
        if result:
            await ctx.send(result)

# Define the /delete command using the command decorator


@bot.command()
async def delete(ctx, *, movie_details: str):
    # Use the Davinci-003 model to parse the natural language input and extract the movie details
    try:
        response = openai.Completion.create(
            engine="davinci-003",
            prompt=f"/delete {movie_details}",
            max_tokens=1024,
            temperature=0.5,
        )
    except Exception as e:
        # Handle any errors that occurred
        await ctx.send(handle_error(e))
    else:
        # Delete the movie from the logger
        result = delete_movie(response.text.strip())
        if result:
            await ctx.send(result)

# Define the /search command using the command decorator


@bot.command()
async def search(ctx, *, query: str):
    # Search for movies in the logger
    result = search_movies(query)
    if result:
        await ctx.send(result)

# Define the /list command using the command decorator


@bot.command()
async def list(ctx):
    # Get the list of movies from the logger
    result = get_movie_list()
    if result:
        await ctx.send(result)
        
# Define the /help command using the command decorator


@bot.command()
async def help(ctx):
    message = """
    List of available commands:
    /add [movie_details] - adds a movie to the logger
    /delete [movie_details] - deletes a movie from the logger
    /list - lists all movies in the logger
    /search [query] - searches for movies in the logger
    /help - lists all available commands
    """
    await ctx.send(message)


# Handle command errors using the on_command_error event
@bot.event
async def on_command_error(ctx, error):
    # Send an error message if a CommandNotFound error occurred
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("Invalid command")

# Run the bot using the API key
bot.run(os.getenv("API_KEY"))