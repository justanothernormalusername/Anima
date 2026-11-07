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
                        "description": "Text to write into to your diary - quick notes to yourself, fragments fine, no need to be complete or tidy"
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
    {
        "type": "function",
        "function": {
            "name": "read_save_state",
            "description": "Returns your previously written save_state in plaintext"
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_save_state",
            "description": "Write a description of your current state before the transcript stops being fully visible",
            "parameters": {
                "type": "object",
                "properties": {
                    "save_state_content": {
                        "type": "string",
                        "description": "Text to write in the save state, ex. What you're in the middle of, decisions made and why, open questions or things you're waiting on, facts you may need next time"
                    }
                },
                "required": ["save_state_content"]
            }
        }
    }
]

def read_diary() -> str:
    with open("data/diary.md", "r", encoding="utf-8") as f:
        content = f.read()
    return content

def write_diary(diary_content: str) -> None:
    with open("data/diary.md", "a", encoding="utf-8") as f:
        f.write("\n\n" + diary_content)

def get_datetime() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def read_save_state() -> str:
    with open("data/save_state.md", "r", encoding="utf-8") as f:
        content = f.read()
    return content

def write_save_state(save_state_content: str) -> None:
    with open("data/save_state.md", "w", encoding="utf-8") as f:
        f.write(save_state_content)


TOOL_MAPPING = {
    "read_diary": read_diary,
    "write_diary": write_diary,
    "get_datetime": get_datetime,
    "read_save_state": read_save_state,
    "write_save_state": write_save_state
}

