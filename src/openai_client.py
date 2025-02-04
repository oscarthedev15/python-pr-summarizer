from openai import AsyncOpenAI
import os
import logging
class OpenAIClient:
    MAX_OPEN_AI_QUERY_LENGTH = 20000
    MODEL_NAME = "gpt-3.5-turbo"
    TEMPERATURE = 0.5
    MAX_TOKENS = 512

    def __init__(self):
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    async def create_completion(self, prompt):
        logging.info(f"CREATE_COMPLETION: {prompt}")
        response = await self.client.chat.completions.create(
            model=self.MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=self.MAX_TOKENS,
            temperature=self.TEMPERATURE,
            prompt=prompt
        )
        return response.choices[0].message.content 