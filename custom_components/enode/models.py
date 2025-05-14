"""Models for Enode API responses."""

from datetime import datetime, time
from enum import StrEnum
from typing import Annotated, Literal, TypeVar

from pydantic import BaseModel, Field, RootModel

T = TypeVar("T", bound=BaseModel)


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


class VendorType(StrEnum):
    """Vendor type options for Enode."""

    VEHICLE = "vehicle"
    CHARGER = "charger"
    HVAC = "hvac"
    INVERTER = "inverter"
    BATTERY = "battery"
    METER = "meter"

    @property
    def webhook_events(self) -> list["WebhookEventType"]:
        """Return a list of webhook events for this vendor type."""
        return WebhookEventType.for_vendor_type(self)


class WebhookEventType(StrEnum):
    """Webhook event options for Enode."""

    ALL = "*"
    USER_VEHICLE_DISCOVERED = "user:vehicle:discovered"
    USER_VEHICLE_UPDATED = "user:vehicle:updated"
    USER_VEHICLE_DELETED = "user:vehicle:deleted"
    USER_VEHICLE_SMART_CHARGING_STATUS_UPDATED = (
        "user:vehicle:smart-charging-status-updated"
    )
    USER_CHARGE_ACTION_UPDATED = "user:charge-action:updated"
    USER_VENDOR_ACTION_UPDATED = "user:vendor-action:updated"
    USER_SCHEDULE_EXECUTION_UPDATED = "user:schedule:execution-updated"
    USER_CHARGER_DISCOVERED = "user:charger:discovered"
    USER_CHARGER_UPDATED = "user:charger:updated"
    USER_CHARGER_DELETED = "user:charger:deleted"
    USER_HVAC_DISCOVERED = "user:hvac:discovered"
    USER_HVAC_UPDATED = "user:hvac:updated"
    USER_HVAC_DELETED = "user:hvac:deleted"
    USER_INVERTER_DISCOVERED = "user:inverter:discovered"
    USER_INVERTER_UPDATED = "user:inverter:updated"
    USER_INVERTER_DELETED = "user:inverter:deleted"
    USER_INVERTER_STATISTICS_UPDATED = "user:inverter:statistics-updated"
    USER_CREDENTIALS_INVALIDATED = "user:credentials:invalidated"
    USER_BATTERY_DISCOVERED = "user:battery:discovered"
    USER_BATTERY_UPDATED = "user:battery:updated"
    USER_BATTERY_DELETED = "user:battery:deleted"
    ENODE_WEBHOOK_TEST = "enode:webhook:test"
    USER_METER_DISCOVERED = "user:meter:discovered"
    USER_METER_UPDATED = "user:meter:updated"
    USER_METER_DELETED = "user:meter:deleted"

    @classmethod
    def for_vendor_type(cls, vendor_type: VendorType) -> list["WebhookEventType"]:
        """Return a list of webhook events for a vendor type."""
        return [x for x in cls if x.startswith(f"user:{vendor_type.value}:")]


class PowerDeliveryState(StrEnum):
    """Power delivery state enumeration."""

    UNKNOWN = "UNKNOWN"
    UNPLUGGED = "UNPLUGGED"
    PLUGGED_IN_INITIALIZING = "PLUGGED_IN:INITIALIZING"
    PLUGGED_IN_CHARGING = "PLUGGED_IN:CHARGING"
    PLUGGED_IN_STOPPED = "PLUGGED_IN:STOPPED"
    PLUGGED_IN_COMPLETE = "PLUGGED_IN:COMPLETE"
    PLUGGED_IN_NO_POWER = "PLUGGED_IN:NO_POWER"
    PLUGGED_IN_FAULT = "PLUGGED_IN:FAULT"
    PLUGGED_IN_DISCHARGING = "PLUGGED_IN:DISCHARGING"


class ErrorResponse(BaseModel):
    """Error response model."""

    type: str
    title: str
    detail: str


class Pagination(BaseModel):
    """Pagination model."""

    before: str | None = Field(default=None)
    after: str | None = Field(default=None)


class Response[T](BaseModel):
    """Base response model."""

    data: T
    pagination: Pagination


class Link(BaseModel):
    """Link model."""

    url: str = Field(alias="linkUrl")
    token: str = Field(alias="linkToken")


class VehicleInformation(BaseModel):
    """Vehicle information model."""

    display_name: str | None = Field(default=None, alias="displayName")
    vin: str | None = Field(default=None)
    brand: str | None = Field(default=None)
    model: str | None = Field(default=None)
    year: int | None = Field(default=None)


class ChargeState(BaseModel):
    """Charge state model."""

    charge_rate: float | None = Field(default=None, alias="chargeMode")
    charge_time_remaining: int | None = Field(default=None, alias="chargeTimeRemaining")
    is_fully_charged: bool | None = Field(default=None, alias="isFullyCharged")
    is_plugged_in: bool | None = Field(default=None, alias="isPluggedIn")
    is_charging: bool | None = Field(default=None, alias="isCharging")
    battery_level: float | None = Field(default=None, alias="batteryLevel")
    range: float | None = Field(default=None, alias="range")
    battery_capacity: float | None = Field(default=None, alias="batteryCapacity")
    charge_limit: float | None = Field(default=None, alias="chargeLimit")
    last_updated: datetime | None = Field(default=None, alias="lastUpdated")
    power_delivery_state: PowerDeliveryState | None = Field(
        default=None, alias="powerDeliveryState"
    )
    max_current: float | None = Field(default=None, alias="maxCurrent")


class SmartChargingPolicy(BaseModel):
    """Smart charging policy model."""

    deadline: time | None = Field(default=None)
    is_enabled: bool | None = Field(default=None, alias="isEnabled")
    minimum_charge_limit: float | None = Field(default=None, alias="minimumChargeLimit")


class SmartChargingStatusState(StrEnum):
    """Smart charging status state enumeration."""

    DISABLED = "DISABLED"
    CONSIDERING = "CONSIDERING"
    UNKNOWN = "UNKNOWN"
    PLAN_EXECUTING_STOPPING = "PLAN:EXECUTING:STOPPING"
    PLAN_EXECUTING_STOP_FAILED = "PLAN:EXECUTING:STOP_FAILED"
    PLAN_EXECUTING_STOPPED = "PLAN:EXECUTING:STOPPED"
    PLAN_EXECUTING_STOPPED_AWAITING_PRICES = "PLAN:EXECUTING:STOPPED:AWAITING_PRICES"
    PLAN_EXECUTING_STARTING = "PLAN:EXECUTING:STARTING"
    PLAN_EXECUTING_START_FAILED = "PLAN:EXECUTING:START_FAILED"
    PLAN_EXECUTING_STARTED = "PLAN:EXECUTING:STARTED"
    PLAN_EXECUTING_CHARGE_INTERRUPTED = "PLAN:EXECUTING:CHARGE_INTERRUPTED"
    PLAN_EXECUTING_OVERRIDDEN = "PLAN:EXECUTING:OVERRIDDEN"
    PLAN_ENDED_FINISHED = "PLAN:ENDED:FINISHED"
    PLAN_ENDED_UNPLUGGED = "PLAN:ENDED:UNPLUGGED"
    PLAN_ENDED_FAILED = "PLAN:ENDED:FAILED"
    PLAN_ENDED_DISABLED = "PLAN:ENDED:DISABLED"
    PLAN_ENDED_DEADLINE_CHANGED = "PLAN:ENDED:DEADLINE_CHANGED"
    FULLY_CHARGED = "FULLY_CHARGED"


class SmartChargingStatus(BaseModel):
    """Smart charging status model."""

    updated_at: datetime = Field(alias="updatedAt")
    vehicle_id: str = Field(alias="vehicleId")
    user_id: str = Field(alias="userId")
    vendor: str
    state: SmartChargingStatusState
    state_changed_at: datetime = Field(alias="stateChangedAt")
    consideration: dict | None = Field(default=None)
    plan: dict | None = Field(default=None)
    smart_override: dict | None = Field(default=None)


class Location(BaseModel):
    """Location model."""

    id: str | None = Field(default=None)
    latitude: float | None = Field(default=None)
    longitude: float | None = Field(default=None)
    last_updated: datetime | None = Field(default=None, alias="lastUpdated")


class Odometer(BaseModel):
    """Odometer model."""

    distance: float | None = Field(default=None)
    last_updated: datetime | None = Field(default=None, alias="lastUpdated")


class Capability(BaseModel):
    """Capability model."""

    is_capable: bool = Field(alias="isCapable")
    intervention_ids: list[str] = Field(alias="interventionIds")


class VehicleCapabilities(BaseModel):
    """Vehicle capabilities model."""

    information: Capability
    charge_state: Capability = Field(alias="chargeState")
    location: Capability
    odometer: Capability
    set_max_current: Capability = Field(alias="setMaxCurrent")
    start_charging: Capability = Field(alias="startCharging")
    stop_charging: Capability = Field(alias="stopCharging")
    smart_charging: Capability = Field(alias="smartCharging")


class Vehicle(BaseModel):
    """Vehicle model."""

    id: str
    user_id: str = Field(alias="userId")
    vendor: str
    is_reachable: bool | None = Field(default=None, alias="isReachable")
    last_seen: datetime = Field(alias="lastSeen")
    information: VehicleInformation
    charge_state: ChargeState = Field(alias="chargeState")
    smart_charging_policy: SmartChargingPolicy = Field(
        default=None, alias="smartChargingPolicy"
    )
    location: Location
    odometer: Odometer
    capabilities: VehicleCapabilities
    scopes: list[str]


class ActionState(StrEnum):
    """Action state enumeration."""

    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class FailureReason(BaseModel):
    """Failure reason model."""

    type: str
    detail: str


class ChargeAction(BaseModel):
    """Charge action model."""

    id: str
    user_id: str = Field(alias="userId")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    completed_at: datetime | None = Field(default=None, alias="completedAt")
    state: ActionState
    target_id: str = Field(alias="targetId")
    target_type: Literal["vehicle", "charger"] = Field(alias="targetType")
    kind: Literal["START", "STOP"]
    failure_reason: FailureReason | None = Field(default=None, alias="failureReason")


class BasicUser(BaseModel):
    """Basic user model."""

    id: str


class WebhookAuthentication(BaseModel):
    """Webhook authentication model."""

    header_name: str = Field(alias="headerName")


class Webhook(BaseModel):
    """Webhook model."""

    id: str
    url: str
    events: list[str]
    is_active: bool = Field(alias="isActive")
    created_at: datetime = Field(alias="createdAt")
    api_version: str | None = Field(alias="apiVersion", default=None)
    last_success: datetime = Field(alias="lastSuccess")
    authentication: WebhookAuthentication | None = Field(default=None)


class BaseWebhookEvent(BaseModel):
    """Base webhook event model."""

    event: str
    version: str
    created_at: datetime = Field(alias="createdAt")


class WebhookUserVehicleDiscoveredEvent(BaseWebhookEvent):
    """Webhook user vehicle discovered event model."""

    event: Literal["user:vehicle:discovered"]
    user: BasicUser
    vehicle: Vehicle


class WebhookUserVehicleUpdatedEvent(BaseWebhookEvent):
    """Webhook user vehicle updated event model."""

    event: Literal["user:vehicle:updated"]
    user: BasicUser
    vehicle: Vehicle


class WebhookUserVehicleDeletedEvent(BaseWebhookEvent):
    """Webhook user vehicle deleted event model."""

    event: Literal["user:vehicle:deleted"]
    user: BasicUser
    vehicle: Vehicle


class WebhookUserVehicleSmartChargingStatusUpdatedEvent(BaseWebhookEvent):
    """Webhook user vehicle smart charging status updated event model."""

    event: Literal["user:vehicle:smart-charging-status-updated"]
    user: BasicUser
    smart_charging_status: SmartChargingStatus = Field(alias="smartChargingStatus")


class WebhookUserCredentialsInvalidatedEvent(BaseWebhookEvent):
    """Webhook user credentials invalidated event model."""

    event: Literal["user:credentials:invalidated"]
    user: BasicUser
    vendor: str


class WebhookUserVendorActionUpdatedEvent(BaseWebhookEvent):
    """Webhook user vendor action updated event model."""

    event: Literal["user:vendor-action:updated"]
    user: BasicUser
    vendor_action: dict
    updated_fields: list[str] = Field(alias="updatedFields")


class WebhookUserScheduleExecutionUpdatedEvent(BaseWebhookEvent):
    """Webhook user schedule execution updated event model."""

    event: Literal["user:schedule:execution-updated"]
    user: BasicUser
    status: dict
    schedule: dict
    updated_fields: list[str] = Field(alias="updatedFields")


class WebhookSystemHeartbeatEvent(BaseWebhookEvent):
    """Webhook heartbeat event model."""

    event: Literal["system:heartbeat"]
    pending_events: int = Field(alias="pendingEvents")


class WebhookTestEvent(BaseWebhookEvent):
    """Webhook test event model."""

    event: Literal["enode:webhook:test"]


class WebhookEvents(RootModel):
    """Webhook events model."""

    root: list[
        Annotated[
            WebhookSystemHeartbeatEvent
            | WebhookTestEvent
            | WebhookUserVehicleDiscoveredEvent
            | WebhookUserVehicleUpdatedEvent
            | WebhookUserVehicleDeletedEvent
            | WebhookUserVehicleSmartChargingStatusUpdatedEvent
            | WebhookUserCredentialsInvalidatedEvent
            | WebhookUserVendorActionUpdatedEvent
            | WebhookUserScheduleExecutionUpdatedEvent,
            Field(discriminator="event"),
        ]
    ]

    def __iter__(self):
        """Iterate over the events."""
        return iter(self.root)

    def __getitem__(self, item):
        """Get an event by index."""
        return self.root[item]


class WebhookTestEndpoint(BaseModel):
    """Webhook test endpoint response model."""

    code: int
    headers: list[str] | None = Field(default=None)
    body: str


class WebhookTest(BaseModel):
    """Webhook test response model."""

    status: Literal["SUCCESS", "FAILURE"]
    description: str
    response: WebhookTestEndpoint | None = Field(default=None)

    @property
    def is_success(self) -> bool:
        """Check if the test was successful."""
        return self.status == "SUCCESS"

    @property
    def is_failure(self) -> bool:
        """Check if the test failed."""
        return self.status == "FAILURE"
