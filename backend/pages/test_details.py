from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

from ..opc import opc

router = APIRouter()


class TestDetailsPayload(BaseModel):
    test_procedure_reference: Optional[str] = None
    unique_number: Optional[str] = None
    rd_reference: Optional[str] = None
    valve_description: Optional[str] = None
    job_number: Optional[str] = None
    valve_drawing_number: Optional[str] = None
    attempt: Optional[str] = None


@router.post("/api/test_details", response_model=TestDetailsPayload)
def save_test_details(details: TestDetailsPayload):
    data = details.model_dump()

    for field_name, value in data.items():
        if value is not None:
            opc.write(field_name, value)

    return details


@router.get("/api/test_details", response_model=TestDetailsPayload)
def get_test_details():
    data = {}
    for field_name in TestDetailsPayload.model_fields.keys():
        raw = opc.read(field_name)
        data[field_name] = None if raw is None else str(raw)

    return TestDetailsPayload(**data)