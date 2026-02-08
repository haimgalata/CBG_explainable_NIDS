import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not GEMINI_API_KEY and not OPENAI_API_KEY:
    raise RuntimeError("No LLM API key is set")

IPQS_API_KEY = os.getenv("IPQS_API_KEY")
VT_API_KEY = os.getenv("VT_API_KEY")
