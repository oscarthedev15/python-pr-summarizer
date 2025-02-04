import os
import logging
import asyncio
from github import Github
from commit_summary import summarize_commits

# Configure logging
logging.basicConfig(level=logging.INFO)

async def run():
    logging.info("Starting the summarizer")

    # Get the GitHub token and initialize the GitHub client
    github_token = os.getenv("GITHUB_TOKEN")
    g = Github(github_token)

    # Get the repository and pull request number from the environment variables
    repo_name = os.getenv("GITHUB_REPOSITORY")
    pull_request_number = int(os.getenv("PULL_REQUEST_NUMBER"))

    logging.info(f"Repository: {repo_name}, Pull Request: {pull_request_number}")

    repo = g.get_repo(repo_name)
    pull_request = repo.get_pull(pull_request_number)

    # Summarize the commits
    await summarize_commits(pull_request)

    logging.info("Summarization complete")

if __name__ == "__main__":
    asyncio.run(run()) 