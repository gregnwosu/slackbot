from enum import Enum

import os
from dotenv import find_dotenv, load_dotenv
from dataclasses import dataclass
load_dotenv(find_dotenv())


@dataclass 
class ChatOpenAI:
    openai_api_base: str = "https://api.openai.com/v1"
    openai_api_key: str = os.environ["OPENAI_API_KEY"]
    model: str = "davinci"
    model_name: str = "gpt-3"
    temperature: float = 0.7
    verbose: bool = False

class LLM(Enum):
    Gorilla = ChatOpenAI(
        openai_api_base="http://zanino.millennium.berkeley.edu:8000/v1",
        openai_api_key="EMPTY",
        model="gorilla-7b-hf-v1",
        verbose=True,
    )
    GPT4 = ChatOpenAI(
        model_name="gpt-4", temperature=0, openai_api_key=os.environ["OPENAI_API_KEY"]
    )
    GPT3_5_TURBO = ChatOpenAI(
        model_name="gpt-3.5-turbo",
        temperature=1,
        openai_api_key=os.environ["OPENAI_API_KEY"],
    )
