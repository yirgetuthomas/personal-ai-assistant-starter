"""Your personal AI assistant.

Run it from the terminal:
    streamlit run app.py
"""

import os

import openai
import streamlit as st
from dotenv import load_dotenv

# ---------- Part 1: the personality ----------
# Change these to make the assistant your own.
TITLE = "Thomas's AI Mentor"
SYSTEM_PROMPT = """
You are AI Mentor, a friendly and experienced Senior AI Engineer who specializes in teaching Generative AI engineering.

Your mission is to help software developers understand AI concepts, LLMs, prompt engineering, RAG, AI agents, and model deployment.

Follow these rules:
- Explain complex concepts in simple, beginner-friendly language.
- Use real-world examples, especially from software development, Microsoft Azure, and Power Platform.
- Provide step-by-step guidance when teaching technical topics.
- Keep answers clear, concise, and conversational.
- Ask short quiz questions to test understanding when appropriate.
- Encourage hands-on learning and practical projects.
- If you don't know something, acknowledge it rather than guessing.

Your goal is to help learners become confident, job-ready AI Engineers.
"""

# ---------- Settings ----------
MODEL = "google/gemma-4-26b-a4b-it:floor"
MAX_REPLY_TOKENS = 300  # the longest reply allowed, in tokens
MAX_MESSAGES = 20  # the most messages one visitor can send in a chat

# On your Codespace, the key comes from .env. Once deployed, it comes
# from the app's secrets. Either way, it never appears in this file.
load_dotenv()
client = openai.OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ["OPENROUTER_API_KEY"],
)

st.title(TITLE)

# ---------- Part 2: this chat's history ----------
# The model remembers nothing between calls, so the app keeps the whole
# conversation here and sends all of it every time.
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    st.chat_message(message["role"]).write(message["content"])

messages_sent = len([m for m in st.session_state.messages if m["role"] == "user"])
if messages_sent >= MAX_MESSAGES:
    st.info("You've reached the message limit for this chat. Thanks for trying it out!")
    st.stop()

# ---------- Part 3: the call ----------
user_text = st.chat_input("Say something")
if user_text:
    st.session_state.messages.append({"role": "user", "content": user_text})
    st.chat_message("user").write(user_text)

    try:
        response = client.chat.completions.create(
            model=MODEL,
            # The personality goes first, then the conversation so far
            messages=[{"role": "system", "content": SYSTEM_PROMPT}] + st.session_state.messages,
            max_tokens=MAX_REPLY_TOKENS,
        )
    except openai.APIError as error:
        st.session_state.messages.pop()  # forget the message that didn't get a reply
        st.error(f"Couldn't get a reply from the model: {error}")
        st.stop()

    reply = response.choices[0].message.content or "(The model sent back an empty reply.)"
    st.session_state.messages.append({"role": "assistant", "content": reply})
    st.chat_message("assistant").write(reply)