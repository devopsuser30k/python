# chatbot_basic.py (Flask UI with AI integration)
import random
from datetime import datetime, timezone
from flask import Flask, render_template_string, request
import openai
import os

app = Flask(__name__)

# Set your OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

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

def get_ai_response(user_input: str) -> str:
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful chatbot."},
                {"role": "user", "content": user_input}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"[Error from AI model: {e}]"

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
            response = get_ai_response(user_input)
            chat_history.append(f"{utc_timestamp()} ChatBot: {response}")
    return render_template_string(HTML_TEMPLATE, chat_log=chat_history)

if __name__ == "__main__":
    app.run(debug=True)
