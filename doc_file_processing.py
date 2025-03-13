# Document Image Processing Functions

import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
import os
from PIL import Image
import time
import fitz  # PyMuPDF
import re
import base64
import io
from io import BytesIO
import gc
import fpdf  # Add this for PDF generation


# Importing from ai_processing.py 
from ai_processing import  clean_response, process_image

# Function to create a PDF from text
def text_to_pdf(text):
    pdf = fpdf.FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    # Split text by lines and add to PDF
    lines = text.split('\n')
    for line in lines:
        # Encode special characters
        encoded_line = line.encode('latin-1', 'replace').decode('latin-1')
        pdf.multi_cell(0, 10, encoded_line)
        
    # Return PDF as bytes
    return BytesIO(pdf.output(dest='S').encode('latin-1'))
    
    
    
# Function to extract images from PDF using BytesIO instead of temp files
def extract_images_from_pdf(pdf_file):
    image_list = []
    
    try:
        # Read PDF file as bytes
        pdf_bytes = pdf_file.read()
        
        # Create a BytesIO object to avoid saving to disk
        pdf_stream = BytesIO(pdf_bytes)
        
        # Open the PDF with PyMuPDF using the BytesIO stream
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        total_pages = len(doc)
        
        # Check page limit
        if total_pages > 10:
            st.warning(f"PDF has {total_pages} pages. Only the first 10 pages will be processed due to the page limit.")
            total_pages = 10
        
        # Create progress bar
        progress_bar = st.progress(0)
        
        for page_num in range(total_pages):
            page = doc.load_page(page_num)
            pix = page.get_pixmap(matrix=fitz.Matrix(300/72, 300/72))
            
            # Convert pixmap to PIL Image directly using BytesIO
            img_bytes = pix.tobytes("png")
            img_stream = BytesIO(img_bytes)
            img = Image.open(img_stream)
            
            # Store PIL image in the list
            image_list.append((page_num + 1, img))
            
            # Update progress
            progress_bar.progress((page_num + 1) / total_pages)
        
        progress_bar.empty()
        return image_list, total_pages
    except Exception as e:
        st.error(f"Error extracting images from PDF: {e}")
        return [], 0
    finally:
        # Force garbage collection
        gc.collect()

# Function to process PDF
def process_pdf(pdf_file, delay_seconds):
    try:
        st.info("Extracting pages from PDF...")
        image_list, total_pages = extract_images_from_pdf(pdf_file)
        
        if not image_list:
            st.error("No pages could be extracted from the PDF.")
            return None
        
        combined_text = ""
        
        with st.expander("Processing Details", expanded=True):
            for page_num, image in image_list:
                st.markdown(f"**Processing page {page_num}/{total_pages}**")
                
                try:
                    # Process the image
                    result = process_image(image)
                    
                    if result:
                        combined_text += result + "\n\n"
                        st.success(f"Page {page_num} processed successfully")
                    else:
                        st.error(f"Failed to process page {page_num}")
                except Exception as e:
                    st.error(f"Error processing page {page_num}: {e}")
                
                # Add delay between API calls to avoid rate limiting
                if page_num < total_pages:  # Don't delay after the last page
                    st.info(f"Waiting {delay_seconds} seconds before processing next page...")
                    time_placeholder = st.empty()
                    for remaining in range(delay_seconds, 0, -1):
                        time_placeholder.info(f"Waiting {remaining} seconds...")
                        time.sleep(1)
                    time_placeholder.empty()
        
        return combined_text.strip()
    finally:
        # Force garbage collection to release memory
        gc.collect()

# Function to create a download link for text as PDF
def get_download_link(text, filename="hinglish_translation.pdf", link_text="Download Hinglish Text as PDF/ Hinglish Text Download Kare"):
    """Generates a link to download the text as a PDF file"""
    pdf_bytes = text_to_pdf(text)
    b64 = base64.b64encode(pdf_bytes.getvalue()).decode()
    href = f'<a href="data:application/pdf;base64,{b64}" download="{filename}">{link_text}</a>'
    return href
