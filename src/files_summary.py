import requests
import logging
from openai_client import OpenAIClient
from shared_prompt import SHARED_PROMPT
MAX_FILES_TO_SUMMARIZE = 20

def preprocess_commit_message(commit_message):
    # Implement the preprocessing logic if needed
    return commit_message

def get_openai_summary_for_file(filename, patch):
    try:
        openai_prompt = f"{SHARED_PROMPT}\n\nTHE GIT DIFF OF {filename} TO BE SUMMARIZED:\n```\n{patch}\n```\n\nSUMMARY:\n"
        if len(openai_prompt) > OpenAIClient.MAX_OPEN_AI_QUERY_LENGTH:
            raise ValueError("OpenAI query too big")
        # logging.info(f"Sending prompt to OpenAI: {openai_prompt}")
        response = OpenAIClient.create_completion(openai_prompt)
        if response and response['choices']:
            return response['choices'][0]['text'] or "Error: couldn't generate summary"
    except Exception as error:
        print(error)
    return "Error: couldn't generate summary"

def get_files_summaries(pull_request):
    files_changed = pull_request.get_files()
    result = {}

    for file in files_changed:
        if file.patch:
            summary = get_openai_summary_for_file(file.filename, file.patch)
            result[file.filename] = summary

    return result 