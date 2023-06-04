from typing import Any, Coroutine
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
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

from cachetools import TTLCache, cached


#TODO make this into a tool.
def draft_email(user_input, name="Dave") -> str:
    chat = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=1)

    template = """
    
    You are a helpful assistant that drafts an email reply based on an a new email.
    
    Your goal is to help the user quickly create a perfect email reply.
    
    Keep your reply short and to the point and mimic the style of the email so you reply in a similar manner to match the tone.
    
    Start your reply by saying: "Hi {name}, here's a draft for your reply:". And then proceed with the reply on a new line.
    
    Make sure to sign of with {signature}.
    
    """

    signature = f"Kind regards, \n\{name}"
    system_message_prompt = SystemMessagePromptTemplate.from_template(template)

    human_template = "Here's the email to reply to and consider any other comments from the user for reply as well: {user_input}"
    human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)

    chat_prompt = ChatPromptTemplate.from_messages(
        [system_message_prompt, human_message_prompt]
    )

    chain = LLMChain(llm=chat, prompt=chat_prompt)
    return chain.run(user_input=user_input, signature=signature, name=name)
    

   


elevenlabs.set_api_key(os.environ["ELEVENLABS_API_KEY"])


@cached(cache=TTLCache(maxsize=100, ttl=300))
def openai_llm():
    return OpenAI(temperatture=0, openai_api_key=os.environ["OPENAI_API_KEY"])

# no need to record audio, just send the audio file to openai
# def record_audio(duration, fs, channels):
#     print("Recording...")
#     recording = sd.rec(int(duration * fs), samplerate=fs, channels=channels)
#     sd.wait()
#     print("Finished recording.")
#     return recording


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
        return draft_email(text)
    

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

