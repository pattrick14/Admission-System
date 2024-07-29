import pytesseract
from PIL import Image
import re, cv2
import numpy as np
from pdf2image import convert_from_path
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors


def convtPDF(file_path):
    pdfImage = convert_from_path(file_path)
    return pdfImage

# Convert the image to grayscale
def grayscaling(image):
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# noise removal
def gaussian_blur(image, kernel_size=(5, 5)):
    return cv2.GaussianBlur(image, kernel_size, 0)

def thresholding(image):
    # Convert the image to grayscale
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # Apply Otsu thresholding
    _, binary_image = cv2.threshold(gray_image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    return binary_image

def resize_image(image, target_width):
    # Calculate the aspect ratio
    aspect_ratio = image.shape[1] / image.shape[0]
    # Calculate the target height based on the aspect ratio
    target_height = int(target_width / aspect_ratio)
    # Resize the image
    resized_image = cv2.resize(image, (target_width, target_height))
    
    return resized_image

# Preprocess the image (e.g., resize, denoise, enhance)
def preprocessing(image: np.ndarray) -> np.ndarray:
    # grayImg = grayscaling(image)
    # thresholdImg = thresholding(image)
    image = cv2.imread(image)
    resizedImg = resize_image(image, (2480,0))

    return resizedImg

def perform_ocr(image_path):
    try:
        print(image_path)
        pdfImage = convert_from_path(image_path, fmt='png', 
                    output_folder='media/images', 
                    poppler_path = r"C:\Users\Pratik Bhilore\Downloads\Release-23.11.0-0\poppler-23.11.0\Library\bin", 
                    first_page=1, last_page=1, grayscale=True)
        # Open the image file
        if pdfImage:
            # processedImg = preprocessing(pdfImage[0])
            # Perform OCR using Tesseract
            text = pytesseract.image_to_string(pdfImage[0])
            return text
    except Exception as e:
        print(f"Error during OCR: {e}")
        return ""

def extract_info(text):
    """
    Extract information from OCR text output.

    Args:
    - text (str): OCR text to extract information from.

    Returns:
    - dict: Dictionary containing extracted information.
    """
    info_dict = {}

    # Example extraction logic based on your previous requirements
    try:
        info_dict['ApplicationID'] = re.search(r'Application ID : (\w+)', text).group(1)
    except AttributeError:
        info_dict['ApplicationID'] = None

    try:
        info_dict['Category'] = re.search(r'Category\s*[\|\[]?\s*(\w+)', text).group(1)
    except AttributeError:
        info_dict['Category'] = None

    try:
        info_dict['Candidate Name'] = re.search(r'Candidate Name\s*[\|\[]?\s*(\w+)', text).group(1)
    except AttributeError:
        info_dict['Candidate Name'] = None

    try:
        info_dict['State General Merit No'] = int(re.search(r'State General Merit No[\s\[\|\(]*([\d]+)', text).group(1))
    except AttributeError:
        info_dict['State General Merit No'] = None

    try:
        info_dict['All India Merit No'] = int(re.search(r'India Merit No[\s\[\|\(]*([\d]+)', text).group(1))
    except AttributeError:
        info_dict['All India Merit No'] = None

    try:
        # info_dict['CET_Physics'] = float(re.search(r'Physics \| (\d+\.\d+)', text).group(1))
        info_dict['CET_Physics'] = float(re.search(r'Physics\s*[\|\[]?\s*(\d+\.\d+)', text).group(1))
    except AttributeError:
        info_dict['CET_Physics'] = None

    try:
        # info_dict['CET_Chemistry'] = float(re.search(r'Chemistry \| (\d+\.\d+)', text).group(1))
        info_dict['CET_Chemistry'] = float(re.search(r'Chemistry\s*[\|\]\[]?\s*(\d+\.\d+)', text).group(1))
    except AttributeError:
        info_dict['CET_Chemistry'] = None

    try:
        info_dict['CET_Mathematics'] = float(re.search(r'Mathematics \s*[\|\[]?\s*(\d+\.\d+)', text).group(1))
    except AttributeError:
        info_dict['CET_Mathematics'] = None

    try:
        # info_dict['CET_Total'] = float(re.search(r'Total PCM (\d+\.\d+)', text).group(1))
        info_dict['CET_Total'] = float(re.search(r'Total PCM \| (\d+\.\d+)', text).group(1))
    except AttributeError:
        info_dict['CET_Total'] = None

    try:
        info_dict['JEE Main Candidate Name'] = re.search(r'Candidate Name \(as per JEE\) (.+)', text).group(1)
    except AttributeError:
        info_dict['JEE Main Candidate Name'] = None

    try:
        if(re.search(r'JEE', text)):
            info_dict['JEE Present'] = 'JEE Details Present'
    except AttributeError:
        info_dict['JEE Present'] = None

    try:
        info_dict['JEE_Physics'] = float(re.search(r'Physics\s*[\|\[]?\s*(\d+\.\d+)', text, re.DOTALL).group(1))
    except AttributeError:
        info_dict['JEE_Physics'] = None

    try:
        info_dict['JEE_Chemistry'] = float(re.search(r'Chemistry\s*[\|\]\[]?\s*(\d+\.\d+)', text, re.DOTALL).group(1))
    except AttributeError:
        info_dict['JEE_Chemistry'] = None

    try:
        info_dict['JEE_Mathematics'] = float(re.search(r'Mathematics\s*[\|\[]?\s*(\d+\.\d+)', text, re.DOTALL).group(1))
    except AttributeError:
        info_dict['JEE_Mathematics'] = None

    try:
        info_dict['JEE_Total'] = float(re.search(r'Total\s*[\|\[]?\s*(\d+\.\d+)', text).group(1))
    except AttributeError:
        info_dict['JEE_Total'] = None
    
    return info_dict

def fill_template(template_path, output_path, text_data, coordinates, font_name="Times-Roman", font_size=30):
    # Create a canvas object with the size of the PDF
    c = canvas.Canvas(output_path, pagesize=(1860, 2630))  # Adjusted to match template size

    # Draw the template PDF
    c.drawImage(template_path, 0, 0, width=1860, height=2630)  # Full size of the template

    page_height = 2630  # Total height of the page in points

    # Set font and font size
    c.setFont(font_name, font_size)

    # Fill the text data at specified coordinates
    for text, (x, y) in zip(text_data, coordinates):
        adjusted_x = x * (72 / 96)  # Adjust x coordinate
        adjusted_y = page_height - (y * (72 / 96))  # Adjust y coordinate for top-down filling
        c.drawString(adjusted_x, adjusted_y, text)

    # Save the filled PDF
    c.save()
    