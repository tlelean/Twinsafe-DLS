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
    "active_program": "ns=4;s=|var|CODESYS Control for Linux ARM64 SL.DLS.GVL.iActiveProgram",
    "loaded_program": "ns=4;s=|var|CODESYS Control for Linux ARM64 SL.DLS.GVL.iLoadedProgram",
    "test_procedure_reference": "ns=4;s=|var|CODESYS Control for Linux ARM64 SL.DLS.GVL.asTestDetails[2,1]",
    "unique_number": "ns=4;s=|var|CODESYS Control for Linux ARM64 SL.DLS.GVL.asTestDetails[2,2]",
    "rd_reference": "ns=4;s=|var|CODESYS Control for Linux ARM64 SL.DLS.GVL.asTestDetails[2,3]",
    "valve_description": "ns=4;s=|var|CODESYS Control for Linux ARM64 SL.DLS.GVL.asTestDetails[2,4]",
    "job_number": "ns=4;s=|var|CODESYS Control for Linux ARM64 SL.DLS.GVL.asTestDetails[2,5]",
    "valve_drawing_number": "ns=4;s=|var|CODESYS Control for Linux ARM64 SL.DLS.GVL.asTestDetails[2,6]",
    "attempt": "ns=4;s=|var|CODESYS Control for Linux ARM64 SL.DLS.GVL.asTestDetails[2,7]",
    "channel_names": "ns=4;s=|var|CODESYS Control for Linux ARM64 SL.DLS.GVL.asChannelNames",
    "channel_readings": "ns=4;s=|var|CODESYS Control for Linux ARM64 SL.DLS.GVL.arChannelReading",
    "channel_visibility": "ns=4;s=|var|CODESYS Control for Linux ARM64 SL.DLS.GVL.axVisibilty",
    "valve_close": "ns=4;s=|var|CODESYS Control for Linux ARM64 SL.DLS.GVL.xValveClose",
    "valve_open": "ns=4;s=|var|CODESYS Control for Linux ARM64 SL.DLS.GVL.xValveOpen",
    "cycle_count": "ns=4;s=|var|CODESYS Control for Linux ARM64 SL.DLS.GVL.iCycleCount",
    "max_range": "ns=4;s=|var|CODESYS Control for Linux ARM64 SL.DLS.GVL.arMaxRange",
    "transducer_codes": "ns=4;s=|var|CODESYS Control for Linux ARM64 SL.DLS.GVL.asTransducerCode",
    "gauge_codes": "ns=4;s=|var|CODESYS Control for Linux ARM64 SL.DLS.GVL.asGaugeCode",
    "sew_calibration_done": "ns=4;s=|var|CODESYS Control for Linux ARM64 SL.DLS.NVL_Receiver_from_Temp_Cab.xCalibrationDone",
    "sew_error": "ns=4;s=|var|CODESYS Control for Linux ARM64 SL.DLS.NVL_Receiver_from_Temp_Cab.xError",
    "sew_rotor_lock": "ns=4;s=|var|CODESYS Control for Linux ARM64 SL.DLS.GVL.stSendData.xLockRotor",
    "sew_calibrate": "ns=4;s=|var|CODESYS Control for Linux ARM64 SL.DLS.GVL.stSendData.xCalibrate",
    "sew_speed": "ns=4;s=|var|CODESYS Control for Linux ARM64 SL.DLS.GVL.stSendData.iSetPointSpeed",
    "sew_acceleration": "ns=4;s=|var|CODESYS Control for Linux ARM64 SL.DLS.GVL.stSendData.iAcceleration",
    "sew_deceleration": "ns=4;s=|var|CODESYS Control for Linux ARM64 SL.DLS.GVL.stSendData.iDeceleration",
    "sew_release_torque": "ns=4;s=|var|CODESYS Control for Linux ARM64 SL.DLS.GVL.stSendData.iReleaseTorque",
    "sew_alarm_mask": "ns=4;s=|var|CODESYS Control for Linux ARM64 SL.DLS.GVL.stSendData.iStartPosMask",
    "sew_initial_cycle_speed": "ns=4;s=|var|CODESYS Control for Linux ARM64 SL.DLS.GVL.stSendData.iTorqueSpeed",
    "sew_torque_limit_timer": "ns=4;s=|var|CODESYS Control for Linux ARM64 SL.DLS.GVL.stSendData.iTorqueLimitTimer",
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