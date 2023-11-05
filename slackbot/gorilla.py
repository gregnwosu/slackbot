
from slackbot.agent import Agents



async def get_gorilla_response(
    input_question: str,
    memory,
    agent: Agents,
    channel: str = None,
    level: int = None,
):
    
    
    
    print(
        f""" ***********************************************************
          ***********************GORILLA START {agent.value.display_name}***************************"""
    )

    print("EXECUTING")
    try:
        pass
        
    except Exception as e:
        return f""" I tried to answer {input_question} by generating this code :
        
       
        
        but I got an error. The error was {e}. Please ask Geoffrey to review my code and give me advice on how to fix it."""
