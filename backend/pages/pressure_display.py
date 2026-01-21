from fastapi import APIRouter
from pydantic import BaseModel

from ..opc import opc

router = APIRouter()


class ChannelSettingsPayload(BaseModel):
    visibility: list[bool]
    max_range: list[float]
    transducer_codes: list[str]
    gauge_codes: list[str]


EXPECTED_VIS_COUNT = 27
EXPECTED_RANGE_COUNT = 23
EXPECTED_CODES_COUNT = 27


def pad_list(values, target_len, fill_value):
    """Utility to pad lists to a fixed length."""
    if len(values) < target_len:
        return values + [fill_value] * (target_len - len(values))
    return values[:target_len]  # defensive trimming


# -------------------------
# POST
# -------------------------

@router.post("/api/channel_settings", response_model=ChannelSettingsPayload)
def set_channel_settings(payload: ChannelSettingsPayload):

    visibility = pad_list(payload.visibility, EXPECTED_VIS_COUNT, False)
    max_range = pad_list(payload.max_range, EXPECTED_RANGE_COUNT, 0.0)
    transducer_codes = pad_list(payload.transducer_codes, EXPECTED_CODES_COUNT, "")
    gauge_codes = pad_list(payload.gauge_codes, EXPECTED_CODES_COUNT, "")

    opc.write("channel_visibility", visibility)
    opc.write("max_range", max_range)
    opc.write("transducer_codes", transducer_codes)
    opc.write("gauge_codes", gauge_codes)

    return ChannelSettingsPayload(
        visibility=visibility,
        max_range=max_range,
        transducer_codes=transducer_codes,
        gauge_codes=gauge_codes,
    )


# -------------------------
# GET
# -------------------------

@router.get("/api/channel_settings", response_model=ChannelSettingsPayload)
def get_channel_settings():

    # Your OPC wrapper already returns the plain list for these vars
    visibility = pad_list(opc.read("channel_visibility"), EXPECTED_VIS_COUNT, False)
    max_range = pad_list(opc.read("max_range"), EXPECTED_RANGE_COUNT, 0.0)
    transducer_codes = pad_list(opc.read("transducer_codes"), EXPECTED_CODES_COUNT, "")
    gauge_codes = pad_list(opc.read("gauge_codes"), EXPECTED_CODES_COUNT, "")

    return ChannelSettingsPayload(
        visibility=visibility,
        max_range=max_range,
        transducer_codes=transducer_codes,
        gauge_codes=gauge_codes,
    )