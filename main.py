import discord
from discord.ext import commands
import os
import traceback
import random
import tigris
import utils
import re
import marketplace
import pickle
from log import *
from settings import *


# Code for the bot itself (parse commands)

client = commands.Bot(command_prefix='.')
client.help_command = None
bank = tigris.TigrisBank()
marketplace = marketplace.Marketplace()

@client.command(name="help")
async def usage(ctx):
    msg = []

    usage = "# Service de gestion de la monnaie de Fibreville : le tigris (ŧ).\n\n"
    usage += "## Commandes disponibles pour tous et toutes :\n"
    usage += "\t* .help\n"
    usage += "\t\tAffiche ce message.\n"
    msg.append(utils.surround_markdown(usage))

    usage = "\t* .new_account [<user>]\n"
    usage += "\t\tCrée un compte en banque pour l'utilisateur.rice renseigné.e (s'il y a lieu) ou pour l'expéditeur.ice du message.\n"
    usage += "\t\t(Ne fonctionne que si le compte n'existe pas déjà.)\n"
    msg.append(utils.surround_markdown(usage))

    usage = "\t* .balance\n"
    usage += "\t\tVous transmet par message privé votre solde.\n"
    msg.append(utils.surround_markdown(usage))

    usage = "\t* .send <to> <amount> [<message>]\n"
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
    usage += "\t\tAffiche tous les métiers des citoyens du royaume.\n"
    msg.append(utils.surround_markdown(usage))

    usage = "\t* .salary\n"
    usage += "\t\tAffiche votre salaire.\n"
    msg.append(utils.surround_markdown(usage))

    usage = "\t* .monthly_taxes [YYYY-MM]\n"
    usage += "\t\tAffiche la somme des taxes récoltées pour ce mois-ci ou pour le mois renseigné en suivant le format YYYY-MM (par exemple pour Juin 2020 : 2020-06).\n"
    msg.append(utils.surround_markdown(usage))

    usage = "\t* .inventory\n"
    usage += "\t\tVous transmet votre inventaire.\n"
    msg.append(utils.surround_markdown(usage))

    usage = "\t* .create <name> [<description>]\n"
    usage += "\t\tCrée un objet (si vous n'en avez pas déjà créé aujourd'hui).\n"
    msg.append(utils.surround_markdown(usage))

    usage = "\t* .delete <item_id>\n"
    usage += "\t\tSupprime l'objet n°<item_id>. Vous devez en être le propriétaire.\n"
    msg.append(utils.surround_markdown(usage))

    usage = "\t* .trades\n"
    usage += "\t\tVous transmet l'historique des ventes et échanges publics.\n"
    msg.append(utils.surround_markdown(usage))

    usage = "\t* .give <user> <item_id>\n"
    usage += "\t\tDonne l'objet <item_id> à <user>.\n"
    msg.append(utils.surround_markdown(usage))

    usage = "\t* .for_sale\n"
    usage += "\t\tAffiche les objets en vente.\n"
    msg.append(utils.surround_markdown(usage))

    usage = "\t* .sell <item_id> <price> [<user>]\n"
    usage += "\t\tMet en vente l'objet <item_id> au prix de <price>ŧ.\n"
    usage += "\t\tOptionnellement, seul <user> peut acheter cet objet.\n"
    msg.append(utils.surround_markdown(usage))

    usage = "\t* .cancel_sale <item_id>\n"
    usage += "\t\tRetire l'objet <item_id> de la vente.\n"
    msg.append(utils.surround_markdown(usage))

    usage = "\t* .buy <item_id>\n"
    usage += "\t\tAchète l'objet <item_id>.\n"
    msg.append(utils.surround_markdown(usage))
    if ctx.author.id in ADMIN:
        usage = "## Commandes spéciales (pour notre bon Roy et certains privilégiés) :\n"
        usage += "\t* .all_balance\n"
        usage += "\t\tVous transmet par message privé l'état de tous les comptes en banque.\n"
        msg.append(utils.surround_markdown(usage))

        usage = "\t* .all_jobs\n"
        usage += "\t\tTransmet, en privé, tous les métiers des citoyens du royaume, avec le salaire associé.\n"
        msg.append(utils.surround_markdown(usage))

        usage = "\t* .new_job <user> <salary> <title>\n"
        usage += "\t\tAjoute un nouveau métier à <user>. Il devient <title> et est payé <salary>.\n"
        msg.append(utils.surround_markdown(usage))

        usage = "\t* .del_job <user> <job_id>\n"
        usage += "\t\tSupprime le métier <job_id> de <user>.\n"
        msg.append(utils.surround_markdown(usage))

        usage = "\t* .salary [<user>]\n"
        usage += "\t\tVous transmet votre salaire ou celui de <user>.\n"
        msg.append(utils.surround_markdown(usage))

        usage = "\t* .all_salaries\n"
        usage += "\t\tVous transmet les salaires de tous les citoyens.\n"
        msg.append(utils.surround_markdown(usage))

        usage = "\t* .pay_salaries\n"
        usage += "\t\tDéclenche la paye des salaires à tous les citoyens.\n"
        usage += "\t\t(À utiliser avec précaution, commande très peu testée)\n"
        msg.append(utils.surround_markdown(usage))

    dm = await ctx.author.create_dm()
    await utils.send_msg(msg, dm)


@client.command()
@commands.check(utils.is_admin)
async def nini(ctx):
    log_info("nini start")
    message = ctx.message

    filename = "./nini_history_" + ctx.message.channel.name
    c = 0
    if os.path.isfile(filename):
        log_info("nini history file found")
        history = pickle.load(open(filename, "rb"))
        date = history[0]
        all_losers = history[1] 
    else:
        log_error("nini history file not found")
        all_losers = {}
        date = None

    async for m in message.channel.history(limit=None, after=date, oldest_first=True):
        c += 1
        auth = m.author.name
        if auth not in all_losers:
            all_losers[auth] = dict()
        all_losers[auth]["messages"] += 1

        react_lose = False
        losers = set()
        for reaction in m.reactions:
            if reaction.emoji == '🚨':
                if not react_lose:
                    losers.add(auth)
                await m.add_reaction('🚨')
            if reaction.emoji == '👌':
                react_lose = True
                losers = set([l.name for l in await reaction.users().flatten()])

        for l in losers:
            if l not in all_losers:
                all_losers[l] = dict()
            all_losers[l]["errors"] += 1
            all_losers[l]["streak"] = 0

        all_losers[auth]["streak"] += 1
        all_losers[auth]["streak_max"] = max(all_losers[auth]["streak_max"], all_losers[auth]["streak"])

    date = m.created_at
    pickle.dump([date, all_losers], open(filename, "wb"))

    all_losers = sorted([(name, data) for name, data in all_losers.items() if (data["messages"] >= 300 and data["errors"] > 0)],
                        key=lambda x: x[1]["messages"]/x[1]["errors"], reverse=True)
    res = ":drum::nini::drum:\n"
    res.append("`{} | {} | {} | {} | {} | {}`".format("Pseudo".center(20), "# défaites".center(12), "# messages".center(12),
                                                      "Ratio".center(7), "Streak".center(12), "Streak max".center(12)))
    for username, data in all_losers:
        res.append("`{} | {} | {} | {} | {} | {}`".format(username.center(20), str(data["messages"]).center(12), str(data["errors"]).center(12),
                                                          str(int(data["messages"]/data["errors"])).center(7), str(data["streak"]).center(12), str(data["streak_max"]).center(12)))

    log_info('\n'.join(res))
    await utils.send_msg(res, ctx)
    log_info("nini command done! {} messages".format(c))

@client.command()
async def fillon(ctx):
    transacs = bank.get_history(ADMIN[0])
    if transacs is None:
        res = ["Erreur : Pas de compte en banque."]
    else:
        res = []
        res.append("Historique du ministre des finances :")
        res.append("")
        for t in transacs:
            amount = ("{}" + str(t[2]/100)).rjust(10)
            if t[0] == ADMIN[0]:
                username = await get_name(t[1])
                res.append("`{}\t|{}|{}ŧ | '{}'`".format(t[4], username.center(20), amount.format('-'), t[3]))
            elif t[1] == ADMIN[0]:
                username = await get_name(t[0])
                res.append("`{}\t|{}|{}ŧ | '{}'`".format(t[4], username.center(20), amount.format('+'), t[3]))
    log_info('\n'.join(res))
    await utils.send_msg(res, ctx)


@client.command()
async def say(ctx, msg, channel: discord.TextChannel = None):
    inventory = marketplace.get_inventory(ctx.author.id)
    found = False
    for creator_id, name, _, _, _ in inventory:
        if creator_id == TIGRISBOT_CREATOR and name == "Télécommande du TigrisBot":
            found = True
            break
    if not found:
        await ctx.send("Erreur : Vous n'avez pas la Télécommande du TigrisBot")
        return
    if channel is None:
        await ctx.send(msg)
    else:
        await channel.send(msg)


@client.command(name="citizens")
async def get_citizens(ctx):
    dm = await ctx.author.create_dm()
    citizens = bank.get_citizens()
    res = []
    if not citizens:
        await dm.send("La ville est déserte.")
        return

    res.append("Liste des citoyens de Fibreville :")
    for citizen in citizens:
        res.append("{} : {}".format(await get_name(citizen[0]), utils.mention(citizen[0])))
    await utils.send_msg(res, dm)


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


@client.command(name="create", ignore_extra=False)
async def create_item(ctx, name, description = ""):
    description = description[:256]
    item_id = marketplace.create_item(ctx.author.id, name, description)
    if not item_id:
        res = "Erreur : Vous ne pouvez créer qu'un seul objet par jour."
    else:
        res = "Vous venez de créer {} (id : {})".format(name, item_id)
    await ctx.send(res)


@create_item.error
async def create_item_error(ctx, error):
    log_error(error)
    if isinstance(error, commands.MissingRequiredArgument):
        res = "Erreur : Nombre de paramètres insuffisant.\n"
        res += "`.create <name> [<description>]`"
        await ctx.send(res)
    elif isinstance(error, commands.TooManyArguments):
        res = "Erreur : Trop de paramètres.\n"
        res += "N'oubliez pas d'entourer votre nom d'objet ou votre description de guillemets (\")"
        await ctx.send(res)
    else:
        raise error


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

    is_tax_free = ctx.guild.id in TAX_FREE_SERVER

    # Call DB function
    status = bank.send(from_id, to_id, amount, msg, tax_free=is_tax_free)

    # Branch on return status
    if status == 0:
        res = "L'opération est enregistrée.\n"
        if to_id == client.user.id:
            res += "Fais un voeu."
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
async def get_all_salaries(ctx):
    all_salaries = bank.get_all_salaries()
    res = "Salaires des citoyens :\n\n"
    tot = 0
    for user_id, salary in all_salaries:
        tot += salary
        username = await get_name(user_id)
        res += "`{}|{}ŧ`\n".format(username.ljust(30), str(salary/100).rjust(10))

    res += '`' + '-'*42 + "`\n"
    res += "`{}|{}ŧ`\n".format("Total".ljust(30), str(tot/100).rjust(10))
    dm = await ctx.author.create_dm()
    await utils.send_msg(res.split('\n'), dm)


@get_all_salaries.error
async def get_all_salaries_error(ctx, error):
    log_error(error)
    if isinstance(error, commands.CheckFailure):
        res = "Erreur : vous n'avez pas le droit de faire ceci."
        await ctx.send(res)
    else:
        raise error


@client.command(ignore_extra=False)
@commands.check(utils.is_admin)
async def new_job(ctx, user: discord.Member, salary: float, title):
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

    job = bank.remove_job(user_id, job_id)
    if job is None:
        res = "Erreur : Le métier pour le citoyen ({}) ayant pour identifiant {} n'existe pas".format(utils.mention(user_id), job_id)
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

    jobs = bank.get_jobs(user_id)

    res = "Le ou les métiers de **{}** :\n".format(await get_name(user_id))
    res += "```\n"
    for _, job_id, title, salary in jobs:
        res += "* {}".format(title.center(70))
        if user is None or await utils.is_admin(ctx):
            res += "| {}ŧ | {}".format(str(salary/100).rjust(10), job_id)
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


@client.command(name="salary")
async def get_salary(ctx, user: discord.Member = None):
    if user is None:
        user_id = ctx.author.id
    else:
        if not await utils.is_admin(ctx):
            return
        user_id = user.id

    salary = bank.get_salary(user_id)
    if user is not None:
        dm = await ctx.author.create_dm()

        if salary is None:
            res = "Erreur : {} n'a aucun de métier.".format(utils.mention(user_id))
            log_error(res)
        else:
            res = "{} a un salaire mensuel de {} pour l'ensemble de ses métiers.".format(utils.mention(user_id), salary/100)
            log_info(res)

        await dm.send(res)
    else:
        if salary is None:
            res = "Erreur : vous n'avez pas de métier."
            log_error(res)
        else:
            res = "Vous avez un salaire mensuel de {}ŧ pour l'ensemble de vos métiers.".format(salary/100)
            log_info(res)

        await ctx.send(res)


@get_salary.error
async def get_salary_error(ctx, error):
    log_error(error)
    if isinstance(error, commands.BadArgument):
        await ctx.send(error)
    elif isinstance(error, commands.TooManyArguments):
        res = "Erreur : Mauvais nombre de paramètre.\n"
        res += ".salary (classique)\n"
        res += ".salary [<user>] (privilégié)"
        await ctx.send(res)
    else:
        raise error


@client.command()
@commands.check(utils.is_admin)
async def pay_salaries(ctx):
    from_id = ctx.author.id
    ret_values = bank.pay_all_salaries(from_id)

    res = []
    paid = []
    error = []
    for user_id, v, salary in ret_values:
        if v == 1:
            error.append("Erreur : Le compte débiteur ({}) n'existe pas.".format(utils.mention(from_id)))
            log_error(res[-1])
            break

        if v == 0:
            res.append("Son salaire a été versé à {}.\n".format(get_name(user_id)))
            paid.append((user_id, salary))
            log_info(res[-1])
        elif v == 2:
            error.append("Erreur : La salaire de {} est nul.".format(get_name(user_id)))
            log_error(res[-1])
        elif v == 3:
            error.append("Erreur : Le débiteur ({}) n'a plus les fonds nécéssaires.".format(utils.mention(from_id)))
            res.append(error[-1][1])
            log_error(res[-1])
            break

    for user_id, amount in paid:
        user = await client.fetch_user(user_id)
        dm = await user.create_dm()
        await dm.send("Vous avez reçu votre salaire de {}ŧ.".format(amount/100))

    await utils.send_msg(error + res, ctx)


@pay_salaries.error
async def pay_salaries_error(ctx, error):
    log_error(error)
    if isinstance(error, commands.CheckFailure):
        res = "Erreur : vous n'avez pas le droit de faire ceci."
        await ctx.send(res)
    else:
        raise error


@client.command(name="monthly_taxes")
async def get_monthly_taxes(ctx, month = None):
    if month is not None:
        pattern_month = re.compile("(\d\d\d\d-\d\d)")
        match = pattern_month.match(msg[1])
        if match is None:
            res = "Erreur : Mauvais format pour le mois demandé ({})".format(msg[1])
            log_error(res)
            await ctx.send(res)
            return

        month = match.group(1)
        sum_tax = bank.get_monthly_taxes(month)
        if sum_tax is None:
            res = "Aucune taxe n'a été récoltée ce mois-ci."
            log_error(res)
            return res
        res = "Somme des taxes récoltées pour le mois {} : {}ŧ".format(month, sum_tax/100)
    else:
        sum_tax = bank.get_monthly_taxes()
        if sum_tax is None:
            res = "Aucune taxe n'a été récoltée ce mois-ci."
            log_error(res)
            return res
        res = "Somme des taxes récoltées pour ce mois-ci : {}ŧ".format(sum_tax/100)



    log_info(res)
    await ctx.send(res)


@get_monthly_taxes.error
async def get_monthly_taxes_error(ctx, error):
    log_error(error)
    raise error


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
