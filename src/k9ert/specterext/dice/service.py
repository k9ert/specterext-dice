import datetime
import json
import logging
import pytz

from flask import current_app as app
from flask_babel import lazy_gettext as _
from typing import List
from cryptoadvance.specter.specter_error import SpecterError

from cryptoadvance.specter.user import User

from cryptoadvance.specter.services.service import Service, devstatus_alpha
from cryptoadvance.specter.addresslist import Address
from cryptoadvance.specter.wallet import Wallet

logger = logging.getLogger(__name__)


class DiceService(Service):
    id = "dice"
    name = "Specter Dice"
    icon = "dice/dice_logo.png"
    logo = "dice/dice_logo.png"
    desc = "Send your bet!"
    has_blueprint = True
    blueprint_module = "k9ert.specterext.dice.controller"
    isolated_client = False
    devstatus = devstatus_alpha

    # TODO: As more Services are integrated, we'll want more robust categorization and sorting logic
    sort_priority = 1

    # Service-specific constants
    MIN_PENDING_AUTOWITHDRAWAL_ADDRS = 10

    # ServiceEncryptedStorage field names for Swan
    SPECTER_WALLET_ALIAS = "wallet"
    SWAN_WALLET_ID = "swan_wallet_id"
    ACCESS_TOKEN = "access_token"
    ACCESS_TOKEN_EXPIRES = "expires"
    REFRESH_TOKEN = "refresh_token"
    AUTOWITHDRAWAL_ID = "autowithdrawal_id"
    AUTOWITHDRAWAL_THRESHOLD = "withdrawal_threshold"

    @classmethod
    def is_access_token_valid(cls):
        service_data = cls.get_current_user_service_data()
        if not service_data or not service_data.get(cls.ACCESS_TOKEN_EXPIRES):
            return False
        return (
            service_data[cls.ACCESS_TOKEN_EXPIRES]
            > datetime.datetime.now(tz=pytz.utc).timestamp()
        )

    @classmethod
    def has_refresh_token(cls):
        return cls.REFRESH_TOKEN in cls.get_current_user_service_data()

    @classmethod
    def get_associated_wallet(cls) -> Wallet:
        """Get the Specter `Wallet` that is currently associated with Swan auto-withdrawals"""
        service_data = cls.get_current_user_service_data()
        if not service_data or cls.SPECTER_WALLET_ALIAS not in service_data:
            # Service is not initialized; nothing to do
            return
        try:
            return app.specter.wallet_manager.get_by_alias(
                service_data[cls.SPECTER_WALLET_ALIAS]
            )
        except SpecterError as e:
            logger.debug(e)
            # Referenced an unknown wallet
            # TODO: keep ignoring or remove the unknown wallet from service_data?
            return

    @classmethod
    def set_associated_wallet(cls, wallet: Wallet):
        """Set the Specter `Wallet` that is currently associated with Swan auto-withdrawals"""
        cls.update_current_user_service_data({cls.SPECTER_WALLET_ALIAS: wallet.alias})

    @classmethod
    def reserve_addresses(
        cls, wallet: Wallet, label: str = None, num_addresses: int = 10
    ) -> List[str]:
        """
        * Reserves addresses for Swan auto-withdrawals
        * Sets the associated Specter `Wallet` that will receive auto-withdrawals
        * Removes any existing unused reserved addresses in the previously associated `Wallet`
        * Performs matching cleanup and update on the Swan side

        Overrides base classmethod to add Swan-specific functionality & data management.
        """
        from . import client as swan_client

        # Update Addresses as reserved (aka "associated") with Swan in our Wallet
        addresses = super().reserve_addresses(
            wallet=wallet, label=label, num_addresses=num_addresses
        )

        # Clear out any prior unused reserved addresses if this is a different Wallet
        cur_wallet = cls.get_associated_wallet()
        if cur_wallet and cur_wallet != wallet:
            super().unreserve_addresses(cur_wallet)

        # Store our `Wallet` as the current one for Swan auto-withdrawals
        cls.set_associated_wallet(wallet)

        # Send the new list to Swan (DELETES any unused ones; creates a new SWAN_WALLET_ID if needed)
        swan_client.update_autowithdrawal_addresses(
            specter_wallet_name=wallet.name,
            specter_wallet_alias=wallet.alias,
            addresses=addresses,
        )

        return addresses

    @classmethod
    def set_autowithdrawal_settings(cls, wallet: Wallet, btc_threshold: str):
        """
        btc_threshold: "0", "0.01", "0.025", or "0.05"

        Performs a lot of maintenance behind the scenes in order to keep Specter's
        internal data in sync (e.g. resetting previously reserved addresses) and the same
        in the api to keep Swan's notion of a wallet and list of addrs in sync.
        """
        from . import client as swan_client

        # Reserve auto-withdrawal addresses for this Wallet; clear out an unused ones in a prior wallet
        cls.reserve_addresses(
            wallet=wallet, num_addresses=cls.MIN_PENDING_AUTOWITHDRAWAL_ADDRS
        )

        # Send the autowithdrawal threshold
        swan_client.set_autowithdrawal(btc_threshold=btc_threshold)

        # Store the threshold setting in the User's service data
        cls.update_current_user_service_data(
            {SwanService.AUTOWITHDRAWAL_THRESHOLD: btc_threshold}
        )

    @classmethod
    def on_user_login(cls):
        pass
