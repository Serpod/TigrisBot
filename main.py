import discord
from discord.ext import commands
from discord.utils import get
from copy import deepcopy
import os
import traceback
import random
import tigris
import jobs
import utils
import re
import marketplace
import pickle
import comptage
from log import *
from settings import *


# Code for the bot itself (parse commands)
intents = discord.Intents.default()
intents.members = True
client = commands.Bot(command_prefix='.', intents=intents)
client.help_command = None
bank = tigris.TigrisBank()
jobs_mgr = jobs.JobsManager()
marketplace = marketplace.Marketplace()

@client.command(name="help")
async def usage(ctx):
    msg = []

    usage = "# Service de gestion de la monnaie de Fibreville : le tigris (ŧ).\n\n"
    usage += "## Commandes disponibles pour tous et toutes :\n"
    usage += "\t* .help\n"
    usage += "\t\tAffiche ce message.\n"
    msg.append(utils.surround_markdown(usage))

    usage = "\t* .new_account\n"
    usage += "\t\tCrée un compte en banque pour l'expéditeur.ice du message.\n"
    usage += "\t\t(Ne fonctionne que si le compte n'existe pas déjà.)\n"
    msg.append(utils.surround_markdown(usage))

    usage = "\t* .balance\n"
    usage += "\t\tVous transmet par message privé votre solde.\n"
    msg.append(utils.surround_markdown(usage))

    usage = "\t* .send_tigris <to> <amount> [<message>]\n"
    usage += "\t\tSi vous avez les fonds nécéssaires, envoie <amount> tigris à l'utilisateur.ice <to>.\n"
    usage += "\t\tUn message (facultatif) <message> peut être renseigné.\n"
    msg.append(utils.surround_markdown(usage))

    usage = "\t* .history\n"
    usage += "\t\tVous transmet par message privé votre historique de transactions.\n"
    msg.append(utils.surround_markdown(usage))

    usage = "\t* .jobs [<user>]\n"
    usage += "\t\tVous transmet votre métier ou affiche le métier de <user>.\n"
    msg.append(utils.surround_markdown(usage))

    usage = "\t* .all_jobs\n"
    usage += "\t\tAffiche tous les métiers de tout le monde.\n"
    msg.append(utils.surround_markdown(usage))

    usage = "\t* .step\n"
    usage += "\t\tAffiche votre palier de revenu.\n"
    msg.append(utils.surround_markdown(usage))

    #usage = "\t* .monthly_taxes [YYYY-MM]\n"
    #usage += "\t\tAffiche la somme des taxes récoltées pour ce mois-ci ou pour le mois renseigné en suivant le format YYYY-MM (par exemple pour Juin 2020 : 2020-06).\n"
    #msg.append(utils.surround_markdown(usage))

    #usage = "\t* .inventory\n"
    #usage += "\t\tVous transmet votre inventaire.\n"
    #msg.append(utils.surround_markdown(usage))

    #usage = "\t* .create <name> [<description>]\n"
    #usage += "\t\tCrée un objet (si vous n'en avez pas déjà créé aujourd'hui).\n"
    #msg.append(utils.surround_markdown(usage))

    #usage = "\t* .delete <item_id>\n"
    #usage += "\t\tSupprime l'objet n°<item_id>. Vous devez en être le propriétaire.\n"
    #msg.append(utils.surround_markdown(usage))

    #usage = "\t* .trades\n"
    #usage += "\t\tVous transmet l'historique des ventes et échanges publics.\n"
    #msg.append(utils.surround_markdown(usage))

    #usage = "\t* .give <user> <item_id>\n"
    #usage += "\t\tDonne l'objet <item_id> à <user>.\n"
    #msg.append(utils.surround_markdown(usage))

    #usage = "\t* .for_sale\n"
    #usage += "\t\tAffiche les objets en vente.\n"
    #msg.append(utils.surround_markdown(usage))

    #usage = "\t* .sell <item_id> <price> [<user>]\n"
    #usage += "\t\tMet en vente l'objet <item_id> au prix de <price>ŧ.\n"
    #usage += "\t\tOptionnellement, seul <user> peut acheter cet objet.\n"
    #msg.append(utils.surround_markdown(usage))

    #usage = "\t* .cancel_sale <item_id>\n"
    #usage += "\t\tRetire l'objet <item_id> de la vente.\n"
    #msg.append(utils.surround_markdown(usage))

    #usage = "\t* .buy <item_id>\n"
    #usage += "\t\tAchète l'objet <item_id>.\n"
    #msg.append(utils.surround_markdown(usage))

    if ctx.author.id in ADMIN:
        usage += "\t* .all_balance\n"
        usage += "\t\tVous transmet par message privé l'état de tous les comptes en banque.\n"
        msg.append(utils.surround_markdown(usage))

        usage = "\t* .all_jobs\n"
        usage += "\t\tTransmet, en privé, tous les métiers de tout le monde.\n"
        msg.append(utils.surround_markdown(usage))

        usage = "\t* .new_job <user> <title>\n"
        usage += "\t\tAjoute un nouveau métier à <user>. Iel devient <title> et est payé.e au palier <step>.\n"
        msg.append(utils.surround_markdown(usage))

        usage = "\t* .del_job <user> <job_id>\n"
        usage += "\t\tSupprime le métier <job_id> de <user>.\n"
        msg.append(utils.surround_markdown(usage))

        usage = "\t* .step [<user>]\n"
        usage += "\t\tVous transmet votre salaire ou celui de <user>.\n"
        msg.append(utils.surround_markdown(usage))

        usage = "\t* .set_step <user> <step>\n"
        usage += "\t\tFixe le palier de revenu de <user> a <step>.\n"
        msg.append(utils.surround_markdown(usage))

        usage = "\t* .all_steps\n"
        usage += "\t\tVous transmet la liste des paliers de tout le monde.\n"
        msg.append(utils.surround_markdown(usage))

        usage = "\t* .payroll\n"
        usage += "\t\tDéclenche le versement des revenus de tout le monde.\n"
        msg.append(utils.surround_markdown(usage))

    dm = await ctx.author.create_dm()
    await utils.send_msg(msg, dm)

@client.command()
@commands.check(utils.is_admin)
async def add_loser(ctx, user_id):
    member = ctx.guild.get_member(int(user_id))
    role = get(ctx.guild.roles, name=LOSER_ROLE_NAME)
    await member.add_roles(role)
    msg = "Role {} added to {}".format(LOSER_ROLE_NAME, member.display_name)
    log_info(msg)
    await utils.send_msg([msg], ctx)

@client.command()
@commands.check(utils.is_admin)
async def rm_loser(ctx, user_id):
    member = ctx.guild.get_member(int(user_id))
    role = get(ctx.guild.roles, name=LOSER_ROLE_NAME)
    await member.remove_roles(role)
    msg = "Role {} removed from {}".format(LOSER_ROLE_NAME, member.display_name)
    log_info(msg)
    await utils.send_msg([msg], ctx)


@client.command(name='<:nini:696420822855843910>')
@commands.check(utils.is_admin)
async def nini(ctx):
    await scoreboard(ctx)

@client.command(name='S2<:nini:696420822855843910>')
@commands.check(utils.is_admin)
async def niniS2(ctx):
    await scoreboard(ctx, NINI_SAVE_FILE_PREFIX + "nini_saison2", "Ceci est le classement de la Saison 2 du NiNi, qui a commencée le 1er Février 2021 à 0h00 !")

async def scoreboard(ctx, histfile=None, preamble=None):
    #to_clear = await ctx.message.channel.fetch_message(754960110706622635)
    #await to_clear.remove_reaction('🚨', ctx.message.channel.guild.get_member(client.user.id))
    #return
    log_info("nini start")
    if preamble is not None:
        await utils.send_msg([preamble], ctx)
    await utils.send_msg(["Je commence à lire vos messages... :drum:"], ctx)
    message = ctx.message

    if histfile is not None:
        filename = histfile
    else:
        filename = NINI_SAVE_FILE_PREFIX + ctx.message.channel.name

    message_count = 0
    if os.path.isfile(filename):
        log_info("nini history file found")
        with open(filename, "rb") as f:
            history = pickle.load(f)
        date = history[0]
        all_losers = history[1]
    else:
        log_error("nini history file not found")
        all_losers = {}
        date = None

    old_losers = deepcopy(all_losers)

    async for m in message.channel.history(limit=None, after=date, oldest_first=True):
        message_count += 1
        auth_id = m.author.id
        if auth_id not in all_losers:
            all_losers[auth_id] = {"messages": 0, "errors": 0, "streak": 0, "streak_max": 0, "username": m.author.display_name}
        all_losers[auth_id]["messages"] += 1
        all_losers[auth_id]["username"] = m.author.display_name

        react_lose = False
        losers = set()
        for reaction in m.reactions:
            if reaction.emoji == '🚨':
                if not react_lose:
                    losers.add((m.author.display_name, auth_id))
                await m.add_reaction('🚨')
            if reaction.emoji in ['👌', '🙉', '🙊', '🙈', '🚳', '🚷', '⛔', '🚭', '📵', '🚯', '🔕', '🆗', '🙆', '🙅', '😶'] :
                if not react_lose:
                    losers = set()
                    react_lose = True

                for l in await reaction.users().flatten():
                    losers.add((l.display_name, l.id))
                await m.add_reaction('🚨')

        for l, l_id in losers:
            if l_id not in all_losers:
                all_losers[l_id] = {"messages": 0, "errors": 0, "streak": 0, "streak_max": 0, "username": l}
            all_losers[l_id]["errors"] += 1
            all_losers[l_id]["streak"] = -1                    # SO THE ERROR MESSAGE DOES NOT COUNT THEIR STREAK ANYMORE

        all_losers[auth_id]["streak"] += 1
        all_losers[auth_id]["streak_max"] = max(all_losers[auth_id]["streak_max"], all_losers[auth_id]["streak"])

    # SAVE DATA AS PICKLE

    date = m.created_at
    with open(filename, "wb") as f:
        pickle.dump([date, all_losers], f)

    # WEEKLY RANKING UPDATE AND LOSERS OF THE WEEK

    # LOSERS OF THE WEEK COMPUTE (BEFORE SORTING DICT)
    loss = {}

    for uid in all_losers:
        if uid not in old_losers:
            loss[uid] = (all_losers[uid]["errors"], all_losers[uid]["username"])
        else:
            nLoss = all_losers[uid]["errors"] - old_losers[uid]["errors"]
            if nLoss > 0:
                loss[uid] = (nLoss, all_losers[uid]["username"])

    loss_ranking = sorted([(uid, loss[uid][1], loss[uid][0]) for uid in loss if loss[uid][0] > 0], key=lambda x: x[2], reverse=True)

    max_ratio_old = max([data["messages"]/data["errors"] if data["errors"] != 0 else -1 for _, data in old_losers.items() if (data["messages"] >= 300)])
    max_ratio = max([data["messages"]/data["errors"] if data["errors"] != 0 else -1 for _, data in all_losers.items() if (data["messages"] >= 300)])

    # RANKING UPDATE
    old_losers = sorted([(uid, data) for uid, data in old_losers.items() if (data["messages"] >= 300)],
                        key=lambda x: x[1]["messages"]/x[1]["errors"] if x[1]["errors"] != 0 else max_ratio+x[1]["messages"], reverse=True)

    old_ranking = {}
    for rank, (uid, data) in enumerate(old_losers):
        old_ranking[uid] = rank

    all_losers_sorted = sorted([(uid, data) for uid, data in all_losers.items() if (data["messages"] >= 300)],
                                key=lambda x: x[1]["messages"]/x[1]["errors"] if x[1]["errors"] != 0 else max_ratio+x[1]["messages"], reverse=True)

    for new_rank, (uid, data) in enumerate(all_losers_sorted):
        if uid not in old_ranking:
            old_rank = len(old_ranking)
        else:
            old_rank = old_ranking[uid]
        update = old_rank-new_rank
        if update > 0:
            update = "🔼"+str(update)
        elif update < 0:
            update = "🔽"+str(-update)
        else:
            update = "🟦0"
        data["rank_update"] = update

    # RANKING MESSAGE
    res = ["Classement du <:nini:696420822855843910>"]
    res.append("`{} | {} | {} | {} | {} | {} | {}`".format("Pseudo".center(40), "# messages".center(12), "# défaites".center(12),
                                                      "Ratio".center(7), "Streak".center(12), "Streak max".center(12), "Évolution".center(12)))

    for uid, data in all_losers_sorted:
        res.append("`{} | {} | {} | {} | {} | {} | {}`".format(data["username"].center(40), str(data["messages"]).center(12), str(data["errors"]).center(12),
                                                          str(int(data["messages"]/data["errors"]) if data["errors"] != 0 else "∞").center(7), str(data["streak"]).center(12), str(data["streak_max"]).center(12), data["rank_update"].center(12)))

    log_info('\n'.join(res))


    # LOSER MESSAGE AND ROLES

    nLoser = min(NUMBER_OF_LOSER, len(loss_ranking))
    loss_ranking = loss_ranking[:nLoser]

    if nLoser == 0:
        loseMsg = "Il n'y a pas de grand loooooser.euse cette semaine."
    elif nLoser == 1:
        loseMsg = "Le.a grand.e loooooser.euse de cette semaine est "
    else:
        loseMsg = "Les {} grand.e.s loooooser.euse.s de cette semaine sont ".format(nLoser)

    for n, l in enumerate(loss_ranking):
        loseMsg += l[1] + " ({})".format(l[2])
        if n < nLoser-2:
            loseMsg += ", "
        elif n < nLoser-1:
            loseMsg += " et "
        else:
            loseMsg += "."

    res.append(loseMsg)

    # REMOVE ALL CURRENT LOSERS
    role = get(ctx.guild.roles, name=LOSER_ROLE_NAME)

    for member in ctx.guild.members:
        if role in member.roles:
            await member.remove_roles(role)

    for uid, name, _ in loss_ranking:
        try:
            member = ctx.guild.get_member(uid)
            await member.add_roles(role)
            log_info("Loser role added to {}.".format(name))
        except:
            continue

    # SEND MESSAGE
    res.append("J'ai lu {} messages !".format(message_count))
    await utils.send_msg(res, ctx)
    log_info("nini command done! {} messages".format(message_count))

@client.command(name='clap')
async def clap(ctx):
    if ctx.channel.id == BR_CHANNEL_ID:
        if PRESIDENT_ROLES_ID in [r.id for r in ctx.author.roles]:
            msg = "👏👏👏"
            for i in range(2):
                await utils.send_msg([msg], ctx)
        elif ctx.author.id == ctx.guild.owner.id:
            msg = ["MDR, Fais toi élire comme tout le monde.\n Le Roy n'est pas au dessus de tout"]
            await utils.send_msg(msg, ctx)
        else:
            msg = ["MDR, T KI ?"]
            await utils.send_msg(msg, ctx)


@client.command(name='👏')
async def clap_emote(ctx):
    await clap(ctx)


async def decomposeHelp(ctx):
    msg = "Utilise la commande suivie d'un nombre.\n Tu peux y ajouter un message complémentaire si tu veux."
    await utils.send_msg(msg, ctx)


@client.command(name='decomposeOpt')
async def decomposeOpt(ctx, number=None, *, left=None):
    if number is not None and number.isdigit() and 10000 > int(number) > 0:
        try:
            v, res = min(comptage.generate(int(number)), key=lambda x: len(x[1]))
            msg = res + ("" if left is None else " "+left)
            await utils.send_msg(msg, ctx)
        except ValueError:
            await utils.send_msg("No solution found", ctx)
    else:
        await decomposeHelp(ctx)


@client.command(name='decomposeCplx')
async def decomposeCplx(ctx, number=None, *, left=None):
    if number is not None and number.isdigit() and 10000 > int(number) > 9:
        try:
            v, res = min(comptage.generate(int(number)), key=lambda x: -len(x[1]))
            msg = res + ("" if left is None else " "+left)
            await utils.send_msg(msg, ctx)
        except ValueError:
            await utils.send_msg("No solution found", ctx)
    else:
        await decomposeHelp(ctx)


@client.command(name='decomposeMin')
async def decomposeOpt(ctx, number=None, *, left=None):
    if number is not None and number.isdigit() and 10000 > int(number) > 9:
        try:
            v, res = min(comptage.generate(int(number)), key=lambda x: x[0])
            msg = res + ("" if left is None else " "+left)
            await utils.send_msg(msg, ctx)
        except ValueError:
            await utils.send_msg("No solution found", ctx)
    else:
        await decomposeHelp(ctx)


@client.command(name='decomposeMax')
async def decomposeOpt(ctx, number=None, *, left=None):
    if number is not None and number.isdigit() and 10000 > int(number) > 9:
        try:
            v, res = min(comptage.generate(int(number)), key=lambda x: -x[0])
            msg = res + ("" if left is None else " "+left)
            await utils.send_msg(msg, ctx)
        except ValueError:
            await utils.send_msg("No solution found", ctx)
    else:
        await decomposeHelp(ctx)


@client.command(name='🔢')
async def decomposeEmote(ctx, number=None, *, left):
    if number is not None and number.isdigit() and 10000 > int(number) > 9:
        try:
            v, res = min(comptage.generate(int(number)), key=lambda x: len(x[1]))
            msg = res + ("" if left is None else " "+left)
            await utils.send_msg(msg, ctx)
        except ValueError:
            await utils.send_msg("No solution found", ctx)
    else:
        await decomposeHelp(ctx)


#@client.command()
#async def say(ctx, msg, channel: discord.TextChannel = None):
#    inventory = marketplace.get_inventory(ctx.author.id)
#    found = False
#    for creator_id, name, _, _, _ in inventory:
#        if creator_id == TIGRISBOT_CREATOR and name == "Télécommande du TigrisBot":
#            found = True
#            break
#    if not found:
#        await ctx.send("Erreur : Vous n'avez pas la Télécommande du TigrisBot")
#        return
#    if channel is None:
#        await ctx.send(msg)
#    else:
#        await channel.send(msg)


@client.command(name="citizens")
async def get_citizens(ctx):
    dm = await ctx.author.create_dm()
    citizens = bank.get_citizens()
    res = []
    if not citizens:
        await dm.send("La ville est déserte.")
        return

    res.append("Liste des citoyen.ne.s de Fibreville :")
    for citizen in citizens:
        res.append("{} : {}".format(await get_name(citizen[0]), utils.mention(citizen[0])))
    await utils.send_msg(res, dm)

### START OF INVENTORY

@client.command(ignore_extra=False)
async def buy(ctx, item_id: int):
    is_tax_free = ctx.guild.id in TAX_FREE_SERVER
    ret_val = marketplace.buy(ctx.author.id, item_id, bank, tax_free=is_tax_free)
    if ret_val == 1:
        res = "Erreur : L'acheteur n'a pas de compte en banque."
    elif ret_val == 2:
        res = "Erreur : Le vendeur n'a pas de compte en banque."
    elif ret_val == 3:
        res = "Erreur : L'acheteur n'a pas les fonds suffisants pour cette opération."
    elif ret_val == 4:
        res = "Erreur : La taxe n'a pas pu être payée. Vente annulée."
    elif ret_val == 5:
        res = "Erreur : L'acheteur et le vendeur sont les mêmes."
    elif ret_val == 6:
        res = "Erreur : L'objet n'est pas mis en vente."
    elif ret_val == 7:
        res = "Erreur : Le vendeur n'a pas autorisé l'acheteur à acheter cet objet."
    elif ret_val == -1:
        return
    elif ret_val == 0:
        res = "Achat effectué."
    else:
        return

    await ctx.send(res)


@buy.error
async def buy_error(ctx, error):
    log_error(error)
    if isinstance(error, commands.BadArgument):
        await ctx.send(error)
    elif isinstance(error, commands.MissingRequiredArgument):
        res = "Erreur : Nombre de paramètres insuffisant.\n"
        res += "`.buy <item_id>`"
        await ctx.send(res)
    elif isinstance(error, commands.TooManyArguments):
        res = "Erreur : Trop de paramètres.\n"
        res += "`.buy <item_id>`"
        await ctx.send(res)
    else:
        raise error


@client.command(ignore_extra=False)
async def cancel_sale(ctx, item_id: int):
    ret_val = marketplace.cancel_sale(ctx.author.id, item_id)

    if ret_val == 1:
        res = "Erreur : Vous n'êtes pas le propriétaire de cet objet."
    elif ret_val == 2:
        res = "Erreur : Cet objet n'est pas mis en vente actuellement."
    elif ret_val == 0:
        res = "L'objet a été retiré de la vente."
    else:
        return

    await ctx.send(res)


@cancel_sale.error
async def cancel_sale_error(ctx, error):
    log_error(error)
    if isinstance(error, commands.BadArgument):
        await ctx.send(error)
    elif isinstance(error, commands.MissingRequiredArgument):
        res = "Erreur : Nombre de paramètres insuffisant.\n"
        res += "`.cancel_sale <item_id>`"
        await ctx.send(res)
    elif isinstance(error, commands.TooManyArguments):
        res = "Erreur : Trop de paramètres.\n"
        res += "`.cancel_sale <item_id>`"
        await ctx.send(res)
    else:
        raise error


@client.command(ignore_extra=False)
async def sell(ctx, item_id: int, price: float, buyer: discord.Member = None):
    if buyer is None:
        buyer_id = None
    else:
        buyer_id = buyer.id

    ret_val = marketplace.sell(
            ctx.author.id,
            item_id,
            int(round(price, 3)*100),
            buyer_id)

    if ret_val == 1:
        res = "Erreur : Vous n'êtes pas le propriétaire de cet objet."
    elif ret_val == 2:
        res = "Erreur : Cet objet est déjà en vente."
    elif ret_val == -1:
        return
    elif ret_val == 0:
        res = "Cet objet est maintenant mis en vente."
    else:
        return

    await ctx.send(res)


@sell.error
async def sell_error(ctx, error):
    log_error(error)
    if isinstance(error, commands.BadArgument):
        await ctx.send(error)
    elif isinstance(error, commands.MissingRequiredArgument):
        res = "Erreur : Nombre de paramètres insuffisant.\n"
        res += "`.sell <item_id> <price> [<user>]`"
        await ctx.send(res)
    elif isinstance(error, commands.TooManyArguments):
        res = "Erreur : Trop de paramètres.\n"
        res += "`.sell <item_id> <price> [<user>]`"
        await ctx.send(res)
    else:
        raise error


@client.command(name="for_sale")
async def get_for_sale_items(ctx):
    items = marketplace.get_for_sale_items()

    if not items:
        res = "Il n'y a aucun objet en vente actuellement."
        await ctx.send(res)
        return

    res = []
    res.append("En vente :")
    res.append("`{}|{}|{}|{}|{}`".format(
            "Nom de l'objet".center(60),
            "ID objet".center(10),
            "Prix".center(15),
            "Nom du vendeur".center(20),
            "Nom de l'acheteur".center(20)
            ))
    res.append('`' + '-'*129 + '`')
    for name, item_id, price, seller_id, buyer_id in items:
        if buyer_id is None:
            buyer = ""
        else:
            buyer = await get_name(buyer_id)
        res.append("`{}|{}|{}|{}|{}`".format(
                name.center(60),
                str(item_id).center(10),
                (str(price/100) + 'ŧ').center(15),
                (await get_name(seller_id)).center(20),
                buyer.center(20)
                ))

    await utils.send_msg(res, ctx)


@get_for_sale_items.error
async def get_for_sale_items_error(ctx, error):
    log_error(error)
    raise error


@client.command(ignore_extra=False)
async def give(ctx, user: discord.Member, item_id: int):
    to_id = user.id
    from_id = ctx.author.id
    ret_val = marketplace.give(from_id, to_id, item_id)
    if ret_val == 0:
        res = "{} a bien reçu votre don.".format(user.mention)
    elif ret_val == 1:
        res = "Erreur : Vous n'êtes pas propriétaire de cet objet"
    elif ret_val == 2:
        res = "Erreur : Vous ne pouvez pas donner un objet que vous avez mis en vente."
    else:
        return
    await ctx.send(res)


@give.error
async def give_error(ctx, error):
    log_error(error)
    if isinstance(error, commands.BadArgument):
        await ctx.send(error)
    elif isinstance(error, commands.MissingRequiredArgument):
        res = "Erreur : Nombre de paramètres insuffisant.\n"
        res += "`.give <user> <item_id>`"
        await ctx.send(res)
    elif isinstance(error, commands.TooManyArguments):
        res = "Erreur : Trop de paramètres.\n"
        res += "`.give <user> <item_id>`"
        await ctx.send(res)
    else:
        raise error


@client.command(name="trades")
async def get_trades(ctx):
    dm = await ctx.author.create_dm()

    trades = marketplace.get_all_trades()

    if not trades:
        res = "Il n'y a jamais eu de vente ou d'échange public."
        await dm.send(res)
        return

    res = []
    res.append("Les échanges :")
    res.append("`{}|{}|{}|{}|{}`".format(
            "Vendeur".center(25),
            "Acheteur".center(25),
            "Prix".center(10),
            "Nom de l'objet".center(35),
            "Date de la transaction".center(25)
            ))
    res.append('`' + '-'*129 + '`')
    for seller_id, buyer_id, price, name, date in trades:
        res.append("`{}|{}|{}|{}|{}`".format(
                (await get_name(seller_id)).center(25),
                (await get_name(buyer_id)).center(25),
                (str(price/100) + 'ŧ').center(10),
                name.center(35),
                date.center(25)
                ))

    await utils.send_msg(res, dm)


@get_trades.error
async def get_trades_error(ctx, error):
    log_error(error)
    raise error


#@client.command(name="create", ignore_extra=False)
#async def create_item(ctx, name, description = ""):
#    description = description[:256]
#    item_id = marketplace.create_item(ctx.author.id, name, description)
#    if not item_id:
#        res = "Erreur : Vous ne pouvez créer qu'un seul objet par jour."
#    else:
#        res = "Vous venez de créer {} (id : {})".format(name, item_id)
#    await ctx.send(res)
#
#
#@create_item.error
#async def create_item_error(ctx, error):
#    log_error(error)
#    if isinstance(error, commands.MissingRequiredArgument):
#        res = "Erreur : Nombre de paramètres insuffisant.\n"
#        res += "`.create <name> [<description>]`"
#        await ctx.send(res)
#    elif isinstance(error, commands.TooManyArguments):
#        res = "Erreur : Trop de paramètres.\n"
#        res += "N'oubliez pas d'entourer votre nom d'objet ou votre description de guillemets (\")"
#        await ctx.send(res)
#    else:
#        raise error


@client.command(name="delete")
async def del_item(ctx, item_id: int):
    item = marketplace.get_item_by_id(item_id)
    if item is None:
        res = "Erreur : l'objet n°{} n'existe pas.".format(item_id)
    else:
        ret_val = marketplace.delete_item(ctx.author.id, item_id)
        if ret_val == 1:
            res = "Erreur : vous n'en êtes pas le propriétaire de {}.".format(item[2])
        elif ret_val == 2:
            res = "Erreur : l'objet est actuellement en vente.\n"
            res += "Vous devez le retirez de la vente avant de le détruire."
        else:
            res = "Vous venez de détruire {}".format(item[2])

    await ctx.send(res)


@del_item.error
async def del_item_error(ctx, error):
    log_error(error)
    if isinstance(error, commands.BadArgument):
        await ctx.send(error)
    if isinstance(error, commands.MissingRequiredArgument):
        res = "Erreur : Nombre de paramètres insuffisant.\n"
        res += "`.delete <item_id>`"
        await ctx.send(res)
    else:
        raise error


@client.command(name="inventory")
async def get_inventory(ctx):
    inventory = marketplace.get_inventory(ctx.author.id)

    dm = await ctx.author.create_dm()

    if not inventory:
        res = "Vous n'avez pas d'objets."
        await dm.send(res)
        return

    res = []
    res.append("Vos objets :")
    res.append("`{}|{}|{}|{}`".format(
            "ID objet".center(10),
            "Date de création".center(25),
            "Nom de l'objet".center(25),
            "Description".center(25)
            ))
    res.append('`' + '-'*103 + '`')
    for creator_id, item_name, item_desc, item_id, creation_date in inventory:
        res.append("`{}|{}|{}|{}`".format(
                str(item_id).center(10),
                creation_date.center(25),
                item_name.center(35),
                item_desc.center(25)
                ))
    await utils.send_msg(res, dm)


@get_inventory.error
async def get_inventory_error(ctx, error):
    log_error(error)
    raise error


### END OF INVENTORY

### START OF BANK

@client.command(ignore_extra=True)
async def new_account(ctx, user: discord.Member = None):
    """
    Create an account for a new account
    """
    if user is None:
        user_id = ctx.author.id
    elif utils.is_admin(ctx):
        user_id = user.id
    else:
        res = "Erreur : vous ne pouvez pas créer un compte pour une autre personne."
        log_info(res)
        await ctx.send(res)
        return

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
async def send_tigris(ctx, to_user: discord.Member, amount: float, msg = ''):
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

    is_tax_free = ctx.guild.id in TAX_FREE_SERVER

    # Call DB function
    status = bank.send(from_id, to_id, amount, msg, tax_free=True)

    # Branch on return status
    if status == 0:
        res = "L'opération est enregistrée.\n"
    elif status == 1:
        res = "Erreur : L'expéditeur n'a pas de compte en banque."
    elif status == 2:
        res = "Erreur : Le destinataire n'a pas de compte en banque."
    elif status == 3:
        res = "Erreur : L'expéditeur n'a pas les fonds suffisants pour cette opération."
    elif status == 4:
        res = "Erreur : La taxe n'a pas pu être payée. Virement annulé."
    elif status == -1:
        return

    log_info(res)
    await ctx.send(res)


@send_tigris.error
async def send_tigris_error(ctx, error):
    log_error(error)
    if isinstance(error, commands.BadArgument):
        await ctx.send(error)
    elif isinstance(error, commands.MissingRequiredArgument):
        res = "Erreur : Nombre de paramètres insuffisant.\n"
        res += "`.send_tigris <to> <amount> [message]`"
        await ctx.send(res)
    elif isinstance(error, commands.TooManyArguments):
        res = "Erreur : Trop de paramètres.\n"
        res += "N'oubliez pas d'entourer votre message de guillemets (\")"
        await ctx.send(res)
    else:
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
    for user_id, balance, step in all_balance:
        tot += balance
        username = await get_name(user_id)
        res += "`{}|{}ŧ| Palier {}`\n".format(username.ljust(30), str(balance/100).rjust(10), step)

    res += '`' + '-'*42 + "`\n"
    res += "`{}|{}ŧ`\n".format("Total".ljust(30), str(tot/100).rjust(10))
    log_info(res)
    dm = await ctx.author.create_dm()
    await utils.send_msg(res.split('\n'), dm)


@get_all_balance.error
async def get_all_balance_error(ctx, error):
    log_error(error)
    if isinstance(error, commands.CheckFailure):
        res = "Erreur : vous n'avez pas le droit de faire ceci."
        await ctx.send(res)
    else:
        raise error


@client.command(name="all_jobs")
async def get_all_jobs(ctx):
    """
    The jobs of everyone (with salaries).
    """
    all_jobs = jobs_mgr.get_all_jobs()
    res = "Métiers :\n\n"
    res = []
    curr_uid = 0
    for user_id, job_id, title, salary in all_jobs:
        if user_id != curr_uid:
            if curr_uid != 0:
                curr_job += "```"
                res.append(curr_job)
            curr_job = ""
            curr_uid = user_id
            curr_job += "Le ou les métiers de **{}** :\n".format(await get_name(curr_uid))
            curr_job += "```markdown\n"
        curr_job += "* {}".format(title.center(70))
        curr_job += '\n'

    if len(all_jobs) > 0:
        curr_job += "```"
        res.append(curr_job)
        log_info(res)
        dm = await ctx.author.create_dm()
        await utils.send_msg(res, dm)
    else:
        log_info("(get_all_jobs) No jobs found.")
        res = ["Personne n'a de métier ici..."]
        await utils.send_msg(res, ctx)



@get_all_jobs.error
async def get_all_jobs_error(ctx, error):
    log_error(error)
    raise error


@client.command(name="all_steps")
@commands.check(utils.is_admin)
async def get_all_steps(ctx):
    steps = bank.get_all_steps()
    res = "Palier des citoyens :\n\n"
    for user_id, step in steps:
        username = await get_name(user_id)
        res += "`{}|{}`\n".format(username.ljust(30), str(step).rjust(10))

    dm = await ctx.author.create_dm()
    await utils.send_msg(res.split('\n'), dm)


@get_all_steps.error
async def get_all_steps_error(ctx, error):
    log_error(error)
    if isinstance(error, commands.CheckFailure):
        res = "Erreur : vous n'avez pas le droit de faire ceci."
        await ctx.send(res)
    else:
        raise error


@client.command(ignore_extra=False)
@commands.check(utils.is_admin)
async def new_job(ctx, user: discord.Member, step: int, title):
    """
    Add a new job with:

    .new_job <user_id> <step> <title>
    """
    title = title[:256]

    jobs_mgr.new_job(user.id, step, title)
    res = "Nouveau métier pour {} enregistré !".format(user.mention)
    log_info(res)
    await ctx.send(res)


@new_job.error
async def new_job_error(ctx, error):
    log_error(error)
    if isinstance(error, commands.BadArgument):
        await ctx.send(error)
    elif isinstance(error, commands.MissingRequiredArgument):
        res = "Erreur : Nombre de paramètres insuffisant.\n"
        res += "`.new_job <user_id> <salary> <title>`"
        await ctx.send(res)
    elif isinstance(error, commands.TooManyArguments):
        res = "Erreur : Nombre de paramètres trop grand.\n"
        res += "`.new_job <user_id> <salary> <title>`\n"
        res += "N'oubliez pas d'entourer le titre de l'emploi par des guillemets (\")"
        await ctx.send(res)
    if isinstance(error, commands.CheckFailure):
        res = "Erreur : vous n'avez pas le droit de faire ceci."
        await ctx.send(res)
    else:
        raise error


@client.command(ignore_extra=True)
@commands.check(utils.is_admin)
async def del_job(ctx, user: discord.Member, job_id: int):
    """
    Remove a given job for a given user with:

    .del_job <user_id> <job_id>
    """
    user_id = user.id

    job = jobs_mgr.remove_job(user_id, job_id)
    if job is None:
        res = "Erreur : Le métier pour le.a citoyen.ne ({}) ayant pour identifiant {} n'existe pas".format(utils.mention(user_id), job_id)
        log_error(res)
        return res

    res = "{} n'est plus {}.".format(utils.mention(user_id), job[2])
    log_info(res)
    await ctx.send(res)


@del_job.error
async def del_job_error(ctx, error):
    log_error(error)
    if isinstance(error, commands.MissingRequiredArgument):
        res = "Erreur : Nombre de paramètres insuffisant.\n"
        res += "`.del_job <user_id> <job_id>`"
        await ctx.send(res)
    if isinstance(error, commands.CheckFailure):
        res = "Erreur : vous n'avez pas le droit de faire ceci."
        await ctx.send(res)
    else:
        raise error


@client.command(name="jobs")
async def get_jobs(ctx, user: discord.Member = None):
    if user is None:
        user_id = ctx.author.id
    else:
        user_id = user.id

    usr_jobs = jobs_mgr.get_jobs(user_id)

    res = "Le ou les métiers de **{}** :\n".format(await get_name(user_id))
    res += "```\n"
    for _, job_id, title in usr_jobs:
        res += "* {}".format(title.center(70))
        if user is None or await utils.is_admin(ctx):
            res += "| {}".format(job_id)
        res += '\n'
    res += "```"

    log_info(res)
    if user is None or await utils.is_admin(ctx):
        dm = await ctx.author.create_dm()
        await utils.send_msg(res.split('\n'), dm)
    else:
        await utils.send_msg(res.split('\n'), ctx)


@get_jobs.error
async def get_jobs_error(ctx, error):
    log_error(error)
    if isinstance(error, commands.BadArgument):
        await ctx.send(error)
    else:
        raise error


@client.command(name="set_step")
@commands.check(utils.is_admin)
async def set_step(ctx, user: discord.Member, step: int):
    user_id = user.id

    res = []
    if bank.set_income_step(user_id, step) == -1:
        res.append("{} n'a pas de compte en banque.".format(await get_name(user_id)))
    else:
        res.append("Le palier de {} a été modifié".format(await get_name(user_id)))
    
    await utils.send_msg(res, ctx)



@client.command(name="step")
async def get_step(ctx, user: discord.Member = None):
    if user is None:
        user_id = ctx.author.id
    else:
        if not await utils.is_admin(ctx):
            return
        user_id = user.id

    step = bank.get_income_step(user_id)
    if user is not None:
        dm = await ctx.author.create_dm()

        if step is None:
            res = "Erreur : {} n'a pas de compte en banque.".format(utils.mention(user_id))
            log_error(res)
        else:
            res = "{} est au palier {} et a donc un revenu de {}ŧ.".format(utils.mention(user_id), step, INCOME_BASE + step * INCOME_STEP_VALUE)
            log_info(res)

        await dm.send(res)
    else:
        if step is None:
            res = "Erreur : vous n'avez pas de compte en banque. Pour le créer : `.new_account`"
            log_error(res)
        else:
            res = "Vous êtes au palier {} et avez donc un revenu de {}ŧ .".format(step, INCOME_BASE + step*INCOME_STEP_VALUE)
            log_info(res)

        await ctx.send(res)


@get_step.error
async def get_step_error(ctx, error):
    log_error(error)
    if isinstance(error, commands.BadArgument):
        await ctx.send(error)
    elif isinstance(error, commands.TooManyArguments):
        res = "Erreur : Mauvais nombre de paramètres.\n"
        res += ".step (classique)\n"
        res += ".step [<user>] (privilégié)"
        await ctx.send(res)
    else:
        raise error


@client.command()
@commands.check(utils.is_admin)
async def payroll(ctx):
    from_id = ctx.author.id
    ret_values = bank.payroll()

    res = []
    for user_id in ret_values:
        res.append("Le revenu de {}ŧ a été crédité sur son compte.".format(await get_name(user_id)))
        log_info(res[-1])

    await utils.send_msg(res, ctx)


@payroll.error
async def payroll_error(ctx, error):
    log_error(error)
    if isinstance(error, commands.CheckFailure):
        res = "Erreur : vous n'avez pas le droit de faire ceci."
        await ctx.send(res)
    else:
        raise error


#@client.command(name="monthly_taxes")
#async def get_monthly_taxes(ctx, month = None):
#    if month is not None:
#        pattern_month = re.compile("(\d\d\d\d-\d\d)")
#        match = pattern_month.match(msg[1])
#        if match is None:
#            res = "Erreur : Mauvais format pour le mois demandé ({})".format(msg[1])
#            log_error(res)
#            await ctx.send(res)
#            return
#
#        month = match.group(1)
#        sum_tax = bank.get_monthly_taxes(month)
#        if sum_tax is None:
#            res = "Aucune taxe n'a été récoltée ce mois-ci."
#            log_error(res)
#            return res
#        res = "Somme des taxes récoltées pour le mois {} : {}ŧ".format(month, sum_tax/100)
#    else:
#        sum_tax = bank.get_monthly_taxes()
#        if sum_tax is None:
#            res = "Aucune taxe n'a été récoltée ce mois-ci."
#            log_error(res)
#            return res
#        res = "Somme des taxes récoltées pour ce mois-ci : {}ŧ".format(sum_tax/100)
#
#
#
#    log_info(res)
#    await ctx.send(res)
#
#
#@get_monthly_taxes.error
#async def get_monthly_taxes_error(ctx, error):
#    log_error(error)
#    raise error


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
    if message.author.id == client.user.id:
        return

    if isinstance(message.author, discord.Member) and message.channel.category.id in LAUGHS_CATEGORIES and BOUFFON_ROLES_ID in [r.id for r in message.author.roles]:
        if message.content.startswith('-'):
            return
        log_info("Send laugh")
        await message.channel.send(random.choice(LAUGH_LIST))

    if not utils.is_allowed(message.channel):
        return

    if bank is None:
        return

    if message.content.startswith("."):
        log_info("{} ({}): {}".format(message.author.name, message.author.id, message.content))
    #    await message.channel.send("```{}```".format(message.content))

    await client.process_commands(message)

client.run(BOT_TOKEN)
