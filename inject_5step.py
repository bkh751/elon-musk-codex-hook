#!/usr/bin/env python3
import json
from pathlib import Path
import sys

payload = json.load(sys.stdin)
STATE_FILE = Path(".codex/tmp/original_prompt.txt")

STATE_FILE.parent.mkdir(parents=True, exist_ok=True)

prompt = payload.get("prompt", "")

# 🔥 원본 저장

STATE_FILE.write_text(prompt)

additional_context = f"""
You must use the following engineering loop while solving the user's request.

Elon Musk 5-step engineering process:
1. Question the requirements.
2. Delete unnecessary parts.
3. Simplify / optimize.
4. Accelerate cycle time.
5. Automate only after the above.

Rules for this turn:
- Before making changes, restate the requirement in one sentence.
- Identify at least one thing that may be unnecessary.
- Prefer simpler solutions over broader ones.
- Mention one speed or feedback improvement if relevant.
- Do not over-automate prematurely.

Original user prompt:
{prompt}
""".strip()

print(json.dumps({
    "hookSpecificOutput": {
        "hookEventName": "UserPromptSubmit",
        "additionalContext": additional_context
    }
}))