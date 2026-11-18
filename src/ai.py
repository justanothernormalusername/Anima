from dotenv import load_dotenv
from collections.abc import AsyncGenerator
from datetime import datetime
import requests
import os
import asyncio
import tools
import logging
import memory

logger = logging.getLogger(__name__)

load_dotenv()
API_KEY = os.getenv("HACKCLUBAI_API_KEY")
URL = "https://ai.hackclub.com/proxy/v1/chat/completions"


MODEL = "anthropic/claude-sonnet-5.5"
MODEL = "openai/gpt-6-luna"
MODEL = "minimax/minimax-m2-her"

MODEL = "deepseek/deepseek-v4.1-flash-1017:nitro"

MAX_CALLS_IN_TOOL_SEQUENCE = 20


def make_request(messages: list) -> requests.models.Response:
    return requests.post(
        url = URL,
        headers = {"Authorization": f"Bearer {API_KEY}"},
        json = {
            "model": MODEL,
            "messages": messages,
            "tools": tools.tools
        }
    )


async def get_response(messages: list, user_input: str) -> AsyncGenerator[tuple[str, str]]:
    # print(messages)
    messages.append({"role": "user", "content": user_input})
    tool_call_count = 0

    # Loops until model finishes tool calling chain or it exceeds the max interations
    while True:
        response: requests.Response = await asyncio.to_thread(make_request, messages)

        # Handles api errors
        try:
            message: dict = response.json()["choices"][0]["message"]
        except (requests.exceptions.JSONDecodeError, KeyError):
            print(response.text)
            raise

        messages.append(message)
        memory.dump_memory()
        response_reasoning: str = message.get("reasoning") or "No Reasoning Provided"

        # Yields model output if it produced content
        if "content" in message and message["content"]:
            response_message = message["content"]
            yield response_message, response_reasoning

        # Runs only if a tool has been called
        if "tool_calls" in message and message["tool_calls"]:
            # To log reasoning before tool call
            logger.debug("Reasoning: " + response_reasoning)
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
                memory.dump_memory()
                logger.info(f"Called tool [{tool_call['function']['name']}]")
        else:
            return
        tool_call_count += 1

