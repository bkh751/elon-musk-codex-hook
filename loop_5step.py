#!/usr/bin/env python3
import json
import os
import re
import sys
from pathlib import Path

STATE_DIR = Path(".codex/tmp")
STATE_DIR.mkdir(parents=True, exist_ok=True)
STATE_FILE = STATE_DIR / "five_step_loop_state.json"

ORIGINAL_PROMPT_FILE = STATE_DIR /"original_prompt.txt"

original_prompt = ""

if ORIGINAL_PROMPT_FILE.exists():

    original_prompt = ORIGINAL_PROMPT_FILE.read_text()

MAX_ITERS = int(os.environ.get("CODEX_5STEP_MAX_ITERS", "5"))

def load_state():
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text())
        except Exception:
            pass
    return {"iterations": 0}

def save_state(state):
    STATE_FILE.write_text(json.dumps(state))

payload = json.load(sys.stdin)
last_msg = payload.get("last_assistant_message") or ""

state = load_state()
if "session_id" not in state or state.get("session_id") != payload.get("session_id"):
    state = {"iterations": 0, "session_id": payload.get("session_id")}
iters = state.get("iterations", 0)

# 종료 조건 1: 최대 반복 횟수
if iters >= MAX_ITERS:
    print(json.dumps({"continue": False}))
    sys.exit(0)

# 종료 조건 2: assistant가 완료 신호를 명시
done_markers = [
    # "DONE_5STEP",
    # "All checks passed",
    # "No further improvements",
    # "Final answer ready"
    "PROCEED 15 LOOP"
]
if any(marker.lower() in last_msg.lower() for marker in done_markers):
    print(json.dumps({"continue": False}))
    sys.exit(0)

# 간단한 품질 점검
issues = []

# 1) 요구사항 점검 흔적
if not re.search(r"requirement|요구사항|restat", last_msg, re.I):
    issues.append("요구사항을 한 문장으로 다시 정리하지 않았습니다.")

# 2) 제거/단순화 흔적
if not re.search(r"remove|delete|unnecessary|simplif|불필요|제거|단순", last_msg, re.I):
    issues.append("불필요한 요소 제거 또는 단순화 설명이 부족합니다.")

# 3) 검증 흔적
if not re.search(r"test|verify|validated|검증|테스트", last_msg, re.I):
    issues.append("결과 검증 또는 테스트 언급이 없습니다.")

if not issues:
    state["iterations"] = iters + 1
    save_state(state)
    if iters + 1 >= MAX_ITERS:
        print(json.dumps({"continue": False}))
    else:
        print(json.dumps({
            "decision": "block",
            "reason": f"Iteration {state['iterations']}/{MAX_ITERS} passed. Continue loop with only required improvements next."
        }))
    sys.exit(0)

state["iterations"] = iters + 1
save_state(state)

continuation_prompt = f"""


Original Prompt:
{original_prompt}

Revise the previous result using Elon Musk's 5-step engineering process.

Problems found:
- {chr(10).join(f"- {x}" for x in issues)}

Instructions:
1. Re-question the requirement. (Compact the Requirement, Save your Context, Review Remaining PRs and Merge If there is no question)
2. Remove anything unnecessary. (Refactor and delete unnecessary codes, Make PRs for this)
3. Simplify the approach. (Spawn Subagents, Save your Context)
4. Improve speed of feedback or execution.(Make Evaluator Script)
5. Only automate what is now stable. (Make Regression Test Code Which is Stable, Make PR for the Feature if is stable)

AUTO COMPACT if context is more than 35%

Spawn Subagents for Issues That are trivial, Use as much subagents as possible for the current Session

Current Session's context IS Very Valuable Resource

Try To find another Issue You cans Solve, 

Check Evaluator If the Evaluation Actually Solves the Problem

작업 진행도를 수치화 할 수 있는 부분(work evaluation) 을 평가하는 evaluator 는 현 작업 진행하면서 스크립트로 개발하면서 진행한다.

Try to Develop the script to evalaute the task progress if it is possible to measure. 

if it is not, then try to simplify(or abstract) the task until it is measurable.

현작업에 대한 진행도가 85% 되었다고 수치가 나오면 (스크립트 결과값이) 100%까지 마저 진행할지 아니면 판단하에 후속 이슈로 진행할지(남은 15% 채우는 작업이 너무 많을듯하다면) 결정하도록한다.

if the task progress which came out from the evaluator script is more than 85%, then you decide the task should be done until 100% or the task should stop and solve it in the future task, 

if it is possible to make the task progress to 100%, then finish this (within 5Hours) to solve the problem.

if this does not look so, estimate the remaining time to finish ( if the time spent for the task is more then 5 hour for making the progress 85%, then the estimate is likely more than 5 hour)

Task별 진행이 끝나면 elon-startegy-log.jsonl 에 append 로 작업 기록을 남겨줘


""".strip()

print(json.dumps({
    "decision": "block",
    "reason": continuation_prompt
}))
