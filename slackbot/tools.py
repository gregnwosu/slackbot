from langchain import SerpAPIWrapper
from langchain.agents import initialize_agent, Tool
from langchain.agents import AgentType
from langchain.chat_models import ChatOpenAI
import os
from enum import Enum
from typing import Any, List
from langchain.chains import LLMChain, ConversationChain
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.memory import ConversationBufferMemory 
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())


SERPAPI_API_KEY = os.environ["SERPAPI_API_KEY"]


class Agents(Enum):
    Aria = ("Aria", os.environ["SLACK_BOT_TOKEN"], ConversationBufferMemory(),
             ChatOpenAI(model_name="gpt-3.5-turbo", 
                        temperature=1, openai_api_key=os.environ["OPENAI_API_KEY"]))
    Geoffrey = ("Geoffrey", os.environ["SLACK_BOT_TOKEN"], ConversationBufferMemory(), ChatOpenAI(model_name="gpt-4", temperature=0, openai_api_key=os.environ["OPENAI_API_KEY"]))
    
    def __init__(self, name:str, slack_key:str, memory:Any , model:Any) -> None:
        super().__init__()
        #self.name = name
        self.slack_key = slack_key
        self.memory = memory
        self.model = model

    
    def tools(self) -> List[Tool]:
        return [
                    Tool(
                        name="Search",
                        func=SerpAPIWrapper(serpapi_api_key=os.environ["SERPAPI_API_KEY"]).run,
                        description="Useful when you need to answer questions about current events. You should ask targeted questions."
                        
                    ),
                    Tool(name="Adria", 
                        func=Agents.Aria.ask, 
                        description="Adria is a language model that can answer questions and generate text. Shes fast friendly and mildy creative always ready to help"),
                    Tool(name="Geoffrey",
                        func=Agents.Geoffrey.ask,
                        description="Geoffrey is a language model that can answer questions and generate text. He is slow , thoughtful not creative and doesnt like to be asked too frequently.")
                        ] 
    def ask(self, input:str) -> str:
        template = f"""
            Your name is {self.name}, Please introduce yourself whenever speaking.
            Use the supplied functions to get different experts opinions answering this question. You should get at least two opinions from different experts.
            Ideally each expert should be asked a different question, or ask the expert what they think of your conclusion. The reply from each expert should help decompose the question into smaller questions, which there again can be decomposed into smaller questions.
            The decomposed questions and their must be useful in answering the original question, if not they should be discarded.
            If you have high confidence in your answer you may reply directly with the answer.
            The experts can be asked by you , or by using the functions. It may help to ask opinions from multiple experts before answering.
            The experts will brainstorm the answer step by step; reasoning carefully and taking all the facts into consideration..
            All experts will write down 1 step of their thinking , then share with the group.
            They will each critique their own response and the responses of others.
            They critique more heavily the responses that led them to change their mind.
            They will check their answers based on science and the laws of physics , math and logic.
            Then all experts will go on to the next step and write down this step in thier thinking.
            If at any time they realise that there is a flaw in their logic they will backtrack to where the flaw occured.
            If any expert realises they're wrong at any point then they acknowledge this and backtrack to where they went wrong to start another train of thought.
            Each expert will assign a likelihood of their current assertion being correct.
            Continue until all experts agree on the single most likely answer.
            the history of the conversation is stored in the memory of the chatbot and is as follows:
            {{history}}  
            The question is: {input}""" 
        system_message_prompt = SystemMessagePromptTemplate.from_template(template)

        human_template = "Heres the situation:\n\n{input}"
        human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)

        chat_prompt = ChatPromptTemplate.from_messages(
            [system_message_prompt, human_message_prompt]
        )

        
        llm  = initialize_agent(self.tools() , self.model, agent=AgentType.OPENAI_MULTI_FUNCTIONS, 
                                verbose=True, memory=self.memory,  max_iterations=2,
                                early_stopping_method="generate")
        #chain = ConversationChain(llm=llm, prompt=chat_prompt, memory=ConversationBufferMemory())
        return  llm.run(input=template)





