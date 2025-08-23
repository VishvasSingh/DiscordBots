import os
import discord
import asyncpraw
import random
from dotenv import load_dotenv

# --- LOAD ENVIRONMENT VARIABLES ---
load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
REDDIT_CLIENT_ID = os.getenv('REDDIT_CLIENT_ID')
REDDIT_CLIENT_SECRET = os.getenv('REDDIT_CLIENT_SECRET')
REDDIT_USER_AGENT = os.getenv('REDDIT_USER_AGENT')
REDDIT_USERNAME = os.getenv('REDDIT_USERNAME')
REDDIT_PASSWORD = os.getenv('REDDIT_PASSWORD')

# --- BOT SETUP ---
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# Declare reddit client in the global scope but initialize it later
reddit = None


# --- BOT EVENTS ---
@client.event
async def on_ready():
    global reddit  # Use the global reddit variable
    print(f'We have logged in as {client.user}')
    print('MemeBot is now online!')

    # Initialize the Reddit client here, inside the async context
    reddit = asyncpraw.Reddit(
        client_id=REDDIT_CLIENT_ID,
        client_secret=REDDIT_CLIENT_SECRET,
        user_agent=REDDIT_USER_AGENT,
        username=REDDIT_USERNAME,
        password=REDDIT_PASSWORD,
    )

    try:
        # A quick check to confirm Reddit login was successful
        print(f"Logged into Reddit as {await reddit.user.me()}")
    except Exception as e:
        print(f"Failed to log into Reddit: {e}")
    print('-------------------------------------------------')


@client.event
async def on_message(message):
    # Ignore messages from the bot itself and prevent commands before reddit is ready
    if message.author == client.user or reddit is None:
        return

    if message.content.startswith('!meme'):
        await message.channel.send("Hold on, finding a spicy meme...")
        try:
            subreddit_name = 'desimemes'
            subreddit = await reddit.subreddit(subreddit_name)

            # Fetch hot posts and filter out any stickied/pinned posts
            hot_posts = [post async for post in subreddit.hot(limit=100) if not post.stickied]

            if not hot_posts:
                await message.channel.send(f"Couldn't find any non-pinned hot posts in r/{subreddit_name} right now.")
                return

            random_post = random.choice(hot_posts)

            # Create and send the embed
            embed = discord.Embed(
                title=random_post.title,
                url=f"https://reddit.com{random_post.permalink}",
                color=discord.Color.blue()
            )
            embed.set_image(url=random_post.url)
            embed.set_footer(text=f"👍 {random_post.score} | 💬 {random_post.num_comments} | r/{subreddit_name}")

            await message.channel.send(embed=embed)

        except Exception as e:
            await message.channel.send(f"Sorry, I ran into an error: {e}")


# --- RUN THE BOT ---
try:
    client.run(DISCORD_TOKEN)
except discord.errors.LoginFailure:
    print("ERROR: Failed to log in. The Discord token is incorrect or invalid.")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
