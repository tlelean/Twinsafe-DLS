import sys
from pathlib import Path

# Add project root to sys.path to ensure we can import the shared config
root = Path(__file__).resolve().parent.parent.parent
if str(root) not in sys.path:
    sys.path.append(str(root))

# Import all constants from the shared config to maintain backward compatibility
from shared_config import (
    PDF_DIR,
    HISTORICAL_CSV,
    FRONTEND_DIR,
    TEST_DETAILS_DIR,
    PLC_ENDPOINT,
    NODE_IDS,
    UNIQUE_NUMBER_NODE_IDS,
    CHANNEL_NAMES,
    STATUS_NODE_IDS,
    RSYNC_COMMAND
)
