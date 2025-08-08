# # streamlit_app.py

# import streamlit as st
# from logic import MedAILogic

# # --- Page Configuration ---
# st.set_page_config(
#     page_title="Dr.Sachin's MedAI",
#     page_icon="🩺",
#     layout="centered",
#     initial_sidebar_state="auto"
# )

# # --- App Title and Description ---
# st.title("🩺 Dr.Sachin's MedAI")
# st.markdown("Your Hyper-Personalized AI Health Assistant. All conversations are stored locally and privately on your machine.")

# # --- Core Logic and Session State ---
# # This ensures that the MedAILogic class and chat history are initialized only once per session.
# if "med_ai_logic" not in st.session_state:
#     # Initialize the main logic controller
#     st.session_state.med_ai_logic = MedAILogic()
    
#     # Load the conversation history from the local JSON file
#     # The 'interaction_history' is already in the format we need for the chat.
#     st.session_state.messages = st.session_state.med_ai_logic.user_profile.get("user_profile", {}).get("interaction_history", [])
    
#     # If the history is empty, it means it's a new user. Get the initial welcome message.
#     if not st.session_state.messages:
#         initial_message = st.session_state.med_ai_logic.get_initial_message()
#         st.session_state.messages.append(initial_message)

# # --- Display Chat History ---
# # Loop through the messages stored in the session state and display them
# for message in st.session_state.messages:
#     with st.chat_message(message["role"], avatar="🧑‍⚕️" if message["role"] == "assistant" else "👤"):
#         st.markdown(message["content"])

# # --- Handle User Input ---
# # st.chat_input will return the user's message when they press Enter
# if prompt := st.chat_input("What can I help you with today?"):
    
#     # 1. Add user message to session state and display it
#     st.session_state.messages.append({"role": "user", "content": prompt})
#     with st.chat_message("user", avatar="👤"):
#         st.markdown(prompt)

#     # 2. Get AI response and display it
#     with st.chat_message("assistant", avatar="🧑‍⚕️"):
#         with st.spinner("Dr. MedAI is thinking..."):
#             # Call the logic controller to process the message
#             ai_response = st.session_state.med_ai_logic.process_message(prompt)
            
#             # The logic controller already saves the history to the file,
#             # so we just need to display the response.
#             st.markdown(ai_response)

#     # 3. Add AI response to the session state messages list
#     # (The logic handler already added it to the file, but we need it for the current screen session)
#     # Note: process_message already adds it to the internal history for the *next* call,
#     # but we add it here to re-render correctly without a full page reload.
#     st.session_state.messages.append({"role": "assistant", "content": ai_response})













# streamlit_app.py

import streamlit as st
from logic import MedAILogic
import time

# --- Page Configuration ---
st.set_page_config(
    page_title="Dr.Sachin's MedAI",
    page_icon="🩺",
    layout="wide",  # Use wide layout for a sidebar
    initial_sidebar_state="expanded"
)

# --- Initialize Logic Controller ---
logic = MedAILogic()

# --- Sidebar ---
with st.sidebar:
    st.header("Chat History")
    
    # "New Chat" button
    if st.button("➕ New Chat", use_container_width=True):
        st.session_state.session_id = None
        st.session_state.messages = [logic.get_initial_message()]
        st.rerun()

    st.markdown("---")

    # Display list of past conversations
    conversations = logic.get_conversations()
    for session_id, summary in conversations:
        col1, col2 = st.columns([4, 1])
        with col1:
            # Button to load a past conversation
            if st.button(summary, key=f"load_{session_id}", use_container_width=True, help=f"Load chat from {summary}"):
                st.session_state.session_id = session_id
                st.session_state.messages = logic.load_conversation(session_id)
                st.rerun()
        with col2:
            # Button to delete a conversation
            if st.button("🗑️", key=f"delete_{session_id}", help=f"Delete this chat", use_container_width=True):
                logic.delete_conversation(session_id)
                # If we deleted the active chat, reset to a new chat state
                if st.session_state.get('session_id') == session_id:
                    st.session_state.session_id = None
                    st.session_state.messages = [logic.get_initial_message()]
                st.rerun()

# --- Main Chat Interface ---
st.title("🩺 Dr.Sachin's MedAI")
st.markdown("Your Hyper-Personalized AI Health Assistant. All conversations are stored locally.")

# --- Session State Initialization ---
# This block ensures that the session state is set up correctly for the first run.
if "messages" not in st.session_state:
    st.session_state.messages = [logic.get_initial_message()]
if "session_id" not in st.session_state:
    st.session_state.session_id = None

# --- Display Chat History ---
for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar="🧑‍⚕️" if message["role"] == "assistant" else "👤"):
        st.markdown(message["content"])

# --- Handle User Input ---
if prompt := st.chat_input("What can I help you with today?"):
    
    # Add user message to the current chat session
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    # Get AI response
    with st.chat_message("assistant", avatar="🧑‍⚕️"):
        with st.spinner("Dr. MedAI is thinking..."):
            # The logic handler needs the current conversation to provide context
            ai_response = logic.process_message(prompt, st.session_state.messages)
            st.markdown(ai_response)

    # Add AI response to the current chat session
    st.session_state.messages.append({"role": "assistant", "content": ai_response})

    # --- Save the conversation ---
    # If this is the first message of a new chat, create a session_id
    if st.session_state.session_id is None:
        st.session_state.session_id = str(time.time())

    # Save the entire updated conversation
    logic.save_conversation(st.session_state.session_id, st.session_state.messages)
    
    # Rerun to update the sidebar with the new chat if it's the first message
    st.rerun()