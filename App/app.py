import base64
import streamlit as st
import torch
from PIL import Image
from torchvision import models

# ---------------------------------------------------------
# Page Setup & Base Configuration
# ---------------------------------------------------------
st.set_page_config(
    page_title="Pet Image Classifier",
    page_icon="🐾",
    layout="centered"
)

# Background GIFs / Images URLs
DEFAULT_BG = "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExdzl5dGtmeHJvZTBkY3NmY2Y3OXBzZW43bjZsdGRzYXhiZnA0dms4ZyZlcD12MV9naWZzX3NlYXJjaCZjdD1n/vUc341wCXiY4U/giphy.gif" # Representative image from uploaded pet media
CAT_BG = "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExYnJ2MXhhZjh5a2R2ZnByZnRwMHFmeWpxdHZid3Rhbms4Y3gzZnB4eiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/JIX9t2j0ZTN9S/giphy.gif"
DOG_BG = "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExaG9kZDV5ZDFid3V2bnFmYmFiM3pzaHByNDR6Y2k0cnE2MThqazk0YyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/4Zo41lhzKt6iZ8xff9/giphy.gif"
OTHER_BG = "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExM2F3OXFvNHZxdzMzbTVtd2Z6OXg3Z2VjNWN4ZGZidXpxd2xnb2s2byZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/H5C8CevNMbpBqNqFjl/giphy.gif"

def set_dynamic_background(bg_url):
    """Injects CSS to update the full-page background dynamically."""
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: linear-gradient(rgba(0, 0, 0, 0.45), rgba(0, 0, 0, 0.45)), url("{bg_url}");
            background-attachment: fixed;
            background-size: cover;
            background-position: center;
        }}
        
        /* Container Glassmorphism Styling */
        .block-container {{
            background: rgba(255, 255, 255, 0.88);
            border-radius: 20px;
            padding: 30px !important;
            margin-top: 40px;
            margin-bottom: 40px;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
            backdrop-filter: blur(8px);
            -webkit-backdrop-filter: blur(8px);
        }}

        .main-title {{
            text-align: center;
            color: #1A237E;
            font-size: 2.8rem;
            font-weight: 800;
            margin-bottom: 5px;
        }}

        .sub-writeup {{
            text-align: center;
            font-size: 1.1rem;
            color: #333333;
            line-height: 1.6;
            margin-bottom: 25px;
        }}

        div[data-testid="stFileUploader"] {{
            border: 2px dashed #1A237E;
            border-radius: 12px;
            background-color: rgba(255, 255, 255, 0.9);
        }}
        </style>
        """,
        unsafe_allow_html=True
    )


# Set initial default background
set_dynamic_background(DEFAULT_BG)

# ---------------------------------------------------------
# Header & Instructions
# ---------------------------------------------------------
st.markdown("<h1 class='main-title'>Pet Image Classifier</h1>", unsafe_allow_html=True)

st.markdown(
    "<p class='sub-writeup'>"
    "Once the image is uploaded, the type of pet—whether it is a <b>Cat</b>, <b>Dog</b>, "
    "or <b>Other</b>—will be specified by the website."
    "</p>", 
    unsafe_allow_html=True
)

st.divider()


# ---------------------------------------------------------
# Model Loading & Classification Logic
# ---------------------------------------------------------
@st.cache_resource
def load_classifier():
    weights = models.ResNet50_Weights.DEFAULT
    model = models.resnet50(weights=weights)
    model.eval()
    
    transform = weights.transforms()
    categories = weights.meta["categories"]
    return model, transform, categories

model, transform, categories = load_classifier()

def process_and_classify(image, confidence_threshold=0.25):
    input_tensor = transform(image).unsqueeze(0)
    
    with torch.no_grad():
        outputs = model(input_tensor)
        probabilities = torch.nn.functional.softmax(outputs[0], dim=0)
    
    top_prob, top_catid = torch.max(probabilities, 0)
    top_label = categories[top_catid.item()].lower()
    score = top_prob.item() * 100

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
# File Upload Tab
# ---------------------------------------------------------
uploaded_file = st.file_uploader(
    "Upload an image of a pet or object...", 
    type=["jpg", "jpeg", "png", "webp"]
)


# ---------------------------------------------------------
# Analysis Report & Dynamic GIF Change
# ---------------------------------------------------------
if uploaded_file is not None:
    st.divider()
    st.markdown("### 📊 Analysis Report")

    image = Image.open(uploaded_file).convert("RGB")
    
    col1, col2 = st.columns([1, 1], gap="medium")

    with col1:
        st.image(image, caption="Uploaded Image", use_container_width=True)

    with col2:
        with st.spinner("Analyzing visual features..."):
            pred_class, score, raw_label = process_and_classify(image)

        # Dynamic Background update based on prediction
        if pred_class == "Cat":
            set_dynamic_background(CAT_BG)
            st.success("🐱 **Specified Pet Type: CAT**")
        elif pred_class == "Dog":
            set_dynamic_background(DOG_BG)
            st.success("🐶 **Specified Pet Type: DOG**")
        else:
            set_dynamic_background(OTHER_BG)
            st.warning("⚠️ **Specified Pet Type: OTHER / UNKNOWN**")

        st.metric(label="Prediction Certainty", value=f"{score:.2f}%")
        st.progress(min(int(score), 100))

        with st.expander("🔬 Technical Details"):
            st.write(f"**Primary Feature Detected:** `{raw_label.title()}`")
            st.write(f"**Classification Category:** `{pred_class}`")
