from flask import Flask, request, jsonify, send_from_directory, render_template
import cv2
import numpy as np
import os

app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def cartoonize_image(image_path):
    image = cv2.imread(image_path)
    # Convert to grayscale
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # Apply Gaussian Blur
    blur_image = cv2.GaussianBlur(gray_image, (3, 3), 0)
    # Adaptive Thresholding
    detect_edge = cv2.adaptiveThreshold(blur_image, 255,
                                        cv2.ADAPTIVE_THRESH_MEAN_C,
                                        cv2.THRESH_BINARY, 5, 5)
    # Bitwise AND to create the cartoon effect
    output = cv2.bitwise_and(image, image, mask=detect_edge)
    
    output_path = os.path.join(UPLOAD_FOLDER, 'cartoon_image.png')
    cv2.imwrite(output_path, output)
    return output_path

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return jsonify({"error": "No file part"})
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({"error": "No selected file"})
    
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)
    
    # Cartoonize the image
    cartoon_image_path = cartoonize_image(file_path)
    
    return jsonify({"cartoon_image": cartoon_image_path})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)
