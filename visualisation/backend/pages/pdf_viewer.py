from fastapi import APIRouter
from pydantic import BaseModel
from typing import List
from fastapi.responses import FileResponse
from fastapi import HTTPException

from ..opc import opc
from ..config import STATUS_NODE_IDS, UNIQUE_NUMBER_NODE_IDS, PDF_DIR

router = APIRouter()


class PdfListResponse(BaseModel):
    files: List[str]

class TestStatusPayload(BaseModel):
    status: bool


@router.get("/api/pdf-list", response_model=PdfListResponse)
def pdf_list():
    pdf_paths = [
        p for p in PDF_DIR.iterdir()
        if p.is_file() and p.suffix.lower() == ".pdf"
    ]

    # Sort newest first by last modified time
    pdf_paths.sort(key=lambda p: p.stat().st_mtime, reverse=True)

    return PdfListResponse(files=[p.name for p in pdf_paths])

@router.get("/api/pdf/{filename}")
def get_pdf(filename: str):
    # Stop path traversal (e.g. ../../etc/passwd)
    file_path = (PDF_DIR / filename).resolve()
    pdf_dir = PDF_DIR.resolve()

    if pdf_dir not in file_path.parents and file_path != pdf_dir:
        raise HTTPException(status_code=400, detail="Invalid filename")

    if not file_path.is_file() or file_path.suffix.lower() != ".pdf":
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(path=str(file_path), media_type="application/pdf", filename=file_path.name)

def find_slot_for_unique(unique: str) -> int:
    unique = str(unique).strip()

    for slot, nodeid in UNIQUE_NUMBER_NODE_IDS.items():
        val = opc.read_direct(nodeid)
        if str(val).strip() == unique:
            return slot

    raise ValueError(f"Unique number {unique} not found in slots")

def write_passfail(unique: str, is_pass: bool):
    slot = find_slot_for_unique(unique)
    nodeid = STATUS_NODE_IDS[slot]  # this is Hold[slot].xPass
    opc.write_direct(nodeid, bool(is_pass))

def read_passfail(unique: str) -> bool:
    slot = find_slot_for_unique(unique)
    nodeid = STATUS_NODE_IDS[slot]  # Hold[slot].xPass (bool)
    val = opc.read_direct(nodeid)
    return bool(val)

@router.post("/api/pdf/status/{unique}")
def pdf_status(unique: str, payload: TestStatusPayload):
    try:
        write_passfail(unique, payload.status)  # status is bool
        return {"message": "Status updated"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/api/pdf-close/")
def pdf_close():
    try:
        opc.write("close_pdf", True)
        return {"ok": True}
    except Exception as e:
        # This will show up in your JS error handling as `detail`
        raise HTTPException(status_code=500, detail=f"pdf_close failed: {e}")
    
@router.get("/api/pdf/status/{unique}")
def pdf_status(unique: str):
    try:
        is_pass = read_passfail(unique)
        return {"status": is_pass}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))