from typing import Any, Dict
from autogpt.commands.command import command
from autogpt.config import Config

CFG = Config()

@command(
    "local_gpt",
    "Local GPT",
    '"name": "agent_name_here", "task": "agent_task_here", "local_prompt": "message to the local agent"',
    )
def local_gpt(name: str, task: str, local_prompt: str) -> Dict[str, Any]:
    from .gpt_agent import main as gpt_agent_main
    result = gpt_agent_main(name, task, local_prompt)
    
    return {"message": result}

