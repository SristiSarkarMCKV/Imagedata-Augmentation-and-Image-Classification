import cv2
import numpy as np
import streamlit as st
import torch
import torch.nn as nn
from PIL import Image
from torchvision import models, transforms

# ---------------------------------------------------------
# Page Configuration
# ---------------------------------------------------------
st.set_page_config(
    page_title="Cat vs Dog Image Classifier",
    page_icon="🐾",
    layout="centered"
)


# ---------------------------------------------------------
# Model Setup & Caching
# ---------------------------------------------------------
@st.cache_resource
def load_classifier_model():
    """
    Loads a pre-trained ResNet-18 model and adjusts the final 
    layer for binary classification (Cat vs Dog).
    """
    # Load ResNet-18 with pre-trained ImageNet weights
    model = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)

    # Modify the fully connected output layer to 2 classes: [Cat, Dog]
    num_features = model.fc.in_features
    model.fc = nn.Linear(num_features, 2)

    # Set model to evaluation mode
    model.eval()
    return model


model = load_classifier_model()

# Standard ImageNet normalization and transformation pipeline
transform_pipeline = transforms.Compose([
    transforms.Resize((255, 255)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406], 
        std=[0.229, 0.224, 0.225]
    ),
])

# Class names corresponding to outputs 0 and 1
CLASS_NAMES = ["Cat", "Dog"]


# ---------------------------------------------------------
# User Interface (Streamlit)
# ---------------------------------------------------------
st.title("🐾 Image Classifier: Cat, Dog, or Other?")
st.write(
    "Upload an image below to check whether it contains a **Cat**, a **Dog**, or **Something Else**."
)

# File Uploader
uploaded_file = st.file_uploader(
    "Choose an image file (JPG, JPEG, PNG)...", 
    type=["jpg", "jpeg", "png"]
)

if uploaded_file is not None:
    # 1. Load Image using PIL
    image = Image.open(uploaded_file).convert("RGB")

    # Layout: Two columns for Display and Results
    col1, col2 = st.columns([1, 1])

    with col1:
        st.image(image, caption="Uploaded Image", use_container_width=True)

    # 2. Image Augmentation / OpenCV Integration Test (Grayscale check)
    img_np = np.array(image)
    gray_img = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)

    # 3. Model Inference
    input_tensor = transform_pipeline(image).unsqueeze(0)  # Add batch dimension

    with torch.no_grad():
        outputs = model(input_tensor)
        probabilities = torch.nn.functional.softmax(outputs[0], dim=0)

    top_prob, top_class_id = torch.max(probabilities, 0)
    confidence = top_prob.item() * 100
    predicted_label = CLASS_NAMES[top_class_id]

    # 4. Display Classification Results
    with col2:
        st.subheader("Analysis Result")

        # Thresholding for non-cat/dog items:
        # If the highest confidence score is below 70%, categorize as 'Other'
        CONFIDENCE_THRESHOLD = 70.0

        if confidence < CONFIDENCE_THRESHOLD:
            st.warning("⚠️ **Result: Other / Unsure**")
            st.write(
                f"The image does not clearly depict a Cat or Dog (Max confidence: {confidence:.1f}%)."
            )
        else:
            st.success(f"🎉 **Result: {predicted_label}**")
            st.metric(label="Confidence Level", value=f"{confidence:.2f}%")

        # Detailed probability Breakdown
        st.markdown("---")
        st.write("**Prediction Scores:**")
        for idx, class_name in enumerate(CLASS_NAMES):
            prob = probabilities[idx].item() * 100
            st.write(f"{class_name}: {prob:.2f}%")
            st.progress(int(prob))
