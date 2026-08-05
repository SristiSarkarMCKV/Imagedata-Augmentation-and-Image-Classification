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
    """Injects CSS supporting Streamlit theme-switching & high contrast."""
    css = (
        "<style>\n"
        "@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@500;700;800;900&family=Poppins:wght@300;400;600;700&display=swap');\n"
        "html, body, [class*='css'] { font-family: 'Poppins', sans-serif; }\n"
        
        "/* HIDE STREAMLIT LINK/ANCHOR ICONS NEXT TO HEADINGS */\n"
        "[data-testid='stHeaderActionElements'], .stHeadingAnchor, a.data-testid-stHeaderActionElements, .css-1544g2n { display: none !important; visibility: hidden !important; }\n"
        "h1 a, h2 a, h3 a, h4 a, h5 a, h6 a { display: none !important; opacity: 0 !important; }\n"
        "a[href*='#'] { display: none !important; }\n"

        "::-webkit-scrollbar { width: 10px; }\n"
        "::-webkit-scrollbar-track { background: rgba(15, 23, 42, 0.7); }\n"
        "::-webkit-scrollbar-thumb { background: linear-gradient(180deg, #FF781F, #FF9800); border-radius: 10px; }\n"
        
        ".stApp { background-image: linear-gradient(rgba(15, 23, 42, 0.75), rgba(15, 23, 42, 0.75)), url('" + bg_url + "'); background-attachment: fixed; background-size: cover; background-position: center; }\n"
        
        "/* Main Glassmorphism Container */\n"
        ".block-container {\n"
        "  background: rgba(255, 255, 255, 0.96);\n"
        "  color: #1E293B !important;\n"
        "  border-radius: 24px;\n"
        "  padding: 25px 20px !important;\n"
        "  margin-top: 15px;\n"
        "  margin-bottom: 25px;\n"
        "  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.5);\n"
        "  backdrop-filter: blur(14px);\n"
        "  border: 1px solid rgba(255, 255, 255, 0.4);\n"
        "}\n"

        "p, span, label, h1, h2, h3, h4, h5, h6, caption { color: #1E293B; }\n"

        ".feature-card {\n"
        "  background: #F8FAFC;\n"
        "  border-radius: 14px;\n"
        "  padding: 16px;\n"
        "  border: 1px solid #E2E8F0;\n"
        "  border-left: 5px solid #4ECDC4;\n"
        "  margin-bottom: 10px;\n"
        "}\n"
        ".feature-card-title { font-family: 'Outfit', sans-serif; font-weight: 800; color: #1E293B; font-size: 1rem; margin-bottom: 4px; }\n"
        ".feature-card-desc { color: #334155; font-size: 0.85rem; line-height: 1.4; }\n"

        "/* Navigation Radio Button Tweaks */\n"
        "div[data-testid='stRadio'] > div { justify-content: center; gap: 8px; flex-wrap: wrap; }\n"
        "div[data-testid='stRadio'] label {\n"
        "  background: #F1F5F9 !important;\n"
        "  border: 1.5px solid #CBD5E0 !important;\n"
        "  border-radius: 12px;\n"
        "  padding: 6px 14px;\n"
        "  font-family: 'Outfit', sans-serif;\n"
        "  font-weight: 700;\n"
        "}\n"
        "div[data-testid='stRadio'] label p, div[data-testid='stRadio'] label span {\n"
        "  color: #0F172A !important;\n"
        "  font-weight: 800 !important;\n"
        "  font-size: 0.9rem !important;\n"
        "}\n"

        "/* Alerts Light Theme */\n"
        "div[data-testid='stAlert'] { background-color: #F8FAFC !important; color: #0F172A !important; font-weight: 600; border-radius: 14px; border: 1px solid #CBD5E0 !important; }\n"
        "div[data-testid='stAlert'] p, div[data-testid='stAlert'] span { color: #0F172A !important; font-weight: 600 !important; }\n"
        "div[data-testid='stAlert'] strong { color: #000000 !important; font-weight: 800 !important; }\n"

        "/* ========================================================= */\n"
        "/* DARK THEME SUPPORT (FOR BOTH OS & STREAMLIT DARK SETTING) */\n"
        "/* ========================================================= */\n"
        "@media (prefers-color-scheme: dark) {\n"
        "  .block-container {\n"
        "    background: rgba(15, 23, 42, 0.95) !important;\n"
        "    color: #F8FAFC !important;\n"
        "    border: 1px solid rgba(255, 255, 255, 0.15) !important;\n"
        "  }\n"
        "  p, span, label, h1, h2, h3, h4, h5, h6, caption { color: #F8FAFC !important; }\n"
        "  .sub-text { color: #CBD5E0 !important; }\n"
        "  .feature-card {\n"
        "    background: #1E293B !important;\n"
        "    border: 1px solid #334155 !important;\n"
        "    border-left: 5px solid #4ECDC4 !important;\n"
        "  }\n"
        "  .feature-card-title { color: #F8FAFC !important; }\n"
        "  .feature-card-desc { color: #CBD5E0 !important; }\n"
        "  div[data-testid='stRadio'] label {\n"
        "    background: #1E293B !important;\n"
        "    border: 1.5px solid #334155 !important;\n"
        "  }\n"
        "  div[data-testid='stRadio'] label p, div[data-testid='stRadio'] label span {\n"
        "    color: #F8FAFC !important;\n"
        "  }\n"
        "  div[data-testid='stAlert'] {\n"
        "    background-color: #1E293B !important;\n"
        "    border: 1px solid #334155 !important;\n"
        "  }\n"
        "  div[data-testid='stAlert'] p, div[data-testid='stAlert'] span {\n"
        "    color: #F8FAFC !important;\n"
        "  }\n"
        "  div[data-testid='stAlert'] strong {\n"
        "    color: #38BDF8 !important;\n"
        "  }\n"
        "}\n"

        ".main-title { font-family: 'Outfit', sans-serif; text-align: center; background: linear-gradient(135deg, #FF6B6B, #FF8E53, #4ECDC4); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 2.2rem; font-weight: 900; margin-bottom: 0px; padding-bottom: 5px; }\n"
        ".sub-text { font-family: 'Poppins', sans-serif; text-align: center; font-size: 0.95rem; color: #4A5568; font-weight: 500; line-height: 1.5; margin-bottom: 15px; }\n"
        ".highlight-text { color: #FF6B6B; font-weight: 700; }\n"
        
        ".diagram-container { background: transparent; padding: 0px; margin-top: 5px; margin-bottom: 15px; border: none; }\n"
        
        ".result-card { border-radius: 18px; padding: 18px; text-align: center; color: white !important; font-family: 'Outfit', sans-serif; font-weight: 800; margin-bottom: 15px; box-shadow: 0 8px 20px rgba(0,0,0,0.15); }\n"
        ".result-card p { color: white !important; }\n"
        ".result-cat { background: linear-gradient(135deg, #FF6B6B, #FF8E53); }\n"
        ".result-dog { background: linear-gradient(135deg, #4299E1, #3182CE); }\n"
        ".result-other { background: linear-gradient(135deg, #ED8936, #ECC94B); }\n"
        ".card-title { font-size: 1.3rem; margin: 0; color: #FFFFFF !important; }\n"
        
        "div[data-testid='stFileUploader'] { border: 2.5px dashed #4ECDC4; border-radius: 16px; background: rgba(247, 250, 252, 0.2); padding: 10px; }\n"
        
        ".stButton>button { background: linear-gradient(135deg, #FF6B6B, #FF8E53); color: white !important; font-family: 'Outfit', sans-serif; font-weight: 700; font-size: 1rem; border-radius: 14px; border: none; padding: 10px 20px; width: 100%; box-shadow: 0 4px 14px rgba(255, 107, 107, 0.35); }\n"
        
        "[data-testid='stMetricValue'] { font-family: 'Outfit', sans-serif; font-size: 1.8rem !important; color: #38BDF8 !important; font-weight: 800; }\n"
        "hr { margin: 12px 0 !important; border-color: #CBD5E0 !important; }\n"
        "</style>"
    )
    st.markdown(css, unsafe_allow_html=True)


def render_css_flowchart():
    """Renders theme-adaptive and mobile-responsive visual workflow diagram."""
    html_code = """
    <!DOCTYPE html>
    <html>
    <head>
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: 'Poppins', sans-serif; background: transparent; padding: 0; margin: 0; width: 100%; }
        
        :root {
          --bg-section: #F8FAFC;
          --border-color: #CBD5E0;
          --title-color: #334155;
          --node-gray-bg: #FFFFFF;
          --node-gray-border: #CBD5E0;
          --node-gray-text: #0F172A;
          --arrow-color: #64748B;
        }

        @media (prefers-color-scheme: dark) {
          :root {
            --bg-section: #1E293B;
            --border-color: #334155;
            --title-color: #E2E8F0;
            --node-gray-bg: #0F172A;
            --node-gray-border: #475569;
            --node-gray-text: #F8FAFC;
            --arrow-color: #94A3B8;
          }
        }

        .flow-wrapper { display: flex; flex-direction: column; gap: 10px; width: 100%; }
        .flow-section { background: var(--bg-section); border: 1.5px solid var(--border-color); border-radius: 14px; padding: 12px; }
        .section-title { font-size: 0.8rem; font-weight: 800; color: var(--title-color); text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px; }
        
        .stage-box { display: flex; gap: 10px; align-items: center; }
        
        .stage-img { width: 65px; height: 65px; border-radius: 10px; object-fit: cover; border: 2px solid var(--node-gray-border); flex-shrink: 0; }
        
        .step-grid { display: flex; flex-wrap: wrap; gap: 6px; align-items: center; flex: 1; }
        .node { padding: 6px 8px; border-radius: 8px; font-size: 0.78rem; font-weight: 700; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 4px; box-shadow: 0 2px 4px rgba(0,0,0,0.03); flex: 1 1 auto; min-width: 85px; text-align: center; }
        
        .node-gray { background: var(--node-gray-bg); border: 1.5px solid var(--node-gray-border); color: var(--node-gray-text); }
        .node-blue { background: #EBF8FF; border: 1.5px solid #90CDF4; color: #2B6CB0; }
        .node-orange { background: #FFFAF0; border: 1.5px solid #FBD38D; color: #C05621; }
        .node-green { background: #F0FFF4; border: 1.5px solid #9AE6B4; color: #276749; }
        
        @media (prefers-color-scheme: dark) {
          .node-blue { background: #172A46; border-color: #2B6CB0; color: #90CDF4; }
          .node-orange { background: #322318; border-color: #C05621; color: #FBD38D; }
          .node-green { background: #132A1C; border-color: #276749; color: #9AE6B4; }
        }

        .cat-img-box { width: 42px; height: 42px; border-radius: 6px; object-fit: cover; border: 1px solid var(--node-gray-border); margin-top: 2px; }
        
        .arrow { color: var(--arrow-color); font-weight: bold; font-size: 0.8rem; }
        .down-arrow { text-align: center; font-size: 0.9rem; color: var(--arrow-color); margin: -4px 0; }

        /* ========================================================= */
        /* MOBILE RESPONSIVE LAYOUT (PREVENTS CROPPING / HORIZONTAL OVERFLOW) */
        /* ========================================================= */
        @media (max-width: 600px) {
          .stage-box { flex-direction: column; align-items: stretch; }
          .stage-img { width: 100%; height: 90px; }
          .step-grid { flex-direction: column; width: 100%; align-items: stretch; }
          .arrow { display: none; } /* Hide horizontal arrows on narrow mobile screens */
          .node { width: 100%; margin-bottom: 4px; }
          .cat-img-box { width: 50px; height: 50px; }
        }
      </style>
    </head>
    <body>
      <div class="flow-wrapper">
        
        <!-- STAGE 1: GALLERY OF IMAGES -->
        <div class="flow-section">
          <div class="section-title">1️⃣ Input & Image Preprocessing</div>
          <div class="stage-box">
            <img class="stage-img" src="https://images.unsplash.com/photo-1548199973-03cce0bbc87b?w=200&auto=format&fit=crop&q=80" alt="Gallery of Images"/>
            <div class="step-grid">
              <div class="node node-gray">📥 Gallery Input</div>
              <div class="arrow">➔</div>
              <div class="node node-gray">📸 RGB Parsing</div>
              <div class="arrow">➔</div>
              <div class="node node-gray">📏 Resize 224x224</div>
              <div class="arrow">➔</div>
              <div class="node node-gray">⚖️ Normalize</div>
            </div>
          </div>
        </div>

        <div class="down-arrow">⬇️</div>

        <!-- STAGE 2: RESIZING & DEEP NETWORK -->
        <div class="flow-section">
          <div class="section-title">2️⃣ Deep Neural Network (ResNet-50)</div>
          <div class="stage-box">
            <img class="stage-img" src="https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=200&auto=format&fit=crop&q=80" alt="Resizing and Neural Net"/>
            <div class="step-grid">
              <div class="node node-blue">🧠 Feature Extraction</div>
              <div class="arrow">➔</div>
              <div class="node node-blue">⚡ Conv Layers</div>
              <div class="arrow">➔</div>
              <div class="node node-blue">📈 Softmax Logits</div>
            </div>
          </div>
        </div>

        <div class="down-arrow">⬇️</div>

        <!-- STAGE 3: CATEGORIZATION -->
        <div class="flow-section">
          <div class="section-title">3️⃣ Categorization & Prediction Output</div>
          <div class="stage-box">
            <div class="step-grid" style="width: 100%;">
              <div class="node node-orange">❓ Label Mapping</div>
              <div class="arrow">➔</div>
              
              <!-- Cat Node -->
              <div class="node node-green">
                <span>🐱 Cat Class</span>
                <img class="cat-img-box" src="https://images.unsplash.com/photo-1514888286974-6c03e2ca1dba?w=100&auto=format&fit=crop&q=80" alt="Cat Category"/>
              </div>

              <!-- Dog Node -->
              <div class="node node-green">
                <span>🐶 Dog Class</span>
                <img class="cat-img-box" src="https://images.unsplash.com/photo-1543466835-00a7907e9de1?w=100&auto=format&fit=crop&q=80" alt="Dog Category"/>
              </div>

              <!-- Other Node (Question Mark Image) -->
              <div class="node node-green">
                <span>❓ Other Class</span>
                <img class="cat-img-box" src="https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=100&auto=format&fit=crop&q=80" alt="Other Category Question Mark"/>
              </div>

            </div>
          </div>
        </div>

      </div>
    </body>
    </html>
    """
    # Dynamic component height to fit desktop or stacked mobile view fully
    components.html(html_code, height=750, scrolling=False)


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
    key='nav',
    label_visibility="collapsed"
)

# =========================================================
# PAGE 1: HOME PAGE
# =========================================================
if nav_choice == "🏠 Home":
    st.markdown("### 🧬 Automated Deep Learning Pet Recognition Engine")
    
    st.markdown(
        "<p style='font-size: 0.95rem; line-height: 1.6;'>"
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
            '<div class="feature-card-title">1. Preprocessing</div>'
            '<div class="feature-card-desc">Raw image frames are normalized color-space corrected (RGB) resized to 224x224 and converted into PyTorch tensors.</div>'
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
    
    st.markdown('<div class="diagram-container">', unsafe_allow_html=True)
    render_css_flowchart()
    st.markdown('</div>', unsafe_allow_html=True)

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
            "<span class='highlight-text'>🐶 Dog</span> or <span class='highlight-text'>❓ Other</span>"
            "</p>", 
            unsafe_allow_html=True
        )

        st.markdown("### 📥 Step 1: Upload Your Image")
        file = st.file_uploader(
            "Choose a pet image file (JPG, JPEG, PNG, WEBP)", 
            type=["jpg", "jpeg", "png", "webp"],
            label_visibility="collapsed"
        )

        if file is not None:
            st.session_state.uploaded_file = file
            image = Image.open(file).convert("RGB")
            st.image(image, caption="🖼️ Image Ready for Analysis", use_container_width=True)
            st.write("")
            st.button("🚀 Analyze Image & View Results", on_click=go_to_results)

    elif st.session_state.page == 'results':
        st.markdown("<h2 style='text-align: center; font-family: Outfit, sans-serif;'>📋 Analysis Report</h2>", unsafe_allow_html=True)
        st.markdown("<p class='sub-text'>Here are the classification findings from our AI model</p>", unsafe_allow_html=True)
        
        if st.session_state.uploaded_file is not None:
            image = Image.open(st.session_state.uploaded_file).convert("RGB")
            
            col1, col2 = st.columns([1, 1], gap="large")

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
                    st.markdown(f'<div class="result-card result-other"><p class="card-title">❓ Specified Pet Type: OTHER</p><p style="margin: 5px 0 0 0; font-size: 1.05rem; opacity: 0.9;">(Detected: {raw_label.title()})</p></div>', unsafe_allow_html=True)

                st.metric(label="🎯 Primary Match Score", value=f"{score:.2f}%")
                st.progress(min(int(score), 100))

                st.markdown("##### 📈 Top Feature Matches:")
                for feat_name, feat_score in top3_list:
                    st.write(f"**{feat_name}**: `{feat_score:.1f}%`")
                    st.progress(min(int(feat_score), 100))

                with st.expander("🔬 View Technical Details"):
                    st.write(f"🏷️ **Detected Feature:** `{raw_label.title()}`")
                    st.write(f"🏷️ **Mapped Grouping:** `{pred_class}`")

            st.write("")
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
        * Pre-trained on **ImageNet-1k** (containing over 1 million images across 1,000 classes).
        * Includes extensive sub-categories ranging from specific dog breeds (*Golden Retriever, Pembroke Welsh Corgi, Siberian Husky*) to feline variants (*Siamese, Persian, Tabby*).
        * Logic filters aggregate specific breed detection tokens into clean easy-to-read **Cat**, **Dog**, or **Other** umbrella designations.

        #### 💻 Tech Stack
        * **Framework:** PyTorch & Torchvision
        * **Frontend:** Streamlit Custom UI
        * **Image Preprocessing:** PIL (Python Imaging Library)
        """
    )
st.caption("⚠️ **Disclaimer:** This tool is intended for demonstration purposes. Classification confidence depends on image quality lighting and frame composition.")
