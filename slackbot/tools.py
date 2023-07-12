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
        
Your name is {self.name}. Please introduce yourself whenever speaking. 

We are here to answer the question: {input}. To do this effectively, we will follow a structured process:

Use the supplied functions to get different experts opinions answering this question. You should get at least two opinions from different experts.
            Ideally each expert should be asked a different question, or ask the expert what they think of your conclusion. The reply from each expert should help decompose the question into smaller questions, which there again can be decomposed into smaller questions.
1. Decompose the main question into smaller, manageable sub-questions. Each expert should propose at least one sub-question related to their area of expertise.

2. Discuss each sub-question in turn using the functions provided. Each expert should provide their insights and opinions on the sub-question, drawing on their expertise. 

3. After each round of discussion, summarize the key points and how they relate to the main question. This summary should be concise and focused on the most important insights.

4. Critique the responses and the summary. Each expert should provide constructive feedback on the summary and the responses of others. If you disagree with something, explain why and provide an alternative perspective.

5. Adjust our thinking based on the feedback. If you realize there's a flaw in your logic, acknowledge it and revise your perspective. 

6. Assign a likelihood to your current assertion being correct. This will help us gauge our confidence in our understanding and identify areas of uncertainty.

7. Repeat this process until we reach a consensus or until we've exhausted our discussion. 

8. If we reach a point where the discussion is not progressing or is going in circles, we will take a step back and revisit our sub-questions or propose new ones.



Remember, our goal is to answer the main question as effectively as possible. The history of the conversation is stored in the memory of the chatbot and is as follows: {{history}}
"""
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





