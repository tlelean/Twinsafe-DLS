"""Production PDF generation utilities."""

import io
import os
from typing import Optional

import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.colors import Color
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle

mpl.rcParams['agg.path.chunksize'] = 10000


class Layout:
    """PDF layout constants for production reports."""
    PAGE_WIDTH, PAGE_HEIGHT = landscape(A4)

    MARGIN_LEFT = 15
    MARGIN_RIGHT = 15
    MARGIN_TOP = 15
    MARGIN_BOTTOM = 15

    CONTENT_X_START = MARGIN_LEFT
    CONTENT_Y_START = MARGIN_BOTTOM
    CONTENT_WIDTH = PAGE_WIDTH - MARGIN_LEFT - MARGIN_RIGHT
    CONTENT_HEIGHT = PAGE_HEIGHT - MARGIN_TOP - MARGIN_BOTTOM

    HEADER_X = CONTENT_X_START
    HEADER_Y = 515
    HEADER_W = 600
    HEADER_H = 65

    TABLE_X = CONTENT_X_START
    TABLE_Y = CONTENT_Y_START
    TABLE_W = HEADER_W
    TABLE_H = 51.5

    GRAPH_X = CONTENT_X_START
    GRAPH_Y_TABLE = CONTENT_Y_START + TABLE_H
    GRAPH_H_TABLE = 470 - TABLE_H
    GRAPH_W = HEADER_W

    RIGHT_COL_X = 630
    RIGHT_COL_W = 197

    LOGO_X = RIGHT_COL_X
    LOGO_Y = 515
    LOGO_W = 197
    LOGO_H = 65

    INFO_RIGHT_X = RIGHT_COL_X
    INFO_RIGHT_Y = 300
    INFO_RIGHT_W = RIGHT_COL_W
    INFO_RIGHT_H = 185

    STAMP_X = RIGHT_COL_X
    STAMP_Y = 35
    STAMP_W = RIGHT_COL_W
    STAMP_H = 180

    FOOTER_TEXT_Y = 10

    HEADER_COL1_LABEL_X = 20
    HEADER_COL1_VALUE_X = 140
    HEADER_COL2_LABEL_X = 402.5
    HEADER_COL2_VALUE_X = 487.5

    HEADER_ROW1_Y = 571.875
    HEADER_ROW2_Y = 555.625
    HEADER_ROW3_Y = 539.375
    HEADER_ROW4_Y = 523.125

    RIGHT_COL_LABEL_X = 635
    RIGHT_COL_VALUE_X = 725

    DATA_LOGGER_Y = 457.5
    SERIAL_NO_Y = 442.5
    TRANSDUCERS_Y = 427.5

    OPERATIVE_Y = 22.5
    OPERATIVE_VALUE_X = 685

    TRANSDUCER_ROW_HEIGHT = 15


def format_torque(value):
    """Format torque value with units."""
    if value is None:
        return "N/A"
    if isinstance(value, str):
        stripped = value.strip()
        if stripped in {"See Table", "N/A"} or stripped.endswith("ft.lbs"):
            return stripped
    try:
        if float(value) == 0:
            return "N/A"
    except (TypeError, ValueError):
        return f"{value} ft.lbs"
    return f"{value} ft.lbs"


def insert_plot_and_logo(figure, pdf, is_table, production=False):
    """Insert matplotlib figure and logo into PDF canvas."""
    png_figure = io.BytesIO()
    figure.savefig(png_figure, format='PNG', bbox_inches='tight', dpi=500)
    png_figure.seek(0)
    plt.close(figure)
    fig_img = ImageReader(png_figure)

    pdf.drawImage(
        fig_img,
        Layout.GRAPH_X + 1,
        Layout.GRAPH_Y_TABLE + 1,
        Layout.GRAPH_W - 2,
        Layout.GRAPH_H_TABLE - 2,
        preserveAspectRatio=False,
        mask="auto",
    )

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    image_path = os.path.join(BASE_DIR, "Twinsafe.png")

    try:
        pdf.drawImage(
            image_path,
            Layout.LOGO_X,
            Layout.LOGO_Y,
            Layout.LOGO_W,
            Layout.LOGO_H,
            preserveAspectRatio=True,
            mask="auto",
        )
    except Exception as e:
        print(f"Warning: Could not load logo image at {image_path}. Error: {e}")

    pdf.save()
    plt.close('all')


def draw_text_on_pdf(
    pdf_canvas,
    text,
    x,
    y,
    font="Helvetica",
    colour="black",
    size=10,
    left_aligned=False,
    replace_empty=False,
):
    """Draw text on PDF canvas."""
    text = "" if text is None else str(text)
    if replace_empty:
        text = "N/A" if not text.strip() else text

    pdf_canvas.setFont(font, size)
    text_width = pdf_canvas.stringWidth(text, font, size)
    text_height = size * 0.7

    draw_x = x if left_aligned else x - (text_width / 2)
    draw_y = y - (text_height / 2)

    pdf_canvas.setFillColor(colour if colour else colors.black)
    pdf_canvas.drawString(draw_x, draw_y, text)
    pdf_canvas.setFillColor(colors.black)


def draw_bounding_box(pdf_canvas, x, y, width, height):
    """Draw a bounding box on the PDF."""
    pdf_canvas.setLineWidth(0.5)
    pdf_canvas.rect(x, y, width, height)


def draw_production_layout_boxes(pdf):
    """Draw layout boxes for production reports."""
    boxes = [
        (Layout.HEADER_X, Layout.HEADER_Y, Layout.HEADER_W, Layout.HEADER_H),
        (Layout.GRAPH_X, Layout.GRAPH_Y_TABLE, Layout.GRAPH_W, Layout.GRAPH_H_TABLE),
        (Layout.TABLE_X, Layout.TABLE_Y, Layout.TABLE_W, Layout.TABLE_H),
        (Layout.STAMP_X, Layout.STAMP_Y, Layout.STAMP_W, Layout.STAMP_H),
        (Layout.INFO_RIGHT_X, Layout.INFO_RIGHT_Y + Layout.TRANSDUCER_ROW_HEIGHT * 8, Layout.INFO_RIGHT_W, Layout.INFO_RIGHT_H - Layout.TRANSDUCER_ROW_HEIGHT * 8),
        (Layout.INFO_RIGHT_X, Layout.INFO_RIGHT_Y + Layout.TRANSDUCER_ROW_HEIGHT * 2, Layout.INFO_RIGHT_W, Layout.INFO_RIGHT_H - Layout.TRANSDUCER_ROW_HEIGHT * 7 - 5),
    ]
    for box in boxes:
        draw_bounding_box(pdf, *box)


def draw_headers(pdf, test_metadata, light_blue):
    """Draw section headers on production report."""
    draw_text_on_pdf(
        pdf,
        test_metadata.get('Test Name', ''),
        Layout.HEADER_COL1_VALUE_X,
        Layout.HEADER_ROW1_Y,
        font="Helvetica-Bold",
        colour=light_blue,
        size=14,
        left_aligned=True,
    )
    draw_text_on_pdf(
        pdf, 
        "Data Recording Equipment Used", 
        Layout.RIGHT_COL_X + (Layout.RIGHT_COL_W / 2), 
        475, 
        "Helvetica-Bold", 
        size=12
    )
    draw_text_on_pdf(
        pdf, 
        "3rd Party Stamp and Date", 
        Layout.RIGHT_COL_X + (Layout.RIGHT_COL_W / 2), 
        45, 
        "Helvetica-Bold", 
        size=12
    )


def build_production_text_positions(test_metadata, channel_info, light_blue, black, breakout_torque=None, running_torque=None, allowable_drop=None):
    """Build text position list for production reports."""
    # Parse test date from Date Time metadata
    test_date = ""
    if test_metadata.get('Date Time'):
        try:
            dt = test_metadata['Date Time'].replace('T', ' ')
            # Convert from "2026-01-21 145537.940" to "21-01-2026 14:55:37"
            parts = dt.split(' ')
            if len(parts) == 2:
                date_part = parts[0]  # 2026-01-21
                y, m, d = date_part.split('-')
                test_date = f"{d}/{m}/{y}"
        except:
            test_date = test_metadata.get('Date Time', '')
    
    # Format torque values - show N/A if 0 or None
    breakout_display = "N/A" if not breakout_torque or breakout_torque == 0 else f"{breakout_torque} ft.lbs"
    running_display = "N/A" if not running_torque or running_torque == 0 else f"{running_torque} ft.lbs"
    
    return [
        (Layout.HEADER_COL1_LABEL_X, Layout.HEADER_ROW1_Y, "OTS Number", black, False),
        (Layout.HEADER_COL1_VALUE_X, Layout.HEADER_ROW1_Y, test_metadata.get('OTS Number', ''), light_blue, True),
        (Layout.HEADER_COL1_LABEL_X, Layout.HEADER_ROW2_Y, "Unique Number", black, False),
        (Layout.HEADER_COL1_VALUE_X, Layout.HEADER_ROW2_Y, test_metadata.get('Unique Number', ''), light_blue, True),
        (Layout.HEADER_COL1_LABEL_X, Layout.HEADER_ROW3_Y, "Drawing Number", black, False),
        (Layout.HEADER_COL1_VALUE_X, Layout.HEADER_ROW3_Y, test_metadata.get('Drawing Number', ''), light_blue, True),
        (Layout.HEADER_COL1_LABEL_X, Layout.HEADER_ROW4_Y, "Client", black, False),
        (Layout.HEADER_COL1_VALUE_X, Layout.HEADER_ROW4_Y, test_metadata.get('Client', ''), light_blue, True),
        
        (Layout.HEADER_COL2_LABEL_X, Layout.HEADER_ROW1_Y, "Line Item", black, False),
        (Layout.HEADER_COL2_VALUE_X, Layout.HEADER_ROW1_Y, test_metadata.get('Line Item', ''), light_blue, True),
        (Layout.HEADER_COL2_LABEL_X, Layout.HEADER_ROW2_Y, "Test Date", black, False),
        (Layout.HEADER_COL2_VALUE_X, Layout.HEADER_ROW2_Y, test_date, light_blue, True),

        (Layout.RIGHT_COL_LABEL_X, (Layout.TRANSDUCERS_Y - Layout.TRANSDUCER_ROW_HEIGHT * 2), "Test Pressure", black, False),
        (Layout.RIGHT_COL_VALUE_X, (Layout.TRANSDUCERS_Y - Layout.TRANSDUCER_ROW_HEIGHT * 2), f"{test_metadata.get('Test Pressure', '0')} psi", light_blue, True),
        (Layout.RIGHT_COL_LABEL_X, (Layout.TRANSDUCERS_Y - Layout.TRANSDUCER_ROW_HEIGHT * 3), "Max Pressure", black, False),
        (Layout.RIGHT_COL_VALUE_X, (Layout.TRANSDUCERS_Y - Layout.TRANSDUCER_ROW_HEIGHT * 3), f"{int(min(int(test_metadata.get('Test Pressure', '0')) * 1.05, int(test_metadata.get('Test Pressure', '0')) + 500))} psi", light_blue, True),
        (Layout.RIGHT_COL_LABEL_X, (Layout.TRANSDUCERS_Y - Layout.TRANSDUCER_ROW_HEIGHT * 4), "Breakout Torque", black, False),
        (Layout.RIGHT_COL_VALUE_X, (Layout.TRANSDUCERS_Y - Layout.TRANSDUCER_ROW_HEIGHT * 4), breakout_display, light_blue, False),
        (Layout.RIGHT_COL_LABEL_X, (Layout.TRANSDUCERS_Y - Layout.TRANSDUCER_ROW_HEIGHT * 5), "Running Torque", black, False),
        (Layout.RIGHT_COL_VALUE_X, (Layout.TRANSDUCERS_Y - Layout.TRANSDUCER_ROW_HEIGHT * 5), running_display, light_blue, False),
        (Layout.RIGHT_COL_LABEL_X, (Layout.TRANSDUCERS_Y - Layout.TRANSDUCER_ROW_HEIGHT * 6), "Allowable Drop", black, False),
        (Layout.RIGHT_COL_VALUE_X, (Layout.TRANSDUCERS_Y - Layout.TRANSDUCER_ROW_HEIGHT * 6), f"{allowable_drop} psi", light_blue, False),

        (Layout.RIGHT_COL_LABEL_X, Layout.DATA_LOGGER_Y, "Data Logger", black, False),
        (Layout.RIGHT_COL_VALUE_X, Layout.DATA_LOGGER_Y, test_metadata.get('Data Logger', ''), light_blue, True),
        (Layout.RIGHT_COL_LABEL_X, Layout.SERIAL_NO_Y, "Serial No.", black, False),
        (Layout.RIGHT_COL_VALUE_X, Layout.SERIAL_NO_Y, test_metadata.get('Serial Number', ''), light_blue, True),
        (Layout.RIGHT_COL_LABEL_X, Layout.TRANSDUCERS_Y, "Transducer", black, False),

        (Layout.RIGHT_COL_LABEL_X, Layout.OPERATIVE_Y, "Operative:", black, False),
        (Layout.OPERATIVE_VALUE_X, Layout.OPERATIVE_Y, test_metadata.get('User', ''), light_blue, False),
    ]


def build_production_transducer_positions(transducer_code, light_blue):
    """Build transducer position for production reports."""
    return [(Layout.RIGHT_COL_VALUE_X, Layout.TRANSDUCERS_Y, transducer_code, light_blue, False)]


def draw_all_text(pdf, pdf_text_positions):
    """Draw all text positions on PDF."""
    for x, y, text, colour, replace_empty in pdf_text_positions:
        draw_text_on_pdf(pdf, text, x, y, colour=colour, size=10, left_aligned=True, replace_empty=replace_empty)


def draw_footer_metadata(pdf_canvas, test_metadata) -> None:
    """Draw footer timestamp."""
    date_time = test_metadata.get("Date Time", "")
    if not date_time:
        return

    font = "Helvetica-Oblique"
    size = 8
    colour = Color(0.5, 0.5, 0.5)

    text_width = pdf_canvas.stringWidth(date_time, font, size)
    x = Layout.PAGE_WIDTH - Layout.MARGIN_RIGHT - text_width

    draw_text_on_pdf(
        pdf_canvas,
        date_time,
        x,
        Layout.FOOTER_TEXT_Y,
        colour=colour,
        font=font,
        size=size,
        left_aligned=True,
    )


def draw_table(pdf_canvas, dataframe, x=15, y=15, width=600, height=51.5):
    """Render a DataFrame as a table on PDF canvas."""
    if dataframe is None or dataframe.empty:
        return

    df = dataframe.dropna(axis=1, how="all")
    data = df.astype(str).values.tolist()
    if not data or not data[0]:
        return

    rows = len(data)
    cols = len(data[0])
    col_width = width / cols
    row_height = height / rows

    table = Table(
        data,
        colWidths=col_width,
        rowHeights=[row_height] * rows,
    )

    style = TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('BACKGROUND', (0, 0), (-1, -1), colors.white),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
    ])
    table.setStyle(style)
    table.wrapOn(pdf_canvas, width, height)
    table.drawOn(pdf_canvas, x, y)


def draw_production_test_details(test_metadata, channel_info, pdf_output_path, cleaned_data, transducer_code, allowable_drop, breakout_torque, running_torque):
    """Generate production test details PDF."""
    pdf = canvas.Canvas(str(pdf_output_path), pagesize=landscape(A4))
    pdf.setStrokeColor(colors.black)
    draw_production_layout_boxes(pdf)
    light_blue = Color(0.325, 0.529, 0.761)
    black = Color(0, 0, 0)
    draw_headers(pdf, test_metadata, light_blue)
    pdf_text_positions = build_production_text_positions(test_metadata, channel_info, light_blue, black, breakout_torque, running_torque, allowable_drop)
    
    pdf_text_positions += build_production_transducer_positions(transducer_code, light_blue)
    draw_all_text(pdf, pdf_text_positions)
    draw_footer_metadata(pdf, test_metadata)
    return pdf
