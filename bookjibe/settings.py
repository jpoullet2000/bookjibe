from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

openai_model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
