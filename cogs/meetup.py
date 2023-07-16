import pprint
import traceback

import discord
from discord import ScheduledEvent, app_commands
from discord.ext import commands

from helpers import checks, db_manager, meetup_api


class Token(discord.ui.Modal, title="Meetup.com Token"):
    token = discord.ui.TextInput(
        label="Meetup.com Token",
        placeholder="Enter your Meetup.com token here...",
        required=True,
    )

    async def on_submit(self, interaction: discord.Interaction):
        token = self.token.value

        # Perform authentication using the token
        try:
            response = await meetup_api.get_access_token(token)
            pprint.pprint(response)

            if "access_token" in response:
                access_token = response["access_token"]
                await interaction.response.send_message(
                    f"Success! Access Token: {access_token}", ephemeral=True
                )
                # Save the token to the database
                server_id = interaction.guild.id  # Assuming guild-specific tokens
                expires_in = response["expires_in"]
                refresh_token = response["refresh_token"]
                await db_manager.save_meetup_token(
                    server_id, access_token, expires_in, refresh_token, "bearer"
                )
            else:
                error = response["error"]
                await interaction.response.send_message(
                    f"Failed to obtain access token. Error: {error}", ephemeral=True
                )
        except Exception as e:
            await interaction.response.send_message(
                f"An error occurred during authentication: {str(e)}", ephemeral=True
            )

    async def on_error(
        self, interaction: discord.Interaction, error: Exception
    ) -> None:
        await interaction.response.send_message(
            "Oops! Something went wrong.", ephemeral=True
        )
        # Make sure we know what the error actually is
        traceback.print_tb(error.__traceback__)


class Meetup(commands.Cog, name="meetup"):
    def __init__(self, bot):
        self.bot = bot
        self.channel_id = 1057047905262911540

    @app_commands.command(
        name="authenticate", description="Authenticate with Meetup.com"
    )
    async def authenticate(self, interaction: discord.Interaction):
        # Step 1: Redirect user to authorization URL
        authorization_url = await meetup_api.get_authorization_url()
        await interaction.response.send_message(
            f"Authenticate with meeup.com:\n {authorization_url}", ephemeral=True
        )

    @app_commands.command(name="paste_token", description="Paste your meetup.com token")
    async def paste_token(self, interaction: discord.Interaction):
        await interaction.response.send_modal(Token())

    @commands.Cog.listener()
    async def on_scheduled_event_create(self, event: ScheduledEvent):
        channel = self.bot.get_channel(self.channel_id)
        message = (
            f"New event created in {event.guild.name} (ID: {event.guild.id}) by {event.creator} (ID: {event.creator_id})\n"
            f"Event name: {event.name}\n"
            f"Event description: {event.description}\n"
            f"Event start time: {event.start_time}\n"
            f"Event end time: {event.end_time}\n"
            F"Event image: {event.cover_image.url}"
        )
        self.bot.logger.info(message)
        await channel.send(message)

    @commands.Cog.listener()
    async def on_scheduled_event_update(
        self, before: ScheduledEvent, event: ScheduledEvent
    ):
        channel = self.bot.get_channel(self.channel_id)
        message = (
            f"Event updated in {event.guild.name} (ID: {event.guild.id}) by {event.creator} (ID: {event.creator_id})\n"
            f"Event name: {event.name}\n"
            f"Event description: {event.description}\n"
            f"Event start time: {event.start_time}\n"
            f"Event end time: {event.end_time}\n"
            F"Event image: {event.cover_image.url}"
        )

        self.bot.logger.info(message)
        await channel.send(message)

    @commands.Cog.listener()
    async def on_scheduled_event_delete(self, event: ScheduledEvent):
        channel = self.bot.get_channel(self.channel_id)
        message = (
            f"Event deleted in {event.guild.name} (ID: {event.guild.id}) by {event.creator} (ID: {event.creator_id})\n"
            f"Event name: {event.name}\n"
            f"Event description: {event.description}\n"
            f"Event start time: {event.start_time}\n"
            f"Event end time: {event.end_time}\n"
            F"Event image: {event.cover_image.url}"
        )
        self.bot.logger.info(message)
        await channel.send(message)


async def setup(bot):
    await bot.add_cog(Meetup(bot))
