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
    
    
