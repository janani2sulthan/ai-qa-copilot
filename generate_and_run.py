# generate_and_run.py
import os
import json
import datetime
from pathlib import Path
from agents.requirement_agent import RequirementAgent
from agents.testcase_agent import TestCaseAgent
from agents.automation_agent import AutomationAgent
from agents.execution_agent import ExecutionAgent
from agents.jira_agent import JiraAgent
from memory.persistent import PersistentMemory
from agents.llm_client import LMClient
import requests

BASE = Path(__file__).parent
SAMPLE = BASE / "sample_data" / "story_login.md"
GENERATED = BASE / "generated_tests"
LOGS = BASE / "logs"
XRAY = os.getenv("XRAY_MOCK_URL", "http://localhost:5001")

LOGS.mkdir(exist_ok=True)
GENERATED.mkdir(exist_ok=True)


def trace(msg):
    ts = datetime.datetime.utcnow().isoformat() + "Z"
    print(f"{ts} | {msg}")


def main():
    trace("Starting enhanced pipeline")
    if not SAMPLE.exists():
        print("Create sample_data/story_login.md first")
        return
    story = SAMPLE.read_text()

    lm = LMClient()
    req = RequirementAgent()
    memory = PersistentMemory()
    gen = TestCaseAgent(lm=lm, memory=memory)
    auto = AutomationAgent(lm=lm)
    exec_agent = ExecutionAgent()
    jira = JiraAgent()

    trace("Analyze")
    feature = req.analyze(story)
    fid = feature.get("feature_id", "feat_demo")
    memory.save_feature(fid, feature)
    trace(f"Feature saved: {fid}")

    trace("Generate TCs")
    # in a CLI run we don't have images; pass empty list
    tests_json = gen.generate(feature, image_paths=[])
    tc_path = GENERATED / f"testcases_{tests_json.get('feature_id', fid)}.json"
    tc_path.write_text(json.dumps(tests_json, indent=2))

    trace("Synthesize automation")
    out_file = GENERATED / f"test_suite_{tests_json.get('feature_id', fid)}.py"
    auto.synthesize_pytests(tests_json, str(out_file))

    trace("Run tests")
    code, stdout, stderr = exec_agent.run_pytest(str(out_file))
    trace(f"Run done exit={code}")
    res_path = GENERATED / f"results_{fid}.txt"
    res_path.write_text(stdout + "\n" + stderr)

    trace("Attach to Jira")
    jira_resp = jira.attach_testcases("STORY-101", tests_json)
    trace(f"Attach to Jira: {jira_resp}")

    trace("XRAY post")
    try:
        resp = requests.post(f"{XRAY}/xray/executions", json={"feature_id": fid, "summary": "demo exec"}, timeout=3)
        trace(f"XRAY post response: {resp.status_code}")
    except Exception as e:
        trace(f"XRAY post failed: {e}")

    trace("Pipeline complete")


if __name__ == "__main__":
    main()