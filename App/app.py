import streamlit as st
import torch
from PIL import Image
from torchvision import models, transforms

# ---------------------------------------------------------
# Page Configuration & Styling
# ---------------------------------------------------------
st.set_page_config(
    page_title="Pet Image Classifier",
    page_icon="🐾",
    layout="centered"
)

# Custom CSS for a clean, modern UI
st.markdown("""
    <style>
    .main-title {
        text-align: center;
        color: #1E88E5;
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 5px;
    }
    .sub-text {
        text-align: center;
        font-size: 1.1rem;
        color: #555555;
        margin-bottom: 25px;
    }
    div[data-testid="stFileUploader"] {
        border: 2px dashed #1E88E5;
        border-radius: 12px;
        padding: 10px;
    }
    </style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------
# Header & Subtitle Section
# ---------------------------------------------------------
st.markdown("<h1 class='main-title'>Pet image classifier</h1>", unsafe_allow_html=True)
st.markdown(
    "<p class='sub-text'>"
    "Once the image is uploaded, the type of pet—whether it is a <b>Cat</b>, <b>Dog</b>, "
    "or <b>Other</b>—will be specified by the website."
    "</p>", 
    unsafe_allow_html=True
)

st.divider()


# ---------------------------------------------------------
# Model Loading & ImageNet Mapping
# ---------------------------------------------------------
@st.cache_resource
def load_classifier():
    # Load ResNet-50 with default pre-trained ImageNet weights for robust feature recognition
    weights = models.ResNet50_Weights.DEFAULT
    model = models.resnet50(weights=weights)
    model.eval()
    
    # Preprocessing pipeline
    transform = weights.transforms()
    categories = weights.meta["categories"]
    
    return model, transform, categories

model, transform, categories = load_classifier()

def classify_pet(image, confidence_threshold=0.30):
    """
    Classifies if an image contains a Cat, Dog, or Other by inspecting 
    the top predicted ImageNet class labels.
    """
    input_tensor = transform(image).unsqueeze(0)
    
    with torch.no_grad():
        outputs = model(input_tensor)
        probabilities = torch.nn.functional.softmax(outputs[0], dim=0)
    
    top_prob, top_catid = torch.max(probabilities, 0)
    top_label = categories[top_catid.item()].lower()
    prob_score = top_prob.item() * 100

    # Broad keywords to match ImageNet's detailed cat/dog sub-species
    dog_keywords = ['dog', 'retriever', 'terrier', 'spaniel', 'poodle', 'hound', 'bulldog', 'shepherd', 'husky', 'collie', 'pug', 'chihuahua', 'beagle', 'mutt']
    cat_keywords = ['cat', 'tabby', 'cougar', 'cheetah', 'leopard', 'siamese', 'persian']

    # Determine class
    is_dog = any(kw in top_label for kw in dog_keywords)
    is_cat = any(kw in top_label for kw in cat_keywords)

    if prob_score < (confidence_threshold * 100):
        return "Other", prob_score, top_label
    elif is_dog:
        return "Dog", prob_score, top_label
    elif is_cat:
        return "Cat", prob_score, top_label
    else:
        return "Other", prob_score, top_label


# ---------------------------------------------------------
# Image Upload Tab Section
# ---------------------------------------------------------
uploaded_file = st.file_uploader(
    "Upload a Pet Image", 
    type=["jpg", "jpeg", "png", "webp"]
)

# ---------------------------------------------------------
# Analysis Report Display Section
# ---------------------------------------------------------
if uploaded_file is not None:
    st.divider()
    st.subheader("📋 Analysis Report")

    # Load image
    image = Image.open(uploaded_file).convert("RGB")
    
    col1, col2 = st.columns([1, 1], gap="medium")

    with col1:
        st.image(image, caption="Uploaded Image", use_container_width=True)

    with col2:
        with st.spinner("Analyzing image..."):
            pred_class, score, raw_label = classify_pet(image)

        # Display result badge based on prediction
        if pred_class == "Dog":
            st.success("🐶 **Specified Pet Type: DOG**")
        elif pred_class == "Cat":
            st.success("🐱 **Specified Pet Type: CAT**")
        else:
            st.warning("❓ **Specified Pet Type: OTHER / UNKNOWN**")

        st.metric(label="Model Certainty", value=f"{score:.2f}%")

        st.markdown("---")
        with st.expander("🔍 View Technical Details"):
            st.write(f"**Detected Primary Feature:** `{raw_label.title()}`")
            st.caption("The classification logic maps ImageNet features directly to Cat/Dog taxonomies to avoid false positive biases.")
