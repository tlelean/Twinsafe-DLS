from pathlib import Path
from typing import Dict

PLC_ENDPOINT = "opc.tcp://localhost:4840"

FRONTEND_DIR = Path("/var/opt/codesys/PlcLogic/html_visu/frontend")

PDF_DIR = Path("/var/opt/codesys/PlcLogic/trend_data/static/pdfs")
HISTORICAL_CSV = Path("/var/opt/codesys/PlcLogic/trend_data/historical.csv")
LIVE_JSON = Path("/var/opt/codesys/PlcLogic/trend_data/live.json")

TEST_DETAILS_DIR = Path("/var/opt/codesys/PlcLogic/Test Details")

RSYNC_COMMAND = [
    "rsync",
    "-av",
    "--include=*.bin",
    "--exclude=*/",
    "--exclude=*",
    "DAQ_Station@rndfs01.valves.co.uk:/media/nss/DOCS/Userdoc/R & D/DAQ_Station/Test Details/",
    "/var/opt/codesys/PlcLogic/Test Details/",
]

NODE_IDS: Dict[str, str] = {
    "channel_names": "ns=4;s=|var|CODESYS Control for Linux ARM64 SL.DLS.GVL.asChannelNames",
    "channel_readings": "ns=4;s=|var|CODESYS Control for Linux ARM64 SL.DLS.GVL.arChannelReading",
    "channel_visibility": "ns=4;s=|var|CODESYS Control for Linux ARM64 SL.DLS.GVL.axVisibilty",
    "valve_close": "ns=4;s=|var|CODESYS Control for Linux ARM64 SL.DLS.GVL.xValveClose",
    "valve_open": "ns=4;s=|var|CODESYS Control for Linux ARM64 SL.DLS.GVL.xValveOpen",
    "cycle_count": "ns=4;s=|var|CODESYS Control for Linux ARM64 SL.DLS.GVL.iCycleCount",
    "close_pdf": "ns=4;s=|var|CODESYS Control for Linux ARM64 SL.DLS.GVL.xClosePdf",
    "filename_details_production": "ns=4;s=|var|CODESYS Control for Linux ARM64 SL.DLS.GVL.sFileNameDetailsProduction",
    "ots_number": "ns=4;s=|var|CODESYS Control for Linux ARM64 SL.DLS.GVL.asTestDetailsProduction[2,1]",
}

UNIQUE_NUMBER_NODE_IDS: Dict[int, str] = {
    1: "ns=4;s=|var|CODESYS Control for Linux ARM64 SL.DLS.GVL.asUniqueNumbers[2,1]",
    2: "ns=4;s=|var|CODESYS Control for Linux ARM64 SL.DLS.GVL.asUniqueNumbers[2,2]",
    3: "ns=4;s=|var|CODESYS Control for Linux ARM64 SL.DLS.GVL.asUniqueNumbers[2,3]",
    4: "ns=4;s=|var|CODESYS Control for Linux ARM64 SL.DLS.GVL.asUniqueNumbers[2,4]",
}

STATUS_NODE_IDS: Dict[int, str] = {
    1: "ns=4;s=|var|CODESYS Control for Linux ARM64 SL.DLS.ProgramSelecter.Production.Hold[1].xPass",
    2: "ns=4;s=|var|CODESYS Control for Linux ARM64 SL.DLS.ProgramSelecter.Production.Hold[2].xPass",
    3: "ns=4;s=|var|CODESYS Control for Linux ARM64 SL.DLS.ProgramSelecter.Production.Hold[3].xPass",
    4: "ns=4;s=|var|CODESYS Control for Linux ARM64 SL.DLS.ProgramSelecter.Production.Hold[4].xPass",
}