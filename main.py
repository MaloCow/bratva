import discord
from discord.ext import commands, tasks
from datetime import datetime, timezone

intents = discord.Intents.default()
intents.presences = True  # Pour obtenir les données de présence qui incluent les activités
intents.members = True    # Pour accéder aux membres
intents.guilds = True     # Nécessaire pour accéder aux informations complètes des guildes et des rôles

client = commands.Bot(command_prefix="!", intents=intents)

# Variable pour stocker le message qui doit être modifié
last_message = None

# Mapping des rôles à des titres spécifiques
role_titles = {
    1204916299713478737: "Le patron",
    1204916299713478736: "Le bras-droit",
    1204916299684380721: "Le commandant",
    1204916299684380720: "Le lieutenant",
    1204916299684380718: "Le soldat",
    1204916299684380717: "La recrue"
}

@client.event
async def on_ready():
    print(f"Logged in as {client.user} (ID: {client.user.id})")
    log_activities.start()  # Démarrer la tâche de journalisation des activités

@tasks.loop(seconds=10)
async def log_activities():
    global last_message
    channel = client.get_channel(1218639301131374662)  # ID du canal spécifique
    if not channel:
        print("Channel not found!")
        return

    message_content = "<@&1204916299663155287>, __**Voici la liste des Bratva étant en ville:**__\n\n"
    player_count = 0  # Compteur pour le nombre de joueurs

    for guild in client.guilds:
        sunset_players = []
        for member in guild.members:
            # Vérifiez si le membre possède le rôle requis
            if any(role.id == 1204916299663155287 for role in member.roles):
                # Vérifiez les membres qui sont en ligne, ne pas déranger, ou inactifs
                if member.status in (discord.Status.online, discord.Status.dnd, discord.Status.idle):
                    member_title = ""
                    # Vérifier et assigner le titre basé sur le rôle du membre
                    for role_id, title in role_titles.items():
                        if any(role.id == role_id for role in member.roles):
                            member_title = title + " "
                            break
                    for activity in member.activities:
                        if hasattr(activity, 'name') and "Sunset" in activity.name and hasattr(activity, 'start'):
                            start_time = activity.start
                            time_playing = datetime.now(timezone.utc) - start_time
                            hours, remainder = divmod(int(time_playing.total_seconds()), 3600)
                            minutes, seconds = divmod(remainder, 60)
                            time_str = f"{hours}h {minutes}m {seconds}s"
                            sunset_players.append(f"> {member_title}**{member.display_name}** est en ville depuis ``{time_str}``.")
                            player_count += 1  # Incrémenter le compteur de joueurs
                            break
            
        if sunset_players:
            message_content += "\n".join(sunset_players) + "\n"
        else:
            message_content += "Aucun joueur connecté actuellement avec 'Sunset' dans leurs activités.\n"

    message_content += f"\nIl y a donc {player_count} bratva en ville."  # Ajouter le nombre total de joueurs

    if last_message:
        try:
            await last_message.edit(content=message_content)
        except discord.NotFound:
            last_message = await channel.send(message_content)
    else:
        last_message = await channel.send(message_content)

client.run('MTIzMzE4MDg3MzU1NDI2NDEwNQ.GMetw-.0sbRusJivydmiie0iuxLVSC6KyVYL3_z7nqm74')

