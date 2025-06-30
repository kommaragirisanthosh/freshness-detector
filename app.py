from flask import Flask, render_template, request, jsonify
import os
from werkzeug.utils import secure_filename
import cv2
import numpy as np
from datetime import datetime, timedelta

app = Flask(__name__)

# Configure upload folder
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def analyze_freshness(image_path):
    """Simulate freshness analysis based on image processing"""
    try:
        # Load the image
        img = cv2.imread(image_path)
        
        if img is None:
            return {"error": "Could not read the image"}
        
        # Convert to HSV color space
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        
        # Calculate color metrics (simplified for demo)
        mean_saturation = np.mean(hsv[:,:,1])
        mean_value = np.mean(hsv[:,:,2])
        
        # Simple freshness estimation (this would be more complex in a real system)
        freshness_score = (mean_saturation + mean_value) / 2
        
        # Determine freshness level
        if freshness_score > 160:
            freshness = "Very Fresh"
            shelf_life = "7-10 days"
        elif freshness_score > 120:
            freshness = "Fresh"
            shelf_life = "4-6 days"
        elif freshness_score > 80:
            freshness = "Moderate"
            shelf_life = "2-3 days"
        else:
            freshness = "Not Fresh"
            shelf_life = "Consume immediately"
        
        # Calculate expiration date (simplified)
        expiration_date = (datetime.now() + timedelta(days=int(shelf_life.split('-')[0]))).strftime('%Y-%m-%d')
        
        return {
            "freshness": freshness,
            "score": round(freshness_score, 2),
            "shelf_life": shelf_life,
            "expiration_date": expiration_date,
            "color_saturation": round(mean_saturation, 2),
            "brightness": round(mean_value, 2)
        }
    
    except Exception as e:
        return {"error": str(e)}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"})
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"})
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Analyze the image
        result = analyze_freshness(filepath)
        
        # Add image path to result
        result['image_path'] = filepath
        
        return jsonify(result)
    
    return jsonify({"error": "File type not allowed"})

if __name__ == '__main__':
    app.run(debug=True)