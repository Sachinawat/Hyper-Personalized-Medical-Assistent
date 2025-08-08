# # logic.py

# import os
# import json
# from datetime import datetime
# from openai import OpenAI
# from prompt import SYSTEM_PROMPT
# from dotenv import load_dotenv  # <-- NEW: Import load_dotenv

# # --- Configuration ---
# load_dotenv()  # <-- NEW: Load variables from .env file

# # <-- NEW: Get variables from the environment
# API_KEY = os.getenv("OPENROUTER_API_KEY")
# MODEL_NAME = os.getenv("MODEL_NAME") # Default model if not set
# PROFILE_FILE = "user_profile.json"

# # <-- NEW: Add a check to ensure the API key is set
# if not API_KEY:
#     raise ValueError("OPENROUTER_API_KEY not found in .env file. Please set it.")

# # Initialize the OpenAI client to connect to OpenRouter
# client = OpenAI(
#   base_url="https://openrouter.ai/api/v1",
#   api_key=API_KEY,
# )

# class MedAILogic:
#     def __init__(self):
#         self.user_profile = self._load_or_create_profile()
#         self.is_first_interaction = not self.user_profile.get("user_profile", {}).get("setup_completed")
        
#     def _load_or_create_profile(self):
#         """
#         Loads the user profile from JSON file.
#         If the file doesn't exist or is empty/corrupt, it creates a new one.
#         """
#         # --- START: MODIFIED CODE ---
#         if os.path.exists(PROFILE_FILE):
#             try:
#                 # First, check if the file is not empty
#                 if os.path.getsize(PROFILE_FILE) > 0:
#                     with open(PROFILE_FILE, 'r') as f:
#                         return json.load(f)
#                 else:
#                     # File is empty, so we'll create a new one
#                     return self._create_new_profile()
#             except json.JSONDecodeError:
#                 # File is corrupt, so we'll create a new one
#                 return self._create_new_profile()
#         else:
#             # File does not exist, create a new one
#             return self._create_new_profile()

#     def _create_new_profile(self):
#         """Helper function to generate a fresh profile structure."""
#         return json.loads("""
#             {
#               "user_profile": {
#                 "setup_completed": null,
#                 "interaction_history": []
#               }
#             }
#         """)

#     def _save_profile(self):
#         """Saves the current user profile to the JSON file."""
#         with open(PROFILE_FILE, 'w') as f:
#             json.dump(self.user_profile, f, indent=2)

#     def get_initial_message(self):
#         """Returns the first message based on whether the user is new or returning."""
#         profile = self.user_profile.get("user_profile", {})
#         if self.is_first_interaction:
#             # Welcome message for first-time users from the system prompt
#             return {
#                 "role": "assistant",
#                 "content": "Welcome! I'm Dr. MedAI, your personal AI medical assistant. To provide you with the most accurate, personalized medical guidance, I need to gather some important information about you. This will only take 5-10 minutes. Are you ready to begin your medical profile setup?"
#             }
#         else:
#             name = profile.get("personal_info", {}).get("preferred_name", "there")
#             return {
#                 "role": "assistant",
#                 "content": f"Welcome back, {name}! I have your medical profile. Before we begin, have there been any updates to your health or medications since we last spoke? Or, how can I help you today?"
#             }

#     def process_message(self, user_message: str):
#         """Processes the user message, gets a response from the AI, and updates history."""
        
#         # Add user message to history first
#         self._add_to_history("user", user_message)

#         # Prepare messages for the API call
#         conversation_history = self.user_profile["user_profile"]["interaction_history"]
        
#         messages = [{"role": "system", "content": SYSTEM_PROMPT}]
#         # The history already includes the latest user message
#         messages.extend(conversation_history)

#         try:
#             completion = client.chat.completions.create(
#                 model=MODEL_NAME, # Uses the model from .env
#                 messages=messages
#             )
#             ai_response = completion.choices[0].message.content

#             # Add AI response to history and save
#             self._add_to_history("assistant", ai_response)
#             self._save_profile()

#             # The AI will guide the user through setup if it's their first time.
#             # We can check for keywords to mark setup as complete.
#             if self.is_first_interaction and "profile is now complete" in ai_response.lower():
#                 self.user_profile["user_profile"]["setup_completed"] = datetime.now().isoformat()
#                 self._save_profile()
#                 self.is_first_interaction = False

#             return ai_response

#         except Exception as e:
#             print(f"An error occurred: {e}")
#             return "I'm sorry, but I'm having trouble connecting to my knowledge base right now. Please try again in a moment."

#     def _add_to_history(self, role: str, content: str):
#         """Adds a message to the interaction history."""
#         self.user_profile["user_profile"]["interaction_history"].append({
#             "role": role,
#             "content": content
#         })












# logic.py

import os
import json
from datetime import datetime
from openai import OpenAI
from prompt import SYSTEM_PROMPT
from dotenv import load_dotenv

# --- Configuration ---
load_dotenv()
API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME")
CONVERSATIONS_DIR = "conversations"  # Directory to store chat histories

if not API_KEY:
    raise ValueError("OPENROUTER_API_KEY not found in .env file. Please set it.")

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=API_KEY,
)

class MedAILogic:
    def __init__(self):
        """Initializes the logic class and ensures the conversations directory exists."""
        os.makedirs(CONVERSATIONS_DIR, exist_ok=True)

    def get_conversations(self):
        """
        Lists all saved conversations, sorted by most recently modified.
        Returns a list of tuples (session_id, summary).
        """
        try:
            files = [f for f in os.listdir(CONVERSATIONS_DIR) if f.endswith(".json")]
            # Sort by modification time (newest first)
            files.sort(key=lambda x: os.path.getmtime(os.path.join(CONVERSATIONS_DIR, x)), reverse=True)

            conversations = []
            for f in files:
                session_id = os.path.splitext(f)[0]
                # For summary, we'll just use the filename for now, but this could be more complex
                summary = f"Chat from {datetime.fromtimestamp(float(session_id)).strftime('%Y-%m-%d %H:%M')}"
                conversations.append((session_id, summary))
            return conversations
        except Exception as e:
            print(f"Error reading conversations: {e}")
            return []

    def load_conversation(self, session_id: str):
        """Loads a specific conversation's message history from a JSON file."""
        filepath = os.path.join(CONVERSATIONS_DIR, f"{session_id}.json")
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def save_conversation(self, session_id: str, messages: list):
        """Saves the message history of a conversation to a JSON file."""
        filepath = os.path.join(CONVERSATIONS_DIR, f"{session_id}.json")
        with open(filepath, 'w') as f:
            json.dump(messages, f, indent=2)

    def delete_conversation(self, session_id: str):
        """Deletes a conversation file."""
        filepath = os.path.join(CONVERSATIONS_DIR, f"{session_id}.json")
        if os.path.exists(filepath):
            os.remove(filepath)

    def get_initial_message(self):
        """Returns the standard welcome message for a new chat."""
        # This is a simplified initial message for new chats.
        # The full onboarding is still in the system prompt for the AI to handle.
        return {
            "role": "assistant",
            "content": "Welcome! I'm Dr. MedAI. To provide personalized guidance, I'll start by asking a few questions during our first real interaction. How can I help you today?"
        }

    def process_message(self, user_message: str, conversation_history: list):
        """
        Processes a user message by sending the full conversation history to the AI
        and returning the AI's response.
        """
        # The AI needs the full context, including the system prompt
        messages_for_api = [{"role": "system", "content": SYSTEM_PROMPT}] + conversation_history
        # Add the new user message to the end
        messages_for_api.append({"role": "user", "content": user_message})
        
        try:
            completion = client.chat.completions.create(
                model=MODEL_NAME,
                messages=messages_for_api
            )
            ai_response = completion.choices[0].message.content
            return ai_response
        except Exception as e:
            print(f"An error occurred: {e}")
            return "I'm sorry, but I'm having connection issues. Please try again."