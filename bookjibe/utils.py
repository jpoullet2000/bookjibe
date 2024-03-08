from typing import Union
from pathlib import Path
import base64
import pandas as pd
import json
import io
from langchain import hub
from langchain_core.prompts.chat import ChatPromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain.chains.question_answering import load_qa_chain


def get_prompt():
    prompt = hub.pull("hwchase17/openai-functions-agent")
    prompt.input_variables = ["agent_scratchpad", "input", "context"]
    return prompt


def create_chain_from_memory_and_prompt(
    llm, prompt: ChatPromptTemplate, memory: ConversationBufferMemory = None
):
    """Create a chain from a memory and a prompt.

    Args:
        llm (ChatOpenAI): The language model to be used for the chain.
        memory (ConversationBufferMemory): The memory to be used for the chain.
        prompt (str): The prompt to be used for the chain.

    Returns:
        Chain: The chain that can be used to generate the next chapter.
    """
    if memory is None:
        memory = ConversationBufferMemory(memory_key="chat_history", input_key="input")
    chain = load_qa_chain(llm, chain_type="stuff", memory=memory, prompt=prompt)
    return chain


def get_human_prompt_from_file(file_path: Union[str, Path]):
    """Load the prompt from a file.

    Args:
        file_path (str): The path to the file where the prompt is saved.

    Returns:
        str: The prompt to be used for the next chapter.
    """
    with open(file_path, "r") as f:
        human_prompt = f.read()
    return human_prompt

def check_if_name_in_message(messages):
    """Check if the name attribute is in the messages and is either "synopsis" or "chapterX" where X is any integer starting from 1."""
    for message in messages:
        if hasattr(message, "name") and (
            message.name == "synopsis"
            or message.name.startswith("chapter")
        ):
            return True
    return False

def get_last_chapter_number_from_messages(messages):
    """Get the last chapter number from the messages. If there are no chapters, return 0.
    
    Check first if the name attribute is in the messages and is either "synopsis" or "chapterX" where X is any integer starting from 1. 
    If it is, return the highest chapter number found. If not, assume that AIMessages are for "synopsis", "chapter1", "chapter2", etc, in the right order. 
    The "synopsis" message is not counted as a chapter.
    If no AIMessage is found return 0.

    """
    if check_if_name_in_message(messages):
        max_chapter = 0
        for message in messages:
            if hasattr(message, "name") and message.name.startswith("chapter"):
                current_chapter = int(message.name.replace("chapter", ""))
                if current_chapter > max_chapter:
                    max_chapter = current_chapter
        return max_chapter
    else:
        return len([message for message in messages if message["type"] == "AIMessage"]) - 1

def parse_file_contents(contents, filename):
    """Parse the contents of a JSON file."""
    content_type, content_string = contents.split(",")
    decoded = base64.b64decode(content_string)
    try:
        if "json" in filename:
            # Assume that the user uploaded a JSON file
            return json.loads(decoded)
        elif "csv" in filename:
            # Assume that the user uploaded a CSV file
            return pd.read_csv(io.StringIO(decoded.decode("utf-8")))
    except Exception as e:
        print(e)
        return None
