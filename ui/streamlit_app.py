# ui/streamlit_app.py
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import pathlib
import os
from pathlib import Path
import streamlit as st
from dotenv import load_dotenv
import json
import tempfile
import time
import requests

# ensure env loaded
load_dotenv()

# allow imports from project root
ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

# imports
from agents.requirement_agent import RequirementAgent
from agents.testcase_agent import TestCaseAgent
from agents.automation_agent import AutomationAgent
from agents.execution_agent import ExecutionAgent
from agents.jira_agent import JiraAgent
from tools.figma_tool import FigmaTool
from memory.persistent import PersistentMemory
from agents.llm_client import LMClient
from agents.conversation_agent import ConversationAgent
from agents.clarifier_agent import ClarifierAgent


# UI layout settings
st.set_page_config(page_title="AI QA Co-Pilot — Enterprise UI", layout="wide")
st.title("AI QA Co-Pilot — Interactive Multi-Agent QA Assistant")

# ------------------------------
# INIT CONVERSATION MEMORY
# ------------------------------
mem = PersistentMemory()

if "conv" not in st.session_state:
    st.session_state["conv"] = ConversationAgent(mem=mem, conv_id="main_ui_chat")
conv = st.session_state["conv"]
if "clar_questions" not in st.session_state:
    st.session_state["clar_questions"] = []
if "clar_answers" not in st.session_state:
    st.session_state["clar_answers"] = {}
if "clar_active" not in st.session_state:
    st.session_state["clar_active"] = False

# Left / middle / right columns
left, middle, right = st.columns([1.2, 2, 1])

with left:
    st.header("Uploads & File Manager")
    images = st.file_uploader("Drag and drop images", type=["png", "jpg", "jpeg"], accept_multiple_files=True)
    st.markdown("Limit 200MB per file • PNG, JPG, JPEG")
    st.markdown("---")
    st.markdown("**Upload story (.md .txt)**")
    story_file = st.file_uploader("Upload .md/.txt", type=["md", "txt"])
    st.markdown("Or paste story text below")
    st.markdown("---")
    if images:
        st.write("Uploaded images")
        for img in images:
            st.write(f"- {img.name} ({img.size} bytes)")
    if story_file:
        st.write(f"Uploaded story file: {story_file.name}")

with middle:
    st.header("Story / Feature")
    story_text = ""
    if story_file:
        try:
            story_text = story_file.getvalue().decode("utf-8")
        except Exception:
            story_text = "<binary file - open in editor>"
    story_text = st.text_area("Story (edit if needed)", value=story_text, height=240)

    st.markdown("---")
    st.header("Actions")
    col_a, col_b, col_c = st.columns(3)
    analyze_btn = col_a.button("Analyze Feature (Extract Context)")
    gen_tc_btn = col_b.button("Generate Test Cases")
    gen_auto_btn = col_c.button("Generate Automation")
    gen_gherkin_btn = st.button("Generate Gherkin Feature")
    sync_btn = st.button("Sync Pytest from Gherkin")
    run_tests_btn = st.button("Run Tests")
    publish_btn = st.button("Publish to Jira/Xray")

    st.markdown("---")
    st.header("Interactive Chat")
    chat_box = st.container()
    with chat_box:
        st.markdown("### Conversation")
        # show history
        conv: ConversationAgent = st.session_state["conv"]
        for turn in conv.history:
            role = "You" if turn["role"] == "user" else "Agent"
            if turn["role"] == "user":
                st.info(f"**You:** {turn['text']}")
            else:
                st.success(f"**Agent:** {turn['text']}")
        user_input = st.text_input("Send a message to the agent", key="chat_input")
        send_chat = st.button("Send Message")

    st.markdown("---")
    st.header("Outputs")
    feature_placeholder = st.empty()
    tc_placeholder = st.empty()
    auto_placeholder = st.empty()
    exec_placeholder = st.empty()
    publish_placeholder = st.empty()

with right:
    st.header("Memory")
    mem = PersistentMemory()
    fid_input = st.text_input("Load feature id", value="")
    if st.button("Load feature from memory"):
        if fid_input.strip():
            loaded = mem.get_feature(fid_input.strip())
            if loaded:
                st.success(f"Loaded feature {fid_input.strip()}")
                story_text = json.dumps(loaded, indent=2)
            else:
                st.error("Feature not found")
    st.markdown("### Stored features")
    try:
        rows = mem.list_features()
        for r in rows[:20]:
            st.write(f"- {r[0]} (updated: {r[1]})")
    except Exception:
        st.write("No stored features yet")

# Instantiate agents
lm = LMClient()
req_agent = RequirementAgent()
mem = PersistentMemory()
testcase_agent = TestCaseAgent(lm=lm, memory=mem)
auto_agent = AutomationAgent(lm=lm)
exec_agent = ExecutionAgent()
jira_agent = JiraAgent()
figma_tool = FigmaTool(token=os.getenv("FIGMA_TOKEN"))
clarifier = ClarifierAgent()

# helper functions
def save_uploaded_images(files):
    paths = []
    for f in files or []:
        tmp = Path("uploads") / f.name
        tmp.parent.mkdir(parents=True, exist_ok=True)
        with open(tmp, "wb") as out:
            out.write(f.getbuffer())
        paths.append(str(tmp))
    return paths

def show_json_or_text(obj, area):
    if isinstance(obj, (dict, list)):
        area.json(obj)
    else:
        area.text(str(obj))

# --- Action handlers ---

# Analyze Feature
if analyze_btn:
    if not story_text.strip():
        st.warning("Provide story text (paste/upload) first.")
    else:
        feature = req_agent.analyze(story_text)
        feature_placeholder.subheader("Feature Summary")
        feature_placeholder.json(feature)
        try:
            fid = feature.get("feature_id", f"feat_{int(time.time())}")
            mem.save_feature(fid, feature)
            st.success(f"Saved feature to memory: {fid}")
        except Exception as e:
            st.error(f"Memory save failed: {e}")

# ---------------------------
# CHAT SEND / CLARIFIER FLOW
# ---------------------------
if send_chat:
    user_msg = user_input.strip()
    conv = st.session_state["conv"]

    if not user_msg:
        conv.add_agent_msg("Please enter a valid message.")
        st.rerun()

    # 1) Store user message
    conv.add_user_msg(user_msg)

    # 2) If clarifier not started, begin clarifier questions
    if not st.session_state["clar_active"]:
        # Parse feature once
        try:
            feature_ctx = json.loads(story_text)
        except Exception:
            feature_ctx = req_agent.analyze(story_text) if story_text.strip() else {}

        # Generate questions
        qs = clarifier.determine_questions(feature_ctx)

        st.session_state["clar_questions"] = qs
        st.session_state["clar_answers"] = {}
        st.session_state["clar_active"] = True

        # Ask first question
        next_q = st.session_state["clar_questions"].pop(0)
        st.session_state["last_q"] = next_q
        conv.add_agent_msg(next_q)
        st.rerun()

    # 3) Clarifier is active → store answer
    else:
        # Save answer to last question
        last_q = st.session_state["last_q"]
        st.session_state["clar_answers"][last_q] = user_msg

        # If more questions remain
        if st.session_state["clar_questions"]:
            next_q = st.session_state["clar_questions"].pop(0)
            st.session_state["last_q"] = next_q
            conv.add_agent_msg(next_q)
            st.rerun()

        # 4) No more questions → generate testcases
        else:
            conv.add_agent_msg("Thanks! Generating test cases now using your clarifications…")

            st.session_state["clar_active"] = False

            clar_map = st.session_state["clar_answers"]

            # Prepare feature & images
            try:
                feature = json.loads(story_text)
            except Exception:
                feature = req_agent.analyze(story_text) if story_text.strip() else {}

            image_paths = save_uploaded_images(images) if images else []
            image_descs = [lm.describe_image(p) for p in image_paths] if image_paths else []

            # Generate test cases
            try:
                tcs = testcase_agent.generate(
                    feature=feature,
                    image_paths=image_paths,
                    image_descriptions=image_descs,
                    clarifications=clar_map,
                )
                tc_placeholder.subheader("Generated Test Cases")
                tc_placeholder.json(tcs)

                # Save testcases
                outdir = Path("generated_tests")
                outdir.mkdir(exist_ok=True)
                outpath = outdir / f"testcases_{tcs.get('feature_id','feat_demo')}.json"
                outpath.write_text(json.dumps(tcs, indent=2))

                conv.add_agent_msg("Test cases generated and saved.")

            except Exception as e:
                conv.add_agent_msg(f"Test case generation failed: {e}")

            st.rerun()


# Generate Test Cases (direct button flow)
if gen_tc_btn:
    image_paths = save_uploaded_images(images) if images else []
    image_descs = []
    for p in image_paths:
        try:
            d = lm.describe_image(p)
            image_descs.append(d)
        except Exception:
            image_descs.append(f"[desc_failed] {p}")
    try:
        feature = None
        try:
            feature = json.loads(story_text)
        except Exception:
            feature = req_agent.analyze(story_text) if story_text.strip() else {}
        tc_placeholder.subheader("Generated Test Cases")
        tcs = testcase_agent.generate(feature=feature, image_paths=image_paths, image_descriptions=image_descs)
        tc_placeholder.json(tcs)
        st.success("Test cases generated")
        outdir = Path("generated_tests")
        outdir.mkdir(exist_ok=True)
        outpath = outdir / f"testcases_{tcs.get('feature_id','feat_demo')}.json"
        outpath.write_text(json.dumps(tcs, indent=2))
    except Exception as e:
        tc_placeholder.error(f"Test Casey generation failed: {e}")

# Generate Automation
if gen_auto_btn:
    gen_dir = Path("generated_tests")
    last = None
    if gen_dir.exists():
        files = sorted([p for p in gen_dir.glob("testcases_*.json")], key=lambda p: p.stat().st_mtime, reverse=True)
        if files:
            last = files[0]
    if not last:
        st.warning("No testcases found. Generate test cases first.")
    else:
        tcs = json.loads(last.read_text())
        out_py = gen_dir / f"test_suite_{tcs.get('feature_id','feat_demo')}.py"
        auto_agent.synthesize_pytests(tcs, str(out_py))
        auto_placeholder.subheader("Generated Automation")
        auto_placeholder.code(out_py.read_text(), language="python")
        st.success(f"Automation written: {out_py}")

# Run Tests
if run_tests_btn:
    gen_dir = Path("generated_tests")
    files = sorted([p for p in gen_dir.glob("test_suite_*.py")], key=lambda p: p.stat().st_mtime, reverse=True)
    if not files:
        exec_placeholder.warning("No automation found. Generate automation first.")
    else:
        target = files[0]
        exec_placeholder.subheader("Execution Output")
        code, out, err = exec_agent.run_pytest(str(target))
        exec_placeholder.text(f"Exit: {code}\n{out}\n{err}")

# Publish
if publish_btn:
    gen_dir = Path("generated_tests")
    files = sorted([p for p in gen_dir.glob("testcases_*.json")], key=lambda p: p.stat().st_mtime, reverse=True)
    if not files:
        publish_placeholder.warning("No testcases to publish. Generate test cases first.")
    else:
        tcs = json.loads(files[0].read_text())
        issue_key = st.text_input("Jira issue key to attach to", value="STORY-101")
        res = jira_agent.attach_testcases(issue_key, tcs)
        publish_placeholder.subheader("Publish Result")
        publish_placeholder.json(res)
        xray_url = os.getenv("XRAY_MOCK_URL", "http://localhost:5001")
        exec_files = sorted([p for p in gen_dir.glob("results_*.txt")], key=lambda p: p.stat().st_mtime, reverse=True)
        if exec_files:
            try:
                payload = {"feature_id": tcs.get("feature_id", "feat_demo"), "results": exec_files[0].read_text()}
                r = requests.post(f"{xray_url}/xray/executions", json=payload, timeout=3)
                publish_placeholder.write(f"XRAY response: {r.status_code}")
            except Exception as e:
                publish_placeholder.error(f"XRAY post failed: {e}")

if gen_gherkin_btn:
    gen_dir = Path("generated_tests")
    last_tc = None
    if gen_dir.exists():
        files = sorted([p for p in gen_dir.glob("testcases_*.json")],
                       key=lambda p: p.stat().st_mtime, reverse=True)
        if files:
            last_tc = files[0]

    if not last_tc:
        st.warning("No testcases found. Generate testcases first.")
    else:
        tcs = json.loads(last_tc.read_text())
        feature_path = gen_dir / f"{tcs.get('feature_id','feat_demo')}.feature"
        auto_agent.synthesize_behave_feature(tcs, str(feature_path))
        st.success(f"Gherkin feature generated: {feature_path}")
        st.code(feature_path.read_text(), language="gherkin")

if sync_btn:
    gen_dir = Path("generated_tests")
    feature_files = sorted([p for p in gen_dir.glob("*.feature")],
                           key=lambda p: p.stat().st_mtime, reverse=True)

    if not feature_files:
        st.warning("No feature file found. Generate Gherkin first.")
    else:
        feature_file = feature_files[0]
        out_py = gen_dir / f"test_suite_{feature_file.stem}.py"
        auto_agent.sync_gherkin_to_pytest(str(feature_file), str(out_py))
        st.success(f"Pytest updated from Gherkin: {out_py}")
        st.code(out_py.read_text(), language="python")
