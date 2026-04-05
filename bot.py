from keep_alive import keep_alive
keep_alive()

import discord
from discord.ext import commands
import os
import time

# ===== VARIABLES =====
TOKEN = os.environ['TOKEN']
CONFESSION_CHANNEL_ID = int(os.environ['CONFESSION_CHANNEL_ID'])
LOG_CHANNEL_ID = int(os.environ['LOG_CHANNEL_ID'])

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

confession_count = 0
cooldowns = {}

# ===== MODAL =====
class ConfessionModal(discord.ui.Modal, title="Envoyer une confession"):

    confession = discord.ui.TextInput(
        label="Ta confession",
        style=discord.TextStyle.paragraph,
        max_length=500
    )

    async def on_submit(self, interaction: discord.Interaction):
        global confession_count

        user_id = interaction.user.id
        now = time.time()

        # Anti-spam 30 sec
        if user_id in cooldowns and now - cooldowns[user_id] < 30:
            await interaction.response.send_message(
                "⏳ Attends 30 secondes avant d'envoyer une autre confession !",
                ephemeral=True
            )
            return

        cooldowns[user_id] = now
        confession_count += 1

        confession_channel = bot.get_channel(CONFESSION_CHANNEL_ID)
        log_channel = bot.get_channel(LOG_CHANNEL_ID)

        # Embed confession rose
        embed_conf = discord.Embed(
            title=f"💌 Confession #{confession_count}",
            description=f"```{self.confession.value}```",
            color=0xff4d88
        )
        embed_conf.set_footer(text="Confession anonyme")
        embed_conf.set_thumbnail(url="https://cdn-icons-png.flaticon.com/512/833/833472.png")

        await confession_channel.send(embed=embed_conf, view=ConfessionView())

        # Embed log staff
        embed_log = discord.Embed(
            title=f"📋 Confession #{confession_count}",
            description=f"👤 Auteur : {interaction.user} ({interaction.user.id})\n\n💬 Message :\n```{self.confession.value}```",
            color=0x2ecc71
        )
        embed_log.set_footer(text="Logs staff")
        await log_channel.send(embed=embed_log)

        # Confirmation utilisateur
        await interaction.response.send_message(
            "Ta confession a été envoyée anonymement 🤫",
            ephemeral=True
        )

# ===== VIEW =====
class ConfessionView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Faire une confession", style=discord.ButtonStyle.primary, emoji="💌")
    async def confess(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(ConfessionModal())

    @discord.ui.button(label="Supprimer", style=discord.ButtonStyle.danger, emoji="🗑️")
    async def delete(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.guild_permissions.manage_messages:
            await interaction.message.delete()
        else:
            await interaction.response.send_message(
                "❌ Tu n'as pas la permission !",
                ephemeral=True
            )

# ===== PANEL =====
@bot.command()
async def confessionpanel(ctx):
    embed = discord.Embed(
        title="💌 Confessions du serveur",
        description="Clique sur le bouton ci-dessous pour envoyer une confession anonyme 🤫",
        color=0xff4d88
    )
    embed.set_footer(text="100% anonyme • Respect obligatoire")
    embed.set_thumbnail(url="https://cdn-icons-png.flaticon.com/512/833/833472.png")
    await ctx.send(embed=embed, view=ConfessionView())

# ===== READY =====
@bot.event
async def on_ready():
    bot.add_view(ConfessionView())
    print(f"{bot.user} est connecté !")

# ===== RUN =====
bot.run(TOKEN)