import streamlit as st
import requests
import json
import os
from io import BytesIO
from fpdf import FPDF

# Set page config
st.set_page_config(
    page_title="Document Processing Pipeline",
    page_icon="📄",
    layout="wide"
)

# Custom CSS styling
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
    .output-box {
        background-color: #333333;
        border-radius: 5px;
        padding: 20px;
        margin-top: 20px;
        min-height: 100px;
    }
    .header {
        color: #FFD700;
    }
    </style>
    """, unsafe_allow_html=True)

# API base URL
API_URL = "http://localhost:8000"

# Initialize session state
if 'mode' not in st.session_state:
    st.session_state.mode = 'manual'
if 'output' not in st.session_state:
    st.session_state.output = None

# Header
st.markdown("<h1 class='header'>Document Processing Pipeline</h1>", unsafe_allow_html=True)

# Mode selection
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("Manual Mode"):
        st.session_state.mode = 'manual'
with col2:
    if st.button("Sequential Mode"):
        st.session_state.mode = 'sequential'
with col3:
    if st.button("Rules Matching"):
        st.session_state.mode = 'rules_matching'


st.markdown("---")

# Rules Matching Mode
if st.session_state.mode == 'rules_matching':
    st.markdown("### Rules Matching Pipeline")

    rules_file = st.file_uploader("Upload a PDF file for rules matching", type=["pdf"], key="rules_match_file")

    if st.button("Run Rules Matching"):
        if rules_file:
            with st.spinner("Running rules matching..."):
                response = requests.post(f"{API_URL}/full-compliance-pipeline", files={"file": rules_file})
                if response.status_code == 200:
                    result = response.json()
                    
                    # Correct key names
                    match_result = result.get("semantic_gap_analysis", "N/A")
                    generated_rules = result.get("generated_rules", "N/A")
                    compliance_result = result.get("compliance_result", "N/A")
                    extracted_text = result.get("extracted_text", "N/A")

                    st.session_state.output = {
                        "generated_rules": generated_rules,
                        "compliance_result": compliance_result,
                        "match_result": match_result,
                        "extracted_text": extracted_text
                    }
                    st.success("Rules matched successfully!")

                    st.markdown("#### 🧾 Extracted Text")
                    st.code(extracted_text)
                    st.markdown("#### 🔍 Match Result (List Format)")
                    try:
                        if isinstance(match_result, list) and all(isinstance(item, dict) for item in match_result):
                            for idx, item in enumerate(match_result, start=1):
                                st.markdown(f"**Result {idx}:**")
                                for key, value in item.items():
                                    st.markdown(f"- **{key}**: {value}")
                                st.markdown("---")
                        else:
                            st.code(json.dumps(match_result, indent=2), language="json")
                    except Exception as e:
                        st.error(f"Error displaying match result: {e}")                    
                    

                    st.markdown("#### 📜 Generated Rules")
                    st.code(json.dumps(generated_rules, indent=2) if isinstance(generated_rules, (dict, list)) else str(generated_rules), language="json")

                    st.markdown("#### ✅ Compliance Result")
                    st.code(json.dumps(compliance_result, indent=2) if isinstance(compliance_result, (dict, list)) else str(compliance_result), language="json")

                else:
                    st.error(f"Error: {response.text}")
        else:
            st.warning("Please upload a PDF file first.")

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
        brd_file = st.file_uploader("Upload a PDF for BRD Generation", type=["pdf"], key="brd_file")
        if st.button("Generate BRD with Rules"):
            if brd_file:
                with st.spinner("Running full compliance pipeline for BRD..."):
                    # Post the uploaded file bytes correctly
                    response = requests.post(
                        f"{API_URL}/full-compliance-pipeline",
                        files={"file": ("uploaded_brd.pdf", brd_file.getvalue(), "application/pdf")}
                    )

                    if response.status_code == 200:
                        result = response.json()
                        st.session_state.output = result

                        # Download buttons for rules JSON and BRD PDF
                        col1, col2 = st.columns(2)
                        with col1:
                            rules_json = json.dumps(result.get("rules", {}), indent=2, ensure_ascii=False)
                            st.download_button(
                                label="Download BRD Rules (JSON)",
                                data=rules_json,
                                file_name="generated_brd_rules.json",
                                mime="application/json"
                            )

                        with col2:
                            # Assuming the backend sends back PDF bytes or a path - let's fetch again to be sure
                            # If your API returns 'pdf_path', you may need a separate endpoint to fetch the file
                            # But here, we'll call /generate-brd-pdf again with the same file
                            pdf_response = requests.post(
                                f"{API_URL}/generate-brd-pdf",
                                files={"file": ("uploaded_brd.pdf", brd_file.getvalue(), "application/pdf")}
                            )

                            if pdf_response.status_code == 200:
                                st.download_button(
                                    label="Download BRD (PDF)",
                                    data=pdf_response.content,
                                    file_name="generated_brd.pdf",
                                    mime="application/pdf"
                                )
                            else:
                                st.error("Failed to fetch BRD PDF.")

                        # Display the BRD text nicely
                        brd_text = result.get("brd_text", None)
                        if brd_text:
                            st.markdown("#### 📄 Business Requirement Document (BRD) Text")
                            # Show in a scrollable container or markdown with limited height
                            st.text_area("BRD Content", value=brd_text, height=400)

                        # Display BRD rules JSON
                        st.markdown("#### 📘 Generated BRD and Compliance Rules")
                        brd_rules_display = result.get("rules", {})
                        if isinstance(brd_rules_display, (dict, list)):
                            st.code(json.dumps(brd_rules_display, indent=2), language="json")
                        else:
                            st.text(str(brd_rules_display))

                        # Display Summary if present
                        if "summary" in result:
                            st.markdown("#### 📝 Document Summary")
                            summary = result["summary"]
                            if isinstance(summary, (dict, list)):
                                st.code(json.dumps(summary, indent=2), language="json")
                            else:
                                st.text(str(summary))

                    else:
                        st.error(f"Error: {response.text}")
            else:
                st.warning("Please upload a PDF file for BRD Generation")
                    

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
if st.session_state.mode == 'sequential':
    st.markdown("### Full Pipeline Processing")

    uploaded_file = st.file_uploader("Upload a PDF file for full pipeline processing", type=["pdf"], key="pipeline_file")
    brd_requirements_file = st.file_uploader("Upload a PDF for BRD requirements", type=["pdf"], key="pipeline_brd_file")

    def generate_pdf(data, brd_rules):
        pdf = FPDF()
        pdf.add_page()

        # Set base font
        pdf.set_font("Times", size=14)
        pdf.cell(0, 10, "Full Pipeline Processing Result", ln=True, align="C")
        pdf.ln(5)

        # --- Summary Section ---
        pdf.set_font("Times", size=14)
        pdf.cell(0, 10, "Summary", ln=True)
        pdf.set_font("Times", size=12)
        pdf.multi_cell(0, 8, data.get("summary", "N/A"))
        pdf.ln(5)

        # --- Requirements Section ---
        pdf.set_font("Times", size=14)
        pdf.cell(0, 10, "Generated Requirements", ln=True)
        pdf.set_font("Times", size=12)
        requirements = data.get("requirements", [])
        if isinstance(requirements, list):
            for req in requirements:
                pdf.multi_cell(0, 8, f"- {req}")
        else:
            pdf.multi_cell(0, 8, str(requirements))
        pdf.ln(5)

        # --- Compliance Result ---
        pdf.set_font("Times", size=14)
        pdf.cell(0, 10, "Compliance Result", ln=True)
        pdf.set_font("Times", size=12)
        compliance = data.get("compliance_result", {})
        pdf.multi_cell(0, 8, json.dumps(compliance, indent=2))
        pdf.ln(5)

        # --- BRD Rules ---
        pdf.set_font("Times", size=14)
        pdf.cell(0, 10, "BRD Rules", ln=True)
        pdf.set_font("Times", size=12)
        if isinstance(brd_rules, list):
            for rule in brd_rules:
                pdf.multi_cell(0, 8, f"- {rule}")
        else:
            pdf.multi_cell(0, 8, str(brd_rules))
        pdf.ln(5)

        # --- Generate PDF to BytesIO ---
        pdf_bytes = pdf.output(dest='S').encode('latin1')
        pdf_output = BytesIO(pdf_bytes)
        pdf_output.seek(0)

        return pdf_output



    if st.button("Run Full Pipeline"):
        if uploaded_file is not None and brd_requirements_file is not None:
            with st.spinner("Processing your document through the full pipeline..."):
                # Call full pipeline endpoint
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
                process_response = requests.post(f"{API_URL}/run-full-pipeline", files=files)

                if process_response.status_code == 200:
                    # Call BRD generation endpoint
                    brd_response = requests.post(
                        f"{API_URL}/generate-brd-and-rules",
                        files={"file": (brd_requirements_file.name, brd_requirements_file.getvalue(), "application/pdf")}
                    )

                    if brd_response.status_code == 200:
                        result = process_response.json()
                        brd_result = brd_response.json()

                        # Display pipeline results nicely
                        st.subheader("Summary")
                        st.write(result.get("summary", "No summary available."))

                        st.subheader("Requirements")
                        requirements = result.get("requirements", [])
                        if isinstance(requirements, list):
                            for req in requirements:
                                st.markdown(f"- {req}")
                        else:
                            st.write(requirements)

                        # st.subheader("Compliance Result")
                        # st.json(result.get("compliance_result", {}))

                        st.subheader("BRD Rules")
                        rules = brd_result.get("rules", [])
                        if isinstance(rules, list):
                            for rule in rules:
                                st.markdown(f"- {rule}")
                        else:
                            st.write(rules)

                        # Generate downloadable PDF with all results
                        pdf_file = generate_pdf(result, rules)

                        st.success("Full pipeline completed successfully!")

                        # col1, col2 = st.columns(2)
                        # with col1:
                        #     st.download_button(
                        #         label="Download BRD (JSON)",
                        #         data=json.dumps(brd_result["rules"], indent=2),
                        #         file_name="full_pipeline_brd.json",
                        #         mime="application/json"
                        #     )
                        # with col2:
                        #     st.download_button(
                        #         label="Download Compliance Rules (JSON)",
                        #         data=json.dumps(brd_result["rules"], indent=2),
                        #         file_name="full_pipeline_rules.json",
                        #         mime="application/json"
                        #     )

                        # st.download_button(
                        #     label="Download Full Pipeline Result (PDF)",
                        #     data=pdf_file,
                        #     file_name="full_pipeline_result.pdf",
                        #     mime="application/pdf"
                        # )

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
    output = st.session_state.output

    st.markdown("<div class='output-box'>", unsafe_allow_html=True)

    st.markdown("#### 📜 Generated Rules")
    st.code(output.get("generated_rules", "No rules generated"), language="json")

    st.markdown("#### ✅ Compliance Result")
    st.code(output.get("compliance_result", "No compliance result"), language="json")

    st.markdown("#### 🔍 Match Result")
    st.code(output.get("match_result", "No match result"), language="json")

    st.markdown("</div>", unsafe_allow_html=True)

    if st.button("Clear Output"):
        st.session_state.output = None
else:
    st.markdown("<div class='output-box'>Output will appear here after processing</div>", 
                unsafe_allow_html=True)