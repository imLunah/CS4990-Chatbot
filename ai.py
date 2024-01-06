import os
import json

import google.generativeai as genai


class Gemini:
    def __init__(self) -> None:
        api_key = os.environ["GOOGLE_API_KEY"]
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-pro")

    def chat(self, message: str):
        with open('gemini_safety_settings.json') as f:
            safety_settings = json.load(f)

        return self.model.generate_content(
            message,
            stream=True,
            safety_settings=safety_settings,
        )
