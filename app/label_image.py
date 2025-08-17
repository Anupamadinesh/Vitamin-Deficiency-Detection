import tensorflow as tf
import numpy as np
import cv2
import os

# Load model
model_path = "app/vitamin_deficiency_model.h5"
model = tf.keras.models.load_model(model_path)
print("✅ Model loaded successfully!")

def predict_vitamin_deficiency(image_path):
    image = cv2.imread(image_path)
    image = cv2.resize(image, (224, 224))  # Adjust based on model input size
    image = np.array(image) / 255.0
    image = np.expand_dims(image, axis=0)

    prediction = model.predict(image)
    predicted_label = np.argmax(prediction)  # Get the predicted class index

    labels = ["Vitamin A Deficiency", "Vitamin B Deficiency", "Vitamin C Deficiency", "Healthy"]
    result = labels[predicted_label]

    # Simulate clustering (you need to implement your actual clustering logic)
    clustered_image = image_path  # Replace with actual clustered image path if needed

    return result, clustered_image
