from dataclasses import dataclass
from pydantic import BaseModel, Field
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.prompts.chat import ChatPromptTemplate, HumanMessagePromptTemplate
from langchain.output_parsers import PydanticOutputParser
from functools import partial
from typing import List, Optional
from langchain.vectorstores import Chroma
from langchain.agents import AgentType, Tool, initialize_agent
from langchain.memory import ConversationSummaryBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain.agents.agent import AgentExecutor
from slackbot import utils
from slackbot.agent import Agents
from slackbot.prompts import PromptTemplates
from slackbot.tools import Tools
# https://python.langchain.com/docs/use_cases/agent_simulations/two_agent_debate_tools


def not_implemented(input_question: str):
    raise NotImplementedError(
        f"This function is not implemented yet. {input_question=}"
    )


class ConversationResponse(BaseModel):
    question: str = Field(description="input_question")
    answer: str = Field(description="the answer to the question")
    level: int = Field(description="the level of the question")
    agent_name_asker: str = Field(description="the name of the agent that asked the question")
    agent_name_answer: str = Field(description="the name of the agent that answered the question")
    channel: str = Field(description="the name of the slack channel the question was asked in")


parser = PydanticOutputParser(pydantic_object=ConversationResponse)
@dataclass
class Conversation:
    agent: Optional[Agents] #cant have this causes the get_format_instructions to fail, as it tries to serialise agents
    level: int
    memory: ConversationSummaryBufferMemory
    channel: str

    #@utils.redis_memory_decorator
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

        tools: List[Tool] = [
            Tool(
                name=Tools[nm].name,
                func=not_implemented,
                coroutine=partial(
                    Tools[nm].value.coroutine
                    if Tools[nm].value.coroutine
                    else self.ask,
                    memory=self.memory,
                    channel=channel,
                    agent=Agents[nm] if hasattr(Agents, nm) else Agents.Aria,
                    level=level,
                ),
                description=Tools[nm].value.description,
            )
            for nm in agent.value.tool_names
        ]
        tools_description = "\n\t".join(
            [f"{tool.name}:{tool.description}" for tool in tools]
        )

        embeddings = OpenAIEmbeddings()
        from langchain import document_loaders 
        from langchain.schema.document import Document
        documents = document_loaders.TextLoader.load

        #vectorstore = Chroma.from_documents([], embeddings)
        # create a vectorstore from the a string
        vectorstore = Chroma.from_documents([Document(page_content="hi")], embeddings)

        message_template: HumanMessagePromptTemplate = HumanMessagePromptTemplate.from_template(template=agent.value.prompt_template)
        chat_prompt_template = ChatPromptTemplate.from_messages(messages=[message_template])
        chat_prompt_template_with_values = chat_prompt_template.format_prompt(tools_description=tools_description, input_question=input_question, chat_history=memory.load_memory_variables({})['history'], level=level, format_instructions=parser.get_format_instructions())
        # https://python.langchain.com/docs/modules/agents/how_to/handle_parsing_errors
        llm: AgentExecutor = initialize_agent(
            tools,
            agent.value.model,
            agent=AgentType.OPENAI_FUNCTIONS,
            verbose=True,
            #memory=memory,
            retriever=vectorstore.as_retriever(),
            prompt=chat_prompt_template_with_values,
            handle_parsing_errors=f"Check your output and make sure it conforms to the following format: {parser.get_format_instructions()} ",
            parser=parser
        )
        

       
        #if level > 0:
        answer =  await llm.arun(
           input=  chat_prompt_template_with_values,
           chat_history=memory.load_memory_variables({})['history'],
           parser=parser,
           handle_parsing_errors=f"Check your output and make sure it conforms to the following format: {parser.get_format_instructions()} ",
        )
        answer = parser.parse(answer)
        # print(f"{answer=}")

        # qa = ConversationalRetrievalChain.from_llm(llm=llm, retriever=vectorstore.as_retriever(), memory=memory)

        # answer = qa(chat_prompt_template_with_values)
        
        # else:
        #     answer = await initialised_agent.arun(
        #        # input=f"please summarise the answer to the question: {input_question}. You may not call any functions or use any tools."
        #     )

        return answer
