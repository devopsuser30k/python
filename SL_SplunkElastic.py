# chatbot_streamlit_splunk.py
import os
import re
import streamlit as st
from datetime import datetime, timezone
import requests
from elasticsearch import Elasticsearch

# Splunk credentials from environment variables
SPLUNK_BASE_URL = os.getenv("SPLUNK_BASE_URL")
SPLUNK_AUTH_TOKEN = os.getenv("SPLUNK_AUTH_TOKEN")

# Elasticsearch credentials
ES_HOST = os.getenv("ES_HOST")
ES_USERNAME = os.getenv("ES_USERNAME")
ES_PASSWORD = os.getenv("ES_PASSWORD")

BUSINESS_QUERY_MAP = {
    "errors last hour": ("splunk", "index=main sourcetype=error_logs earliest=-1h"),
    "login failures today": ("splunk", "index=main event=login status=failure earliest=@d"),
    "top pages visited": ("splunk", "index=web_logs | top page limit=10"),
    "average response time": ("splunk", "index=web_logs | stats avg(response_time)"),
    "failed payments": ("splunk", "index=transactions status=failure action=payment"),
    "recent user activity": ("elastic", {"index": "user_logs", "query": {"match_all": {}}}),
    "high cpu usage servers": ("elastic", {"index": "server_metrics", "query": {"range": {"cpu": {"gte": 90}}}})
}

def utc_timestamp() -> str:
    return datetime.now(timezone.utc).strftime("[%Y-%m-%d %H:%M:%S UTC]")

def query_splunk(query: str) -> str:
    try:
        headers = {
            "Authorization": f"Bearer {SPLUNK_AUTH_TOKEN}",
            "Content-Type": "application/json"
        }
        data = {
            "search": f"search {query}",
            "exec_mode": "blocking"
        }
        response = requests.post(f"{SPLUNK_BASE_URL}/services/search/jobs/export", headers=headers, json=data, verify=False)
        if response.status_code == 200:
            return response.text[:1500]
        else:
            return f"[Splunk Error {response.status_code}: {response.text}]"
    except Exception as e:
        return f"[Error connecting to Splunk: {e}]"

def query_elasticsearch(query: dict) -> str:
    try:
        es = Elasticsearch([ES_HOST], basic_auth=(ES_USERNAME, ES_PASSWORD), verify_certs=False)
        result = es.search(index=query["index"], query=query["query"], size=5)
        hits = result.get("hits", {}).get("hits", [])
        if not hits:
            return "No results found."
        return "\n\n".join([str(hit["_source"]) for hit in hits])
    except Exception as e:
        return f"[Error connecting to Elasticsearch: {e}]"

def extract_relative_time(user_input: str) -> str:
    match = re.search(r'last (\d+) (minute|hour|day|week|month)s?', user_input.lower())
    if match:
        num = match.group(1)
        unit = match.group(2)[0]  # first letter: m, h, d, w, M
        return f"earliest=-{num}{unit}"
    return ""

# Streamlit UI
st.title("📊 Data Assistant for Business Users")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

user_input = st.text_input("Ask a question about system data (e.g. 'errors last hour'):", key="input")
if user_input:
    st.session_state.chat_history.append(f"{utc_timestamp()} You: {user_input}")

    mapped = BUSINESS_QUERY_MAP.get(user_input.strip().lower())
    if mapped:
        source, query = mapped
        if source == "splunk":
            response = query_splunk(query)
        elif source == "elastic":
            response = query_elasticsearch(query)
    else:
        relative_time = extract_relative_time(user_input)
        if "system log" in user_input.lower() and relative_time:
            query = f"index=main sourcetype=system_logs {relative_time}"
            response = query_splunk(query)
        else:
            response = "Sorry, I don't recognize that request. Try: 'errors last hour', 'login failures today', or 'recent user activity'."

    st.session_state.chat_history.append(f"{utc_timestamp()} DataBot: {response}")

for line in st.session_state.chat_history:
    st.write(line)
