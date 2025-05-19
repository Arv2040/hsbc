
import streamlit as st
import requests
import json
import io

# Set page config with HSBC styling
st.set_page_config(
    page_title="BRD Generator & Compliance System",
    page_icon="📄",
    layout="wide"
)

# Custom CSS for HSBC-style UI
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
        white-space: pre-wrap;
    }
    .header {
        color: #FFD700;
    }
    .agent-container {
        background-color: #222222;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 20px;
    }
    .agent-name {
        color: #FFD700;
        font-size: 1.2em;
        font-weight: bold;
    }
    .agent-task {
        font-style: italic;
        margin: 5px 0 10px 0;
    }
    .agent-output {
        background-color: #333333;
        padding: 10px;
        border-radius: 5px;
        margin: 10px 0;
        white-space: pre-wrap;
    }
    .agent-summary {
        color: #AAAAAA;
        font-size: 0.9em;
    }
    </style>
""", unsafe_allow_html=True)

BACKEND_URL = "http://localhost:8000"  # Change if needed

def call_backend(endpoint, files=None, data=None):
    try:
        url = f"{BACKEND_URL}/{endpoint}"
        if files and data:
            response = requests.post(url, files=files, json=data)
        elif files:
            response = requests.post(url, files=files)
        elif data:
            response = requests.post(url, json=data)
        else:
            response = requests.post(url)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Backend error: {response.text}")
            return None
    except Exception as e:
        st.error(f"Connection error: {str(e)}")
        return None

def display_agent_progress(agent_name, task, output=None, summary=None):
    st.markdown(f"<div class='agent-container'>", unsafe_allow_html=True)
    st.markdown(f"<div class='agent-name'>{agent_name}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='agent-task'>{task}</div>", unsafe_allow_html=True)

    if output:
        if isinstance(output, (dict, list)):
            st.json(output)
        else:
            st.markdown(f"<div class='agent-output'>{output}</div>", unsafe_allow_html=True)

    if summary:
        st.markdown(f"<div class='agent-summary'>{summary}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ----- Manual Mode -----
def manual_mode():
    st.markdown("### Manual Mode - Trigger Agents Individually")

    uploaded_file = st.file_uploader("Upload a PDF document", type=["pdf"], key="manual_upload")
    prompt_text = st.text_area("Optional Prompt (for BRD generation)", key="manual_prompt")
    template_file = st.file_uploader("Optional Template PDF (for BRD generation)", type=["pdf"], key="manual_template")

    if not uploaded_file:
        st.warning("Please upload a PDF document to proceed.")
        return

    # Read uploaded file bytes once for repeated requests
    file_bytes = uploaded_file.read()
    template_bytes = None
    if template_file:
        template_bytes = template_file.read()

    # Run each agent on button press, show results individually

    if st.button("Run Ingestion Agent"):
        with st.spinner("Running Ingestion Agent..."):
            files = {"file": (uploaded_file.name, io.BytesIO(file_bytes), uploaded_file.type)}
            result = call_backend("ingestion", files=files)
            if result:
                display_agent_progress("Ingestion Agent", "Extracting text from PDF", result.get("text", ""), "Text extracted successfully")

    if st.button("Run Preprocessing Agent"):
        with st.spinner("Running Preprocessing Agent..."):
            files = {"file": (uploaded_file.name, io.BytesIO(file_bytes), uploaded_file.type)}
            result = call_backend("preprocess", files=files)
            if result:
                display_agent_progress("Preprocessing Agent", "Cleaning and structuring text", result, "Text preprocessed successfully")

    if st.button("Run Summarization Agent"):
        with st.spinner("Running Summarization Agent..."):
            files = {"file": (uploaded_file.name, io.BytesIO(file_bytes), uploaded_file.type)}
            result = call_backend("summarize-content", files=files)
            if result:
                display_agent_progress("Summarization Agent", "Creating document summary", result.get("summary", ""), "Content summarized successfully")

    if st.button("Run Requirement Generation Agent"):
        with st.spinner("Running Requirement Generation Agent..."):
            files = {"file": (uploaded_file.name, io.BytesIO(file_bytes), uploaded_file.type)}
            data = {"prompt": prompt_text} if prompt_text else None
            result = call_backend("generate-requirements", files=files, data=data)
            if result:
                display_agent_progress("Requirement Agent", "Generating system requirements", result.get("requirements", []), "Requirements generated successfully")

    if st.button("Run Compliance Agent"):
        with st.spinner("Running Compliance Agent..."):
            files = {"file": (uploaded_file.name, io.BytesIO(file_bytes), uploaded_file.type)}
            result = call_backend("check-compliance", files=files)
            if result:
                display_agent_progress("Compliance Agent", "Validating requirements against standards", result.get("result", {}), "Compliance checked successfully")

    if st.button("Run BRD Generation Agent"):
        with st.spinner("Running BRD Generation Agent..."):
            files = {"file": (uploaded_file.name, io.BytesIO(file_bytes), uploaded_file.type)}
            if template_bytes:
                files["template_file"] = (template_file.name, io.BytesIO(template_bytes), template_file.type)
            data = {"prompt": prompt_text} if prompt_text else None
            result = call_backend("generate-brd", files=files, data=data)
            if result:
                display_agent_progress("BRD Generation Agent", "Creating Business Requirements Document", result.get("brd_text", ""), "BRD generated successfully")
                # Optional: show download link if backend supports it
                pdf_url = f"{BACKEND_URL}/download-brd/"
                st.markdown(f"[Download BRD PDF]({pdf_url})", unsafe_allow_html=True)

# ----- Sequential Mode -----
def sequential_mode():
    st.markdown("### BRD & Compliance System - Sequential Mode")

    uploaded_file = st.file_uploader("Upload a PDF document", type=["pdf"], key="sequential_upload")
    prompt_text = st.text_area("Optional Prompt (for BRD generation)", key="sequential_prompt")
    template_file = st.file_uploader("Optional Template PDF (for BRD generation)", type=["pdf"], key="sequential_template")

    if st.button("Start Process"):

        if not uploaded_file:
            st.warning("Please upload a PDF file first")
            return

        file_bytes = uploaded_file.read()
        template_bytes = None
        if template_file:
            template_bytes = template_file.read()

        # 1. Ingestion Agent
        with st.spinner("Running Ingestion Agent..."):
            files = {"file": (uploaded_file.name, io.BytesIO(file_bytes), uploaded_file.type)}
            ingestion_result = call_backend("ingestion", files=files)
        if ingestion_result is None:
            return

        # Show expander after agent has completed
        with st.expander("🧠 Ingestion Agent - Text extracted successfully", expanded=True):
            display_agent_progress(
                "Ingestion Agent",
                "Extracting text from PDF",
                ingestion_result.get("text", ""),
                "Text extracted successfully"
            )


        # 2. Preprocessing Agent
        with st.spinner("Running Preprocessing Agent..."):
            files = {"file": (uploaded_file.name, io.BytesIO(file_bytes), uploaded_file.type)}
            preprocess_result = call_backend("preprocess", files=files)
        if preprocess_result is None:
            return

        with st.expander("🧹 Preprocessing Agent - Text preprocessed successfully", expanded=True):
            display_agent_progress(
                "Preprocessing Agent",
                "Cleaning and structuring text",
                preprocess_result,
                "Text preprocessed successfully"
            )


        # 3. Summarization Agent
        with st.spinner("Running Summarization Agent..."):
            files = {"file": (uploaded_file.name, io.BytesIO(file_bytes), uploaded_file.type)}
            summarize_result = call_backend("summarize-content", files=files)
        if summarize_result is None:
            return

        with st.expander("📝 Summarization Agent - Content summarized successfully", expanded=True):
            display_agent_progress(
                "Summarization Agent",
                "Creating document summary",
                summarize_result.get("summary", ""),
                "Content summarized successfully"
            )


        # 4. Requirement Generation
        # data = {"prompt": prompt_text} if prompt_text else None
        # with st.spinner("Running Requirement Generation Agent..."):
        #     files = {"file": (uploaded_file.name, io.BytesIO(file_bytes), uploaded_file.type)}
        #     requirement_result = call_backend("generate-requirements", files=files, data=data)
        # if requirement_result is None:
        #     return
        # display_agent_progress(
        #     "Requirement Agent",
        #     "Generating system requirements",
        #     requirement_result.get("requirements", []),
        #     "Requirements generated successfully"
        # )

        # 5. Compliance Check Agent
        with st.spinner("Running Compliance Agent..."):
            files = {"requirements_file": (uploaded_file.name, io.BytesIO(file_bytes), uploaded_file.type)}
            compliance_result = call_backend("check-compliance", files=files)
        if compliance_result is None:
            return

        with st.expander("📋 Compliance Agent - Compliance checked successfully", expanded=True):
            st.markdown("#### Validating requirements against standards")

            result = compliance_result.get("result", {})

            # If result is a list of dicts (preferred for tabular data)
            if isinstance(result, list):
                st.table(result)
            # If result is a single dictionary
            elif isinstance(result, dict):
                df_data = [{"Key": k, "Value": v} for k, v in result.items()]
                st.table(df_data)
            else:
                st.write("Unsupported result format")



        # 6. BRD Generation Agent
        brd_files = {"file": (uploaded_file.name, io.BytesIO(file_bytes), uploaded_file.type)}
        if template_bytes is not None:
            brd_files["template_file"] = (template_file.name, io.BytesIO(template_bytes), template_file.type)

        data = {"prompt": prompt_text} if prompt_text else None

        with st.spinner("Running BRD Generation Agent..."):
            brd_result = call_backend("generate-brd", files=brd_files, data=data)
        if brd_result is None:
            return

        with st.expander("📄 BRD Generation Agent - BRD generated successfully", expanded=True):
            display_agent_progress(
                "BRD Generation Agent",
                "Creating Business Requirements Document",
                brd_result.get("brd_text", ""),
                "BRD generated successfully"
            )

        pdf_url = f"{BACKEND_URL}/download-brd/"
        st.markdown(f"[⬇️ Download BRD PDF]({pdf_url})", unsafe_allow_html=True)



# ----- Rules Matching Mode (placeholder) -----
def rules_matching_mode():
    st.markdown("### Rules Matching Mode (Coming Soon)")
    st.info("This mode is not implemented yet. Please check back later.")

# ----- Main app -----
def main():
    st.markdown("<h1 class='header'>BRD Generator & Compliance System</h1>", unsafe_allow_html=True)
    st.markdown("---")

    mode = st.radio(
        "Select Mode:",
        ("Manual Mode", "Sequential Mode"
        #  , "Rules Matching"
         ),
        horizontal=True,
        label_visibility="hidden"
    )

    st.markdown("---")

    if mode == "Manual Mode":
        manual_mode()
    elif mode == "Sequential Mode":
        sequential_mode()
    else:
        rules_matching_mode()

    st.markdown("---")
    # st.subheader("Feedback")
    # feedback = st.text_area("Provide feedback on the system:")
    # if st.button("Submit Feedback"):
    #     if feedback:
    #         data = {"text": feedback, "rating": 5}  # Default rating
    #         result = call_backend("feedback-log", data=data)
    #         if result:
    #             st.success("Thank you for your feedback!")
    #     else:
    #         st.warning("Please enter feedback before submitting")

if __name__ == "__main__":
    main()

 