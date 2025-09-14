from flask import Flask, request, jsonify
from flask_cors import CORS
import mediapipe as mp
import cv2
import numpy as np
import os
import pickle
import base64

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize MediaPipe components
mp_drawing = mp.solutions.drawing_utils
mp_holistic = mp.solutions.holistic
mp_face_mesh = mp.solutions.face_mesh

# Load the model
with open('body_language.pkl', 'rb') as f:
    model = pickle.load(f)

@app.route('/api/health', methods=['GET'])
def health_check():
    """Check if API is running."""
    return jsonify({
        "status": "online",
        "message": "Body Language API is running"
    }), 200

@app.route('/api/predict', methods=['POST'])
def predict():
    """Predict body language from an image."""
    if 'image' not in request.files and 'image_base64' not in request.json:
        return jsonify({
            "status": "error",
            "message": "No image provided. Please upload an image file or provide a base64 encoded image."
        }), 400
    
    try:
        # Process image from file upload or base64 string
        if 'image' in request.files:
            file = request.files['image']
            image_np = np.frombuffer(file.read(), np.uint8)
            image = cv2.imdecode(image_np, cv2.IMREAD_COLOR)
        else:
            # Decode base64 image
            base64_image = request.json['image_base64']
            image_data = base64.b64decode(base64_image)
            image_np = np.frombuffer(image_data, np.uint8)
            image = cv2.imdecode(image_np, cv2.IMREAD_COLOR)
        
        # Process with MediaPipe
        with mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5) as holistic:
            # Convert to RGB
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            image_rgb.flags.writeable = False
            
            # Make detections
            results = holistic.process(image_rgb)
            
            if not results.pose_landmarks or not results.face_landmarks:
                return jsonify({
                    "status": "error",
                    "message": "No body landmarks detected in the image. Please use a clearer image with a person visible."
                }), 400
            
            # Extract landmarks
            try:
                # Extract Pose landmarks
                pose = results.pose_landmarks.landmark
                pose_row = list(np.array([[landmark.x, landmark.y, landmark.z, landmark.visibility] 
                                        for landmark in pose]).flatten())
                
                # Extract Face landmarks
                face = results.face_landmarks.landmark
                face_row = list(np.array([[landmark.x, landmark.y, landmark.z, landmark.visibility] 
                                        for landmark in face]).flatten())
                
                # Combine rows
                row = pose_row + face_row
                
                # Make prediction
                X = np.array([row])
                body_language_class = model.predict(X)[0]
                body_language_prob = model.predict_proba(X)[0]
                
                # Get the confidence for the predicted class
                confidence = round(body_language_prob[np.argmax(body_language_prob)] * 100, 2)
                
                # Return result
                return jsonify({
                    "status": "success",
                    "prediction": body_language_class,
                    "confidence": confidence,
                    "class_probabilities": {
                        class_name: round(float(prob) * 100, 2) 
                        for class_name, prob in zip(model.classes_, body_language_prob)
                    }
                }), 200
                
            except Exception as e:
                return jsonify({
                    "status": "error",
                    "message": f"Error processing landmarks: {str(e)}"
                }), 500
    
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Error processing image: {str(e)}"
        }), 500

@app.route('/api/classes', methods=['GET'])
def get_classes():
    """Get available body language classes."""
    try:
        available_classes = list(model.classes_)
        return jsonify({
            "status": "success",
            "classes": available_classes
        }), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Error retrieving classes: {str(e)}"
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
