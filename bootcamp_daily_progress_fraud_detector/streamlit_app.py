import streamlit as st
import requests

st.title("Fraud Detection System")

# Input fields
student_id = st.text_input("Enter Student ID")
yesterday_work = st.text_area("Enter Yesterday Work")

# Button
if st.button("Check Fraud"):

    if student_id and yesterday_work:

        url = "http://127.0.0.1:8000/today_update"

        payload = {
            "student_id": student_id,
            "yesterdayWork": yesterday_work
        }

        response = requests.post(url, json=payload)

        if response.status_code == 200:
            data = response.json()

            st.subheader("Result")

            st.write("Similarity:", data["similarity_percent"], "%")
            st.write("Fraud:", data["fraud"])

            if data["matched_data"]:
                st.write("Matched Text:", data["matched_data"])
                st.write("Matched Date:", data["matched_date"])

        else:
            st.error("API Error")
    
    else:
        st.warning("Please fill all fields")