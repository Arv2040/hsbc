import streamlit as st
import requests
import json

# Backend API URL
API_BASE = "http://localhost:8000"  # Change if needed

# Set page config
st.set_page_config(page_title="HSBC AI Data Pipeline", layout="wide")
st.title("🔍 HSBC Unified AI Processing")

# Custom CSS for styling
st.markdown("""
<style>
    /* Green Run Pipeline button */
    .green-button {
        background-color: #28a745 !important;
        color: white !important;
        border: none !important;
        padding: 0.5rem 1rem !important;
        border-radius: 0.25rem !important;
        font-weight: 500 !important;
    }
    /* Box around agent buttons */
    .agent-box {
        border: 2px solid #0066cc;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 20px;
        background-color: #f8f9fa;
    }
    /* Agent buttons */
    .agent-button {
        width: 100%;
        margin: 5px 0;
    }
    /* Better spacing */
    .section-spacing {
        margin-top: 30px;
    }
</style>
""", unsafe_allow_html=True)

# UI control for execution mode
st.markdown("## 🔧 Execution Mode")
exec_mode = st.radio("Choose how to run the pipeline:", ["Sequential", "Manual"], horizontal=True)

# Agent buttons in a box
with st.container():
    st.markdown('<div class="agent-box">', unsafe_allow_html=True)
    st.markdown("### 🛠️ Agents")
    
    # Horizontal button row
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    if col1.button("1️⃣ Ingest Emails", key="ingest", help="Fetch emails from server"):
        with st.spinner("Fetching emails..."):
            res = requests.get(f"{API_BASE}/emails")
            st.json(res.json())
    
    if col2.button("2️⃣ Preprocess File", key="preprocess", help="Clean and prepare text data"):
        uploaded = st.file_uploader("Upload File for Preprocessing", type=["txt"])
        if uploaded and st.button("Run Preprocessing", key="run_preprocess"):
            files = {"file": uploaded.getvalue()}
            res = requests.post(f"{API_BASE}/preprocess/", files=files)
            st.json(res.json())
    
    if col3.button("3️⃣ Summarize Content", key="summarize", help="Generate document summary"):
        input_data = st.text_area("Paste content to summarize")
        if input_data and st.button("Run Summarization", key="run_summarize"):
            res = requests.post(f"{API_BASE}/summarize-content", json=input_data)
            st.json(res.json())
    
    if col4.button("4️⃣ Generate Requirements", key="requirements", help="Create business requirements"):
        with st.spinner("Generating requirements..."):
            res = requests.get(f"{API_BASE}/generate-requirements")
            st.json(res.json())
    
    if col5.button("5️⃣ Check Compliance", key="compliance", help="Validate against regulations"):
        feedback_text = st.text_area("Enter structured feedback JSON")
        if feedback_text and st.button("Run Compliance Check", key="run_compliance"):
            feedback = json.loads(feedback_text)
            res = requests.post(f"{API_BASE}/check-compliance", json=feedback)
            st.json(res.json())
    
    if col6.button("6️⃣ View Feedback Log", key="feedback", help="See all feedback entries"):
        with st.spinner("Retrieving feedback log..."):
            res = requests.get(f"{API_BASE}/feedback-log")
            st.json(res.json())
    
    st.markdown('</div>', unsafe_allow_html=True)

# Sequential execution
st.markdown('<div class="section-spacing">', unsafe_allow_html=True)
if exec_mode == "Sequential":
    if st.button("🚀 Run Full Pipeline", key="run_pipeline", 
                help="Run all agents in sequence", 
                type="primary", 
                use_container_width=True, 
                disabled=(exec_mode != "Sequential")):
        st.subheader("Running All Agents In Sequence")
        try:
            steps = []
            steps.append(("Fetching Emails", requests.get(f"{API_BASE}/emails")))
            steps.append(("Generating Requirements", requests.get(f"{API_BASE}/generate-requirements")))
            
            dummy_text = {"text": "This is some dummy text for summarization."}
            steps.append(("Summarizing", requests.post(f"{API_BASE}/summarize-content", json=dummy_text)))
            
            dummy_feedback = {
                "requirement": "Requirement example",
                "document": "Document example",
                "notes": "Some notes"
            }
            steps.append(("Checking Compliance", requests.post(f"{API_BASE}/check-compliance", json=dummy_feedback)))
            
            for label, resp in steps:
                st.markdown(f"### ✅ {label}")
                st.json(resp.json())
        
        except Exception as e:
            st.error(f"Error occurred: {e}")
st.markdown('</div>', unsafe_allow_html=True)