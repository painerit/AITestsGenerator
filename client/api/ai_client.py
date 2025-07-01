import requests
from config import Config

class AIClient:
    def __init__(self):
        self.config = Config()
        self.headers = {
            'Authorization': f'Bearer {self.config.AI_API_KEY}',
            'Content-Type': 'application/json'
        }
        self.base_payload = {
            "model": self.config.MODEL,
            "messages": [{"role": "user", "content": ""}]
        }

    def send_request(self, prompt):
        try:
            self.base_payload["messages"][0]["content"] = prompt
            response = requests.post(
                self.config.AI_API_URL,
                json=self.base_payload,
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            raise RuntimeError(f"AI API Error: {str(e)}")