import streamlit as st
import torch
from PIL import Image
from torchvision import models, transforms

# ---------------------------------------------------------
# Page Setup & Configuration
# ---------------------------------------------------------
st.set_page_config(
    page_title="Pet Image Classifier",
    page_icon="🐾",
    layout="centered"
)

# Background GIFs
DEFAULT_BG = "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExdzl5dGtmeHJvZTBkY3NmY2Y3OXBzZW43bjZsdGRzYXhiZnA0dms4ZyZlcD12MV9naWZzX3NlYXJjaCZjdD1n/vUc341wCXiY4U/giphy.gif"
CAT_BG = "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExYnJ2MXhhZjh5a2R2ZnByZnRwMHFmeWpxdHZid3Rhbms4Y3gzZnB4eiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/JIX9t2j0ZTN9S/giphy.gif"
DOG_BG = "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExaG9kZDV5ZDFid3V2bnFmYmFiM3pzaHByNDR6Y2k0cnE2MThqazk0YyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/4Zo41lhzKt6iZ8xff9/giphy.gif"
OTHER_BG = DEFAULT_BG  # Requested general background for unknown/other


def apply_custom_styles_and_bg(bg_url):
    """Injects Google Fonts, Glassmorphism UI styling, and Dynamic Backgrounds."""
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;800&family=Poppins:wght@300;400;600;700&display=swap');

        /* Global Page Styling */
        html, body, [class*="css"] {{
            font-family: 'Poppins', sans-serif;
        }}

        .stApp {{
            background-image: linear-gradient(rgba(0, 0, 0, 0.55), rgba(0, 0, 0, 0.55)), url("{bg_url}");
            background-attachment: fixed;
            background-size: cover;
            background-position: center;
        }}

        /* Central Glass Card */
        .block-container {{
            background: rgba(255, 255, 255, 0.92);
            border-radius: 24px;
            padding: 35px !important;
            margin-top: 30px;
            margin-bottom: 30px;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.4);
            backdrop-filter: blur(10px);
        }}

        /* Typography Styling */
        .main-title {{
            font-family: 'Outfit', sans-serif;
            text-align: center;
            background: linear-gradient(135deg, #0D47A1, #1976D2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 3rem;
            font-weight: 800;
            margin-bottom: 5px;
            letter-spacing: -0.5px;
        }}

        .sub-text {{
            font-family: 'Poppins', sans-serif;
            text-align: center;
            font-size: 1.15rem;
            color: #37474F;
            font-weight: 400;
            line-height: 1.6;
            margin-bottom: 25px;
        }}

        /* File Uploader Custom Border */
        div[data-testid="stFileUploader"] {{
            border: 2.5px dashed #1976D2;
            border-radius: 16px;
            background: rgba(255, 255, 255, 0.8);
            padding: 10px;
        }}

        /* Metric Typography */
        [data-testid="stMetricValue"] {{
            font-family: 'Outfit', sans-serif;
            font-size: 2.2rem !important;
            color: #0D47A1;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )


# Apply Default Background on Startup
apply_custom_styles_and_bg(DEFAULT_BG)


# ---------------------------------------------------------
# Header Section
# ---------------------------------------------------------
st.markdown("<h1 class='main-title'>Pet Image Classifier</h1>", unsafe_allow_html=True)
st.markdown(
    "<p class='sub-text'>"
    "Once the image is uploaded, the type of pet—whether it is a <b>Cat</b>, <b>Dog</b>, "
    "or <b>Other</b>—will be specified by the website."
    "</p>", 
    unsafe_allow_html=True
)

st.divider()


# ---------------------------------------------------------
# Robust Classification Engine
# ---------------------------------------------------------
@st.cache_resource
def load_model():
    weights = models.ResNet50_Weights.DEFAULT
    model = models.resnet50(weights=weights)
    model.eval()
    
    transform = weights.transforms()
    categories = weights.meta["categories"]
    return model, transform, categories

model, transform, categories = load_model()

def classify_pet_image(image, confidence_threshold=0.20):
    """
    Evaluates top ImageNet probabilities across exhaustive cat and dog 
    taxonomies to ensure both species are accurately predicted.
    """
    input_tensor = transform(image).unsqueeze(0)
    
    with torch.no_grad():
        outputs = model(input_tensor)
        probabilities = torch.nn.functional.softmax(outputs[0], dim=0)
    
    top_prob, top_catid = torch.max(probabilities, 0)
    top_label = categories[top_catid.item()].lower()
    score = top_prob.item() * 100

    # Exhaustive Cat Taxonomy Keywords (Covers domestic breeds & ImageNet labels)
    cat_keywords = [
        'cat', 'tabby', 'tiger cat', 'persian cat', 'siamese cat', 'siamese', 
        'egyptian cat', 'cougar', 'lynx', 'leopard', 'panther', 'cheetah', 
        'jaguar', 'lion', 'angora', 'lynx', 'felis'
    ]
    
    # Exhaustive Dog Taxonomy Keywords
    dog_keywords = [
        'dog', 'retriever', 'terrier', 'spaniel', 'poodle', 'hound', 'bulldog', 
        'shepherd', 'husky', 'collie', 'pug', 'chihuahua', 'beagle', 'mutt', 
        'pinscher', 'schnauzer', 'doberman', 'rottweiler', 'corgi', 'boxer',
        'great dane', 'st. bernard', 'pomeranian', 'chow', 'basset', 'dalmatian',
        'dingo', 'wolfhound', 'elkhound', 'groenendael', 'papillon', 'whippet'
    ]

    is_cat = any(kw in top_label for kw in cat_keywords)
    is_dog = any(kw in top_label for kw in dog_keywords)

    if score < (confidence_threshold * 100):
        return "Other", score, top_label
    elif is_cat:
        return "Cat", score, top_label
    elif is_dog:
        return "Dog", score, top_label
    else:
        return "Other", score, top_label


# ---------------------------------------------------------
# Image Upload Section
# ---------------------------------------------------------
uploaded_file = st.file_uploader(
    "Upload a Pet Image...", 
    type=["jpg", "jpeg", "png", "webp"]
)


# ---------------------------------------------------------
# Analysis & Dynamic Output Section
# ---------------------------------------------------------
if uploaded_file is not None:
    st.divider()
    st.subheader("📋 Analysis Report")

    image = Image.open(uploaded_file).convert("RGB")
    
    col1, col2 = st.columns([1, 1], gap="medium")

    with col1:
        st.image(image, caption="Uploaded Image", use_container_width=True)

    with col2:
        with st.spinner("Analyzing pet features..."):
            pred_class, score, raw_label = classify_pet_image(image)

        # Dynamic Background and Alert Badges
        if pred_class == "Cat":
            apply_custom_styles_and_bg(CAT_BG)
            st.success("🐱 **Specified Pet Type: CAT**")
        elif pred_class == "Dog":
            apply_custom_styles_and_bg(DOG_BG)
            st.success("🐶 **Specified Pet Type: DOG**")
        else:
            apply_custom_styles_and_bg(OTHER_BG)
            st.warning("⚠️ **Specified Pet Type: OTHER / UNKNOWN**")

        st.metric(label="Model Certainty Score", value=f"{score:.2f}%")
        st.progress(min(int(score), 100))

        st.markdown("---")
        with st.expander("🔍 View Technical Details"):
            st.write(f"**Identified ImageNet Feature:** `{raw_label.title()}`")
            st.write(f"**Mapped Category:** `{pred_class}`")
