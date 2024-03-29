from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

openai_model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
init_prompt_folder = os.getenv("BOOKJIBE_PROMPT_FOLDER")
user_language = os.getenv("BOOKJIBE_USER_LANGUAGE")
temporary_folder = os.getenv("BOOKJIBE_TEMPORARY_FOLDER", "/tmp/bookjibe")
