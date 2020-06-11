import discord
from discord.ext import commands
import traceback
import tigris
import utils
import re
from log import *
from settings import *


# Code for the bot itself (parse commands)

client = commands.Bot(command_prefix='.')
#client.help_command = None
bank = tigris.TigrisBank()

@client.command(name="usage")
async def usage(ctx):
    msg = []
    usage = '```markdown\n'
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
    usage += "\t* .salary\n"
    usage += "\t\tAffiche votre salaire.\n"
    usage += '\n'
    usage += "\t* .monthly_taxes [YYYY-MM]\n"
    usage += "\t\tAffiche la somme des taxes récoltées pour ce mois-ci ou pour le mois renseigné en suivant le format YYYY-MM (par exemple pour Juin 2020 : 2020-06).\n"
    usage += '\n'
    usage += "\t* .help\n"
    usage += "\t\tAffiche ce message.\n"
    usage += "```"
    msg.append(usage)
    if ctx.author.id in ADMIN:
        usage = "```markdown\n"
        usage += "## Commandes spéciales (pour notre bon Roy et certains privilégiés) :\n"
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
        usage += "\t* .salary [<user>]\n"
        usage += "\t\tVous transmet votre salaire ou celui de <user>.\n"
        usage += '\n'
        usage += "\t* .all_salaries\n"
        usage += "\t\tVous transmet les salaires de tous les citoyens.\n"
        usage += '\n'
        usage += "\t* .pay_salaries\n"
        usage += "\t\tDéclenche la paye des salaires à tous les citoyens.\n"
        usage += "\t\t(À utiliser avec précaution, commande très peu testée)\n"
        usage += "```"
        msg.append(usage)

    await utils.send_msg(msg, ctx)

@client.command(ignore_extra=True)
async def new_account(ctx, user: discord.Member = None):
    """
    Create an account for a new account
    """
    if user is None:
        user_id = ctx.author.id
    else:
        user_id = user.id

    if bank.new_account(user_id):
        res = "<@{}> a maintenant un compte en banque.".format(user_id)
    else:
        res = "Erreur : <@{}> a déjà un compte en banque.".format(user_id)

    log_info(res)
    await ctx.send(res)

@new_account.error
async def new_account_error(ctx, error):
    log_error(error)
    if isinstance(error, commands.BadArgument):
        await ctx.send(error)
    else:
        raise error

    
@client.command(name="balance", ignore_extra=True)
async def get_balance(ctx):
    user_id = ctx.author.id
    balance = bank.get_balance(user_id)
    dm = await ctx.author.create_dm()
    if balance >= 0:
        res = "Vous avez {}ŧ (tigris) en banque.".format(balance/100)
    else:
        res = "Erreur : Vous n'avez pas de compte en banque.\n"
        res += "Vous pouvez en créer un avec la commande `.new_account`."

    log_info(res)
    await dm.send(res)


@get_balance.error
async def get_balance_error(ctx, error):
    log_error(error)
    raise error


@client.command(ignore_extra=False)
async def send(ctx, to_user: discord.Member, amount: float, msg = ''):
    from_id = ctx.author.id

    amount = int(round(amount, 3)*100)

    if amount <= 0:
        res = "Erreur : Le montant envoyé doit être strictement positif."
        log_info(res)
        await ctx.send(res)
        return

    to_id = to_user.id
    if to_id == from_id:
        res = "Erreur : L'expéditeur est le même que le destinataire."
        log_info(res)
        await ctx.send(res)
        return

    msg = msg[:256]

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
    elif status == 4:
        res = "Erreur : La taxe n'a pas pu être payée. Virement annulé."

    log_info(res)
    await ctx.send(res)


@send.error
async def send_error(ctx, error):
    log_error(error)
    if isinstance(error, commands.BadArgument):
        await ctx.send(error)
    elif isinstance(error, commands.MissingRequiredArgument):
        res = "Erreur : Nombre de paramètres insuffisant.\n"
        res += "`.send <to> <amount> [message]`"
        await ctx.send(res)
    elif isinstance(error, commands.TooManyArguments):
        res = "Erreur : Trop de paramètres.\n"
        res += "N'oubliez pas d'entourer votre message de guillemets (\")"
        await ctx.send(res)
    raise error


@client.command(name="history")
async def get_history(ctx):
    user_id = ctx.author.id
    transacs = bank.get_history(user_id)
    if transacs is None:
        res = ["Erreur : vous n'avez pas de compte en banque."]
    else:
        res = []
        res.append("Votre historique :")
        res.append("")
        for t in transacs:
            amount = ("{}" + str(t[2]/100)).rjust(10)
            if t[0] == user_id:
                username = await get_name(t[1])
                res.append("`{}\t|{}|{}ŧ | '{}'`".format(t[4], username.center(20), amount.format('-'), t[3]))
            elif t[1] == user_id:
                username = await get_name(t[0])
                res.append("`{}\t|{}|{}ŧ | '{}'`".format(t[4], username.center(20), amount.format('+'), t[3]))
    log_info('\n'.join(res))
    dm = await ctx.author.create_dm()
    await utils.send_msg(res, dm)


@get_history.error
async def get_history_error(ctx, error):
    log_error(error)
    raise error


@client.command(name="all_balance")
@commands.check(utils.is_admin)
async def get_all_balance(ctx):
    all_balance = bank.get_all_balance()
    res = "Comptes en banque :\n\n"
    tot = 0
    for user_id, balance in all_balance:
        tot += balance
        username = await get_name(user_id)
        res += "`{}|{}ŧ`\n".format(username.ljust(30), str(balance/100).rjust(10))

    res += '`' + '-'*42 + "`\n"
    res += "`{}|{}ŧ`\n".format("Total".ljust(30), str(tot/100).rjust(10))
    log_info(res)
    dm = await ctx.author.create_dm()
    await utils.send_msg(res.split('\n'), dm)


@get_all_balance.error
async def get_all_balance_error(ctx, error):
    log_error(error)
    raise error


@client.command(name="all_jobs")
async def get_all_jobs(ctx):
    """
    The jobs of everyone (with salaries).
    """
    admin = 
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
        if await utils.is_admin(ctx):
            curr_job += "| {}ŧ | {}".format(str(salary/100).rjust(10), job_id)
        curr_job += '\n'

    if len(all_jobs) > 0:
        curr_job += "```"
        jobs.append(curr_job)

    log_info(jobs)
    dm = await ctx.author.create_dm()
    await utils.send_msg(jobs, dm)


@get_all_jobs.error
async def get_all_jobs_error(ctx, error):
    log_error(error)
    raise error


@client.command(name="all_salaries")
@commands.check(utils.is_admin)
async def get_all_salaries():
    all_salaries = bank.get_all_salaries()
    res = "Salaires des citoyens :\n\n"
    tot = 0
    for user_id, salary in all_salaries:
        tot += salary
        username = await get_name(user_id)
        res += "`{}|{}ŧ`\n".format(username.ljust(30), str(salary/100).rjust(10))

    res += '`' + '-'*42 + "`\n"
    res += "`{}|{}ŧ`\n".format("Total".ljust(30), str(tot).rjust(10))
    dm = await ctx.author.create_dm()
    await utils.send_msg(res.split('\n'), dm)


@get_all_salaries.error
async def get_all_salaries_error(ctx, error):
    log_error(error)
    raise error


@client.command(ignore_extra=False)
@commands.check(utils.is_admin)
def new_job(ctx, user: discord.Member, salary: float, title):
    """
    Add a new job with:

    .new_job <user_id> <salary> <title>
    """
    salary = int(round(salary, 3)*100)

    title = title[:256]

    bank.new_job(user.id, salary, title)
    res = "Nouveau métier pour {} enregistré !".format(user.mention)
    log_info(res)
    await ctx.send(res)


@new_job.error
async def new_job_error(ctx, error):
    log_error(error)
    if isinstance(error, discord.BadArgument):
        await ctx.send(error)
    elif isinstance(error, discord.MissingRequiredArgument):
        res = "Erreur : Nombre de paramètres insuffisant.\n"
        res += "`.new_job <user_id> <salary> <title>`"
        await ctx.send(res)
    elif isinstance(error, discord.TooManyArguments):
        res = "Erreur : Nombre de paramètres trop grand.\n"
        res += "`.new_job <user_id> <salary> <title>`"
        res += "N'oubliez pas d'entourer le titre de l'emploi par des guillemets (\")"
        await ctx.send(res)

def del_job(message):
    """
    Remove a given job for a given user with:

    .del_job <user_id> <job_id>
    """
    msg = message.content.split()
    if len(msg) < 3:
        res = "Erreur : Nombre de paramètres insuffisant.\n"
        res += "`.del_job <user_id> <job_id>`"
        return res

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


async def get_jobs(message, is_other=False):
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

    res = "Le ou les métiers de **{}** :\n".format(await get_name(user_id))
    res += "```\n"
    for _, job_id, title, salary in jobs:
        res += "* {}".format(title.center(70))
        if not is_other:
            res += "| {}ŧ | {}".format(str(salary/100).rjust(10), job_id)
        res += '\n'
    res += "```"

    log_info(res)
    return res.split('\n')


def get_salary(message):
    m = message.content.split()
    if message.author.id in ADMIN and len(m) == 2:
        user_id = utils.get_user_id(m[1])
        if user_id is None:
            res = "Erreur : Mauvais format de l'identifiant utilisateur : {}".format(m[1])
            log_error(res)
            return res
    elif len(m) == 1:
        user_id = message.author.id
    else:
        res = "Erreur : Mauvais nombre de paramètre.\n"
        res += ".salary (classique)\n"
        res += ".salary [<user>] (privilégié)"
        log_error(res)
        return res

    salary = bank.get_salary(user_id)
    if len(m) == 2:
        if salary is None:
            res = "Erreur : {} n'a aucun de métier.".format(utils.mention(user_id))
            log_error(res)
            return res
        else:
            res = "{} a un salaire mensuel de {} pour l'ensemble de ses métiers.".format(utils.mention(user_id), salary/100)
            log_info(res)
            return res
    else:
        if salary is None:
            res = "Erreur : vous n'avez pas de métier."
            log_error(res)
            return res
        else:
            res = "Vous avez un salaire mensuel de {}ŧ pour l'ensemble de vos métiers.".format(salary/100)
            log_info(res)
            return res


def pay_salaries(message):
    from_id = message.author.id

    ret_values = bank.pay_all_salaries(from_id)

    res = []
    paid = []
    error = []
    for user_id, v, salary in ret_values:
        if v == 1:
            res.append("Erreur : Le compte débiteur ({}) n'existe pas.".format(utils.mention(from_id)))
            log_error(res[-1])
            return res, paid, error

        if v == 0:
            res.append("Son salaire a été versé à {}.\n".format(utils.mention(user_id)))
            paid.append((user_id, salary))
        elif v == 2:
            error.append((user_id, "Erreur : La salaire de {} est nul.".format(utils.mention(user_id))))
        elif v == 3:
            error.append((user_id, "Erreur : Le débiteur ({}) n'a plus les fonds nécéssaires.".format(utils.mention(user_id))))
            res.append(error[-1][1])
            log_error(res[-1])
            return res, paid, error

    return res, paid, error


def get_monthly_taxes(message):
    msg = message.content.split()
    if len(msg) > 1:
        pattern_month = re.compile("(\d\d\d\d-\d\d)")
        match = pattern_month.match(msg[1])
        if match is None:
            res = "Erreur : Mauvais format pour le mois demandé ({})".format(msg[1])
            log_error(res)
            return res

        month = match.group(1)
        sum_tax = bank.get_monthly_taxes(month)
        if sum_tax is None:
            res = "Aucune taxe n'a été récoltée ce mois-ci."
            log_error(res)
            return res
        res = "Somme des taxes récoltées pour le mois {} : {}ŧ".format(month, sum_tax/100)
    else:
        # len(msg) == 0:
        sum_tax = bank.get_monthly_taxes()
        if sum_tax is None:
            res = "Aucune taxe n'a été récoltée ce mois-ci."
            log_error(res)
            return res
        res = "Somme des taxes récoltées pour ce mois-ci : {}ŧ".format(sum_tax/100)



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
        if message.content.startswith(".all_jobs"):
            msg = message.content.split()
            if len(msg) == 2 and msg[1] == "classic":
                jobs = await get_all_jobs()
                await utils.send_msg(jobs, message.channel)
            else:
                jobs = await get_all_jobs(True)
                dm = await message.author.create_dm()
                await utils.send_msg(jobs, dm)

        elif message.content.startswith(".del_job"):
            try:
                await message.channel.send("{}".format(del_job(message)))
            except Exception as e:
                log_error("An error occured in del_job function")
                log_error(e)
                traceback.print_exc()

        elif message.content.startswith(".salary"):
            res = get_salary(message)
            dm = await message.author.create_dm()
            await dm.send(res)

        elif message.content.startswith(".pay_salaries"):
            res, paid, error = pay_salaries(message)
            for user_id, amount in paid:
                user = await client.fetch_user(user_id)
                dm = await user.create_dm()
                await dm.send("Vous avez reçu votre salaire de {}ŧ.".format(amount))
            try:
                await utils.send_msg(res, message.channel)
            except Exception as e:
                log_error("An error occured in pay_salaries function")
                log_error(e)
                traceback.print_exc()


    # Functions for everyone
    if message.content.startswith(".jobs"):
        msg = message.content.split()
        if len(msg) == 1:
            res = await get_jobs(message, is_other=False)
            dm = await message.author.create_dm()
            await utils.send_msg(res, dm)
        elif len(msg) == 2:
            try:
                await utils.send_msg(await get_jobs(message, is_other=True), message.channel)
            except Exception as e:
                log_error("An error occured in jobs function")
                log_error(e)
                traceback.print_exc()
        else:
            res = "Erreur : Mauvais nombre de paramètres.\n"
            res += ".jobs [<user>]"
            log_error(res)
            try:
                await utils.send_msg(res, message.channel)
            except Exception as e:
                log_error("An error occured in jobs function")
                log_error(e)
                traceback.print_exc()

    elif message.content.startswith(".monthly_taxes"):
        try:
            res = get_monthly_taxes(message)
            await message.channel.send(res)
        except Exception as e:
            log_error("An error occured in monthly_taxes function")
            log_error(e)
            traceback.print_exc()

    elif message.author.id not in ADMIN and message.content.startswith(".all_jobs"):
        try:
            jobs = await get_all_jobs()
            await utils.send_msg(jobs, message.channel)
        except Exception as e:
            log_error("An error occured in all_jobs function")
            log_error(e)
            traceback.print_exc()

    elif message.author.id not in ADMIN and message.content.startswith(".salary"):
        try:
            await message.channel.send(get_salary(message))
        except Exception as e:
            log_error("An error occured in help function")
            log_error(e)
            traceback.print_exc()

    await client.process_commands(message)

client.run(BOT_TOKEN)
