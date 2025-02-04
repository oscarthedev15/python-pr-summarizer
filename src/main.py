# import os
# import logging
# import asyncio
# from github import Github
# from agent_team import AgentTeam
# from pull_request_parser import PullRequestParser

# # Configure logging
# logging.basicConfig(level=logging.INFO)

# async def run():
#     # Get the GitHub token and initialize the GitHub client
#     github_token = os.getenv("GITHUB_TOKEN")
#     g = Github(github_token)

#     # Get the repository and pull request number from the environment variables
#     repo_name = os.getenv("GITHUB_REPOSITORY")
#     pull_request_number = int(os.getenv("PULL_REQUEST_NUMBER"))

#     repo = g.get_repo(repo_name)
#     pull_request = repo.get_pull(pull_request_number)

#     # Parse the pull request
#     parser = PullRequestParser(pull_request)
#     pull_request_summary = parser.get_summary()

#     # Initialize and run the agent team
#     agent_team = AgentTeam()
#     await agent_team.review_pull_request(pull_request_summary)

#     logging.info("Summarization and agent review complete")

# if __name__ == "__main__":
#     asyncio.run(run()) 


import os
import logging
import asyncio
from github import Github
from commit_summary import summarize_commits
from files_summary import get_files_summaries
from agent_team import AgentTeam

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

    # Get the modified files summaries
    modified_files_summaries = get_files_summaries(pull_request)
    agent_team = AgentTeam()

    # Summarize the commits
    await summarize_commits(pull_request, modified_files_summaries, agent_team)

    logging.info("Summarization complete")

if __name__ == "__main__":
    asyncio.run(run()) 