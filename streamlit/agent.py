import requests
import streamlit as st
import os
URL = os.environ.get("VLLM_URL","http://localhost:8000/v1/chat/completions")
MODEL = "ornith-ai/Ornith-1.5-9B"

if "messages" not in st.session_state:
    st.session_state.messages = []   # <-- this list IS the conversation.

def chat(user_input):
    st.session_state.messages.append({"role":"user","content":user_input})

    r = requests.post(URL,json={"model":MODEL,"messages":st.session_state.messages})
    data = r.json()
    print(data)
    print(f"[{data['usage']['prompt_tokens']} tokens]")

    reply= data["choices"][0]["message"]["content"]

    st.session_state.messages.append({"role":"assistant", "content":reply})

    return reply

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
         st.markdown(message["content"])

if prompt := st.chat_input("Ask anything..."):
    chat(prompt)
    st.rerun()
