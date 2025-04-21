"""Constants for the Enode integration."""

from datetime import timedelta
import logging
from typing import Final

DOMAIN: Final[str] = "enode"

LOGGER: Final[logging.Logger] = logging.getLogger(__package__)

DATA_USER_ID: Final[str] = "user_id"
DATA_COORDINATORS: Final[str] = "coordinators"
DATA_STORE: Final[str] = "store"

STORAGE_VERSION: Final[int] = 1
STORAGE_KEY: Final[str] = DOMAIN

OAUTH2_AUTHORIZE: Final[str] = ""
OAUTH2_TOKEN: Final[str] = "https://oauth.sandbox.enode.io/oauth2/token"
API_URL: Final[str] = "https://enode-api.sandbox.enode.io"

UPDATE_INTERVAL: Final[timedelta] = timedelta(minutes=5)
