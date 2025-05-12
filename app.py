# for streamlit 
import streamlit as st
import barcode
from barcode.writer import ImageWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
import os
import math
from datetime import datetime
from io import BytesIO
from PIL import Image

# Generate barcodes
def generate_barcodes(codes, output_folder="barcodes_streamlit"):
    os.makedirs(output_folder, exist_ok=True)
    filenames = []
    for code in codes:
        barcode_class = barcode.get_barcode_class('code128')
        my_code = barcode_class(code, writer=ImageWriter())
        filename = os.path.join(output_folder, f"{code}.png")
        my_code.save(
            filename.replace(".png", ""),
            options={
                "module_height": 2.8,
                "font_size": 6.0,
                "text_distance": 2.25,
                "quiet_zone": 2.0
            }
        )
        filenames.append(filename)
    return filenames

# Create PDF
def create_sticker_sheet(barcode_files):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    page_width, page_height = A4

    cols = 3
    label_width = 60 * mm
    label_height = 18* mm

    x_margin = (page_width - (cols * label_width)) / 2
    y_start = page_height - 40 * mm  # top margin

    max_rows_per_page = int((page_height - 20 * mm) // label_height)

    for idx, file in enumerate(barcode_files):
        page_index = (idx // (cols * max_rows_per_page))
        position_on_page = idx % (cols * max_rows_per_page)
        col = position_on_page % cols
        row = position_on_page // cols

        x = x_margin + col * label_width
        y = y_start - (row * label_height)

        if position_on_page == 0 and idx != 0:
            c.showPage()

        c.drawImage(file, x, y, width=label_width, height=label_height)

    c.save()
    buffer.seek(0)
    return buffer

# Streamlit UI
st.set_page_config(page_title="Barcode Sheet Generator", layout="centered")
st.title("📦 SPD GEOAXIS Barcode Sheet Generator")

start = st.number_input("Start Number", min_value=1, step=1)
end = st.number_input("End Number", min_value=start, step=1)

if st.button("Generate PDF"):
    if start <= end:
        with st.spinner("Generating barcodes and preparing PDF..."):
            sample_codes = [f"UEPL-SPD-{i:08d}" for i in range(start, end + 1)]
            barcodes = generate_barcodes(sample_codes)
            pdf_file = create_sticker_sheet(barcodes)

        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        st.success("✅ PDF ready!")
        st.download_button(
            label="📄 Download Sticker Sheet PDF",
            data=pdf_file,
            file_name=f"sticker_sheet_{timestamp}.pdf",
            mime="application/pdf"
        )
    else:
        st.error("❌ End number must be greater than or equal to Start number.")
