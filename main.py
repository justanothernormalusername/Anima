from dotenv import load_dotenv
import requests
import os


load_dotenv()
API_KEY = os.getenv("HACKCLUBAI_API_KEY")
URL = "https://ai.hackclub.com/proxy/v1/chat/completions"

model = "z-ai/glm-5.2"
prompt = ""

messages = []

def make_request() -> requests.models.Response:
    return requests.post(
        url = URL,
        headers = {"Authorization": f"Bearer {API_KEY}"},
        json = {
            "model": model,
            "messages": messages
        }
    )

while True:
    new_message = input()
    messages.append({"role": "user", "content": new_message})

    response = make_request()
    print(response.text)
    response_message = response.json()["choices"][0]["message"]["content"]
    print(response_message)

    messages.append(response_message)

