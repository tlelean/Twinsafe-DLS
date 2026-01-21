from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Response, HTTPException
from pydantic import BaseModel

from ..config import HISTORICAL_CSV, CHANNEL_NAMES, UNIQUE_NUMBER_NODE_IDS
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
    if opc is None:
        raise HTTPException(status_code=503, detail="OPC UA server not available")
    
    now = datetime.now(tz=timezone.utc)

    # 9 analogue channels
    channel_values = opc.read("channel_readings")[:9]

    channel_visibility = opc.read("channel_visibility")[:9]
    
    # Read unique numbers for channel names
    channel_unique_numbers = []
    for i in range(1, 10):
        if i in UNIQUE_NUMBER_NODE_IDS:
            try:
                unique_num = opc.read_direct(UNIQUE_NUMBER_NODE_IDS[i])
                channel_unique_numbers.append(str(unique_num) if unique_num is not None else CHANNEL_NAMES.get(i, f"Channel {i}"))
            except:
                channel_unique_numbers.append(CHANNEL_NAMES.get(i, f"Channel {i}"))
        else:
            channel_unique_numbers.append(CHANNEL_NAMES.get(i, f"Channel {i}"))

    channels: List[ChannelReading] = []
    for i in range(9):
        channel_name = channel_unique_numbers[i] if i < len(channel_unique_numbers) else CHANNEL_NAMES.get(i + 1, f"Channel {i + 1}")
        channels.append(
            ChannelReading(
                name=channel_name,
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