# chatbot_basic.py (Flask UI version)
import random
from datetime import datetime, timezone
from flask import Flask, render_template_string, request

app = Flask(__name__)

HTML_TEMPLATE = """
<!doctype html>
<title>ChatBot</title>
<h1>ChatBot Interface</h1>
<form method=post>
  <input name=user_input style="width: 300px;">
  <input type=submit value=Send>
</form>
<div>
  {% for line in chat_log %}
    <p>{{ line }}</p>
  {% endfor %}
</div>
"""

def get_response(user_input: str) -> str:
    user_input = user_input.lower().strip()

    intents = {
        "greeting": ["hi", "hello", "hey"],
        "farewell": ["bye", "goodbye", "see you"],
        "thanks": ["thanks", "thank you"],
        "name": ["your name", "who are you"],
        "age": ["how old are you"],
    }

    responses = {
        "greeting": ["Hello!", "Hi there!", "Hey!"],
        "farewell": ["Goodbye!", "See you later!", "Bye!"],
        "thanks": ["You're welcome!", "No problem!", "Anytime!"],
        "name": ["I'm a simple chatbot.", "You can call me CodeBot."],
        "age": ["I'm timeless!", "I was born in code."]
    }

    for intent, keywords in intents.items():
        for keyword in keywords:
            if keyword in user_input:
                return random.choice(responses[intent])

    return "I'm not sure how to respond to that."

def utc_timestamp() -> str:
    return datetime.now(timezone.utc).strftime("[%Y-%m-%d %H:%M:%S UTC]")

chat_history = []

@app.route("/", methods=["GET", "POST"])
def chat():
    if request.method == "POST":
        user_input = request.form.get("user_input", "")
        chat_history.append(f"{utc_timestamp()} You: {user_input}")
        if user_input.strip().lower() == "exit":
            chat_history.append(f"{utc_timestamp()} ChatBot: Goodbye!")
        else:
            response = get_response(user_input)
            chat_history.append(f"{utc_timestamp()} ChatBot: {response}")
    return render_template_string(HTML_TEMPLATE, chat_log=chat_history)

if __name__ == "__main__":
    app.run(debug=True)
