#!/usr/bin/env python3
"""派工。讀標籤，決定下一個工人是誰。

這一份由腳手架維護。不要改 —— 改了升級會停下來回報。
要改走外迴圈：產出一個對腳手架的 PR。


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
    ("帳本上一列是上一輪", "fac-monitor", "從帳本算，不用排程器"),
    ("帳本上一列超過門檻天數", "fac-improve-*", "同上。門檻在 factory.json"),
]

KIND_LABELS = {"fac-kind-bug", "fac-kind-feature", "fac-kind-copy", "fac-kind-chore"}
STATE_FILE = ".factory/dispatch-state.json"
FACTORY_FILE = ".factory/factory.json"
LEDGER = "docs/factory-log.md"

# 要在隔離的 worktree 裡跑的站。
NEEDS_WORKTREE = {"fac-implement"}


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


def load_factory(factory: Path):
    """讀工廠宣告。缺了就停下來，不要猜。"""
    path = factory / FACTORY_FILE
    if not path.is_file():
        die(f"找不到 {FACTORY_FILE}。那一份宣告「這座工廠怎麼跑」，少了它派不了工。")
    d = json.loads(path.read_text(encoding="utf-8"))
    cmd = (d.get("worker") or {}).get("command") or ""
    if not cmd or cmd.startswith("{{"):
        die("factory.json 的 worker.command 還沒填。\n"
            "建廠第 4 站該填它。見腳手架的 docs/factory-setup.md 第 3 節的驗收清單。")
    return d


def worker_argv(template: str, skill: str, task: int):
    """把宣告裡的指令樣板展開。{skill} 與 {task} 是它的兩個洞。"""
    if "{skill}" not in template:
        die("worker.command 裡沒有 {skill}。那樣起來的工人不知道自己是哪一站。")
    return [
        part.replace("{skill}", skill).replace("{task}", str(task))
        for part in template.split()
    ]


def ledger_last_day(factory: Path):
    """工廠帳本最後一列的日期。排程不是服務，帳本就是那個時鐘。"""
    path = factory / LEDGER
    if not path.is_file():
        return None
    import re
    days = re.findall(r"\b(20\d\d-\d\d-\d\d)\b", path.read_text(encoding="utf-8"))
    return max(days) if days else None


def due(factory: Path, conf):
    """該不該跑監控與外迴圈。算出來的，不是排程器叫的。"""
    from datetime import date
    last = ledger_last_day(factory)
    every = (conf.get("dispatch") or {}).get("improve_every_days", 7)
    if last is None:
        return ["監控（帳本還是空的，所以第一輪就該跑）"]
    gap = (date.today() - date.fromisoformat(last)).days
    out = []
    if gap >= 1:
        out.append(f"監控（帳本最後一列是 {last}，{gap} 天前）")
    if gap >= every:
        out.append(f"外迴圈（距今 {gap} 天，門檻 {every}）")
    return out


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


def make_worktree(factory: Path, conf, number: int) -> Path:
    """實作站跑在隔離的 worktree。派工建，跑完移除。"""
    root = (conf.get("isolation") or {}).get("worktree_root") or ""
    if not root or root.startswith("{{"):
        die("factory.json 的 isolation.worktree_root 還沒填。"
            "實作站要隔離的 worktree，不然它污染工作目錄。")
    base = (factory / root).resolve()
    base.mkdir(parents=True, exist_ok=True)
    tree = base / f"task-{number}"
    if tree.exists():
        die(f"{tree} 已經在了。前一輪沒清乾淨，先看一眼再決定，不要蓋掉。")
    branch = f"task/{number}"
    subprocess.run(
        ["git", "worktree", "add", "-b", branch, str(tree)],
        cwd=factory, check=True, capture_output=True, text=True,
    )
    return tree


def drop_worktree(factory: Path, tree: Path):
    subprocess.run(["git", "worktree", "remove", "--force", str(tree)],
                   cwd=factory, check=False, capture_output=True)


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

    conf = load_factory(factory)
    jobs = plan(factory)

    for line in due(factory, conf):
        print(f"排程   {line}")

    if not jobs:
        print("沒有開著的任務。")
        return 0

    state = load_state(factory)
    worker = os.environ.get("FAC_WORKER_CMD") or conf["worker"]["command"]

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
        argv = worker_argv(worker, skill, number)
        cwd = factory
        tree = None
        if skill in NEEDS_WORKTREE:
            tree = make_worktree(factory, conf, number)
            cwd = tree
            print(f"       worktree {tree}")
        # 起工人之前先記，不是之後。起到一半掛掉也不會被派第二次 ——
        # 開 PR、貼評論、部署都有副作用。見 docs/factory.md 5.5.4。
        state[key] = {"skill": skill, "dispatched": True}
        save_state(factory, state)
        try:
            subprocess.run(argv, cwd=cwd, check=False)
        finally:
            if tree and (conf.get("isolation") or {}).get("remove_after", True):
                drop_worktree(factory, tree)

    if action != "run":
        print("\n這是 plan。要真的派工加 run，而且給 FAC_WORKER_CMD。")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
