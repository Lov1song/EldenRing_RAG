import requests
import json

class OllamaClient:
    def __init__(self,model_name="qwen:4b"):
        self.model = model_name
        self.url = f"http://localhost:11434/api/generate"

    def generate(self,prompt,max_tokens=512,temperature=0.7):
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "max_tokens":max_tokens,
            "stop":["\n\n"]
        }
        resp = requests.post(self.url,json=payload)
        resp.raise_for_status()
        result = resp.json()

        return result['response']