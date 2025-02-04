import os
import logging
from github import Github

async def post_github_comment(repo_name: str, pull_request_number: int, comment_body: str) -> str:
    """Post a comment on a GitHub pull request."""
    try:
        logging.info("_+_________++++++++++++++++++++++++++++++++++\n\n\n")
        logging.info(f"Attempting to post comment to PR #{pull_request_number} in repo {repo_name}.")
        logging.info(f"Comment Body: {comment_body}")
        logging.info("_+_________++++++++++++++++++++++++++++++++++\n\n\n")
        # Get the GitHub token and initialize the GitHub client
        github_token = os.getenv("GITHUB_TOKEN")
        g = Github(github_token)

        # Get the repository and pull request
        repo = g.get_repo(repo_name)
        pull_request = repo.get_pull(pull_request_number)

        # Create the comment
        pull_request.create_issue_comment(comment_body)
        logging.info("Comment posted successfully.")
        return "Comment posted successfully."
    except Exception as e:
        logging.error(f"Failed to post comment: {str(e)}")
        return f"Failed to post comment: {str(e)}"