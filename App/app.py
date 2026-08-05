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
    """Injects high-contrast dark CSS across Streamlit UI components."""
    css = f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@500;700;800;900&family=Poppins:wght@300;400;600;700&display=swap');
    
    html, body, [class*='css'] {{ font-family: 'Poppins', sans-serif; }}
    
    /* HIDE STREAMLIT LINK/ANCHOR ICONS */
    [data-testid='stHeaderActionElements'], .stHeadingAnchor, a.data-testid-stHeaderActionElements {{ display: none !important; visibility: hidden !important; }}
    h1 a, h2 a, h3 a, h4 a, h5 a, h6 a {{ display: none !important; opacity: 0 !important; }}

    ::-webkit-scrollbar {{ width: 10px; }}
    ::-webkit-scrollbar-track {{ background: rgba(15, 23, 42, 0.7); }}
    ::-webkit-scrollbar-thumb {{ background: linear-gradient(180deg, #FF781F, #FF9800); border-radius: 10px; }}
    
    .stApp {{ 
        background-image: linear-gradient(rgba(15, 23, 42, 0.85), rgba(15, 23, 42, 0.85)), url('{bg_url}'); 
        background-attachment: fixed; 
        background-size: cover; 
        background-position: center; 
    }}
    
    /* Main Dark Glassmorphism Container with compact padding */
    .block-container {{
      background: rgba(15, 23, 42, 0.95) !important;
      color: #F8FAFC !important;
      border-radius: 20px;
      padding: 18px 16px !important;
      margin-top: 10px;
      margin-bottom: 15px;
      box-shadow: 0 20px 50px rgba(0, 0, 0, 0.6);
      backdrop-filter: blur(14px);
      border: 1px solid rgba(255, 255, 255, 0.15) !important;
    }}

    p, span, label, h1, h2, h3, h4, h5, h6, caption {{ color: #F8FAFC !important; }}
    .sub-text {{ color: #CBD5E0 !important; }}

    /* Remove background style blocks for core capability cards, text-only styling matching theme */
    .feature-card {{
      background: transparent !important;
      border-radius: 12px;
      padding: 10px 4px;
      border: none !important;
      border-left: 4px solid #4ECDC4 !important;
      margin-bottom: 6px;
    }}
    .feature-card-title {{ font-family: 'Outfit', sans-serif; font-weight: 800; color: #38BDF8 !important; font-size: 0.95rem; margin-bottom: 2px; }}
    .feature-card-desc {{ color: #CBD5E0 !important; font-size: 0.82rem; line-height: 1.35; }}

    /* Navigation Radio Button Styling */
    div[data-testid='stRadio'] > div {{ justify-content: center; gap: 8px; flex-wrap: wrap; }}
    div[data-testid='stRadio'] label {{
      background: #1E293B !important;
      border: 1.5px solid #334155 !important;
      border-radius: 10px;
      padding: 4px 12px;
      font-family: 'Outfit', sans-serif;
    }}
    div[data-testid='stRadio'] label p, div[data-testid='stRadio'] label span {{
      color: #F8FAFC !important;
      font-weight: 800 !important;
      font-size: 0.85rem !important;
    }}

    /* Alert Boxes */
    div[data-testid='stAlert'] {{ 
      background-color: transparent !important; 
      color: #F8FAFC !important; 
      border-radius: 10px; 
      border: 1px solid #334155 !important;
      padding: 8px 12px !important;
    }}
    div[data-testid='stAlert'] p, div[data-testid='stAlert'] span {{ color: #CBD5E0 !important; font-size: 0.8rem !important; }}
    div[data-testid='stAlert'] strong {{ color: #38BDF8 !important; }}

    .main-title {{ font-family: 'Outfit', sans-serif; text-align: center; background: linear-gradient(135deg, #FF6B6B, #FF8E53, #4ECDC4); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 1.9rem; font-weight: 900; margin-bottom: 0px; padding-bottom: 0px; }}
    .highlight-text {{ color: #FF6B6B; font-weight: 700; }}
    
    .diagram-container {{ background: transparent; padding: 0px; margin-top: 2px; margin-bottom: 8px; border: none; }}
    
    .result-card {{ border-radius: 14px; padding: 14px; text-align: center; color: white !important; font-family: 'Outfit', sans-serif; font-weight: 800; margin-bottom: 10px; box-shadow: 0 6px 15px rgba(0,0,0,0.15); }}
    .result-card p {{ color: white !important; }}
    .result-cat {{ background: linear-gradient(135deg, #FF6B6B, #FF8E53); }}
    .result-dog {{ background: linear-gradient(135deg, #4299E1, #3182CE); }}
    .result-other {{ background: linear-gradient(135deg, #ED8936, #ECC94B); }}
    .card-title {{ font-size: 1.15rem; margin: 0; color: #FFFFFF !important; }}
    
    div[data-testid='stFileUploader'] {{ border: 2px dashed #4ECDC4; border-radius: 14px; background: rgba(30, 41, 59, 0.3); padding: 6px; }}
    
    .stButton>button {{ background: linear-gradient(135deg, #FF6B6B, #FF8E53); color: white !important; font-family: 'Outfit', sans-serif; font-weight: 700; font-size: 0.95rem; border-radius: 12px; border: none; padding: 8px 16px; width: 100%; box-shadow: 0 4px 12px rgba(255, 107, 107, 0.3); }}
    
    [data-testid='stMetricValue'] {{ font-family: 'Outfit', sans-serif; font-size: 1.6rem !important; color: #38BDF8 !important; font-weight: 800; }}
    hr {{ margin: 8px 0 !important; border-color: #334155 !important; }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


def render_css_flowchart():
    """Renders theme-adaptive and mobile-responsive flowchart with zero text background boxes and auto-sizing."""
    html_code = """
    <!DOCTYPE html>
    <html>
    <head>
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: 'Poppins', sans-serif; background: transparent; padding: 2px; margin: 0; width: 100%; color: #F8FAFC; }
        
        :root {
          --bg-section: transparent;
          --border-color: #334155;
          --title-color: #38BDF8;
          --node-gray-bg: #0F172A;
          --node-gray-border: #475569;
          --node-gray-text: #F8FAFC;
          --arrow-color: #94A3B8;
        }

        .flow-wrapper { display: flex; flex-direction: column; gap: 6px; width: 100%; }
        .flow-section { background: var(--bg-section); border: none; border-radius: 0px; padding: 2px 0; }
        .section-title { font-size: 0.78rem; font-weight: 800; color: var(--title-color); text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 4px; }
        
        .stage-box { display: flex; gap: 8px; align-items: center; }
        .stage-img { width: 55px; height: 55px; border-radius: 8px; object-fit: cover; border: 1.5px solid var(--node-gray-border); flex-shrink: 0; }
        
        .step-grid { display: flex; flex-wrap: wrap; gap: 4px; align-items: center; flex: 1; }
        .node { padding: 5px 8px; border-radius: 6px; font-size: 0.75rem; font-weight: 700; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 2px; box-shadow: 0 1px 3px rgba(0,0,0,0.15); flex: 1 1 auto; min-width: 75px; text-align: center; }
        
        .node-gray { background: var(--node-gray-bg); border: 1px solid var(--node-gray-border); color: var(--node-gray-text); }
        .node-blue { background: #172A46; border: 1px solid #2B6CB0; color: #90CDF4; }
        .node-orange { background: #322318; border: 1px solid #C05621; color: #FBD38D; }
        .node-green { background: #132A1C; border: 1px solid #276749; color: #9AE6B4; }

        .cat-img-box { width: 36px; height: 36px; border-radius: 4px; object-fit: cover; border: 1px solid var(--node-gray-border); margin-top: 1px; }
        
        .arrow { color: var(--arrow-color); font-weight: bold; font-size: 0.75rem; }
        .down-arrow { text-align: center; font-size: 0.8rem; color: var(--arrow-color); margin: -2px 0; }

        @media (max-width: 600px) {
          .stage-box { flex-direction: column; align-items: stretch; gap: 6px; }
          .stage-img { width: 100%; height: 70px; }
          .step-grid { flex-direction: column; width: 100%; align-items: stretch; gap: 4px; }
          .arrow { display: none; }
          .node { width: 100%; margin-bottom: 2px; padding: 6px; }
          .cat-img-box { width: 42px; height: 42px; }
        }
      </style>
    </head>
    <body>
      <div class="flow-wrapper" id="flowWrapper">
        
        <!-- STAGE 1 -->
        <div class="flow-section">
          <div class="section-title">1️⃣ Input & Image Preprocessing</div>
          <div class="stage-box">
            <img class="stage-img" src="https://images.unsplash.com/photo-1548199973-03cce0bbc87b?w=200&auto=format&fit=crop&q=80" alt="Gallery"/>
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

        <!-- STAGE 2 -->
        <div class="flow-section">
          <div class="section-title">2️⃣ Deep Neural Network (ResNet-50)</div>
          <div class="stage-box">
            <img class="stage-img" src="https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=200&auto=format&fit=crop&q=80" alt="ResNet"/>
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

        <!-- STAGE 3 -->
        <div class="flow-section">
          <div class="section-title">3️⃣ Categorization & Prediction Output</div>
          <div class="stage-box">
            <div class="step-grid" style="width: 100%;">
              <div class="node node-orange">❓ Label Mapping</div>
              <div class="arrow">➔</div>
              
              <div class="node node-green">
                <span>🐱 Cat Class</span>
                <img class="cat-img-box" src="https://images.unsplash.com/photo-1514888286974-6c03e2ca1dba?w=100&auto=format&fit=crop&q=80" alt="Cat"/>
              </div>

              <div class="node node-green">
                <span>🐶 Dog Class</span>
                <img class="cat-img-box" src="https://images.unsplash.com/photo-1543466835-00a7907e9de1?w=100&auto=format&fit=crop&q=80" alt="Dog"/>
              </div>

              <div class="node node-green">
                <span>❓ Other Class</span>
                <img class="cat-img-box" src="https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=100&auto=format&fit=crop&q=80" alt="Other"/>
              </div>

            </div>
          </div>
        </div>

      </div>

      <script>
        function sendHeight() {
          const height = document.getElementById('flowWrapper').scrollHeight + 15;
          window.parent.postMessage({ type: 'streamlit:setComponentHeight', height: height }, '*');
        }
        window.addEventListener('load', sendHeight);
        window.addEventListener('resize', sendHeight);
        setTimeout(sendHeight, 100);
      </script>
    </body>
    </html>
    """
    # Responsive component height fallback with automatic message resize listener support
    components.html(html_code, height=540, scrolling=False)


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
        "<p style='font-size: 0.9rem; line-height: 1.4; margin-bottom: 8px;'>"
        "Welcome! This application utilizes state-of-the-art Deep Computer Vision to instantly analyze "
        "identify and classify uploaded images. Built on top of a 50-layer Deep Residual Neural Network "
        "(ResNet50) the system evaluates visual feature representations across 1,000 object categories "
        "and intelligently maps them into concise pet classifications: 🐱 <b>Cat</b> 🐶 <b>Dog</b> or ❓ <b>Other</b>."
        "</p>", 
        unsafe_allow_html=True
    )
    
    st.markdown("#### ⚙️ Classification Architecture")
    
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.markdown(
            '<div class="feature-card">'
            '<div class="feature-card-title">1. Preprocessing</div>'
            '<div class="feature-card-desc">Raw image frames are normalized, RGB parsed, and resized to tensors.</div>'
            '</div>', unsafe_allow_html=True
        )
    with col_b:
        st.markdown(
            '<div class="feature-card">'
            '<div class="feature-card-title">2. ResNet50 Inference</div>'
            '<div class="feature-card-desc">Visual feature extraction occurs across deep convolutional blocks.</div>'
            '</div>', unsafe_allow_html=True
        )
    with col_c:
        st.markdown(
            '<div class="feature-card">'
            '<div class="feature-card-title">3. Logic & Classification</div>'
            '<div class="feature-card-desc">Softmax output logits map top predictions into species groupings.</div>'
            '</div>', unsafe_allow_html=True
        )

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
        st.markdown("<p class='sub-text' style='text-align: center;'>Here are the classification findings from our AI model</p>", unsafe_allow_html=True)
        
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
                    st.markdown(f'<div class="result-card result-other"><p class="card-title">❓ Specified Pet Type: OTHER</p><p style="margin: 4px 0 0 0; font-size: 0.95rem; opacity: 0.9;">(Detected: {raw_label.title()})</p></div>', unsafe_allow_html=True)

                st.metric(label="🎯 Primary Match Score", value=f"{score:.2f}%")
                st.progress(min(int(score), 100))

                st.markdown("##### 📈 Top Feature Matches:")
                for feat_name, feat_score in top3_list:
                    st.write(f"**{feat_name}**: `{feat_score:.1f}%`")

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
