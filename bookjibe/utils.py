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
