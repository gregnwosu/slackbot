from dataclasses import dataclass
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
import azure.cognitiveservices.speech as speechsdk
import azure.cognitiveservices.speech as speechsdk

load_dotenv(find_dotenv())


@dataclass
class InMemoryStream(speechsdk.audio.PullAudioInputStreamCallback):
    _buffer: bytes
    _position: int = 0

    def read(self, size: int) -> bytes:
        chunk, self._position = self._buffer[self._position:self._position + size], self._position + size
        return chunk

    def close(self):
        pass

    @property
    def audio_config(self) -> speechsdk.audio.AudioConfig:
        return speechsdk.audio.AudioConfig(stream=speechsdk.audio.PullAudioInputStream(self))

    async def speech_to_text(self) -> str:
        primary_access_key = await get_secret("slackbot-synth-primary-access-key")
        endpoint = await get_secret("slackbot-synth-endpoint")
        
        # Create a speech configuration
        speech_config = speechsdk.SpeechConfig(subscription=primary_access_key, endpoint=endpoint)
        
        # Create a speech recognizer
        recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=self.audio_config)
        
        # Recognize the speech from the audio stream
        result = await recognizer.recognize_once_async()
        
        # Check the result for any errors and return the recognized text
        if result.reason == speechsdk.ResultReason.RecognizedSpeech:
            return result.text
        elif result.reason == speechsdk.ResultReason.NoMatch:
            return "No speech could be recognized."
        elif result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = result.cancellation_details
            return f"Speech Recognition canceled: {cancellation_details.reason}. {cancellation_details.error_details}"


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

    data: bytes = result.audio_data
    return data

async def speak( input_question: str, channel:str, agent: Agents, memory=None, level=None) -> str:
    data = await text_to_speech(input_question)
    
    response = await agent.value.slack_client.files_upload_v2(
        channel=channel,
        content=data,
        title="audio.mp3",
        initial_comment=input_question,
    )

    return response["data"]