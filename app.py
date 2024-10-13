from flask import Flask, request, jsonify, render_template_string
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
    
    # Apply bilateral filter to smooth the image while preserving edges
    smooth_image = cv2.bilateralFilter(image, d=9, sigmaColor=300, sigmaSpace=300)
    
    # Convert to grayscale
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Apply adaptive thresholding to detect edges
    edge_detected = cv2.adaptiveThreshold(gray_image, 255,
                                          cv2.ADAPTIVE_THRESH_MEAN_C,
                                          cv2.THRESH_BINARY, 9, 9)
    
    # Combine the edge-detected image with the smoothed image
    cartoon_image = cv2.bitwise_and(smooth_image, smooth_image, mask=edge_detected)

    # Optionally sharpen the image
    kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
    cartoon_image = cv2.filter2D(cartoon_image, -1, kernel)

    output_path = os.path.join(UPLOAD_FOLDER, 'cartoon_image.png')
    cv2.imwrite(output_path, cartoon_image)
    return output_path

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'image' not in request.files:
            return jsonify({"error": "No file part"}), 400
        file = request.files['image']
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400
        if file:
            # Save the uploaded file
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(image_path)

            # Process the image to cartoonize it
            cartoon_image_path = cartoonize_image(image_path)

            # Return the path of the cartoon image
            return jsonify({"cartoon_image": cartoon_image_path})

    return render_template_string('''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Make this Photo a Cartoon</title>
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
            .content {
                padding: 20px;
            }
            .content h1 {
                font-size: 24px;
                font-weight: bold;
                margin: 20px 0;
            }
            .upload-button {
                display: inline-block;
                padding: 10px 20px;
                margin: 10px 0;
                background-color: #007bff;
                color: white;
                border: none;
                border-radius: 5px;
                cursor: pointer;
            }
            .upload-button:hover {
                background-color: #0056b3;
            }
            .image-preview-box {
                display: none;
                margin-top: 20px;
            }
            #previewImage {
                max-width: 100%;
                height: auto;
            }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Photo Cartoonizer</h1>
        </div>
        <div class="content">
            <h1>Upload your image to cartoonize</h1>
            <form id="uploadForm" method="post" enctype="multipart/form-data">
                <input type="file" name="image" accept="image/*" required>
                <button type="submit" class="upload-button">Upload</button>
            </form>
            <div class="image-preview-box" id="imagePreview">
                <h2>Cartoon Image Preview:</h2>
                <img alt="Image preview" id="previewImage" src="" />
            </div>
        </div>

        <script>
            document.getElementById('uploadForm').onsubmit = function(event) {
                event.preventDefault(); // Prevent form submission
                const formData = new FormData(this);
                fetch('/', {
                    method: 'POST',
                    body: formData
                })
                .then(response => response.json())
                .then(data => {
                    if (data.cartoon_image) {
                        document.getElementById('previewImage').src = data.cartoon_image;
                        document.getElementById('imagePreview').style.display = 'block';
                    } else {
                        alert(data.error || 'Something went wrong!');
                    }
                })
                .catch(error => console.error('Error:', error));
            };
        </script>
    </body>
    </html>
    ''')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)
