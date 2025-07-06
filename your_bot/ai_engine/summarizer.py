from together_client import TogetherClient
from prompt_templates import generate_prompt

class NewsSummarizer:
    def __init__(self, api_key: str):
        self.client = TogetherClient(api_key)

    def summarize_news(self, news: str) -> str:
        prompt = generate_prompt(news)
        return self.client.summarize(prompt)
