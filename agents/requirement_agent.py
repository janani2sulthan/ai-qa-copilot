
import json
from .llm_client import LMClient
from .vision_agent import VisionAgent

class RequirementAgent:
    def __init__(self, lm=None):
        self.lm = lm or LMClient()
        self.vision = VisionAgent()

    def analyze(self, story_text: str, image_paths=None):
        image_context = []

        if image_paths:
            for img in image_paths:
                image_context.append(self.vision.analyze_image(img))

        prompt = f"""
Extract feature details from the story and return STRICT JSON:

{{
  "feature_id": "<string>",
  "title": "<string>",
  "screens": [
      {{"name": "<string>", "elements": ["btn_login", "email_field", ...]}}
  ],
  "flows": ["happy_path", "error_path"],
  "api_endpoints": ["POST /api/login"],
  "risks": ["validation", "empty_input"]
}}
        Story:
        {story_text}

        Extracted UI:
        {json.dumps(image_context)}
        """

        raw = self.lm.generate(prompt)

        try:
            return json.loads(raw)
        except:
            return {"feature_id": "feat_demo", "title": "Unknown Feature", "screens": image_context}