"""
Swan API uses PKCE OAuth2. Per Swan's API team: The client secret here is not considered
to be a real secret. There is no reasonable attack vector for this secret being public.
"""


class BaseConfig:
    pass


class ProductionConfig(BaseConfig):
    pass
