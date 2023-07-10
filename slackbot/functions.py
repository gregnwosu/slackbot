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


async def generate_audio(text,  cache: aioredis.Redis, voice="Bella", model="eleven_monolingual_v1"):
    if result := await cache.get(text):
        return result
    elevenlabs.set_api_key(os.environ["ELEVENLABS_API_KEY"])
    audio = elevenlabs.generate(text=text, voice=voice, model=model)
    await cache.set(text, audio)
    return audio


#TODO this needs to be changed to use OpenAI function calling.
# There will be a function called ask experts which will take a list of experts to call
# Ask experts will call ask expert.
# Each enum of experts will have a name a model and a slackbot api key
# Ask expert will call the convo model but with the depth decremented, when the value is 0 it will not call any more openai function calling
# when thre response is a function call ask epert will call the function with the expert required but with the depth decremented.


async def convo(user_input:str, expert_name="Dave", channel="admin") -> str:
    chat = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=1)

    template = f"""
    Imagine three different experts are answering this question.
    They will brainstorm the answer step by step; reasoning carefully and taking all the facts into consideration..
    All experts will write down 1 step of their thinking , then share with the group.
    They will each critique their own response and the responses of others.
    They critique more heavily the responses that led them to change their mind.
    They will check their answers based on science and the laws of physics , math and logic.
    Then all experts will go on to the next step and write down this step in thier thinking.
    If at any time they realise that there is a flaw in their logic they will backtrack to where the flaw occured.
    If any expert realises they're wrong at any point then they acknowledge this and backtrack to where they went wrong to start another train of thought.
    Each expert will assign a likelihood of their current assertion being correct.
    Continue until all experts agree on the single most likely answer.
    The Question is: {user_input}
    
    """

    signature = f"Kind regards, \n\{expert_name}"
    system_message_prompt = SystemMessagePromptTemplate.from_template(template)

    human_template = "Here's the reply from the panel of experts:}"
    human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)

    chat_prompt = ChatPromptTemplate.from_messages(
        [system_message_prompt, human_message_prompt]
    )
    memory_key = f"expert:{expert_name},channel:{channel}"
    chain = ConversationChain(llm=chat, prompt=chat_prompt, memory=ConversationBufferMemory(memory_key=memory_key))
    return await chain.arun(user_input=user_input, signature=signature, name=expert_name)


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

