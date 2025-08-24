import os
import discord
import asyncpraw
import random
import logging
import asyncio
from dotenv import load_dotenv
from discord.ext import commands
from constants import MEME_SUBREDDIT_LIST

# --- LOAD ENVIRONMENT VARIABLES ---
load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
REDDIT_CLIENT_ID = os.getenv('REDDIT_CLIENT_ID')
REDDIT_CLIENT_SECRET = os.getenv('REDDIT_CLIENT_SECRET')
REDDIT_USER_AGENT = os.getenv('REDDIT_USER_AGENT')
REDDIT_USERNAME = os.getenv('REDDIT_USERNAME')
REDDIT_PASSWORD = os.getenv('REDDIT_PASSWORD')

# --- BOT SETUP ---
# Use commands.Bot instead of discord.Client
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# We will initialize the Reddit client when the bot is ready
reddit = None


# --- HELPER FUNCTION TO GET A MEME ---
async def get_meme(subreddit_name):
    """Fetches a random hot meme from a given subreddit."""
    try:
        subreddit = await reddit.subreddit(subreddit_name)
        hot_posts = [post async for post in subreddit.hot(limit=100) if not post.stickied]
        if not hot_posts:
            return None, f"Could not find any hot posts in r/{subreddit_name}."
        return random.choice(hot_posts), None
    except Exception as e:
        return None, f"Could not access subreddit r/{subreddit_name}. It might be private or banned. Error: {e}"


# --- BOT EVENTS ---
@bot.event
async def on_ready():
    global reddit
    logging.info(f'We have logged in as {bot.user}')
    logging.info('MemeBot is now online!')

    # Initialize the Reddit client
    reddit = asyncpraw.Reddit(
        client_id=REDDIT_CLIENT_ID,
        client_secret=REDDIT_CLIENT_SECRET,
        user_agent=REDDIT_USER_AGENT,
        username=REDDIT_USERNAME,
        password=REDDIT_PASSWORD,
    )

    try:
        logging.info(f"Logged into Reddit as {await reddit.user.me()}")
    except Exception as e:
        logging.info(f"Failed to log into Reddit: {e}")
    logging.info('-------------------------------------------------')


# --- BOT COMMANDS ---
@bot.command(name='meme', help='Posts a random meme from a default list of subreddits.')
async def meme(ctx):
    # Choose a random subreddit from our constants file
    random_subreddit = random.choice(MEME_SUBREDDIT_LIST)
    logging.info(f"Looking for random meme in r/{random_subreddit}")
    await ctx.send(f"Searching for a meme in r/{random_subreddit}...")

    random_post, error = await get_meme(random_subreddit)

    if error:
        await ctx.send(error)
        return

    post_url = random_post.url

    if post_url.endswith(('.jpg', '.jpeg', '.png', '.gif')):
        embed = discord.Embed(title=random_post.title, url=f"https://reddit.com{random_post.permalink}",
                              color=discord.Color.blue())
        embed.set_image(url=post_url)
        embed.set_footer(text=f"👍 {random_post.score} | 💬 {random_post.num_comments} | r/{random_subreddit}")
        await ctx.send(embed=embed)
    else:
        await ctx.send(f"**{random_post.title}**\n{post_url}")


@bot.command(name='memebomb', help='Posts 20 memes from the 5 default subreddits.')
async def meme_bomb(ctx):
    await ctx.send(f"🔥 MEME BOMB INCOMING! Fetching 20 memes from our top channels... 🔥")
    logging.info(f"Started fetching memes")

    memes_sent = 0
    for subreddit_name in MEME_SUBREDDIT_LIST:
        # Get 4 memes from each of the 5 subreddits (4 * 5 = 20)
        for _ in range(4):
            post, error = await get_meme(subreddit_name)
            if error:
                await ctx.send(error)
                continue

            # To avoid spamming embeds, we'll just post the links for the bomb
            await ctx.send(f"**{post.title}** (from r/{subreddit_name})\n{post.url}")
            memes_sent += 1
            # A small delay to avoid rate-limiting issues
            await asyncio.sleep(1)

    await ctx.send(f"✅ Meme bomb complete! Deployed {memes_sent} memes.")
    logging.info(f"✅ Meme bomb complete! Deployed {memes_sent} memes.")


# --- RUN THE BOT ---
bot.run(DISCORD_TOKEN)
