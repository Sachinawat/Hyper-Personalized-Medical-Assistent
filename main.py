from flask import Flask, render_template, request, jsonify
from logic import MedAILogic

app = Flask(__name__)

# Initialize our logic controller
med_ai = MedAILogic()

@app.route('/')
def index():
    """Render the main chat page."""
    return render_template('index.html')

@app.route('/get_initial', methods=['GET'])
def get_initial():
    """Provide the initial message when the page loads."""
    initial_message = med_ai.get_initial_message()
    history = med_ai.user_profile.get("user_profile", {}).get("interaction_history", [])
    
    # Return both history and the initial dynamic message
    return jsonify({
        "history": history,
        "initial_message": initial_message if not history else None # Only send if history is empty
    })


@app.route('/chat', methods=['POST'])
def chat():
    """Handle the chat message from the user."""
    user_message = request.json.get('message')
    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    ai_response = med_ai.process_message(user_message)
    return jsonify({'response': ai_response})

if __name__ == '__main__':
    app.run(debug=True)