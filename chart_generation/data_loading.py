"""Helpers for loading CSV test data."""

from pathlib import Path
import pandas as pd
import json


def load_csv_file(file_path: str, **kwargs) -> pd.DataFrame:
    """Wrapper around :func:`pandas.read_csv` with friendly errors."""
    try:
        return pd.read_csv(file_path, **kwargs, dayfirst=True)
    except FileNotFoundError as exc:
        raise FileNotFoundError(f"File not found: {file_path}") from exc
    except pd.errors.EmptyDataError as exc:
        raise ValueError(f"File is empty: {file_path}") from exc
    except Exception as exc:  # pragma: no cover - unexpected read error
        raise Exception(f"Error reading file {file_path}: {exc}") from exc
    
def load_test_information(test_details_path: str):
    """Load all test information from the details JSON file."""

    root = json.load(open(test_details_path))
    test_metadata = root["metadata"]
    channel_info = pd.DataFrame(root["channel_info"])

    # Filter to only visible channels with unique_number
    channel_info = channel_info[channel_info["visible"] == True].reset_index(drop=True)

    return test_metadata, channel_info

def prepare_primary_data(primary_data_path: str, channel_info: pd.DataFrame):
    """Load the primary data CSV and return cleaned data with mapped columns."""

    # Load raw data from CSV
    raw_data = load_csv_file(primary_data_path, header=0)

    # Extract unique numbers from channel_info for visible channels
    unique_numbers = channel_info["unique_number"].tolist()
    
    # Build column mapping: numeric column -> unique_number
    # Columns in CSV: Datetime, 1-8 (numeric), Ambient Temperature
    column_map = {}
    for idx, uid in enumerate(unique_numbers, start=1):
        if uid:  # Only if unique_number is not empty
            column_map[str(idx)] = uid
    column_map["Ambient Temperature"] = "Ambient Temperature"
    
    # Rename columns to meaningful names
    raw_data = raw_data.rename(columns=column_map)
    
    # Ensure Datetime column is properly formatted
    raw_data["Datetime"] = pd.to_datetime(
        raw_data["Datetime"],
        format="%Y-%m-%dT%H:%M:%S.%f",
        errors="coerce",
    )
    
    # Keep only Datetime, active channel data, and Ambient Temperature
    active_channels = [uid for uid in unique_numbers if uid]
    required_columns = ["Datetime"] + active_channels + ["Ambient Temperature"]
    data_subset = raw_data[required_columns].copy()
    
    # Drop duplicate timestamps
    dedupe_mask = ~data_subset["Datetime"].duplicated(keep="first")
    if not dedupe_mask.all():
        data_subset = data_subset.loc[dedupe_mask].copy()
        raw_data = raw_data.loc[dedupe_mask].copy()
    
    return data_subset, active_channels