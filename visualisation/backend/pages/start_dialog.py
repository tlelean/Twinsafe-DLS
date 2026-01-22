from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from ..opc import opc

router = APIRouter()


class StartDialogState(BaseModel):
    section_number: Optional[str] = None
    test_name: Optional[str] = None
    hold_period: Optional[str] = None
    test_pressure: Optional[str] = None


def _to_text(value) -> str:
    if value is None:
        return ""
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value).strip()


@router.get("/api/start-dialog")
def get_start_dialog_state():
    return _read_start_dialog_state()


@router.post("/api/start-dialog")
def update_start_dialog_state(payload: StartDialogState):
    updates = {
        "section_number": payload.section_number,
        "test_name": payload.test_name,
        "hold_period": payload.hold_period,
        "test_pressure": payload.test_pressure,
    }

    try:
        for key, value in updates.items():
            if value is not None:
                opc.write(key, value)
    except KeyError as exc:
        raise HTTPException(status_code=500, detail=f"Missing OPC node: {exc}") from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"OPC write failed: {exc}") from exc

    return _read_start_dialog_state()


def _read_start_dialog_state() -> dict:
    try:
        section_number = opc.read("section_number")
        test_name = opc.read("test_name")
        hold_period = opc.read("hold_period")
        test_pressure = opc.read("test_pressure")
    except KeyError as exc:
        raise HTTPException(status_code=500, detail=f"Missing OPC node: {exc}") from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"OPC read failed: {exc}") from exc

    return {
        "section_number": _to_text(section_number),
        "test_name": _to_text(test_name),
        "hold_period": _to_text(hold_period),
        "test_pressure": _to_text(test_pressure),
    }