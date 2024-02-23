from langchain.docstore.document import Document
from langchain.chains.question_answering import load_qa_chain
from langchain.memory import ConversationBufferMemory
from langchain import hub
from langchain_core.prompts.chat import ChatPromptTemplate
from bookjibe.llm import llm
from langchain_core.messages import AIMessage, HumanMessage
from pathlib import Path
import copy
from pprint import pprint
from typing import Union
import json
from bookjibe.settings import init_prompt_folder, user_language, temporary_folder
from bookjibe.utils import (
    get_prompt,
    create_chain_from_memory_and_prompt,
    get_human_prompt_from_file,
)

init_chapter_prompt = {
    "en": "Write chapter XXX of the story.",
    "fr": "Ecris le chapitre XXX de l'histoire."
}


class Writer:
    _chain = None

    def __init__(self, initial_memory=None):
        # self.llm = llm
        self.initial_memory = initial_memory
        self.prompt = self._generate_prompt()

    @property
    def chain(self):
        if self._chain:
            return self._chain
        else:
            return create_chain_from_memory_and_prompt(
                llm=llm, prompt=self.prompt, memory=self.initial_memory
            )

    def _generate_prompt(self):
        return get_prompt()

    def generate_book_story(
        self, init_prompt_file: Union[str, Path], story_prompt: str
    ):
        """Generate a book idea using a chain."""
        print("Generating book story...")
        print(f"Init prompt file: {init_prompt_file}")
        init_prompt = get_human_prompt_from_file(Path(init_prompt_folder) / init_prompt_file)
        print("Init prompt:", init_prompt)
        print("Story prompt:", story_prompt)
        return self.chain.invoke(
            {
                "input": f"{init_prompt} {story_prompt}",
                "agent_scratchpad": [],
                "input_documents": [],
            }
        )
    

    def generate_chapter(self, chapter_prompt, chapter, temporary_file_path=None):
        """Generate the next chapter of the book.

        Args:
            chain (Chain): The chain to be used to generate the next chapter.
            chapter_prompt (str): The prompt to be used for the chapter.
            chapter (int): The number of the current chapter.

        Returns:
            chain: The chain that can be used to generate the next chapter.
            next_chapter (int): The next chapter of the book.
        """
        print("Generating chapter...")
        chain = self.chain
        temporary_file_path = Path(temporary_folder) / f"chapter{chapter}.txt"
        init_chapter_prompt_txt = init_chapter_prompt[user_language].replace("XXX", str(chapter))
        versions = {}
        versions[1] = chain(
            {
                "input": f"{init_chapter_prompt_txt} {chapter_prompt}",
                "agent_scratchpad": [],
                "input_documents": [
                    Document(page_content=chapter_prompt, metadata={"source": "local"})
                ],
            }
        )
        ai_message1 = chain.memory.chat_memory.messages.pop(-1)
        human_message1 = chain.memory.chat_memory.messages.pop(-1)

        versions[2] = chain(
            {
                "input": f"{init_chapter_prompt_txt} {chapter_prompt}",
                "agent_scratchpad": [],
                "input_documents": [
                    Document(page_content=chapter_prompt, metadata={"source": "local"})
                ],
            }
        )
        ai_message2 = chain.memory.chat_memory.messages.pop(-1)
        human_message2 = chain.memory.chat_memory.messages.pop(-1)

        # Demandez à l'utilisateur de choisir la meilleure version
        print("Version 1:", versions[1]["output_text"])
        print("Version 2:", versions[2]["output_text"])

        with open(temporary_file_path, "a") as f:
            f.write(f"Chapitre {chapter}\n")
            f.write("Version 1:\n")
            f.write(versions[1]["output_text"])
            f.write("\n")
            f.write("Version 2:\n")
            f.write(versions[2]["output_text"])
            f.write("\n\n\n")
        user_choice = int(
            input("Choisissez la version (1 ou 2, ou 0 si aucune version convient): ")
        )

        # Use the prefered version to generate the next chapter
        if user_choice == 1:
            chain.memory.chat_memory.messages.append(human_message1)
            chain.memory.chat_memory.messages.append(ai_message1)
            next_chapter = chapter + 1
        elif user_choice == 2:
            chain.memory.chat_memory.messages.append(human_message2)
            chain.memory.chat_memory.messages.append(ai_message2)
            next_chapter = chapter + 1
        else:
            print("Aucune version choisie. Fin de la génération.")
            next_chapter = chapter
        return chain, next_chapter

    def save_history_to_file(
        file_path: Union[str, Path], chain_memory: ConversationBufferMemory
    ):
        """Save the conversation history to a file.

        It should keep the messages in the same order as they were generated.
        It should include the chapter, the human message, and the AI message.

        Args:
            file_path (str): The path to the file where the history will be saved.
            chain_memory (ConversationBufferMemory): The memory of the chain that contains the conversation history.

        Example:
        {
            "chapter1": {
                "human_message": "The human message",
                "ai_message": "The AI message"
            },
            "chapter2": {
                "human_message": "The human message",
                "ai_message": "The AI message"
            }
        }
        """
        history = {}
        messages = chain_memory.chat_memory.messages
        for i, message in enumerate(messages):
            chapter_counter = 1
            if isinstance(message, AIMessage) and i > 2:
                history[f"chapter{chapter_counter}"] = {
                    "human_message": messages[i - 1].content,
                    "ai_message": message.content,
                }
                chapter_counter += 1
        with open(file_path, "w") as f:
            json.dump(history, f)
        # with open(file_path, "w") as f:
        #     f.write(history)

    def update_chain_memory_with_messages_from_file(
        file_path: Union[str, Path],
        chain_memory: ConversationBufferMemory,
        keep_chapters: int = None,
    ):
        """Load the conversation history from a file and add to the chain memory.

        Args:
            file_path (str): The path to the file where the history is saved.
            chain_memory (ConversationBufferMemory): The memory of the chain that contains the conversation history.
            keep_chapters (int): The number of chapters to keep in the memory. If None, keep all chapters.

        Returns:
            list: The list of messages in the same order as they were generated.

        Example:
        {
            "chapter1": {
                "human_message": "The human message",
                "ai_message": "The AI message"
            },
            "chapter2": {
                "human_message": "The human message",
                "ai_message": "The AI message"
            }
        }
        """
        with open(file_path, "r") as f:
            history = json.load(f)
        for chapter, messages in history.items():
            chapter_number = int(chapter.replace("chapter", ""))
            if keep_chapters is not None and chapter_number > keep_chapters:
                break
            chain_memory.chat_memory.messages.append(
                HumanMessage(messages["human_message"])
            )
            chain_memory.chat_memory.messages.append(AIMessage(messages["ai_message"]))
        return chain_memory




    def generate_book(chain, number_of_chapters, starting_chapter=1):
        """Generate a book using a chain.

        Args:
            chain (Chain): The chain to be used to generate the book.
            number_of_chapters (int): The number of chapters in the book.

        Returns:
            list: The list of chapters in the book.
        """
        chapter = starting_chapter
        while chapter <= number_of_chapters:
            prompt = input(
                f"Want to add something specific for this chapter {chapter}: "
            )
            chain, chapter = generate_next_chapter(chain, prompt, chapter)
        return chain

    def save_book_to_file(file_path: Union[str, Path], chain):
        """Save the book to a file.

        Args:
            file_path (str): The path to the file where the book will be saved.
            chain (Chain): The chain that was used to generate the book.

        """
        book = chain.memory.chat_memory.messages
        chapters = [i.content for i in book if isinstance(i, AIMessage)]

        with open(file_path, "w") as f:
            f.write("\n".join(chapters))

        return file_path

    def init_chain(
        human_prompt_file: Union[str, Path], memory: ConversationBufferMemory = None
    ):
        """Initialize the chain with a prompt and a memory.

        Args:
            human_prompt_file (str): The path to the file where the prompt is saved.
            memory (ConversationBufferMemory): The memory to be used for the chain.

        Returns:
            Chain: The chain that can be used to generate the next chapter.
        """
        human_prompt_txt = get_human_prompt_from_file(human_prompt_file)
        prompt = get_prompt()
        chain = create_chain_from_memory_and_prompt(llm, prompt)
        prompt_story = input("Want to add something specific for the story: ")
        chain.invoke(
            {
                "input": f"{human_prompt_txt} {prompt_story}",
                "agent_scratchpad": [],
                "input_documents": [],
            }
        )
        return chain
