import streamlit as st
import requests
import uuid
import json
from datetime import datetime

# Set page title and favicon
st.set_page_config(
    page_title="Longevity Health Agent",
    page_icon="🧬",
    layout="wide"
)

# Initialize session state variables if they don't exist
if 'session_id' not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'first_interaction' not in st.session_state:
    st.session_state.first_interaction = True

# FastAPI backend URL
API_URL = "http://localhost:8000"

# Custom styles (minimal, using Streamlit's built-in styling)
st.markdown("""
    <style>
    .main-header {
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# Main header
st.markdown("<h1 class='main-header'>Longevity Health Agent</h1>", unsafe_allow_html=True)

# Brief description
st.markdown("""
    Your personal health concierge specializing in longevity. I can help identify your health goals 
    and recommend appropriate supplements, lifestyle changes, and more to support your journey.
""")

# Disclaimer
st.info("""
    **Medical Disclaimer**: This is an AI assistant providing general health information. 
    It does not replace professional medical advice, diagnosis, or treatment. 
    Always consult with qualified healthcare providers before making any health decisions.
""")

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Initial welcome message
if st.session_state.first_interaction:
    with st.chat_message("assistant"):
        st.markdown("""
            Hello! I'm your Longevity Health Agent. I can help you with:
            
            - Understanding your health goals and concerns
            - Recommending evidence-based supplements and protocols
            - Providing lifestyle and exercise guidance tailored to longevity
            - Suggesting ways to optimize your health
            
            What health goals would you like to discuss today?
        """)
        st.session_state.messages.append({"role": "assistant", "content": 
            "Hello! I'm your Longevity Health Agent. I can help you with:\n\n"
            "- Understanding your health goals and concerns\n"
            "- Recommending evidence-based supplements and protocols\n"
            "- Providing lifestyle and exercise guidance tailored to longevity\n"
            "- Suggesting ways to optimize your health\n\n"
            "What health goals would you like to discuss today?"
        })
        st.session_state.first_interaction = False

# Chat input
if prompt := st.chat_input("Type your message here..."):
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Get response from backend
    with st.spinner("Thinking..."):
        try:
            response = requests.post(
                f"{API_URL}/chat",
                json={
                    "session_id": st.session_state.session_id,
                    "message": prompt
                }
            )
            
            if response.status_code == 200:
                response_data = response.json()
                assistant_response = response_data["response"]
                
                # Display assistant response
                with st.chat_message("assistant"):
                    st.markdown(assistant_response)
                    
                    # Display product recommendations if available
                    if "recommendations" in response_data and response_data["recommendations"]:
                        if "supplements" in response_data["recommendations"]:
                            st.markdown("### Recommended Supplements:")
                            for supplement in response_data["recommendations"]["supplements"]:
                                st.markdown(f"""
                                    **{supplement['name']}**
                                    - Dosage: {supplement['dosage']}
                                    - [Purchase on Amazon]({supplement['referral_link']})
                                """)
                
                # Add assistant response to history
                st.session_state.messages.append({"role": "assistant", "content": assistant_response})
            else:
                st.error(f"Error: {response.status_code} - {response.text}")
        except Exception as e:
            st.error(f"Failed to communicate with the backend: {str(e)}")
            
# Add footer with timestamp
st.caption(f"Session ID: {st.session_state.session_id[:8]}... | Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
