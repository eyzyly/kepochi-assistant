import json
import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

MODEL = os.getenv("KEPOCHI_MODEL", "gpt-4o-mini")

_client = None


def client():
    global _client
    if _client is None:
        _client = OpenAI()
    return _client


def chat_json(system_prompt, user_prompt):
    response = client().chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        response_format={"type": "json_object"},
    )
    return json.loads(response.choices[0].message.content)
