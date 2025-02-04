import openai
import os

class OpenAIClient:
    MAX_OPEN_AI_QUERY_LENGTH = 20000
    MODEL_NAME = "text-davinci-003"
    TEMPERATURE = 0.5
    MAX_TOKENS = 512

    @staticmethod
    def create_completion(prompt):
        openai.api_key = os.getenv("OPENAI_API_KEY")
        return openai.Completion.create(
            model=OpenAIClient.MODEL_NAME,
            prompt=prompt,
            max_tokens=OpenAIClient.MAX_TOKENS,
            temperature=OpenAIClient.TEMPERATURE
        ) 