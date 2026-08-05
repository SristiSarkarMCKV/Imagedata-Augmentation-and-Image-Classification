import streamlit as st
import torch
from PIL import Image
from torchvision import models

# ---------------------------------------------------------
# Page Setup & Configuration
# ---------------------------------------------------------
st.set_page_config(
    page_title="Pet Image Classifier",
    page_icon="🐾",
    layout="centered"
)

# Custom CSS for UI styling, card animations, and background tints
st.markdown("""
    <style>
    /* Main Background Accent */
    .stApp {
        background-color: #f8f9fa;
    }
    
    /* Header Styling */
    .main-title {
        text-align: center;
        color: #2E7D32;
        font-size: 2.8rem;
        font-weight: 800;
        margin-bottom: 0px;
    }
    
    .sub-writeup {
        text-align: center;
        font-size: 1.15rem;
        color: #424242;
        line-height: 1.6;
        margin-top: 10px;
        margin-bottom: 25px;
        padding: 0 15px;
    }

    /* Card Box Container */
    .report-card {
        background-color: #ffffff;
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        border: 1px solid #e0e0e0;
    }

    /* Custom File Uploader Border */
    div[data-testid="stFileUploader"] {
        background-color: #ffffff;
        border: 2px dashed #2E7D32;
        border-radius: 15px;
        padding: 15px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.03);
    }
    
    /* Center GIF alignment */
    .gif-container {
        display: flex;
        justify-content: center;
        margin-bottom: 15px;
    }
    </style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------
# Header & Intro Section (With Animated Header GIF)
# ---------------------------------------------------------
st.markdown(
    '<div class="gif-container">'
    '<img src="https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExM3Z6ZnR5eDRxZjR4eXpza3YxeThxN3BxbnJ4eGg2Z3R4ZnNxeXF3ZCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/3o72F8t9TDi2xVnxOE/giphy.gif" width="120">'
    '</div>',
    unsafe_allow_html=True
)

st.markdown("<h1 class='main-title'>Pet Image Classifier</h1>", unsafe_allow_html=True)

st.markdown(
    "<p class='sub-writeup'>"
    "Welcome! Upload an image below, and our smart AI model will automatically analyze it. "
    "Once processed, the website will specify whether the uploaded image is a <b>Cat</b>, "
    "a <b>Dog</b>, or <b>Other</b> (any object, person, or non-pet animal)."
    "</p>", 
    unsafe_allow_html=True
)

st.divider()


# ---------------------------------------------------------
# AI Model & Robust Classifier Pipeline
# ---------------------------------------------------------
@st.cache_resource
def load_classifier():
    # Pre-trained ResNet-50 model with ImageNet V2 weights
    weights = models.ResNet50_Weights.DEFAULT
    model = models.resnet50(weights=weights)
    model.eval()
    
    transform = weights.transforms()
    categories = weights.meta["categories"]
    return model, transform, categories

model, transform, categories = load_classifier()

def process_and_classify(image, confidence_threshold=0.25):
    """
    Evaluates image against comprehensive ImageNet taxonomy to accurately
    distinguish Cats, Dogs, and Other non-pet images.
    """
    input_tensor = transform(image).unsqueeze(0)
    
    with torch.no_grad():
        outputs = model(input_tensor)
        probabilities = torch.nn.functional.softmax(outputs[0], dim=0)
    
    top_prob, top_catid = torch.max(probabilities, 0)
    top_label = categories[top_catid.item()].lower()
    score = top_prob.item() * 100

    # Comprehensive taxonomy search keywords
    cat_keywords = [
        'cat', 'tabby', 'tiger cat', 'persian cat', 'siamese cat', 'siamese', 
        'egyptian cat', 'cougar', 'lynx', 'leopard', 'panther', 'cheetah', 'jaguar', 'lion'
    ]
    
    dog_keywords = [
        'dog', 'retriever', 'terrier', 'spaniel', 'poodle', 'hound', 'bulldog', 
        'shepherd', 'husky', 'collie', 'pug', 'chihuahua', 'beagle', 'mutt', 
        'pinscher', 'schnauzer', 'doberman', 'rottweiler', 'corgi', 'boxer',
        'great dane', 'st. bernard', 'pomeranian', 'chow', 'basset', 'dalmatian'
    ]

    is_cat = any(keyword in top_label for keyword in cat_keywords)
    is_dog = any(keyword in top_label for keyword in dog_keywords)

    if score < (confidence_threshold * 100):
        return "Other", score, top_label
    elif is_cat:
        return "Cat", score, top_label
    elif is_dog:
        return "Dog", score, top_label
    else:
        return "Other", score, top_label


# ---------------------------------------------------------
# Upload Tab Section
# ---------------------------------------------------------
st.markdown("### 📥 Step 1: Upload Your Image")
uploaded_file = st.file_uploader(
    "Drag and drop or choose an image file...", 
    type=["jpg", "jpeg", "png", "webp"]
)


# ---------------------------------------------------------
# Analysis & Output Report
# ---------------------------------------------------------
if uploaded_file is not None:
    st.divider()
    st.markdown("### 📊 Step 2: Analysis Report")

    image = Image.open(uploaded_file).convert("RGB")
    
    # Grid column layout
    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        st.image(image, caption="Uploaded Image", use_container_width=True)

    with col2:
        with st.spinner("🔍 AI is inspecting visual features..."):
            pred_class, score, raw_label = process_and_classify(image)

        # Result badge & animated response GIFs
        if pred_class == "Cat":
            st.success("🐱 **Specified Pet Type: CAT**")
            st.image("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExYnJ2MXhhZjh5a2R2ZnByZnRwMHFmeWpxdHZid3Rhbms4Y3gzZnB4eiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/JIX9t2j0ZTN9S/giphy.gif", width=220)
        elif pred_class == "Dog":
            st.success("🐶 **Specified Pet Type: DOG**")
            st.image("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExaG9kZDV5ZDFid3V2bnFmYmFiM3pzaHByNDR6Y2k0cnE2MThqazk0YyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/4Zo41lhzKt6iZ8xff9/giphy.gif", width=220)
        else:
            st.warning("⚠️ **Specified Pet Type: OTHER / NOT A CAT OR DOG**")
            st.image("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExM2F3OXFvNHZxdzMzbTVtd2Z6OXg3Z2VjNWN4ZGZidXpxd2xnb2s2byZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/H5C8CevNMbpBqNqFjl/giphy.gif", width=220)

        st.metric(label="Prediction Certainty", value=f"{score:.2f}%")
        st.progress(min(int(score), 100))

        # Expandable inspection box
        with st.expander("🔬 View Model Detection Details"):
            st.write(f"**Identified ImageNet Feature:** `{raw_label.title()}`")
            st.write(f"**Assigned Group:** `{pred_class}`")
