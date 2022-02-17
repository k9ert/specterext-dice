"""
Swan API uses PKCE OAuth2. Per Swan's API team: The client secret here is not considered
to be a real secret. There is no reasonable attack vector for this secret being public.
"""
import os
from cryptoadvance.specter.config import ProductionConfig as SpecterProductionConfig


class BaseConfig:
    pass


class ProductionConfig(BaseConfig):
    pass

class AppProductionConfig(SpecterProductionConfig):
    # Where should the User endup if he hits the root of that domain?
    ROOT_URL_REDIRECT = "/spc/ext/dice"
    # I guess this is the only extension which should be available?
    EXTENSION_LIST = [
        "k9ert.specterext.dice.service"
    ]
    SPECTER_DATA_FOLDER=os.path.expanduser("~/.dice")