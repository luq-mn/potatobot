# This project is licensed under the terms of the GPL v3.0 license. Copyright 2024 Cyteon


import random
import discord
import os
import aiohttp
import json
import requests
import io

from gtts import gTTS
from PIL import Image, ImageFilter
from io import BytesIO
from discord.ui import Button, View
from typing import List


from discord.ext import commands
from discord.ext.commands import Context
from PIL import Image, ImageDraw, ImageFont

from utils import Checks

subcommands = [
    "blur",
    "pixelate",
    "trigger",
    "jail",
    "wasted"
]

TENOR_API_KEY = os.getenv("TENOR_API_KEY")

# Here we name the cog and create a new class for the cog.

class TicTacToeButton(Button):
    def __init__(self, x: int, y: int, player_x: discord.Member, player_o: discord.Member):
        super().__init__(style=discord.ButtonStyle.secondary, label="\u200b", row=y)
        self.x = x
        self.y = y
        self.player_x = player_x
        self.player_o = player_o

    async def callback(self, interaction: discord.Interaction):
        view: TicTacToeView = self.view
        if interaction.user != view.current_player:
            await interaction.response.send_message("It's not your turn!", ephemeral=True)
            return

        if self.label == "\u200b":
            self.label = "X" if view.current_player == self.player_x else "O"
            self.style = discord.ButtonStyle.danger if view.current_player == self.player_x else discord.ButtonStyle.primary
            self.disabled = True
            view.board[self.x][self.y] = 1 if view.current_player == self.player_x else -1
            view.current_player = self.player_o if view.current_player == self.player_x else self.player_x

            await interaction.response.edit_message(content=f"{view.current_player.mention}, your turn.", view=view)

            winner = view.check_winner()
            if winner:
                await interaction.followup.send(f"{winner.mention} wins!", ephemeral=False)
                view.stop()
            elif all(cell != 0 for row in view.board for cell in row):
                await interaction.followup.send("It's a tie!", ephemeral=False)
                view.stop()
        else:
            await interaction.response.send_message("This button is already clicked!", ephemeral=True)

class TicTacToeView(View):
    def __init__(self, player_x: discord.Member, player_o: discord.Member):
        super().__init__(timeout=None)
        self.player_x = player_x
        self.player_o = player_o
        self.current_player = player_x
        self.board = [[0 for _ in range(3)] for _ in range(3)]

        for x in range(3):
            for y in range(3):
                self.add_item(TicTacToeButton(x, y, player_x, player_o))

    def check_winner(self):
        for row in self.board:
            if sum(row) == 3:
                return self.player_x
            elif sum(row) == -3:
                return self.player_o

        for col in range(3):
            if self.board[0][col] + self.board[1][col] + self.board[2][col] == 3:
                return self.player_x
            elif self.board[0][col] + self.board[1][col] + self.board[2][col] == -3:
                return self.player_o

        if self.board[0][0] + self.board[1][1] + self.board[2][2] == 3:
            return self.player_x
        elif self.board[0][0] + self.board[1][1] + self.board[2][2] == -3:
            return self.player_o

        if self.board[0][2] + self.board[1][1] + self.board[2][0] == 3:
            return self.player_x
        elif self.board[0][2] + self.board[1][1] + self.board[2][0] == -3:
            return self.player_o

        return None

class Fun(commands.Cog, name="🎉 Fun"):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.command(
        name="joos",
        description="joos",
        usage="joos"
    )
    @commands.check(Checks.is_not_blacklisted)
    async def joos(self, context: Context) -> None:
        await context.send("<:joos:1254878760218529873>")

    @commands.hybrid_command(
        name="http",
        description="Get image of cats representing http codes",
        usage="http <code>"
    )
    @commands.check(Checks.is_not_blacklisted)
    async def http(self, context: Context, code) -> None:
        await context.send(f"https://http.cat/{code}.jpg")

    @commands.hybrid_command( # TODO: fix this crap
        name="bored",
        description="Get an activity if you are bored"
    )
    @commands.check(Checks.is_not_blacklisted)
    async def bored(self, context: Context) -> None:
        async with aiohttp.ClientSession() as session:
            url="https://bored-api.appbrewery.com/random"

            #if participants > 0:
                #url = "https://bored-api.appbrewery.com/filter"

                #url = f"{url}?participants={str(participants)}"

            async with session.get(url) as r:
                if r.status == 200:
                    data = await r.json()

                    embed = discord.Embed()

                    if "error" in data:
                        embed = discord.Embed(title=data["error"], color=discord.Color.brand_red())
                    else:
                        embed = discord.Embed(title=data["activity"], color=discord.Color.teal())

                        embed.add_field(name = "Type", value = data["type"].capitalize())
                        embed.add_field(name = "Participants", value = data["participants"])
                        embed.add_field(name = "Price", value = data["price"])

                    await context.send(embed=embed)
                elif r.status == 404:
                    embed = discord.Embed(title="No activities found", color=discord.Color.brand_red())

                    await context.send(embed=embed)
                else:
                    await context.send(f"BoredAPI is currently experiencing issues Status")
    @commands.hybrid_command(
        name="advice",
        description="Get some advice",
        usage="advice"
    )
    @commands.check(Checks.is_not_blacklisted)
    async def advice(self, context: Context) -> None:
        async with aiohttp.ClientSession() as session:
            r = requests.get("https://api.adviceslip.com/advice")
            data = json.loads(r.text)

            await context.send(data["slip"]["advice"])

    @commands.hybrid_command(
        name="insult",
        description="Get an insult"
    )
    @commands.check(Checks.is_not_blacklisted)
    async def insult(self, context: Context) -> None:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://evilinsult.com/generate_insult.php?lang=en&type=json") as r:
                if r.status == 200:
                    data = await r.json()

                    await context.send(data["insult"])

    @commands.hybrid_command(
        name="cat",
        description="Get a random cat image",
        usage="cat"
    )
    @commands.check(Checks.is_not_blacklisted)
    async def cat(self, context: Context) -> None:

        async with aiohttp.ClientSession() as session:
            data = await session.get(
                "https://some-random-api.com/animal/cat"
            )

            data = await data.json()

            img = await session.get(
                data["image"]
            )

            imageData = io.BytesIO(await img.read())
            await context.send(file=discord.File(imageData, "cat.png"))

    @commands.hybrid_command(
        name="dog",
        description="Get a random dog image",
        usage="dog"
    )
    @commands.check(Checks.is_not_blacklisted)
    async def dog(self, context: Context) -> None:

        async with aiohttp.ClientSession() as session:
            data = await session.get(
                "https://some-random-api.com/animal/dog"
            )

            data = await data.json()

            img = await session.get(
                data["image"]
            )

            imageData = io.BytesIO(await img.read())
            await context.send(file=discord.File(imageData, "dog.png"))

    @commands.hybrid_command(
        name="gif",
        description="Get a random gif, unless query is specified",
        usage="gif [optional: query]"
    )
    @commands.check(Checks.is_not_blacklisted)
    async def gif(self, context: Context, *, query="NONE") -> None:
        rand = False
        if query == "NONE":
            #get random from array
            query = random.choice(
                [
                    "bored",
                    "exited",
                    "happy",
                    "sad",
                    "angry",
                    "confused",
                    "crying",
                    "cat",
                    "dog",
                    "slap",
                    "animal",
                    "building",
                    "car",
                    "technology",
                    "random",
                    "plane"
                ]
            )
            rand = True

        async with aiohttp.ClientSession() as session:
            data = await session.get(
                f"https://tenor.googleapis.com/v2/search?random={rand}&q={query}&key=" + TENOR_API_KEY
            )

            data = await data.json()

            img = await session.get(
                data["results"][0]["media_formats"]["gif"]["url"]
            )



            #await context.send(data["data"]["embed_url"])

            imageData = io.BytesIO(await img.read())
            await context.send(file=discord.File(imageData, "gif.gif"))

    @commands.hybrid_group(
        name="avatar",
        description="Commands for avatar manipulation",
        usage="avatar <subcommand>"
    )
    @commands.check(Checks.is_not_blacklisted)
    async def avatar(self, context: Context) -> None:
        embed = discord.Embed(
            title="Avatar",
            description="Commands"
        )

        # get all subcommands in group

        subcommands = [cmd for cmd in self.avatar.walk_commands()]

        data = []

        for subcommand in subcommands:
            description = subcommand.description.partition("\n")[0]
            data.append(f"{await self.bot.get_prefix(context)}avatar {subcommand.name} - {description}")

        help_text = "\n".join(data)
        embed = discord.Embed(
            title=f"Help: Avatar", description="List of available commands:", color=0xBEBEFE
        )
        embed.add_field(
            name="Commands", value=f"```{help_text}```", inline=False
        )

        await context.send(embed=embed)

    @avatar.command(
        name="get",
        description="Get someone's avatar",
        usage="avatar get [optional: user]"
    )
    @commands.check(Checks.is_not_blacklisted)
    async def get(self, context: Context, user: discord.User = None) -> None:
        if not user:
            user = context.author

        embed = discord.Embed(
            title=f"{user.name}'s Avatar",
            color=discord.Color.blurple()
        )

        embed.set_image(url=user.display_avatar.url)

        await context.send(embed=embed)

    @avatar.command(
        name="blur",
        description="Blur someone",
        usage="avatar blur [optional: user]"
    )
    @commands.check(Checks.is_not_blacklisted)
    async def blur(self, context: Context, user: discord.User = None) -> None:
        if not user:
            user = context.author

        async with aiohttp.ClientSession() as session:
            img = await session.get(
                f"https://some-random-api.com/canvas/misc/blur?avatar={user.display_avatar.url}"
            )

            imageData = io.BytesIO(await img.read())
            await context.send(file=discord.File(imageData, "blur.png"))

        #await context.send("https://some-random-api.com/canvas/overlay/triggered?avatar=" + user.display_avatar.url)
    @avatar.command(
        name="pixelate",
        description="Pixelate someone",
        usage="avatar pixelate [optional: user]"
    )
    @commands.check(Checks.is_not_blacklisted)
    async def pixelate(self, context: Context, user: discord.User = None) -> None:
        if not user:
            user = context.author

        async with aiohttp.ClientSession() as session:
            img = await session.get(
                f"https://some-random-api.com/canvas/misc/pixelate?avatar={user.display_avatar.url}"
            )

            imageData = io.BytesIO(await img.read())
            await context.send(file=discord.File(imageData, "pixelate.png"))

    @avatar.command(
        name="trigger",
        description="Trigger someone",
        usage="avatar trigger [optional: user]"
    )
    @commands.check(Checks.is_not_blacklisted)
    async def trigger(self, context: Context, user: discord.User = None) -> None:
        if not user:
            user = context.author

        async with aiohttp.ClientSession() as session:
            img = await session.get(
                f"https://some-random-api.com/canvas/overlay/triggered?avatar={user.display_avatar.url}"
            )

            imageData = io.BytesIO(await img.read())
            await context.send(file=discord.File(imageData, "triggered.gif"))

    @avatar.command(
        name="jail",
        description="Put someone in jail",
        usage="avatar jail [optional: user]"
    )
    @commands.check(Checks.is_not_blacklisted)
    async def jail(self, context: Context, user: discord.User = None) -> None:
        if not user:
            user = context.author

        async with aiohttp.ClientSession() as session:
            img = await session.get(
                f"https://some-random-api.com/canvas/overlay/jail?avatar={user.display_avatar.url}"
            )

            imageData = io.BytesIO(await img.read())
            await context.send(file=discord.File(imageData, "jail.png"))

    @avatar.command(
        name="wasted",
        description="Wasted",
        usage="avatar wasted [optional: user]"
    )
    @commands.check(Checks.is_not_blacklisted)
    async def wasted(self, context: Context, user: discord.User = None) -> None:
        if not user:
            user = context.author

        async with aiohttp.ClientSession() as session:
            img = await session.get(
                f"https://some-random-api.com/canvas/overlay/wasted?avatar={user.display_avatar.url}"
            )

            imageData = io.BytesIO(await img.read())
            await context.send(file=discord.File(imageData, "wasted.png"))

    @commands.hybrid_command(
        name="ttt",
        description="Play a game of Tic-Tac-Toe",
        usage="ttt <opponent>"
    )
    @commands.check(Checks.is_not_blacklisted)
    async def tictactoe(self, context: Context, opponent: discord.Member) -> None:
        """Start a game of Tic-Tac-Toe with the specified opponent."""

        if opponent == context.author:
            await context.send("You cannot play against yourself!")
            return

        if opponent.bot:
            await context.send("You cannot play against bots!")
            return

        await context.send(f"{context.author.mention} vs {opponent.mention}!", view=TicTacToeView(context.author, opponent))

# And then we finally add the cog to the bot so that it can load, unload, reload and use it's content.
async def setup(bot) -> None:
    await bot.add_cog(Fun(bot))
