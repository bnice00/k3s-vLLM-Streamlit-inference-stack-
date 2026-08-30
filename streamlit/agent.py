import requests
import streamlit as st
import os
# local dev via port forward vs in cluster DNS as fallback
URL = os.environ.get("VLLM_URL","http://localhost:8000/v1/chat/completions")
MODEL = "ornith-ai/Ornith-1.5-9B"

if "messages" not in st.session_state:
    st.session_state.messages = []   # <-- this list IS the conversation.

def chat(user_input):
    st.session_state.messages.append({"role":"user","content":user_input})

    r = requests.post(URL,json={"model":MODEL,"messages":st.session_state.messages})
    data = r.json()

    reply = data["choices"][0]["message"]["content"]

    st.session_state.messages.append({"role":"assistant", "content":reply, "tokens": data["usage"]["prompt_tokens"]})

    return reply

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
         st.markdown(message["content"])
         if message.get("tokens"):
             st.caption(f"{message['tokens']} tokens")
if prompt := st.chat_input("Ask anything..."):
    chat(prompt)
    st.rerun()
