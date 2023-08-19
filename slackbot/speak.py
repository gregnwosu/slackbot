from slackbot.parsing.file.model import MimeType
from slackbot.vault import get_secret
from azure.cognitiveservices.speech import (
    SpeechSynthesizer,
    SpeechSynthesisOutputFormat,
    SpeechSynthesisResult,
)
from dotenv import load_dotenv, find_dotenv
from slack_sdk.web.async_client import AsyncWebClient
from slackbot.agent import Agents

load_dotenv(find_dotenv())
import azure.cognitiveservices.speech as speechsdk

async def text_to_speech(text: str) -> bytes:
    primary_access_key = await get_secret("slackbot-synth-primary-access-key")
    endpoint = await get_secret("slackbot-synth-endpoint")
    speech_config = speechsdk.SpeechConfig(
        subscription=primary_access_key,
        endpoint=endpoint
    )

    synthesizer: SpeechSynthesizer = SpeechSynthesizer(speech_config=speech_config)
    speech_config.set_speech_synthesis_output_format(
        SpeechSynthesisOutputFormat.Audio16Khz32KBitRateMonoMp3
    )

    result: SpeechSynthesisResult = synthesizer.speak_text_async(text).get()
    result.audio_data
    data: bytes = result.audio_data
    return data

async def speak( input_question: str, channel:str, agent: Agents, memory=None, level=None) -> str:
    data = await text_to_speech(input_question)

    response = await agent.value.slack_client.files_upload_v2(
        channel=channel,
        file=data,
        filename="audio.mp3",
        filetype=MimeType.AUDIO_MP3.value,
        initial_comment=input_question,
    )
    return response["data"]