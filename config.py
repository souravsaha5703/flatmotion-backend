from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

A4F_API_KEY = os.getenv("A4F_API_KEY_VALUE")
A4F_BASE_URL = os.getenv("A4F_BASE_URL")

client = OpenAI(
    api_key=A4F_API_KEY,
    base_url=A4F_BASE_URL,
)