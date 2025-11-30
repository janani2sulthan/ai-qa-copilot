# 🚀 AI QA Co-Pilot  
### **An Interactive Multi-Agent QA Automation Assistant Powered by Gemini**

Enterprise-grade, autonomous QA system that analyzes requirements, generates test cases, writes automation scripts, executes tests, and updates Jira — all through an intelligent multi-agent architecture.

---

## 🌟 Overview

AI QA Co-Pilot is a **multi-agent, memory-enabled QA assistant** built to automate the entire QA lifecycle.  
Unlike traditional test generators, this system:

- **Understands** requirements  
- **Asks clarifying questions**  
- **Generates complete structured test cases**  
- **Writes Playwright/Pytest automation**  
- **Executes tests locally**  
- **Publishes results to Jira/Xray**  
- **Understands Figma & Screenshots**  
- **Retains context using persistent memory**  

It behaves like a *smart QA engineer* — fast, consistent, and always available.

---

# 🧠 Core Features

## 1️⃣ Requirement Analysis  
- Extracts acceptance criteria  
- Identifies flows, validations, edge cases  
- Parses screenshots & Figma designs  

## 2️⃣ Intelligent Test Case Generation  
- Functional / negative / edge cases  
- API + UI test cases  
- Structured JSON output  
- BDD (Given/When/Then) support  
- Full sprint-coverage test planning  

## 3️⃣ Automation Generation  
Supports:
- **Playwright (Python)**
- **PyTest UI automation**
- API Test automation  

Generated code adheres to:
- Page Object Model (POM)  
- Reusable locator structure  
- Clean coding practices  

## 4️⃣ Test Execution  
- Runs automation via PyTest  
- Captures logs + output  
- Provides pass/fail summary  

## 5️⃣ Jira / Xray Integration  
- Uploads test cases  
- Posts test execution results  
- Maintains traceability  

## 6️⃣ Vision + Figma Understanding  
- Extracts UI structure from screenshots  
- Knows screen flows and components  
- Reads Figma nodes + layers  

## 7️⃣ Memory + Conversation  
- Persistent SQLite memory  
- Saves feature-level context  
- Saves conversation history  
- Clarification Q&A memory  

---

# 🏗️ Architecture

```
                       ┌──────────────────────────┐
                       │      ConversationAgent    │
                       │   (UI chat + memory)      │
                       └──────────────┬────────────┘
                                      │
                       ┌──────────────▼─────────────┐
                       │      ClarifierAgent         │
                       │ Asks clarifying questions   │
                       └──────────────┬─────────────┘
                                      │
┌─────────────────────────────────────▼─────────────────────────────────────┐
│                           RequirementAgent                                 │
│    Extracts stories, flows, acceptance criteria, dependencies              │
└───────────────────────────────┬───────────────────────────────────────────┘
                                │
                       ┌────────▼─────────┐
                       │  TestCaseAgent   │
                       │ Generates full   │
                       │ JSON test suites │
                       └────────┬─────────┘
                                │
                       ┌────────▼─────────┐
                       │ AutomationAgent  │
                       │ Generates POM +  │
                       │ PyTest code      │
                       └────────┬─────────┘
                                │
                       ┌────────▼─────────┐
                       │ ExecutionAgent   │
                       │ Runs tests       │
                       └────────┬─────────┘
                                │
                       ┌────────▼─────────┐
                       │    JiraAgent     │
                       │ Publishes tests  │
                       │ + run results    │
                       └──────────────────┘
```

---

# 📂 Project Structure

```
option_a_ai_heavy_full/
│
├── agents/
│   ├── llm_client.py
│   ├── requirement_agent.py
│   ├── testcase_agent.py
│   ├── automation_agent.py
│   ├── execution_agent.py
│   ├── jira_agent.py
│   ├── conversation_agent.py
│   ├── clarifier_agent.py
│
├── ui/
│   ├── streamlit_app.py
│
├── memory/
│   ├── persistent.py
│
├── tools/
│   ├── figma_tool.py
│
├── generated_tests/
├── uploads/
├── generate_and_run.py
├── config_env.py
└── README.md
```

---

# ⚙️ Setup Instructions

### 1. Clone the repository  
```bash
git clone <YOUR_GITHUB_REPO_URL>
cd ai-qa-copilot
```

### 2. Create virtual environment  
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Add `.env` file  
```
GOOGLE_API_KEY=xxxx
FIGMA_TOKEN=xxxx
JIRA_BASE=https://yourcompany.atlassian.net
JIRA_EMAIL=you@example.com
JIRA_API_TOKEN=xxxx
```

---

# ▶️ Running the App

## **Streamlit UI**
```bash
streamlit run ui/streamlit_app.py
```

Once opened, you can:
- Upload screenshots  
- Paste story text  
- Chat with agent  
- Generate test cases  
- Generate automation  
- Run tests  
- Publish to Jira  

## **CLI Pipeline**
```bash
python generate_and_run.py
```

Executes the entire workflow automatically.

---

# 🧪 Example Generated Test Case

```json
{
  "feature_id": "login",
  "test_cases": [
    {
      "id": "TC_LOGIN_001",
      "title": "Login with valid credentials",
      "priority": "P0",
      "type": "functional",
      "automation_feasible": "ui",
      "steps": [
        "Open login page",
        "Enter valid username",
        "Enter valid password",
        "Click Login"
      ],
      "expected": "User lands on dashboard"
    }
  ]
}
```

---

# 🧪 Example Generated Automation (PyTest + Playwright and Behave(Gherkin))

```python
def test_login_valid(page):
    page.goto("https://app.example.com/login")
    page.fill("#email", "user@example.com")
    page.fill("#password", "Correct@123")
    page.click("button[type=submit']")
    assert "/dashboard" in page.url
```

```Behave (Gherkin) feature file 
Feature: Login

  Scenario: Login with valid credentials
    Given I open the login page
    When I enter valid credentials
    And I click login
    Then I should see the dashboard

  Scenario: Login with invalid credentials
    Given I open the login page
    When I enter invalid credentials
    And I click login
    Then I should see an error message
```


# Worked Example
---

### 📌 Input: User Story

```text
As a user, I want to log into the application using my email and password so that I can access my dashboard.

Acceptance Criteria:
- User can enter email
- User can enter password
- Login button becomes enabled when both fields are filled
- Show error message for invalid credentials
- Redirect to dashboard on successful login
```

### 🧠 Step 1 — RequirementAgent Output (Extracted Requirements)

```
Flows:
- Valid login flow
- Invalid login flow

Validations:
- Email field must allow valid email formats
- Password required
- Login button enabled only when inputs are valid

Edge Cases:
- Empty fields
- Incorrect password
- Invalid email format
```

### 🧪 Step 2 — TestCaseAgent Output (Structured JSON Testcases)

```json
{
  "feature_id": "login",
  "test_cases": [
    {
      "id": "TC_LOGIN_001",
      "title": "Login with valid credentials",
      "priority": "P0",
      "type": "functional",
      "steps": [
        "Open login page",
        "Enter valid email",
        "Enter valid password",
        "Click Login"
      ],
      "expected": "User is redirected to dashboard"
    },
    {
      "id": "TC_LOGIN_002",
      "title": "Login with invalid credentials",
      "priority": "P1",
      "type": "negative",
      "steps": [
        "Open login page",
        "Enter valid email",
        "Enter invalid password",
        "Click Login"
      ],
      "expected": "Error message displayed"
    }
  ]
}
```

### 🤖 Step 3 — AutomationAgent Output (Playwright + PyTest)

```python
def test_login_valid(page):
    page.goto("https://app.example.com/login")
    page.fill("#email", "user@example.com")
    page.fill("#password", "Correct@123")
    page.click("button[type=submit']")
    assert "/dashboard" in page.url
```

### 🚀 Step 4 — ExecutionAgent Output

```output
Test Execution Summary:
✓ 2 tests passed  
⏱ Duration: 3.2s  
Logs saved to /generated_tests/logs/login/
```

### 📌 Step 5 — JiraAgent Output
```
✓ Testcases uploaded to JIRA-123  
✓ Execution results attached  
```

# ⚠️ Limitations & Future Work

Although AI QA Co-Pilot is already powerful, the following areas can be improved for enterprise-level robustness:

---

### 🚧 Current Limitations

1. LLM-Generated Automation Is Not Always Deterministic
	•	Playwright selectors may vary slightly between runs.
	•	Dynamic IDs or complex shadow DOM structures require extra post-processing.

2. BDD (Gherkin) Support Is Basic
	•	Feature files are generated successfully,
but step definition auto-generation is limited.

3. Limited Vision Validation
	•	Screenshot understanding works for simple UI screens.
	•	Complex UI (carousels, nested modals) may require manual validation.

4. Jira/Xray Schema Variability
	•	Different Jira installations have different fields,
which may require custom mapping.

5. No Full “CI Pipeline Runner” Yet
	•	Tests execute locally.
	•	GitHub Actions/Cloud Run execution is possible but not fully integrated.

6. Memory Store Not Optimized for Large-Scale QA Data
	•	SQLite is ideal for single-user development.
	•	For multi-user enterprise mode, Postgres or Redis-based memory would be preferable.

----

# 🚀 Future Enhancements

1. Auto-Fixing Failing Automation Scripts
	•	Rerun tests, detect failing selectors, regenerate only broken steps.

2. Full BDD Lifecycle Support
	•	Auto-generate step definitions
	•	Auto-map steps to UI actions automatically

3. Deployment-ready Cloud Agent Runtime
	•	One-click deploy to GCP Cloud Run / Streamlit Cloud.

4. Multi-Agent Parallel Execution
	•	Generate test cases + automation + Jira updates in parallel.

5. Vision+Figma Deep Layout Understanding
	•	Detect clickable regions, text inputs, component types automatically.

6. Enterprise Memory System
	•	Semantic memory with vector embedding stores for 100+ features.

7. API Monitoring & Contract Testing
	•	Automatic test generation for OpenAPI Specs
	•	API drift detection

---

# 📌 Tech Used

- **Python**
- **Gemini API**
- **Streamlit**
- **Playwright**
- **PyTest**
- **SQLite Memory Store**
- **Figma REST API**
- **Jira REST API**

---

# ⭐ Final Notes  
This project demonstrates:
- Multi-agent reasoning  
- Memory + stateful sessions  
- Tool integrations  
- Code generation & execution  
- Enterprise workflow automation  
- Real-world QA engineering  

An end-to-end autonomous QA system built for production-grade environments.

