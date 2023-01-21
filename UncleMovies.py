import re
import openai
import discord
import os
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
import asyncio
import json
import uuid

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
    try:
        with open("movies.json", "r") as json_file:
            data = json.load(json_file)
    except FileNotFoundError:
        return "movies.json file not found"
    else:
        movie_list = []
        for i, movie in enumerate(data["movies"]):
            movie_list.append(
                f"{i+1}. {movie['movie_name']} (UID: {movie['id']})")
        return "\n".join(movie_list)


# This function is used to search for movies in the logger (by searching the movie-log.txt file)


def search_movies(query, search_by="movie_name"):
    # Initialize an empty list to store search results
    search_results = []
    # Check if the query is an empty string
    if not query:
        return "The query cannot be an empty string."

    # Check if the search criteria is an empty string
    if not search_by:
        return "The search criteria cannot be an empty string."

    # Check if the search criteria is valid
    if search_by not in ["movie_name", "year", "director", "description", "genre"]:
        return "Invalid search criteria. Please choose from 'movie_name', 'year', 'director', 'description', or 'genre'."

    try:
        # Open the json file in read mode
        with open("movies.json", "r") as json_file:
            # Load the data from the json file
            data = json.load(json_file)
    except FileNotFoundError:
        return "movies.json file not found"
    else:
        # Iterate over each movie in the json data
        for movie in data["movies"]:
            # Check if the query matches the movie's title
            if search_by == "movie_name":
                if query.lower() in movie["movie_name"].lower():
                    search_results.append(f"{movie['movie_name']} (UID: {movie['id']})")
            # Check if the query matches the movie's year
            elif search_by == "year":
                if query.lower() in movie["year"].lower():
                    search_results.append(
                        f"{movie['movie_name']} - {movie['year']}")
            # Check if the query matches the movie's director
            elif search_by == "director":
                if query.lower() in movie["director"].lower():
                    search_results.append(
                        f"{movie['movie_name']} - {movie['director']}")
            # Check if the query matches the movie's description
            elif search_by == "description":
                if query.lower() in movie["description"].lower():
                    search_results.append(
                        f"{movie['movie_name']} - {movie['description']}")
            # Check if the query matches the movie's genre
            elif search_by == "genre":
                if query.lower() in movie["genre"].lower():
                    search_results.append(
                        f"{movie['movie_name']} - {movie['genre']}")

    # if no movies are found, return "No movies found"
    if not search_results:
        return "No movies found"
    # otherwise, return the search results
    return search_results

# This function is used to add a movie to the logger (by appending to the movie-log.txt file)


def add_movie(movie_name):
    # Check if the movie name is empty
    if not movie_name:
        return "The movie name cannot be an empty string."
    # Check if the movie already exists in the logger
    search_results = search_movies(movie_name)
    # If the movie already exists, return "Movie already exists"
    if len(search_results) > 0:
        return "'{movie_name}' already exists in the logger."


    # Set the prompt
    prompt = (f"Information about the movie {movie_name}\n"
              "Include the movie name, year, director, short description, and genre.")

    # Set the model to use for completion
    model = "text-davinci-003"

    # Set the number of completions to generate
    num_completions = 1

    # Set the temperature (controls the creativity of the completions)
    temperature = 0.5

    try:
        # Generate completions
        completions = openai.Completion.create(
            engine=model, prompt=prompt, max_tokens=2048, n=num_completions, temperature=temperature, format="text"
        )
    except openai.error.Timeout as e:
        # Handle timeout error, e.g. retry or log
        print(f"OpenAI API request timed out: {e}")
        pass
    except openai.error.APIError as e:
        # Handle API error, e.g. retry or log
        print(f"OpenAI API returned an API Error: {e}")
        pass
    except openai.error.APIConnectionError as e:
        # Handle connection error, e.g. check network or log
        print(f"OpenAI API request failed to connect: {e}")
        pass
    except openai.error.InvalidRequestError as e:
        # Handle invalid request error, e.g. validate parameters or log
        print(f"OpenAI API request was invalid: {e}")
        pass
    except openai.error.AuthenticationError as e:
        # Handle authentication error, e.g. check credentials or log
        print(f"OpenAI API request was not authorized: {e}")
        pass
    except openai.error.PermissionError as e:
        #Handle permission error, e.g. check scope or log
        print(f"OpenAI API request was not permitted: {e}")
        pass
    except openai.error.RateLimitError as e:
        #Handle rate limit error, e.g. wait or log
        print(f"OpenAI API request exceeded rate limit: {e}")
        pass


    # Get the first completion
    completion = completions.choices[0].text

    print(completion)
    
    # Extract the movie name, year, director, description, and genre from the completion
    movie_name = re.search("Movie Name:(.*)", completion).group(1).strip()
    year = re.search("Year:(.*)", completion).group(1).strip()
    director = re.search("Director:(.*)", completion).group(1).strip()
    description = re.search(
        "Description:(.*)", completion, re.DOTALL).group(1).strip()
    genre_matches = re.finditer("Genre:(.*?)\n", completion, re.DOTALL)
    genres = []
    for match in genre_matches:
        genres.append(match.group(1).strip())
    genre = ', '.join(genres)

    # Create a new movie object
    movie = {
        "id": uuid.uuid4().hex,
        "movie_name": movie_name,
        "year": year,
        "director": director,
        "description": description,
        "genre": genre
    }

    try:
        # open the json file in read mode
        with open("movies.json", "r") as json_file:
            # load the data from the json file
            data = json.load(json_file)
    # if the json file does not exist
    except FileNotFoundError:
        # create an empty json file with an empty array of movies
        data = {"movies": []}
        # open the json file in write mode
        with open("movies.json", "w") as json_file:
            # write the empty data to the json file
            json.dump(data, json_file)
    # if the json file exists
    else:
        # append the new movie to the array of movies
        data["movies"].append(movie)
        # open the json file in write mode
        with open("movies.json", "w") as json_file:
            # write the updated data to the json file
            json.dump(data, json_file)

    # Print a message to confirm that the movie was added
    print(f"Movie '{movie_name}' was added to the database.")


# This function is used to delete a movie from the logger (by overwriting the movie-log.txt file)


def delete_movie(movie_name_or_ID):
    # Open the movies.json file in read mode
    try:
        with open("movies.json", "r") as movie_log_file:
            movie_data = json.load(movie_log_file)
    except FileNotFoundError:
        return "movies.json file not found"
    except json.decoder.JSONDecodeError as e:
        return f"Error reading json file: {e}"

    # Check if the movie name or ID is empty
    if not movie_name_or_ID:
        return "The movie name or ID cannot be an empty string."

    # Find the movie to delete
    movie_to_delete = None
    for movie in movie_data:
        if movie_name_or_ID in (movie["movie_name"], movie["uniqueID"]):
            movie_to_delete = movie
            break
    else:
        return "Movie not found"

    # Remove the movie from the movie_data list
    movie_data.remove(movie_to_delete)
    # Open the movies.json file in write mode and write the updated movie_data list
    try:
        with open("movies.json", "w") as movie_log_file:
            json.dump(movie_data, movie_log_file)
    except Exception as e:
        return f"An error occurred: {e}"


# This function is used to update a movie in the logger (by overwriting the movie-log.txt file)


def update_movie(movie_name, field_to_update, new_value):
    try:
        # Open the json file in read mode
        with open("movies.json", "r") as json_file:
            # Load the data from the json file
            data = json.load(json_file)
    except FileNotFoundError:
        return "movies.json file not found"
    else:
        # Iterate over each movie in the json data
        for movie in data["movies"]:
            if movie["movie_name"].lower() == movie_name.lower():
                movie[field_to_update] = new_value
                break
        else:
            return f"Movie with name '{movie_name}' not found."
    # Open the json file in write mode
    with open("movies.json", "w") as json_file:
        # Write the updated data to the json file
        json.dump(data, json_file)
    return f"{field_to_update} of movie '{movie_name}' is updated to '{new_value}'"



# This function is used to sort the movies in the logger based on the specified criteria


def sort_movies(sort_by):
    # Read the movies from the json file and store them in a list
    try:
        with open("movies.json", "r") as json_file:
            data = json.load(json_file)
            movies = data["movies"]
    except FileNotFoundError:
        return "movies.json file not found"
    except Exception as e:
        return f"An error occurred: {e}"

    # Sort the list of movies based on the specified criteria
    if sort_by == "movie_name":
        sorted_movies = sorted(movies, key=lambda movie: movie["movie_name"])
        sorted_movies = [
            f"{movie['movie_name']} (UID: {movie['id']})" for movie in sorted_movies]
    elif sort_by == "year":
        sorted_movies = sorted(movies, key=lambda movie: movie["year"])
        sorted_movies = ["-".join([movie["movie_name"], movie["year"]])
                         for movie in sorted_movies]
    elif sort_by == "genre":
        sorted_movies = sorted(movies, key=lambda movie: movie["genre"])
        sorted_movies = ["-".join([movie["movie_name"], movie["genre"]])
                         for movie in sorted_movies]
    else:
        return "Invalid criteria. Please choose from 'movie_name', 'year', or 'genre'."

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


# Define the >movies command


@bot.command(name="movies")
async def movies(ctx):
    try:
        movie_list = get_movie_list()
    except FileNotFoundError:
        await ctx.send("movies.json file not found")
    else:
        await ctx.send(f"List of movies:\n{movie_list}")

# Define the >search command


@bot.command(name="search")
async def search(ctx, *, query):
    try:
        search_results = search_movies(query)
    except FileNotFoundError:
        await ctx.send("movies.json file not found")
    else:
        if search_results == "No movies found":
            await ctx.send("No movies found")
        else:
            await ctx.send(f"Search results:\n{search_results}")


# Define the >add command


@bot.command(name="add")
async def add(ctx, *, movie_details):
    if not movie_details:
        await ctx.send("No movie details provided")
    else:
        try:
            add_movie(movie_details)
        except FileNotFoundError:
            await ctx.send("movies.json file not found")
        else:
            await ctx.send(f"Added movie: {movie_details}")

# Define the >delete command


@bot.command(name="delete")
async def delete(ctx, *, movie_name):
    if not movie_name:
        await ctx.send("No movie name provided")
    else:
        try:
            delete_movie_status = delete_movie(movie_name)
        except FileNotFoundError:
            await ctx.send("movies.json file not found")
        else:
            if delete_movie_status == "Movie not found":
                await ctx.send("Movie not found")
            else:
                await ctx.send(f"Deleted movie: {movie_name}")

# Define the >update command


@bot.command(name="update")
async def update(ctx, movie_name: str, *, update_str: str):
    try:
        # Parse the update string to get the new movie details
        updates = {}
        for update in update_str.split(", "):
            key, value = update.split(": ")
            updates[key.lower()] = value

        # Call the update_movie() function
        result = update_movie(movie_name, **updates)
    except FileNotFoundError:
        await ctx.send("movies.json file not found")
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

# change to use json!!!
@bot.command(name="sort")
async def sort(ctx, sort_by: str):
    # Validate the sort criteria
    if sort_by not in ["movie_name", "year", "genre"]:
        await ctx.send("Invalid sort criteria. Please choose from 'movie_name', 'year', or 'genre'")
        return

    # Call the sort_movies function
    try:
        sorted_movies = sort_movies(sort_by)
    except FileNotFoundError:
        await ctx.send("movies.json file not found")
    except Exception as e:
        await ctx.send("An error occurred while sorting the movies: {}".format(e))
        return

    # Send the sorted movie list to the channel
    message = "\n".join(sorted_movies)
    await ctx.send(message)




# Handle command errors using the on_command_error event
@bot.event
async def on_command_error(ctx, error):
    # If the command has local error handler, return
    if hasattr(ctx.command, "on_error"):
        return

    # Get the original error
    error = getattr(error, "original", error)

    # Ignore the following errors
    ignored = (commands.CommandNotFound, commands.UserInputError)
    if isinstance(error, ignored):
        return

    # Log the error
    print(f"Error in command '{ctx.command}': {error}")

# Run the using the bot token
bot.run(os.getenv("DISCORD_BOT_TOKEN"))
