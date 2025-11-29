# agents/testcase_agent.py
import json
import logging
import re
from typing import List, Dict, Any, Optional

from agents.llm_client import LMClient
from memory.persistent import PersistentMemory

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def extract_clean_json(raw: str) -> Any:
    if not raw:
        raise ValueError("Empty output")

    cleaned = raw.strip()
    cleaned = re.sub(r"^```(?:json|python)?\s*", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s*```$", "", cleaned, flags=re.IGNORECASE)

    first = min([p for p in (cleaned.find("{"), cleaned.find("[")) if p != -1], default=None)
    if first is None:
        raise ValueError("No JSON found in model output")

    opening = cleaned[first]
    closing = "}" if opening == "{" else "]"
    last = cleaned.rfind(closing)
    candidate = cleaned[first:last+1] if last != -1 else cleaned[first:]

    # Remove trailing commas
    candidate = re.sub(r",\s*(?=[}\]])", "", candidate)

    return json.loads(candidate)


class TestCaseAgent:
    """
    Interactive TestCaseAgent. Accepts clarifications from a conversation,
    uses persistent memory, and produces testcases.
    """

    def __init__(self, lm: Optional[LMClient] = None, memory: Optional[PersistentMemory] = None):
        self.lm = lm or LMClient()
        self.memory = memory or PersistentMemory()

    def _build_prompt(self, feature: Dict[str, Any], stored_context: Dict[str, Any], clarifications: Optional[Dict[str, Any]] = None, image_descriptions: Optional[List[str]] = None) -> str:
        schema = {
            "feature_id": "string",
            "test_cases": [
                {
                    "id": "string",
                    "title": "string",
                    "priority": "P0|P1|P2",
                    "type": "functional|negative|edge|performance|security",
                    "automation_feasible": "ui|api|no",
                    "steps": ["string"],
                    "expected": "string"
                }
            ]
        }

        clar_text = json.dumps(clarifications, indent=2) if clarifications else "{}"
        stored_text = json.dumps(stored_context, indent=2) if stored_context else "None"
        images_text = "\n".join(f"- {d}" for d in image_descriptions) if image_descriptions else "None"

        prompt = f"""
You are a senior QA engineer. Generate comprehensive test cases for the given feature.

IMPORTANT RULES:
- Output ONLY valid JSON following the provided schema (no commentary, no markdown fences).
- Use double quotes, no trailing commas.

SCHEMA:
{json.dumps(schema, indent=2)}

FEATURE:
{json.dumps(feature, indent=2)}

STORED MEMORY (prior runs / context):
{stored_text}

IMAGE DESCRIPTIONS:
{images_text}

USER CLARIFICATIONS:
{clar_text}

Now produce a JSON object that contains 'feature_id' and 'test_cases' as per the schema.
Keep test cases concise. For automation_feasible prefer 'ui' or 'api' or 'no'.
"""
        return prompt.strip()

    def generate(
        self,
        feature: Dict[str, Any],
        image_paths: Optional[List[str]] = None,
        image_descriptions: Optional[List[str]] = None,
        clarifications: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:

        feature_id = feature.get("feature_id", f"feat_{int(__import__('time').time())}")

        # Load memory if available
        stored = self.memory.get_feature(feature_id) or {}

        # If image_paths are provided, generate descriptions via LMClient (best-effort)
        if image_paths and not image_descriptions:
            image_descriptions = []
            for p in image_paths:
                try:
                    image_descriptions.append(self.lm.describe_image(p))
                except Exception:
                    image_descriptions.append(f"[desc_failed] {p}")

        prompt = self._build_prompt(feature, stored, clarifications, image_descriptions)

        logger.info("TestCaseAgent: sending prompt (len=%d)", len(prompt))
        raw = self.lm.generate(prompt, max_output_tokens=4096)
        logger.info("TestCaseAgent: raw output (first 500 chars): %s", raw[:500])

        parsed = None
        try:
            parsed = extract_clean_json(raw)
            logger.info("TestCaseAgent: parsed JSON successfully")
        except Exception as e:
            logger.warning("TestCaseAgent: parse failed, retrying with strict prompt: %s", e)
            # Strict retry
            strict_prompt = "OUTPUT ONLY VALID JSON (NO MARKDOWN). REPEAT your JSON now.\n\n" + prompt
            raw2 = self.lm.generate(strict_prompt, max_output_tokens=4096)
            try:
                parsed = extract_clean_json(raw2)
                logger.info("TestCaseAgent: parsed retry JSON block")
            except Exception as e2:
                logger.error("TestCaseAgent: retry parse failed: %s", e2)
                parsed = self._fallback(feature)

        # Persist feature + testcases
        try:
            self.memory.save_feature(feature_id, feature)
            if parsed:
                self.memory.save_feature(f"{feature_id}_tcs", parsed)
        except Exception:
            logger.exception("Failed to save memory (non-fatal)")

        return parsed

    def _fallback(self, feature: Dict[str, Any]) -> Dict[str, Any]:
        fid = feature.get("feature_id", "feat_fallback")
        return {
            "feature_id": fid,
            "test_cases": [
                {
                    "id": f"{fid}_TC_01",
                    "title": "Fallback testcase",
                    "priority": "P1",
                    "type": "functional",
                    "automation_feasible": "ui",
                    "steps": ["Step 1", "Step 2"],
                    "expected": "Fallback result"
                }
            ]
        }