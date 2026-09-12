from dotenv import load_dotenv
import requests
import os
import json


load_dotenv()
API_KEY = os.getenv("HACKCLUBAI_API_KEY")
URL = "https://ai.hackclub.com/proxy/v1/chat/completions"

model = "deepseek/deepseek-v4.1-flash"
prompt = ""

with open("messages.json", "r") as f:
    messages = json.load(f)

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
    # print(response.text)
    response_message = response.json()["choices"][0]["message"]["content"]
    response_reasoning = response.json()["choices"][0]["message"]["reasoning"]
    print(response_reasoning)
    print(response_message)

    messages.append({"role": "assistant", "content": response_message})

    with open("messages.json", "w") as f:
        json.dump(messages, f, indent=4)

response_format = {
   "id": "gen-1789175134-5Wx3x2e9TjEgQK1bkwxy",
  "object": "chat.completion",
  "created": 1789175134,
  "model": "z-ai/glm-5.2",
  "provider": "Mistral",
  "system_fingerprint": null,
  "service_tier": null,
  "choices": [
    {
      "index": 0,
      "logprobs": null,
      "finish_reason": "stop",
      "native_finish_reason": "stop",
      "message": {
        "role": "assistant",
        "content": "Just saying hello! Is there something I can help you with today, or just testing things out?",
        "refusal": null,
        "reasoning": "1.  **Analyze the user's input:** The user said \"wat\" (a colloquial/typo version of \"what\").\n2.  **Context:** The user previously said \"helo\" (typo for \"hello\"), I responded with a standard greeting, and now they are responding with \"wat\" which indicates confusion, testing the bot, or just playing around.\n3.  **Determine the appropriate response:**\n    *   Acknowledge the informal nature of the input (\"wat\").\n    *   Keep it light, friendly, and helpful.\n    *   Ask if they need assistance or if they are just testing the waters.\n4.  **Drafting responses:**\n    *   *Option 1:* \"Did I say something confusing? Let me know if you have any questions!\"\n    *   *Option 2:* \"Haha, I'm an AI assistant. Did you need help with something specific, or just saying hi?\"\n    *   *Option 3:* \"Just greeting you! What's on your mind?\"\n5.  **Selecting the best fit:** Option 2 or 3 is good. Let's go with a simple, slightly playful clarification. \"I was just saying hello! Did you have a question or need help with something?\"\n6.  **Final Polish:** \"Just saying hello! Is there something I can help you with, or were you just testing things out?\"",
        "reasoning_details": [
          {
            "type": "reasoning.text",
            "text": "1.  **Analyze the user's input:** The user said \"wat\" (a colloquial/typo version of \"what\").\n2.  **Context:** The user previously said \"helo\" (typo for \"hello\"), I responded with a standard greeting, and now they are responding with \"wat\" which indicates confusion, testing the bot, or just playing around.\n3.  **Determine the appropriate response:**\n    *   Acknowledge the informal nature of the input (\"wat\").\n    *   Keep it light, friendly, and helpful.\n    *   Ask if they need assistance or if they are just testing the waters.\n4.  **Drafting responses:**\n    *   *Option 1:* \"Did I say something confusing? Let me know if you have any questions!\"\n    *   *Option 2:* \"Haha, I'm an AI assistant. Did you need help with something specific, or just saying hi?\"\n    *   *Option 3:* \"Just greeting you! What's on your mind?\"\n5.  **Selecting the best fit:** Option 2 or 3 is good. Let's go with a simple, slightly playful clarification. \"I was just saying hello! Did you have a question or need help with something?\"\n6.  **Final Polish:** \"Just saying hello! Is there something I can help you with, or were you just testing things out?\"",
            "format": "unknown",
            "index": 0
          }
        ]
      }
    }
  ],
  "usage": {
    "prompt_tokens": 25,
    "completion_tokens": 316,
    "total_tokens": 341,
    "cost": 0.0014254,
    "is_byok": false,
    "prompt_tokens_details": {
      "cached_tokens": 0,
      "cache_write_tokens": 0,
      "audio_tokens": 0,
      "video_tokens": 0
    },
    "cost_details": {
      "upstream_inference_cost": 0.0014254,
      "upstream_inference_prompt_cost": 0.000035,
      "upstream_inference_completions_cost": 0.0013904
    },
    "completion_tokens_details": {
      "reasoning_tokens": 288,
      "image_tokens": 0,
      "audio_tokens": 0
    }
  }
}