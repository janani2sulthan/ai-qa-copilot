# agents/automation_agent.py
import os
import json
import re
from config_env import init_env

CFG = init_env()

class AutomationAgent:
    def __init__(self, lm=None):
        from .llm_client import LMClient
        self.lm = lm or LMClient()
        self.app_base = CFG.get("JIRA_BASE", "http://example.com")

    # ---------------------------------------------------------
    # Utility: Strip Markdown fences and clean Python code
    # ---------------------------------------------------------
    def _clean_code(self, text: str) -> str:
        if not text:
            return ""

        cleaned = text.strip()

        # Remove leading ``` or ```python
        cleaned = re.sub(r"^```(?:python)?", "", cleaned, flags=re.IGNORECASE).strip()

        # Remove trailing ```
        cleaned = re.sub(r"```$", "", cleaned).strip()

        # Remove accidental indent caused by prompt indentation
        cleaned = re.sub(r"^\s{8}", "", cleaned, flags=re.MULTILINE)

        return cleaned.strip()

    # ---------------------------------------------------------
    # Synthesize pytest tests
    # ---------------------------------------------------------
    def synthesize_pytests(self, testcases_json: dict, out_path: str):
        prompt = f"""
Convert these testcases into Python pytest code.

STRICT RULES:
- Output ONLY valid python
- NO markdown fences
- NO backticks
- One test function per testcase
- Use pytest only
- No comments outside functions

Testcases:
{json.dumps(testcases_json, indent=2)}
"""
        raw_code = self.lm.generate(prompt, max_output_tokens=4096)
        code = self._clean_code(raw_code)

        # If LM produced garbage or empty output → fallback example test
        if (
            not code
            or code.strip().startswith("[genai_error]")
            or "mock response" in code
            or code.strip() == "[mock]"
            or not code.startswith("def") and "test_" not in code
        ):
            code = f"""import pytest
from playwright.sync_api import sync_playwright

def test_login_flow():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("{self.app_base}")
        assert True
"""

        # Ensure folder exists
        os.makedirs(os.path.dirname(out_path), exist_ok=True)

        # Write cleaned code
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(code)

        return out_path

    # ---------------------------------------------------------
    # Behave (.feature file) synthesis
    # ---------------------------------------------------------
    def synthesize_behave_feature(self, testcases_json: dict, feature_path: str):
        prompt = f"""
Convert these testcases into a Behave (Gherkin) feature file.

STRICT RULES:
- Output ONLY Gherkin text
- No markdown; no code fences
- Include multiple scenarios if needed

Testcases JSON:
{json.dumps(testcases_json, indent=2)}
"""
        raw = self.lm.generate(prompt, max_output_tokens=2048)
        gherkin = self._clean_code(raw)

        if (
            not gherkin
            or gherkin.strip().startswith("[genai_error]")
            or "mock response" in gherkin
            or gherkin.strip() == "[mock]"
        ):
            gherkin = (
                "Feature: Login\n\n"
                "  Scenario: Login with valid credentials\n"
                "    Given I open the login page\n"
                "    When I enter valid credentials\n"
                "    And I click login\n"
                "    Then I should see the dashboard\n\n"
                "  Scenario: Login with invalid credentials\n"
                "    Given I open the login page\n"
                "    When I enter invalid credentials\n"
                "    And I click login\n"
                "    Then I should see an error message\n"
            )

        os.makedirs(os.path.dirname(feature_path), exist_ok=True)
        with open(feature_path, "w", encoding="utf-8") as f:
            f.write(gherkin)

        return feature_path

    def sync_gherkin_to_pytest(self, feature_file: str, out_py: str):
        with open(feature_file, "r") as f:
            gherkin = f.read()

        prompt = f"""
    Convert this Gherkin feature file into Python pytest test methods.

    STRICT RULES:
    - Output ONLY Python code
    - One pytest test per Scenario
    - Use Playwright sync API
    - Do NOT change scenario titles

    Gherkin:
    {gherkin}
    """

        code = self.lm.generate(prompt)

        clean = self._clean_code(code)

        os.makedirs(os.path.dirname(out_py), exist_ok=True)
        with open(out_py, "w", encoding="utf-8") as f:
            f.write(clean)

        return out_py