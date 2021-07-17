import os

import discord
from discord.ext import commands
from discord.utils import get

import botdb as bdb
from user import User

EMPTY_CHAR = "\u200b"
TOKEN = os.environ["BOT_TOKEN"]
client = commands.Bot(command_prefix="!ab ")
client.remove_command("help")

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
    embed.add_field(name="Event Name", value=nameText, inline=True)
    embed.add_field(name="Event ID", value=idText, inline=True)
    embed.set_footer(text=f"Event count: {count}")
    await ctx.send(embed=embed)

@help.error
@createevent.error
@listevents.error
@joinevent.error
@leaveevent.error
@listplayers.error
@listme.error
async def unresolved_error(ctx:commands.Context, error):
    print("ERROR: message:{} server:{} author:{}".format(ctx.message.content, ctx.message.guild.id, ctx.message.author.id))
    print("ERROR:", error)
    embed = discord.Embed(
        title = "An unresolved error has occured. Make sure you have proper permissions for this command.",
        color = discord.Color.red()
    )
    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/219037484531580929/764304895909298206/tenor.gif")
    embed.add_field(name="If you have other issues. You can contact me at:", value="Email: hoyfjeldsbildee@gmail.com\nInstagram: @kirbyydoge", inline=True)
    embed.set_footer(text="Make sure your provide a brief explanation (if possible with screenshots) of how this bug occured.")
    await ctx.send(embed=embed)

client.run(TOKEN)