import streamlit as st
import requests
import json

# ------------------------------
# Page Config
# ------------------------------
st.set_page_config(page_title="ADAS Logical Scenario Generator", layout="wide")

# ------------------------------
# Constants
# ------------------------------
EXPERT_PROMPT = """You are an expert in ADAS functions and ADAS technology...
(keep the rest of your long expert prompt unchanged here)
"""

USER_PROMPTS = [
    "Extract KPIs from the document",
    "List all PSVs and their descriptions",
    "Summarize the logical scenario",
    "Identify parameters relevant to ADAS",
    "Generate a JSON structure for the scenario"
]

# ------------------------------
# Session State Defaults
# ------------------------------
st.session_state.setdefault("response", "")
st.session_state.setdefault("text_data", "")
st.session_state.setdefault("additional_text_data", "")
st.session_state.setdefault("generated_output", "")
st.session_state.setdefault("chat_history", [])

# ------------------------------
st.sidebar.text_input("User Mail", placeholder="Enter your email", key="user_mail")

# ------------------------------

from PIL import Image

# Load and display MAGNA logo
magna_logo = Image.open("magna_logo_temp.jpg")
st.sidebar.image(magna_logo, caption="", use_column_width=True)


#-----------------------------------
# Sidebar Navigation
# ------------------------------

nav_option = st.sidebar.radio("Navigation", [
    "Welcome", "Upload Documents", "Generate Scenario", "Chat with Document", "Export JSON"
])

# ------------------------------
st.sidebar.slider("Max Roles", 0, 5, 2)

# ------------------------------
# Main Area Based on Navigation
# ------------------------------
st.title("ADAS Logical Scenario Generator")

if nav_option == "Welcome":
    st.markdown("### 👋 Welcome to the ADAS Scenario Generator")
    st.write("Use the sidebar to navigate through the app features.")

elif nav_option == "Upload Documents":
    st.subheader("📄 Upload Standard Document")
    main_files = st.file_uploader("Upload Standard Docs", type=["pdf", "txt", "docx"], accept_multiple_files=True)
    if main_files:
        st.session_state.text_data = extract_text_from_files(main_files)

    st.subheader("📄 Upload Reference Document")
    ref_files = st.file_uploader("Upload Reference Docs", type=["pdf", "txt", "docx"], accept_multiple_files=True)
    if ref_files:
        st.session_state.additional_text_data = extract_text_from_files(ref_files)

    if st.checkbox("Preview Document"):
        preview_text = st.session_state.text_data or "No Standard Document uploaded"
        if st.session_state.additional_text_data:
            preview_text += "\n\n--- Reference Docs ---\n" + st.session_state.additional_text_data
        st.text_area("Document Preview", preview_text, height=200)

elif nav_option == "Generate Scenario":
    st.subheader("🧠 Generate Logical Scenario")
    prompt = st.selectbox("Choose Prompt", USER_PROMPTS)
    custom_prompt = st.text_area("Custom Prompt", value=prompt, height=100)

    if st.button("🚀 Generate"):
        if not (st.session_state.text_data or st.session_state.additional_text_data):
            st.warning("Please upload at least one document first.")
        else:
            combined_text = st.session_state.text_data + "\n\n" + st.session_state.additional_text_data
            final_prompt = f"{EXPERT_PROMPT}\n\n{custom_prompt}\n\n{combined_text}"

            try:
                res = requests.post(
                    "http://localhost:11434/api/generate",
                    headers={"Content-Type": "application/json"},
                    json={"model": "llama3", "prompt": final_prompt, "stream": False}
                )
                if res.ok:
                    st.session_state.response = res.json().get("response", "No response.")
                    st.session_state.generated_output = json.dumps({
                        "scenario": "ADAS Logical Scenario",
                        "prompt": custom_prompt,
                        "response": st.session_state.response
                    }, indent=4)
                else:
                    st.session_state.response = f"Error: {res.status_code} - {res.text}"
            except Exception as e:
                st.session_state.response = f"Error connecting to model: {e}"

    if st.session_state.response:
        st.text_area("Model Response", st.session_state.response, height=200)

elif nav_option == "Chat with Document":
    st.subheader("💬 Chat with Document")
    chat_input = st.text_input("Ask something about the document")
    if st.button("Send"):
        st.session_state.chat_history.append(f"You: {chat_input}")
        # Simulate response (replace with actual model call if needed)
        st.session_state.chat_history.append(f"Bot: Response to '{chat_input}'")

    if st.button("Clear Chat"):
        st.session_state.chat_history = []

    for msg in st.session_state.chat_history:
        st.markdown(msg)

elif nav_option == "Export JSON":
    st.subheader("📦 Export Generated JSON")
    if st.session_state.generated_output:
        st.download_button("Download JSON", st.session_state.generated_output, "ADAS_output.json", "application/json")
    else:
        st.warning("No JSON generated yet.")

