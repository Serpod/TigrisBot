import discord
import traceback
import tigris
import utils
from log import *
from settings import *


# Code for the bot itself (parse commands)

client = discord.Client()
bank = tigris.TigrisBank()

def usage():
    usage = ''
    usage += "Service de gestion de la monnaie de Fibreville : le tigris (ŧ).\n"
    usage += "Commandes disponibles :\n"
    usage += "\t.new_account [user]\n"
    usage += "\t\tCrée un compte en banque pour l'utilisateur renseigné (s'il y en a un) ou pour l'expéditeur du message.\n"
    usage += "\t\t(Ne fonctionne que si le compte n'existe pas déjà.)\n"
    usage += "\t.balance\n"
    usage += "\t\tVous transmet par message privé votre solde.\n"
    usage += "\t.send <to> <amount> [message]\n"
    usage += "\t\tSi vous avez les fonds nécéssaires, envoie <amount> tigris à l'utilisateur <to>.\n"
    usage += "\t\tUn message (facultatif) peut être renseigné.\n"
    usage += "\t.history\n"
    usage += "\t\tVous transmet par message privé votre historique de transactions.\n"
    usage += "\t.help\n"
    usage += "\t\tAffiche ce message.\n"

    return usage


def new_account(message):
    """
    Create an account for a new account
    """
    msg = message.content.split()
    if len(msg) == 2:
        match = utils.pattern_id.match(msg[1])
        if match is not None:
            user_id = match.group(1)
        else:
            user_id = None
    else:
        user_id = message.author.id

    try:
        user_id = int(user_id)
    except Exception as e:
        res = "Erreur : Mauvais format de l'identifiant utilisateur : {}".format(msg[1])
        log_error(res)
        log_error("({})".format(e))
        return res

    if bank.new_account(user_id):
        res = "<@{}> a maintenant un compte en banque.".format(user_id)
    else:
        res = "Erreur : <@{}> a déjà un compte en banque.".format(user_id)

    log_info(res)
    return res
    
def get_balance(message):
    user_id = message.author.id
    balance = bank.get_balance(user_id)
    if balance >= 0:
        res = "Vous avez {}ŧ (tigris) en banque.".format(balance)
    else:
        res = "Erreur : Vous n'avez pas de compte en banque.\n"
        res += "Vous pouvez en créer un avec la commande `.new_account`."

    log_info(res)
    return res


def send(message):
    # Parse command
    from_id = message.author.id
    msg_cont = message.content.split()
    if len(msg_cont) < 3:
        res = "Erreur : Nombre de paramètres insuffisant.\n"
        res += "`.send <to> <amount> [message]`"
        return res

    match = utils.pattern_id.match(msg_cont[1])
    if match is not None:
        to_id = match.group(1)
    else:
        to_id = None

    try:
        to_id = int(to_id)
    except Exception as e:
        res = "Erreur : Mauvais format de l'identifiant utilisateur : {}".format(msg_cont[1])
        log_error(res)
        log_error("({})".format(e))
        traceback.print_exc()
        return res

    try:
        amount = round(float(msg_cont[2]), 3)
    except Exception as e:
        res = "Erreur : Mauvais format du montant de la transaction : {}".format(msg_cont[2])
        log_error(res)
        log_error("({})".format(e))
        traceback.print_exc()
        return res

    if amount <= 0:
        res = "Erreur : Le montant envoyé doit être strictement positif."
        log_info(res)
        return res

    if to_id == from_id:
        res = "Erreur : L'expéditeur et le même que le destinataire."
        log_info(res)
        return res

    msg = ''
    if len(msg_cont) > 3:
        msg = ' '.join(msg_cont[3:])[:256]

    # Call DB function
    status = bank.send(from_id, to_id, amount, msg)

    # Branch on return status
    if status == 0:
        res = "L'opération est enregistrée.\n"
        if to_id == TIGRISBOT_ID:
            res += "Fais un voeu."
    elif status == 1:
        res = "Erreur : L'expéditeur n'a pas de compte en banque."
    elif status == 2:
        res = "Erreur : Le destinataire n'a pas de compte en banque."
    elif status == 3:
        res = "Erreur : L'expéditeur n'a pas les fonds suffisants pour cette opération."

    log_info(res)
    return res
    
def get_history(message):
    user_id = message.author.id
    transacs = bank.get_history(user_id)
    res = ''
    res += "Votre historique :\n\n"
    for t in transacs:
        if t[0] == user_id:
            res += "{}\t | <@{}>\t\t | {}ŧ | {}\n".format(t[4], t[1], ('-' + str(t[2])).rjust(10), t[3])
        elif t[1] == user_id:
            res += "{}\t | <@{}>\t\t | {}ŧ | {}\n".format(t[4], t[0], ('+' + str(t[2])).rjust(10), t[3])
    log_info(res)
    return res


@client.event
async def on_ready():
    log_info("We have logged in as {0.user}".format(client))

@client.event
async def on_message(message):
    if not utils.is_allowed(message.channel):
        return
    if bank is None:
        return

    if message.author == client.user:
        return


    if DEBUG and message.content.startswith("."):
        log_info("{} ({}): {}".format(message.author.name, message.author.id, message.content))
    #    await message.channel.send("```{}```".format(message.content))

    if message.content.startswith(".new_account"):
        try:
            await message.channel.send("{}".format(new_account(message)))
        except Exception as e:
            log_error("An error occured in new_account function")
            log_error(e)
            traceback.print_exc()

    elif message.content.startswith(".balance"):
        res = get_balance(message)
        dm = await message.author.create_dm()
        await dm.send(res)

    elif message.content.startswith(".send"):
        try:
            await message.channel.send("{}".format(send(message)))
        except Exception as e:
            log_error("An error occured in send function :")
            log_error(e)
            traceback.print_exc()

    elif message.content.startswith(".help"):
        try:
            await message.channel.send("```\n{}```".format(usage()))
        except Exception as e:
            log_error("An error occured in help function")
            log_error(e)
            traceback.print_exc()

    elif message.content.startswith(".history"):
        res = get_history(message)
        dm = await message.author.create_dm()
        await dm.send(res)
        

client.run(BOT_TOKEN)

