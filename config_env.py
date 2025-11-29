
from dotenv import load_dotenv
import os
from pathlib import Path

def init_env(path=None):
    env_path = path or Path(__file__).parent / ".env.example"
    load_dotenv(env_path)
    return {
        "GOOGLE_API_KEY": os.getenv("GOOGLE_API_KEY"),
        "GEMINI_MODEL": os.getenv("GEMINI_MODEL"),
        "XRAY_MOCK_URL": os.getenv("XRAY_MOCK_URL"),
        "APP_BASE_URL": os.getenv("APP_BASE_URL"),
    }
