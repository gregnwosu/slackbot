
import pytest, asyncio
from dotenv import load_dotenv, find_dotenv
from slackbot import agent


import os
def test_agency():

    prompt = "Can you please find out what legal action i can take if my ex locked me out of my house?"
    message_output_iterator = agent.agency.get_completion(prompt)

    for i in range(5):
        msg_output = next(message_output_iterator)
        print(msg_output)
        msg_output.cprint()
        print(msg_output.content)
