import pandas as pd
import streamlit as st
import requests
import json
import io
from agents.remediation_agent import analyze_compliance_issues
from agents.new import generate_remediation_suggestions

# Set page config with HSBC styling
st.set_page_config(
    page_title="RemedAI",
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
    .remediation-table {
        width: 100%;
        border-collapse: collapse;
        margin: 15px 0;
    }
    .remediation-table th {
        background-color: #FFD700;
        color: #000000;
        padding: 10px;
        text-align: left;
    }
    .remediation-table td {
        padding: 10px;
        border-bottom: 1px solid #555;
    }
    .remediation-table tr:nth-child(even) {
        background-color: #333;
    }
    .two-column-remediation {
        display: flex;
        gap: 20px;
        margin-top: 20px;
    }
    .remediation-column {
        flex: 1;
        background-color: #222;
        border-radius: 8px;
        padding: 15px;
    }
    .remediation-column-header {
        color: #FFD700;
        font-weight: bold;
        margin-bottom: 15px;
        font-size: 1.1em;
    }
    .remediation-item {
        padding: 10px;
        border-bottom: 1px solid #444;
        margin-bottom: 10px;
    }
    .mismatched-policy {
        color: #FF6B6B;
    }
    .remediation-suggestion {
        color: #A5D6A7;
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

def sequential_mode():
    uploaded_file = st.file_uploader("Upload a PDF document", type=["pdf"], key="sequential_upload")

    agent_steps = {
        "Ingestion Agent": False,
        "Preprocessing Agent": False,
        "Summarization Agent": False,
        "Compliance Rules Generator": False,
        "Compliance Agent": False,
        "Remediation Agent": False,
    }

    total_steps = len(agent_steps)
    status_placeholder = st.empty()

    def update_progress():
        completed_steps = sum(agent_steps.values())
        steps = list(agent_steps.keys())

        bar_html = """
        <style>
        .progress-container {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-top: 20px;
            margin-bottom: 20px;
            position: relative;
        }}
        .progress-line {{
            position: absolute;
            top: 50%;
            left: 0;
            height: 4px;
            width: 100%;
            background-color: #333;
            z-index: 0;
        }}
        .progress-line-fill {{
            height: 4px;
            background-color: #00c853;
            position: absolute;
            top: 50%;
            left: 0;
            z-index: 1;
            width: {progress_percent}%;
        }}
        .checkpoint {{
            z-index: 2;
            background-color: #111;
            border: 3px solid #555;
            color: white;
            width: 32px;
            height: 32px;
            border-radius: 50%;
            text-align: center;
            line-height: 28px;
            font-weight: bold;
            font-size: 16px;
            position: absolute;
            transform: translateX(-50%);
        }}
        .checkpoint.checked {{
            background-color: #00c853;
            border: 3px solid #00c853;
        }}
        .step-labels {{
            display: flex;
            justify-content: space-between;
            margin-top: 5px;
            font-size: 12px;
            color: #bbb;
        }}
        </style>
        <div class="progress-container">
            <div class="progress-line"></div>
            <div class="progress-line-fill"></div>
            {checkpoints}
        </div>
        <div class="step-labels">{labels}</div>
        """

        checkpoints_html = ""
        labels_html = ""
        for i, (step, done) in enumerate(agent_steps.items()):
            is_checked = "checked" if done else ""
            checkpoints_html += f"<div class='checkpoint {is_checked}' style='left: {i / (total_steps - 1) * 100}%;'>{'✓' if done else i + 1}</div>"
            labels_html += f"<div style='width:{100 / total_steps}%; text-align:center;'>{step}</div>"

        progress_percent = int((completed_steps / total_steps) * 100)

        full_html = bar_html.format(
            progress_percent=progress_percent,
            checkpoints=checkpoints_html,
            labels=labels_html
        )

        status_placeholder.markdown(full_html, unsafe_allow_html=True)

    if st.button("Start Process"):
        if not uploaded_file:
            st.warning("Please upload a PDF file first")
            return

        file_bytes = uploaded_file.read()
        update_progress()

        with st.spinner("Running Ingestion Agent..."):
            files = {"file": (uploaded_file.name, io.BytesIO(file_bytes), uploaded_file.type)}
            ingestion_result = call_backend("ingestion", files=files)
        if ingestion_result is None:
            return
        agent_steps["Ingestion Agent"] = True
        update_progress()

        with st.expander("🧠 Ingestion Agent - Text extracted successfully", expanded=True):
            display_agent_progress(
                "Ingestion Agent",
                "Extracting text from PDF",
                ingestion_result.get("text", ""),
                "Text extracted successfully"
            )

        with st.spinner("Running Preprocessing Agent..."):
            files = {"file": (uploaded_file.name, io.BytesIO(file_bytes), uploaded_file.type)}
            preprocess_result = call_backend("preprocess", files=files)
        if preprocess_result is None:
            return
        agent_steps["Preprocessing Agent"] = True
        update_progress()

        with st.expander("🧹 Preprocessing Agent - Text preprocessed successfully", expanded=True):
            display_agent_progress(
                "Preprocessing Agent",
                "Cleaning and structuring text",
                preprocess_result,
                "Text preprocessed successfully"
            )

        with st.spinner("Running Summarization Agent..."):
            files = {"file": (uploaded_file.name, io.BytesIO(file_bytes), uploaded_file.type)}
            summarize_result = call_backend("summarize-content", files=files)
        if summarize_result is None:
            return
        agent_steps["Summarization Agent"] = True
        update_progress()

        with st.expander("📝 Summarization Agent - Content summarized successfully", expanded=True):
            display_agent_progress(
                "Summarization Agent",
                "Creating document summary",
                summarize_result.get("summary", ""),
                "Content summarized successfully"
            )

        with st.spinner("Running Compliance Rules Generator Agent..."):
            files = {"brd_file": (uploaded_file.name, io.BytesIO(file_bytes), uploaded_file.type)}
            compliance_rules_result = call_backend("generate-compliance-rules", files=files)
        if compliance_rules_result is None:
            return
        agent_steps["Compliance Rules Generator"] = True
        update_progress()

        rules_text = compliance_rules_result.get("rules_text", "")
        download_rules_url = f"{BACKEND_URL}/download/compliance-rules"
        download_remediation_url = f"{BACKEND_URL}/download/remediation"

        with st.expander("📋 Compliance Rules Generator - Rules generated successfully", expanded=True):
            display_agent_progress(
                "Compliance Rules Generator",
                "Generating compliance rules from BRD...",
                rules_text,
                "Compliance rules generated successfully!"
            )
            st.markdown(f"[⬇️ Download Compliance Rules Excel]({download_rules_url})", unsafe_allow_html=True)

        with st.spinner("Running Compliance Agent..."):
            files = {
                "requirements_file": (
                    uploaded_file.name,
                    io.BytesIO(file_bytes),
                    uploaded_file.type
                )
            }

            response = call_backend("check-compliance", files=files)

            if not response or "result" not in response:
                st.error(f"❌ Backend error: {response.get('error', 'Unexpected response format.')}")
                return

            compliance_result = response["result"]

            if not isinstance(compliance_result, list):
                st.error("⚠ Backend returned unexpected format. Expected a list of results.")
                return

            matched_rules = [item for item in compliance_result if item.get("status") == "Matched"]
            mismatched_rules = [item for item in compliance_result if item.get("status") == "Mismatched"]

            compliance_data = {
                f"R{i+1}": {
                    "AI GENRATED POLICIES": item.get("AI GENRATED POLICIES", ""),
                    "COMPANY POLICIES": item.get("COMPANY POLICIES", "")
                }
                for i, item in enumerate(matched_rules)
            }

            compliance_data = json.dumps(compliance_data)

            agent_steps["Compliance Agent"] = True
            update_progress()

            with st.expander("📋 Compliance Agent - Compliance checked successfully", expanded=True):
                st.markdown("#### ✅ Validating requirements against standards")

                df = pd.DataFrame(compliance_result)

                if "status" in df.columns:
                    matched_df = df[df["status"] == "Matched"]
                    mismatched_df = df[df["status"] == "Mismatched"]

                    st.markdown("### ✅ Matched Policy Rules")
                    if not matched_df.empty:
                        st.table(matched_df[["AI GENRATED POLICIES", "COMPANY POLICIES"]])
                    else:
                        st.info("No matched rules found.")

                    st.markdown("### ❌ Mismatched Policy Rules")
                    if not mismatched_df.empty:
                        st.table(mismatched_df[["AI GENRATED POLICIES"]])
                    else:
                        st.success("No mismatched rules found.")
                else:
                    st.error("⚠ 'status' field not found in the response. Check backend output.")

        with st.spinner("Running Remediation Agent..."):
            files = {"requirements_file": (uploaded_file.name, io.BytesIO(file_bytes), uploaded_file.type)}
            remediation_result = call_backend("generate-remediation", files=files)

            remediation_output = None
            if mismatched_rules:
                remediation_output = generate_remediation_suggestions(mismatched_rules)

                if remediation_output.get("status") == "success":
                    remedies_data = remediation_output["remedies"]

                    if len(remedies_data) != len(mismatched_rules):
                        st.warning(f"Got {len(remedies_data)} remedies for {len(mismatched_rules)} policies. Some may be missing.")

                    policy_remedy_map = {
                        item["mismatched_policy"]: item["remedy"]
                        for item in remedies_data
                    }

        if remediation_result is None:
            return
        agent_steps["Remediation Agent"] = True
        update_progress()

        with st.expander("🛠️ Remediation Agent - Suggestions generated for mismatched rules", expanded=True):
            st.markdown("#### 🧾 Remediation Guidance for Mismatched Policies")

            if mismatched_rules:
                if remediation_output and remediation_output.get("status") == "success":
                    # Table headers
                    col1, col2 = st.columns([1, 2])
                    col1.markdown("**❌ Mismatched Policies**")
                    col2.markdown("**🛠️ Remediation Suggestions**")

                    # Table rows
                    for policy in mismatched_rules:
                        policy_text = policy.get("AI GENRATED POLICIES", "Unknown policy")
                        remedy = policy_remedy_map.get(policy_text, "No specific recommendation provided")

                        col1, col2 = st.columns([1, 2])
                        col1.markdown(f"➤ {policy_text}")
                        col2.markdown(f"✏️ {remedy}")
                else:
                    st.error("Failed to generate structured remediation suggestions")
            else:
                st.success("🎉 No mismatched rules found - all policies are compliant!")

            st.markdown(f"[⬇️ Download Detailed Remediation Report]({download_remediation_url})", unsafe_allow_html=True)



def main():
    st.markdown("<h1 class='header'>COMPLIANCE AND REMEDIATION GENERATOR</h1>", unsafe_allow_html=True)
    st.markdown("---")

    mode = st.radio(
        "Select Mode:",
        ("Sequential Mode"),
        horizontal=True,
        label_visibility="hidden"
    )

    st.markdown("---")

    if mode == "Sequential Mode":
        sequential_mode()

    st.markdown("---")

if __name__ == "__main__":
    main()  
