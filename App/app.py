import streamlit as st
import torch
from PIL import Image
from torchvision import models

# ---------------------------------------------------------
# Page Setup & Configuration
# ---------------------------------------------------------
st.set_page_config(
    page_title="Pet Image Classifier 🐾",
    page_icon="🐾",
    layout="centered"
)

# Permanent Background GIF
PERMANENT_BG_GIF = "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExdzl5dGtmeHJvZTBkY3NmY2Y3OXBzZW43bjZsdGRzYXhiZnA0dms4ZyZlcD12MV9naWZzX3NlYXJjaCZjdD1n/vUc341wCXiY4U/giphy.gif"


def inject_custom_styles(bg_url):
    """Injects Google Fonts, frosted glass containers, vivid orange scrollbar styling, and polished card designs."""
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@500;700;800;900&family=Poppins:wght@300;400;600;700&display=swap');

        html, body, [class*="css"] {{
            font-family: 'Poppins', sans-serif;
        }}

        /* Dynamic Vibrant Orange Scrollbar */
        ::-webkit-scrollbar {{
            width: 12px;
        }}
        ::-webkit-scrollbar-track {{
            background: rgba(15, 23, 42, 0.7);
        }}
        ::-webkit-scrollbar-thumb {{
            background: linear-gradient(180deg, #FF781F, #FF9800, #F57C00);
            border-radius: 10px;
            border: 2px solid rgba(255, 255, 255, 0.25);
        }}
        ::-webkit-scrollbar-thumb:hover {{
            background: linear-gradient(180deg, #E65100, #FF6D00, #FF9800);
        }}

        /* Full page Background */
        .stApp {{
            background-image: linear-gradient(rgba(15, 23, 42, 0.70), rgba(15, 23, 42, 0.70)), url("{bg_url}");
            background-attachment: fixed;
            background-size: cover;
            background-position: center;
        }}

        /* Frosted Glass Main Container */
        .block-container {{
            background: rgba(255, 255, 255, 0.95);
            border-radius: 28px;
            padding: 40px !important;
            margin-top: 35px;
            margin-bottom: 35px;
            box-shadow: 0 20px 50px rgba(0, 0, 0, 0.5);
            backdrop-filter: blur(14px);
            border: 1px solid rgba(255, 255, 255, 0.4);
        }}

        /* Main Headings */
        .main-title {{
            font-family: 'Outfit', sans-serif;
            text-align: center;
            background: linear-gradient(135deg, #FF6B6B, #FF8E53, #4ECDC4);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 3rem;
            font-weight: 900;
            margin-bottom: 5px;
            letter-spacing: -0.5px;
        }}

        .sub-text {{
            font-family: 'Poppins', sans-serif;
            text-align: center;
            font-size: 1.1rem;
            color: #4A5568;
            font-weight: 500;
            line-height: 1.6;
            margin-bottom: 25px;
        }}

        .highlight-text {{
            color: #E53E3E;
            font-weight: 700;
        }}

        /* Results Card Design */
        .result-card {{
            border-radius: 20px;
            padding: 22px;
            text-align: center;
            color: white;
            font-family: 'Outfit', sans-serif;
            font-weight: 800;
            margin-bottom: 20px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.15);
        }}

        .result-cat {{
            background: linear-gradient(135deg, #FF6B6B, #FF8E53);
        }}

        .result-dog {{
            background: linear-gradient(135deg, #4299E1, #3182CE);
        }}

        .result-other {{
            background: linear-gradient(135deg, #ED8936, #ECC94B);
        }}

        .card-title {{
            font-size: 1.6rem;
            margin: 0;
            letter-spacing: 0.5px;
        }}

        /* Upload Box Styling */
        div[data-testid="stFileUploader"] {{
            border: 3px dashed #4ECDC4;
            border-radius: 20px;
            background: rgba(247, 250, 252, 0.9);
            padding: 15px;
            transition: all 0.3s ease;
        }}

        div[data-testid="stFileUploader"]:hover {{
            border-color: #FF6B6B;
            transform: translateY(-2px);
        }}

        /* Action Buttons */
        .stButton>button {{
            background: linear-gradient(135deg, #FF6B6B, #FF8E53);
            color: white;
            font-family: 'Outfit', sans-serif;
            font-weight: 700;
            font-size: 1.15rem;
            border-radius: 16px;
            border: none;
            padding: 12px 28px;
            width: 100%;
            transition: all 0.3s ease;
            box-shadow: 0 6px 18px rgba(255, 107, 107, 0.35);
        }}

        .stButton>button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 10px 25px rgba(255, 107, 107, 0.5);
        }}

        [data-testid="stMetricValue"] {{
            font-family: 'Outfit', sans-serif;
            font-size: 2.2rem !important;
            color: #2B6CB0;
            font-weight: 800;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )


inject_custom_styles(PERMANENT_BG_GIF)


# ---------------------------------------------------------
# AI Model & Categorization Engine
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

def classify_image(image):
    input_tensor = transform(image).unsqueeze(0)
    
    with torch.no_grad():
        outputs = model(input_tensor)
        probabilities = torch.nn.functional.softmax(outputs[0], dim=0)
    
    top5_prob, top5_catid = torch.topk(probabilities, 5)
    
    top1_score = top5_prob[0].item() * 100
    top1_label = categories[top5_catid[0].item()].lower()

    # Precise feline keywords
    cat_keywords = [
        'cat', 'tabby', 'persian cat', 'siamese cat', 'siamese', 'egyptian cat', 
        'cougar', 'lynx', 'leopard', 'panther', 'cheetah', 'jaguar', 'felis', 
        'kitten', 'marmalade cat', 'tortoiseshell', 'calico', 'manx', 'burmese'
    ]
    
    # Precise canine keywords
    dog_keywords = [
        'dog', 'retriever', 'terrier', 'spaniel', 'poodle', 'hound', 'bulldog', 
        'shepherd', 'husky', 'collie', 'pug', 'chihuahua', 'beagle', 'mutt', 
        'pinscher', 'schnauzer', 'doberman', 'rottweiler', 'corgi', 'boxer',
        'great dane', 'st. bernard', 'pomeranian', 'chow', 'basset', 'dalmatian',
        'dingo', 'wolfhound', 'elkhound', 'groenendael', 'papillon', 'whippet', 'puppy'
    ]

    # Top-3 probability breakdown
    top3_details = []
    for idx in range(3):
        top3_details.append((
            categories[top5_catid[idx].item()].title(), 
            top5_prob[idx].item() * 100
        ))

    # Primary check on top prediction
    is_top1_cat = any(kw in top1_label for kw in cat_keywords)
    is_top1_dog = any(kw in top1_label for kw in dog_keywords)

    if is_top1_cat:
        return "Cat", top1_score, top1_label, top3_details
    elif is_top1_dog:
        return "Dog", top1_score, top1_label, top3_details

    # Secondary check across top-3 candidates for cat/dog variations
    top3_labels = [categories[idx.item()].lower() for idx in top5_catid[:3]]
    is_cat_fallback = any(any(kw in lbl for kw in cat_keywords) for lbl in top3_labels)
    is_dog_fallback = any(any(kw in lbl for kw in dog_keywords) for lbl in top3_labels)

    # Only map to Cat/Dog if it is strongly indicated; otherwise strictly assign to "Other"
    if is_cat_fallback and not is_top1_dog:
        return "Cat", top1_score, top1_label, top3_details
    elif is_dog_fallback and not is_top1_cat:
        return "Dog", top1_score, top1_label, top3_details
    else:
        return "Other", top1_score, top1_label, top3_details


# ---------------------------------------------------------
# Navigation & Session State
# ---------------------------------------------------------
if 'page' not in st.session_state:
    st.session_state.page = 'upload'
if 'uploaded_file' not in st.session_state:
    st.session_state.uploaded_file = None

def go_to_results():
    st.session_state.page = 'results'

def go_to_upload():
    st.session_state.page = 'upload'
    st.session_state.uploaded_file = None


# =========================================================
# PAGE 1: UPLOAD PAGE
# =========================================================
if st.session_state.page == 'upload':
    st.markdown("<h1 class='main-title'>🐾 Pet Image Classifier 🐾</h1>", unsafe_allow_html=True)
    st.markdown(
        "<p class='sub-text'>"
        "Upload any pet image below to analyze it. "
        "The website will classify whether it is a <span class='highlight-text'>🐱 Cat</span>, "
        "<span class='highlight-text'>🐶 Dog</span>, or <span class='highlight-text'>❓ Other</span>!"
        "</p>", 
        unsafe_allow_html=True
    )

    st.divider()

    st.markdown("### 📥 Step 1: Upload Your Image")
    file = st.file_uploader(
        "Choose a pet image file (JPG, JPEG, PNG, WEBP)... 📸", 
        type=["jpg", "jpeg", "png", "webp"]
    )

    if file is not None:
        st.session_state.uploaded_file = file
        
        image = Image.open(file).convert("RGB")
        st.image(image, caption="🖼️ Image Ready for Analysis", use_container_width=True)
        
        st.write("")
        st.button("🚀 Analyze Image & View Results", on_click=go_to_results)


# =========================================================
# PAGE 2: RESULTS PAGE
# =========================================================
elif st.session_state.page == 'results':
    st.markdown("<h1 class='main-title'>🐾 Analysis Report 🐾</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-text'>Here are the classification findings from our AI model!</p>", unsafe_allow_html=True)
    
    st.divider()

    if st.session_state.uploaded_file is not None:
        image = Image.open(st.session_state.uploaded_file).convert("RGB")
        
        col1, col2 = st.columns([1, 1], gap="large")

        with col1:
            st.markdown("#### 🖼️ Image Preview")
            st.image(image, use_container_width=True)

        with col2:
            with st.spinner("🧠 Scanning visual patterns... 🔍"):
                pred_class, score, raw_label, top3_list = classify_image(image)

            # Hero Result Card
            if pred_class == "Cat":
                st.markdown(
                    """
                    <div class="result-card result-cat">
                        <p class="card-title">🐱 Specified Pet Type: CAT</p>
                    </div>
                    """, 
                    unsafe_allow_html=True
                )
            elif pred_class == "Dog":
                st.markdown(
                    """
                    <div class="result-card result-dog">
                        <p class="card-title">🐶 Specified Pet Type: DOG</p>
                    </div>
                    """, 
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    f"""
                    <div class="result-card result-other">
                        <p class="card-title">❓ Specified Pet Type: OTHER</p>
                        <p style="margin: 5px 0 0 0; font-size: 1.05rem; opacity: 0.9;">(Detected: {raw_label.title()})</p>
                    </div>
                    """, 
                    unsafe_allow_html=True
                )

            # AI Certainty Metric & Bar
            st.metric(label="🎯 Primary Match Score", value=f"{score:.2f}%")
            st.progress(min(int(score), 100))

            # Top 3 Matches
            st.markdown("---")
            st.markdown("##### 📈 Top Feature Matches:")
            for feat_name, feat_score in top3_list:
                st.write(f"**{feat_name}**: `{feat_score:.1f}%`")
                st.progress(min(int(feat_score), 100))

            st.markdown("---")
            with st.expander("🔬 View Technical Details"):
                st.write(f"🏷️ **Detected Feature:** `{raw_label.title()}`")
                st.write(f"🏷️ **Mapped Grouping:** `{pred_class}`")

        st.divider()
        st.button("🔄 Upload Another Image", on_click=go_to_upload)
    else:
        st.warning("No image found!")
        st.button("⬅️ Back to Upload Page", on_click=go_to_upload)
