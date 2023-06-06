    #!/usr/bin/env python
# -*- coding: utf-8 -*-
# Install Tesserac:
# https://github.com/UB-Mannheim/tesseract/wiki

# Importing libraries
from PIL import Image
import pytesseract
import cv2
import numpy as np

pytesseract.pytesseract.tesseract_cmd = r'C:/Users/Chaps/AppData/Local/Tesseract-OCR/tesseract.exe'

# Loading image using OpenCV
img_pathes = [
    # r"C:\Users\Chaps\Git\PythonMisc\Samples\20220915_162707.jpg",
    # r"C:\Users\Chaps\Git\PythonMisc\Samples\20220915_162707 - Copy.jpg",
    # r"C:\Users\Chaps\Git\PythonMisc\Samples\20220915_162717.jpg",
    # r"C:\Users\Chaps\Git\PythonMisc\Samples\20220915_162657.jpg",
    # r"C:\Users\Chaps\Git\PythonMisc\Samples\20220915_173322.jpg",
    r"C:\Users\Chaps\Git\PythonMisc\Samples\Screenshot 2022-09-17 213004.png",
]
for path in img_pathes:
    print("========================================================")
    print(path)
    print("========================================================")
    def process_image():
        img = Image.open(path)
        text = pytesseract.image_to_string(img)
        # text = pytesseract.image_to_string(img, lang='fra')
        print(text)
    def process_opencv():
        img = cv2.imread(path)
        # Converting to grayscale
        gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # creating Binary image by selecting proper threshold
        binary_image = cv2.threshold(gray_image, 130, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        # Inverting the image
        inverted_bin = cv2.bitwise_not(binary_image)
        # Some noise reduction
        kernel = np.ones((2, 2), np.uint8)
        processed_img = cv2.erode(inverted_bin, kernel, iterations=1)
        processed_img = cv2.dilate(processed_img, kernel, iterations=1)
        # Save image for tests
        cv2.imwrite(path[:-4] + ".PROCESSED.jpg", processed_img)
        # Read
        text = pytesseract.image_to_string(processed_img, lang='fra')
        print(text)
    def process_opencv2():
        img = cv2.imread(path)
        norm_img = np.zeros((img.shape[0], img.shape[1]))
        img = cv2.normalize(img, norm_img, 0, 255, cv2.NORM_MINMAX)
        img = cv2.threshold(img, 100, 255, cv2.THRESH_BINARY)[1]
        img = cv2.GaussianBlur(img, (1, 1), 0)
        # Save image for tests
        cv2.imwrite(path[:-4] + ".PROCESSED.jpg", img)
        # Read
        text = pytesseract.image_to_string(img, lang='fra')
        print(text)
    # process_image()
    process_opencv2()
