from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_core import CancellationToken
from autogen_ext.models.openai import OpenAIChatCompletionClient
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
            tools=[],
            system_message="You may summarize the code changes. Provide a summary of the code changes using analysis on the code changes.",
        )

    async def create_summary(self, prompt) -> str:
        response = await self.summary_agent.on_messages(
            [TextMessage(content=prompt, source="user")],
            cancellation_token=CancellationToken(),
        )
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