from openai import OpenAI
from dotenv import load_dotenv
import os
import locale

load_dotenv()

openai_model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
init_prompt_folder = os.getenv("BOOKJIBE_PROMPT_FOLDER")
prompt_generator_folder = os.getenv("BOOKJIBE_PROMPT_GENERATOR_FOLDER")
user_language = os.getenv("BOOKJIBE_USER_LANGUAGE")
temporary_folder = os.getenv("BOOKJIBE_TEMPORARY_FOLDER", "/tmp/bookjibe")

user_language = locale.getdefaultlocale()[0]
user_language_part = user_language.split("_")[0]
match user_language_part:
    case "fr":
        user_language = "fr"
    case "en":
        user_language = "en"
    case _:
        user_language = "en"

language = os.getenv("BOOKJIBE_LANGUAGE", user_language)