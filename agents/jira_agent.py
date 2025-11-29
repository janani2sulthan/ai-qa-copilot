from tools.jira_tool import JiraAPI

class JiraAgent:
    def __init__(self):
        self.jira = JiraAPI()

    def attach_testcases(self, issue_key: str, testcases_json: dict):
        body = "### Auto-generated test cases\n"
        for tc in testcases_json.get("test_cases", []):
            body += f"- **{tc.get('id')}**: {tc.get('title')} (priority: {tc.get('priority')})\n"
        return self.jira.add_comment(issue_key, body)

    def attach_artifact(self, issue_key: str, file_path: str):
        return self.jira.add_attachment(issue_key, file_path)