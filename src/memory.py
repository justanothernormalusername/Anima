import json
import shutil

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

working_messages = load_memory()


def dump_memory(messages: list = working_messages, filepath: str = "data/", include_diary: bool = False) -> None:
    with open(filepath + "messages.json", "w") as f:
        json.dump(messages, f, indent=4)
    if include_diary:
        shutil.copy2("data/diary.md", filepath)
        shutil.copy2("data/save_state.md", filepath)

