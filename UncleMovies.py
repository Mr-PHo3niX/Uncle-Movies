import re
import openai
import discord
import os
from discord.ext import commands
from dotenv import load_dotenv
import asyncio

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
bot = commands.Bot(command_prefix=">", intents=discord.Intents.all())

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


def search_movies(query, search_by="title"):
    search_results = []
    if not query:
        return "The query cannot be an empty string."

    if not search_by:
        return "The search criteria cannot be an empty string."

    if search_by not in ["title", "year", "director", "description", "genre"]:
        return "Invalid search criteria. Please choose from 'title', 'year', 'director', 'description', or 'genre'."
    
    try:
        with open("movie-log.txt", "r") as movie_log_file:
            for line in movie_log_file:
                if search_by == "title":
                    movie_title = line.split("\n")[0].split(": ")[1]
                    if query.lower() in movie_title.lower():
                        search_results.append(line.strip())
                # You can add more elif statements here to search by other criteria (e.g. year, director)
                elif search_by == "year":
                    movie_year = line.split("\n")[1].split(": ")[1]
                    if query.lower() in movie_year.lower():
                        search_results.append(line.strip())
                elif search_by == "director":
                    movie_director = line.split("\n")[2].split(": ")[1]
                    if query.lower() in movie_director.lower():
                        search_results.append(line.strip())
                elif search_by == "description":
                    movie_description = line.split("\n")[3].split(": ")[1]
                    if query.lower() in movie_description.lower():
                        search_results.append(line.strip())
                elif search_by == "genre":
                    movie_genre = line.split("\n")[4].split(": ")[1]
                    if query.lower() in movie_genre.lower():
                        search_results.append(line.strip())
    except FileNotFoundError:
        return "movie-log.txt file not found"
    else:
        if not search_results:
            return "No results found"
        return "\n".join(search_results)

# This function is used to add a movie to the logger (by appending to the movie-log.txt file)


def add_movie(movie_name):
    
    # Check if the movie name is empty
    if not movie_name:
        return "The movie name cannot be an empty string."
    
    # Check if the movie already exists in the logger
    if movie_name in search_movies(movie_name):
        return

    # Set the prompt
    prompt = f"Information about the movie {movie_name}"

    # Set the model to use for completion
    model = "text-davinci-002"

    # Set the number of completions to generate
    num_completions = 1

    # Set the temperature (controls the creativity of the completions)
    temperature = 0.5

    try:
        # Generate completions
        completions = openai.Completion.create(
            engine=model, prompt=prompt, max_tokens=1024, n=num_completions, temperature=temperature)
    except openai.api_error.ApiError as e:
        # Code to handle any errors that might occur when using the OpenAI API
        return "An error occurred when calling the OpenAI API: {}".format(e)
    except Exception as e:
        # Code to handle any other exceptions that might occur
        return "An unexpected error occurred: {}".format(e)

    # Get the first completion
    completion = completions.choices[0].text

    # Extract the information about the movie from the completion
    # You may need to modify the regular expression depending on the format of the completion
    try:
        movie_details = re.search(
            r"Movie: (.*)\nYear: (\d+)\nDirector: (.*)\nDescription: (.*)\nGenre: (.*)", completion).groups()
    except AttributeError:
        # Code to handle the AttributeError exception
        return "Unexpected format for completion returned by the OpenAI API"

    # Format the movie details
    movie_details = f"Movie: {movie_details[0]}\nYear: {movie_details[1]}\nDirector: {movie_details[2]}\nDescription: {movie_details[3]}\nGenre: {movie_details[4]}\n"

    try:
        # Code to write to the movie-log.txt file
        with open("movie-log.txt", "a") as movie_log_file:
            movie_log_file.write(f"{movie_details}\n")
    except FileNotFoundError:
        # Code to handle the FileNotFoundError exception
        return "movie-log.txt file not found"


# This function is used to delete a movie from the logger (by overwriting the movie-log.txt file)


def delete_movie(movie_name):
    # Get the list of movies
    movie_list = get_movie_list()
    
    # Check if the movie name is empty
    if not movie_name:
        return "The movie name cannot be an empty string."
    
    # Check if the movie exists in the list
    if movie_name  not in movie_list:
        return "Movie not found"


    # Set the prompt
    prompt = f"Information about movies in the logger except the movie {movie_name}"

    # Set the model to use for completion
    model = "text-davinci-002"

    # Set the number of completions to generate
    num_completions = 1

    # Set the temperature (controls the creativity of the completions)
    temperature = 0.5

    try:
        # Generate completions
        completions = openai.Completion.create(
            engine=model, prompt=prompt, max_tokens=1024, n=num_completions, temperature=temperature)
    except openai.api_error.ApiError as e:
        # Code to handle any errors that might occur when using the OpenAI API
        return "An error occurred when calling the OpenAI API: {}".format(e)

    # Get the first completion
    completion = completions.choices[0].text

    # Extract the information about the movies from the completion
    # You may need to modify the regular expression depending on the format of the completion
    try:
        movie_details = re.findall(
            r"Movie: (.*)\nYear: (\d+)\nDirector: (.*)\nDescription: (.*)\nGenre: (.*)", completion)
    except AttributeError:
        return "Unexpected format for completion returned by the OpenAI API"

    # Create a new list of movies that includes all movies except the one being deleted
    updated_movie_list = [
        f"Movie: {movie[0]}\nYear: {movie[1]}\nDirector: {movie[2]}\nDescription: {movie[3]}\nGenre: {movie[4]}\n" for movie in movie_details if movie[0] != movie_name]

    try:
        # Write the updated movie list to the movie-log.txt file
        with open("movie-log.txt", "w") as movie_log_file:
            for movie in updated_movie_list:
                movie_log_file.write(f"{movie}\n")
    except FileNotFoundError:
        return "movie-log.txt file not found"

# This function is used to update a movie in the logger (by overwriting the movie-log.txt file)

def update_movie(movie_name, new_movie_name=None, new_year=None, new_director=None, new_description=None, new_genre=None):
    # Read the movie-log.txt file into a list of lines
    try:
        with open("movie-log.txt", "r") as movie_log_file:
            lines = movie_log_file.readlines()
    except FileNotFoundError:
        return "movie-log.txt file not found"
    except Exception as e:
        return f"An error occurred: {e}"

    # Iterate through the lines and find the movie to update
    for i, line in enumerate(lines):
        if movie_name in line:
            # Split the line into movie details
            movie_details = line.split("\n")
            # Update the movie details
            if new_movie_name is not None:
                movie_details[0] = f"Movie: {new_movie_name}"
            if new_year is not None:
                movie_details[1] = f"Year: {new_year}"
            if new_director is not None:
                movie_details[2] = f"Director: {new_director}"
            if new_description is not None:
                movie_details[3] = f"Description: {new_description}"
            if new_genre is not None:
                movie_details[4] = f"Genre: {new_genre}"
            # Join the movie details back into a single line
            lines[i] = "\n".join(movie_details)
            break
    else:
        return "Movie not found"

    # Write the updated lines back to the movie-log.txt file
    try:
        with open("movie-log.txt", "w") as movie_log_file:
            movie_log_file.writelines(lines)
    except Exception as e:
        return f"An error occurred: {e}"
    

def sort_movies(sort_by):
    # Read the movies from the movie-log.txt file and store them in a list
    movies = []
    with open("movie-log.txt", "r") as movie_log_file:
        for line in movie_log_file:
            movies.append(line.strip())

    # Sort the list of movies based on the specified criteria
    if sort_by == "title":
        sorted_movies = sorted(
            movies, key=lambda movie: movie.split("\n")[0].split(": ")[1])
    elif sort_by == "year":
        sorted_movies = sorted(
            movies, key=lambda movie: movie.split("\n")[1].split(": ")[1])
    elif sort_by == "director":
        sorted_movies = sorted(
            movies, key=lambda movie: movie.split("\n")[2].split(": ")[1])
    elif sort_by == "description":
        sorted_movies = sorted(
            movies, key=lambda movie: movie.split("\n")[3].split(": ")[1])
    elif sort_by == "genre":
        sorted_movies = sorted(
            movies, key=lambda movie: movie.split("\n")[4].split(": ")[1])
    else:
        return "Invalid criteria. Specify a valid criteria (title, year, director, description, or genre)"

    return "\n".join(sorted_movies)




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

# Define the >help command


@bot.slash_command(name="help")
async def help(ctx):
    await ctx.send(
        "```List of available commands:\n>help - Shows this message\n>movies - Shows the list of movies in the logger\n>search <query> [search_by] - Searches for movies in the logger based on the given query and search criteria. The search criteria can be 'title', 'year', 'director', 'description', or 'genre'. If no search criteria is provided, the default is 'title'.\n>add <movie_name> - Adds a movie to the logger\n>delete <movie_name> - Deletes a movie from the logger\n>update <movie_name> <new_movie_name> <new_year> <new_director> <new_description> <new_genre> - Updates the movie details of the movie with the given name in the logger. Any field that you do not want to update can be left blank. \nExample: >update 'The Shawshank Redemption' 'The Shawshank Redemption' 1994 'Frank Darabont' 'Two imprisoned men bond over a number of years, finding solace and eventual redemption through acts of common decency.' 'Comedy'\n>sort <criteria> - Sorts the list of movies in the logger based on the given criteria. The criteria can be 'title', 'year', 'director', 'description', or 'genre'.\n```"
)


# Define the >movies command


@bot.command()
async def movies(ctx):
    try:
        movie_list = get_movie_list()
    except FileNotFoundError:
        await ctx.send("movie-log.txt file not found")
    else:
        await ctx.send(f"List of movies:\n{movie_list}")

# Define the >search command


@bot.command()
async def search(ctx, *, query):
    try:
        search_results = search_movies(query)
    except FileNotFoundError:
        await ctx.send("movie-log.txt file not found")
    else:
        if search_results == "No results found":
            await ctx.send("No results found")
        else:
            await ctx.send(f"Search results:\n{search_results}")

# Define the >add command


@bot.command()
async def add(ctx, *, movie_details):
    if not movie_details:
        await ctx.send("No movie details provided")
    else:
        try:
            add_movie(movie_details)
        except FileNotFoundError:
            await ctx.send("movie-log.txt file not found")
        else:
            await ctx.send(f"Added movie: {movie_details}")

# Define the >delete command


@bot.command()
async def delete(ctx, *, movie_details):
    if not movie_details:
        await ctx.send("No movie details provided")
    else:
        try:
            delete_movie_status = delete_movie(movie_details)
        except FileNotFoundError:
            await ctx.send("movie-log.txt file not found")
        else:
            if delete_movie_status == "Movie not found":
                await ctx.send("Movie not found")
            else:
                await ctx.send(f"Deleted movie: {movie_details}")

# Define the >update command


@bot.command()
async def update(ctx, movie_name: str, *, update_str: str):
    try:
        # Parse the update string to get the new movie details
        updates = {}
        for update in update_str.split(", "):
            key, value = update.split(": ")
            updates[key.lower()] = value

        # Call the update_movie() function
        result = update_movie(movie_name, **updates)
    except Exception as e:
        # Catch any errors that might occur and log them
        import logging
        logging.exception(e)
        await ctx.send("An error occurred while updating the movie")
    else:
        if result == "Movie not found":
            await ctx.send("Movie not found")
        else:
            await ctx.send("Movie updated successfully")
            
# Define the >sort command


@bot.command()
async def sort(ctx, sort_by: str):
    # Validate the sort criteria
    if sort_by not in ["title", "year", "director", "genre"]:
        await ctx.send("Invalid sort criteria. Please choose from 'title', 'year', 'director' or 'genre'")
        return

    # Call the sort_movies function
    try:
        sorted_movies = sort_movies(sort_by)
    except Exception as e:
        await ctx.send("An error occurred while sorting the movies: {}".format(e))
        return

    # Send the sorted movie list to the channel
    message = "\n".join(sorted_movies)
    await ctx.send(message)



# Handle command errors using the on_command_error event
@bot.event
async def on_command_error(ctx, error):
    # Ignore the CommandNotFound error
    if isinstance(error, commands.CommandNotFound):
        return

    # Handle other errors
    await ctx.send(handle_error(error))

# Run the using the bot token
bot.run(os.getenv("DISCORD_BOT_TOKEN"))
