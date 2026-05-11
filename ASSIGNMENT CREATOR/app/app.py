import streamlit as st
import google.generativeai as genai
from pymongo import MongoClient
from datetime import datetime
from bson import ObjectId
import os
import io
import re
from fpdf import FPDF
from dotenv import load_dotenv

# -------------------------
# 🔐 ENV & CONFIG
# -------------------------
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

users_col = db["users"]
domains_col = db["domains"]
bootcamps_col = db["bootcamps"]
assignments_col = db["assignments"]

# -------------------------
# 🎨 CORPORATE ICONS (SVG)
# -------------------------
ICONS = {
    "teacher": '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>',
    "assignment": '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>',
    "ai": '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2v4"/><path d="m4.93 4.93 2.83 2.83"/><path d="M22 12h-4"/><path d="m19.07 19.07-2.83-2.83"/><path d="M12 22v-4"/><path d="m4.93 19.07 2.83-2.83"/><path d="M2 12h4"/><path d="m7.76 4.93-2.83 2.83"/><circle cx="12" cy="12" r="4"/></svg>',
    "config": '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.38a2 2 0 0 0-.73-2.73l-.15-.1a2 2 0 0 1-1-1.72v-.51a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z"/><circle cx="12" cy="12" r="3"/></svg>',
    "save": '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"/><polyline points="17 21 17 13 7 13 7 21"/><polyline points="7 3 7 8 15 8"/></svg>',
    "status": '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>',
    "power": '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18.36 6.64a9 9 0 1 1-12.73 0"/><line x1="12" y1="2" x2="12" y2="12"/></svg>'
}

def icon_text(icon_name, text, font_size="1.2rem"):
    return f'<div style="display: flex; align-items: center; gap: 10px;"><span style="color: #4facfe;">{ICONS[icon_name]}</span><span style="font-size: {font_size}; font-weight: 600;">{text}</span></div>'


# -------------------------
# 🎨 CUSTOM STYLING (Midnight Steel Corporate)
# -------------------------
def apply_custom_css():
    st.markdown("""
        <style>
        /* Main background and font */
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600&display=swap');
        
        html, body, [class*="css"] {
            font-family: 'Outfit', sans-serif;
        }

        .main {
            background: radial-gradient(circle at top left, #1a1c2c 0%, #0f1016 100%);
            color: #e0e6ed;
        }

        /* Sidebar styling */
        [data-testid="stSidebar"] {
            background-color: #161821;
            border-right: 1px solid #2d3142;
        }

        /* Card-like containers */
        .st-emotion-cache-12w0qpk, .st-emotion-cache-6q9sum {
            background: rgba(255, 255, 255, 0.03);
            border-radius: 12px;
            padding: 20px;
            border: 1px solid rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(10px);
        }

        /* Headings */
        h1, h2, h3 {
            background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 600;
        }

        /* Buttons */
        .stButton>button {
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            color: white !important;
            border: none;
            padding: 12px 24px;
            border-radius: 8px;
            font-weight: 600;
            transition: all 0.3s ease;
            width: 100%;
            text-transform: uppercase;
            letter-spacing: 1px;
            box-shadow: 0 4px 15px rgba(79, 172, 254, 0.3);
        }

        .stButton>button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(79, 172, 254, 0.5);
            opacity: 0.9;
        }

        /* Inputs */
        .stTextInput>div>div>input, .stTextArea>div>div>textarea, .stSelectbox>div>div>div {
            background-color: rgba(255, 255, 255, 0.05) !important;
            color: white !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            border-radius: 8px !important;
        }

        /* Metrics */
        [data-testid="stMetricValue"] {
            color: #00f2fe;
            font-size: 1.8rem;
        }

        /* Status messages */
        .stAlert {
            background-color: rgba(255, 255, 255, 0.02) !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            border-radius: 8px;
        }
        
        /* Custom Footer or Info */
        .footer {
            position: fixed;
            bottom: 10px;
            right: 10px;
            font-size: 0.8rem;
            color: rgba(255, 255, 255, 0.3);
        }
        </style>
    """, unsafe_allow_html=True)

# -------------------------
# 🧠 BUSINESS LOGIC
# -------------------------

def auto_extract_title(content):
    """
    Intelligently extracts or generates a title from the markdown content.
    Looks for the first H1 header (#) or falls back to the first line.
    """
    lines = content.strip().split('\n')
    for line in lines:
        clean_line = line.strip()
        if clean_line.startswith('#'):
            return clean_line.lstrip('#').strip()
    
    # Fallback: Use the first non-empty line
    for line in lines:
        if line.strip():
            first_val = line.strip()
            return (first_val[:60] + '...') if len(first_val) > 60 else first_val
            
    return "Untitled Assignment"

def create_pdf(text, title):
    """
    Generates a professional PDF from the assignment content.
    """
    # Clean text: Remove characters that FPDF's default fonts can't handle (emojis, etc)
    def clean_text(s):
        return re.sub(r'[^\x00-\xff]', '', s)

    text = clean_text(text)
    title = clean_text(title)

    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Title Header
    pdf.set_font("helvetica", 'B', 20)
    pdf.set_text_color(26, 28, 44) # Corporate Blue
    pdf.cell(0, 15, title, new_x="LMARGIN", new_y="NEXT", align='C')
    pdf.set_draw_color(79, 172, 254)
    pdf.line(20, pdf.get_y(), 190, pdf.get_y())
    pdf.ln(10)
    
    # Body
    pdf.set_text_color(40, 44, 52)
    for line in text.split('\n'):
        line = line.strip()
        if not line:
            pdf.ln(3)
            continue
            
        if line.startswith('# '):
            continue # Already used for title header
        elif line.startswith('## '):
            pdf.ln(5)
            pdf.set_font("helvetica", 'B', 14)
            pdf.set_text_color(26, 28, 44)
            pdf.cell(0, 10, line.replace('## ', ''), new_x="LMARGIN", new_y="NEXT")
            pdf.set_font("helvetica", size=11)
            pdf.set_text_color(40, 44, 52)
        elif line.startswith('### '):
            pdf.ln(3)
            pdf.set_font("helvetica", 'B', 12)
            pdf.cell(0, 8, line.replace('### ', ''), new_x="LMARGIN", new_y="NEXT")
            pdf.set_font("helvetica", size=11)
        elif line.startswith('- ') or line.startswith('* '):
            pdf.set_font("helvetica", size=11)
            # Indented bullet point
            pdf.set_x(15)
            pdf.write(6, chr(149) + " ") # Standard bullet
            
            # Handle bold within bullets
            content = line[2:]
            parts = content.split('**')
            for i, part in enumerate(parts):
                if i % 2 == 1:
                    pdf.set_font("helvetica", 'B', 11)
                else:
                    pdf.set_font("helvetica", size=11)
                pdf.write(6, part)
            pdf.ln()
        else:
            pdf.set_font("helvetica", size=11)
            pdf.set_x(10)
            parts = line.split('**')
            for i, part in enumerate(parts):
                if i % 2 == 1:
                    pdf.set_font("helvetica", 'B', 11)
                else:
                    pdf.set_font("helvetica", size=11)
                pdf.write(6, part)
            pdf.ln()

    return pdf.output()

def get_teacher_data(teacher_id):
    try:
        obj_id = ObjectId(teacher_id)
        teacher = users_col.find_one({"_id": obj_id, "role": "teacher"})
        if not teacher:
            return None
        
        bootcamp_ids = [ObjectId(b) for b in teacher.get("teacherBootcampIds", []) if b]
        domain_ids = [ObjectId(d) for d in teacher.get("teacherDomainIds", []) if d]
        
        bootcamps = list(bootcamps_col.find({"_id": {"$in": bootcamp_ids}}))
        domains = list(domains_col.find({"_id": {"$in": domain_ids}}))
        
        return {
            "teacher": teacher,
            "bootcamps": bootcamps,
            "domains": domains
        }
    except Exception as e:
        print(f"Error fetching teacher: {e}")
        return None

def generate_assignment(prompt, context_data):
    try:
        bootcamp_name = context_data.get('bootcamp_name', 'N/A')
        domain_name = context_data.get('domain_name', 'N/A')
        module = context_data.get('module', 'N/A')
        
        structured_prompt = f"""
You are Course Director at a High-End Tech Academy. Create a clean, well-structured assignment.

CONTEXT:
- PROGRAM: {bootcamp_name}
- MODULE: {module}
- FOCUS: {prompt}

STYLE GUIDE:
1. Use # for Title, ## for Sections, ### for Sub-sections.
2. NO redundant bolding on headers. 
3. Use bullet points (-) for lists.
4. ONLY bold key technical terms using **term**.
5. Keep paragraphs concise and professional.

REQUIRED STRUCTURE:
# [Title]

## Overview
[A clear 2-3 sentence summary]

## Learning Objectives
- [Objective 1]
- [Objective 2]

## Tech Stack & Constraints
- [Point 1]
- [Point 2]

## Implementation Phases
### Phase 1: Setup
[Tasks]
### Phase 2: Core Development
[Tasks]
### Phase 3: Final Polish
[Tasks]

## Submission Requirements
- [Requirement 1]
- [Requirement 2]

## Grading Rubric
- Implementation: [Weight]%
- Code Quality: [Weight]%
- Documentation: [Weight]%
"""
        response = model.generate_content(structured_prompt)
        return response.text if hasattr(response, "text") else "❌ AI Error: Empty response"
    except Exception as e:
        return f"❌ AI Error: {str(e)}"

# -------------------------
# 🚀 APP ENTRY POINT
# -------------------------

def main():
    st.set_page_config(page_title="Corporate AI Assignment Creator", layout="wide", page_icon="🧠")
    apply_custom_css()

    # --- SESSION STATE ---
    if "teacher_logged_in" not in st.session_state:
        st.session_state.teacher_logged_in = False
    if "teacher_info" not in st.session_state:
        st.session_state.teacher_info = None
    if "generated_content" not in st.session_state:
        st.session_state.generated_content = ""

    # --- SIDEBAR: AUTH & CREDENTIALS ---
    with st.sidebar:
        st.markdown(icon_text("teacher", "Teacher Portal", "1.5rem"), unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        
        if not st.session_state.teacher_logged_in:
            teacher_id_input = st.text_input("Enter Teacher ID", placeholder="Employee Identification Number")
            if st.button("Authenticate System"):
                if teacher_id_input:
                    data = get_teacher_data(teacher_id_input)
                    if data:
                        st.session_state.teacher_info = data
                        st.session_state.teacher_logged_in = True
                        st.rerun()
                    else:
                        st.error("Identification Failed: Record not found.")
                else:
                    st.warning("Please provide Identification Number.")
        else:
            teacher = st.session_state.teacher_info['teacher']
            st.success(f"Session Active: {teacher.get('name', 'Instructor')}")
            st.info(f"{teacher.get('email')}")
            
            if st.button("Terminate Session"):
                st.session_state.teacher_logged_in = False
                st.session_state.teacher_info = None
                st.session_state.generated_content = ""
                st.rerun()

        st.markdown("---")
        st.markdown(icon_text("status", "System Integrity"), unsafe_allow_html=True)
        st.write("🟢 Database: Operational")
        st.write("🟢 Engine: Stable")

    # --- MAIN CONTENT ---
    if not st.session_state.teacher_logged_in:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("<br><br>", unsafe_allow_html=True)
            st.markdown(f'<div style="text-align: center; color: #4facfe;">{ICONS["ai"].replace("24", "80")}</div>', unsafe_allow_html=True)
            st.markdown("<h1 style='text-align: center;'>Assignment Architect</h1>", unsafe_allow_html=True)
            st.markdown("""
            <div style='text-align: center; opacity: 0.8;'>
            Welcome to the <b>Enterprise Curriculum Intelligence</b>. <br>
            Please authenticate using your identification number in the secure portal.
            </div>
            """, unsafe_allow_html=True)
    else:
        # Step 1: Assignment Context
        st.markdown(icon_text("config", "Technical Configuration", "1.5rem"), unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        
        t_info = st.session_state.teacher_info
        bootcamps = t_info['bootcamps']
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            bootcamp_map = {str(b['_id']): b.get('name', 'Unnamed Bootcamp') for b in bootcamps}
            selected_bootcamp_id = st.selectbox("Program Track", options=list(bootcamp_map.keys()), format_func=lambda x: bootcamp_map[x])
        
        with col2:
            filtered_domains = [d for d in t_info['domains'] if d.get('bootcamp') == ObjectId(selected_bootcamp_id)]
            if not filtered_domains:
                filtered_domains = t_info['domains']
            
            domain_map = {str(d['_id']): d.get('name', 'Unnamed Domain') for d in filtered_domains}
            selected_domain_id = st.selectbox("Department", options=list(domain_map.keys()), format_func=lambda x: domain_map[x])
            
        with col3:
            module = st.selectbox("Specialization Module", ["Modern Frontend", "Advanced Backend", "AI & Machine Learning", "Design Systems (UI/UX)", "Cloud Infrastructure"])

        st.markdown("---")
        
        # Step 2: Prompt and Generation
        col_left, col_right = st.columns([1, 1])
        
        with col_left:
            st.markdown(icon_text("ai", "Inquiry Parameters"), unsafe_allow_html=True)
            prompt = st.text_area("Objective Specification", height=200, placeholder="Define the primary technical objectives for this curriculum module...")
            
            deadline = st.date_input("Deadline Alignment")
            
            if st.button("Generate Architectural Blueprint"):
                if prompt.strip():
                    with st.spinner("Processing intelligence protocols..."):
                        context = {
                            "bootcamp_name": bootcamp_map[selected_bootcamp_id],
                            "module": module
                        }
                        st.session_state.generated_content = generate_assignment(prompt, context)
                else:
                    st.warning("Intelligence input required.")

        with col_right:
            st.markdown(icon_text("assignment", "Blueprint Validation"), unsafe_allow_html=True)
            if st.session_state.generated_content:
                detected_title = auto_extract_title(st.session_state.generated_content)
                st.markdown(f"**Identified Subject:** `{detected_title}`")
                
                edited_text = st.text_area("Validation Console", value=st.session_state.generated_content, height=350)
                current_title = auto_extract_title(edited_text)

                col_b1, col_b2 = st.columns(2)
                with col_b1:
                    if st.button("Deploy to Database"):
                        assignment_doc = {
                            "title": current_title,
                            "description": edited_text,
                            "domain": ObjectId(selected_domain_id),
                            "teacher": ObjectId(st.session_state.teacher_info['teacher']['_id']),
                            "bootcamp": ObjectId(selected_bootcamp_id),
                            "module": module,
                            "deadline": datetime.combine(deadline, datetime.min.time()),
                            "status": "Active",
                            "requiredLinks": [],
                            "createdAt": datetime.utcnow(),
                            "updatedAt": datetime.utcnow()
                        }
                        
                        try:
                            assignments_col.insert_one(assignment_doc)
                            st.balloons()
                            st.success("Deployment Successful.")
                        except Exception as e:
                            st.error(f"Deployment Error: {e}")
                
                with col_b2:
                    pdf_data = create_pdf(edited_text, current_title)
                    st.download_button(
                        label="Export to PDF",
                        data=bytes(pdf_data),
                        file_name=f"{current_title.replace(' ', '_')}.pdf",
                        mime="application/pdf",
                    )
            else:
                st.info("Awaiting architectural blueprint generation.")


    st.markdown('<div class="footer">Corporate Assignment Intelligence v2.0 | Powered by Gemini 2.0 Flash</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()