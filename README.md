# 🤖 AI QA Copilot

**AI QA Copilot** is an AI-powered assistant that helps QA engineers automate key testing activities such as **test case generation, test analysis, and QA workflow support** using LLM-based agent concepts.

This project was initially built as part of the **5-Day AI Agents Intensive Course with Google (via Kaggle)** and later extended locally with additional real-world features.

---

## 🚀 Project Overview

Modern QA workflows involve repetitive and time-consuming tasks such as understanding requirements, writing test cases, and managing test artifacts across tools.

AI QA Copilot aims to **assist QA engineers** by introducing **AI agents** that can:
- Understand user stories or requirements
- Generate structured manual test cases
- Support automation-ready outputs
- Integrate with QA management tools

This project demonstrates how **AI + QA Automation** can work together in practical, real-world scenarios.

---

## ✨ Key Features

- 📄 **Requirement Analysis** – Converts user stories into testable scenarios  
- 🧪 **Test Case Generation** – Produces structured test cases in JSON format  
- 🤖 **AI Agent Workflow** – Modular, extensible agent-based architecture  
- 🖥 **Enhanced Streamlit UI** (local version)  
- 🔗 **Jira Xray Synchronization** (local version)  
- 🧠 **LLM-powered reasoning**  
- 🐍 **Python-based implementation**

---

## 🛠 Tech Stack

- **Python**
- **LLM Support**
  - Gemini (course implementation)
  - Claude (local enhanced version)
- **Streamlit** (UI)
- **Playwright**
- **PyTest**
- **SQLite** (memory / context persistence)
- **Jira / Xray integration**

---

## 🚀 Local Enhancements (Extended Version)

In my local development environment, this project has been extended beyond the course requirements to include:

- ✅ Enhanced Streamlit UI for improved usability
- ✅ Jira Xray synchronization for managing test cases
- ✅ LLM flexibility with support for Claude in addition to Gemini
- ✅ Improved agent coordination and output formatting

These enhancements demonstrate how the project can be adapted and scaled for real-world QA environments.

---

## 📂 Project Structure

```text
ai-qa-copilot/
│
├── agents/               # AI agent logic
├── core/                 # Core processing logic
├── ui/                   # Streamlit UI
├── generate_and_run.py   # Main execution script
├── requirements.txt
├── README.md
└── .env.example
```
## ⚙️ Setup & Installation

# 1️⃣ Clone the repository
git clone https://github.com/janani2sulthan/ai-qa-copilot.git
cd ai-qa-copilot

# 2️⃣ Create virtual environment & install dependencies
python -m venv venv
source venv/bin/activate   # Mac/Linux
venv\Scripts\activate      # Windows

pip install -r requirements.txt

# 3️⃣ Configure Environment Variables

Create a .env file using .env.example and add your own API keys:
GOOGLE_API_KEY=your_google_api_key
CLAUDE_API_KEY=your_claude_api_key
JIRA_API_TOKEN=your_jira_token

# ▶️ How to Run

Run the main script to generate test cases:
python generate_and_run.py
Input can be a user story, Figma links, screenshots  or requirement text.
Output will be structured test cases in JSON format.

```

```
### 🧪 Example Generated Test Case

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
````
````
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
### 🎯 Learning Outcomes

Through this project, I gained experience in:
	•	Designing AI agent-based systems
	•	Applying LLMs to QA workflows
	•	Integrating AI with QA automation concepts
	•	Extending course projects into real-world solutions
``` 
```
### 🚧 Future Enhancements
	•	CI/CD pipeline integration
	•	Advanced test execution and reporting
	•	Role-based access in UI
	•	Additional LLM support
	•	Production-ready deployment
>>>>>>> 9c6ef1d (updated readme)

```
``` 
###🙌 Acknowledgements
	•	Google – AI Agents Intensive Course
	•	Kaggle – Learning platform and resources
```