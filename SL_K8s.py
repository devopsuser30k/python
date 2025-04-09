# chatbot_basic.py (Streamlit UI with Kubernetes/OCP resource fetcher)
import subprocess
from datetime import datetime, timezone
import streamlit as st
import re

st.set_page_config(page_title="ChatBot", layout="centered")
st.title("OCP/Kubernetes ChatBot Interface")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

def utc_timestamp() -> str:
    return datetime.now(timezone.utc).strftime("[%Y-%m-%d %H:%M:%S UTC]")

def interpret_input_to_command(user_input: str) -> str:
    lowered = user_input.lower()
    is_ocp = lowered.startswith("ocp:")
    is_kubectl = lowered.startswith("kubectl:")

    if not (is_ocp or is_kubectl):
        return ""

    tool = "oc" if is_ocp else "kubectl"
    lowered = lowered[len("ocp:"):] if is_ocp else lowered[len("kubectl:"):]
    namespace_match = re.search(r"namespace\s+(\S+)", lowered)
    namespace = namespace_match.group(1) if namespace_match else None

    if "pods" in lowered:
        return f"{tool} get pods -n {namespace}" if namespace else f"{tool} get pods -A"
    elif "nodes" in lowered:
        return f"{tool} get nodes"
    elif "services" in lowered:
        return f"{tool} get svc -n {namespace}" if namespace else f"{tool} get svc -A"
    elif "deployments" in lowered:
        return f"{tool} get deployments -n {namespace}" if namespace else f"{tool} get deployments -A"
    elif "namespaces" in lowered:
        return f"{tool} get ns"
    elif "configmaps" in lowered:
        return f"{tool} get configmaps -n {namespace}" if namespace else f"{tool} get configmaps -A"
    elif "secrets" in lowered:
        return f"{tool} get secrets -n {namespace}" if namespace else f"{tool} get secrets -A"
    return ""

def run_kubectl_command(command: str) -> str:
    try:
        result = subprocess.run(command.split(), capture_output=True, text=True, timeout=10)
        return result.stdout.strip() if result.returncode == 0 else result.stderr.strip()
    except Exception as e:
        return f"[Error running command: {e}]"

user_input = st.text_input("Enter command (use 'ocp:' or 'kubectl:' prefix):", key="input")
if user_input:
    st.session_state.chat_history.append(f"{utc_timestamp()} You: {user_input}")
    if user_input.strip().lower() == "exit":
        st.session_state.chat_history.append(f"{utc_timestamp()} ChatBot: Goodbye!")
    else:
        command = interpret_input_to_command(user_input)
        if command:
            response = run_kubectl_command(command)
            st.session_state.chat_history.append(f"{utc_timestamp()} ChatBot: {response}")
        else:
            st.session_state.chat_history.append(f"{utc_timestamp()} ChatBot: Sorry, I couldn't understand your request.")

for line in st.session_state.chat_history:
    st.markdown(line)
