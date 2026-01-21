"""Production chart report generator."""

from pathlib import Path
from typing import List
import pandas as pd

from graph_plotter import plot_production_channel_data, plot_crosses
from pdf_helpers import draw_table, draw_production_test_details, insert_plot_and_logo
from additional_info_functions import locate_key_time_rows


class BaseReportGenerator:
    def __init__(self, **kwargs):
        self.program_name = kwargs.get("program_name")
        self.pdf_output_path = kwargs.get("pdf_output_path")
        self.test_metadata = kwargs.get("test_metadata")
        self.active_channels = kwargs.get("active_channels")
        self.cleaned_data = kwargs.get("cleaned_data")
        self.channel_info = kwargs.get("channel_info")

        if isinstance(self.test_metadata, pd.DataFrame):
            self.test_metadata = self.test_metadata.iloc[:, 0].to_dict()
        elif isinstance(self.test_metadata, pd.Series):
            self.test_metadata = self.test_metadata.to_dict()

    def build_output_path(self, test_metadata) -> Path:
        """Construct the output PDF path from metadata."""
        return self.pdf_output_path / (
            f"{test_metadata.get('Unique Number', 'unknown')}_"
            f"{test_metadata.get('Test Name', 'test')}_"
            f"{test_metadata.get('Date Time', 'now')}.tmp.pdf"
        )
    
    def finalize_output_path(self, temp_path: Path) -> Path:
        """Rename the temporary PDF path to its final name and return it."""
        name = temp_path.name

        if not name.endswith(".tmp.pdf"):
            return temp_path

        final_path = Path(temp_path.parent, name[:-8] + ".pdf")

        if final_path.exists():
            final_path.unlink()

        if not temp_path.exists():
            return final_path

        temp_path.replace(final_path)
        return final_path

    def generate(self) -> List[Path]:
        """Generate the report."""
        raise NotImplementedError


class ProductionReportGenerator(BaseReportGenerator):
    """Generate per-channel production reports."""
    
    def generate(self) -> List[Path]:
        generated_paths: List[Path] = []

        for idx, channel_row in self.channel_info.iterrows():
            if channel_row.get("visible", False):
                path = self.generate_single_report(channel_row)
                generated_paths.append(path)

        return generated_paths

    def generate_single_report(self, channel_info: pd.Series):
        is_table = True

        unique_number = channel_info["unique_number"]
        channel_col = str(unique_number)

        # Build cleaned_data with the specific channel
        cleaned_data = self.cleaned_data[[
            "Datetime", 
            channel_col, 
            "Ambient Temperature"
        ]].copy()

        # Copy metadata so you don't mutate shared dict
        metadata = dict(self.test_metadata)
        metadata["Unique Number"] = unique_number

        unique_path = self.pdf_output_path / f"{unique_number}_{metadata.get('Test Name', 'test')}_{metadata.get('Date Time', 'now').replace('T', '_').replace(':', '-')}.tmp.pdf"

        # Ensure output directory exists
        unique_path.parent.mkdir(parents=True, exist_ok=True)

        # Get key point indices and display table
        key_point_indicies, display_table = locate_key_time_rows(
            cleaned_data, 
            channel_info, 
            unique_number,
            production=True
        )

        # Plot the production channel data
        figure, ax = plot_production_channel_data(cleaned_data)

        # Add key point markers
        plot_crosses(
            df=key_point_indicies,
            channel=channel_col,
            data=cleaned_data,
            ax=ax,
        )

        transducer_code = channel_info.get("transducer", "")
        breakout_torque = channel_info.get("breakout_torque", 0)
        running_torque = channel_info.get("running_torque", 0)
        
        # Calculate allowable drop (typically 10% of test pressure)
        test_pressure = float(self.test_metadata.get('Test Pressure', '0') or 0)
        allowable_drop = int(test_pressure * 0.1) if test_pressure else 0

        # Create PDF with test details
        pdf = draw_production_test_details(
            metadata,
            channel_info,
            unique_path,
            cleaned_data,
            transducer_code,
            allowable_drop,
            breakout_torque,
            running_torque
        )

        # Format display table for PDF
        display_table.loc[-1] = display_table.columns
        display_table.index = display_table.index + 1
        display_table = display_table.sort_index()
        display_table.columns = range(display_table.shape[1])

        # Add table and plot to PDF
        draw_table(pdf_canvas=pdf, dataframe=display_table)
        insert_plot_and_logo(figure, pdf, is_table, True)
        
        return self.finalize_output_path(unique_path)
