from dataclasses import dataclass
from typing import Dict, Any

from authlib.integrations.starlette_client import OAuth
from authlib.oauth2 import OAuth2Client
from starlette.config import Config


@dataclass
class OAuthIntegration:
    name: str
    overwrite: bool
    kwargs: Dict[str, Any]


class OAuthSecurityService:

    def __init__(self, oauth_config: Config, *oauth_integrations: OAuthIntegration):
        self._oauth_client = OAuth(oauth_config)
        for integration in oauth_integrations:
            self._oauth_client.register(
                name=integration.name,
                overwrite=integration.overwrite,
                **integration.kwargs
            )

    def __getattr__(self, key: str) -> OAuth2Client:
        try:
            return object.__getattribute__(self, key)
        except AttributeError:
            return self._oauth_client.__getattr__(key)
