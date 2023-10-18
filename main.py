import datetime
import os
import time
import numpy as np
import pyperclip
import re
import cv2
from PIL import Image, ImageEnhance, ImageGrab, ImageOps
from pytesseract import pytesseract

timestamp = None
global pics_dir_path
pics_dir_path = None
dir_path = os.path.dirname(os.path.realpath(__file__))
pics_dir_path = os.path.join(dir_path, "pics")
# Add pics file if not exist
if not os.path.exists(pics_dir_path):
    os.makedirs(pics_dir_path)
pyperclip.copy(' ') # Set the clipboard contents to an empty string
empty_clipboard_text = pyperclip.paste()
# Set the clipboard contents to an empty string
print("Hello World!")


def enhance_image(image):
    # Upscale
    image = upscale_and_set_dpi(image, scale_factor=5.0, dpi=300)

    # Convert PIL Image to OpenCV format
    img_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

    # Convert to LAB color space
    lab = cv2.cvtColor(img_cv, cv2.COLOR_BGR2Lab)

    # Split LAB into L, A and B channels
    l_channel, a_channel, b_channel = cv2.split(lab)

    # Apply CLAHE to L channel
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    cl = clahe.apply(l_channel)
    
    # Merge the CLAHE enhanced L channel with the original A and B channel
    merged_channels = cv2.merge([cl, a_channel, b_channel])

    # Convert back from LAB to BGR
    enhanced_img_cv = cv2.cvtColor(merged_channels, cv2.COLOR_Lab2BGR)

    # Convert back to PIL format
    enhanced_image = Image.fromarray(cv2.cvtColor(enhanced_img_cv, cv2.COLOR_BGR2RGB))
    
    return image

def upscale_and_set_dpi(image, scale_factor=2.0, method='bicubic', dpi=300):
    """Upscales the image using the specified method and sets the DPI"""
    
    # Convert PIL Image to OpenCV format
    img_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    
    new_width = int(img_cv.shape[1] * scale_factor)
    new_height = int(img_cv.shape[0] * scale_factor)
    dim = (new_width, new_height)

    if method == 'bicubic':
        upscaled_img_cv = cv2.resize(img_cv, dim, interpolation=cv2.INTER_CUBIC)
    elif method == 'lanczos':
        upscaled_img_cv = cv2.resize(img_cv, dim, interpolation=cv2.INTER_LANCZOS4)
    else:
        raise ValueError("Invalid upscaling method. Choose 'bicubic' or 'lanczos'.")

    # Convert back to PIL format
    upscaled_image = Image.fromarray(cv2.cvtColor(upscaled_img_cv, cv2.COLOR_BGR2RGB))
    
    # Set DPI
    upscaled_image.info['dpi'] = (dpi, dpi)

    return upscaled_image



def save_image(image):
    """Saves the image to the 'pics' directory and returns the path"""
    global timestamp
    timestamp = str(time.time()).replace(".", "")
    image_path = os.path.join(pics_dir_path, f"{timestamp}_clipboard_image.png")
    image.save(image_path, "PNG")
    return image_path


def save_text(text):
    """Saves the OCR output to a file and copies it to the clipboard"""
    pyperclip.copy(text)
    with open(os.path.join(pics_dir_path, f"{timestamp}_clipboard_text.txt"), 'w') as f:
        f.write(text)
    current_time = datetime.datetime.now().strftime("%H:%M:%S")
    print("[{}] OCR output has been copied to the clipboard.".format(current_time))

def ocr_me(image, image_path):
    # time.sleep(1)
    ocr_text = pytesseract.image_to_string(image, lang='eng', config="--psm 6 --oem 3 -c tessedit_char_whitelist= *0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!@#$%^&*()_+-={}[]|\:;<>,.?/~`")
    # Clean up the text
    ocr_text = re.sub(r'[^\x00-\x7F]+', '', ocr_text)
    # ocr_text = pytesseract.image_to_string(image, lang='eng', config="--psm 6 --oem 3")
    return ocr_text

while True:
    # Wait for a new image to be pasted into the clipboard
    pyperclip.waitForNewPaste()
    # time.sleep(0.25)

    # Get the image from the clipboard
    image = ImageGrab.grabclipboard()

    if image:
        image = enhance_image(image)
        image_path = save_image(image)
        ########################################OCR-OCR-CCR#############################################
        ocr_text = ocr_me(image, image_path)
        ########################################OCR-OCR-CCR#############################################
        save_text(ocr_text)
        # time.sleep(0.01)
    else:
        current_time = datetime.datetime.now().strftime("%H:%M:%S")
        print("[{}] No image found in the clipboard.".format(current_time))












