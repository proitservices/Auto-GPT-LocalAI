import json
import os
import re
import time
import multiprocessing
import threading
from typing import Any, Dict, List
from urllib import request, parse
from autogpt.commands.command import command
from autogpt.config import Config

CFG = Config()
processing_status = {}
current_chunk = 0
total_chunks = 0
chunk_responses = {}


def call_local_gpt_api(name, task, prompt):
    url = "http://localhost:8080/v1/completions"
    headers = {"Content-Type": "application/json"}
    data = {
        "model": "ggml-gpt4all-j.bin",
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
    "local_gpt",
    "Local GPT",
    '"name": "agent_name_here", "task": "agent_task_here", "local_prompt": "message to the local agent"',
)
def local_gpt(name: str, task: str, local_prompt: str) -> Dict[str, Any]:
    try:
        result = call_local_gpt_api(name, task, local_prompt)
    except Exception as e:
        result = {"message": f"Error: {str(e)}"}
    return result

def split_content_into_chunks(content: str, word_count: int) -> List[str]:
    words = content.split()
    return [
        " ".join(words[i:i + word_count])
        for i in range(0, len(words), word_count)
    ]

def process_single_chunk(index: int, chunk: str, message: str, word_count: int,chunk_responses: Dict[int, Dict[str, Any]] ):
    #global chunk_responses
    try:
        name='task'
        response = call_local_gpt_api(name,chunk,message)
        chunk_responses[index] = response
        #print(f"Processed chunk {index}")  #outputs to terminal while processing check procesm

    except Exception as e:
        print(f"Error processing chunk {index}: {str(e)}")

def process_file(file: str, local_prompt: str, word_count: int):
    #global total_chunks, current_chunk
    chunk_responses = {}
    
    if file not in processing_status:
        processing_status[file] = {"status":"started", "responses": {},"total_chunks": 0}
        with open(file, "r") as f:
            content = f.read()

        chunks = split_content_into_chunks(content, word_count)
        total_chunks = len(chunks)

        for index, chunk in enumerate(chunks):
            process_single_chunk(index, chunk, local_prompt, word_count,chunk_responses)
            time.sleep(2)
            #print(f"processing {chunk}/{total_chunks}")
            processing_status[file] = {
                "status": "processing", 
                "responses": chunk_responses, 
                "total_chunks": total_chunks}

        processing_status[file] = {
                "status": "complete",
                "responses": chunk_responses,
                "total_chunks": total_chunks}

@command(
    "local_gpt_file_read",
    "Local GPT File Read",
    '"file": "path_to_the_file", "local_prompt": "message to the local agent"',
)
def local_gpt_file_read(file: str, local_prompt: str) -> Dict[str, Any]:
    global current_chunk, total_chunks, chunk_responses

    if not os.path.exists(file):
            return {"message": f"Error: File '{file}' does not exist"}
    if file not in processing_status:
        word_count = 300

        #starts a new thread with file processing
        thread = threading.Thread(target=process_file, args=(file, local_prompt, word_count))
        thread.start()

        return {"message": "Started processing the file, please check back in 10 minutes."}
    else: 
        return {"message": f" {file} processing, check get_processing_status for more information."}

@command(
    "get_processing_status",
    "Get Processing Status",
    '"file": "path_to_the_file"',
)
def get_processing_status(file: str) -> Dict[str, Any]:
    #global current_chunk, total_chunks

    if file in processing_status:
        file_data = processing_status[file]
        return {
            "filename": file,
            "status" : file_data["status"],
            "current_chunk": len(file_data["responses"]),
            "total_chunks": file_data["total_chunks"],
        }
    else:
        return {"filename": "Nothing is processing now"}

@command(
    "local_gpt_return",
    "Local GPT Return",
    '"file": "path_to_the_file", "key": "chunk_number"',
)
def local_gpt_return(file: str, key: int) -> Dict[str, Any]:
    if file in processing_status:
        if key in processing_status[file]["responses"]:
            result = {"filename": file, "key": key}
            result.update(processing_status[file]["responses"][key])
            return result
        else:
            return {"message": f"Chunk {key} not found for file {file}"}
    else:
        return {"message": f"No data found for file {file}"}

