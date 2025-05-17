import streamlit as st
import requests
import json
import tempfile
import os

# Set page config
st.set_page_config(
    page_title="Document Processing Pipeline",
    page_icon="📄",
    layout="wide"
)

# Custom CSS for styling
st.markdown("""
    <style>
    .stApp {
        background-color: #000000;
        color: #ffffff;
    }
    .stButton>button {
        background-color: #FFD700;
        color: #000000;
        border: none;
        padding: 10px 24px;
        border-radius: 4px;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #FFC000;
        color: #000000;
    }
    .stTextInput>div>div>input, .stTextArea>div>div>textarea {
        background-color: #333333;
        color: #ffffff;
    }
    .stSelectbox>div>div>select {
        background-color: #333333;
        color: #ffffff;
    }
    .stFileUploader>div>div>div>button {
        background-color: #FFD700;
        color: #000000;
    }
    .output-box {
        background-color: #333333;
        border-radius: 5px;
        padding: 20px;
        margin-top: 20px;
        min-height: 200px;
    }
    .header {
        color: #FFD700;
    }
    .mode-button {
        margin: 0 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# API configuration
API_URL = "http://localhost:8000"

# Initialize session state
if 'mode' not in st.session_state:
    st.session_state.mode = 'manual'
if 'output' not in st.session_state:
    st.session_state.output = None

# Header
st.markdown("<h1 class='header'>Document Processing Pipeline</h1>", unsafe_allow_html=True)

# Mode selection
col1, col2 = st.columns(2)
with col1:
    if st.button("Manual Mode", key="manual_mode"):
        st.session_state.mode = 'manual'
with col2:
    if st.button("Sequential Mode", key="sequential_mode"):
        st.session_state.mode = 'sequential'

st.markdown("---")

# Manual Mode
if st.session_state.mode == 'manual':
    st.markdown("### Manual Processing Steps")
    
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "Ingestion", "BRD Generation", "Preprocessing", 
        "Summarization", "Requirements", "Compliance", "Feedback"
    ])
    
    with tab1:
        st.markdown("#### PDF Ingestion")
        uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"], key="ingestion_file")
        if st.button("Process PDF"):
            if uploaded_file is not None:
                files = {"file": uploaded_file.getvalue()}
                response = requests.post(f"{API_URL}/ingestion", files=files)
                if response.status_code == 200:
                    st.session_state.output = response.json()
                    st.success("PDF processed successfully!")
                else:
                    st.error(f"Error: {response.text}")
            else:
                st.warning("Please upload a PDF file first")
    
    with tab2:
        st.markdown("#### BRD Generation")
        brd_file = st.file_uploader("Upload requirements PDF", type=["pdf"], key="brd_file")
        if st.button("Generate BRD with Rules"):
            if brd_file:
                with st.spinner("Generating BRD and compliance rules..."):
                    response = requests.post(
                        f"{API_URL}/generate-brd-and-rules",
                        files={"file": brd_file}
                    )
                    if response.status_code == 200:
                        result = response.json()
                        st.session_state.output = result
                        
                        # Download buttons
                        col1, col2 = st.columns(2)
                        with col1:
                            st.download_button(
                                label="Download BRD (JSON)",
                                data=json.dumps(result["rules"], indent=2),
                                file_name="generated_brd.json",
                                mime="application/json"
                            )
                        with col2:
                            st.download_button(
                                label="Download Compliance Rules",
                                data=json.dumps(result["rules"], indent=2),
                                file_name="compliance_rules.json",
                                mime="application/json"
                            )
                        
                        st.success("BRD and rules generated successfully!")
                    else:
                        st.error(f"Error: {response.text}")
            else:
                st.warning("Please upload a requirements PDF first")
    
    with tab3:
        st.markdown("#### PDF Preprocessing")
        preprocess_file = st.file_uploader("Upload a PDF file", type=["pdf"], key="preprocess_file")
        if st.button("Preprocess PDF"):
            if preprocess_file is not None:
                response = requests.post(f"{API_URL}/preprocess/", files={"file": preprocess_file})
                if response.status_code == 200:
                    st.session_state.output = response.json()
                    st.success("PDF preprocessed successfully!")
                else:
                    st.error(f"Error: {response.text}")
            else:
                st.warning("Please upload a PDF file first")
    
    with tab4:
        st.markdown("#### PDF Summarization")
        summarize_file = st.file_uploader("Upload a PDF file", type=["pdf"], key="summarize_file")
        if st.button("Summarize PDF"):
            if summarize_file is not None:
                response = requests.post(f"{API_URL}/summarize-content", files={"file": summarize_file})
                if response.status_code == 200:
                    st.session_state.output = response.json()
                    st.success("PDF summarized successfully!")
                else:
                    st.error(f"Error: {response.text}")
            else:
                st.warning("Please upload a PDF file first")
    
    with tab5:
        st.markdown("#### Generate Requirements")
        if st.button("Generate Requirements"):
            response = requests.get(f"{API_URL}/generate-requirements")
            if response.status_code == 200:
                st.session_state.output = response.json()
                st.success("Requirements generated successfully!")
            else:
                st.error(f"Error: {response.text}")
    
    with tab6:
        st.markdown("#### Check Compliance")
        requirement_file = st.file_uploader("Upload requirements PDF", type=["pdf"], key="requirement_file")
        if st.button("Check Compliance"):
            if requirement_file is not None:
                response = requests.post(
                    f"{API_URL}/check-compliance",
                    files={"requirements_file": requirement_file}
                )
                if response.status_code == 200:
                    st.session_state.output = response.json()
                    st.success("Compliance checked successfully!")
                else:
                    st.error(f"Error: {response.text}")
            else:
                st.warning("Please upload a requirements PDF file")
    
    with tab7:
        st.markdown("#### Feedback Management")
        feedback_requirement = st.text_area("Requirement", height=68, key="feedback_req")
        feedback_text = st.text_area("Feedback Text", height=100, key="feedback_text_area")
        feedback_rating = st.slider("Rating (1-5)", 1, 5, 3, key="feedback_rating")
        
        if st.button("Submit Feedback"):
            if feedback_requirement and feedback_text:
                payload = {
                    "requirement": feedback_requirement,
                    "feedback": feedback_text,
                    "rating": feedback_rating
                }
                response = requests.post(
                    f"{API_URL}/submit-feedback",
                    json=payload
                )
                if response.status_code == 200:
                    st.session_state.output = response.json()
                    st.success("Feedback submitted successfully!")
                else:
                    st.error(f"Error: {response.text}")
            else:
                st.warning("Please enter both requirement and feedback text")
        
        if st.button("View Feedback Log"):
            response = requests.get(f"{API_URL}/feedback-log")
            if response.status_code == 200:
                st.session_state.output = response.json()
                st.success("Feedback log retrieved successfully!")
            else:
                st.error(f"Error: {response.text}")

# Sequential Mode
else:
    # Sequential Mode

    st.markdown("### Full Pipeline Processing")

    # Main input for full pipeline (e.g., a policy or document)
    uploaded_file = st.file_uploader("Upload a PDF file for full pipeline processing", type=["pdf"], key="pipeline_file")

    # Separate input for BRD requirements
    brd_requirements_file = st.file_uploader("Upload a PDF for BRD requirements", type=["pdf"], key="pipeline_brd_file")

    if st.button("Run Full Pipeline"):
        if uploaded_file is not None and brd_requirements_file is not None:
            with st.spinner("Processing your document through the full pipeline..."):
                # Step 1: Process main document
                files = {"file": uploaded_file.getvalue()}
                process_response = requests.post(f"{API_URL}/run-full-pipeline", files=files)

                if process_response.status_code == 200:
                    # Step 2: Generate BRD from a *different* file
                    brd_response = requests.post(
                        f"{API_URL}/generate-brd-and-rules",
                        files={"file": brd_requirements_file.getvalue()}
                    )

                    if brd_response.status_code == 200:
                        result = process_response.json()
                        brd_result = brd_response.json()

                        # Combine results
                        full_result = {
                            **result,
                            "brd_generation": {
                                "status": "success",
                                "rules": brd_result["rules"]
                            }
                        }

                        st.session_state.output = full_result
                        st.success("Full pipeline completed successfully!")

                        # Download buttons
                        col1, col2 = st.columns(2)
                        with col1:
                            st.download_button(
                                label="Download BRD (JSON)",
                                data=json.dumps(brd_result["rules"], indent=2),
                                file_name="full_pipeline_brd.json",
                                mime="application/json"
                            )
                        with col2:
                            st.download_button(
                                label="Download Compliance Rules",
                                data=json.dumps(brd_result["rules"], indent=2),
                                file_name="full_pipeline_rules.json",
                                mime="application/json"
                            )
                    else:
                        st.error(f"BRD generation error: {brd_response.text}")
                else:
                    st.error(f"Pipeline processing error: {process_response.text}")
        else:
            st.warning("Please upload both files: main document and BRD requirements PDF")


# Output display
st.markdown("---")
st.markdown("### Output")

if st.session_state.output is not None:
    output_box = st.empty()
    with output_box.container():
        st.markdown(f"<div class='output-box'><pre>{json.dumps(st.session_state.output, indent=2)}</pre></div>", 
                    unsafe_allow_html=True)
        
        if st.button("Clear Output"):
            st.session_state.output = None
            output_box.empty()
else:
    st.markdown("<div class='output-box'>Output will appear here after processing</div>", 
                unsafe_allow_html=True)