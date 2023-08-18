from langchain.chat_models import ChatOpenAI
from slackbot.agent import Agents
from langchain.memory import ConversationSummaryBufferMemory


async def get_gorilla_response(
    input_question: str,
    memory: ConversationSummaryBufferMemory,
    agent: Agents,
    channel: str = None,
    level: int = None,
):
    gorilla_llm: ChatOpenAI = agent.value.model

    chat_and_code = await gorilla_llm.apredict(input_question)
    code = chat_and_code.split(">>>:")[-1].strip("\n")
    chat = chat_and_code.split(">>>:")[0].strip("\n")
    print(
        f""" ***********************************************************
          ***********************GORILLA START {agent.value.display_name}***************************"""
    )
    print(f"  SAYS {chat=}")
    print(f"  CODE {code=}")
    print("EXECUTING")
    try:
        code_result = exec(code)
        return code_result
    except Exception as e:
        return f""" I tried to answer {input_question} by generating this code :
        
        {code}
        
        but I got an error. The error was {e}. Please ask Geoffrey to review my code and give me advice on how to fix it."""
