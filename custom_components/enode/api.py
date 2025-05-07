"""API for Enode bound to Home Assistant OAuth."""

from enum import StrEnum
from typing import Literal

from aiohttp import ClientResponse, ClientResponseError
from aiohttp.hdrs import METH_DELETE, METH_GET, METH_POST
from yarl import URL

from homeassistant.helpers import config_entry_oauth2_flow

from .const import LOGGER, PRODUCTION_API_URL, SANDBOX_API_URL
from .models import ChargeAction, ErrorResponse, Link, Response, T, Vehicle, Webhook

SCOPES = [
    "battery:control:operation_mode",
    "battery:read:location",
    "battery:read:data",
    "charger:control:charging",
    "charger:read:data",
    "hvac:control:mode",
    "hvac:read:data",
    "inverter:read:data",
    "inverter:read:location",
    "meter:read:location",
    "meter:read:data",
    "vehicle:control:charging",
    "vehicle:read:data",
    "vehicle:read:location",
]


class Language(StrEnum):
    """Language options for Enode."""

    BROWSER = "browser"
    DA_DK = "da-DK"
    DE_DE = "de-DE"
    EN_US = "en-US"
    EN_GB = "en-GB"
    ES_ES = "es-ES"
    FI_FI = "fi-FI"
    FR_FR = "fr-FR"
    IT_IT = "it-IT"
    NB_NO = "nb-NO"
    NL_NL = "nl-NL"
    NL_BE = "nl-BE"
    PT_PT = "pt-PT"
    RO_RO = "ro-RO"
    SV_SE = "sv-SE"


class Vendor(StrEnum):
    """Vendor options for Enode."""

    AFORE = "AFORE"
    APSYSTEMS = "APSYSTEMS"
    CSISOLAR = "CSISolar"
    DEYE = "Deye"
    ENPHASE = "ENPHASE"
    FOXESS = "FOXESS"
    FRONIUS = "FRONIUS"
    GIVENERGY = "GIVENERGY"
    GOODWE = "GOODWE"
    GROWATT = "GROWATT"
    HOYMILES = "Hoymiles"
    HUAWEI = "HUAWEI"
    INVT = "INVT"
    SMA = "SMA"
    SOFAR = "SOFAR"
    SOLAREDGE = "SOLAREDGE"
    SOLARK = "SOLARK"
    SOLAX = "SOLAX"
    SOLIS = "SOLIS"
    SOLPLANET = "SOLPLANET"
    SUNGROW = "SUNGROW"
    SUNSYNK = "SUNSYNK"
    TESLA = "TESLA"
    TSUN = "TSUN"
    ACURA = "ACURA"
    AUDI = "AUDI"
    BMW = "BMW"
    HONDA = "HONDA"
    HYUNDAI = "HYUNDAI"
    JAGUAR = "JAGUAR"
    LANDROVER = "LANDROVER"
    KIA = "KIA"
    MERCEDES = "MERCEDES"
    MINI = "MINI"
    NISSAN = "NISSAN"
    PEUGEOT = "PEUGEOT"
    PORSCHE = "PORSCHE"
    RENAULT = "RENAULT"
    SEAT = "SEAT"
    SKODA = "SKODA"
    VOLKSWAGEN = "VOLKSWAGEN"
    VOLVO = "VOLVO"
    FORD = "FORD"
    OPEL = "OPEL"
    DS = "DS"
    TOYOTA = "TOYOTA"
    LEXUS = "LEXUS"
    CITROEN = "CITROEN"
    CUPRA = "CUPRA"
    VAUXHALL = "VAUXHALL"
    FIAT = "FIAT"
    RIVIAN = "RIVIAN"
    NIO = "NIO"
    CHEVROLET = "CHEVROLET"
    GMC = "GMC"
    CADILLAC = "CADILLAC"
    XPENG = "XPENG"
    POLESTAR = "POLESTAR"
    SUBARU = "SUBARU"
    JEEP = "JEEP"
    MAZDA = "MAZDA"
    MG = "MG"
    CHRYSLER = "CHRYSLER"
    DODGE = "DODGE"
    RAM = "RAM"
    ALFAROMEO = "ALFAROMEO"
    LANCIA = "LANCIA"
    LUCID = "LUCID"
    BYD = "BYD"
    TADO = "TADO"
    MILL = "MILL"
    ADAX = "ADAX"
    ECOBEE = "ECOBEE"
    SENSIBO = "SENSIBO"
    HONEYWELL = "HONEYWELL"
    RESIDEO = "RESIDEO"
    MITSUBISHI = "MITSUBISHI"
    MICROMATIC = "MICROMATIC"
    NIBE = "NIBE"
    PANASONIC = "PANASONIC"
    TOSHIBA = "TOSHIBA"
    DAIKIN = "DAIKIN"
    NEST = "NEST"
    FUJITSU = "FUJITSU"
    BOSCH = "BOSCH"
    NETATMO = "NETATMO"
    ZAPTEC = "ZAPTEC"
    EASEE = "EASEE"
    WALLBOX = "WALLBOX"
    EO = "EO"
    CHARGEAMPS = "CHARGEAMPS"
    EVBOX = "EVBOX"
    GOE = "GOE"
    CHARGEPOINT = "CHARGEPOINT"
    ENELX = "ENELX"
    OHME = "OHME"
    GARO = "GARO"
    SCHNEIDER = "SCHNEIDER"
    PODPOINT = "PODPOINT"
    KEBA = "KEBA"
    HYPERVOLT = "HYPERVOLT"
    MYENERGI = "MYENERGI"
    HEIDELBERG = "HEIDELBERG"


class VendorType(StrEnum):
    """Vendor type options for Enode."""

    VEHICLE = "vehicle"
    CHARGER = "charger"
    HVAC = "hvac"
    INVERTER = "inverter"
    BATTERY = "battery"
    METER = "meter"


class EnodeError(ClientResponseError):
    """Enode API error."""

    def __init__(self, response: ClientResponse, data: dict) -> None:
        """Initialize Enode error."""
        self.data = ErrorResponse.model_validate(data)
        super().__init__(
            request_info=response.request_info,
            history=response.history,
            status=response.status,
            message=f"{self.data.title}: {self.data.detail}",
            headers=response.headers,
        )


class EnodeClient:
    """Enode API client."""

    def __init__(
        self,
        oauth_session: config_entry_oauth2_flow.OAuth2Session,
        sandbox: bool = False,
    ) -> None:
        """Initialize Enode auth."""
        self._oauth_session = oauth_session
        self._api_url = SANDBOX_API_URL if sandbox else PRODUCTION_API_URL

    async def _make_request(
        self, type_: T, method: str, path: str, **kwargs
    ) -> Response[T]:
        """Make a request to the Enode API."""
        url = URL(self._api_url).with_path(path)
        LOGGER.debug("Making %s request to %s", method, url)
        headers = kwargs.pop("headers", {})
        headers["Content-Type"] = "application/json"
        response = await self._oauth_session.async_request(
            method=method, url=url, headers=headers, **kwargs
        )
        LOGGER.debug(
            "Received %d response having content length of %d",
            response.status,
            response.content_length or 0,
        )
        is_error = response.status == 400
        if not response.ok and not is_error:
            response.raise_for_status()
        data = await response.json()
        if is_error:
            raise EnodeError(response, data)
        return type_.model_validate(data)

    @property
    def client_id(self) -> str | None:
        """Return the client ID."""
        return getattr(self._oauth_session.implementation, "client_id", None)

    async def list_vehicles(self) -> list[Vehicle]:
        """List vehicles."""
        response = await self._make_request(
            Response[list[Vehicle]], method=METH_GET, path="/vehicles"
        )
        return response.data

    async def list_user_vehicles(self, user_id: str) -> list[Vehicle]:
        """List vehicles."""
        response = await self._make_request(
            Response[list[Vehicle]],
            method=METH_GET,
            path=f"/users/{user_id}/vehicles",
        )
        return response.data

    async def user_link(
        self,
        user_id: str,
        redirect_uri: str | URL,
        language: Language = Language.BROWSER,
        vendor: Vendor | None = None,
        vendor_type: VendorType | None = None,
    ) -> Link:
        """Link a device to a user."""
        if vendor_type is None:
            scopes = SCOPES
        else:
            scopes = [s for s in SCOPES if s.startswith(f"{vendor_type.value}:")]
        data = {
            "language": language.value,
            "redirectUri": str(redirect_uri),
            "scopes": scopes,
        }
        if vendor:
            data["vendor"] = vendor.value
        if vendor_type:
            data["vendorType"] = vendor_type.value
        return await self._make_request(
            Link,
            method=METH_POST,
            path=f"/users/{user_id}/link",
            json=data,
        )

    async def control_charging(
        self, vehicle_id: str, action: Literal["START", "STOP"]
    ) -> None:
        """Control charging for a vehicle."""
        data = {
            "action": action,
        }
        await self._make_request(
            ChargeAction,
            method=METH_POST,
            path=f"/vehicles/{vehicle_id}/charging",
            json=data,
        )

    async def create_webhook(
        self,
        url: str | URL,
        secret: str,
        events: list[str] | None = None,
        api_version: str | None = None,
    ) -> Webhook:
        """Create a webhook."""
        if events is None:
            events = ["*"]
        data = {
            "url": str(url),
            "secret": secret,
            "events": events,
        }
        if api_version:
            data["apiVersion"] = api_version
        return await self._make_request(
            Webhook,
            method=METH_POST,
            path="/webhooks",
            json=data,
        )

    async def delete_webhook(self, webhook: str | Webhook) -> None:
        """Delete a webhook."""
        if isinstance(webhook, Webhook):
            webhook = webhook.id
        await self._make_request(
            Response[None],
            method=METH_DELETE,
            path=f"/webhooks/{webhook}",
        )
