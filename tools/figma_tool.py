# tools/figma_tool.py
import os, requests
from urllib.parse import urlparse

class FigmaTool:
    """
    Lightweight helper to fetch a Figma file (requires FIGMA_TOKEN env var) or return mock
    frames if token not provided.
    """

    def __init__(self, token: str = None):
        self.token = token or os.getenv("FIGMA_TOKEN")
        self.headers = {"X-Figma-Token": self.token} if self.token else None

    def fetch_file(self, file_key: str):
        """
        If token present, call Figma API and return a simplified dict of frames:
        { "frames": [{"id":..., "name":..., "elements": [...]}, ...] }
        If token missing or fetch fails, return a small mock structure.
        """
        if not self.headers:
            return {"mock": True, "frames": [{"id":"frame_login", "name":"Login", "elements":["email","password","login_btn"]}]}
        # try to extract file key if full URL given
        if file_key.startswith("http"):
            parsed = urlparse(file_key)
            file_key = parsed.path.strip("/").split("/")[-1]
        url = f"https://api.figma.com/v1/files/{file_key}"
        r = requests.get(url, headers=self.headers, timeout=10)
        r.raise_for_status()
        data = r.json()
        # Walk document nodes for frames (best-effort)
        frames = []
        try:
            doc = data.get("document", {})
            # naive traversal for frames
            def walk(node):
                if not isinstance(node, dict):
                    return
                typ = node.get("type")
                if typ == "FRAME":
                    frames.append({"id": node.get("id"), "name": node.get("name"), "children_count": len(node.get("children", []))})
                for c in node.get("children", []) or []:
                    walk(c)
            walk(doc)
        except Exception:
            frames = [{"id":"frame_1","name":"Main","elements":[]}]
        return {"mock": False, "frames": frames, "raw": {"name": data.get("name")}}