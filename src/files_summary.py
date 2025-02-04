import logging
from autogen_client import AutogenClient
from shared_prompt import SHARED_PROMPT
MAX_FILES_TO_SUMMARIZE = 20

def preprocess_commit_message(commit_message):
    # Implement the preprocessing logic if needed
    return commit_message

async def get_files_summaries(pull_request):
    try:
        files_changed = pull_request.get_files()
        raw_git_diff = "\n".join(
            f"File: {file.filename}\nDiff:\n{file.patch}" for file in files_changed if file.patch
        )
        autogen_prompt = f"{SHARED_PROMPT}\n\nTHE GIT DIFF TO BE SUMMARIZED:\n```\n{raw_git_diff}\n```\n\nTHE SUMMARY:\n"

        client = AutogenClient()
        summary = await client.create_summary(autogen_prompt)
        return summary
    except Exception as error:
        logging.error(f"Error in generating file summaries: {error}")
        return "Error: couldn't generate file summaries" 