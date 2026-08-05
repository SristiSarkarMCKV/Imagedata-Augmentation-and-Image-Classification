import streamlit as st
import torch
from PIL import Image
from torchvision import models
import streamlit.components.v1 as components

# ---------------------------------------------------------
# Page Setup & Configuration
# ---------------------------------------------------------
st.set_page_config(
    page_title="Pet Image Classifier 🐾",
    page_icon="🐾",
    layout="centered"
)

PERMANENT_BG_GIF = "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExdzl5dGtmeHJvZTBkY3NmY2Y3OXBzZW43bjZsdGRzYXhiZnA0dms4ZyZlcD12MV9naWZzX3NlYXJjaCZjdD1n/vUc341wCXiY4U/giphy.gif"


def inject_custom_styles(bg_url):
    """Injects custom CSS styling safely."""
    css = (
        "<style>\n"
        "@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@500;700;800;900&family=Poppins:wght@300;400;600;700&display=swap');\n"
        "html, body, [class*='css'] { font-family: 'Poppins', sans-serif; }\n"
        "::-webkit-scrollbar { width: 12px; }\n"
        "::-webkit-scrollbar-track { background: rgba(15, 23, 42, 0.7); }\n"
        "::-webkit-scrollbar-thumb { background: linear-gradient(180deg, #FF781F, #FF9800, #F57C00); border-radius: 10px; border: 2px solid rgba(255, 255, 255, 0.25); }\n"
        "::-webkit-scrollbar-thumb:hover { background: linear-gradient(180deg, #E65100, #FF6D00, #FF9800); }\n"
        ".stApp { background-image: linear-gradient(rgba(15, 23, 42, 0.70), rgba(15, 23, 42, 0.70)), url('" + bg_url + "'); background-attachment: fixed; background-size: cover; background-position: center; }\n"
        ".block-container { background: rgba(255, 255, 255, 0.95); border-radius: 28px; padding: 40px !important; margin-top: 35px; margin-bottom: 35px; box-shadow: 0 20px 50px rgba(0, 0, 0, 0.5); backdrop-filter: blur(14px); border: 1px solid rgba(255, 255, 255, 0.4); }\n"
        ".main-title { font-family: 'Outfit', sans-serif; text-align: center; background: linear-gradient(135deg, #FF6B6B, #FF8E53, #4ECDC4); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 2.7rem; font-weight: 900; margin-bottom: 5px; letter-spacing: -0.5px; }\n"
        ".sub-text { font-family: 'Poppins', sans-serif; text-align: center; font-size: 1.05rem; color: #4A5568; font-weight: 500; line-height: 1.6; margin-bottom: 25px; }\n"
        ".highlight-text { color: #E53E3E; font-weight: 700; }\n"
        "div[data-testid='stRadio'] > div { justify-content: center; gap: 15px; }\n"
        "div[data-testid='stRadio'] label { background: rgba(240, 244, 248, 0.8); border: 1px solid #CBD5E0; border-radius: 12px; padding: 8px 18px; font-family: 'Outfit', sans-serif; font-weight: 700; transition: all 0.2s ease-in-out; }\n"
        "div[data-testid='stRadio'] label:hover { border-color: #FF6B6B; background: #FFFFFF; }\n"
        ".feature-card { background: #F7FAFC; border-radius: 16px; padding: 20px; border-left: 5px solid #4ECDC4; height: 100%; box-shadow: 0 4px 12px rgba(0,0,0,0.05); }\n"
        ".feature-card-title { font-family: 'Outfit', sans-serif; font-weight: 800; color: #2D3748; font-size: 1.15rem; margin-bottom: 8px; }\n"
        ".feature-card-desc { color: #718096; font-size: 0.9rem; line-height: 1.5; }\n"
        ".diagram-container { background: #FFFFFF; padding: 15px; border-radius: 16px; border: 1px solid #E2E8F0; margin-bottom: 25px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); overflow-x: auto; }\n"
        ".result-card { border-radius: 20px; padding: 22px; text-align: center; color: white; font-family: 'Outfit', sans-serif; font-weight: 800; margin-bottom: 20px; box-shadow: 0 10px 25px rgba(0,0,0,0.15); }\n"
        ".result-cat { background: linear-gradient(135deg, #FF6B6B, #FF8E53); }\n"
        ".result-dog { background: linear-gradient(135deg, #4299E1, #3182CE); }\n"
        ".result-other { background: linear-gradient(135deg, #ED8936, #ECC94B); }\n"
        ".card-title { font-size: 1.6rem; margin: 0; letter-spacing: 0.5px; }\n"
        "div[data-testid='stFileUploader'] { border: 3px dashed #4ECDC4; border-radius: 20px; background: rgba(247, 250, 252, 0.9); padding: 15px; transition: all 0.3s ease; }\n"
        "div[data-testid='stFileUploader']:hover { border-color: #FF6B6B; transform: translateY(-2px); }\n"
        ".stButton>button { background: linear-gradient(135deg, #FF6B6B, #FF8E53); color: white; font-family: 'Outfit', sans-serif; font-weight: 700; font-size: 1.15rem; border-radius: 16px; border: none; padding: 12px 28px; width: 100%; transition: all 0.3s ease; box-shadow: 0 6px 18px rgba(255, 107, 107, 0.35); }\n"
        ".stButton>button:hover { transform: translateY(-2px); box-shadow: 0 10px 25px rgba(255, 107, 107, 0.5); }\n"
        "[data-testid='stMetricValue'] { font-family: 'Outfit', sans-serif; font-size: 2.2rem !important; color: #2B6CB0; font-weight: 800; }\n"
        "</style>"
    )
    st.markdown(css, unsafe_allow_html=True)


def render_mermaid(code):
    """Renders landscape Mermaid.js diagram with large crisp fonts."""
    html = (
        "<!DOCTYPE html><html><head>"
        "<script type='module'>"
        "import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';"
        "mermaid.initialize({ startOnLoad: true, theme: 'neutral', flowchart: { useMaxWidth: true, htmlLabels: true } });"
        "</script>"
        "<style>"
        "body { margin: 0; padding: 0; display: flex; justify-content: center; align-items: center; background: transparent; overflow: hidden; }"
        ".mermaid { width: 100%; display: flex; justify-content: center; }"
        ".mermaid svg { width: 100% !important; height: auto !important; min-height: 250px; font-size: 13px !important; }"
        "</style>"
        "</head><body><div class='mermaid'>" + code + "</div></body></html>"
    )
    components.html(html, height=280, scrolling=False)


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

    cat_keywords = [
        'cat', 'tabby', 'persian cat', 'siamese cat', 'siamese', 'egyptian cat', 
        'cougar', 'lynx', 'leopard', 'panther', 'cheetah', 'jaguar', 'felis', 
        'kitten', 'marmalade cat', 'tortoiseshell', 'calico', 'manx', 'burmese'
    ]
    
    dog_keywords = [
        'dog', 'retriever', 'terrier', 'spaniel', 'poodle', 'hound', 'bulldog', 
        'shepherd', 'husky', 'collie', 'pug', 'chihuahua', 'beagle', 'mutt', 
        'pinscher', 'schnauzer', 'doberman', 'rottweiler', 'corgi', 'boxer',
        'great dane', 'st. bernard', 'pomeranian', 'chow', 'basset', 'dalmatian',
        'dingo', 'wolfhound', 'elkhound', 'groenendael', 'papillon', 'whippet', 'puppy'
    ]

    top3_details = []
    for idx in range(3):
        top3_details.append((
            categories[top5_catid[idx].item()].title(), 
            top5_prob[idx].item() * 100
        ))

    is_top1_cat = any(kw in top1_label for kw in cat_keywords)
    is_top1_dog = any(kw in top1_label for kw in dog_keywords)

    if is_top1_cat:
        return "Cat", top1_score, top1_label, top3_details
    elif is_top1_dog:
        return "Dog", top1_score, top1_label, top3_details

    top3_labels = [categories[idx.item()].lower() for idx in top5_catid[:3]]
    is_cat_fallback = any(any(kw in lbl for kw in cat_keywords) for lbl in top3_labels)
    is_dog_fallback = any(any(kw in lbl for kw in dog_keywords) for lbl in top3_labels)

    if is_cat_fallback and not is_top1_dog:
        return "Cat", top1_score, top1_label, top3_details
    elif is_dog_fallback and not is_top1_cat:
        return "Dog", top1_score, top1_label, top3_details
    else:
        return "Other", top1_score, top1_label, top3_details


# ---------------------------------------------------------
# Global Navigation Header & State Management
# ---------------------------------------------------------
st.markdown("<h1 class='main-title'>🐾 Pet Image Classifier 🐾</h1>", unsafe_allow_html=True)

if 'nav' not in st.session_state:
    st.session_state.nav = '🏠 Home'
if 'page' not in st.session_state:
    st.session_state.page = 'upload'
if 'uploaded_file' not in st.session_state:
    st.session_state.uploaded_file = None

def go_to_results():
    st.session_state.page = 'results'

def go_to_upload():
    st.session_state.page = 'upload'
    st.session_state.uploaded_file = None

def switch_to_prediction():
    st.session_state.nav = '🔮 Prediction'

nav_choice = st.radio(
    "",
    ["🏠 Home", "🔮 Prediction", "ℹ️ About"],
    horizontal=True,
    key='nav'
)

st.divider()

# =========================================================
# PAGE 1: HOME PAGE
# =========================================================
if nav_choice == "🏠 Home":
    st.markdown("### 🧬 Automated Deep Learning Pet Recognition Engine")
    
    st.markdown(
        "<p style='color: #4A5568; font-size: 1rem; line-height: 1.7;'>"
        "Welcome! This application utilizes state-of-the-art Deep Computer Vision to instantly analyze "
        "identify and classify uploaded images. Built on top of a 50-layer Deep Residual Neural Network "
        "(ResNet50) the system evaluates visual feature representations across 1,000 object categories "
        "and intelligently maps them into concise pet classifications: 🐱 <b>Cat</b> 🐶 <b>Dog</b> or ❓ <b>Other</b>."
        "</p>", 
        unsafe_allow_html=True
    )
    
    st.markdown("#### ⚙️ Classification System Architecture & Workflow")
    
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.markdown(
            '<div class="feature-card" style="border-left-color: #FF6B6B;">'
            '<div class="feature-card-title">1. Input Preprocessing</div>'
            '<div class="feature-card-desc">Raw image frames are normalized color-space corrected (RGB) dynamic-resized to 224x224 and converted into PyTorch tensors.</div>'
            '</div>', unsafe_allow_html=True
        )
    with col_b:
        st.markdown(
            '<div class="feature-card" style="border-left-color: #4ECDC4;">'
            '<div class="feature-card-title">2. ResNet50 Inference</div>'
            '<div class="feature-card-desc">Visual feature extraction occurs across deep convolutional bottleneck blocks evaluating edge pattern activations.</div>'
            '</div>', unsafe_allow_html=True
        )
    with col_c:
        st.markdown(
            '<div class="feature-card" style="border-left-color: #4299E1;">'
            '<div class="feature-card-title">3. Logic & Classification</div>'
            '<div class="feature-card-desc">Softmax output logits map top predictions into species groupings calculating confidence metrics.</div>'
            '</div>', unsafe_allow_html=True
        )

    st.write("")
    st.markdown("#### 📊 Visual Workflow Diagram")
    
    # Updated to LR (Left to Right) for wide, clear, horizontal layout
    mermaid_code = """
    graph LR
        Start("📥 Upload Image") --> Read("📸 Read RGB")
        Read --> Resize("📏 Resize 224x224")
        Resize --> Normalize("⚖️ Normalize Tensors")
        Normalize --> Model("🧠 ResNet50 Model")
        Model --> Softmax("📈 Probabilities")
        Softmax --> Top1{"❓ Cat or Dog?"}
        Top1 -- Yes --> Final("🏁 Cat / Dog")
        Top1 -- No --> Other("🏁 Other Class")

        classDef process fill:#E2E8F0,stroke:#718096,stroke-width:1.5px,rx:6,ry:6;
        classDef model fill:#C4F1F9,stroke:#00B5D8,stroke-width:2px,rx:10,ry:10,color:#000;
        classDef decision fill:#FEEBC8,stroke:#DD6B20,stroke-width:1.5px,color:#000;
        classDef endNode fill:#C6F6D5,stroke:#38A169,stroke-width:2px,rx:8,ry:8,color:#000;

        class Start,Read,Resize,Normalize,Softmax process;
        class Model model;
        class Top1 decision;
        class Final,Other endNode;
    """
    
    st.markdown('<div class="diagram-container">', unsafe_allow_html=True)
    render_mermaid(mermaid_code)
    st.markdown('</div>', unsafe_allow_html=True)

    st.write("")
    st.markdown("#### 🎯 Core Capabilities Highlight")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("**⚡ Instant Analysis**\n\nHigh-speed tensor processing delivering real-time predictions.")
    with col2:
        st.success("**🔬 Deep Traversal**\n\nExamines top candidate probability distributions for sub-breed identification.")
    with col3:
        st.warning("**🛡️ Smart Grouping**\n\nFallback categorization logic ensuring precise non-pet filters.")

    st.write("")
    st.button("🚀 Launch Image Classifier Engine", on_click=switch_to_prediction)


# =========================================================
# PAGE 2: PREDICTION PAGE
# =========================================================
elif nav_choice == "🔮 Prediction":
    if st.session_state.page == 'upload':
        st.markdown(
            "<p class='sub-text'>"
            "Upload any pet image below to analyze it. "
            "The model will classify whether it is a <span class='highlight-text'>🐱 Cat</span> "
            "<span class='highlight-text'>🐶 Dog</span> or <span class='highlight-text'>❓ Other</span>!"
            "</p>", 
            unsafe_allow_html=True
        )

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

    elif st.session_state.page == 'results':
        st.markdown("<h2 style='text-align: center; font-family: Outfit, sans-serif;'>📋 Analysis Report</h2>", unsafe_allow_html=True)
        st.markdown("<p class='sub-text'>Here are the classification findings from our AI model!</p>", unsafe_allow_html=True)
        
        if st.session_state.uploaded_file is not None:
            image = Image.open(st.session_state.uploaded_file).convert("RGB")
            
            col1, col2 = st.columns([1, 1], gap="large")

            with col1:
                st.markdown("#### 🖼️ Image Preview")
                st.image(image, use_container_width=True)

            with col2:
                with st.spinner("🧠 Scanning visual patterns... 🔍"):
                    pred_class, score, raw_label, top3_list = classify_image(image)

                if pred_class == "Cat":
                    st.markdown('<div class="result-card result-cat"><p class="card-title">🐱 Specified Pet Type: CAT</p></div>', unsafe_allow_html=True)
                elif pred_class == "Dog":
                    st.markdown('<div class="result-card result-dog"><p class="card-title">🐶 Specified Pet Type: DOG</p></div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="result-card result-other"><p class="card-title">❓ Specified Pet Type: OTHER</p><p style="margin: 5px 0 0 0; font-size: 1.05rem; opacity: 0.9;">(Detected: {raw_label.title()})</p></div>', unsafe_allow_html=True)

                st.metric(label="🎯 Primary Match Score", value=f"{score:.2f}%")
                st.progress(min(int(score), 100))

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

# =========================================================
# PAGE 3: ABOUT PAGE
# =========================================================
elif nav_choice == "ℹ️ About":
    st.markdown("### ℹ️ About the Model & Technology")
    st.markdown(
        """
        #### 🤖 Model Architecture: ResNet-50
        This system leverages **ResNet-50** a residual deep learning neural network architecture with 50 layers. 
        Residual connections resolve the vanishing gradient problem enabling the network to learn rich feature representations.

        #### 📚 Dataset & Categorization Mapping
        - Pre-trained on **ImageNet-1k** (containing over 1 million images across 1,000 classes).
        - Includes extensive sub-categories ranging from specific dog breeds (*Golden Retriever Pembroke Welsh Corgi Siberian Husky*) to feline variants (*Siamese Persian Tabby*).
        - Logic filters aggregate specific breed detection tokens into clean easy-to-read **Cat** **Dog** or **Other** umbrella designations.

        #### 💻 Tech Stack
        * **Framework:** PyTorch & Torchvision
        * **Frontend:** Streamlit Custom UI
        * **Image Preprocessing:** PIL (Python Imaging Library)
        """
    )

st.markdown("---")
st.caption("⚠️ **Disclaimer:** This tool is intended for demonstration purposes. Classification confidence depends on image quality lighting and frame composition.")
