import ai
import asyncio

while True:
    user_input = input()
    response_message, response_reasoning = asyncio.run(ai.get_response(user_input))
    print(response_message)