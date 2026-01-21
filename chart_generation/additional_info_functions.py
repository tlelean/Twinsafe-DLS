"""Production data analysis utilities."""

import pandas as pd


def locate_key_time_rows(cleaned_data, hold_info: pd.Series, channel_unique_number: str, production=False):
    """Return indices of key time points closest to provided timestamps.
       Always includes all rows, leaving blanks for missing timestamps.
    """
    date_time_index = cleaned_data.set_index('Datetime')

    def parse_time(value):
        if pd.isna(value) or str(value).strip() == "":
            return None
        return pd.to_datetime(
            value,
            format="%Y-%m-%dT%H:%M:%S.%f",
            errors="coerce",
        )

    # Parse timestamps
    sos_time = parse_time(hold_info.get('start_of_stabilisation'))
    soh_time = parse_time(hold_info.get('start_of_hold'))
    eoh_time = parse_time(hold_info.get('end_of_hold'))

    # Use the new column naming format (just the unique_number)
    pressure_col = str(channel_unique_number)
    pressure_col_display = f"{pressure_col} (psi)"

    # Prep index table (always show all, blank if missing)
    index_data = {
        'SOS_Index': [None],
        'SOH_Index': [None],
        'EOH_Index': [None]
    }

    # Default blank table rows
    labels = ['Start of Stabilisation', 'Start of Hold', 'End of Hold']
    times   = [sos_time, soh_time, eoh_time]

    display_table_data = {
        '': labels,
        'Datetime': ['' for _ in labels],
        pressure_col_display: ['' for _ in labels],
        'Ambient Temperature (°C)': ['' for _ in labels]
    }

    # Populate only where valid
    for i, (label, ts) in enumerate(zip(labels, times)):
        if ts is None or pd.isna(ts):
            continue

        # Find nearest index
        nearest_idx = date_time_index.index.get_indexer([ts], method="nearest")[0]

        # Fill index table
        if label == 'Start of Stabilisation':
            index_data['SOS_Index'][0] = nearest_idx
        elif label == 'Start of Hold':
            index_data['SOH_Index'][0] = nearest_idx
        elif label == 'End of Hold':
            index_data['EOH_Index'][0] = nearest_idx

        # Fill display table
        pressure_val = cleaned_data.loc[nearest_idx, pressure_col]

        temp_val = cleaned_data.loc[nearest_idx, 'Ambient Temperature']

        display_table_data['Datetime'][i] = ts.strftime("%d/%m/%Y %H:%M:%S")
        display_table_data[pressure_col_display][i] = int(pressure_val)
        display_table_data['Ambient Temperature (°C)'][i] = temp_val

    holds_indices = pd.DataFrame(index_data)
    display_table = pd.DataFrame(display_table_data)

    return holds_indices, display_table
