import google.generativeai as genai
import base64
import json
import os

class VisionAgent:
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_API_KEY")
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel("gemini-1.5-flash")

    def analyze_image(self, image_path: str):
        """Returns UI elements extracted from a screenshot."""
        with open(image_path, "rb") as f:
            image_data = f.read()

        encoded = base64.b64encode(image_data).decode()

        prompt = """
        You are an expert UI analyst.
        Extract UI components from this mobile/web screen.
        Return JSON ONLY with fields:
        - screen_name
        - elements: [{type, label, xpath_or_identifier}]
        - interactions
        - validations
        """

        response = self.model.generate_content(
            contents=[
                prompt,
                {"mime_type": "image/png", "data": image_data}
            ]
        )

        try:
            return json.loads(response.text)
        except:
            return {"screen_name": "unknown", "elements": [], "interactions": [], "validations": []}