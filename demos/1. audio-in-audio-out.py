# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

import asyncio # This module is used to run asynchronous code
import base64
import os
import sys

import numpy as np
import soundfile as sf
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv # This module is used to load environment variables from a .env file
from scipy.signal import resample

from rtclient import (
    InputAudioBufferAppendMessage,
    InputAudioTranscription,
    RTLowLevelClient,
    ServerVAD,
    SessionUpdateMessage,
    SessionUpdateParams,
)

# Load environment variables from the .env file
load_dotenv(dotenv_path='/workspaces/AudioRAG-realtime/aoai.env')

def resample_audio(audio_data, original_sample_rate, target_sample_rate):
    number_of_samples = round(len(audio_data) * float(target_sample_rate) / original_sample_rate)
    resampled_audio = resample(audio_data, number_of_samples)
    return resampled_audio.astype(np.int16)


async def send_audio(client: RTLowLevelClient, audio_file_path: str): # the audio file is read using soundfile, base64 encoded, and then sent as InputAudioBufferAppendMessage
    sample_rate = 24000 # Sample rate is the number of samples of audio carried per second, measured in Hz.
    duration_ms = 100 # Duration of the audio chunk in milliseconds
    samples_per_chunk = sample_rate * (duration_ms / 1000)
    bytes_per_sample = 2
    bytes_per_chunk = int(samples_per_chunk * bytes_per_sample)

    extra_params = (
        {
            "samplerate": sample_rate,
            "channels": 1,
            "subtype": "PCM_16",
        }
        if audio_file_path.endswith(".raw")
        else {}
    )

    audio_data, original_sample_rate = sf.read(audio_file_path, dtype="int16", **extra_params)

    if original_sample_rate != sample_rate:
        audio_data = resample_audio(audio_data, original_sample_rate, sample_rate)

    audio_bytes = audio_data.tobytes()

    for i in range(0, len(audio_bytes), bytes_per_chunk):
        chunk = audio_bytes[i : i + bytes_per_chunk]
        base64_audio = base64.b64encode(chunk).decode("utf-8")
        await client.send(InputAudioBufferAppendMessage(audio=base64_audio))


async def receive_messages(client: RTLowLevelClient):
    while not client.closed:
        message = await client.recv()
        if message is None:
            continue
        match message.type:
            case "session.created":
                print("Session Created Message")
                print(f"  Model: {message.session.model}")
                print(f"  Session Id: {message.session.id}")
                pass
            case "error":
                print("Error Message")
                print(f"  Error: {message.error}")
                pass
            case "input_audio_buffer.committed":
                print("Input Audio Buffer Committed Message")
                print(f"  Item Id: {message.item_id}")
                pass
            case "input_audio_buffer.cleared":
                print("Input Audio Buffer Cleared Message")
                pass
            case "input_audio_buffer.speech_started":
                print("Input Audio Buffer Speech Started Message")
                print(f"  Item Id: {message.item_id}")
                print(f"  Audio Start [ms]: {message.audio_start_ms}")
                pass
            case "input_audio_buffer.speech_stopped":
                print("Input Audio Buffer Speech Stopped Message")
                print(f"  Item Id: {message.item_id}")
                print(f"  Audio End [ms]: {message.audio_end_ms}")
                pass
            case "conversation.item.created":
                print("Conversation Item Created Message")
                print(f"  Id: {message.item.id}")
                print(f"  Previous Id: {message.previous_item_id}")
                if message.item.type == "message":
                    print(f"  Role: {message.item.role}")
                    for index, content in enumerate(message.item.content):
                        print(f"  [{index}]:")
                        print(f"    Content Type: {content.type}")
                        if content.type == "input_text" or content.type == "text":
                            print(f"  Text: {content.text}")
                        elif content.type == "input_audio" or content.type == "audio":
                            print(f"  Audio Transcript: {content.transcript}")
                pass
            case "conversation.item.truncated":
                print("Conversation Item Truncated Message")
                print(f"  Id: {message.item_id}")
                print(f" Content Index: {message.content_index}")
                print(f"  Audio End [ms]: {message.audio_end_ms}")
            case "conversation.item.deleted":
                print("Conversation Item Deleted Message")
                print(f"  Id: {message.item_id}")
            case "conversation.item.input_audio_transcription.completed":
                print("Input Audio Transcription Completed Message")
                print(f"  Id: {message.item_id}")
                print(f"  Content Index: {message.content_index}")
                print(f"  Transcript: {message.transcript}")
            case "conversation.item.input_audio_transcription.failed":
                print("Input Audio Transcription Failed Message")
                print(f"  Id: {message.item_id}")
                print(f"  Error: {message.error}")
            case "response.created":
                print("Response Created Message")
                print(f"  Response Id: {message.response.id}")
                print("  Output Items:")
                for index, item in enumerate(message.response.output):
                    print(f"  [{index}]:")
                    print(f"    Item Id: {item.id}")
                    print(f"    Type: {item.type}")
                    if item.type == "message":
                        print(f"    Role: {item.role}")
                        match item.role:
                            case "system":
                                for content_index, content in enumerate(item.content):
                                    print(f"    [{content_index}]:")
                                    print(f"      Content Type: {content.type}")
                                    print(f"      Text: {content.text}")
                            case "user":
                                for content_index, content in enumerate(item.content):
                                    print(f"    [{content_index}]:")
                                    print(f"      Content Type: {content.type}")
                                    if content.type == "input_text":
                                        print(f"      Text: {content.text}")
                                    elif content.type == "input_audio":
                                        print(f"      Audio Data Length: {len(content.audio)}")
                            case "assistant":
                                for content_index, content in enumerate(item.content):
                                    print(f"    [{content_index}]:")
                                    print(f"      Content Type: {content.type}")
                                    print(f"      Text: {content.text}")
                    elif item.type == "function_call":
                        print(f"    Call Id: {item.call_id}")
                        print(f"    Function Name: {item.name}")
                        print(f"    Parameters: {item.arguments}")
                    elif item.type == "function_call_output":
                        print(f"    Call Id: {item.call_id}")
                        print(f"    Output: {item.output}")
            case "response.done":
                print("Response Done Message")
                print(f"  Response Id: {message.response.id}")
                if message.response.status_details:
                    print(f"  Status Details: {message.response.status_details.model_dump_json()}")
                break
            case "response.output_item.added":
                print("Response Output Item Added Message")
                print(f"  Response Id: {message.response_id}")
                print(f"  Item Id: {message.item.id}")
            case "response.output_item.done":
                print("Response Output Item Done Message")
                print(f"  Response Id: {message.response_id}")
                print(f"  Item Id: {message.item.id}")

            case "response.content_part.added":
                print("Response Content Part Added Message")
                print(f"  Response Id: {message.response_id}")
                print(f"  Item Id: {message.item_id}")
            case "response.content_part.done":
                print("Response Content Part Done Message")
                print(f"  Response Id: {message.response_id}")
                print(f"  ItemPart Id: {message.item_id}")
            case "response.text.delta":
                print("Response Text Delta Message")
                print(f"  Response Id: {message.response_id}")
                print(f"  Text: {message.delta}")
            case "response.text.done":
                print("Response Text Done Message")
                print(f"  Response Id: {message.response_id}")
                print(f"  Text: {message.text}")
            case "response.audio_transcript.delta":
                print("Response Audio Transcript Delta Message")
                print(f"  Response Id: {message.response_id}")
                print(f"  Item Id: {message.item_id}")
                print(f"  Transcript: {message.delta}")
            case "response.audio_transcript.done":
                print("Response Audio Transcript Done Message")
                print(f"  Response Id: {message.response_id}")
                print(f"  Item Id: {message.item_id}")
                print(f"  Transcript: {message.transcript}")
            case "response.audio.delta":
                print("Response Audio Delta Message")
                print(f"  Response Id: {message.response_id}")
                print(f"  Item Id: {message.item_id}")
                print(f"  Audio Data Length: {len(message.delta)}")
            case "response.audio.done":
                print("Response Audio Done Message")
                print(f"  Response Id: {message.response_id}")
                print(f"  Item Id: {message.item_id}")
            case "response.function_call_arguments.delta":
                print("Response Function Call Arguments Delta Message")
                print(f"  Response Id: {message.response_id}")
                print(f"  Arguments: {message.delta}")
            case "response.function_call_arguments.done":
                print("Response Function Call Arguments Done Message")
                print(f"  Response Id: {message.response_id}")
                print(f"  Arguments: {message.arguments}")
            case "rate_limits.updated":
                print("Rate Limits Updated Message")
                print(f"  Rate Limits: {message.rate_limits}")
            case _:
                print("Unknown Message")


def get_env_var(var_name: str) -> str:
    value = os.environ.get(var_name)
    if not value:
        raise OSError(f"Environment variable '{var_name}' is not set or is empty.")
    return value


async def with_azure_openai(audio_file_path: str):
    key = os.environ["AZURE_OPENAI_API_KEY"]
    endpoint = os.environ["AZURE_OPENAI_ENDPOINT"]
    deployment = os.environ["AZURE_OPENAI_DEPLOYMENT"]

    async with RTLowLevelClient(
        endpoint, key_credential=AzureKeyCredential(key), azure_deployment=deployment
    ) as client:
        await client.send(
            SessionUpdateMessage(
                session=SessionUpdateParams(
                    # instructions="<your system instructions>" # Optional system prompt
                    turn_detection=ServerVAD(type="server_vad"), # Server VAD (Voice Acivity Detection) is used to detect the start and end of speech. Turn detection is used to detect the end of a turn.
                    input_audio_transcription=InputAudioTranscription(model="whisper-1"), # The model used for audio transcription is "whisper-1". This model is optimized for real-time transcription.
                )
            )
        )

        await asyncio.gather(send_audio(client, audio_file_path), receive_messages(client)) # The send_audio and receive_messages functions are run concurrently


if __name__ == "__main__":
    load_dotenv()
    file_path = sys.argv[1]
    if len(sys.argv) == 2:
        asyncio.run(with_azure_openai(file_path))
    else:
        print("Usage: python sample.py <audio file>")
        sys.exit(1)