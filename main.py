import discord
from discord.ext import commands
import logging
import requests
import asyncio
import sys
import traceback
from checkuser import is_valid_username
from getpic import get_roblox_avatar_url
from getuserid import get
import os
import platform
import psutil
import socket

#logging.basicConfig(level=logging.DEBUG)

# im not very good with python, if somthing can be optimized or redone in a simpler way let me know

UNIVERSE_ID = "7003688753"

fail = "<:ex:1323417818112200704>"
star = "<:yellowStar:1323398522933874790>"
mark = "<:question:1323422069492551872>"

activities = [
    ("Playing", "ggg3"),
    ("Watching", "ggg3"),
    ("Listening to", "ggg3"),
    ("Competing in", "ggg3")
]


with open("resources/roblox/test.key", "r") as api_key_file:
    API_KEY = api_key_file.read().strip()

with open("resources/discord/bot.key", "r") as bot_key_file:
    TOKEN = bot_key_file.read().strip()



intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

bot.remove_command("help")


REQUIRED_ROLE = "Founding fathers"


async def cycle_activities():
    """Background task to cycle through activities."""
    while True:
        for activity_type, activity_name in activities:
            if activity_type == "Playing":
                activity = discord.Game(name=activity_name)
            elif activity_type == "Watching":
                activity = discord.Activity(type=discord.ActivityType.watching, name=activity_name)
            elif activity_type == "Listening to":
                activity = discord.Activity(type=discord.ActivityType.listening, name=activity_name)
            elif activity_type == "Competing in":
                activity = discord.Activity(type=discord.ActivityType.competing, name=activity_name)
            else:
                continue

            await bot.change_presence(activity=activity)
            await asyncio.sleep(2)


async def read(DATASTORE_NAME, entry_key, ctx):

    print("read " + str(entry_key) + " from " + DATASTORE_NAME)
    BASE_URL = f"https://apis.roblox.com/datastores/v1/universes/{UNIVERSE_ID}/standard-datastores/datastore/entries"
    url = f"{BASE_URL}/entry?datastoreName={DATASTORE_NAME}&entryKey={entry_key}"

    headers = {
        "x-api-key": API_KEY,
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        print("Data retrieved successfully.")
        print("Response:", response.json())
        data = response.json()
        key_value = data
        return key_value

    else:
        print("Failed to retrieve data.")
        print("Status Code:", response.status_code)
        print("Response:", response.text)
        await ctx.send(response.text)
        return None




def remove_data(datastore_name, entry_key):
    base_url = f"https://apis.roblox.com/datastores/v1/universes/{UNIVERSE_ID}/standard-datastores/datastore/entries"
    url = f"{base_url}/entry?datastoreName={datastore_name}&entryKey={entry_key}"

    headers = {
        "x-api-key": API_KEY,
    }

    response = requests.delete(url, headers=headers)

    if response.status_code == 200:
        print("Data removed successfully.")
    else:
        print("Failed to remove data.")
        print("Status Code:", response.status_code)
        print("Response:", response.text)


def delete_key(datastore_name, key):
    base_url = "https://apis.roblox.com/datastores/v1/universes"
    endpoint = f"{base_url}/{UNIVERSE_ID}/standard-datastores/datastore/entries/entry"

    headers = {
        "x-api-key": API_KEY,
        "Content-Type": "application/json"
    }

    params = {
        "datastoreName": datastore_name,
        "entryKey": key
    }

    try:
        response = requests.delete(endpoint, headers=headers, params=params)

        if response.status_code == 204:
            print(f"Successfully deleted key '{key}' from datastore '{datastore_name}'.")
            return True
        elif response.status_code == 404:
            return False
        else:
            print(f"Failed to delete key. Status code: {response.status_code}")
            print(f"Error: {response.json()}")
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")




async def write(DATASTORE_NAME, entry_key, value, ctx):
    BASE_URL = f"https://apis.roblox.com/datastores/v1/universes/{UNIVERSE_ID}/standard-datastores/datastore/entries"
    url = f"{BASE_URL}/entry?datastoreName={DATASTORE_NAME}&entryKey={entry_key}"

    headers = {
        "x-api-key": API_KEY,
        "Content-Type": "application/json",
    }


    payload = value

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()  # Raise an error for HTTP errors
        print("Data written successfully:", response.json())
    except requests.exceptions.RequestException as e:
        print(f"Failed to write data: {e}")
        print("Response text:", response.text if response else "No response")




async def wait_for_user_message(ctx):
    """Waits for the user who ran the command to send a message and returns its content."""
    def check(message):
        return message.author == ctx.author and message.channel == ctx.channel

    try:
        user_message = await ctx.bot.wait_for('message', timeout=60.0, check=check)
        return user_message.content
    except asyncio.TimeoutError:
        await ctx.send(f"[{fail}] Response timeout")
        return None




async def input_username(ctx):
    while True:
        user = await wait_for_user_message(ctx)

        if user and user != "!":
            if is_valid_username(user):
                await ctx.send(get_roblox_avatar_url(user))
                return user
            else:
                await ctx.send(f"[{fail}] " + user + " is not a vaild roblox user, please enter a username or enter ! to cancel")
                continue
        else:
            return None






async def handle_game_command(command_string, ctx):
    if command_string == 'shutdown':
        await ctx.send(f"[{star}] Shutdown command recognized")
        # TODO: shutdown logic

    if command_string == 'exp':
        await ctx.send(f"[{mark}] Exp command recognized. Please enter the username of the user you wish to add or deduct Exp from, or enter `!` to cancel.")
        response = await input_username(ctx)
        if response and response != '!':
            await ctx.send(f"[{mark}] {response} has been selected. Please enter the amount to add (+amount) or deduct (-amount), or enter `!` to cancel.")
            response2 = await wait_for_user_message(ctx)

            if response2 and response2 != "!":
                try:
                    usid = get(response)
                    current = int(await read('DataPoints', usid, ctx))

                    if response2.startswith("-"):
                        deduct_amount = int(response2[1:])
                        new_exp = current - deduct_amount
                    elif response2.startswith("+"):
                        add_amount = int(response2[1:])
                        new_exp = current + add_amount
                    else:
                        add_amount = int(response2)
                        new_exp = current + add_amount

                    await write('DataPoints', usid, new_exp, ctx)
                    await ctx.send(f"[{star}] {response2} exp applied to {response}. New total: {new_exp}.")
                except ValueError:
                    await ctx.send(f"[{fail}] Invalid input format. Please provide a valid number.")
                except Exception as e:
                    await ctx.send(f"[{fail}] An error occurred: {str(e)}")
                    traceback.print_exc()
        else:
            await ctx.send(f"[{star}] Operation canceled")



    if command_string == 'ban':
        await ctx.send(f"[{mark}] Ban command recognized, please enter the username of the user you wish to ban or enter ! to cancel")
        user = await input_username(ctx)

        if user and user != '!':
            await ctx.send(f"[{mark}] " + user + " selected, proceed with ban? (y/n/!)")
            while True:
                yn = await wait_for_user_message(ctx)
                if yn and yn != '!':
                    if yn == 'y':
                        usid = get(user)

                        await write('bans', usid, 0, ctx)
                        await ctx.send(f"[{star}] user " + user + " banned, what a loser")
                        break
                    elif yn == 'n':
                        await ctx.send(f"[{star}] Operation canceled")
                        break
                    else:
                        await ctx.send(f"[{fail}] Invaild response, enter y for yes, n for no, or ! to cancel")
                        continue



                else:
                    await ctx.send(f"[{star}] Operation canceled")
                    break
        else:
            await ctx.send(f"[{star}] Operation canceled")



    if command_string == "unban":
        await ctx.send(f"[{mark}] Unban command recognized, please enter the username of the user you wish to unban or enter ! to cancel")
        user = await input_username(ctx)

        if user and user != "!":
            await ctx.send(f"[{mark}] " + user + " selected, proceed with unban? (y/n/!)")
            while True:
                yn = await wait_for_user_message(ctx)
                if yn and yn != '!':
                    if yn == 'y':
                        usid = get(user)
                        print(usid)
                        val = delete_key('bans', usid)
                        if val == True:
                            await ctx.send(f"[{star}] User " + user + " has been unbanned")
                        elif val == False:
                            await ctx.send(f"[{fail}] User " + user + " is not banned")
                        else:
                            await ctx.send(f"[{fail}] Unknown error occurred")
                        break
                    elif yn == 'n':
                        await ctx.send(f"[{star}] Operation canceled")
                        break
                    else:
                        await ctx.send(f"[{fail}] Invaild response, enter y for yes, n for no, or ! to cancel")
                        continue


                else:
                    await ctx.send(f"[{star}] Operation canceled")
                    break
        else:
            await ctx.send(f"[{star}] Operation canceled")








@bot.command(name='gamecmd')
async def gamecmd(ctx, *, command_string: str = None):
    """Handles the !gamecmd command."""
    if REQUIRED_ROLE in [role.name for role in ctx.author.roles]:
        if command_string != None:
            await ctx.send("[<:yellowStar:1323398522933874790>] Game command received")
            await handle_game_command(command_string, ctx)
        else:
            await ctx.send(f"[{fail}] No Argument provided")
    else:
        await ctx.send(f"[{fail}] You don't have the required role to use this command.")



@bot.command(name='end')
async def end(ctx):
    """Kills execution for this bot."""
    ALLOWED_USER_ID = 1255202317779599422  # me  -Zeus_gameover

    if ctx.author.id == ALLOWED_USER_ID:
        await ctx.send(f"Killing execution for [<@{bot.user.id}>]...")
        await bot.close()
        sys.exit(0)
    else:
        await ctx.send(f"[{fail}] You don't have permission to use this command.")

@bot.command(name='help')
async def help(ctx):
    with open("help.txt", "r") as file:
        help_text = file.read()
    await ctx.send(f"```{help_text}```")


@bot.command(name='host')
async def host(ctx):
    """gives host information about the bot."""
    if REQUIRED_ROLE in [role.name for role in ctx.author.roles]:
        try:
            hostname = socket.gethostname()
            ip_address = socket.gethostbyname(hostname)

            os_info = platform.system() + " " + platform.release()

            ram = psutil.virtual_memory()
            total_ram = ram.total / (1024**3)
            used_ram = ram.used / (1024**3)
            ram_usage_percentage = ram.percent

            response = (
                f"**Server/Host Information:**\n"
                f"📡 Internet Protocol Address: {ip_address}\n"
                f"🖥️  Operating System:Debian 12.2.0-14\n"
                f"💾 RAM Usage: {used_ram:.2f} GB / {total_ram:.2f} GB "
                f"({ram_usage_percentage}%)"
            )
            await ctx.send(response)


        except Exception as e:
            await ctx.send(f"[{fail}] An error occurred while retrieving server information: {e}")


    else:
        await ctx.send(f"[{fail}] You don't have permission to use this command")


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send(f"[{fail}] You don't have the required permissions to run this command.")
    else:
        raise error

@bot.event
async def on_ready():
    print(f"Successfuly logged in as {bot.user} (ID: {bot.user.id})")
    pid = os.getpid()
    activity = discord.Activity(
        type=discord.ActivityType.watching,
        name=f"the temple on PID {pid}"
    )
    await bot.change_presence(activity=activity)
    guild = bot.get_guild(1295887754177024080)
    if guild:
        await guild.me.edit(nick=f"Temple keeper")
    #bot.loop.create_task(cycle_activities())


bot.run(TOKEN)

