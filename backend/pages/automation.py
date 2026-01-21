from fastapi import APIRouter

from ..opc import opc

router = APIRouter()

@router.post("/api/programs/load/{index}")
def load_program(index: int):
    opc.write("loaded_program", index)
    return {"status": "ok", "loaded_program": index}