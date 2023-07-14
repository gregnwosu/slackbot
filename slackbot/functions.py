from typing import Any, Coroutine
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain, ConversationChain
from langchain.agents import initialize_agent, load_tools
from langchain.agents.agent import AgentExecutor
from langchain.agents.agent_toolkits import ZapierToolkit
from langchain.llms import OpenAI 

from langchain.agents.agent_types import AgentType
from langchain.memory import ConversationBufferMemory 
from langchain.utilities.zapier import ZapierNLAWrapper
import numpy as np
import openai
#import sounddevice as sd
import soundfile as sf
import tempfile
from langchain.tools import BaseTool
from langchain.utilities.zapier import ZapierNLAWrapper
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
import os 
import elevenlabs
import aioredis
from cachetools import TTLCache, cached
import datetime as dt


async def generate_audio(text,  cache: aioredis.Redis, voice="Bella", model="eleven_monolingual_v1"):
    if result := await cache.get(text):
        return result
    elevenlabs.set_api_key(os.environ["ELEVENLABS_API_KEY"])
    audio = elevenlabs.generate(text=text, voice=voice, model=model)
    await cache.set(text, audio, ex=dt.timedelta(minutes=5))
    return audio


#TODO this needs to be changed to use OpenAI function calling.
# There will be a function called ask experts which will take a list of experts to call
# Ask experts will call ask expert.
# Each enum of experts will have a name a model and a slackbot api key
# Ask expert will call the convo model but with the depth decremented, when the value is 0 it will not call any more openai function calling
# when thre response is a function call ask epert will call the function with the expert required but with the depth decremented.


async def convo(input:str, expert_name="Dave", channel="admin") -> str:
    chat = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=1)

    template = """
    Decompose the problem into parts. Use the functions to ask the most appropriate expert for each part.
    All questions asked to an agent will be prefixed by a numeric level. The level will be decremented each time a question is asked.
    If no level is specified then the level will be 3.
    If a level is specified then the level will be decremented by 1 each time a question is asked.
    Once the level reaches 0 then no more questions will be asked to any agent. You should then recombine the answers to the questions to form the answer to the original question.
    When returning an answer to the original question you will  assign a likelihood of your current assertion being correct.
    You will  will brainstorm the answer step by step; reasoning carefully and taking all the facts into consideration..
    The maximum number of functions the you  can call is 3, after that you will stop calling functions and will return the answer to the original question.
    You will check their answers based on science and the laws of physics , math and logic.
    If at any time you realise that there is a flaw in the logic of an opinion you have  recieved you will backtrack to where the flaw occured.
    If you realise any expert is wrong at any point then acknowledge this and backtrack to where they went wrong to start another train of thought.
    
    Continue until all experts agree on the single most likely answer.
    the history of the conversation is stored in the memory of the chatbot and is as follows:
    {history}
    
    """

    ## NB  ConversationChain only supports history and input as parameters: https://github.com/hwchase17/langchain/issues/1800

    system_message_prompt = SystemMessagePromptTemplate.from_template(template)

    human_template = "Heres the situation:\n\n{input}"
    human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)

    chat_prompt = ChatPromptTemplate.from_messages(
        [system_message_prompt, human_message_prompt]
    )
    

    chain = ConversationChain(llm=chat, prompt=chat_prompt, memory=ConversationBufferMemory())
    #history and input are supplied by the conversationalbuffermemory
    return await chain.arun(input=input, )



#elevenlabs.set_api_key(os.environ["ELEVENLABS_API_KEY"])

@cached(cache=TTLCache(maxsize=100, ttl=300))
def openai_llm():
    return OpenAI(temperatture=0, openai_api_key=os.environ["OPENAI_API_KEY"])


def transcribe_audio(recording, fs):
    duration = 5  # duration of each recording in seconds
    sample_rate = 44100  # sample rate
    channels = 1
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_audio:
        sf.write(file=temp_audio.name, data=recording, sample_rate=sample_rate)
        temp_audio.close()
        with open(temp_audio.name, "rb") as audio_file:
            transcript = openai.Audio.transcribe("whisper-1", audio_file)
        os.remove(temp_audio.name)
    return transcript["text"].strip()

@cached(cache=TTLCache(maxsize=100, ttl=300))
def agi() -> AgentExecutor:
    open_ai_llm = openai_llm()
    memory = ConversationBufferMemory(memory_key="slackbot-chat-history")
    zapier = ZapierNLAWrapper(zapier_nla_api_key=os.environ["ZAPIER_API_KEY"], zapier_nla_oauth_access_token=None)
    zapier_toolkit = ZapierToolkit.from_zapier_nla_wrapper(zapier)
    tools = zapier_toolkit.get_tools() + load_tools(["human"])
    return initialize_agent(tools, open_ai_llm, memory=memory, agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION, verbose=True)
    


def play_generated_audio(text, voice="Bella", model="eleven_monolingual_v1"):
    audio = elevenlabs.generate(text=text, voice=voice, model=model)
    elevenlabs.play(audio)

class EmailTool(BaseTool):
    name = "send email via gmail"
    description = "send email via gmail"

    def _run(self, text:str) -> str:
        """Use the tool"""
        return convo(text)
    

    async def _arun(self, *args: Any, **kwargs: Any) -> Coroutine[Any, Any, Any]:
        raise NotImplementedError()
        #return await super()._arun(*args, **kwargs)
    

    # while True:
    #     print("Press spacebar to start recording.")
    #     keyboard.wait("space")  # wait for spacebar to be pressed
    #     recorded_audio = record_audio(duration, fs, channels)
    #     message = transcribe_audio(recorded_audio, fs)
    #     print(f"You: {message}")
    #     assistant_message = agent.run(message)
    #     play_generated_audio(assistant_message)

    #TODO just need to use the slack voice message to send and receive audio


