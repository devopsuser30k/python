# chatbot_basic.py (Flask UI with Splunk integration, no LLM, dynamic keyword-driven)
import random
from datetime import datetime, timezone
from flask import Flask, render_template_string, request
import os
import requests
import re

app = Flask(__name__)

# Splunk config
SPLUNK_URL = os.getenv("SPLUNK_URL")
SPLUNK_TOKEN = os.getenv("SPLUNK_TOKEN")

HTML_TEMPLATE = """
<!doctype html>
<title>Splunk - ChatBot</title>
<h1>Splunk Interface</h1>
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

def query_splunk(spl_query: str) -> str:
    try:
        headers = {
            "Authorization": f"Bearer {SPLUNK_TOKEN}",
            "Content-Type": "application/json"
        }
        payload = {
            "search": spl_query,
            "exec_mode": "blocking"
        }
        response = requests.post(f"{SPLUNK_URL}/services/search/jobs/export",
                                 headers=headers,
                                 params=payload,
                                 verify=False)
        if response.status_code == 200:
            return response.text.strip()
        else:
            return f"[Splunk Error {response.status_code}]: {response.text}"
    except Exception as e:
        return f"[Error querying Splunk: {e}]"

def utc_timestamp() -> str:
    return datetime.now(timezone.utc).strftime("[%Y-%m-%d %H:%M:%S UTC]")

def interpret_input_to_query(user_input: str) -> str:
    lowered = user_input.lower()
    app_match = re.search(r"app\d+", lowered)
    app_name = app_match.group(0) if app_match else "*"

    if "applications received" in lowered:
        return f"search index=main sourcetype=app_logs app={app_name} action=received"
    elif "failed apps" in lowered:
        return f"search index=main sourcetype=app_logs app={app_name} status=failure | stats count"
    elif "traffic" in lowered and "last week" in lowered:
        return f"search index=traffic_logs app={app_name} earliest=-1w@w latest=-1w@w+7d"
    elif "errors" in lowered:
        return "search index=main sourcetype=app_logs error"
    elif "login failures" in lowered:
        return "search index=main sourcetype=auth_logs action=failure"
    elif "cpu usage" in lowered:
        return "search index=metrics metric_name=cpu.usage_system"
    elif "memory usage" in lowered:
        return "search index=metrics metric_name=memory.usage"
    elif "recent logs" in lowered:
        return "search index=main | head 20"
    return ""

chat_history = []

@app.route("/", methods=["GET", "POST"])
def chat():
    if request.method == "POST":
        user_input = request.form.get("user_input", "")
        chat_history.append(f"{utc_timestamp()} You: {user_input}")
        if user_input.strip().lower() == "exit":
            chat_history.append(f"{utc_timestamp()} ChatBot: Goodbye!")
        else:
            query = interpret_input_to_query(user_input)
            if query:
                response = query_splunk(query)
                chat_history.append(f"{utc_timestamp()} ChatBot: {response}")
            else:
                chat_history.append(f"{utc_timestamp()} ChatBot: Sorry, I couldn't understand your request.")
    return render_template_string(HTML_TEMPLATE, chat_log=chat_history)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5001))
    app.run(debug=True, port=port)
