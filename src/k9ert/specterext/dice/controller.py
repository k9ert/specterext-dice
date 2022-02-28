import json
import logging

from decimal import Decimal
from flask import redirect, render_template, request, url_for, flash
from flask import current_app as app
from flask import session
from flask.json import jsonify
from flask_babel import lazy_gettext as _
from flask_login import current_user, login_required
from functools import wraps
from cryptoadvance.specter.user import User
from cryptoadvance.specter.wallet import Wallet

from .service import DiceService
from cryptoadvance.specter.services.controller import user_secret_decrypted_required


logger = logging.getLogger(__name__)

dice_endpoint = DiceService.blueprint



@dice_endpoint.route("/")
@login_required
def index():
    wallet_names = sorted(current_user.wallet_manager.wallets.keys())
    wallets = [current_user.wallet_manager.wallets[name] for name in wallet_names]
    return render_template(
        "dice/index.jinja", wallet=app.specter.ext["dice"].get_associated_wallet(),
    )


@dice_endpoint.route("/check")
def check():
    wallet = current_user.wallet_manager.get_by_alias("myhot_2")
    txlist = wallet.txlist(
        fetch_transactions=True,
        current_blockheight=0,
        
    )

    for tx in txlist:
        if tx["amount"] < 20:
            if session.get(tx["txid"]) == None:
                print(tx)

    return render_template(
        "dice/check.jinja", wallet=wallet, txlist=txlist,  services=app.specter.service_manager.services,
    )


@dice_endpoint.route("/settings", methods=["GET"])
@login_required
def settings_get():
    associated_wallet: Wallet = app.specter.ext["dice"].get_associated_wallet()

    # Get the user's Wallet objs, sorted by Wallet.name
    wallet_names = sorted(current_user.wallet_manager.wallets.keys())
    wallets = [current_user.wallet_manager.wallets[name] for name in wallet_names]

    return render_template(
        "dice/settings.jinja",
        associated_wallet=associated_wallet,
        wallets=wallets,
        cookies=request.cookies,
    )

@dice_endpoint.route("/settings", methods=["POST"])
@login_required
def settings_post():
    show_menu = request.form["show_menu"]
    user = app.specter.user_manager.get_user()
    if show_menu == "yes":
        user.add_service(DiceService.id)
    else:
        user.remove_service(DiceService.id)
    used_wallet_alias = request.form.get("used_wallet")
    if used_wallet_alias != None:
        wallet = current_user.wallet_manager.get_by_alias(used_wallet_alias)
        app.specter.ext["dice"].set_associated_wallet(wallet)
    return redirect(url_for(f"{DiceService.get_blueprint_name()}.settings_get"))