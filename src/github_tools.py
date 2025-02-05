import os
import logging
from github import Github

async def post_github_comment(repo_name: str, pull_request_number: int, comment_body: str) -> str:
    """Post a comment on a GitHub pull request."""
    try:
        github_token = os.getenv("GITHUB_TOKEN")
        g = Github(github_token)

        repo = g.get_repo(repo_name)
        pull_request = repo.get_pull(pull_request_number)

        pull_request.create_issue_comment(comment_body)
        logging.info("Comment posted successfully.")
        return "Comment posted successfully."
    except Exception as e:
        logging.error(f"Failed to post comment: {str(e)}")
        return f"Failed to post comment: {str(e)}"

async def post_github_line_comment(repo_name: str, pull_request_number: int, file_path: str, line_number: int, comment_body: str) -> str:
    """Post a comment on a specific line of a file in a GitHub pull request."""
    try:
        github_token = os.getenv("GITHUB_TOKEN")
        g = Github(github_token)

        repo = g.get_repo(repo_name)
        pull_request = repo.get_pull(pull_request_number)

        # Find the file in the pull request
        for file in pull_request.get_files():
            if file.filename == file_path:
                # Calculate the correct position in the diff
                position = calculate_diff_position(file.patch, line_number)

                if position is None:
                    return f"Line {line_number} not found in the diff for {file_path}."

                # Create a comment on the specific line
                pull_request.create_review_comment(
                    body=comment_body,
                    commit_id=pull_request.head.sha,
                    path=file_path,
                    position=position
                )
                logging.info(f"Comment posted on {file_path} at line {line_number}.")
                return "Comment posted successfully."
        return "File not found in pull request."
    except Exception as e:
        logging.error(f"Failed to post line comment: {str(e)}")
        return f"Failed to post line comment: {str(e)}"

def calculate_diff_position(patch: str, line_number: int) -> int:
    """
    Calculate the position of a line in the diff.
    The position is the line number in the diff where the comment should be placed.
    """
    lines = patch.splitlines()
    position = 0

    for line in lines:
        if line.startswith("@@"):
            # Parse the diff hunk header to get the line ranges
            hunk_header = line
            parts = hunk_header.split(" ")
            old_range = parts[1][1:].split(",")
            new_range = parts[2][1:].split(",")

            old_start = int(old_range[0])
            new_start = int(new_range[0])

            # Reset position for each hunk
            position = 0
        elif line.startswith("+") or line.startswith("-"):
            position += 1
        elif line.startswith(" "):
            position += 1

        # Check if the current line matches the target line number
        if line.startswith("+") and new_start + position - 1 == line_number:
            return position

    return None