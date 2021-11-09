from discord.ext import commands
import discord
import youtube_dl

import os


global bot
bot = commands.Bot(command_prefix="!")


guilds = []

commands = ['!p']

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class MyFunctions():
    def __init__(self):
        self.queue = []
        self.guilds_queue = {}

    def delete(self,id):
        self.guilds_queue[id] = []

    def len(self,id):
        return len(self.guilds_queue[id])

    def create(self,id):
        self.guilds_queue[id] = []

    def add(self,id,URL):
        self.guilds_queue[id].append(URL)

    def get(self,id):
        return self.guilds_queue[id].pop(0)

    def getList(self,id):
        return self.guilds_queue[id]


in_queue = MyFunctions()
def song_from_in_queue(ctx):
    song = in_queue.get(ctx.guild.id)
    if ctx.voice_client:
        if not ctx.voice_client.is_playing() and in_queue.len(ctx.guild.id) != 0:
            play_song(ctx,song)

def play_song(ctx, URL):
    if not ctx.voice_client or ctx.voice_client.is_playing() == False:
        try:
            file = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(ytdl.extract_info(URL, download=False)['url']),1.0)
            ctx.voice_client.play(file, after=lambda err: print(err) if err else song_from_in_queue(ctx))
        except discord.errors.ClientException:
            pass

async def join(ctx):
    try:
        if ctx.voice_client:
            await ctx.voice_client.move_to(ctx.author.voice.channel)
        else:
            await ctx.author.voice.channel.connect()
    except Exception as e:
        print(e)


async def search(ctx, arg):
    info = ytdl.extract_info(f"ytsearch:{arg}", download=False)['entries'][0]
    print(info['duration'])
    return info['title'],info['formats'][1]['url']


@bot.command()
async def p(ctx, *args):
    if ctx.guild.id not in guilds:
        guilds.append(ctx.guild.id)
        in_queue.create(ctx.guild.id)
    to_queue = False
    URL = ''
    for a in args:
        URL += str(a)+" "
    print(f"!p request from {ctx.author.name}")
    async def http_play(ctx,URL,title):
        await ctx.send('Now playing -> {0}'.format(title))
        in_queue.add(ctx.guild.id,URL)
        play_song(ctx,URL)

    try:
        if URL.startswith('http'):
            if ctx.voice_client.is_playing():
                await ctx.send("To queue...")
                in_queue.add(ctx.guild.id,URL)

            elif not ctx.voice_client.is_playing():
                video = ytdl.extract_info(URL, download=False)
                await http_play(ctx,URL,video['title'])

        else:
            if ctx.voice_client.is_playing():
                to_queue = True
            raise Exception

    except:
        if URL:
            if URL.startswith('http'):
                await join(ctx)
                video = ytdl.extract_info(URL, download=False)
                await http_play(ctx,URL,video['title'])
            else:
                title,URL = await search(ctx,URL)
                if not to_queue:
                    await join(ctx)
                    video = ytdl.extract_info(URL, download=False)
                    await http_play(ctx,URL,title)
                else:
                    await ctx.send("To queue...")
                    in_queue.add(ctx.guild.id,URL)

        else:
            await ctx.send("Url error")

@bot.command()
async def s(ctx):
    ctx.voice_client.stop()

@bot.command()
async def pause(ctx):
    if ctx.voice_client:
        if ctx.voice_client.is_playing():
            ctx.voice_client.pause()
        else:
            ctx.voice_client.resume()
    else:
        await ctx.send("No playing!")

@bot.command()
async def dis(ctx):
    if len(bot.voice_clients) > 0:
        await bot.voice_clients[bot.voice_clients.index(ctx.voice_client)].disconnect()
        in_queue.delete(ctx.guild.id)
    else:
        await ctx.send("Not connected!")

@bot.command()
async def queue(ctx):
    if in_queue.len(ctx.guild.id) > 0:
        now_in_queue = in_queue.getListf(ctx.guild.id)[:5]
        i = 1
        mess = ''
        for msg in now_in_queue:
            mess += str(i)+'.'+ytdl.extract_info(URL, download=False)['title'] +'\n'
            i += 1
        await ctx.send(mess)
    else:
        await ctx.send("Queue is empty..")

@bot.command()
async def help(ctx):


@bot.event
async def on_ready():
    print(f"Logged as {bot.user.name} {bot.user.id}")
    await bot.change_presence(status = discord.Status.online, activity = discord.Game("!help"))

bot.run('OTA3MjAwMDg4NDI0NzM4ODQ2.YYjt7A.mWuVUBwD98FpYzt-0b1zxSHc0c0')