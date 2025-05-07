"""Constants for the Enode integration."""

from datetime import timedelta
import logging
from typing import Final

DOMAIN: Final[str] = "enode"

LOGGER: Final[logging.Logger] = logging.getLogger(__package__)

CONF_SANDBOX: Final[str] = "sandbox"
CONF_USER_ID: Final[str] = "user_id"

DATA_COORDINATORS: Final[str] = "coordinators"

STATE_REACHABLE: Final[str] = "reachable"
STATE_UNREACHABLE: Final[str] = "unreachable"

OAUTH2_AUTHORIZE: Final[str] = ""
PRODUCTION_OAUTH2_TOKEN: Final[str] = "https://oauth.production.enode.io/oauth2/token"
SANDBOX_OAUTH2_TOKEN: Final[str] = "https://oauth.sandbox.enode.io/oauth2/token"
PRODUCTION_API_URL: Final[str] = "https://enode-api.production.enode.io"
SANDBOX_API_URL: Final[str] = "https://enode-api.sandbox.enode.io"

UPDATE_INTERVAL: Final[timedelta] = timedelta(minutes=5)
