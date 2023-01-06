# Uncle-Movies
A Discord bot written in Python that uses the OpenAI API to assist users in managing a list of movies. It allows users to search, add, and delete movies from the list. It's purpose is to log movies that we watch on my discord server and keep track of them in a nice listed format.

To use the bot, users must first set their OpenAI API key using openai.api_key = 'YOUR_API_KEY'. They can then invoke the bot's commands by using the / prefix followed by the command name and any necessary arguments.

The available commands are:

`/add`: adds a movie to the list. The movie details must be provided as a natural language string (e.g. "Add the movie 'Inception' directed by Christopher Nolan and released in 2010"). The OpenAI API is used to parse the string and extract the relevant information.

`/delete`: deletes a movie from the list. The movie details must be provided as a natural language string (e.g. "Delete the movie 'Inception' directed by Christopher Nolan and released in 2010"). The OpenAI API is used to parse the string and extract the relevant information.

`/list`: lists all the movies in the list.

`/search`: searches the list for movies matching the provided query. The search is case-insensitive and matches partial strings.

`/help`: provides information on how to use the various commands available to users.

This bot can be useful for keeping track of movies that a user or a group of users have watched or are planning to watch. It allows users to easily add and delete movies from the list, and to search the list for specific movies.
