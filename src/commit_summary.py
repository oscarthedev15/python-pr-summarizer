import requests
import logging
from openai_client import OpenAIClient
from shared_prompt import SHARED_PROMPT

MAX_COMMITS_TO_SUMMARIZE = 20

# Configure logging
logging.basicConfig(level=logging.INFO)

def format_git_diff(filename, patch):
    result = [f"--- a/{filename}", f"+++ b/{filename}"]
    result.extend(patch.split("\n"))
    result.append("")
    return "\n".join(result)

def postprocess_summary(files_list, summary, diff_metadata):
    for file_name in files_list:
        short_name = file_name.split("/")[-1]
        link = f"https://github.com/{diff_metadata['repository']['owner']['login']}/{diff_metadata['repository']['name']}/blob/{diff_metadata['commit']['data']['sha']}/{file_name}"
        summary = summary.replace(f"[{file_name}]", f"[{short_name}]({link})")
    return summary

async def get_openai_completion(comparison, diff_metadata):
    try:
        raw_git_diff = "\n".join(
            format_git_diff(file.filename, file.patch) for file in comparison.files
        )
        openai_prompt = f"{SHARED_PROMPT}\n\nTHE GIT DIFF TO BE SUMMARIZED:\n```\n{raw_git_diff}\n```\n\nTHE SUMMARY:\n"

        if len(openai_prompt) > OpenAIClient.MAX_OPEN_AI_QUERY_LENGTH:
            raise ValueError("OpenAI query too big")

        client = OpenAIClient()
        # logging.info(f"Sending prompt to OpenAI: {openai_prompt}")
        completion = await client.create_completion(openai_prompt)
        return postprocess_summary(
            [file.filename for file in comparison.files],
            completion,
            diff_metadata
        )
    except Exception as error:
        logging.error(f"Error in OpenAI completion: {error}")
        return "Error: couldn't generate summary"

async def summarize_commits(pull_request, modified_files_summaries):
    commit_summaries = []

    commits = pull_request.get_commits()
    head_commit = pull_request.head.sha
    repo = pull_request.base.repo

    for commit in commits:
        existing_comment = next((comment for comment in pull_request.get_issue_comments() if comment.body.startswith(f"GPT summary of {commit.sha}:")), None)

        if existing_comment:
            commit_summaries.append((commit.sha, existing_comment.body))
            continue

        commit_object = commit.commit
        parent = commit_object.parents[0].sha if commit_object.parents else None

        if parent:
            comparison = repo.compare(parent, commit.sha)
            logging.info(f"Comparing commits: {parent}..{commit.sha}")
            completion = await get_openai_completion(comparison, {
                'sha': commit.sha,
                'repository': repo,
                'commit': commit_object
            })
            commit_summaries.append((commit.sha, completion))

            logging.info(f"Posting comment for commit {commit.sha}")
            pull_request.create_issue_comment(f"GPT summary of {commit.sha}:\n\n{completion}")

    return commit_summaries 