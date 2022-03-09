import os
from .config import SpecterProductionConfig

class AppProductionConfig(SpecterProductionConfig):
    # Where should the User endup if he hits the root of that domain?
    ROOT_URL_REDIRECT = "/spc/ext/dice"
    # I guess this is the only extension which should be available?
    EXTENSION_LIST = [
        "k9ert.specterext.dice.service"
    ]
    SPECTER_DATA_FOLDER=os.path.expanduser("~/.dice")