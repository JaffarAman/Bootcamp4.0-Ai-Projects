import streamlit as st
import requests

# =========================
# CONFIG
# =========================
BASE_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="AI Quiz Generator",
    page_icon="⚡",
    layout="centered"
)

# =========================
# DARK THEME (FIXED CONTRAST)
# =========================
st.markdown("""
<style>

.stApp {
    background-color: #0e1117;
    color: #e6e6e6;
}

h1, h2, h3, h4 {
    color: #ffffff;
}

p, div, span, label {
    color: #e6e6e6;
}

/* Input box */
input {
    background-color: #1c1f26 !important;
    color: white !important;
    border: 1px solid #333 !important;
}

/* Button */
.stButton > button {
    background-color: #2d3139;
    color: white;
    border-radius: 8px;
    border: 1px solid #3a3f4b;
    width: 100%;
    padding: 0.6rem;
}

/* Expander */
.streamlit-expanderHeader {
    color: white !important;
}

</style>
""", unsafe_allow_html=True)

# =========================
# API FUNCTION
# =========================
def generate_quiz(quiz_id):
    try:
        response = requests.post(f"{BASE_URL}/create_quiz/{quiz_id}")

        # 🔥 DEBUG (VERY IMPORTANT)
        st.write("STATUS CODE:", response.status_code)
        st.write("RAW RESPONSE:", response.text)

        if response.status_code in [200, 201]:
            return response.json()

    except Exception as e:
        st.error(f"Request failed: {e}")

    return None


# =========================
# UI
# =========================
st.title("⚡ AI Quiz Generator")

quiz_id = st.text_input("Enter Quiz ID")

if st.button("Generate Quiz"):

    if not quiz_id:
        st.warning("Please enter Quiz ID first")
    else:

        with st.spinner("Generating quiz..."):

            data = generate_quiz(quiz_id)

            if not data:
                st.error("Quiz generation failed (check API response above)")
            else:

                st.success("Quiz generated successfully")

                st.metric("MCQs Generated", data.get("no_of_mcqs", 0))

                st.divider()

                for i, mcq in enumerate(data.get("mcqs", []), start=1):

                    with st.expander(f"Question {i}"):

                        st.write(mcq.get("question", "No question"))

                        options = mcq.get("options", {})

                        st.write("A:", options.get("option_a"))
                        st.write("B:", options.get("option_b"))
                        st.write("C:", options.get("option_c"))
                        st.write("D:", options.get("option_d"))

                        st.success(
                            f"Correct Answer: {mcq.get('correct_option')}"
                        )