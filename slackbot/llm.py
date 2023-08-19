from enum import Enum
from langchain.chat_models import ChatOpenAI

import os

class LLM(Enum):
    Gorilla = ChatOpenAI(
                openai_api_base="http://zanino.millennium.berkeley.edu:8000/v1",
                openai_api_key="EMPTY",
                model="gorilla-7b-hf-v1",
                verbose=True)
    GPT4 =  ChatOpenAI(
            model_name="gpt-4",
            temperature=0,
            openai_api_key=os.environ["OPENAI_API_KEY"])
    GPT3_5_TURBO = ChatOpenAI(
            model_name="gpt-3.5-turbo",
            temperature=1,
            openai_api_key=os.environ["OPENAI_API_KEY"]),
    