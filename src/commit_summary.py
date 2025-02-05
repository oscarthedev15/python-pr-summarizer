import requests
import logging
from autogen_client import AutogenClient
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
    repo_owner = diff_metadata['repository'].owner.login
    repo_name = diff_metadata['repository'].name
    commit_sha = diff_metadata['commit'].sha

    for file_name in files_list:
        short_name = file_name.split("/")[-1]
        link = f"https://github.com/{repo_owner}/{repo_name}/blob/{commit_sha}/{file_name}"
        summary = summary.replace(f"[{file_name}]", f"[{short_name}]({link})")
    return summary

async def get_autogen_completion(comparison, diff_metadata):
    try:
        raw_git_diff = "\n".join(
            format_git_diff(file.filename, file.patch) for file in comparison.files
        )
        autogen_prompt = f"{SHARED_PROMPT}\n\nTHE GIT DIFF TO BE SUMMARIZED:\n```\n{raw_git_diff}\n```\n\nTHE metadata:\n{diff_metadata}\n"

        client = AutogenClient()
        # completion = await client.create_summary(autogen_prompt)
        completion = await client.team_execution(autogen_prompt)
        return completion
    except Exception as error:
        logging.error(f"Error in Autogen completion: {error}")
        return "Error: couldn't generate summary"

async def summarize_commits(pull_request):
    commit_summaries = []

    commits = pull_request.get_commits()
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
            completion = await get_autogen_completion(comparison, {
                'sha': commit.sha,
                'repository': repo,
                'commit': commit_object,
                'pull_request_number': pull_request.number
            })


    return commit_summaries 