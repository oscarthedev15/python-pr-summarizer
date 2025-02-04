from github import PullRequest

class PullRequestParser:
    def __init__(self, pull_request: PullRequest):
        self.pull_request = pull_request

    def get_summary(self):
        """Extract a comprehensive summary of the pull request."""
        commit_summaries = self.get_commit_summaries()
        file_summaries = self.get_file_summaries()
        return {
            "commit_summaries": commit_summaries,
            "file_summaries": file_summaries
        }

    def get_commit_summaries(self):
        """Extract commit summaries from the pull request."""
        commit_summaries = []
        commits = self.pull_request.get_commits()

        for commit in commits:
            commit_object = commit.commit
            summary = {
                'sha': commit.sha,
                'message': commit_object.message,
                'author': commit_object.author.name,
                'date': commit_object.author.date.isoformat()
            }
            commit_summaries.append(summary)

        return commit_summaries

    def get_file_summaries(self):
        """Extract the file summaries from the pull request."""
        files_changed = self.pull_request.get_files()
        file_summaries = [
            {
                "filename": file.filename,
                "changes": file.changes,
                "additions": file.additions,
                "deletions": file.deletions,
                "patch": file.patch
            }
            for file in files_changed if file.patch
        ]
        return file_summaries

    def get_diff_contents(self):
        """Extract the diff contents from the pull request."""
        files_changed = self.pull_request.get_files()
        diff_contents = "\n".join(
            f"File: {file.filename}\nDiff:\n{file.patch}" for file in files_changed if file.patch
        )
        return diff_contents 