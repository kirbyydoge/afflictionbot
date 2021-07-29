print("PROCESS BEGIN")

from logging import error
import os

import discord
from discord.colour import Colour
from discord.ext import commands, tasks
from discord.utils import get
from googleapiclient.discovery import build

import botdb as bdb
from user import User

from globalvars import production

authorized_user = 165686666198122496 #cp memberi

EMPTY_CHAR = "\u200b"
GOOGLE_DEV_KEY = os.environ["GOOGLE_DEV_KEY"]
if production:
	BOT_TOKEN = os.environ["BOT_TOKEN"]
	client = commands.Bot(command_prefix="!ab ")
else:
	BOT_TOKEN = os.environ["TEST_TOKEN"]
	client = commands.Bot(command_prefix="!rb ")
client.remove_command("help")

error_buffer = []
cached_youtubers = []
cached_videos = None
youtube_channel = None
youtube = None

"""UTIL SETUP FUNCS"""
def load_youtubers():
	global cached_youtubers
	cached_youtubers = []
	youtubers = bdb.fetch_youtubers()
	for youtuber in youtubers:
		cached_youtubers.append((youtuber["name"], youtuber["url"]))

def update_cache():
	global cached_videos
	load_youtubers()
	for name, url in cached_youtubers:
		if not cached_videos.get(name):
			print(f"Initializing entry for {name}.")
			req = youtube.playlistItems().list(
				playlistId = url,
				part = "snippet",
				maxResults = 1
			)
			res = req.execute()
			video_id = res['items'][0]['snippet']['resourceId']['videoId']
			cached_videos[name] = video_id

"""MAIN BOT FUNCS"""
@client.command()
async def help(ctx:commands.Context, *arg):
	if len(arg) == 0:
		embed = discord.Embed(
			title = "Available Commands",
			color = discord.Colour.red()
		)
		message = "createevent\ndeleteevent\nlistevents\njoinevent\nleaveevent\nlistplayers"
		embed.add_field(name="Use <!ab help <command>> to display usage", value=message, inline=True)
		await ctx.send(embed=embed)
	elif len(arg) > 1:
		embed = discord.Embed(
			title = "Unsupported Format!",
			color = discord.Colour.red()
		)
		message = "<!ab help <command>> or <!ab help>"
		embed.add_field(name="Usage:", value=message, inline=True)
		await ctx.send(embed=embed)
	elif arg[0] == "createevent":
		embed = discord.Embed(
			title = "<!ab createevent <event_name>>",
			color = discord.Colour.red()
		)
		message = "Creates an event with requested name.\nRequires administrator permissions."
		embed.add_field(name="\u200b", value=message, inline=True)
		await ctx.send(embed=embed)
	elif arg[0] == "deleteevent":
		embed = discord.Embed(
			title = "<!ab deleteevent <event_id>",
			color = discord.Colour.red()
		)
		message = "Deletes the event with given id. Deleting with name is not allowed, as they are not strictly unique.\nRequires administrator permissions."
		embed.add_field(name="\u200b", value=message, inline=True)
		await ctx.send(embed=embed)
	elif arg[0] == "listevents":
		embed = discord.Embed(
			title = "<!ab listevents>",
			color = discord.Colour.red()
		)
		message = "Provides a <name, id> list of available events."
		embed.add_field(name="\u200b", value=message, inline=True)
		await ctx.send(embed=embed)
	elif arg[0] == "joinevent":
		embed = discord.Embed(
			title = "<!ab joinevent <event_id>",
			color = discord.Colour.red()
		)
		message = "Makes you join to the event <event_id>."
		embed.add_field(name="\u200b", value=message, inline=True)
		await ctx.send(embed=embed)
	elif arg[0] == "leaveevent":
		embed = discord.Embed(
			title = "<!ab leaveevent <event_id>>",
			color = discord.Colour.red()
		)
		message = "Removes you from the event <event_id>."
		embed.add_field(name="\u200b", value=message, inline=True)
		await ctx.send(embed=embed)
	elif arg[0] == "listplayers":
		embed = discord.Embed(
			title = "<!ab listplayers <event_id>>",
			color = discord.Colour.red()
		)
		message = "Provides a list of players in event <event_id>."
		embed.add_field(name="\u200b", value=message, inline=True)
		await ctx.send(embed=embed)
	elif arg[0] == "listme":
		embed = discord.Embed(
			title = "<!ab listme>",
			color = discord.Colour.red()
		)
		message = "Provides a list of events you are in."
		embed.add_field(name="\u200b", value=message, inline=True)
		await ctx.send(embed=embed)
	elif arg[0] == "addyoutuber":
		embed = discord.Embed(
			title = "<!ab addyoutuber <name>, <playlist_url>>",
			color = discord.Colour.red()
		)
		message = "Get notifications of uploads from the given list.\nYou need to obtain main list id if you want to follow the whole channel.\nPlease use 1 notification per youtuber."
		embed.add_field(name="\u200b", value=message, inline=True)
		await ctx.send(embed=embed)
	elif arg[0] == "deleteyoutuber":
		embed = discord.Embed(
			title = "<!ab deleteyoutuber name>",
			color = discord.Colour.red()
		)
		message = "Stop following youtuber notifications."
		embed.add_field(name="\u200b", value=message, inline=True)
		await ctx.send(embed=embed)
	elif arg[0] == "listyoutubers":
		embed = discord.Embed(
			title = "<!ab listyoutubers>",
			color = discord.Colour.red()
		)
		message = "Provides a list of youtuber notifications and lists."
		embed.add_field(name="\u200b", value=message, inline=True)
		await ctx.send(embed=embed)
	elif arg[0] == "setyoutubechannel":
		embed = discord.Embed(
			title = "<!ab listyoutubers>",
			color = discord.Colour.red()
		)
		message = "Set the main notification channel."
		embed.add_field(name="\u200b", value=message, inline=True)
		await ctx.send(embed=embed)

@client.event
async def on_ready():
	global youtube, youtube_channel, cached_videos, cached_youtubers
    print("Setting Up")
	youtube = build('youtube', 'v3', developerKey=GOOGLE_DEV_KEY)
	youtube_channel_id = bdb.youtube_channel_load()
	if youtube_channel_id:
		youtube_channel = await client.fetch_channel(youtube_channel_id)
	cached_videos = bdb.youtube_cache_load()
	if not cached_videos:
		print("Setting up new cache.")
		cached_videos = {}
	update_cache()
	youtube_check.start()
    print("Ready To Roll")

@tasks.loop(seconds=60)
async def youtube_check():
	load_youtubers()
	for youtuber in cached_youtubers:
		yt_name = youtuber[0]
		yt_url = youtuber[1]
		req = youtube.playlistItems().list(
			playlistId = yt_url,
			part = "snippet",
			maxResults = 1
		)
		res = req.execute()
		video_id = res['items'][0]['snippet']['resourceId']['videoId']
		try:
			if cached_videos[yt_name] != video_id:
				cached_videos[yt_name] = video_id
				message = f"{yt_name} posted a new video!\nVideo Link: https://www.youtube.com/watch?v={video_id}"
				if youtube_channel:
					await youtube_channel.send(message)
				else:
					print("NO CHANNEL SPECIFIED FOR NOTIFICATIONS")
		except:
			print(f"Error on: {yt_name}. (Ignore this if it does not keep repeating.)")
	bdb.youtube_cache_save(cached_videos)

@client.command()
@commands.has_permissions(administrator=True)
async def setyoutubechannel(ctx:commands.Context, *arg):
	global youtube_channel
	channel_id = ctx.message.channel.id
	bdb.youtube_channel_save(channel_id)
	youtube_channel = await client.fetch_channel(channel_id)

@client.command()
@commands.has_permissions(administrator=True)
async def createevent(ctx:commands.Context, *, arg=None):
	if arg is None:
		# Add error function later
		return
	bdb.create_event(arg)
	user = User(ctx)
	embed = user.get_embed(f"{user.username} created an event.")
	embed.add_field(name="Name", value=arg, inline=True)
	embed.set_thumbnail(url=user.picture)
	await ctx.send(embed=embed)

@client.command()
@commands.has_permissions(administrator=True)
async def deleteevent(ctx:commands.Context, *, arg=None):
	if arg is None:
		return
	args = arg.split(" ")
	if len(args) != 1:
		return
	event_id = int(args[0])
	name = bdb.get_event_name(event_id)
	bdb.delete_event(event_id)
	user = User(ctx)
	if name:
		embed = user.get_embed(f"{user.username} deleted an event.")
		embed.add_field(name="Name:", value=name, inline=True)
	else:
		embed = user.get_embed(f"{user.username} tried to delete an unexisting event.")
		embed.add_field(name="Unknown ID:", value=event_id, inline=True)
	await ctx.send(embed=embed)

@client.command()
@commands.has_permissions(administrator=True)
async def addyoutuber(ctx:commands.Context, *, arg=None):
	global cached_youtubers
	if arg is None:
		return
	arg = arg.replace(" ", "")
	args = arg.split(",")
	if len(args) != 2:
		return
	youtuber_name = args[0]
	youtuber_url = args[1]
	user = User(ctx)
	bdb.add_youtuber(youtuber_name, youtuber_url)
	embed = user.get_embed(f"{user.username} added youtuber {youtuber_name} to video notifications.")
	update_cache()
	bdb.youtube_cache_save(cached_videos)
	await ctx.send(embed=embed)

@client.command()
@commands.has_permissions(administrator=True)
async def deleteyoutuber(ctx:commands.Context, *, arg=None):
	global cached_youtubers
	if arg is None:
		return
	args = arg.split(",")
	if len(args) != 1:
		return
	youtuber_name = args[0]
	user = User(ctx)
	bdb.delete_youtuber(youtuber_name)
	embed = user.get_embed(f"{user.username} removed youtuber {youtuber_name} from video notifications.")
	del cached_videos[youtuber_name]
	bdb.youtube_cache_save(cached_videos)
	await ctx.send(embed=embed)

@client.command()
async def listyoutubers(ctx:commands.Context):
	user = User(ctx)
	youtubers = bdb.fetch_youtubers()
	embed = user.get_embed(f"{user.username} requested a list of video notifications:")
	nameText = ""
	urlText = ""
	count = 0
	for youtuber in youtubers:
		nameText += "{}\n".format(youtuber["name"])
		urlText += "{}\n".format(youtuber["url"])
		count += 1
	if len(nameText) == 0:
		nameText = "No youtuber found"
		urlText = "No youtuber found"
	embed.add_field(name="Youtuber Name", value=nameText, inline=True)
	embed.add_field(name="List URL", value=urlText, inline=True)
	embed.set_footer(text=f"Notification count: {count}")
	await ctx.send(embed=embed)
	
@client.command()
async def listevents(ctx:commands.Context):
	user = User(ctx)
	event_list = bdb.list_events()
	embed = user.get_embed(f"{user.username} requested a list of events available:")
	nameText = ""
	idText = ""
	count = 0
	for event in event_list:
		nameText += "{}\n".format(event["event_name"])
		idText += "{}\n".format(event["event_id"])
		count += 1
	if len(nameText) == 0:
		nameText = "No event found"
		idText = "No event found"
	embed.add_field(name="Event Name", value=nameText, inline=True)
	embed.add_field(name="Event ID", value=idText, inline=True)
	embed.set_footer(text=f"Event count: {count}")
	await ctx.send(embed=embed)

@client.command()
async def joinevent(ctx:commands.Context, *, arg=None):
	if arg is None:
		return
	args = arg.split(" ")
	if len(args) != 1:
		return
	event_id = int(args[0])
	user = User(ctx)
	result = bdb.add_user_to_event(event_id, user.user_id)
	if result == "noevent":
		embed = user.get_embed(f"There is no such event with id {event_id}.")
	elif result == "alreadyjoined":
		embed = user.get_embed(f"{user.username} is already in {bdb.get_event_name(event_id)}.")
		embed.set_footer(text=f"Total Contenders: {bdb.get_event_size(event_id)}")
	elif result == "success":
		embed = user.get_embed(f"{user.username} has joined to {bdb.get_event_name(event_id)}.")
		embed.set_footer(text=f"Total Contenders: {bdb.get_event_size(event_id)}")
	await ctx.send(embed=embed)
	
@client.command()
async def leaveevent(ctx:commands.Context, *, arg=None):
	if arg is None:
		return
	args = arg.split(" ")
	if len(args) != 1:
		return
	event_id = int(args[0])
	user = User(ctx)
	bdb.remove_user_from_event(event_id, user.user_id)
	embed = user.get_embed(f"{user.username} is no longer attending {bdb.get_event_name(event_id)}.") 
	await ctx.send(embed=embed)

@client.command()
async def listplayers(ctx:commands.Context, *, arg=None):
	if arg is None:
		return
	args = arg.split(" ")
	if len(args) != 1:
		return
	event_id = int(args[0])
	user = User(ctx)
	contenders = bdb.get_event_contenders(event_id)
	if contenders is None:
		return
	embed = discord.Embed(
		title = f"Contenders of {bdb.get_event_name(event_id)}",
		color = discord.Colour.red()
	)
	count = 0
	for contender in contenders:
		try:
			cur_cont = await ctx.guild.fetch_member(int(contender["user_id"]))
			name = cur_cont.display_name
			embed.add_field(name=name, value=EMPTY_CHAR)
			count += 1
		except:
			print(f"Deleted corrupted contender: {contender['user_id']}")
			bdb.remove_user_from_event(event_id, contender["user_id"])
	embed.set_footer(text=f"Total contenders: {count}")
	await ctx.send(embed=embed)

@client.command()
async def listme(ctx:commands.Context, *, arg=None):
	user = User(ctx)
	event_list = bdb.get_user_events(user.user_id)
	embed = user.get_embed(f"{user.username} has requested a list of events they are in:")
	nameText = ""
	idText = ""
	count = 0
	for event in event_list:
		name = bdb.get_event_name(event["event_id"])
		id = event["event_id"]
		nameText += "{}\n".format(name)
		idText += "{}\n".format(id)
		count += 1
	if len(nameText) == 0:
		nameText = "No event found"
		idText = "No event found"
	embed.add_field(name="Event Name", value=nameText, inline=True)
	embed.add_field(name="Event ID", value=idText, inline=True)
	embed.set_footer(text=f"Event count: {count}")
	await ctx.send(embed=embed)

@client.command()
async def viewerrorbuffer(ctx:commands.Context, *, arg=None):
	user = User(ctx)
	if user.user_id != authorized_user:
		embed = discord.Embed(
			title = "Authorized user only command",
			color = discord.Colour.red
		)
		return
	for content, guild_id, author_id, error in error_buffer:
		print("ERROR: message:{} server:{} author:{}".format(content, guild_id, author_id))
		print("ERROR:", error)

@client.command()
async def consumerrorbuffer(ctx:commands.Context, *, arg=None):
	global error_buffer
	user = User(ctx)
	if user.user_id != authorized_user:
		embed = discord.Embed(
			title = "Authorized user only command",
			color = discord.Colour.red
		)
		return
	error_buffer = []
	print("Success")

@help.error
@createevent.error
@listevents.error
@joinevent.error
@leaveevent.error
@listplayers.error
@listme.error
async def unresolved_error(ctx:commands.Context, error):
	error_buffer.append((ctx.message.content, ctx.message.guild.id, ctx.message.author.id, error))
	print("ERROR: message:{} server:{} author:{}".format(ctx.message.content, ctx.message.guild.id, ctx.message.author.id))
	print("ERROR:", error)
	embed = discord.Embed(
		title = "An unresolved error has occured. Make sure you have proper permissions for this command.",
		color = discord.Color.red()
	)
	embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/219037484531580929/764304895909298206/tenor.gif")
	embed.add_field(name="If you have other issues. You can contact me at:", value="Email: hoyfjeldsbildee@gmail.com\nInstagram: @kirbyydoge\nTwitter: @kirbyydoge", inline=True)
	embed.set_footer(text="Make sure your provide a brief explanation (if possible with screenshots) of how this bug occured.")
	await ctx.send(embed=embed)

client.run(BOT_TOKEN)
