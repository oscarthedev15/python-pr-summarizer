from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_core import CancellationToken
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination
from autogen_agentchat.ui import Console
from shared_prompt import SHARED_PROMPT
import logging
import os
from github_tools import post_github_comment, post_github_line_comment

class AutogenClient:
    def __init__(self):
        self.client = OpenAIChatCompletionClient(
            api_key=os.getenv("OPENAI_API_KEY"),
            model="gpt-3.5-turbo"
        )

        # self.comment_agent = AssistantAgent(
        #     name="comment_agent",
        #     model_client=self.client,
        #     tools=[post_github_comment],
        #     system_message="You may comment on the code changes. Provide insightful comments on the code changes using analysis on the code changes. Use your tool to post the comments to github every time you have a new comment.",
        # )

        self.summary_agent = AssistantAgent(
            name="summary_agent",
            model_client=self.client,
            tools=[post_github_comment],
            system_message=SHARED_PROMPT + "You should summarize the code changes. Provide a summary of the code changes using analysis on the code changes.   Use your tool to post the summary to github.  Maintain the file name in the summary.",
        )

        self.grammar_agent = AssistantAgent(
            name="grammar_agent",
            model_client=self.client,
            tools=[post_github_line_comment],
            system_message=SHARED_PROMPT + "You are a grammar expert. Review the code changes for grammatical errors and suggest corrections. Use your tool to post comments on specific lines of the code in specific files.  Do not use the tool if there are no grammatical  in the diff.",
        )

        self.style_agent = AssistantAgent(
            name="style_agent",
            model_client=self.client,
            tools=[post_github_line_comment],
            system_message=SHARED_PROMPT + "You are a code style expert. Review the code changes for style issues and suggest improvements. Use your tool to post comments on specific lines of the code.  Do not use the tool if there are no style issues.",
        )

        self.variable_agent = AssistantAgent(
            name="variable_agent",
            model_client=self.client,
            tools=[post_github_line_comment],
            system_message=SHARED_PROMPT + "You are a variable naming expert. Review the code changes for variable naming issues and suggest improvements. Use your tool to post comments on specific lines.  Do not use the tool if there are no variable naming issues.",
        )

        max_msg_termination = MaxMessageTermination(max_messages=8)

        # Define a termination condition that stops the task if the critic approves. WIP do not understand how to stop the task
        # text_termination = TextMentionTermination("APPROVE")

        # Create a team with the primary and critic agents.
        self.team = RoundRobinGroupChat(
            [self.summary_agent, 
            #  self.comment_agent,
             self.grammar_agent, 
             self.style_agent, 
             self.variable_agent],
            termination_condition=max_msg_termination
        )

    async def create_summary(self, prompt) -> str:
        logging.info(f"Creating summary with prompt: {prompt}")

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
    
    async def team_execution(self, prompt) -> str:
        logging.info(f"Running team execution with prompt: {prompt}")

        await Console(self.team.run_stream(task=prompt))  # Stream the messages to the console.

        return "OK"