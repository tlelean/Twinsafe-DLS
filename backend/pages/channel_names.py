from typing import List, Optional

from fastapi import APIRouter
from pydantic import BaseModel, Field

from ..opc import opc

router = APIRouter()


class ChannelNamesPayload(BaseModel):
    names: Optional[List[Optional[str]]] = Field(default_factory=list)

@router.get("/api/channel_names", response_model=ChannelNamesPayload)
def get_channel_names():
    raw = opc.read("channel_names")
    return ChannelNamesPayload(names=raw[1])


@router.post("/api/channel_names", response_model=ChannelNamesPayload)
def save_channel_names(payload: ChannelNamesPayload):
    raw = opc.read("channel_names")

    new_names = [raw[0], payload.names]

    opc.write("channel_names", new_names)
    return payload