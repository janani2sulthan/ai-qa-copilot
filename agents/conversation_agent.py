# agents/conversation_agent.py
import json
from typing import List, Dict, Any

class ConversationAgent:

    def __init__(self, mem, conv_id="default"):
        self.mem = mem
        self.conv_id = conv_id
        self.history = mem.load_conversation(conv_id) or []

    def add_user_msg(self, text):
        self.history.append({"role": "user", "text": text})
        self.mem.save_conversation(self.conv_id, self.history)

    def add_agent_msg(self, text):
        self.history.append({"role": "agent", "text": text})
        self.mem.save_conversation(self.conv_id, self.history)

    def get_context(self) -> str:
        """Convert history to a prompt-friendly text block."""
        ctx_lines = []
        for turn in self.history:
            role = turn.get("role", "user").upper()
            txt = turn.get("text", "")
            ctx_lines.append(f"{role}: {txt}")
        return "\n".join(ctx_lines)

    def clear(self):
        self.history = []

    def to_json(self) -> str:
        return json.dumps(self.history, indent=2)

    def save(self):
        if self.mem:
            self.mem.save_conversation(self.conv_id, self.history)

    def reset(self):
        self.history = []
        self.save()