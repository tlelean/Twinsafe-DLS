from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Response
from pydantic import BaseModel

from ..config import HISTORICAL_CSV
from ..opc import opc

router = APIRouter()


# ---------- Pydantic models ----------

class ChannelReading(BaseModel):
    name: str
    value: Optional[float]  # or float | None if you're on Python 3.10+
    visible: bool


class LiveResponse(BaseModel):
    timestamp: datetime
    channels: List[ChannelReading]


# ---------- Live endpoint ----------

@router.get("/api/live", response_model=LiveResponse)
def get_live_json():
    now = datetime.now(tz=timezone.utc)

    # channel_names comes back as (status, names)
    channel_names = opc.read("channel_names")[1][:26]

    # 23 analogue channels + 3 extras
    channel_values = opc.read("channel_readings")[:23]
    valve_close = opc.read("valve_close")
    valve_open = opc.read("valve_open")
    cycle_count = opc.read("cycle_count")

    channel_values.append(valve_close)
    channel_values.append(valve_open)
    channel_values.append(cycle_count)

    channel_visibility = opc.read("channel_visibility")[:26]

    channels: List[ChannelReading] = []
    for i in range(26):
        channels.append(
            ChannelReading(
                name=channel_names[i],
                value=channel_values[i],
                visible=channel_visibility[i],
            )
        )

    return LiveResponse(
        timestamp=now,
        channels=channels,
    )


# ---------- Historical CSV endpoint ----------

@router.get("/api/historical.csv")
def get_historical_csv():
    with open(HISTORICAL_CSV, "rb") as f:
        data = f.read()

    return Response(
        content=data,
        media_type="text/csv",
        headers={"Cache-Control": "no-store"},
    )