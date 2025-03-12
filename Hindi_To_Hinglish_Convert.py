import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
import os
from PIL import Image
import tempfile
import time
import fitz  # PyMuPDF
import re
import base64
from io import BytesIO
import shutil
import gc
import fpdf  # Add this for PDF generation

# importing from modules
from doc_file_processing import safe_delete, text_to_pdf, extract_images_from_pdf, process_pdf, get_download_link
from ai_processing import process_image, create_prompt, clean_response


# Page configuration
st.set_page_config(
    page_title="Hindi to Hinglish Converter",
    page_icon="🔤💬🇮🇳",
    layout="wide"
)

# Custom CSS for better UI
st.markdown("""
<style>
    .main-title {
        font-size: 36px;
        font-weight: bold;
        color: #FF4B4B;
        text-align: center;
        margin-bottom: 30px;
    }
    .sub-title {
        font-size: 24px;
        font-weight: bold;
        color: #0066CC;
        margin-top: 20px;
        margin-bottom: 10px;
    }
    .info-text {
        font-size: 16px;
        color: #404040;
    }
    .warning-text {
        font-size: 14px;
        color: #FF4B4B;
    }
</style>
""", unsafe_allow_html=True)

# App title and description
st.markdown('<p class="main-title">Hindi to Hinglish Converter</p>', unsafe_allow_html=True)
st.markdown('<p class="info-text">Convert Hindi text from images or PDFs to Hinglish (Hindi written in Roman script)</p>', unsafe_allow_html=True)

with st.expander("How to Use This App", expanded=False):
    st.markdown("""
    ## How to Use the Hindi to Hinglish Converter

    This application converts Hindi text found in images or PDFs to Hinglish (Hindi written in Roman script). Follow these simple steps to use the app:
    ### Step 1: Select Input Type
    - Choose either **Image** or **PDF** option depending on your source file

    ### Step 2: Upload Your File
    - For **Image**: Upload a JPG, JPEG, or PNG file containing Hindi text
    - For **PDF**: Upload a PDF file containing Hindi text (maximum 10 pages)

    ### Step 3: Convert
    - Click the **Convert to Hinglish** button to start the conversion process
    - For PDFs, the app will process each page with a short delay between pages to avoid API rate limits

    ### Step 4: View and Download Results
    - Once processing is complete, the converted Hinglish text will appear in the text area
    - Click the **Download Hinglish Text as PDF** link which is in blue color, to save the conversion as a PDF file
    - The downloaded file will be named using your original filename with "_hinglish_converted" added to it

    ### Notes:
    - The conversion quality depends on the clarity of the Hindi text in your original file
    - For better results, ensure your images are clear and text is easily readable
    - The app processes a maximum of 10 pages for PDF files
    - There is a built-in delay of 10 seconds between processing PDF pages to avoid API rate limits
    """)
# Main app interface
st.markdown('<p class="sub-title">Upload Options</p>', unsafe_allow_html=True)

# Input type selection
input_type = st.radio("Select input type:", ["Image", "PDF"])

delay_seconds = 10

# File uploader
st.markdown('<p class="sub-title">Upload File</p>', unsafe_allow_html=True)

if input_type == "Image":
    uploaded_file = st.file_uploader("Upload an image with Hindi text", type=["jpg", "jpeg", "png"])
    
    if uploaded_file:
        st.image(uploaded_file, caption="Uploaded Image")
        
        if st.button("Convert to Hinglish"):
            # Store image in memory instead of creating a temporary file
            image_bytes = uploaded_file.getvalue()
            image = Image.open(BytesIO(image_bytes))
            
            try:
                result = process_image(image)
                
                # Close the image to release resources
                image.close()
                
                if result:
                    
                    st.markdown('<p class="sub-title">Hinglish Output</p>', unsafe_allow_html=True)
                    st.text_area("Hinglish Text", result, height=250)
                    
                    # Get original filename without extension
                    original_name = os.path.splitext(uploaded_file.name)[0]
                    download_filename = f"{original_name}_hinglish_converted.pdf"
                    
                    st.markdown(get_download_link(result, filename=download_filename), unsafe_allow_html=True)
                    st.toast(f"___Now you can download the converted Hinglish Text from below blue link in pdf format___")
                    st.balloons()
            except Exception as e:
                st.error(f"Error: {e}")

else:  # PDF option
    uploaded_file = st.file_uploader("Upload a PDF with Hindi text (max 10 pages)", type=["pdf"])
    
    if uploaded_file:
        st.info(f"Uploaded: {uploaded_file.name}")
        
        if st.button("Convert to Hinglish"):
            result = process_pdf(uploaded_file, delay_seconds)
            
            if result:
                st.markdown('<p class="sub-title">Hinglish Output</p>', unsafe_allow_html=True)
                st.text_area("Hinglish Text", result, height=350)
                
                # Get original filename without extension
                original_name = os.path.splitext(uploaded_file.name)[0]
                download_filename = f"{original_name}_hinglish_converted.pdf"
                
                st.markdown(get_download_link(result, filename=download_filename), unsafe_allow_html=True)
                st.toast("___Now you can download the converted Hinglish Text from below blue link in pdf format 'Download Hinglish Text as PDF___")
                st.balloons()

# Footer
st.markdown("---")
st.markdown("""Made with 🧠 by [Sourabh Dey](https://linktr.ee/sourabhdey)""")
st.markdown("Hindi to Hinglish Converter | Powered by Google Gemini API")