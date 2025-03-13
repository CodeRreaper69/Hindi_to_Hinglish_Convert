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

# Load environment variables
load_dotenv()

# Function to check if API key is set
def is_api_key_set():
    api_key = os.getenv("API_KEY")
    if not api_key:
        api_key = st.session_state.get('api_key', '')
    return bool(api_key)

# API key input if not set in environment
if not is_api_key_set():
    st.markdown('<p class="sub-title">API Key Setup</p>', unsafe_allow_html=True)
    api_key = st.text_input("Enter your Google Gemini API Key:", type="password")
    if api_key:
        st.session_state['api_key'] = api_key
        os.environ["API_KEY"] = api_key
        st.success("API Key set successfully!")
    else:
        st.warning("Please enter your Google Gemini API Key to continue.")
        st.stop()

# Configure the API
try:
    GOOGLE_API_KEY = os.getenv("API_KEY") or st.session_state.get('api_key', '')
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error(f"Error initializing the API: {e}")
    st.stop()

# Function to create Hinglish conversion prompt
def create_prompt():
    return """
    You are an expert Hinglish translator. You will receive images containing Hindi text, and your task is to accurately convert that text into Hinglish (Hindi written using the Roman alphabet). Pay close attention to context and ensure the transliteration is as natural and readable as possible.
    
    Here are a few examples of Hindi text and their Hinglish conversions:
    **Examples:**
    ***Image Text (Hindi):** नमस्ते
        **Hinglish:** Namaste
    ***Image Text (Hindi):** आप कैसे हैं?
        **Hinglish:** Aap kaise hain?
    ***Image Text (Hindi):** मेरा नाम...
        **Hinglish:** Mera naam...
    ***Image Text (Hindi):** यह एक उदाहरण है।
        **Hinglish:** Yeh ek udaharan hai.
    
    Now, convert the text in the following image to Hinglish
    NOTE - 
    Do Not Add Words like - 
    "Here's the Hinglish translation of the text from the image:" OR "Okay, here's the Hinglish translation of the text from the image:" in the text just the total converted text 
    """

# Function to clean AI-generated prefixes
def clean_response(text):
    # Patterns to remove
    patterns = [
        r"^Here\'s the Hinglish translation of the text from the image:\s*",
        r"^Okay, here\'s the Hinglish translation of the text from the image:\s*",
        r"^The Hinglish translation of the text is:\s*",
        r"^Hinglish translation:\s*",
        r"^Here\'s the translation:\s*",
        r"^Translation:\s*"
    ]
    
    for pattern in patterns:
        text = re.sub(pattern, "", text, flags=re.IGNORECASE)
    
    return text.strip()

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

# Function to process a single image
def process_image(image):
    with st.spinner("Converting image to Hinglish..."):
        try:
            prompt = create_prompt()
            response = model.generate_content([prompt, image])
            result = clean_response(response.text)
            return result
        except Exception as e:
            st.error(f"Error processing image: {e}")
            return None

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

# Main app interface
st.markdown('<p class="sub-title">Upload Options</p>', unsafe_allow_html=True)

# Input type selection
input_type = st.radio("Select input type:", ["Image", "PDF"])

# Set delay
delay_seconds = 10

# File uploader
st.markdown('<p class="sub-title">Upload File</p>', unsafe_allow_html=True)

if input_type == "Image":
    uploaded_file = st.file_uploader("Upload an image with Hindi text", type=["jpg", "jpeg", "png"])
    
    if uploaded_file:
        st.image(uploaded_file, caption="Uploaded Image")
        
        if st.button("Convert to Hinglish / Hinglish me convert kare"):
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
                    st.toast(":green[__Download From Below / Neeche se Download Kare__]")
                    st.balloons()
            except Exception as e:
                st.error(f"Error: {e}")

else:  # PDF option
    uploaded_file = st.file_uploader("Upload a PDF with Hindi text (max 10 pages)", type=["pdf"])
    
    if uploaded_file:
        st.info(f"Uploaded: {uploaded_file.name}")
        
        if st.button("Convert to Hinglish / Hinglish me convert kare"):
            result = process_pdf(uploaded_file, delay_seconds)
            
            if result:
                st.markdown('<p class="sub-title">Hinglish Output</p>', unsafe_allow_html=True)
                st.text_area("Hinglish Text", result, height=350)
                
                # Get original filename without extension
                original_name = os.path.splitext(uploaded_file.name)[0]
                download_filename = f"{original_name}_hinglish_converted.pdf"
                st.markdown(get_download_link(result, filename=download_filename), unsafe_allow_html=True)
                st.toast(":green[__Download From Below / Neeche se Download Kare__]")
                st.balloons()

# Footer
st.markdown("---")
st.markdown("""Made with 🧠 by [Sourabh Dey](https://linktr.ee/sourabhdey)""")
st.markdown("Hindi to Hinglish Converter | Powered by Google Gemini API")
