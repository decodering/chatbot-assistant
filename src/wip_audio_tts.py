from os.path import join
from openai import AzureOpenAI
from api_client import OAIClient
from utils import get_src_dir_path
from dotenv import load_dotenv
from os import getenv

load_dotenv()

MODEL = ""

client = AzureOpenAI(
    api_key=getenv("OPENAI_API_KEY"),
    azure_endpoint=getenv("OPENAI_AZURE_ENDPOINT"),
    api_version=getenv("OPENAI_API_VERSION"),
)

response = client.audio.speech.create(
    model="tts-1",
    voice="alloy",
    input="Hello world! This is a streaming test.",
)

response.stream_to_file("output.mp3")
