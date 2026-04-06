import os

from langchain_openai import ChatOpenAI


def get_chat_model(temperature: float = 0.2) -> ChatOpenAI:
    name = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
    return ChatOpenAI(model=name, temperature=temperature)
