# VoiceRAG: An Application Pattern for RAG + Voice Using Azure AI Search and the GPT-4o Realtime API for Audio

This repo contains an example of how to implement RAG support in applications that use voice as their user interface, powered by the GPT-4o realtime API for audio along with Azure AI search for RAG. This code is customized form of Azure-Samples(https://github.com/Azure-Samples/aisearch-openai-rag-audio)

Video Link - https://www.youtube.com/watch?v=vCTWVPcI3C4


## Features

* **Voice interface**: The app uses the browser's microphone to capture voice input, and sends it to the backend where it is processed by the Azure OpenAI GPT-4o Realtime API.
* **RAG (Retrieval Augmented Generation)**: The app uses the Azure AI Search service to answer questions about a knowledge base, and sends the retrieved documents to the GPT-4o Realtime API to generate a response.
* **Audio output**: The app plays the response from the GPT-4o Realtime API as audio, using the browser's audio capabilities.
* **Citations**: The app shows the search results that were used to generate the response.

### Architecture Diagram

The `RTClient` in the frontend receives the audio input, sends that to the Python backend which uses an `RTMiddleTier` object to interface with the Azure OpenAI real-time API, and includes a tool for searching Azure AI Search.

![Diagram of real-time RAG pattern](RTMTPattern.png)


## Getting Started

### Local environment

1. Install the required tools:
   * [Node.js](https://nodejs.org/)
   * [Python >=3.11](https://www.python.org/downloads/)
      * **Important**: Python and the pip package manager must be in the path in Windows for the setup scripts to work.
      * **Important**: Ensure you can run `python --version` from console. On Ubuntu, you might need to run `sudo apt install python-is-python3` to link `python` to `python3`.
   * [Git](https://git-scm.com/downloads)
   * [Powershell](https://learn.microsoft.com/powershell/scripting/install/installing-powershell) - For Windows users only.

2. Clone the repo (`git clone https://github.com/Azure-Samples/aisearch-openai-rag-audio`)
3. Proceed to the next section.

## Deploying the Azure Resources

Follow the steps provided in the attched video for deploying Azure Resources.

1. Create Azure OpenAI service in US East 2 region.

2. Deploy Realtime and Embedding models.

3. Create Azure Storage account and upload files in the container

4. Create Azure AI Search Service in US East 2.

5. Import and Vectorize data using Azure AI Search service and Storage account.

## Local APP Deployment

1. Create a file .env in the `app/backend` and update the contents:

   ```shell
      AZURE_OPENAI_ENDPOINT=XXXXXX
      AZURE_OPENAI_REALTIME_DEPLOYMENT=gpt-4o-realtime-preview
      AZURE_OPENAI_API_KEY=XXXXX
      AZURE_OPENAI_REALTIME_VOICE_CHOICE=<choose one: echo, alloy, shimmer>
      AZURE_SEARCH_ENDPOINT=XXXX
      AZURE_SEARCH_INDEX=XXXX
      AZURE_SEARCH_API_KEY=XXXX
      AZURE_SEARCH_SEMANTIC_CONFIGURATION=XXXX
      AZURE_SEARCH_IDENTIFIER_FIELD=chunk_id
      AZURE_SEARCH_TITLE_FIELD=title
      AZURE_SEARCH_CONTENT_FIELD=chunk
      AZURE_SEARCH_EMBEDDING_FIELD=text_vector
      AZURE_SEARCH_USE_VECTOR_QUERY=true
      AZURE_TENANT_ID=XXXX
   ```

2. Run this command to start the app:

   Windows:

   ```pwsh
   pwsh .\scripts\start.ps1
   ```

   Linux/Mac:

   ```bash
   ./scripts/start.sh
   ```

4. The app is available on [http://localhost:8765](http://localhost:8765).

## Resources

* [Blog post: VoiceRAG](https://aka.ms/voicerag)
* [Azure OpenAI Realtime Documentation](https://github.com/Azure-Samples/aoai-realtime-audio-sdk/)
