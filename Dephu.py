# ====================== [ I M P O R T I N G ] ======================
import discord
from discord.ext import commands
from discord.ext.commands import Bot
import json
import typing, os
from os import path
from discord import File
import aiohttp
import aiofiles
import random
import glob
import asyncio
from shutil import rmtree
from Private import Secrets

# ====================== [ I N I T I A L  S T A G E ] ======================
prefix = "-" #You can change this anytime for a different preffix
client = commands.Bot(command_prefix = prefix)
client.remove_command('help')

@client.event
async def on_ready():
    print ('Dephanae Speaking.') #You can change this for Bot Status (Visible)
    await client.change_presence(activity=discord.Game(name="-ping"))


os.chdir(os.getcwd())
# ====================== [ C O M M A N D S ] ======================
#CHECK PING
@client.command(aliases = ['ping', 'Ping'])
async def _ping(ctx):
    ping = round(client.latency * 1000)
    goodcomment = ["This seems good.","Your ping is perfect, Don't worry.", "Connection is decent"]
    badcomment =  ["Not acceptable.","High ping means awful connection", "Connection is terrible"]
    if ping < 300:
        comment = random.choice(goodcomment)
    else:
        comment = random.choice(badcomment)
    await ctx.send(f':ping_pong: **{ping}ms** ~ This is the reaction time of your connection \n {comment} :pen_ballpoint:')


#CLEAR CHATS
@client.command(aliases = ['clear', 'Clear'])
@commands.cooldown(1, 10, commands.BucketType.user)
@commands.has_permissions(administrator = True)
async def _clear(ctx, amount=5):
    amount += 1
    deleted = await ctx.channel.purge(limit=amount)
    name = ctx.author.name
    msg = f'I have deleted **{len(deleted) - 1}** message(s) for you, {name} :card_box: '
    message = await ctx.send(msg)
    await asyncio.sleep(5)
    await message.delete()

@_clear.error
async def _clear_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        msgs = ["Don't be so reckless.", "Overhasty as usual.", "Slowdown.", "You might get punished for being so impetuous", "..."]
        comment = random.choice(msgs)

        msg = comment + '\nTry again in {:.2f} seconds :clock:'.format(error.retry_after)
        await ctx.send(msg)
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send(f"You can't do that, {ctx.author.name}.")
    else:
        raise error

# ====================== [ B A C K  U P  C O M M A N D S ] ======================
#JSON
def getJson(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def saveJson(jsonstruct, path):
    with open(path, 'w', encoding='utf-8') as f:
         json.dump(jsonstruct, f, indent = 2)

#READING & DOWNLOADING FROM MESSAGE HISTORY
async def history(ctx, channel_name, path, atcpath):
    if channel_name == "Default":
        channel_name = ctx.channel.name
    files = glob.glob(f"{atcpath}/*")
    for f in files:
        os.remove(f)
    channel = discord.utils.get(ctx.guild.channels, name=channel_name)
    messages = await channel.history(limit=1000).flatten()
    jsonstruct = getJson(path)
    i = len(messages)
    jsonstruct.clear()
    for message in messages:
        content = message.content
        try:
            if message.content == "":
                jsonstruct[i] = f"."
            else:
                jsonstruct[i] = message.content

        except:
            print ("fail")
            pass
#Issue
        if (len(message.attachments) > 0):
            async with aiohttp.ClientSession() as session:
                url = message.attachments[0].proxy_url
                async with session.get(url) as resp:
                    if resp.status == 200:
                        f_data = await resp.read()
                        f_path = f"{i}.png"
                        print (atcpath)
                        f = open(atcpath + "/" + f_path, mode='wb')
                        f.write(f_data)
                        f.close()


        i -= 1

    saveJson(jsonstruct, path)

#LOADING VALUES
async def load(ctx, channel_name, path, atcpath):
    if channel_name == "Default":
        channel_name = ctx.channel.name
    chann = discord.utils.get(ctx.guild.channels, name=channel_name)
    messages = await chann.history(limit  =1000).flatten()
    jsonstruct = getJson(path)
    i = 1
    for i in reversed(jsonstruct):

        msg = jsonstruct[i]
        f_path = f"{i}.png"
        file = os.path.join(atcpath, f_path)
        print (file)

        try:
            with open(file, 'rb') as f:
                await chann.send(f"{msg}", file=File(f))
        except:
            await chann.send(f"{msg}")
            pass

    saveJson(jsonstruct, path)

#CREATING FOLDER IN THE RIGHT DIRECTION
@commands.has_permissions(administrator = True)
@client.command(aliases = ['create', 'createBU', 'createbu', 'createBu'])
async def _create(ctx, channel_name = "Default", full = False):
    if channel_name == "Default":
        channel_name = ctx.channel.name
        await ctx.message.delete()
    server_name = ctx.guild
    data = ".\Private\Data" + f"\{server_name}"
    json_file_name = channel_name + ".json"
    fullpath = os.path.join(data, channel_name)
    filepath = os.path.join(fullpath, json_file_name)

    if not os.path.exists(fullpath):
        os.makedirs(fullpath)
        atc = "\Attachments"
        atcpath = os.path.join(fullpath + atc )
        os.makedirs(atcpath)
        f = open(filepath, "w+")
        json.dump({}, f)
        if full == False:
            msg = await ctx.send("I created an empty backup of this channel. Do `-backup` to store information.")
            await asyncio.sleep(4)
            await msg.delete()

    else:
        if full == False:
            msg = await ctx.send("Backup file of this channel already exists. Do `-backup` to update the file.")
            await asyncio.sleep(4)
            await msg.delete()
    return

@_create.error
async def _create_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send(f"You can't do that, {ctx.author.name}.")
    else:
        raise error

#PUTTING DATA IN THE RIGHT DIRECTION
@commands.has_permissions(administrator = True)
@client.command(aliases = ['backup', 'Backup',])
async def _backup(ctx, channel_name = "Default", full = False):
    if channel_name == "Default":
        channel_name = ctx.channel.name
        await ctx.message.delete()
    server_name = ctx.guild
    data = ".\Private\Data" + f"\{server_name}"
    json_file_name = channel_name + ".json"
    fullpath = os.path.join(data, channel_name)
    filepath = os.path.join(fullpath, json_file_name)
    if not os.path.exists(fullpath):
        if full:
            await _create(ctx, channel_name, True)
        else:
            msg = await ctx.send("No backup file exists for this channel. Do `-create` or `-createBU` ")
            await asyncio.sleep(4)
            await msg.delete()

    else:
        atc = "\Attachments"
        atcpath = os.path.join(fullpath + atc )
        await history(ctx, channel_name, filepath, atcpath)
        if full == False:
            msg = await ctx.send(f"I created a new backup of this channel, {ctx.author.mention}.")
            await asyncio.sleep(4)
            await msg.delete()
    return

@_backup.error
async def _backup_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send(f"You can't do that, {ctx.author.name}.")
    else:
        raise error

#RECOVERING DATA WITH BACKUP
@client.command(aliases = ['load', 'loadBU', 'loadbu', 'loadBu'])
@commands.has_permissions(administrator = True)
async def load_backup(ctx, channel_name = "Default", full = False):
    if channel_name == "Default":
        channel_name = ctx.channel.name
        await ctx.message.delete()
    server_name = ctx.guild
    data = ".\Private\Data" + f"\{server_name}"
    json_file_name = channel_name + ".json"
    fullpath = os.path.join(data, channel_name)
    filepath = os.path.join(fullpath, json_file_name)

    if not os.path.exists(fullpath):
        if full == False:
            await ctx.send("No backup file exists for this channel. ")

    else:
        atc = "\Attachments"
        atcpath = os.path.join(fullpath + atc )
        await load(ctx, channel_name, filepath, atcpath)
        if full == False:
            msg = await ctx.send(f"I loaded the stored backup of this channel, {ctx.author.mention}.")
            await asyncio.sleep(4)
            await msg.delete()

@load_backup.error
async def load_backup_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send(f"You can't do that, {ctx.author.name}.")
    else:
        raise error
# ====================== [ FULL SERVER - VERSION] ======================
#CREATING THE SERVER DIRECTORY IN YOUR SYSTEM
@client.command(aliases = ['createFull', 'createFullBu', 'createfullbu', 'createfullBu', 'createfull'])
@commands.has_permissions(administrator = True)
async def _createFull(ctx):
    server_name = ctx.guild
    data = ".\Private\Data" + f"\{server_name}"
    if os.path.exists(data):
        await ctx.send("You already have a backup folder of this server. Do `-backupFull` to update everything.")
        return
    text_channel_list = []
    for channel in ctx.guild.text_channels:
        text_channel_list.append(channel)
    for i in text_channel_list:
        print(i)
        await _create(ctx, i.name, True)

@_createFull.error
async def _createFull_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send(f"You can't do that, {ctx.author.name}.")
    else:
        raise error

#BACKING UP ALL SERVER DATA FROM THE SERVER
@client.command(aliases = ['backupFull', 'backupfull'])
@commands.has_permissions(administrator = True)
async def _backupFull(ctx):
    text_channel_list = []
    for channel in ctx.guild.text_channels:
        text_channel_list.append(channel)
    for i in text_channel_list:
        await _backup(ctx, i.name, True)

@_backupFull.error
async def _backupFull_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send(f"You can't do that, {ctx.author.name}.")
    else:
        raise error

#UPLOADING ALL SERVER DATA FROM YOUR BACKUP IN THE RESPECTIVE CHANNELS
@client.command(aliases = ['loadFull', 'loadfull'])
@commands.has_permissions(administrator = True)
async def _loadFull(ctx):
    text_channel_list = []
    for channel in ctx.guild.text_channels:
        text_channel_list.append(channel)
    for i in text_channel_list:
        await load_backup(ctx, i.name, True)

@_loadFull.error
async def _loadFull_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send(f"You can't do that, {ctx.author.name}.")
    else:
        raise error


#CREATING ALL CHANNELS IF YOU HAVE THEIR BACKUP
@client.command(aliases = ['setFull', 'setfull'])
@commands.has_permissions(administrator = True)
async def _set(ctx):
    server_name = ctx.guild.name
    data = ".\Private\Data"
    fullpath = os.path.join(data, server_name)
    guild = ctx.message.guild
    if not os.path.exists(fullpath):
        await ctx.send("No backup file exists for this server. ")

    else:
        morestuff = os.listdir(fullpath)
        for i in morestuff:
            await guild.create_text_channel(i)

@_set.error
async def _set_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send(f"You can't do that, {ctx.author.name}.")
    else:
        raise error

#DELETING ALL CHANNELS IF YOU HAVE THEIR BACKUP
@client.command(aliases = ['deleteFull', 'deletefull'])
@commands.has_permissions(administrator = True)
async def _delete(ctx):
    server_name = ctx.guild.name
    data = ".\Private\Data"
    fullpath = os.path.join(data, server_name)
    guild = ctx.message.guild


    if not os.path.exists(fullpath):
        await ctx.send("No backup file exists for this server. ")

    else:
        morestuff = os.listdir(fullpath)
        for i in morestuff:
            existing_channel = discord.utils.get(guild.channels, name=i)
            await existing_channel.delete()
@_delete.error
async def _delete_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send(f"You can't do that, {ctx.author.name}.")
    else:
        raise error

# ====================== [ LAST STAGE - RUNNING ] ======================
client.run(Secrets.Token)

''' ================== ROUGH ========================

'''
