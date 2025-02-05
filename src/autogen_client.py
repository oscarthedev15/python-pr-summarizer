from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_core import CancellationToken
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination
from autogen_agentchat.ui import Console

import logging
import os
from github_tools import post_github_comment

class AutogenClient:
    def __init__(self):
        self.client = OpenAIChatCompletionClient(
            api_key=os.getenv("OPENAI_API_KEY"),
            model="gpt-3.5-turbo"
        )

        self.comment_agent = AssistantAgent(
            name="comment_agent",
            model_client=self.client,
            tools=[post_github_comment],
            system_message="You may comment on the code changes. Provide insightful comments on the code changes using analysis on the code changes. Use your tool to post the comments.",
        )

        self.summary_agent = AssistantAgent(
            name="summary_agent",
            model_client=self.client,
            system_message="You may summarize the code changes. Provide a summary of the code changes using analysis on the code changes.",
        )

        max_msg_termination = MaxMessageTermination(max_messages=3)


        # Define a termination condition that stops the task if the critic approves.
        text_termination = TextMentionTermination("APPROVE")

        # Create a team with the primary and critic agents.
        self.team = RoundRobinGroupChat([self.summary_agent, self.comment_agent], termination_condition=max_msg_termination)


    async def create_summary(self, prompt) -> str:
        logging.info(f"Creating summary with prompt: {prompt}")

        response = await self.summary_agent.on_messages(
            [TextMessage(content=prompt, source="user")],
            cancellation_token=CancellationToken(),
        )
        logging.info("+=================")
        logging.info(f"Summary agent response: {response}")
        logging.info("+=================")
        logging.info(response.inner_messages)
        return response.chat_message.content

    async def create_comment(self, prompt) -> str:
        logging.info(f"Creating comment with prompt: {prompt}")

        response = await self.comment_agent.on_messages(
            [TextMessage(content=prompt, source="user")],
            cancellation_token=CancellationToken(),
        )
        logging.info(response.inner_messages)
        return response.chat_message.content
    
    async def team_execution(self, prompt) -> str:
        logging.info(f"Running team execution with prompt: {prompt}")

        await Console(self.team.run_stream(task=prompt))  # Stream the messages to the console.

        return "OK"