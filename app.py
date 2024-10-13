from flask import Flask, request, jsonify
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
    return '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Make this Photo to Cartoon</title>
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.3/css/all.min.css" rel="stylesheet"/>
        <style>
            body {
                font-family: Arial, sans-serif;
                text-align: center;
                margin: 0;
                padding: 0;
                background-color: #f8f9fa;
            }
            .header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 10px 20px;
                background-color: #ffffff;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            }
            .header img {
                height: 40px;
            }
            .header .menu-icon {
                font-size: 24px;
            }
            .content {
                padding: 20px;
            }
            .content h1 {
                font-size: 24px;
                font-weight: bold;
                margin: 20px 0;
            }
            .content p {
                font-size: 18px;
                margin: 10px 0;
            }
            .content .highlight {
                background-color: #ffeb3b;
                padding: 2px 6px;
                border-radius: 4px;
            }
            .upload-button {
                display: inline-block;
                background-color: #007bff;
                color: #ffffff;
                padding: 15px 30px;
                font-size: 18px;
                border-radius: 25px;
                text-decoration: none;
                margin: 20px 0;
            }
            .image-suggestions {
                display: flex;
                justify-content: center;
                gap: 10px;
                margin: 20px 0;
            }
            .image-suggestions img {
                width: 60px;
                height: 60px;
                border-radius: 8px;
            }
            .image-preview-box {
                border: 2px dashed #007bff;
                padding: 20px;
                margin: 20px 0;
                border-radius: 10px;
                background-color: #ffffff;
                display: none;  /* Hide by default */
            }
            .image-preview-box img {
                max-width: 100%;
                border-radius: 10px;
            }
        </style>
    </head>
    <body>
        <div class="header">
            <img alt="Logo" height="40" src="https://storage.googleapis.com/a1aa/image/3lS5IXarPqIzKldK5eq9Yse0sz3McK2QqYdsJvlMR4yb5VmTA.jpg" width="40"/>
            <i class="fas fa-bars menu-icon"></i>
        </div>
        <div class="content">
            <h1>Make this Photo to Cartoon</h1>
            <p>100% Automatically and <span class="highlight">Free</span></p>
            <form id="uploadForm">
                <input type="file" name="image" accept="image/*" required>
                <button type="submit" class="upload-button">Upload Image</button>
            </form>
            <p>No image? Try one of these:</p>
            <div class="image-suggestions">
                <img alt="Sample image 1" src="https://storage.googleapis.com/a1aa/image/ViCvG3CefrnQp0cyn34yozLy9qVaZ4stFIIYCbRhSbwY5VmTA.jpg" />
                <img alt="Sample image 2" src="https://storage.googleapis.com/a1aa/image/kXnhaYEh0mqLBZc22O6n8pa2uv7i7AeAEDtfGwubnPMa5VmTA.jpg" />
                <img alt="Sample image 3" src="https://storage.googleapis.com/a1aa/image/fN8dtVsyMRytRyPBnTgrkVHq44GL4xHIBziwuXEzPkav8KzJA.jpg" />
                <img alt="Sample image 4" src="https://storage.googleapis.com/a1aa/image/F1xUAyM9Rho3PRRF34Q8ZAGA4VqgLGi5T6Z9qD9z38GXeKzJA.jpg" />
            </div>
            <div class="image-preview-box" id="imagePreview">
                <img alt="Image preview" id="previewImage" src="" />
            </div>
        </div>
        <script>
            document.getElementById('uploadForm').addEventListener('submit', function(event) {
                event.preventDefault();  // Prevent form submission

                let formData = new FormData(this);
                fetch('/upload', {
                    method: 'POST',
                    body: formData
                })
                .then(response => response.json())
                .then(data => {
                    if (data.cartoon_image) {
                        // Display the cartoonized image
                        document.getElementById('previewImage').src = data.cartoon_image;
                        document.getElementById('imagePreview').style.display = 'block';  // Show the preview box
                    } else {
                        alert('Image processing failed. Please try again.');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                });
            });
        </script>
    </body>
    </html>
    '''

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
