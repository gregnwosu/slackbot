from enum import Enum


# from chromadb.utils import embedding_functions
# from autogen import AssistantAgent, UserProxyAgent, config_list_from_json
# from autogen.agentchat.contrib.retrieve_assistant_agent import RetrieveAssistantAgent
# from autogen.agentchat.contrib.retrieve_user_proxy_agent import RetrieveUserProxyAgent
# Load LLM inference endpoints from an env variable or a file
# openai_key = os.environ.get("OPENAI_KEY")
# config_list = [{'model': 'gpt-4', 'api_key': openai_key},]
# openai_ef = embedding_functions.OpenAIEmbeddingFunction(
#         api_key=openai_key,
#         model_name="text-embedding-ada-002",
#     )
# assistant = RetrieveAssistantAgent("assistant", system_message="You are a helpful assistant.", llm_config={"config_list": config_list})
# rag_proxy_agent = RetrieveUserProxyAgent("ragproxyagent",
#                                         retrieve_config={
#                                             "task": "qa",
#                                             "docs_path": "/home/greg/Documents/gregvsesta",
#                                             "embedding_function": openai_ef
#                                         },
#                                         code_execution_config={"work_dir": "coding"})



class Agents(Enum):
    Aria = None
    # Aria: ConversableAgent  = rag_proxy_agent
    # Gorilla = Agent(
    #     "Gorilla",
    #     LLM.Gorilla.value,
    #     PromptTemplates.Gorilla.value,
    #     ["SearchBing", "Geoffrey"],
    #     AsyncWebClient(token=os.environ["SLACK_BOT_TOKEN"]),
    # )
    # Geoffrey = Agent(
    #     "Geoffrey",
    #     LLM.GPT4.value,
    #     PromptTemplates.Geoffrey.value,
    #     ["SearchBing", "Gorilla"],
    #     AsyncWebClient(token=os.environ["SLACK_BOT_TOKEN"]),
    # )
