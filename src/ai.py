from dotenv import load_dotenv
from collections.abc import AsyncGenerator
import requests
import os
import json
import asyncio
import tools

load_dotenv()
API_KEY = os.getenv("HACKCLUBAI_API_KEY")
URL = "https://ai.hackclub.com/proxy/v1/chat/completions"


MODEL = "anthropic/claude-sonnet-5.5"
MODEL = "openai/gpt-6-luna"
MODEL = "minimax/minimax-m2-her"

MODEL = "deepseek/deepseek-v4.1-flash-1017:nitro"

with open("kernel\\v0.4.md") as f:
    PROMPT = f.read()

def load_memory(filepath: str = "messages.json") -> list:
    try:
        with open(filepath, "r") as f:
            messages = json.load(f)
            messages[0] = {"role": "system", "content": PROMPT}
            return messages
    except FileNotFoundError:
        with open("messages.json", "w") as f:
            messages = []
            if PROMPT:
                messages.append({"role": "system", "content": PROMPT})
            json.dump(messages, f, indent=4)
            return messages

messages = load_memory()

def make_request() -> requests.models.Response:
    return requests.post(
        url = URL,
        headers = {"Authorization": f"Bearer {API_KEY}"},
        json = {
            "model": MODEL,
            "messages": messages,
            "tools": tools.tools
        }
    )

def dump_memory(filepath: str = "messages.json") -> None:
    with open(filepath, "w") as f:
        json.dump(messages, f, indent=4)

async def get_response(user_input: str) -> AsyncGenerator[tuple[str, str]]:
    # print(messages)
    messages.append({"role": "user", "content": user_input})

    # Loops until model finishes tool calling chain
    while True:
        response = await asyncio.to_thread(make_request)
        # print(response.text)

        # Handles api errors
        try:
            message = response.json()["choices"][0]["message"]
        except (requests.exceptions.JSONDecodeError, KeyError):
            print(response.text)
            raise

        messages.append(message)
        dump_memory()
        response_reasoning = message["reasoning"]

        # Yields model output if it produced content
        if "content" in message and message["content"]:
            response_message = message["content"]
            yield response_message, response_reasoning

        # Runs only if a tool has been called
        if "tool_calls" in message and message["tool_calls"]:
            # print(message["tool_calls"])
            for tool_call in message["tool_calls"]:
                call_id = tool_call["id"]
                func_name = tool_call["function"]["name"]
                func_args = json.loads(tool_call["function"]["arguments"])

                # Calls the tool function through the tools module's mapping
                result = tools.TOOL_MAPPING[func_name](**func_args)

                messages.append({
                    "role": "tool",
                    "tool_call_id": call_id,
                    "content": json.dumps(result)
                })
                dump_memory()

                yield "tool_call", f"Called tool {func_name}"
        else:
            return

