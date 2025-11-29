# agents/llm_client.py
import os
import json
import logging
from typing import Optional

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class LMClient:
    """
    LMClient updated for the NEW Gemini SDK (2025+).

    Uses:
      from google.generativeai import GenerativeModel
      model = GenerativeModel("gemini-2.0-flash")
      model.generate_content(...)
    """

    def __init__(self, model_name: Optional[str] = None):
        self.api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GENAI_API_KEY")
        self.model_name = model_name or os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
        self.use_mock = not bool(self.api_key)

        if self.use_mock:
            logger.warning("LMClient: API key missing — using mock mode")
            self.model = None
            return

        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            from google.generativeai import GenerativeModel

            self.model = GenerativeModel(self.model_name)
            logger.info("LMClient: Using new Gemini SDK interface")

        except Exception as e:
            logger.exception("LMClient: Failed to initialize new Gemini SDK")
            self.use_mock = True
            self.model = None

    # ---------------------------------------------------------------------
    # TEXT GENERATION
    # ---------------------------------------------------------------------
    def generate(self, prompt: str, max_output_tokens: int = 4096) -> str:
        """Generate text using Gemini 2.x or return mock output."""

        if self.use_mock or self.model is None:
            return self._mock_response(prompt)

        try:
            response = self.model.generate_content(
                prompt,
                generation_config={"max_output_tokens": max_output_tokens, "temperature": 0.0, "top_p": 1, "top_k": 1}
            )

            # new SDK unified text access
            return response.text or ""

        except Exception as e:
            logger.exception("LMClient.generate failed")
            return f"[genai_error] {str(e)}"

    # ---------------------------------------------------------------------
    # IMAGE DESCRIPTION
    # ---------------------------------------------------------------------
    def describe_image(self, image_path: str) -> str:
        """Describe an image using new Gemini multimodal input."""

        if self.use_mock or self.model is None:
            return self._local_fallback(image_path)

        try:
            if not os.path.exists(image_path):
                return f"[image_missing] {image_path}"

            # Multimodal: pass image as binary
            with open(image_path, "rb") as f:
                img_bytes = f.read()

            response = self.model.generate_content(
                [
                    "Describe this image in short bullet points.",
                    {"mime_type": "image/png", "data": img_bytes},
                ]
            )

            return response.text or "[no_description]"

        except Exception:
            logger.exception("LMClient.describe_image: Gemini multimodal failed")
            return self._local_fallback(image_path)

    # ---------------------------------------------------------------------
    # LOCAL IMAGE FALLBACK
    # ---------------------------------------------------------------------
    def _local_fallback(self, image_path: str) -> str:
        """Simple local metadata if multimodal not possible."""
        if not os.path.exists(image_path):
            return f"[image_missing] {image_path}"

        try:
            from PIL import Image
            img = Image.open(image_path)
            w, h = img.size
            return json.dumps({
                "source": os.path.basename(image_path),
                "format": img.format,
                "width": w,
                "height": h,
            })
        except Exception:
            size = os.path.getsize(image_path)
            return json.dumps({
                "file": os.path.basename(image_path),
                "size_bytes": size
            })

    # ---------------------------------------------------------------------
    # MOCK RESPONSE (FOR TEST MODE)
    # ---------------------------------------------------------------------
    def _mock_response(self, prompt: str) -> str:
        p = prompt.lower()

        if "extract feature" in p:
            return json.dumps({
                "feature_id": "feat_demo",
                "title": "Login",
                "screens": [{"name": "Login", "elements": ["email", "password", "login_btn"]}],
                "flows": ["login_success", "login_failure"]
            })

        if "generate testcases" in p:
            return json.dumps({
                "feature_id": "feat_demo",
                "test_cases": [
                    {
                        "id": "TC_LOGIN_01",
                        "title": "Valid Login",
                        "priority": "P0",
                        "steps": ["Enter email", "Enter password", "Click login"],
                        "expected": "Dashboard loaded"
                    }
                ]
            })

        if "convert" in p:
            return "def test_tc_login_01():\n    assert True\n"

        return "[mock] no matching pattern"