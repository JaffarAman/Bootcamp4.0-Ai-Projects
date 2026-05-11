---
title: AI Assignment Creator
emoji: 🧠
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 7860
---

# 🧠 AI Assignment Creator - Backend API

This is the production backend for the **AI Assignment Creator**, hosted on Hugging Face Spaces.

**Live Base URL:** `https://abdulqayyum360-ai-assignment-creator.hf.space`

---

## 🚀 API Reference for Developers

### 📖 Interactive Documentation (Swagger)
You can test the API endpoints directly in your browser here:
👉 [https://abdulqayyum360-ai-assignment-creator.hf.space/docs](https://abdulqayyum360-ai-assignment-creator.hf.space/docs)

---

## 🛣️ API Endpoints

### 1. System Health Check
Check if the backend is operational.
- **URL:** `https://abdulqayyum360-ai-assignment-creator.hf.space/`
- **Method:** `GET`

### 2. Fetch Teacher Context
Required to populate dropdowns for Bootcamps and Domains.
- **URL:** `/api/teacher/{teacher_id}/details`
- **Method:** `GET`

### 3. Generate AI Assignment
Generate assignment content based on technical prompts.
- **URL:** `/api/generate-assignment`
- **Method:** `POST`
- **Payload:**
  ```json
  {
    "prompt": "Create an assignment on Docker basics",
    "teacher_id": "YOUR_TEACHER_ID",
    "domain_id": "YOUR_DOMAIN_ID",
    "bootcamp_id": "YOUR_BOOTCAMP_ID",
    "module": "Backend"
  }
  ```

### 4. Save to Database
Save the final assignment record to MongoDB.
- **URL:** `/api/submit-assignment`
- **Method:** `POST`

---

## 🛠️ Tech Stack
- **Framework:** FastAPI
- **Model:** Gemini 2.5 Flash
- **Database:** MongoDB Atlas
- **Runtime:** Docker (Python 3.10)

## 🔐 Environment Secrets (Hugging Face)
Ensure these are set in the Space Settings:
- `MONGO_URI`
- `DB_NAME`
- `GEMINI_API_KEY`
