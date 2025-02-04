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

        self.agent = AssistantAgent(
            name="assistant",
            model_client=self.client,
            tools=[post_github_comment],
            system_message="You may comment on the code changes. Provide insightful comments on the code changes using analysis on the code changes. Use your tool to post the comments.",
        )

    async def create_completion(self, prompt) -> None:
        response = await self.agent.on_messages(
            [TextMessage(content=prompt, source="user")],
            cancellation_token=CancellationToken(),
        )
        logging.info(response.inner_messages)
        logging.info(response.chat_message)