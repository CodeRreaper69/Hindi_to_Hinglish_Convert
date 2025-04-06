# Hindi to Hinglish Converter

## Overview

Hindi to Hinglish Converter is a web application that transforms Hindi text from images or PDF documents into Hinglish (Hindi written in Roman script). This tool addresses a common challenge: many people can speak Hindi but struggle with reading Devanagari script. The converter provides an accessible solution for those who find it easier to read Hindi content when it's written using the Roman alphabet.

📺 **[Watch the demo video](https://drive.google.com/file/d/1yF8gSUZ3Ql0XM3FqfuOe2J72QNZvAXvU/view?usp=drive_link)**

🌐 **[Live App](https://hindi-to-hinglish-converter-using-ai-gemini-by-sourabh-dey.streamlit.app/)**

## Problem Statement

Many individuals, despite being fluent in speaking Hindi, face difficulties when reading content written in Devanagari script. This creates a significant accessibility barrier for:

- People who grew up speaking Hindi but learned to read primarily in English
- Those who are more comfortable with Roman script
- Learners of Hindi who haven't yet mastered the Devanagari writing system
- Individuals who need to quickly access Hindi content but aren't proficient in reading the script

Existing solutions in the market are either limited in functionality or require payment for comprehensive services.

## Solution

This application leverages Google's Gemini 2.0 Flash model to accurately transliterate Hindi text from images and PDF documents into Hinglish. Key features include:

- Support for both image files (JPG, JPEG, PNG) and PDF documents
- PDF processing capability (up to 10 pages)
- Easy-to-use web interface built with Streamlit
- Downloadable results in PDF format
- Safe rate-limiting to prevent API throttling
- Memory-efficient processing using BytesIO for handling files
- Hosted on Streamlit Cloud for easy access

## How It Works

1. The user uploads an image or PDF containing Hindi text
2. For images: The application processes the image directly
3. For PDFs: The system extracts each page as an image
4. The Gemini 2.0 Flash model identifies Hindi text in the images and converts it to Hinglish
5. Results are displayed in the web interface and available for download as a PDF

## Screenshots

<div align="center">
  <table>
    <tr>
      <td align="center" width="50%">
        <strong>Image Conversion Interface</strong><br>
        <img src="/image/Image_Hindi_to_Hinglish.jpg" alt="Image Hindi to Hinglish" width="100%">
      </td>
      <td align="center" width="50%">
        <strong>PDF Conversion Interface</strong><br>
        <img src="/image/PDF_Conversion.jpg" alt="PDF Conversion" width="100%">
      </td>
    </tr>
    <tr>
      <td align="center" width="50%">
        <strong>Conversion Results</strong><br>
        <img src="/image/Conversion_Result.jpg" alt="Conversion Result" width="100%">
      </td>
      <td align="center" width="50%">
        <strong>Text Output Example</strong><br>
        <img src="/image/Conversion_Result_text.jpg" alt="Conversion Result Text" width="100%">
      </td>
    </tr>
  </table>
</div>

## Technical Implementation

### Architecture

The project is organized with the following structure:

```
\Hindi_to_Hinglish_Convert
    |   .env
    |   ai_processing.py
    |   doc_file_processing.py
    |   hindi_to_hinglish_all_code_at_once.py
    |   main_enhanced.py
    |   requirements.txt
    |   __init__.py
    |
    +---Earlier_Scripts
    |   ai_processing.py
    |   doc_file_processing.py
    |   enhanced_hindi_to_hinglish_conversion.py
    |   hindi_to_hinglish.py
    |   Hindi_To_Hinglish_Convert.py
    |   requirements.txt
    |   __init__.py
    |
    +---image
        +---Conversion_Result
        +---Conversion_Result_text
        +---Image_Hindi_to_Hinglish
        +---PDF_Conversion
```

### Key Components

1. **Streamlit Interface**: Creates a user-friendly web application for file uploads and results display
2. **Google Gemini API Integration**: Handles the AI-powered transliteration of Hindi to Hinglish
3. **PyMuPDF (fitz)**: Extracts images from PDF documents
4. **Memory Management**: Uses BytesIO for efficient file handling without temporary files
5. **PDF Generation**: Creates downloadable PDF files from the converted text

### Technical Choices

- **Streamlit**: Selected for rapid development of web interfaces with minimal frontend code
- **Gemini 2.0 Flash**: Chosen for its powerful image understanding and language capabilities
- **BytesIO**: Implemented to manage memory efficiently without creating temporary files
- **Rate Limiting**: Built-in 10-second delay between page processing to prevent API throttling
- **Page Limitation**: Restricted to 10 pages per PDF to ensure reasonable processing times
- **Streamlit Cloud**: Used for hosting the application for easy access without local setup

## Installation & Setup

1. Clone the repository
```bash
git clone https://github.com/CodeRreaper69/Hindi_to_Hinglish_Convert.git
cd Hindi_to_Hinglish_Convert
```

2. Install the required dependencies
```bash
pip install -r requirements.txt
```

3. Set up your Google Gemini API key
   - Create a `.env` file in the root directory
   - Add your API key: `GEMINI_API_KEY=your_api_key_here`

4. Run the application
```bash
streamlit run main_enhanced.py
```

## Usage Instructions

1. **Launch the application** through your web browser
2. **Select input type**: Choose either "Image" or "PDF" based on your file type
3. **Upload your file**: Use the file uploader to select your Hindi text document
4. **Convert**: Click the "Convert to Hinglish / Hinglish me convert kare" button
5. **View results**: The converted Hinglish text will appear in the text area
6. **Download**: Use the blue download link to save your conversion as a PDF file

## Limitations & Considerations

- Maximum processing limit of 10 pages per PDF
- 10-second delay between pages to respect API rate limits
- Conversion quality depends on the clarity of text in source images
- No data persistence - files are processed in-session and not stored permanently

## Future Enhancements

- Implement batch processing for larger documents
- Add support for more regional Indian languages
- Create offline processing capabilities for improved speed
- Develop user accounts for saving conversion history

## Deployment

This application is deployed on Streamlit Cloud for easy access. You can use the application without setting it up locally by visiting the [live app](https://hindi-to-hinglish-converter-using-ai-gemini-by-sourabh-dey.streamlit.app/).

## Developer

Made with 🧠 by [Sourabh Dey](https://linktr.ee/sourabhdey)
