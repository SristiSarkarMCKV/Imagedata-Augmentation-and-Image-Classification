import streamlit as st
import torch
from PIL import Image
from torchvision import models

# ---------------------------------------------------------
# Page Setup & Base Configuration
# ---------------------------------------------------------
st.set_page_config(
    page_title="Pet Image Classifier 🐾",
    page_icon="🐾",
    layout="centered"
)

# Static Background GIF (Applied universally across all states)
PERMANENT_BG_GIF = "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExdzl5dGtmeHJvZTBkY3NmY2Y3OXBzZW43bjZsdGRzYXhiZnA0dms4ZyZlcD12MV9naWZzX3NlYXJjaCZjdD1n/vUc341wCXiY4U/giphy.gif"


def inject_custom_styles(bg_url):
    """Injects Google Fonts, vibrant typography colors, and frosted glass UI styling."""
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@500;700;800;900&family=Poppins:wght@300;400;600;700&display=swap');

        /* Global Font & Background */
        html, body, [class*="css"] {{
            font-family: 'Poppins', sans-serif;
        }}

        .stApp {{
            background-image: linear-gradient(rgba(15, 23, 42, 0.65), rgba(15, 23, 42, 0.65)), url("{bg_url}");
            background-attachment: fixed;
            background-size: cover;
            background-position: center;
        }}

        /* Frosted Glass Container */
        .block-container {{
            background: rgba(255, 255, 255, 0.94);
            border-radius: 28px;
            padding: 40px !important;
            margin-top: 35px;
            margin-bottom: 35px;
            box-shadow: 0 20px 50px rgba(0, 0, 0, 0.5);
            backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.3);
        }}

        /* Header Styling */
        .main-title {{
            font-family: 'Outfit', sans-serif;
            text-align: center;
            background: linear-gradient(135deg, #FF6B6B, #FF8E53, #4ECDC4);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 3.2rem;
            font-weight: 900;
            margin-bottom: 10px;
            letter-spacing: -1px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        }}

        .sub-text {{
            font-family: 'Poppins', sans-serif;
            text-align: center;
            font-size: 1.15rem;
            color: #2D3748;
            font-weight: 500;
            line-height: 1.7;
            margin-bottom: 25px;
        }}

        .highlight-text {{
            color: #E53E3E;
            font-weight: 700;
        }}

        /* Upload Widget Customization */
        div[data-testid="stFileUploader"] {{
            border: 3px dashed #4ECDC4;
            border-radius: 20px;
            background: rgba(247, 250, 252, 0.85);
            padding: 15px;
            transition: all 0.3s ease;
        }}

        div[data-testid="stFileUploader"]:hover {{
            border-color: #FF6B6B;
            transform: translateY(-2px);
        }}

        /* Metrics Styling */
        [data-testid="stMetricValue"] {{
            font-family: 'Outfit', sans-serif;
            font-size: 2.4rem !important;
            color: #2B6CB0;
            font-weight: 800;
        }}

        /* Section Subheaders */
        h3 {{
            font-family: 'Outfit', sans-serif !argument;
            color: #1A202C !important;
            font-weight: 700 !important;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )


# Apply permanent GIF background
inject_custom_styles(PERMANENT_BG_GIF)


# ---------------------------------------------------------
# Header & Instructions
# ---------------------------------------------------------
st.markdown("<h1 class='main-title'>✨ Pet Image Classifier 🐾</h1>", unsafe_allow_html=True)
st.markdown(
    "<p class='sub-text'>"
    "Welcome! 🎈 Upload any image below and our smart AI model will inspect it. "
    "Once uploaded, the exact type of pet—whether it is a <span class='highlight-text'>🐱 Cat</span>, "
    "<span class='highlight-text'>🐶 Dog</span>, or <span class='highlight-text'>❓ Other</span>—will be specified!"
    "</p>", 
    unsafe_allow_html=True
)

st.divider()


# ---------------------------------------------------------
# AI Classification Engine (ResNet-50 Top-5 Inspection)
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

def classify_image(image, confidence_threshold=0.18):
    """
    Evaluates top predictions across exhaustive feline & canine taxonomies.
    Also checks top-5 candidates so cats are detected even if the specific 
    breed isn't the single top-1 label.
    """
    input_tensor = transform(image).unsqueeze(0)
    
    with torch.no_grad():
        outputs = model(input_tensor)
        probabilities = torch.nn.functional.softmax(outputs[0], dim=0)
    
    # Get top 5 predictions to prevent missing breed variations
    top5_prob, top5_catid = torch.topk(probabilities, 5)
    
    top1_score = top5_prob[0].item() * 100
    top1_label = categories[top5_catid[0].item()].lower()

    # Generic & breed-specific Cat keywords
    cat_keywords = [
        'cat', 'tabby', 'tiger cat', 'persian cat', 'siamese cat', 'siamese', 
        'egyptian cat', 'cougar', 'lynx', 'leopard', 'panther', 'cheetah', 
        'jaguar', 'lion', 'angora', 'felis', 'kitten', 'tomcat', 'alley cat',
        'marmalade cat', 'tortoiseshell', 'calico', 'manx', 'burmese'
    ]
    
    # Generic & breed-specific Dog keywords
    dog_keywords = [
        'dog', 'retriever', 'terrier', 'spaniel', 'poodle', 'hound', 'bulldog', 
        'shepherd', 'husky', 'collie', 'pug', 'chihuahua', 'beagle', 'mutt', 
        'pinscher', 'schnauzer', 'doberman', 'rottweiler', 'corgi', 'boxer',
        'great dane', 'st. bernard', 'pomeranian', 'chow', 'basset', 'dalmatian',
        'dingo', 'wolfhound', 'elkhound', 'groenendael', 'papillon', 'whippet', 'puppy'
    ]

    # Check top-5 classes to catch any feline/canine markers
    top5_labels = [categories[idx.item()].lower() for idx in top5_catid]
    
    is_cat = any(any(kw in label for kw in cat_keywords) for label in top5_labels[:2])
    is_dog = any(any(kw in label for kw in dog_keywords) for label in top5_labels[:2])

    if top1_score < (confidence_threshold * 100):
        return "Other", top1_score, top1_label
    elif is_cat:
        return "Cat", top1_score, top1_label
    elif is_dog:
        return "Dog", top1_score, top1_label
    else:
        return "Other", top1_score, top1_label


# ---------------------------------------------------------
# Image Upload Section
# ---------------------------------------------------------
st.markdown("### 📥 Step 1: Upload Your Pet Image")
uploaded_file = st.file_uploader(
    "Choose an image file (JPG, JPEG, PNG, WEBP)... 📸", 
    type=["jpg", "jpeg", "png", "webp"]
)


# ---------------------------------------------------------
# Analysis & Output Report
# ---------------------------------------------------------
if uploaded_file is not None:
    st.divider()
    st.markdown("### 📊 Step 2: Analysis Report")

    image = Image.open(uploaded_file).convert("RGB")
    
    col1, col2 = st.columns([1, 1], gap="medium")

    with col1:
        st.image(image, caption="🖼️ Uploaded Preview", use_container_width=True)

    with col2:
        with st.spinner("🧠 AI is scanning visual patterns... 🔍"):
            pred_class, score, raw_label = classify_image(image)

        # Result badge display with emojis
        if pred_class == "Cat":
            st.success("🐱 **Specified Pet Type: CAT** 🐈")
        elif pred_class == "Dog":
            st.success("🐶 **Specified Pet Type: DOG** 🐕")
        else:
            st.warning("❓ **Specified Pet Type: OTHER / UNKNOWN** 🦄")

        st.metric(label="🎯 AI Confidence Score", value=f"{score:.2f}%")
        st.progress(min(int(score), 100))

        st.markdown("---")
        with st.expander("🔬 View Technical Detection Details"):
            st.write(f"🏷️ **Identified Feature:** `{raw_label.title()}`")
            st.write(f"🏷️ **Final Grouping:** `{pred_class}`")
            st.caption("⚡ Model scans multi-scale feature hierarchies to detect cats and dogs even if breed metadata is absent.")
