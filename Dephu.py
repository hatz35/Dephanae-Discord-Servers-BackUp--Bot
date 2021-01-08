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

# ====================== [ INITIAL STAGE ] ======================
prefix = "-"
client = commands.Bot(command_prefix = prefix)
client.remove_command('help')

@client.event
async def on_ready():
    print ('Dephanae Speaking.')
    await client.change_presence(activity=discord.Game(name="-ping"))


os.chdir(os.getcwd())


# ====================== [COMMANDS] ======================
@client.command(aliases = ['test', 'Test'])
async def _test(ctx):
    text_channel_list = []
    for channel in ctx.guild.text_channels:
        text_channel_list.append(channel)
    print(text_channel_list)
    for i in text_channel_list:
        await ctx.send(f'{i}')


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

# ====================== [ BACKUP ] ======================
def getJson(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def saveJson(jsonstruct, path):
    with open(path, 'w', encoding='utf-8') as f:
         json.dump(jsonstruct, f, indent = 2)

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
#STUPID COMMAND NOW -> CAN DO MANUAL
'''
@client.command(aliases = ['delete', 'deleteBU', 'deletebu', 'deleteBu'])
async def delete_backup(ctx):
    channel_name  = ctx.channel.name
    data = ".\Private\Data"
    json_file_name = channel_name + ".json"
    fullpath = os.path.join(data, channel_name)
    filepath = os.path.join(fullpath, json_file_name)
    await ctx.message.delete()

    if not os.path.exists(fullpath):
        msg = await ctx.send("No backup file exists for this channel.")
        await asyncio.sleep(4)
        await msg.delete()

    else:
        rmtree(fullpath)
        msg = await ctx.send("I deleted the backup of this channel.")
        await asyncio.sleep(4)
        await msg.delete()
'''

@client.command(aliases = ['load', 'loadBU', 'loadbu', 'loadBu'])
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

@client.command(aliases = ['edit'])
async def _edit(ctx, tokenID, *, newtext: typing.Optional[str]):
    messages = await ctx.channel.history(limit=1000).flatten()
    token_id = int(tokenID)
    print (token_id)
    for message in messages:

        if token_id > 100 and token_id < 1000:
            search = message.content[3:6]
        elif token_id > 10 and token_id < 100:
            search = message.content[3:5]
        elif token_id > 0 and token_id < 10:
            search = message.content[3:4]
        else:
            print("TokenFail?")

        print(search)
        if search == tokenID:
            await message.edit(content=f"**[{tokenID}]**\n\n " + newtext)
            break
        else:
            print(0)
    await asyncio.sleep(3)
    await ctx.message.delete()

# ====================== [ FULL SERVER - VERSION] ======================
@client.command(aliases = ['createFull', 'createFullBu', 'createfullbu', 'createfullBu', 'createfull'])
async def _createFull(ctx):
    text_channel_list = []
    for channel in ctx.guild.text_channels:
        text_channel_list.append(channel)
    for i in text_channel_list:
        print(i)
        await _create(ctx, i.name, True)



@client.command(aliases = ['backupFull', 'backupfull'])
async def _backupFull(ctx):
    text_channel_list = []
    for channel in ctx.guild.text_channels:
        text_channel_list.append(channel)
    for i in text_channel_list:
        await _backup(ctx, i.name, True)


@client.command(aliases = ['loadAll', 'loadall'])
async def _loadFull(ctx):
    text_channel_list = []
    for channel in ctx.guild.text_channels:
        text_channel_list.append(channel)
    for i in text_channel_list:
        await load_backup(ctx, i.name, True)

@client.command(aliases = ['setAll', 'setall'])
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

@client.command(aliases = ['jettAll', 'jettall'])
async def _jettAll(ctx):
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


# ====================== [ LAST STAGE - RUNNING ] ======================
client.run(Secrets.Token)

''' ================== ROUGH ========================

'''
