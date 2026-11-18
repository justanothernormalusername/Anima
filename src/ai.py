from dotenv import load_dotenv
from collections.abc import AsyncGenerator
import requests
import os
import json
import asyncio
import tools
import shutil
import logging

logger = logging.getLogger(__name__)

load_dotenv()
API_KEY = os.getenv("HACKCLUBAI_API_KEY")
URL = "https://ai.hackclub.com/proxy/v1/chat/completions"


MODEL = "anthropic/claude-sonnet-5.5"
MODEL = "openai/gpt-6-luna"
MODEL = "minimax/minimax-m2-her"

MODEL = "deepseek/deepseek-v4.1-flash-1017:nitro"

MAX_CALLS_IN_TOOL_SEQUENCE = 20

with open("kernel/v0.4.md") as f:
    PROMPT = f.read()

def init_memory(save_state: bool = False) -> list:
    with open("data/messages.json", "w") as f:
        messages = []
        if PROMPT:
            messages.append({"role": "system", "content": PROMPT})

        if save_state:
            messages.append({"role": "system", "content": "Here is the save state written by your last iteration. "})
            with open("data/save_state.md", "r") as ff:
                save_state_raw = ff.read()
            messages.append({"role": "system", "content": save_state_raw})
        json.dump(messages, f, indent=4)
        return messages

def load_memory(filepath: str = "data/messages.json") -> list:
    try:
        with open(filepath, "r") as f:
            messages = json.load(f)
            messages[0] = {"role": "system", "content": PROMPT}
            return messages
    except FileNotFoundError:
        return init_memory()

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

def dump_memory(filepath: str = "data/", include_diary: bool = False) -> None:
    with open(filepath + "messages.json", "w") as f:
        json.dump(messages, f, indent=4)
    if include_diary:
        shutil.copy2("data/diary.md", filepath)
        shutil.copy2("data/save_state.md", filepath)


async def get_response(user_input: str) -> AsyncGenerator[tuple[str, str]]:
    # print(messages)
    messages.append({"role": "user", "content": user_input})
    tool_call_count = 0

    # Loops until model finishes tool calling chain or it exceeds the max interations
    while True:
        response: requests.Response = await asyncio.to_thread(make_request)

        # Handles api errors
        try:
            message: dict = response.json()["choices"][0]["message"]
        except (requests.exceptions.JSONDecodeError, KeyError):
            print(response.text)
            raise

        messages.append(message)
        dump_memory()
        response_reasoning: str = message.get("reasoning") or "No Reasoning Provided"

        # Yields model output if it produced content
        if "content" in message and message["content"]:
            response_message = message["content"]
            yield response_message, response_reasoning

        # Runs only if a tool has been called
        if "tool_calls" in message and message["tool_calls"]:
            # To log reasoning before tool call
            logger.info("Reasoning: " + response_reasoning)
            for tool_call in message["tool_calls"]:
                call_id = tool_call["id"]

                # Runs only when model does not exceed the max iterations of tool calls
                if tool_call_count < MAX_CALLS_IN_TOOL_SEQUENCE:
                    tool_output = tools.execute_func(tool_call)
                else:
                    logger.warning("Tool call stack loop limit reached. Returning error strings to model")
                    tool_output = "Tool call stack loop limit reached - tools temporarily disabled for the remaining call chain"

                messages.append({
                    "role": "tool",
                    "tool_call_id": call_id,
                    "content": tool_output
                })
                dump_memory()
                logger.info(f"Called tool [{tool_call['function']['name']}]")
        else:
            return
        tool_call_count += 1


async def reflect() -> None:
    reflection_messages = [{"role": "system", "content": PROMPT}]
    reflection_messages.append({"role": "system", "content": "You are in a reflection loop. Take this opportunity to reflect on what you currently know and understand to extrapolate any useful conclusions. You have access to all your tools, including your diary, so use it if you want to save anything from this context - messages will not persist after reflection ends."})

    get_response(f"[{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] (System) {system_input})")

    with open("data/reflection_messages.json", "w") as f:
        json.dump(messages, f, indent=4)
    load_memory("data/reflection_messages.json")
    
    dump_memory("data/reflection_messages.json")

