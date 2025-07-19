import os
from openai import OpenAI
from utils.logger import logger
from utils.read_write import read_text_file, write_json_file
import re
import json
from config import Config

class AIInterpreter:
    def __init__(self):
        self.openai_api_key = Config.TOKENS.OPENAI
        if not self.openai_api_key:
            logger.error("OpenAI API key not found in environment variables")
        
    def _clean_json_response(self, raw_response: str) -> str:
        # Try to find JSON inside ```json ... ``` or ``` ... ```
        code_fence_match = re.search(r"```(?:json)?\s*(\{.*?\}|\[.*?\])\s*```", raw_response, re.DOTALL)
        if code_fence_match:
            json_str = code_fence_match.group(1)
        else:
            # Fallback: try to find a lone JSON object or array in the whole text
            json_match = re.search(r"(\{.*\}|\[.*\])", raw_response, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                raise ValueError("No JSON found!")

        # Final cleanup: strip leading/trailing whitespace
        json_str = json_str.strip()

        # Validate it
        try:
            parsed = json.loads(json_str)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON: {e}")

        return parsed
                
    def get_interpretation(self, prompt: str) -> str:
        """Get interpretation from ChatGPT for a batch of messages"""

        client = OpenAI(
            api_key=self.openai_api_key,
        )

        response = client.responses.create(
            model="gpt-4o",
            instructions="You are a helpful assistant.",
            max_output_tokens=10000,
            input=prompt,
        )
        return response.output_text
    

    def get_json_response(self, prompt: str) -> str:
        """Get JSON response from ChatGPT"""
        response = self.get_interpretation(prompt)
        return self._clean_json_response(response)
    





if __name__ == "__main__":
    ai_interpreter = AIInterpreter()
    messages = """
    message 1: this morning the US CPI data was released and it was higher than expected.
    message 2: the US Fed is expected to raise interest rates by 0.25% next week.
    message 3: the US unemployment rate is expected to remain at 3.7%.
    message 4: the US GDP is expected to grow by 2.5% next year.
    message 5: the US inflation rate is expected to remain at 2.5% next year.
    message 6: the US unemployment rate is expected to remain at 3.7%.
    message 7: the US GDP is expected to grow by 2.5% next year.
    message 8: the US inflation rate is expected to remain at 2.5% next year.
"""
    

    news_summary_prompt = read_text_file("ai_tools/prompts/news_summary_hebrew.txt") + messages
    response = ai_interpreter.get_json_response(news_summary_prompt)
    write_json_file("news_pdf/news_data.json", response)