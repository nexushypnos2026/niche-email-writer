"""
niche-email-writer — Streamlit Frontend
Nexus AI Product Line
"""

import streamlit as st
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

st.set_page_config(
    page_title="Niche Email Writer — AI Powered",
    page_icon="📧",
    layout="centered",
)

st.title("📧 Niche Email Writer")
st.markdown("AI-powered email writing tailored for your niche.")

# Sidebar for settings
with st.sidebar:
    st.header("Settings")
    niche = st.text_input("Your Niche", placeholder="e.g., SaaS founders, real estate agents...")
    tone = st.selectbox("Tone", ["Professional", "Friendly", "Urgent", "Casual"])
    email_type = st.selectbox("Email Type", [
        "Cold Outreach",
        "Follow-up",
        "Newsletter",
        "Promotional",
        "Support Response",
    ])

# Main input
st.subheader("✍️ Write Your Email")
subject_line = st.text_input("Subject Line (optional)")
context = st.text_area("Context / Notes", height=120, placeholder="What should this email accomplish?")
cta = st.text_input("Call to Action (optional)", placeholder="e.g., Book a demo, Reply yes...")

if st.button("Generate Email", type="primary"):
    if not niche:
        st.warning("Please enter your niche in the sidebar.")
    elif not context:
        st.warning("Please provide some context for the email.")
    else:
        with st.spinner("Generating your email..."):
            try:
                payload = {
                    "niche": niche,
                    "tone": tone,
                    "email_type": email_type,
                    "subject_line": subject_line,
                    "context": context,
                    "cta": cta,
                }
                response = httpx.post(
                    f"{BACKEND_URL}/generate",
                    json=payload,
                    timeout=60.0,
                )
                if response.status_code == 200:
                    data = response.json()
                    st.success("✅ Email Generated!")
                    st.markdown("---")
                    st.markdown("**Subject:**")
                    st.write(data.get("subject", subject_line or "(auto-generated)"))
                    st.markdown("**Body:**")
                    st.write(data.get("body", ""))
                    st.download_button(
                        "📥 Download Email",
                        data.get("body", ""),
                        file_name="generated_email.txt",
                    )
                else:
                    st.error(f"Error: {response.status_code} — {response.text}")
            except httpx.ConnectError:
                st.error(f"Cannot connect to backend at {BACKEND_URL}. Is the server running?")
            except Exception as e:
                st.error(f"Unexpected error: {e}")

# Footer
st.markdown("---")
st.caption("Built with Streamlit + FastAPI + OpenAI GPT-4o-mini | Nexus AI")
