from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

from ..opc import opc

router = APIRouter()


# -------------------------
# Response Model (GET)
# -------------------------

class SewPayload(BaseModel):
    """Full SEW status + settings returned to the frontend."""

    sew_speed: Optional[float] = None
    sew_acceleration: Optional[float] = None
    sew_deceleration: Optional[float] = None
    sew_release_torque: Optional[float] = None
    sew_alarm_mask: Optional[float] = None
    sew_initial_cycle_speed: Optional[float] = None
    sew_torque_limit_timer: Optional[int] = None

# -------------------------
# GET Status Endpoint
# -------------------------

@router.get("/api/sew_status", response_model=SewPayload)
def get_sew_status() -> SewPayload:
    sew_speed = opc.read("sew_speed")
    sew_acceleration = opc.read("sew_acceleration")
    sew_deceleration = opc.read("sew_deceleration")
    sew_release_torque = opc.read("sew_release_torque")
    sew_alarm_mask = opc.read("sew_alarm_mask")
    sew_initial_cycle_speed = opc.read("sew_initial_cycle_speed")
    sew_torque_limit_timer = opc.read("sew_torque_limit_timer")

    return SewPayload(
        sew_speed=sew_speed,
        sew_acceleration=sew_acceleration,
        sew_deceleration=sew_deceleration,
        sew_release_torque=sew_release_torque,
        sew_alarm_mask=sew_alarm_mask,
        sew_initial_cycle_speed=sew_initial_cycle_speed,
        sew_torque_limit_timer=sew_torque_limit_timer,
    )

# -------------------------
# Calibration Status Model
# -------------------------

@router.get("/api/sew_calibration_status")
def get_sew_calibration_status():
    sew_calibration_done = opc.read("sew_calibration_done")
    return {"sew_calibration_done": sew_calibration_done}

@router.get("/api/sew_error_status")
def get_sew_error_status():
    sew_error = opc.read("sew_error")
    return {"sew_error": sew_error}

@router.get("/api/sew_rotor_lock_status")
def get_sew_rotor_lock_status():
    sew_rotor_lock = opc.read("sew_rotor_lock")
    return {"sew_rotor_lock": sew_rotor_lock}

# -------------------------
# Writable Settings Model (POST)
# -------------------------

class SewSettingsPayload(BaseModel):
    """Writable SEW settings from the frontend."""
    sew_speed: Optional[float] = None
    sew_acceleration: Optional[float] = None
    sew_deceleration: Optional[float] = None
    sew_release_torque: Optional[float] = None
    sew_alarm_mask: Optional[float] = None
    sew_initial_cycle_speed: Optional[float] = None
    sew_torque_limit_timer: Optional[int] = None


# -------------------------
# POST Settings Endpoint
# -------------------------

@router.post("/api/sew_status", response_model=SewPayload)
def set_sew_status(payload: SewSettingsPayload) -> SewPayload:
    """Update SEW settings (partial update) and return the full status."""

    if payload.sew_speed is not None:
        opc.write("sew_speed", payload.sew_speed)

    if payload.sew_acceleration is not None:
        opc.write("sew_acceleration", payload.sew_acceleration)

    if payload.sew_deceleration is not None:
        opc.write("sew_deceleration", payload.sew_deceleration)

    if payload.sew_release_torque is not None:
        opc.write("sew_release_torque", payload.sew_release_torque)

    if payload.sew_alarm_mask is not None:
        opc.write("sew_alarm_mask", payload.sew_alarm_mask)

    if payload.sew_initial_cycle_speed is not None:
        opc.write("sew_initial_cycle_speed", payload.sew_initial_cycle_speed)

    if payload.sew_torque_limit_timer is not None:
        opc.write("sew_torque_limit_timer", payload.sew_torque_limit_timer)

    return get_sew_status()


# -------------------------
# POST: Trigger Calibration
# -------------------------

@router.post("/api/sew_calibrate")
def sew_calibrate(payload: dict):
    value = payload.get("sew_calibrate")          # Extract value from dict
    opc.write("sew_calibrate", value)             # Write to OPC
    return {"sew_calibrate": value}               # Return confirmation

@router.post("/api/sew_rotor_lock_status")
def set_sew_rotor_lock_status(payload: dict):
    value = payload.get("sew_rotor_lock")            # Read value out of dict
    opc.write("sew_rotor_lock", value)               # Write to OPC
    return {"sew_rotor_lock": value}                 # Return confirmation
