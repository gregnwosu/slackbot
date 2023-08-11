from enum import Enum
from functools import partial
from typing import Callable, List, Optional, Union
from tenacity import retry, stop_after_attempt
from langchain.agents import initialize_agent, Tool
from langchain.agents import AgentType
from langchain.memory import ConversationSummaryBufferMemory
from slackbot.agent import Agents
from slackbot.search import search_bing
from slackbot.speak import speak
from dataclasses import dataclass
from langchain.chat_models import ChatOpenAI
import openai
import os
from dotenv import load_dotenv, find_dotenv


load_dotenv(find_dotenv())

def not_implemented(input_question:str):
    raise NotImplementedError(f"This function is not implemented yet. {input_question=}")
@dataclass
class Conversation:
    agent: Optional[Agents]
    level: int
    memory: ConversationSummaryBufferMemory
    channel: str

    #@retry(stop=stop_after_attempt(3))
    async def ask(
        self,
        input_question: str,
        level: int,
        memory: ConversationSummaryBufferMemory,
        channel: str,
        agent: Agents = Agents.Aria,
    ) -> str:
        level = level - 1
        print("""
              *******************************************
              *******************************************
              *******************************************
              AGENT IS""", agent)
        tools: List[Tool] = [ Tool(
                    name=Tools[nm].name,
                    func=not_implemented, 
                    coroutine=partial(Tools[nm].value.coroutine if Tools[nm].value.coroutine else self.ask, memory=self.memory, channel=channel, agent=Agents[nm] if hasattr(Agents, nm) else Agents.Aria, level=level),
                    description=Tools[nm].value.description)
                    for nm in agent.value.tool_names]
        tools_description = "\n\t".join([f"{tool.name}:{tool.description}"for tool in tools])
        initialised_agent = initialize_agent(
                tools,
                agent.value.model,
                agent=AgentType.OPENAI_MULTI_FUNCTIONS,
                verbose=True,
                memory=memory,
                prompt=agent.value.prompt_template)
        if level > 0:
            answer = await initialised_agent.arun(input=agent.value.prompt_template.format( input_question=input_question, level=level, tools_description=tools_description))
        else:
            answer = await initialised_agent.arun(input=f"please summarise the answer to the question: {input_question}. You may not call any functions or use any tools." )
        
        return answer

def make_function_async(func):
    async def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper
@dataclass(frozen=True)
class ToolDetails:
    name: str
    description: str
    coroutine: Optional[Callable] = None

async def get_gorilla_response(input_question:str, memory: ConversationSummaryBufferMemory,  
                               agent: Agents, channel: str = None, level: int =None):
    gorilla_llm: ChatOpenAI = agent.value.model
    
    chat_and_code = await gorilla_llm.apredict(input_question)
    code = chat_and_code.split(">>>:")[-1].strip("\n")
    chat = chat_and_code.split(">>>:")[0].strip("\n")
    print(f""" ***********************************************************
          ***********************GORILLA START {agent.value.display_name}***************************""")
    print(f"  SAYS {chat=}")
    print(f"  CODE {code=}")
    print("EXECUTING")
    code_result = exec(code)
    print("EXECUTED")
    print("CODE RESULT", code_result)
    print(""" ***********************************************************
          ***********************GORILLA END***************************""")
    return code_result


class Tools(Enum):
    Aria=ToolDetails(
                name="Aria",
                #partially initialise so just input is needed
                coroutine=None,
                description="Adria is a language model that can answer questions and generate text. She is aware of all of the other agents and their capabilities. Which she can use as tools in order to decompose , delegate and recompose a problem into a solution.",
            )
    Gorilla=ToolDetails(
                name="Gorilla",
                coroutine=get_gorilla_response,
                description="ONLY USE THIS TOOL TO GENERATE CODE FOR Specific Scientifc, Legal, Physics, Questions. Gorilla should not be used to answer general knowledge questions, instead Ask Geoffrey or Aria or BingSearch.",
            )
    Geoffrey=ToolDetails(
                name="Geoffrey",
                coroutine=None,
                description="Geoffrey is an intelligent general language model that can perform complex reasoning and solve intridcate logical problems. He is best used when the problem is too complex for Aria to solve on her own and doesnt require expert knowledge.")
    SearchBing =ToolDetails(
                name="SearchBing",
                description="This tool will search the internet for the answer to your question. It is best used when the problem requires the most up to date information, api defintion or publicshed context.",
                coroutine=search_bing)
    Speak = ToolDetails(
        name="Speak",
        description="Use this tool if you make a discovery that you feel should be reported to the original questioner. This tool will convert text to speech and post it to the designated channel as if it was said by Aria",
        coroutine=speak)
