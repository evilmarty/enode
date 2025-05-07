"""Models for Enode API responses."""

from datetime import datetime, time
from enum import StrEnum
from typing import Literal, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T", bound=BaseModel)


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
