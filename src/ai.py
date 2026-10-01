from dotenv import load_dotenv
import requests
import os
import json
import asyncio

load_dotenv()
API_KEY = os.getenv("HACKCLUBAI_API_KEY")
URL = "https://ai.hackclub.com/proxy/v1/chat/completions"


MODEL = "anthropic/claude-sonnet-5.5"
MODEL = "openai/gpt-6-luna"
MODEL = "minimax/minimax-m2-her"

MODEL = "deepseek/deepseek-v4.1-flash:nitro"

with open("kernel\\v0.3.md") as f:
    PROMPT = f.read()


try:
    with open("messages.json", "r") as f:
        messages = json.load(f)
        messages[0] = {"role": "system", "content": PROMPT}
except FileNotFoundError:
    with open("messages.json", "w") as f:
        messages = []
        if PROMPT:
            messages.append({"role": "system", "content": PROMPT})
        json.dump(messages, f, indent=4)

def make_request() -> requests.models.Response:
    return requests.post(
        url = URL,
        headers = {"Authorization": f"Bearer {API_KEY}"},
        json = {
            "model": MODEL,
            "messages": messages
        }
    )

async def get_response(user_input: str) -> tuple[str, str]:
    messages.append({"role": "user", "content": user_input})

    response = await asyncio.to_thread(make_request)
    print(response.text)
    response_message = response.json()["choices"][0]["message"]["content"]
    response_reasoning = response.json()["choices"][0]["message"]["reasoning"]

    messages.append({"role": "assistant", "content": response_message})

    with open("messages.json", "w") as f:
        json.dump(messages, f, indent=4)

    return response_message, response_reasoning

