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


from ai_processing import process_image, create_prompt, clean_response

# Function to safely delete a file with retries
def safe_delete(file_path, max_retries=5, retry_delay=1):
    """Safely delete a file with retries for Windows compatibility"""
    if not os.path.exists(file_path):
        return True
        
    for i in range(max_retries):
        try:
            # Force garbage collection to release file handles
            gc.collect()
            
            # Try to delete the file
            os.unlink(file_path)
            return True
        except PermissionError:
            if i < max_retries - 1:
                time.sleep(retry_delay)
            else:
                # If we still can't delete it after retries, just log the error
                st.warning(f"Could not delete temporary file: {file_path}")
                return False
        except FileNotFoundError:
            # File already gone
            return True
        except Exception as e:
            st.warning(f"Error deleting file {file_path}: {e}")
            return False
            
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

# Function to extract images from PDF
def extract_images_from_pdf(pdf_file, temp_dir):
    image_files = []
    temp_pdf_path = None
    doc = None
    
    try:
        # Save the uploaded PDF to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_pdf:
            tmp_pdf.write(pdf_file.read())
            temp_pdf_path = tmp_pdf.name
        
        # Open the PDF with PyMuPDF
        doc = fitz.open(temp_pdf_path)
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
            img_path = os.path.join(temp_dir, f"page_{page_num + 1}.png")
            pix.save(img_path)
            image_files.append(img_path)
            
            # Update progress
            progress_bar.progress((page_num + 1) / total_pages)
        
        progress_bar.empty()
        return image_files, total_pages
    except Exception as e:
        st.error(f"Error extracting images from PDF: {e}")
        return [], 0
    finally:
        # Close the document before trying to delete
        if doc:
            doc.close()
            
        # Clean up the temporary PDF file
        if temp_pdf_path:
            # Use a slight delay to ensure file handle is released
            time.sleep(0.5)
            safe_delete(temp_pdf_path)
            
# Function to process PDF
def process_pdf(pdf_file, delay_seconds):
    temp_dir = tempfile.mkdtemp()
    try:
        st.info("Extracting pages from PDF...")
        image_files, total_pages = extract_images_from_pdf(pdf_file, temp_dir)
        
        if not image_files:
            st.error("No pages could be extracted from the PDF.")
            return None
        
        combined_text = ""
        
        with st.expander("Processing Details", expanded=True):
            for i, img_path in enumerate(image_files):
                st.markdown(f"**Processing page {i+1}/{total_pages}**")
                
                try:
                    # Open the image with PIL
                    image = Image.open(img_path)
                    # Process the image
                    result = process_image(image)
                    # Close the image to release file handle
                    image.close()
                    
                    if result:
                        combined_text += result + "\n\n"
                        st.success(f"Page {i+1} processed successfully")
                    else:
                        st.error(f"Failed to process page {i+1}")
                except Exception as e:
                    st.error(f"Error processing page {i+1}: {e}")
                
                # Add delay between API calls to avoid rate limiting
                if i < len(image_files) - 1:  # Don't delay after the last page
                    st.info(f"Waiting {delay_seconds} seconds before processing next page...")
                    time_placeholder = st.empty()
                    for remaining in range(delay_seconds, 0, -1):
                        time_placeholder.info(f"Waiting {remaining} seconds...")
                        time.sleep(1)
                    time_placeholder.empty()
        
        return combined_text.strip()
    finally:
        # Cleanup: remove the temporary directory and all its contents
        try:
            # Force garbage collection to release file handles
            gc.collect()
            # Wait a bit to ensure files are released
            time.sleep(1)
            # Use shutil which is more reliable for directory removal
            shutil.rmtree(temp_dir, ignore_errors=True)
            
            # Double-check if directory still exists and try another method
            if os.path.exists(temp_dir):
                # Try to remove files first
                for root, dirs, files in os.walk(temp_dir):
                    for file in files:
                        safe_delete(os.path.join(root, file))
                # Then try to remove empty directories
                for root, dirs, files in os.walk(temp_dir, topdown=False):
                    for dir in dirs:
                        try:
                            os.rmdir(os.path.join(root, dir))
                        except:
                            pass
                # Finally try to remove the temp dir itself
                try:
                    os.rmdir(temp_dir)
                except:
                    st.warning(f"Note: Could not remove temporary directory: {temp_dir}")
        except Exception as e:
            st.warning(f"Note: Could not completely clean up temporary files. Some files may remain in temporary folders: {e}")
            
# Function to create a download link for text as PDF
def get_download_link(text, filename="hinglish_translation.pdf", link_text="Download Hinglish Text as PDF"):
    """Generates a link to download the text as a PDF file"""
    pdf_bytes = text_to_pdf(text)
    b64 = base64.b64encode(pdf_bytes.getvalue()).decode()
    href = f'<a href="data:application/pdf;base64,{b64}" download="{filename}">{link_text}</a>'
    return href