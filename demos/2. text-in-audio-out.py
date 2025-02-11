import base64
import asyncio
import os
from azure.core.credentials import AzureKeyCredential
from rtclient import (
    ResponseCreateMessage, # This class is used to create a message that will be sent to the Real-Time API
    RTLowLevelClient, # This class is used to interact with the Real-Time API using low-level methods such as send and recv
    ResponseCreateParams, # This class is used to define the parameters of the response message that will be sent to the Real-Time API by the ResponseCreateMessage class
    RequestCreateMessage,
    RequestCreateParams
)

# Set environment variables or edit the corresponding values here.
api_key = os.environ["AZURE_OPENAI_API_KEY"] = "3EIvqTThR1zWk9fTBOEnMrh4sZwyGSDpwOFoWvmPRtfQYSO7v3KoJQQJ99BAACHYHv6XJ3w3AAAAACOGmGUD"
endpoint = os.environ["AZURE_OPENAI_ENDPOINT"] = "https://ai-aifoundryhub404880382143.openai.azure.com/openai/realtime/"
deployment = "gpt-4o-realtime-preview"

async def text_in_audio_out():
    async with RTLowLevelClient(
        url=endpoint,
        azure_deployment=deployment,
        key_credential=AzureKeyCredential(api_key) 
    ) as client:
        await client.send(
            ResponseCreateMessage(
                response=ResponseCreateParams(
                    modalities={"audio", "text"}, 
                    instructions="Please assist the user."
                )
            )
        )
        done = False
        while not done:
            message = await client.recv()
            match message.type:
                case "response.done": # The "done" message type indicates that the conversation has ended
                    done = True
                case "error":
                    done = True
                    print(message.error)
                case "response.audio_transcript.delta": # Text data is received as a string through the "delta" field which is defined in the message schema
                    print(f"Received text delta: {message.delta}")
                case "response.audio.delta": # Audio data is received as base64 encoded bytes
                    buffer = base64.b64decode(message.delta)
                    print(f"Received {len(buffer)} bytes of audio data.")
                case _: # Other message types are ignored
                    pass

async def main():
    await text_in_audio_out() # Run the text_in_audio_out function asynchronously

asyncio.run(main())