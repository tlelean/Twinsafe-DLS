from pathlib import Path
from typing import Dict

# ==========================================
# Centralized Paths
# ==========================================

# Directory where generated PDFs are stored/mirrored
PDF_DIR = Path("/home/mechatronics/Twinsafe-DLS/visualisation/static/pdf")

# Path to the historical data CSV file
HISTORICAL_CSV = Path("/home/mechatronics/Twinsafe-DLS/visualisation/static/historical.csv")

# Frontend files directory
FRONTEND_DIR = Path("/home/mechatronics/Twinsafe-DLS/visualisation/frontend")

# PLC Test Details directory
TEST_DETAILS_DIR = Path("/var/opt/codesys/PlcLogic/Test Details")


# ==========================================
# PLC / OPC UA Configuration
# ==========================================

PLC_ENDPOINT = "opc.tcp://localhost:4840"

NODE_IDS: Dict[str, str] = {
    "channel_readings": "ns=4;s=|var|CODESYS Control for Linux ARM64 SL.DLS.GVL.alrChannelReading",
    "channel_visibility": "ns=4;s=|var|CODESYS Control for Linux ARM64 SL.DLS.GVL.axVisibilty",
    "close_pdf": "ns=4;s=|var|CODESYS Control for Linux ARM64 SL.DLS.GVL.xClosePdf",
    "filename_details_production": "ns=4;s=|var|CODESYS Control for Linux ARM64 SL.DLS.GVL.sFileNameDetailsProduction",
    "ots_number": "ns=4;s=|var|CODESYS Control for Linux ARM64 SL.DLS.GVL.asTestDetails[2,1]",
    "section_number": "ns=4;s=|var|CODESYS Control for Linux ARM64 SL.DLS.GVL.sSectionNumber",
    "test_name": "ns=4;s=|var|CODESYS Control for Linux ARM64 SL.DLS.GVL.sTestName",
    "hold_period": "ns=4;s=|var|CODESYS Control for Linux ARM64 SL.DLS.GVL.iHoldPeriod",
    "test_pressure": "ns=4;s=|var|CODESYS Control for Linux ARM64 SL.DLS.GVL.iTestPressure",
}

UNIQUE_NUMBER_NODE_IDS: Dict[int, str] = {
    1: "ns=4;s=|var|CODESYS Control for Linux ARM64 SL.DLS.GVL.asUniqueNumbers[2,1]",
    2: "ns=4;s=|var|CODESYS Control for Linux ARM64 SL.DLS.GVL.asUniqueNumbers[2,2]",
    3: "ns=4;s=|var|CODESYS Control for Linux ARM64 SL.DLS.GVL.asUniqueNumbers[2,3]",
    4: "ns=4;s=|var|CODESYS Control for Linux ARM64 SL.DLS.GVL.asUniqueNumbers[2,4]",
    5: "ns=4;s=|var|CODESYS Control for Linux ARM64 SL.DLS.GVL.asUniqueNumbers[2,5]",
    6: "ns=4;s=|var|CODESYS Control for Linux ARM64 SL.DLS.GVL.asUniqueNumbers[2,6]",
    7: "ns=4;s=|var|CODESYS Control for Linux ARM64 SL.DLS.GVL.asUniqueNumbers[2,7]",
    8: "ns=4;s=|var|CODESYS Control for Linux ARM64 SL.DLS.GVL.asUniqueNumbers[2,8]",
}

CHANNEL_NAMES = {
    1: "Channel 1",
    2: "Channel 2",
    3: "Channel 3",
    4: "Channel 4",
    5: "Channel 5",
    6: "Channel 6",
    7: "Channel 7",
    8: "Channel 8",
    9: "Ambient Temperature",
}

STATUS_NODE_IDS: Dict[int, str] = {
    1: "ns=4;s=|var|CODESYS Control for Linux ARM64 SL.DLS.Program_Selector.Production.Hold[1].xPass",
    2: "ns=4;s=|var|CODESYS Control for Linux ARM64 SL.DLS.Program_Selector.Production.Hold[2].xPass",
    3: "ns=4;s=|var|CODESYS Control for Linux ARM64 SL.DLS.Program_Selector.Production.Hold[3].xPass",
    4: "ns=4;s=|var|CODESYS Control for Linux ARM64 SL.DLS.Program_Selector.Production.Hold[4].xPass",
}


# ==========================================
# System Commands
# ==========================================

RSYNC_COMMAND = [
    "rsync",
    "-av",
    "--include=*.bin",
    "--exclude=*/",
    "--exclude=*",
    "DAQ_Station@rndfs01.valves.co.uk:/media/nss/DOCS/Userdoc/R & D/DAQ_Station/Test Details/",
    str(TEST_DETAILS_DIR) + "/",
]
