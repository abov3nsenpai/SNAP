import streamlit as st
import os
from image_utils import generate_caption
from api_utils import get_location_from_caption, get_activities, get_food_nutrition

USDA_API_KEY = "BFfGpuMZI8EPKZxOoyJQLyo6V1TztvbMcB5Z7Md6"

st.set_page_config(page_title="SNAP", layout="centered")
st.title("📸 SNAP TRAVEL AI")

def classify_caption(caption):
    place_keywords = ["building", "statue", "monument", "city", "temple", "park", "beach", "mountain", "bridge", "tower"]
    food_keywords = ["burger", "salad", "cake", "egg", "pizza", "soup", "steak", "patty", "bread", "dressing", "meat", "fruit", "vegetable", "rice", "pasta", "leaf", "curry", "chicken"]

    caption_lower = caption.lower()
    if any(word in caption_lower for word in place_keywords):
        return "place"
    elif any(word in caption_lower for word in food_keywords):
        return "food"
    else:
        return "place"

def clean_caption_for_location(caption):
    caption = caption.lower().strip()
    for prefix in ["the ", "a ", "an "]:
        if caption.startswith(prefix):
            caption = caption[len(prefix):]
            break
    return caption

uploaded_file = st.file_uploader("Upload a photo (food or place)", type=["jpg", "png", "jpeg"])

if uploaded_file:
    os.makedirs("sample_images", exist_ok=True)
    img_path = os.path.join("sample_images", uploaded_file.name)

    with open(img_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    st.image(img_path, caption="Uploaded Image", use_container_width=True)

    with st.spinner("Analyzing image..."):
        caption = generate_caption(img_path)

    st.markdown(f"**🧠 Caption:** _{caption}_")

    category = classify_caption(caption)

    if category == "place":
        cleaned_caption = clean_caption_for_location(caption)
        loc = get_location_from_caption(cleaned_caption)
        if loc:
            st.success(f"📍 Recognized as: {loc['name']}")
            st.write(f"**Location:** {loc['address']}")
            st.write(f"**Coordinates:** {loc['lat']}, {loc['lon']}")

            st.markdown("### 🎯 Nearby Activities Today")
            acts = get_activities(loc["lat"], loc["lon"])
            if acts:
                for a in acts:
                    st.markdown(f"- {a}")
            else:
                st.warning("No nearby tourist activities found.")
        else:
            st.warning("Could not find location info.")
    else:
        keywords = ["burger", "salad", "cake", "egg", "pizza", "soup", "steak", "patty", "bread", "meat", "fruit", "vegetable", "rice", "pasta", "leaf", "curry", "chicken"]
        found = [word for word in keywords if word in caption.lower()]
        query_term = found[0] if found else caption

        food_data = get_food_nutrition(query_term, USDA_API_KEY)
        if food_data:
            st.markdown("### 🍽️ Nutrition Info (Food Detected)")
            st.write(f"**Food:** {food_data['description']}")
            st.write(f"**Category:** {food_data['category']}")
            st.markdown("**Nutrients (per 100g):**")
            for key, val in food_data["nutrients"].items():
                st.write(f"- {key}: {val}")
        else:
            st.warning("Could not find nutrition info.")