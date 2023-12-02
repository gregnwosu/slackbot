
import pytest, asyncio
from dotenv import load_dotenv, find_dotenv
from slackbot import agent


import os
def test_agency():

    prompt = "Can you please find out what legal action i can take if my ex locked me out of my house?"
    agent.agency.get_completion(prompt)