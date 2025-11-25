import streamlit as st
import os
import requests  
import zipfile
import io

st.set_page_config(page_title="Autonomous QA Agent", layout="wide")
st.title("🤖 Autonomous QA Agent")

API_URL = "http://localhost:8000"  

if "html_context" not in st.session_state:
    st.session_state["html_context"] = ""
if "kb_ready" not in st.session_state:
    st.session_state["kb_ready"] = False
if "generated_cases" not in st.session_state:
    st.session_state["generated_cases"] = False

def create_demo_zip():
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zf:
        files = ["checkout.html", "product_specs.md", "ui_ux_guide.txt", "api_endpoints.json"]
        for file_name in files:
            file_path = os.path.join("project_assets", file_name)
            if os.path.exists(file_path):
                zf.write(file_path, arcname=file_name)
    return zip_buffer.getvalue()

with st.sidebar:
    st.header("📁 1. Data Ingestion")
    
    uploaded_files = st.file_uploader(
        "Upload Docs & Checkout.html", 
        type=["pdf", "md", "txt", "json", "html"], 
        accept_multiple_files=True
    )

    if st.button("Build Knowledge Base"):
        if uploaded_files:
            with st.spinner("Sending files to Backend API..."):
                try:
                    files_payload = [
                        ('files', (file.name, file.getvalue(), file.type)) 
                        for file in uploaded_files
                    ]
                    
                    response = requests.post(f"{API_URL}/upload-docs", files=files_payload)
                    
                    if response.status_code == 200:
                        data = response.json()
                        st.success(data["message"])
                        st.session_state["kb_ready"] = True
                        
                        if data.get("html_content"):
                            st.session_state["html_context"] = data["html_content"]
                        else:
                            st.warning("checkout.html not found.")
                    else:
                        st.error(f"API Error: {response.text}")
                        
                except Exception as e:
                    st.error(f"Connection Error. Is the backend running? {e}")
        else:
            st.warning("Upload files first!")

    if os.path.exists("project_assets"):
        st.markdown("---")
        zip_data = create_demo_zip()
        st.download_button("📥 Download Demo Assets", zip_data, "demo.zip", "application/zip")


if not st.session_state["kb_ready"]:
    st.info("👈 Upload documents to start. Make sure backend is running on port 8000.")
    st.stop()

st.subheader("🕵️ 2. Test Case Generator")
user_query = st.chat_input("Ex: Generate test cases for discount code...")

if user_query:
    with st.chat_message("user"):
        st.write(user_query)
    with st.chat_message("assistant"):
        with st.spinner("Asking API..."):
            try:
                payload = {"query": user_query}
                response = requests.post(f"{API_URL}/generate-test-cases", json=payload)
                
                if response.status_code == 200:
                    answer = response.json()["response"]
                    st.markdown(answer)
                    st.session_state["generated_cases"] = True
                else:
                    st.error(f"API Error: {response.text}")
            except Exception as e:
                st.error(f"Connection Error: {e}")

if st.session_state["generated_cases"]:
    st.divider()
    st.subheader("💻 3. Selenium Script Generator")

    col1, col2 = st.columns([3, 1])
    with col1:
        selected_case = st.text_area("Paste a Test Scenario:")
    with col2:
        st.write("")
        st.write("") 
        generate_btn = st.button("Generate Script 🚀")

    if generate_btn and selected_case:
        with st.spinner("Requesting Script from API..."):
            try:
                payload = {
                    "test_case": selected_case,
                    "html_code": st.session_state["html_context"]
                }
                response = requests.post(f"{API_URL}/generate-script", json=payload)
                
                if response.status_code == 200:
                    script = response.json()["script"]
                    st.success("Script Generated!")
                    st.code(script, language="python")
                else:
                    st.error(f"API Error: {response.text}")
            except Exception as e:
                st.error(f"Connection Error: {e}")