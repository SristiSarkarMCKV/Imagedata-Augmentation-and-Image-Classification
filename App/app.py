import streamlit as st
import torch
from PIL import Image
from torchvision import models
import streamlit.components.v1 as components
import requests
from io import BytesIO

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
    """Injects robust CSS styling using uniform wrapper spacing and vertical centering to eliminate top sticking."""
    css = (
        "<style>\n"
        "@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@500;700;800;900&family=Poppins:wght@300;400;600;700&display=swap');\n"
        "html, body, [class*='css'] { font-family: 'Poppins', sans-serif; }\n"
        
        "/* HIDE STREAMLIT LINK/ANCHOR ICONS NEXT TO HEADINGS */\n"
        "[data-testid='stHeaderActionElements'], .stHeadingAnchor, a.data-testid-stHeaderActionElements, .css-1544g2n { display: none !important; visibility: hidden !important; }\n"
        "h1 a, h2 a, h3 a, h4 a, h5 a, h6 a { display: none !important; opacity: 0 !important; }\n"
        "a[href*='#'] { display: none !important; }\n"

        "::-webkit-scrollbar { width: 12px; }\n"
        "::-webkit-scrollbar-track { background: rgba(15, 23, 42, 0.7); }\n"
        "::-webkit-scrollbar-thumb { background: linear-gradient(180deg, #FF781F, #FF9800, #F57C00); border-radius: 10px; border: 2px solid rgba(255, 255, 255, 0.25); }\n"
        "::-webkit-scrollbar-thumb:hover { background: linear-gradient(180deg, #E65100, #FF6D00, #FF9800); }\n"
        
        "/* FULL VIEWPORT CENTERING FOR STAPP */\n"
        ".stApp {\n"
        "  background-image: linear-gradient(rgba(15, 23, 42, 0.75), rgba(15, 23, 42, 0.75)), url('" + bg_url + "');\n"
        "  background-attachment: fixed;\n"
        "  background-size: cover;\n"
        "  background-position: center;\n"
        "  min-height: 100vh;\n"
        "  display: flex;\n"
        "  align-items: center;\n"
        "  justify-content: center;\n"
        "}\n"
        
        "/* Main Adaptive Glassmorphism Container - Middle Aligned */\n"
        ".block-container {\n"
        "  background: rgba(255, 255, 255, 0.95);\n"
        "  color: #1A202C;\n"
        "  border-radius: 28px;\n"
        "  padding: 24px 20px !important;\n"
        "  margin: auto !important;\n"
        "  max-width: 720px;\n"
        "  width: 100%;\n"
        "  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.5);\n"
        "  backdrop-filter: blur(14px);\n"
        "  border: 1px solid rgba(255, 255, 255, 0.4);\n"
        "}\n"

        "/* UNIFORM SECTION WRAPPER TO FORCE CONSISTENT GAPS */\n"
        ".content-section {\n"
        "  margin-top: 100px !important;\n"
        "  margin-bottom: 0px !important;\n"
        "}\n"

        "div.element-container {\n"
        "  margin-bottom: 0px !important;\n"
        "  margin-top: 10px !important;\n"
        "}\n"
        "div[data-testid='stVerticalBlock'] {\n"
        "  gap: 0.4rem !important;\n"
        "}\n"
        "h3 {\n"
        "  margin-top: 10px !important;\n"
        "  margin-bottom: 0.3rem !important;\n"
        "}\n"
        "h4 {\n"
        "  margin-top: 10px !important;\n"
        "  margin-bottom: 0.3rem !important;\n"
        "}\n"
        "p {\n"
        "  margin-bottom: 0.3rem !important;\n"
        "  margin-top: 0px !important;\n"
        "}\n"

        "/* FIX CONTRAST FOR ALL CALLOUT BOXES (info, success, warning) */\n"
        "div[data-testid='stAlert'] { color: #1A202C !important; font-weight: 500; border-radius: 12px; margin-bottom: 0.3rem !important; margin-top: 0.2rem !important; }\n"
        "div[data-testid='stAlert'] p { color: #1A202C !important; font-weight: 500; }\n"
        "div[data-testid='stAlert'] strong { color: #000000 !important; font-weight: 800; }\n"
        
        "/* Dark Mode Overrides */\n"
        "@media (prefers-color-scheme: dark) {\n"
        "  .block-container {\n"
        "    background: rgba(15, 23, 42, 0.92) !important;\n"
        "    color: #F7FAFC !important;\n"
        "    border: 1px solid rgba(255, 255, 255, 0.15);\n"
        "  }\n"
        "  .sub-text { color: #E2E8F0 !important; }\n"
        "  .feature-card { background: #1E293B !important; border-color: #334155 !important; }\n"
        "  .feature-card-title { color: #F8FAFC !important; }\n"
        "  .feature-card-desc { color: #CBD5E0 !important; }\n"
        "  div[data-testid='stRadio'] label { background: rgba(30, 41, 59, 0.9) !important; color: #F1F5F9 !important; border-color: #475569 !important; }\n"
        "  p, span, label, h1, h2, h3, h4, h5, h6 { color: #F1F5F9 !important; }\n"
        "  div[data-testid='stAlert'] { background-color: #1E293B !important; color: #F1F5F9 !important; border-color: #475569 !important; }\n"
        "  div[data-testid='stAlert'] p { color: #F1F5F9 !important; }\n"
        "  div[data-testid='stAlert'] strong { color: #FFFFFF !important; }\n"
        "}\n"

        ".main-title { font-family: 'Outfit', sans-serif; text-align: center; background: linear-gradient(135deg, #FF6B6B, #FF8E53, #4ECDC4); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 2rem; font-weight: 900; margin-bottom: 0px; padding-bottom: 0px; letter-spacing: -0.5px; }\n"
        ".sub-text { font-family: 'Poppins', sans-serif; text-align: center; font-size: 0.9rem; color: #4A5568; font-weight: 500; line-height: 1.3; margin-bottom: 6px; }\n"
        ".highlight-text { color: #FF6B6B; font-weight: 700; }\n"
        
        "div[data-testid='stRadio'] > div { justify-content: center; gap: 8px; border: none !important; margin-bottom: 2px; margin-top: 2px; }\n"
        "div[data-testid='stRadio'] label { background: rgba(240, 244, 248, 0.85); border: 1px solid #CBD5E0; border-radius: 10px; padding: 3px 12px; font-family: 'Outfit', sans-serif; font-weight: 700; transition: all 0.2s ease-in-out; color: #2D3748; }\n"
        "div[data-testid='stRadio'] label:hover { border-color: #FF6B6B; background: #FFFFFF; }\n"
        
        ".feature-card { background: #F8FAFC; border-radius: 10px; padding: 10px; border-left: 4px solid #4ECDC4; height: 100%; box-shadow: 0 4px 12px rgba(0,0,0,0.04); }\n"
        ".feature-card-title { font-family: 'Outfit', sans-serif; font-weight: 800; color: #2D3748; font-size: 0.95rem; margin-bottom: 2px; }\n"
        ".feature-card-desc { color: #4A5568; font-size: 0.82rem; line-height: 1.35; }\n"
        
        ".result-card { border-radius: 16px; padding: 14px; text-align: center; color: white !important; font-family: 'Outfit', sans-serif; font-weight: 800; margin-bottom: 10px; box-shadow: 0 8px 20px rgba(0,0,0,0.15); }\n"
        ".result-card p { color: white !important; }\n"
        ".result-cat { background: linear-gradient(135deg, #FF6B6B, #FF8E53); }\n"
        ".result-dog { background: linear-gradient(135deg, #4299E1, #3182CE); }\n"
        ".result-other { background: linear-gradient(135deg, #ED8936, #ECC94B); }\n"
        ".card-title { font-size: 1.25rem; margin: 0; letter-spacing: 0.5px; color: #FFFFFF !important; }\n"
        
        "div[data-testid='stFileUploader'] { border: 2px dashed #4ECDC4; border-radius: 14px; background: rgba(247, 250, 252, 0.4); padding: 8px; transition: all 0.3s ease; }\n"
        "div[data-testid='stFileUploader']:hover { border-color: #FF6B6B; transform: translateY(-1px); }\n"
        
        "/* FORCE FIXED ASPECT RATIO CONTAINER FOR UNIFORM SAMPLE IMAGE SIZES & PREVENT OVERLAPS */\n"
        ".sample-img-container { width: 100%; height: 85px; overflow: hidden; border-radius: 8px; display: flex; align-items: center; justify-content: center; background: #000000; margin-bottom: 2px; }\n"
        ".sample-img-container img { width: 100%; height: 100%; object-fit: cover; }\n"

        ".stButton>button { background: linear-gradient(135deg, #FF6B6B, #FF8E53); color: white !important; font-family: 'Outfit', sans-serif; font-weight: 700; font-size: 0.72rem; border-radius: 8px; border: none; padding: 4px 6px; width: 100%; min-height: 38px; line-height: 1.1; transition: all 0.3s ease; box-shadow: 0 4px 14px rgba(255, 107, 107, 0.35); }\n"
        ".stButton>button:hover { transform: translateY(-1px); box-shadow: 0 8px 20px rgba(255, 107, 107, 0.5); }\n"
        
        "[data-testid='stMetricValue'] { font-family: 'Outfit', sans-serif; font-size: 1.6rem !important; color: #3182CE !important; font-weight: 800; }\n"
        "hr { margin: 6px 0 !important; border-color: #E2E8F0 !important; }\n"
        "ul { list-style-type: none !important; padding-left: 0 !important; }\n"
        "li { padding: 1px 0; }\n"
        "</style>"
    )
    st.markdown(css, unsafe_allow_html=True)


def render_css_flowchart():
    """Renders theme-adaptive visual workflow diagram with dynamic resize injection so height adjusts cleanly without gaps."""
    html_code = """
    <!DOCTYPE html>
    <html>
    <head>
      <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: 'Poppins', sans-serif; background: transparent; padding: 0px; overflow: hidden; }
        
        :root {
          --bg-section: #F8FAFC;
          --border-color: #E2E8F0;
          --title-color: #4A5568;
          --node-gray-bg: #FFFFFF;
          --node-gray-border: #CBD5E0;
          --node-gray-text: #2D3748;
          --arrow-color: #CBD5E0;
        }

        @media (prefers-color-scheme: dark) {
          :root {
            --bg-section: #1E293B;
            --border-color: #334155;
            --title-color: #CBD5E0;
            --node-gray-bg: #0F172A;
            --node-gray-border: #475569;
            --node-gray-text: #F1F5F9;
            --arrow-color: #64748B;
          }
        }

        .flow-wrapper { display: flex; flex-direction: column; gap: 6px; width: 100%; min-width: 280px; }
        .flow-section { background: var(--bg-section); border: 1px solid var(--border-color); border-radius: 10px; padding: 6px 8px; }
        .section-title { font-size: 0.75rem; font-weight: 800; color: var(--title-color); text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 4px; }
        .stage-box { display: flex; gap: 8px; align-items: center; }
        .stage-img { width: 55px; height: 55px; border-radius: 6px; object-fit: cover; border: 2px solid var(--node-gray-border); flex-shrink: 0; }
        .step-grid { display: flex; flex-wrap: wrap; gap: 4px; align-items: center; flex: 1; }
        .node { padding: 5px 6px; border-radius: 6px; font-size: 0.73rem; font-weight: 600; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 2px; box-shadow: 0 1px 3px rgba(0,0,0,0.03); flex: 1 1 auto; min-width: 75px; text-align: center; }
        .node-gray { background: var(--node-gray-bg); border: 1.5px solid var(--node-gray-border); color: var(--node-gray-text); }
        .node-blue { background: #EBF8FF; border: 1.5px solid #90CDF4; color: #2B6CB0; }
        .node-orange { background: #FFFAF0; border: 1.5px solid #FBD38D; color: #C05621; }
        .node-green { background: #F0FFF4; border: 1.5px solid #9AE6B4; color: #276749; }
        .cat-img-box { width: 34px; height: 34px; border-radius: 4px; object-fit: cover; border: 1px solid #CBD5E0; margin-top: 1px; }
        .arrow { color: var(--arrow-color); font-weight: bold; font-size: 0.75rem; }
        .down-arrow { text-align: center; font-size: 0.8rem; color: var(--arrow-color); margin: -3px 0; }
      </style>
    </head>
    <body>
      <div id="content-body" class="flow-wrapper">
        <div class="flow-section">
          <div class="section-title">1️⃣ Input & Image Preprocessing</div>
          <div class="stage-box">
            <img class="stage-img" src="https://images.unsplash.com/photo-1548199973-03cce0bbc87b?w=200&auto=format&fit=crop&q=80" alt="Gallery"/>
            <div class="step-grid">
              <div class="node node-gray">📥 Gallery</div>
              <div class="arrow">➔</div>
              <div class="node node-gray">📸 RGB</div>
              <div class="arrow">➔</div>
              <div class="node node-gray">📏 224x224</div>
              <div class="arrow">➔</div>
              <div class="node node-gray">⚖️ Normalize</div>
            </div>
          </div>
        </div>
        <div class="down-arrow">⬇️</div>
        <div class="flow-section">
          <div class="section-title">2️⃣ Deep Neural Network (ResNet-50)</div>
          <div class="stage-box">
            <img class="stage-img" src="https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=200&auto=format&fit=crop&q=80" alt="ResNet"/>
            <div class="step-grid">
              <div class="node node-blue">🧠 Features</div>
              <div class="arrow">➔</div>
              <div class="node node-blue">⚡ Conv Layers</div>
              <div class="arrow">➔</div>
              <div class="node node-blue">📈 Softmax</div>
            </div>
          </div>
        </div>
        <div class="down-arrow">⬇️</div>
        <div class="flow-section">
          <div class="section-title">3️⃣ Categorization & Prediction Output</div>
          <div class="stage-box">
            <div class="step-grid" style="width: 100%;">
              <div class="node node-orange">❓ Mapping</div>
              <div class="arrow">➔</div>
              <div class="node node-green"><span>🐱 Cat</span><img class="cat-img-box" src="https://images.unsplash.com/photo-1514888286974-6c03e2ca1dba?w=100&auto=format&fit=crop&q=80"/></div>
              <div class="node node-green"><span>🐶 Dog</span><img class="cat-img-box" src="https://images.unsplash.com/photo-1543466835-00a7907e9de1?w=100&auto=format&fit=crop&q=80"/></div>
              <div class="node node-green"><span>❓ Other</span><img class="cat-img-box" src="https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=100&auto=format&fit=crop&q=80"/></div>
            </div>
          </div>
        </div>
      </div>

      <script>
        function sendHeight() {
          const bodyHeight = document.getElementById('content-body').scrollHeight + 10;
          window.parent.postMessage({ type: 'streamlit:setFrameHeight', height: bodyHeight }, '*');
        }
        window.addEventListener('load', sendHeight);
        window.addEventListener('resize', sendHeight);
        setTimeout(sendHeight, 100);
      </script>
    </body>
    </html>
    """
    components.html(html_code, height=360, scrolling=False)


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

    cat_keywords = ['cat', 'tabby', 'persian cat', 'siamese cat', 'siamese', 'egyptian cat', 'cougar', 'lynx', 'leopard', 'panther', 'cheetah', 'jaguar', 'felis', 'kitten', 'marmalade cat', 'tortoiseshell', 'calico', 'manx', 'burmese']
    dog_keywords = ['dog', 'retriever', 'terrier', 'spaniel', 'poodle', 'hound', 'bulldog', 'shepherd', 'husky', 'collie', 'pug', 'chihuahua', 'beagle', 'mutt', 'pinscher', 'schnauzer', 'doberman', 'rottweiler', 'corgi', 'boxer', 'great dane', 'st. bernard', 'pomeranian', 'chow', 'basset', 'dalmatian', 'dingo', 'wolfhound', 'elkhound', 'groenendael', 'papillon', 'whippet', 'puppy']

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
if 'source_mode' not in st.session_state:
    st.session_state.source_mode = 'Upload Image'
if 'selected_sample_url' not in st.session_state:
    st.session_state.selected_sample_url = None

def switch_to_prediction():
    st.session_state.nav = '🔮 Prediction'

nav_choice = st.radio(
    "",
    ["🏠 Home", "🔮 Prediction", "ℹ️ About"],
    horizontal=True,
    key='nav',
    label_visibility="collapsed"
)

# =========================================================
# PAGE 1: HOME PAGE
# =========================================================
if nav_choice == "🏠 Home":
    st.markdown("### 🧬 Automated Deep Learning Pet Recognition Engine")
    st.markdown(
        "<p style='font-size: 0.9rem; line-height: 1.4;'>"
        "Welcome! This application utilizes state-of-the-art Deep Computer Vision to instantly analyze "
        "and classify uploaded images. Built on top of a 50-layer Deep Residual Neural Network "
        "(ResNet50) the system evaluates visual feature representations across 1,000 object categories "
        "and intelligently maps them into concise pet classifications: 🐱 <b>Cat</b> 🐶 <b>Dog</b> or ❓ <b>Other</b>."
        "</p>", 
        unsafe_allow_html=True
    )
    
    st.markdown('<div class="content-section">', unsafe_allow_html=True)
    st.markdown("### ⚙️ Classification System Architecture & Workflow")
    st.markdown('</div>', unsafe_allow_html=True)

    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.markdown('<div class="feature-card" style="border-left-color: #FF6B6B;"><div class="feature-card-title">1. Preprocessing</div><div class="feature-card-desc">Raw image frames are normalized color-space corrected (RGB) resized and converted into PyTorch tensors.</div></div>', unsafe_allow_html=True)
    with col_b:
        st.markdown('<div class="feature-card" style="border-left-color: #4ECDC4;"><div class="feature-card-title">2. ResNet50 Inference</div><div class="feature-card-desc">Visual feature extraction occurs across deep convolutional bottleneck blocks evaluating edge patterns.</div></div>', unsafe_allow_html=True)
    with col_c:
        st.markdown('<div class="feature-card" style="border-left-color: #4299E1;"><div class="feature-card-title">3. Logic & Classification</div><div class="feature-card-desc">Softmax output logits map top predictions into species groupings calculating confidence metrics.</div></div>', unsafe_allow_html=True)

    st.markdown('<div class="content-section">', unsafe_allow_html=True)
    st.markdown("#### 📊 Visual Workflow Diagram")
    st.markdown('</div>', unsafe_allow_html=True)
    render_css_flowchart()

    st.markdown('<div class="content-section">', unsafe_allow_html=True)
    st.markdown("#### 🎯 Core Capabilities Highlight")
    st.markdown('</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("**⚡ Instant Analysis**\n\nHigh-speed tensor processing delivering real-time predictions.")
    with col2:
        st.success("**🔬 Deep Traversal**\n\nExamines top candidate probability distributions for sub-breed identification.")
    with col3:
        st.warning("**🛡️ Smart Grouping**\n\nFallback categorization logic ensuring precise non-pet filters.")

    st.markdown('<div class="content-section">', unsafe_allow_html=True)
    st.button("🚀 Launch Image Classifier Engine", on_click=switch_to_prediction)
    st.markdown('</div>', unsafe_allow_html=True)


# =========================================================
# PAGE 2: PREDICTION PAGE
# =========================================================
elif nav_choice == "🔮 Prediction":
    if st.session_state.page == 'upload':
        st.markdown(
            "<p class='sub-text'>"
            "Select a source and choose or upload an image to analyze. "
            "The model will classify whether it is a <span class='highlight-text'>🐱 Cat</span> "
            "<span class='highlight-text'>🐶 Dog</span> or <span class='highlight-text'>❓ Other</span>"
            "</p>", 
            unsafe_allow_html=True
        )

        st.markdown("**Source:**")
        st.session_state.source_mode = st.radio(
            "Source",
            ["Upload Image", "Sample Images"],
            horizontal=True,
            key='source_mode_radio',
            label_visibility="collapsed"
        )

        if st.session_state.source_mode == "Upload Image":
            st.markdown("### 📥 Upload Your Image")
            file = st.file_uploader(
                "Choose a pet image file (JPG, JPEG, PNG, WEBP)", 
                type=["jpg", "jpeg", "png", "webp"],
                label_visibility="collapsed"
            )

            if file is not None:
                st.session_state.uploaded_file = file
                image = Image.open(file).convert("RGB")
                st.image(image, caption="🖼️ Image Ready for Analysis", use_container_width=True)
                def go_to_results(): st.session_state.page = 'results'
                st.button("🚀 Analyze Image and View Results", on_click=go_to_results)

        else:
            st.markdown("### Select a Sample Image:")
            
            sample_images = {
                "SAMPLE 1": "https://images.unsplash.com/photo-1514888286974-6c03e2ca1dba?w=400&auto=format&fit=crop&q=80",
                "SAMPLE 2": "https://images.unsplash.com/photo-1543466835-00a7907e9de1?w=400&auto=format&fit=crop&q=80",
                "SAMPLE 3": "https://images.unsplash.com/photo-1513360371669-4adf3dd7dff8?w=400&auto=format&fit=crop&q=80",
                "SAMPLE 4": "https://images.unsplash.com/photo-1589941013453-ec89f33b5e95?w=400&auto=format&fit=crop&q=80",
                "SAMPLE 5": "https://images.unsplash.com/photo-1573865526739-10659fec78a5?w=400&auto=format&fit=crop&q=80",
                "SAMPLE 6": "https://images.unsplash.com/photo-1537151608828-ea2b11777ee8?w=400&auto=format&fit=crop&q=80",
                "SAMPLE 7": "https://images.unsplash.com/photo-1561948955-570b270e7c36?w=400&auto=format&fit=crop&q=80",
                "SAMPLE 8": "https://images.unsplash.com/photo-1548199973-03cce0bbc87b?w=400&auto=format&fit=crop&q=80"
            }

            cols = st.columns(4)
            sample_keys = list(sample_images.keys())
            
            for i in range(4):
                with cols[i]:
                    st.markdown(f"<div style='text-align: center; font-weight: 700; font-size: 0.72rem; margin-bottom: 2px;'>{sample_keys[i]}</div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='sample-img-container'><img src='{sample_images[sample_keys[i]]}' /></div>", unsafe_allow_html=True)
                    if st.button(f"🚀 Analyze {sample_keys[i]}", key=f"btn_{i}"):
                        st.session_state.selected_sample_url = sample_images[sample_keys[i]]

            cols_row2 = st.columns(4)
            for i in range(4, 8):
                with cols_row2[i-4]:
                    st.markdown(f"<div style='text-align: center; font-weight: 700; font-size: 0.72rem; margin-bottom: 2px;'>{sample_keys[i]}</div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='sample-img-container'><img src='{sample_images[sample_keys[i]]}' /></div>", unsafe_allow_html=True)
                    if st.button(f"🚀 Analyze {sample_keys[i]}", key=f"btn_{i}"):
                        st.session_state.selected_sample_url = sample_images[sample_keys[i]]

            if st.session_state.selected_sample_url:
                try:
                    response = requests.get(st.session_state.selected_sample_url)
                    st.session_state.uploaded_file = BytesIO(response.content)
                    st.session_state.page = 'results'
                    st.rerun()
                except Exception as e:
                    st.error(f"Error loading sample image: {e}")

    elif st.session_state.page == 'results':
        st.markdown("<h2 style='text-align: center; font-family: Outfit, sans-serif;'>📋 Analysis Report</h2>", unsafe_allow_html=True)
        st.markdown("<p class='sub-text'>Here are the classification findings from our AI model</p>", unsafe_allow_html=True)
        
        if st.session_state.uploaded_file is not None:
            image = Image.open(st.session_state.uploaded_file).convert("RGB")
            col1, col2 = st.columns([1, 1], gap="medium")

            with col1:
                st.markdown("#### 🖼️ Image Preview")
                st.image(image, use_container_width=True)

            with col2:
                with st.spinner("🧠 Scanning visual patterns..."):
                    pred_class, score, raw_label, top3_list = classify_image(image)

                if pred_class == "Cat":
                    st.markdown('<div class="result-card result-cat"><p class="card-title">🐱 Specified Pet Type: CAT</p></div>', unsafe_allow_html=True)
                elif pred_class == "Dog":
                    st.markdown('<div class="result-card result-dog"><p class="card-title">🐶 Specified Pet Type: DOG</p></div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="result-card result-other"><p class="card-title">❓ Specified Pet Type: OTHER</p><p style="margin: 2px 0 0 0; font-size: 0.9rem; opacity: 0.9;">(Detected: {raw_label.title()})</p></div>', unsafe_allow_html=True)

                st.metric(label="🎯 Primary Match Score", value=f"{score:.2f}%")
                st.progress(min(int(score), 100))

                st.markdown("##### 📈 Top Feature Matches:")
                for feat_name, feat_score in top3_list:
                    st.write(f"**{feat_name}**: `{feat_score:.1f}%`")
                    st.progress(min(int(feat_score), 100))

                with st.expander("🔬 View Technical Details"):
                    st.write(f"🏷️ **Detected Feature:** `{raw_label.title()}`")
                    st.write(f"🏷️ **Mapped Grouping:** `{pred_class}`")

            def go_to_upload():
                st.session_state.page = 'upload'
                st.session_state.uploaded_file = None
                st.session_state.selected_sample_url = None
            st.button("🔄 Back to Selection", on_click=go_to_upload)
        else:
            st.warning("No image found!")
            def go_to_upload():
                st.session_state.page = 'upload'
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
        * Pre-trained on **ImageNet-1k** (containing over 1 million images across 1,000 classes).
        * Includes extensive sub-categories ranging from specific dog breeds (*Golden Retriever, Pembroke Welsh Corgi, Siberian Husky*) to feline variants (*Siamese, Persian, Tabby*).
        * Logic filters aggregate specific breed detection tokens into clean easy-to-read **Cat**, **Dog**, or **Other** umbrella designations.

        #### 💻 Tech Stack
        * **Framework:** PyTorch & Torchvision
        * **Frontend:** Streamlit Custom UI
        * **Image Preprocessing:** PIL (Python Imaging Library)
        """
    )
    
    st.markdown("---")
    st.markdown("### 👩‍💻 Developer Details")
    st.markdown(
        """
        * **Name:** Sristi Sarkar
        * **Contact:** 
          * **Email:** `emailsristisarkar@gmail.com`
          * **Phone:** `+91 8240580651`
        """
    )
st.caption("⚠️ **Disclaimer:**  **AI Powered & Verified image classification model:** Built by Sristi Sarkar for reliable pet image classification. Results depend on image clarity and lighting. Use responsibly for demonstration.") 
