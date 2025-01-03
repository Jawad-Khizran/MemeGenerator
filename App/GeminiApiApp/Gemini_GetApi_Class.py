import google.generativeai as genai
from textblob import TextBlob
import re
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)


class GetApi:
    def __init__(self):
        # Set API key
        self.api_key = os.environ.get("GOOGLE_API_KEY")
        # print(self.api_key)
        # self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set.")

        # Configure generative AI
        # genai.configure(self.api_key)
        genai.configure(api_key=self.api_key)

        self.model = genai.GenerativeModel("gemini-pro")

    def get_meme(self):
        while True:
            response = self.model.generate_content(
                "Generate a joke about a multicultural holiday"
            # "Generate a holiday blessing for a multicultural celebration(short and to the point, positive/negative)"
            )
            cleaned_text = self.clean_text(response.text)
            blob = TextBlob(cleaned_text)
            sentiment = blob.sentiment.polarity
            logging.info(f"Sentiment score: {sentiment}")

            return cleaned_text, sentiment

            # if sentiment >= 0:
            #     return cleaned_text, sentiment
            # else:
            #     logging.warning("Sentiment score is negative. Regenerating...")

    def clean_text(self, response):
        # Remove special characters but keep punctuation
        text = re.sub(r'[^a-zA-Z0-9.,!?\'\"\s\n]', '', response)
        return text.strip()  # Remove leading/trailing whitespace
