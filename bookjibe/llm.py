from langchain_openai import ChatOpenAI
from bookjibe.settings import openai_model


def get_chatopenai(model: str = openai_model, temperature: float = 0.3):
    return ChatOpenAI(model=model, temperature=temperature)


llm = get_chatopenai()
