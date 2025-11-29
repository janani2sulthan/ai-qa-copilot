# agents/clarifier_agent.py
from typing import Dict, List

class ClarifierAgent:
    """
    Simple clarifier engine to determine follow-up questions
    for test-case generation. This is intentionally lightweight;
    you can extend to use an LLM to generate dynamic questions.
    """

    def determine_questions(self, feature: Dict) -> List[str]:
        """
        Return an ordered list of clarifying questions based on the feature.
        """
        qs = []

        # Basic questions that apply to most features
        qs.append("Do you want UI testcases, API testcases, or both?")
        qs.append("Should I include negative and edge cases? (yes/no)")
        qs.append("Approximately how many testcases would you like? (e.g., 5)")
        qs.append("Do you want automation generated? (pytest/behave/none)")
        qs.append("Any environment preference? (e.g., chrome/headless/mobile/none)")

        # If feature text mentions authentication, ask about credentials
        text = " ".join(str(v) for v in feature.values() if isinstance(v, str)).lower()
        if "login" in text or "signin" in text:
            qs.insert(0, "Does this feature require authentication? Provide test account details or say 'no'.")

        return qs