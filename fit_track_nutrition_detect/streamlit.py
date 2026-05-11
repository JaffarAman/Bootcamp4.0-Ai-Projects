import streamlit as st
import requests
from PIL import Image
import io

# --- CONFIG ---
API_URL = "http://127.0.0.1:8000/analyze-food"  # FastAPI endpoint

# --- PAGE SETUP ---
st.set_page_config(
    page_title="Nutrition Analyzer",
    page_icon="🥗",
    layout="wide"
)

# --- CUSTOM CSS ---
st.markdown("""
<style>
.main-title {
    font-size: 34px;
    font-weight: bold;
    color: #2E7D32;
}
.card {
    padding: 20px;
    border-radius: 15px;
    background-color: #f5f5f5;
    text-align: center;
    box-shadow: 0px 4px 10px rgba(0,0,0,0.08);
}
.metric {
    font-size: 22px;
    font-weight: bold;
}
.label {
    font-size: 14px;
    color: gray;
}
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
st.sidebar.title("🥗 Nutrition AI")
menu = st.sidebar.radio("Navigation", ["Home", "About"])

# --- HOME PAGE ---
if menu == "Home":
    st.markdown('<p class="main-title">Food Nutrition Detection Dashboard</p>', unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("📤 Upload Food Image")
        uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "png", "jpeg"])

        if uploaded_file:
            image = Image.open(uploaded_file)
            st.image(image, caption="Preview", use_column_width=True)

            if st.button("🔍 Analyze Food"):
                with st.spinner("Analyzing..."):

                    # Convert file to bytes
                    img_bytes = uploaded_file.getvalue()

                    # Send to FastAPI
                    files = {"file": (uploaded_file.name, img_bytes, uploaded_file.type)}
                    response = requests.post(API_URL, files=files)

                    if response.status_code == 200:
                        data = response.json()

                        # --- DISPLAY RESULTS ---
                        with col2:
                            st.subheader("📊 Nutrition Breakdown")

                            st.markdown(f"""
                            <div class="card">
                                <div class="metric">{data.get("food_name", "-")}</div>
                                <div class="label">Food Name</div>
                            </div>
                            """, unsafe_allow_html=True)

                            c1, c2, c3, c4 = st.columns(4)

                            with c1:
                                st.markdown(f"""
                                <div class="card">
                                    <div class="metric">{data.get("calories", 0)} kcal</div>
                                    <div class="label">Calories</div>
                                </div>
                                """, unsafe_allow_html=True)

                            with c2:
                                st.markdown(f"""
                                <div class="card">
                                    <div class="metric">{data.get("protein", 0)} g</div>
                                    <div class="label">Protein</div>
                                </div>
                                """, unsafe_allow_html=True)

                            with c3:
                                st.markdown(f"""
                                <div class="card">
                                    <div class="metric">{data.get("fats", 0)} g</div>
                                    <div class="label">Fats</div>
                                </div>
                                """, unsafe_allow_html=True)

                            with c4:
                                st.markdown(f"""
                                <div class="card">
                                    <div class="metric">{data.get("carbs", 0)} g</div>
                                    <div class="label">Carbs</div>
                                </div>
                                """, unsafe_allow_html=True)

                            st.markdown("---")

                            colA, colB = st.columns(2)

                            with colA:
                                st.info(f"Serving: {data.get('serving', '-')}")

                            with colB:
                                confidence = data.get("confidence", "low")

                                if confidence == "high":
                                    st.success(f"Confidence: {confidence}")
                                elif confidence == "medium":
                                    st.warning(f"Confidence: {confidence}")
                                else:
                                    st.error(f"Confidence: {confidence}")

                            st.subheader("🧾 Ingredients")
                            ingredients = data.get("ingredients", [])

                            if ingredients:
                                st.write(ingredients)
                            else:
                                st.write("No ingredients detected")

                    else:
                        st.error("❌ API Error. Make sure FastAPI is running.")

# --- ABOUT PAGE ---
elif menu == "About":
    st.title("ℹ️ About")
    st.write("""
    This app uses AI to analyze food images and estimate:
    - Calories
    - Protein, fats, carbs
    - Portion size
    - Ingredients
    
    Backend: FastAPI + Gemini Vision  
    Frontend: Streamlit Dashboard
    """)