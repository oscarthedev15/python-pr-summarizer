import os
from github import Github
from commit_summary import summarize_commits
from files_summary import get_files_summaries

def run():
    # Get the GitHub token and initialize the GitHub client
    github_token = os.getenv("GITHUB_TOKEN")
    g = Github(github_token)

    # Get the repository and pull request number from the environment variables
    repo_name = os.getenv("GITHUB_REPOSITORY")
    pull_request_number = int(os.getenv("PULL_REQUEST_NUMBER"))

    repo = g.get_repo(repo_name)
    pull_request = repo.get_pull(pull_request_number)

    # Get the modified files summaries
    modified_files_summaries = get_files_summaries(pull_request)

    # Summarize the commits
    summarize_commits(pull_request, modified_files_summaries)

if __name__ == "__main__":
    run() 