import streamlit as st
import requests
import json

# Backend API URL
API_BASE = "http://localhost:8000"  # Change if needed

st.set_page_config(page_title="HSBC AI Data Pipeline", layout="wide")
st.title("🔍 HSBC Unified AI Processing")

# UI control for execution mode
st.markdown("## 🔧 Execution Mode")
exec_mode = st.radio("Choose how to run the pipeline:", ["Sequential", "Manual"], horizontal=True)

# Horizontal button row
col1, col2, col3, col4, col5, col6 = st.columns(6)

if col1.button("1️⃣ Ingest Emails"):
    with st.spinner("Fetching emails..."):
        res = requests.get(f"{API_BASE}/emails")
        st.json(res.json())

if col2.button("2️⃣ Preprocess File"):
    uploaded = st.file_uploader("Upload File for Preprocessing", type=["txt"])
    if uploaded and st.button("Run Preprocessing"):
        files = {"file": uploaded.getvalue()}
        res = requests.post(f"{API_BASE}/preprocess/", files=files)
        st.json(res.json())

if col3.button("3️⃣ Summarize Content"):
    input_data = st.text_area("Paste content to summarize")
    if input_data and st.button("Run Summarization"):
        res = requests.post(f"{API_BASE}/summarize-content", json=input_data)
        st.json(res.json())

if col4.button("4️⃣ Generate Requirements"):
    with st.spinner("Generating requirements..."):
        res = requests.get(f"{API_BASE}/generate-requirements")
        st.json(res.json())

if col5.button("5️⃣ Check Compliance"):
    feedback_text = st.text_area("Enter structured feedback JSON")
    if feedback_text and st.button("Run Compliance Check"):
        feedback = json.loads(feedback_text)
        res = requests.post(f"{API_BASE}/check-compliance", json=feedback)
        st.json(res.json())

if col6.button("6️⃣ View Feedback Log"):
    with st.spinner("Retrieving feedback log..."):
        res = requests.get(f"{API_BASE}/feedback-log")
        st.json(res.json())

# Sequential execution
if exec_mode == "Sequential" and st.button("🚀 Run Full Pipeline"):
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