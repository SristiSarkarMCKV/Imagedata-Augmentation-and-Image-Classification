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
    """Injects CSS supporting dark mode base styling."""
    css = f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@500;700;800;900&family=Poppins:wght@300;400;600;700&display=swap');
    
    html, body, [class*='css'] {{ font-family: 'Poppins', sans-serif; }}

    /* Hide Streamlit header anchor elements */
    [data-testid='stHeaderActionElements'], .stHeadingAnchor {{ display: none !important; }}

    ::-webkit-scrollbar {{ width: 10px; }}
    ::-webkit-scrollbar-track {{ background: rgba(15, 23, 42, 0.7); }}
    ::-webkit-scrollbar-thumb {{ background: linear-gradient(180deg, #FF781F, #FF9800); border-radius: 10px; }}

    .stApp {{
        background-image: linear-gradient(rgba(15, 23, 42, 0.85), rgba(15, 23, 42, 0.85)), url('{bg_url}');
        background-attachment: fixed;
        background-size: cover;
        background-position: center;
    }}

    /* Container Glassmorphism - Set to Dark Mode Style */
    .block-container {{
        background: rgba(15, 23, 42, 0.95) !important;
        color: #F8FAFC !important;
        border-radius: 24px;
        padding: 25px 20px !important;
        margin-top: 15px;
        margin-bottom: 25px;
        box-shadow: 0 20px 50px rgba(0, 0, 0, 0.6);
        backdrop-filter: blur(14px);
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
    }}

    p, span, label, h1, h2, h3, h4, h5, h6, caption {{ color: #F8FAFC !important; }}
    .sub-text {{ color: #CBD5E0 !important; }}

    .feature-card {{
        background: #1E293B !important;
        border-radius: 14px;
        padding: 16px;
        border: 1px solid #334155 !important;
        border-left: 5px solid #4ECDC4 !important;
        margin-bottom: 10px;
    }}
    .feature-card-title {{ font-family: 'Outfit', sans-serif; font-weight: 800; color: #F8FAFC !important; font-size: 1rem; margin-bottom: 4px; }}
    .feature-card-desc {{ color: #CBD5E0 !important; font-size: 0.85rem; line-height: 1.4; }}

    /* Radio Navigation */
    div[data-testid='stRadio'] > div {{ justify-content: center; gap: 8px; flex-wrap: wrap; }}
    div[data-testid='stRadio'] label {{
        background: #1E293B !important;
        border: 1.5px solid #334155 !important;
        border-radius: 12px;
        padding: 6px 14px;
        font-family: 'Outfit', sans-serif;
    }}
    div[data-testid='stRadio'] label p, div[data-testid='stRadio'] label span {{
        color: #F8FAFC !important;
        font-weight: 800 !important;
        font-size: 0.9rem !important;
    }}

    /* Alert Styling */
    div[data-testid='stAlert'] {{
        background-color: #1E293B !important;
        color: #F8FAFC !important;
        border-radius: 14px;
        border: 1px solid #334155 !important;
    }}
    div[data-testid='stAlert'] p, div[data-testid='stAlert'] span {{ color: #F8FAFC !important; }}
    div[data-testid='stAlert'] strong {{ color: #38BDF8 !important; }}

    .main-title {{ font-family: 'Outfit', sans-serif; text-align: center; background: linear-gradient(135deg, #FF6B6B, #FF8E53, #4ECDC4); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 2.2rem; font-weight: 900; margin-bottom: 0px; padding-bottom: 5px; }}
    .highlight-text {{ color: #FF6B6B; font-weight: 700; }}
    .diagram-container {{ background: transparent; padding: 0px; margin-top: 5px; margin-bottom: 15px; border: none; }}

    .result-card {{ border-radius: 18px; padding: 18px; text-align: center; color: white !important; font-family: 'Outfit', sans-serif; font-weight: 800; margin-bottom: 15px; box-shadow: 0 8px 20px rgba(0,0,0,0.15); }}
    .result-card p {{ color: white !important; }}
    .result-cat {{ background: linear-gradient(135deg, #FF6B6B, #FF8E53); }}
    .result-dog {{ background: linear-gradient(135deg, #4299E1, #3182CE); }}
    .result-other {{ background: linear-gradient(135deg, #ED8936, #ECC94B); }}
    .card-title {{ font-size: 1.3rem; margin: 0; color: #FFFFFF !important; }}

    div[data-testid='stFileUploader'] {{ border: 2.5px dashed #4ECDC4; border-radius: 16px; background: rgba(30, 41, 59, 0.5); padding: 10px; }}
    
    .stButton>button {{ background: linear-gradient(135deg, #FF6B6B, #FF8E53); color: white !important; font-family: 'Outfit', sans-serif; font-weight: 700; font-size: 1rem; border-radius: 14px; border: none; padding: 10px 20px; width: 100%; box-shadow: 0 4px 14px rgba(255, 107, 107, 0.35); }}
    
    [data-testid='stMetricValue'] {{ font-family: 'Outfit', sans-serif; font-size: 1.8rem !important; color: #38BDF8 !important; font-weight: 800; }}
    hr {{ margin: 12px 0 !important; border-color: #334155 !important; }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


def render_css_flowchart():
    """Renders dark-themed mobile responsive flowchart."""
    html_code = """
    <!DOCTYPE html>
    <html>
    <head>
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { 
          font-family: 'Poppins', sans-serif; 
          background: transparent; 
          padding: 0; 
          margin: 0; 
          width: 100%; 
          color: #F8FAFC;
        }
        
        :root {
          --bg-section: #1E293B;
          --border-color: #334155;
          --title-color: #38BDF8;
          --node-gray-bg: #0F172A;
          --node-gray-border: #475569;
          --node-gray-text: #F8FAFC;
          --arrow-color: #94A3B8;
        }

        .flow-wrapper { display: flex; flex-direction: column; gap: 12px; width: 100%; }
        .flow-section { background: var(--bg-section); border: 1.5px solid var(--border-color); border-radius: 14px; padding: 12px; }
        .section-title { font-size: 0.85rem; font-weight: 800; color: var(--title-color); text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 10px; }
        
        .stage-box { display: flex; gap: 10px; align-items: center; }
        .stage-img { width: 65px; height: 65px; border-radius: 10px; object-fit: cover; border: 2px solid var(--node-gray-border); flex-shrink: 0; }
        
        .step-grid { display: flex; flex-wrap: wrap; gap: 6px; align-items: center; flex: 1; }
        .node { 
          padding: 8px 10px; 
          border-radius: 8px; 
          font-size: 0.78rem; 
          font-weight: 700; 
          display: flex; 
          flex-direction: column; 
          align-items: center; 
          justify-content: center; 
          gap: 4px; 
          box-shadow: 0 2px 4px rgba(0,0,0,0.2); 
          flex: 1 1 auto; 
          min-width: 85px; 
          text-align: center; 
        }
        
        .node-gray { background: var(--node-gray-bg); border: 1.5px solid var(--node-gray-border); color: var(--node-gray-text); }
        .node-blue { background: #172A46; border: 1.5px solid #2B6CB0; color: #90CDF4; }
        .node-orange { background: #322318; border: 1.5px solid #C05621; color: #FBD38D; }
        .node-green { background: #132A1C; border: 1.5px solid #276749; color: #9AE6B4; }

        .cat-img-box { width: 42px; height: 42px; border-radius: 6px; object-fit: cover; border: 1px solid var(--node-gray-border); margin-top: 2px; }
        .arrow { color: var(--arrow-color); font-weight: bold; font-size: 0.85rem; }
        .down-arrow { text-align: center; font-size: 1rem; color: var(--arrow-color); margin: -4px 0; }

        /* Responsive Breakpoint for Mobile Displays */
        @media (max-width: 600px) {
          .stage-box { flex-direction: column; align-items: stretch; }
          .stage-img { width: 100%; height: 90px; }
          .step-grid { flex-direction: column; width: 100%; align-items: stretch; }
          .arrow { display: none; }
          .node { width: 100%; margin-bottom: 4px; }
          .cat-img-box { width: 50px; height: 50px; }
        }
      </style>
    </head>
    <body>
      <div class="flow-wrapper">
        
        <!-- STAGE 1 -->
        <div class="flow-section">
          <div class="section-title">1️⃣ Input & Image Preprocessing</div>
          <div class="stage-box">
            <img class="stage-img" src="https://images.unsplash.com/photo-1548199973-03cce0bbc87b?w=200&auto=format&fit=crop&q=80" alt="Gallery Input"/>
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
    </body>
    </html>
    """
    # Expanded frame height accommodates full mobile vertical layout
    components.html(html_code, height=1150, scrolling=False)


inject_custom_styles(PERMANENT_BG_GIF)


# ---------------------------------------------------------
# AI Model Initialization
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

    cat_keywords = ['cat', 'tabby', 'persian', 'siamese', 'lynx', 'leopard', 'kitten']
    dog_keywords = ['dog', 'retriever', 'terrier', 'spaniel', 'poodle', 'hound', 'bulldog', 'husky', 'corgi', 'puppy']

    top3_details = [(categories[top5_catid[i].item()].title(), top5_prob[i].item() * 100) for i in range(3)]

    if any(kw in top1_label for kw in cat_keywords):
        return "Cat", top1_score, top1_label, top3_details
    elif any(kw in top1_label for kw in dog_keywords):
        return "Dog", top1_score, top1_label, top3_details
    else:
        return "Other", top1_score, top1_label, top3_details


# ---------------------------------------------------------
# UI & Navigation Setup
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

# --- HOME ---
if nav_choice == "🏠 Home":
    st.markdown("### 🧬 Automated Deep Learning Pet Recognition Engine")
    st.markdown(
        "<p style='font-size: 0.95rem; line-height: 1.6;'>"
        "Welcome! This application utilizes state-of-the-art Deep Computer Vision to instantly analyze "
        "and classify images via a 50-layer Deep Residual Neural Network (ResNet50)."
        "</p>", 
        unsafe_allow_html=True
    )
    
    st.markdown("#### 📊 Visual Workflow Diagram")
    st.markdown('<div class="diagram-container">', unsafe_allow_html=True)
    render_css_flowchart()
    st.markdown('</div>', unsafe_allow_html=True)

    st.button("🚀 Launch Image Classifier Engine", on_click=switch_to_prediction)

# --- PREDICTION ---
elif nav_choice == "🔮 Prediction":
    if st.session_state.page == 'upload':
        st.markdown("<p class='sub-text'>Upload a pet image below for automatic AI classification.</p>", unsafe_allow_html=True)
        file = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png", "webp"], label_visibility="collapsed")

        if file is not None:
            st.session_state.uploaded_file = file
            image = Image.open(file).convert("RGB")
            st.image(image, caption="🖼️ Image Ready for Analysis", use_container_width=True)
            st.button("🚀 Analyze Image & View Results", on_click=go_to_results)

    elif st.session_state.page == 'results':
        st.markdown("<h2 style='text-align: center;'>📋 Analysis Report</h2>", unsafe_allow_html=True)
        
        if st.session_state.uploaded_file is not None:
            image = Image.open(st.session_state.uploaded_file).convert("RGB")
            col1, col2 = st.columns([1, 1], gap="large")

            with col1:
                st.image(image, use_container_width=True)

            with col2:
                with st.spinner("Analyzing image features..."):
                    pred_class, score, raw_label, top3_list = classify_image(image)

                card_class = "result-cat" if pred_class == "Cat" else ("result-dog" if pred_class == "Dog" else "result-other")
                st.markdown(f'<div class="result-card {card_class}"><p class="card-title">RESULT: {pred_class.upper()}</p></div>', unsafe_allow_html=True)

                st.metric(label="Primary Match Score", value=f"{score:.2f}%")
                st.progress(min(int(score), 100))

                for feat_name, feat_score in top3_list:
                    st.write(f"**{feat_name}**: `{feat_score:.1f}%`")

            st.button("🔄 Upload Another Image", on_click=go_to_upload)


# --- ABOUT ---
elif nav_choice == "ℹ️ About":
    st.markdown("### ℹ️ About the Model")
    st.write("This tool uses PyTorch's ResNet-50 pre-trained model on ImageNet to perform image classification.")
