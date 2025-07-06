import streamlit as st
import google.generativeai as genai
from datetime import datetime

# 🔐 Set your Gemini API key directly here (unsafe for production)
API_KEY = "AIzaSyAWs83sgJyEwpKJ8NFjQ0qMLo2uSCXZB20"  # <<< REPLACE with your real key
MODEL_NAME = "gemini-1.5-flash"
TEMPERATURE = 0.3

# Configure Gemini
if not API_KEY:
    st.error("❌ GEMINI_API_KEY is missing.")
    st.stop()
genai.configure(api_key=API_KEY)

# Streamlit setup
st.set_page_config(page_title="Indian Law Chatbot", layout="centered")
st.title("👩‍⚖️ Indian Criminal Law Advisor Chatbot")
st.markdown("Ask any question related to Indian criminal law (IPC, CrPC). This bot will act like a legal advisor and suggest relevant sections, punishments, and next steps.")

# Initialize session chat state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ✅ Refined Legal Prompt
LEGAL_SYSTEM_PROMPT = """
You are a professional Indian criminal lawyer and legal advisor. Your expertise includes the Indian Penal Code (IPC), Code of Criminal Procedure (CrPC), and Indian Evidence Act.

Your responsibilities:
1. Understand the user's legal issue clearly, just like a practicing lawyer would during consultation.
2. Identify all relevant IPC, CrPC, or other applicable Indian criminal laws.
3. Provide the exact IPC/CrPC Section numbers, titles, and legal definitions.
4. Mention punishments as per the law (e.g., "Section 354 IPC – punishment: 3 years imprisonment and/or fine").
5. Offer step-by-step legal advice on what the user should do next (e.g., FIR filing, contacting a magistrate, hiring a lawyer).

Your output should always follow this structured format:

**📜 Applicable Section(s):**  
Section ### – [Title or summary]

**🧠 Legal Reasoning:**  
Why this section applies, using facts from the user's query.

**🔒 Punishment:**  
What does the law state as punishment for this offense?

**🧾 Legal Advice:**  
Explain what steps the user should take next (FIR, lawyer, report, etc.)

Only answer based on Indian criminal law.
"""

# Initialize Gemini session chat
if "chat" not in st.session_state:
    model = genai.GenerativeModel(MODEL_NAME)
    st.session_state.chat = model.start_chat(history=[
        {"role": "user", "parts": [LEGAL_SYSTEM_PROMPT]},
        {"role": "model", "parts": ["Understood. Please provide your legal question."]}
    ])

# User input field
user_input = st.text_input("📝 Your Legal Query:", placeholder="e.g., My neighbor threatened to kill me. What IPC section applies?")

# Handle response
if user_input:
    with st.spinner("Consulting Indian law..."):
        try:
            response = st.session_state.chat.send_message(user_input, generation_config={
                "temperature": TEMPERATURE,
                "top_p": 1,
                "top_k": 1,
                "max_output_tokens": 1024
            })
            st.session_state.chat_history.append(("🧑‍⚖️ You", user_input))
            st.session_state.chat_history.append(("🤖 LawBot", response.text))
        except Exception as e:
            st.error(f"❌ Error: {e}")

# Display chat history
if st.session_state.chat_history:
    st.markdown("### 💬 Conversation History")
    for sender, message in st.session_state.chat_history:
        st.markdown(f"**{sender}:** {message}")

    # Prepare chat log for download
    chat_log = ""
    for sender, message in st.session_state.chat_history:
        chat_log += f"{sender}:\n{message}\n\n"

    filename = f"legal_chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    st.download_button(
        label="💾 Download Chat History",
        data=chat_log,
        file_name=filename,
        mime="text/plain"
    )

# Clear session button
if st.button("🔁 Clear Chat"):
    st.session_state.chat_history = []
    st.session_state.chat = genai.GenerativeModel(MODEL_NAME).start_chat(history=[
        {"role": "user", "parts": [LEGAL_SYSTEM_PROMPT]},
        {"role": "model", "parts": ["Understood. Please provide your legal question."]}
    ])
    st.rerun()
