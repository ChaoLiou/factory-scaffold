#!/usr/bin/env python3
"""派工。讀標籤，決定下一個工人是誰。

這支程式是派工表唯一的機器可讀副本。表本身的規格在
腳手架的 docs/factory.md 5.5。改這裡要連那裡一起改。

它預設只印出「會派什麼」，不真的起工人。要真的派工得給
FAC_WORKER_CMD，而且加 --run。

用法：
    dispatch.py table                  印出派工表。不需要 GitHub
    dispatch.py plan   [<工廠目錄>]    問 GitHub，印出會派什麼
    dispatch.py run    [<工廠目錄>]    真的派。需要 FAC_WORKER_CMD
"""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

# 標籤 → 載入哪一份 skill。None 表示刻意不派工。
DISPATCH = {
    None: ("fac-intake", "任務身上還沒有 fac- 標籤"),
    "fac-triage": ("fac-triage", ""),
    "fac-needs-spec": ("fac-spec", "要連 specs/<feature>/spec.json 一起讀"),
    "fac-ready": ("fac-implement", "跑在隔離的 worktree"),
    "fac-in-pr": ("fac-review", "跑在乾淨 session"),
    "fac-review-clean": ("fac-verify", ""),
    "fac-review-flagged": ("fac-verify", ""),
    "fac-needs-info": (None, "等廠主補資訊"),
    "fac-needs-decision": (None, "等廠主決定"),
    "fac-evidence": (None, "等廠主看證據，然後合併或退回"),
    "fac-wont-do": (None, "等廠主關掉任務"),
}

# 不由標籤觸發的三個。
NOT_BY_LABEL = [
    ("廠主合併了 PR", "fac-ship", "唯一有部署權限的那一個"),
    ("排程。每輪", "fac-monitor", "不是這支程式的事。用 cron"),
    ("排程。每週", "fac-improve-*", "同上"),
]

KIND_LABELS = {"fac-kind-bug", "fac-kind-feature", "fac-kind-copy", "fac-kind-chore"}
STATE_FILE = ".factory/dispatch-state.json"


def die(msg):
    raise SystemExit(msg)


def print_table():
    print("標籤 → skill\n")
    for label, (skill, note) in DISPATCH.items():
        name = label or "（沒有 fac- 標籤）"
        if skill is None:
            print(f"  {name:22} 不派工。{note}")
        else:
            print(f"  {name:22} {skill:14} {note}")
    print("\n不由標籤觸發：\n")
    for trigger, skill, note in NOT_BY_LABEL:
        print(f"  {trigger:22} {skill:14} {note}")
    print("\n那四個不派工的標籤就是關卡的實作。人不出手，任務就不動。")


def gh(args, cwd):
    if not shutil.which("gh"):
        die("需要 gh。沒有它就問不到標籤。")
    done = subprocess.run(
        ["gh", *args], cwd=cwd, capture_output=True, text=True
    )
    if done.returncode != 0:
        die(f"gh {' '.join(args)} 失敗：\n{done.stderr.strip()}")
    return json.loads(done.stdout or "[]")


def status_label(labels):
    """一筆任務同時只准帶一個狀態標籤。兩個就停下來。"""
    found = [
        n
        for n in labels
        if n.startswith("fac-") and n not in KIND_LABELS and n in DISPATCH
    ]
    if len(found) > 1:
        return "衝突:" + ",".join(sorted(found))
    return found[0] if found else None


def plan(factory: Path):
    issues = gh(
        ["issue", "list", "--state", "open", "--limit", "200",
         "--json", "number,title,labels"],
        factory,
    )
    jobs = []
    for issue in issues:
        label = status_label([l["name"] for l in issue["labels"]])
        if label and label.startswith("衝突:"):
            jobs.append((issue["number"], label, None, "兩個狀態標籤。停下來，不要猜"))
            continue
        skill, note = DISPATCH[label]
        jobs.append((issue["number"], label or "（沒有）", skill, note))
    return jobs


def load_state(factory: Path):
    path = factory / STATE_FILE
    if path.is_file():
        return json.loads(path.read_text(encoding="utf-8"))
    return {}


def save_state(factory: Path, state):
    path = factory / STATE_FILE
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def main(argv):
    if len(argv) < 2 or argv[1] not in {"table", "plan", "run"}:
        die(__doc__)
    action = argv[1]
    if action == "table":
        print_table()
        return 0

    factory = Path(argv[2] if len(argv) > 2 else ".").resolve()
    if not (factory / ".factory" / "manifest.json").is_file():
        die(f"{factory} 不是一座工廠。找不到 .factory/manifest.json")

    jobs = plan(factory)
    if not jobs:
        print("沒有開著的任務。")
        return 0

    state = load_state(factory)
    worker = os.environ.get("FAC_WORKER_CMD")

    for number, label, skill, note in jobs:
        key = f"{number}:{label}"
        if skill is None:
            print(f"#{number:<5} {label:22} 不派工。{note}")
            continue
        if state.get(key):
            print(f"#{number:<5} {label:22} 已經派過了，跳過。{skill}")
            continue
        print(f"#{number:<5} {label:22} → {skill}  {note}")
        if action != "run":
            continue
        if not worker:
            die("要真的派工就給 FAC_WORKER_CMD，例如：\n"
                "  FAC_WORKER_CMD='claude -p' scripts/dispatch.py run <工廠目錄>\n"
                "怎麼起一個工人是會變的東西，所以它不寫死在這裡。")
        # 起工人之前先記，不是之後。起到一半掛掉也不會被派第二次 ——
        # 開 PR、貼評論、部署都有副作用。見 docs/factory.md 5.5.4。
        state[key] = {"skill": skill, "dispatched": True}
        save_state(factory, state)
        subprocess.run([*worker.split(), skill, str(number)], cwd=factory, check=False)

    if action != "run":
        print("\n這是 plan。要真的派工加 run，而且給 FAC_WORKER_CMD。")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
