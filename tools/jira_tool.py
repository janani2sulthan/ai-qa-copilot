# tools/jira_tool.py
import os, requests
from base64 import b64encode

class JiraAPI:
    def __init__(self):
        self.base = os.getenv('JIRA_BASE')
        self.user = os.getenv('JIRA_USER')
        self.api_token = os.getenv('JIRA_API_TOKEN')
        # if any of the above are missing, stay in mock mode
        self.mock = not all([self.base, self.user, self.api_token])
        if not self.mock:
            auth = b64encode(f"{self.user}:{self.api_token}".encode()).decode()
            self.headers = {'Authorization': f'Basic {auth}', 'Content-Type': 'application/json'}

    def add_comment(self, issue_key, comment):
        if self.mock:
            return {'issue': issue_key, 'status': 'mock_comment_added', 'preview': comment[:200]}
        url = f"{self.base}/rest/api/3/issue/{issue_key}/comment"
        resp = requests.post(url, headers=self.headers, json={'body': comment})
        try:
            return {'status_code': resp.status_code, 'response': resp.json()}
        except Exception:
            return {'status_code': resp.status_code, 'response': {'raw_text': resp.text}, 'note': 'response not JSON'}