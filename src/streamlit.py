import streamlit as st
import requests
import json
from typing import Optional
from pydantic import BaseModel

# Backend API URL
API_BASE = "http://localhost:8000"  # Change if needed

st.set_page_config(page_title="HSBC AI Data Pipeline", layout="wide")
st.title("🔍 HSBC Unified AI Processing")

# Custom CSS for better styling
st.markdown("""
<style>
    .stButton>button {
        background-color: #0066cc;
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 0.25rem;
        font-weight: 500;
    }
    .stButton>button:hover {
        background-color: #0052a3;
    }
    .step-card {
        border-left: 4px solid #0066cc;
        padding: 1rem;
        margin: 1rem 0;
        background-color: #f8f9fa;
        border-radius: 0.25rem;
    }
    .success-badge {
        background-color: #28a745;
        color: white;
        padding: 0.25rem 0.5rem;
        border-radius: 0.25rem;
        font-size: 0.75rem;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

class Feedback(BaseModel):
    requirement: str
    feedback: str
    reviewer: Optional[str] = "Anonymous"
    compliant: Optional[bool] = None

# Initialize session state
if 'pipeline_data' not in st.session_state:
    st.session_state.pipeline_data = {
        'raw_text': None,
        'processed_text': None,
        'summary': None,
        'requirements': None,
        'compliance_result': None
    }

# File Upload Section
st.markdown("## 📤 Step 1: Upload Document")
uploaded_file = st.file_uploader("Upload your document (TXT, PDF, DOCX)", 
                                type=["txt", "pdf", "docx"],
                                key="file_uploader")

if uploaded_file:
    if st.button("Process Document"):
        with st.spinner("Uploading and processing document..."):
            try:
                # Step 1: Preprocessing
                files = {"file": uploaded_file.getvalue()}
                preprocess_res = requests.post(f"{API_BASE}/preprocess/", files=files)
                st.session_state.pipeline_data['processed_text'] = preprocess_res.json()
                
                # Display preprocessing results
                with st.expander("Preprocessing Results", expanded=True):
                    st.markdown("<div class='step-card'>", unsafe_allow_html=True)
                    st.markdown("### ✅ Document Preprocessed")
                    st.json(st.session_state.pipeline_data['processed_text'])
                    st.markdown("</div>", unsafe_allow_html=True)
                
                # Step 2: Summarization
                if 'clean_text' in st.session_state.pipeline_data['processed_text']:
                    summary_res = requests.post(
                        f"{API_BASE}/summarize-content",
                        json=st.session_state.pipeline_data['processed_text']['clean_text']
                    )
                    st.session_state.pipeline_data['summary'] = summary_res.json()
                    
                    with st.expander("Summary Results", expanded=True):
                        st.markdown("<div class='step-card'>", unsafe_allow_html=True)
                        st.markdown("### ✅ Content Summarized")
                        st.write(st.session_state.pipeline_data['summary']['summary'])
                        st.markdown("</div>", unsafe_allow_html=True)
                
                # Step 3: Requirement Generation
                req_res = requests.get(f"{API_BASE}/generate-requirements")
                st.session_state.pipeline_data['requirements'] = req_res.json()
                
                with st.expander("Generated Requirements", expanded=True):
                    st.markdown("<div class='step-card'>", unsafe_allow_html=True)
                    st.markdown("### ✅ Requirements Generated")
                    requirements = st.session_state.pipeline_data['requirements']['requirements']
                    if isinstance(requirements, str):
                        st.write(requirements)
                    else:
                        for i, req in enumerate(requirements, 1):
                            st.markdown(f"{i}. {req}")
                    st.markdown("</div>", unsafe_allow_html=True)
                
                # Step 4: Compliance Check
                sample_feedback = Feedback(
                    requirement="Sample requirement for compliance check",
                    feedback="Sample feedback",
                    reviewer="System",
                    compliant=True
                )
                compliance_res = requests.post(
                    f"{API_BASE}/check-compliance",
                    json=sample_feedback.model_dump()
                )
                st.session_state.pipeline_data['compliance_result'] = compliance_res.json()
                
                with st.expander("Compliance Results", expanded=True):
                    st.markdown("<div class='step-card'>", unsafe_allow_html=True)
                    st.markdown("### ✅ Compliance Checked")
                    st.json(st.session_state.pipeline_data['compliance_result'])
                    st.markdown("</div>", unsafe_allow_html=True)
                
                st.success("Pipeline execution completed successfully!")
                
            except Exception as e:
                st.error(f"Error occurred during pipeline execution: {str(e)}")

# Manual Execution Section
st.markdown("## 🛠 Manual Execution Options")
if st.session_state.pipeline_data['processed_text']:
    if st.button("Re-run Summarization Only"):
        with st.spinner("Summarizing content..."):
            summary_res = requests.post(
                f"{API_BASE}/summarize-content",
                json=st.session_state.pipeline_data['processed_text']['clean_text']
            )
            st.session_state.pipeline_data['summary'] = summary_res.json()
            st.success("Summarization updated!")
            st.json(st.session_state.pipeline_data['summary'])

if st.session_state.pipeline_data['summary']:
    if st.button("Re-generate Requirements"):
        with st.spinner("Generating requirements..."):
            req_res = requests.get(f"{API_BASE}/generate-requirements")
            st.session_state.pipeline_data['requirements'] = req_res.json()
            st.success("Requirements updated!")
            st.json(st.session_state.pipeline_data['requirements'])

# Feedback Section
st.markdown("## 💬 Feedback System")
feedback_tab1, feedback_tab2 = st.tabs(["Submit Feedback", "View Feedback Log"])

with feedback_tab1:
    with st.form("feedback_form"):
        st.write("Submit your feedback on the generated requirements")
        req = st.text_area("Requirement")
        feedback = st.text_area("Feedback")
        reviewer = st.text_input("Reviewer Name")
        compliant = st.checkbox("Is Compliant?")
        rating = st.slider("Rating (1-5)", 1, 5, 5)
        
        submitted = st.form_submit_button("Submit Feedback")
        if submitted:
            feedback_data = {
                "requirement": req,
                "feedback": feedback,
                "reviewer": reviewer,
                "compliant": compliant,
                "rating": rating
            }
            try:
                response = requests.post(
                    f"{API_BASE}/submit-feedback",
                    json=feedback_data
                )
                if response.status_code == 200:
                    st.success("Feedback submitted successfully!")
                else:
                    st.error(f"Error: {response.text}")
            except Exception as e:
                st.error(f"Connection error: {str(e)}")

with feedback_tab2:
    if st.button("Refresh Feedback Log"):
        with st.spinner("Loading feedback..."):
            try:
                response = requests.get(f"{API_BASE}/feedback-log")
                if response.status_code == 200:
                    feedback_log = response.json()["log"]
                    if feedback_log:
                        for item in feedback_log:
                            with st.expander(f"Feedback from {item.get('reviewer', 'Anonymous')}"):
                                st.write(f"*Requirement:* {item['requirement']}")
                                st.write(f"*Feedback:* {item['feedback']}")
                                st.write(f"*Compliant:* {'✅' if item['compliant'] else '❌'}")
                                st.write(f"*Rating:* {'⭐' * item.get('rating', 1)}")
                                st.write(f"*Date:* {item.get('timestamp', 'Unknown')}")
                    else:
                        st.info("No feedback entries yet.")
                else:
                    st.error(f"Error: {response.text}")
            except Exception as e:
                st.error(f"Connection error: {str(e)}")

# Governance Section
st.markdown("## 📜 Governance Logs")
if st.button("View Governance Logs"):
    with st.spinner("Retrieving governance logs..."):
        st.info("Governance logs would be displayed here in a production environment")
        sample_logs = [
            {
                "timestamp": "2023-01-01T12:00:00",
                "agent": "preprocess",
                "input": "Document content...",
                "output": "Processed content...",
                "status": "success"
            },
            {
                "timestamp": "2023-01-01T12:05:00",
                "agent": "summarize",
                "input": "Processed content...",
                "output": "Summary content...",
                "status": "success"
            }
        ]
        for log in sample_logs:
            with st.expander(f"{log['agent']} at {log['timestamp']}"):
                st.json(log)