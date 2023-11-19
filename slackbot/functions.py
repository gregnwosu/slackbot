import datetime as dt
import os
import tempfile
from typing import Any, Coroutine

import aioredis
# import elevenlabs
import openai

# import sounddevice as sd
import soundfile as sf
from cachetools import TTLCache, cached



# async def generate_audio(
#     text, cache: aioredis.Redis, voice="Bella", model="eleven_monolingual_v1"
# ):
#     if result := await cache.get(text):
#         return result
#     elevenlabs.set_api_key(os.environ["ELEVENLABS_API_KEY"])
#     audio = elevenlabs.generate(text=text, voice=voice, model=model)
#     await cache.set(text, audio, ex=dt.timedelta(minutes=5))
#     return audio


# TODO this needs to be changed to use OpenAI function calling.
# There will be a function called ask experts which will take a list of experts to call
# Ask experts will call ask expert.
# Each enum of experts will have a name a model and a slackbot api key
# Ask expert will call the convo model but with the depth decremented, when the value is 0 it will not call any more openai function calling
# when thre response is a function call ask epert will call the function with the expert required but with the depth decremented.




def transcribe_audio(recording, fs):
    duration = 5  # duration of each recording in seconds
    sample_rate = 44100  # sample rate
    channels = 1
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_audio:
        sf.write(file=temp_audio.name, data=recording, sample_rate=sample_rate)
        temp_audio.close()
        with open(temp_audio.name, "rb") as audio_file:
            transcript = openai.Audio.transcribe("whisper-1", audio_file)
        os.remove(temp_audio.name)
    return transcript["text"].strip()





# def play_generated_audio(text, voice="Bella", model="eleven_monolingual_v1"):
#     audio = elevenlabs.generate(text=text, voice=voice, model=model)
#     elevenlabs.play(audio)


