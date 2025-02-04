import logging
import os
import asyncio
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import SelectorGroupChat
from autogen_agentchat.conditions import TextMentionTermination
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_agentchat.ui import Console
from autogen_agentchat.messages import ChatMessage

from shared_prompt import (
    SHARED_PROMPT,
    GRAMMAR_AGENT_PROMPT,
    CODE_QUALITY_AGENT_PROMPT,
    COMMENTER_AGENT_PROMPT
)
from github_tools import post_github_comment
from github import Github

# Create an OpenAI model client.
model_client = OpenAIChatCompletionClient(
    model="gpt-4o-2024-08-06",
    api_key=os.getenv("OPENAI_API_KEY")
)

class AgentTeam:
    def __init__(self):
        # Create agents with specific roles
        self.grammar_agent = AssistantAgent(
            "grammar_agent",
            description="A grammar expert agent.",
            model_client=model_client,
            system_message=SHARED_PROMPT + GRAMMAR_AGENT_PROMPT
        )
        
        self.code_quality_agent = AssistantAgent(
            "code_quality_agent",
            description="A code quality expert agent.",
            model_client=model_client,
            system_message=SHARED_PROMPT + CODE_QUALITY_AGENT_PROMPT
        )
        
        self.commenter_agent = AssistantAgent(
            "commenter_agent",
            description="An agent for commenting on code changes.",
            model_client=model_client,
            tools=[post_github_comment],
            system_message=SHARED_PROMPT + COMMENTER_AGENT_PROMPT
        )
        
        # Define a termination condition
        self.termination_condition = TextMentionTermination("APPROVE")
        
        # Create a team with the agents
        self.team = SelectorGroupChat(
            [self.grammar_agent, self.code_quality_agent, self.commenter_agent],
            model_client=model_client,
            termination_condition=self.termination_condition
        )

    async def review_pull_request(self, commit_data):
        logging.info("Starting agent team review of the pull request.")
        
        # Extract necessary data from commit_data
        comparison = commit_data['comparison']
        sha = commit_data['sha']
        repo = commit_data['repository']
        commit_object = commit_data['commit']
        
        # Create a task description from the commit data
        task_description = f"""
            commit_sha: {sha}
            commit_message: {commit_object.message}
            repo: {repo}
            comparison: {comparison}
        """

        logging.info(f"Type of task_description: {type(task_description)}")
        
        logging.info(f"Serialized task: {task_description}\n\n\n\n\n")
        
        try:
            # Run the team with the task and stream the messages to the console
            await Console(self.team.run_stream(task=task_description))
        except Exception as e:
            logging.error(f"Error during agent team execution: {e}")
        
        logging.info("Agent team review completed.")