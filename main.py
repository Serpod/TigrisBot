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
    usage += "# Service de gestion de la monnaie de Fibreville : le tigris (ŧ).\n\n"
    usage += "## Commandes disponibles pour tous et toutes :\n"
    usage += "\t* .new_account [<user>]\n"
    usage += "\t\tCrée un compte en banque pour l'utilisateur.rice renseigné.e (s'il y a lieu) ou pour l'expéditeur.ice du message.\n"
    usage += "\t\t(Ne fonctionne que si le compte n'existe pas déjà.)\n"
    usage += '\n'
    usage += "\t* .balance\n"
    usage += "\t\tVous transmet par message privé votre solde.\n"
    usage += '\n'
    usage += "\t* .send <to> <amount> [<message>]\n"
    usage += "\t\tSi vous avez les fonds nécéssaires, envoie <amount> tigris à l'utilisateur.ice <to>.\n"
    usage += "\t\tUn message (facultatif) <message> peut être renseigné.\n"
    usage += '\n'
    usage += "\t* .history\n"
    usage += "\t\tVous transmet par message privé votre historique de transactions.\n"
    usage += '\n'
    usage += "\t* .jobs [<user>]\n"
    usage += "\t\tVous transmet votre métier ou affiche le métier de <user>.\n"
    usage += '\n'
    usage += "\t* .all_jobs\n"
    usage += "\t\tAffiche tous les métiers des citoyens du royaume.\n"
    usage += '\n'
    usage += "\t* .help\n"
    usage += "\t\tAffiche ce message.\n"
    usage += '\n'
    usage += "\n"
    usage += "## Commande spéciale (nécéssite le statut de gestionnaire des finances) :\n"
    usage += "\t* .all_balance\n"
    usage += "\t\tVous transmet par message privé l'état de tous les comptes en banque.\n"
    usage += '\n'
    usage += "\t* .all_jobs [classic]\n"
    usage += "\t\tTransmet, en privé, tous les métiers des citoyens du royaume, avec le salaire associé.\n"
    usage += "\t\tSi classic est renseigné, équivalent à la commande disponibles pour tout le monde.\n"
    usage += '\n'
    usage += "\t* .new_job <user> <salary> <title>\n"
    usage += "\t\tAjoute un nouveau métier à <user>. Il devient <title> et est payé <salary>.\n"
    usage += '\n'
    usage += "\t* .del_job <user> <job_id>\n"
    usage += "\t\tSupprime le métier <job_id> de <user>.\n"
    usage += '\n'

    return usage


def new_account(message):
    """
    Create an account for a new account
    """
    msg = message.content.split()
    if len(msg) == 2:
        user_id = utils.get_user_id(msg[1])
    else:
        user_id = message.author.id

    if user_id is None:
        res = "Erreur : Mauvais format de l'identifiant utilisateur : {}".format(msg[1])
        log_error(res)
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

    to_id = utils.get_user_id(msg_cont[1])
    if to_id is None:
        res = "Erreur : Mauvais format de l'identifiant utilisateur : {}".format(msg_cont[1])
        log_error(res)
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

async def get_history(message):
    user_id = message.author.id
    transacs = bank.get_history(user_id)
    if transacs is None:
        res = "Erreur : vous n'avez pas de compte en banque."
    else:
        res = ''
        res += "Votre historique :\n\n"
        for t in transacs:
            amount = ("{}" + str(t[2])).rjust(10)
            if t[0] == user_id:
                username = await get_name(t[1])
                res += "`{}\t|**{}**|{}ŧ | '{}'`\n".format(t[4], username.center(20), amount.format('-'), t[3])
            elif t[1] == user_id:
                username = await get_name(t[0])
                res += "`{}\t|**{}**|{}ŧ | '{}'`\n".format(t[4], username.center(20), amount.format('+'), t[3])
    log_info(res)
    return res

async def get_all_balance():
    all_balance = bank.get_all_balance()
    res = "Comptes en banque :\n\n"
    for user_id, balance in all_balance:
        username = await get_name(user_id)
        res += "`**{}**|{}ŧ`\n".format(username.center(30), str(balance).rjust(10))
    log_info(res)
    return res

async def get_all_jobs(is_admin=False):
    """
    The jobs of everyone (with salaries).
    """
    all_jobs = bank.get_all_jobs()
    res = "Métiers :\n\n"
    jobs = []
    curr_uid = 0
    for user_id, job_id, title, salary in all_jobs:
        if user_id != curr_uid:
            if curr_uid != 0:
                curr_job += "```"
                jobs.append(curr_job)
            curr_job = ""
            curr_uid = user_id
            curr_job += "Le ou les métiers de **{}** :\n".format(await get_name(curr_uid))
            curr_job += "```markdown\n"
        curr_job += "* {}".format(title.center(70))
        if is_admin:
            curr_job += "| {}ŧ | {}".format(str(salary).rjust(10), job_id)
        curr_job += '\n'

    if len(all_jobs) > 0:
        curr_job += "```"
        jobs.append(curr_job)

    log_info(jobs)
    return jobs

def new_job(message):
    """
    Add a new job with:

    .new_job <user_id> <salary> <title>
    """
    msg = message.content.split()
    user_id = utils.get_user_id(msg[1])
    if user_id is None:
        res = "Erreur : Mauvais format de l'identifiant utilisateur : {}".format(msg[1])
        log_error(res)
        return res

    try:
        salary = int(msg[2])
    except:
        res = "Erreur : Mauvais format du salaire (chiffres décimaux uniquement) : {}".format(msg[2])
        log_error(res)
        return res

    title = ' '.join(msg[3:])[:256]

    bank.new_job(user_id, salary, title)
    res = "Nouveau métier pour {} enregistré !".format(utils.mention(user_id))
    log_info(res)
    return res

def del_job(message):
    """
    Remove a given job for a given user with:

    .del_job <user_id> <job_id>
    """
    msg = message.content.split()
    user_id = utils.get_user_id(msg[1])
    if user_id is None:
        res = "Erreur : Mauvais format de l'identifiant utilisateur : {}".format(msg[1])
        log_error(res)
        return res

    try:
        job_id = int(msg[2])
    except:
        res = "Erreur : Mauvais format de l'identifiant de métier (chiffres décimaux uniquement) : {}".format(msg[2])
        log_error(res)
        return res

    job = bank.remove_job(user_id, job_id)
    if job is None:
        res = "Erreur : Le métier pour le citoyen ({}) ayant pour identifiant {} n'existe pas".format(utils.mention(user_id), job_id)
        log_error(res)
        return res

    res = "{} n'est plus {}.".format(utils.mention(user_id), job[2])
    log_info(res)
    return res


def get_jobs(message, is_other=False):
    if is_other:
        m = message.content.split()[1]
        user_id = utils.get_user_id(m)
        if user_id is None:
            res = "Erreur : Mauvais format de l'identifiant utilisateur : {}".format(m)
            log_error(res)
            return res
    else:
        user_id = message.author.id

    jobs = bank.get_jobs(user_id)

    res = "Le ou les métiers de {} :\n".format(utils.mention(user_id))
    res += "```\n"
    for _, job_id, title, salary in jobs:
        res += "* {}".format(title.center(70))
        if not is_other:
            res += "| {}ŧ | {}".format(str(salary).rjust(10), job_id)
        res += '\n'
    res += "```"

    log_info(res)
    return res


async def get_name(user_id):
    name = bank.get_name(user_id)
    if name is None:
        name = await set_name(user_id)
    return name

async def set_name(user_id):
    try:
        name = (await client.fetch_user(user_id)).name
    except Exception as e:
        log_error(e)
        traceback.print_exc()
        return "<USERNAME_UNKNOWN>"
    bank.set_name(user_id, name)
    return name

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

    # ADMIN only functions
    if message.author.id in ADMIN:
        if message.content.startswith(".all_balance"):
            res = await get_all_balance()
            dm = await message.author.create_dm()
            await dm.send(res)

        if message.content.startswith(".all_jobs"):
            msg = message.content.split()
            if len(msg) == 2 and msg[1] == "classic":
                jobs = await get_all_jobs()
                for job in jobs:
                    await message.channel.send(job)
            else:
                jobs = await get_all_jobs(True)
                dm = await message.author.create_dm()
                for job in jobs:
                    await dm.send(job)

        elif message.content.startswith(".new_job"):
            try:
                await message.channel.send("{}".format(new_job(message)))
            except Exception as e:
                log_error("An error occured in new_job function")
                log_error(e)
                traceback.print_exc()

        elif message.content.startswith(".del_job"):
            try:
                await message.channel.send("{}".format(del_job(message)))
            except Exception as e:
                log_error("An error occured in del_job function")
                log_error(e)
                traceback.print_exc()

    # Functions for every one
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
            await message.channel.send("```markdown\n{}```".format(usage()))
        except Exception as e:
            log_error("An error occured in help function")
            log_error(e)
            traceback.print_exc()

    elif message.content.startswith(".history"):
        res = await get_history(message)
        dm = await message.author.create_dm()
        await dm.send(res)

    elif message.content.startswith(".jobs"):
        msg = message.content.split()
        if len(msg) == 1:
            res = get_jobs(message, is_other=False)
            dm = await message.author.create_dm()
            await dm.send(res)
        elif len(msg) == 2:
            try:
                await message.channel.send(get_jobs(message, is_other=True))
            except Exception as e:
                log_error("An error occured in jobs function")
                log_error(e)
                traceback.print_exc()
        else:
            res = "Erreur : Mauvais nombre de paramètres.\n"
            res += ".jobs [<user>]"
            log_err(res)
            try:
                await message.channel.send(res)
            except Exception as e:
                log_error("An error occured in jobs function")
                log_error(e)
                traceback.print_exc()

    elif message.author.id not in ADMIN and message.content.startswith(".all_jobs"):
        try:
            jobs = await get_all_jobs()
            for job in jobs:
                await message.channel.send(job)
        except Exception as e:
            log_error("An error occured in all_jobs function")
            log_error(e)
            traceback.print_exc()

        

client.run(BOT_TOKEN)

