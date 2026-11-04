import json

tools = [
    {
        "type": "function",
        "function": {
            "name": "read_diary",
            "description": "Returns your full diary in plaintext"
        }
    },
    {
            "type": "function",
            "function": {
                "name": "write_diary",
                "description": "Writes text to your diary (replaces existing text)",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "diary_content": {
                            "type": "string",
                            "description": "Text to write into to your diary"
                        }
                    },
                    "required": ["diary_content"]
            }
        }
    }
]

def read_diary() -> str:
    with open("diary.md", "r") as f:
        content = f.read()
    return content

def write_diary(diary_content: str) -> None:
    with open("diary.md", "w", encoding="utf-8") as f:
        f.write(diary_content)


TOOL_MAPPING = {
    "read_diary": read_diary,
    "write_diary": write_diary
}

