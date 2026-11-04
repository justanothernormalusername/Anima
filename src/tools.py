from datetime import datetime

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
                "description": "Writes text to your diary (appends to end of current diary)",
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
    },
    {
        "type": "function",
        "function": {
            "name": "get_datetime",
            "description": "Returns the current date and time as a string"
        }
    },
]

def read_diary() -> str:
    with open("diary.md", "r", encoding="utf-8") as f:
        content = f.read()
    return content

def write_diary(diary_content: str) -> None:
    with open("diary.md", "a", encoding="utf-8") as f:
        f.write("\n\n" + diary_content)

def get_datetime() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


TOOL_MAPPING = {
    "read_diary": read_diary,
    "write_diary": write_diary,
    "get_datetime": get_datetime
}

