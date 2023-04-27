import json
from typing import Any, Dict
from urllib import request, parse
from autogpt.commands.command import command
from autogpt.config import Config

CFG = Config()

def call_local_gpt_api(name, task, prompt):
    url = "http://localhost:8080/v1/completions"
    headers = {"Content-Type": "application/json"}
    data = {
        "model": "ggml-vicuna-13b-4bit-rev1.bin",
        "task": task,
        "prompt": prompt,
        "temperature": 0.7
    }
    data = json.dumps(data).encode("utf-8")

    req = request.Request(url, headers=headers, data=data)
    with request.urlopen(req) as response:
        response_text = response.read().decode("utf-8")
        reply = json.loads(response_text)
        choices = reply.get("choices", [])
        result = {"message": choices[0]["text"] if choices else ""}
    return result

@command(
    "vicuna_gpt",
    "Vicuna GPT",
    '"name": "agent_name_here", "task": "agent_task_here", "local_prompt": "message to the local agent"',
)
def vicuna_gpt(name: str, task: str, local_prompt: str) -> Dict[str, Any]:
    try:
        result = call_local_gpt_api(name, task, local_prompt)
    except Exception as e:
        result = {"message": f"Error: {str(e)}"}
    return result
