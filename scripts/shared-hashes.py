#!/usr/bin/env python3
"""共用檔案的雜湊。建廠時寫進 manifest，升級時拿來比對。

哪些檔案算共用、算到哪裡，是規則：

1. `.claude/skills/fac-*/SKILL.md` → **整個檔案**。它們整檔都是腳手架的，
   升級時整批換。只算標記之間的話，標記外面加的東西會躲過比對。
2. `.factory/security.md` 與 `.factory/dispatch.py` → 整個檔案。腳手架出的，工廠不改。
3. 其餘有 `<!-- fac:shared:start -->` 的 → 只算那對標記之間（region）。
   那是混合檔案：`CLAUDE.md` 與 `CONTEXT.md` 一個檔案裡兩層，
   標記外面本來就是那座工廠自己的。

所以新增一份共用 skill 不必改這支程式。

用法：
    shared-hashes.py list    <根目錄>   列出哪些算共用
    shared-hashes.py compute <根目錄>   印出雜湊表
    shared-hashes.py write   <工廠目錄> 寫進那座工廠的 manifest
    shared-hashes.py verify  <工廠目錄> 比對。不符就 exit 1
"""

import hashlib
import json
import sys
from pathlib import Path

START = "<!-- fac:shared:start -->"
END = "<!-- fac:shared:end -->"
WHOLE_FILE = [".factory/security.md", ".factory/dispatch.py"]
SKIP_DIRS = {".git", "node_modules", ".factory/evidence"}


def _is_shared_skill(rel: str) -> bool:
    """共用 skill：.claude/skills/fac-<名>/SKILL.md。整檔都是腳手架的。"""
    parts = rel.split("/")
    return (
        len(parts) == 4
        and parts[0] == ".claude"
        and parts[1] == "skills"
        and parts[2].startswith("fac-")
        and parts[3] == "SKILL.md"
    )


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8").replace("\r\n", "\n")


def shared_paths(root: Path):
    """回傳 [(相對路徑, mode)]，照路徑排序。"""
    found = {}
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(root).as_posix()
        if any(rel == d or rel.startswith(d + "/") for d in SKIP_DIRS):
            continue
        if rel in WHOLE_FILE or _is_shared_skill(rel):
            found[rel] = "file"
            continue
        if path.suffix not in {".md", ".json", ".sh", ".py"}:
            continue
        try:
            if START in _read(path):
                found[rel] = "region"
        except UnicodeDecodeError:
            continue
    return sorted(found.items())


def region(text: str, rel: str) -> str:
    """標記之間的內容。一個檔案只准有一對標記。"""
    if text.count(START) != 1 or text.count(END) != 1:
        raise SystemExit(f"{rel}：界線標記不是剛好一對。停下來，不要猜。")
    body = text.split(START, 1)[1].split(END, 1)[0]
    return body.strip("\n") + "\n"


def digest(root: Path, rel: str, mode: str) -> str:
    text = _read(root / rel)
    payload = text if mode == "file" else region(text, rel)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def compute(root: Path) -> dict:
    return {
        rel: {"mode": mode, "sha256": digest(root, rel, mode)}
        for rel, mode in shared_paths(root)
    }


def _manifest(factory: Path) -> Path:
    path = factory / ".factory" / "manifest.json"
    if not path.is_file():
        raise SystemExit(f"找不到 {path}。這不是一座工廠。")
    return path


def main(argv):
    if len(argv) != 3 or argv[1] not in {"list", "compute", "write", "verify"}:
        raise SystemExit(__doc__)
    action, root = argv[1], Path(argv[2]).resolve()
    if not root.is_dir():
        raise SystemExit(f"找不到目錄 {root}")

    if action == "list":
        for rel, mode in shared_paths(root):
            print(f"{mode:6} {rel}")
        return 0

    if action == "compute":
        print(json.dumps(compute(root), ensure_ascii=False, indent=2))
        return 0

    path = _manifest(root)
    data = json.loads(path.read_text(encoding="utf-8"))

    if action == "write":
        data["shared"] = compute(root)
        path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        print(f"寫進 {path.relative_to(root)}：{len(data['shared'])} 筆")
        return 0

    recorded = data.get("shared") or {}
    if not recorded:
        raise SystemExit("manifest 的 shared 是空的。那座工廠建的時候沒有寫雜湊。")
    now = compute(root)
    bad = []
    for rel in sorted(set(recorded) | set(now)):
        was, is_ = recorded.get(rel), now.get(rel)
        if was is None:
            bad.append(f"多出來  {rel}")
        elif is_ is None:
            bad.append(f"不見了  {rel}")
        elif was["sha256"] != is_["sha256"]:
            bad.append(f"被改過  {rel}")
    if bad:
        print("共用檔案與 manifest 不符：", *bad, sep="\n  ")
        print("\n升級要停下來回報。見 skills-layering.md 6.1。")
        return 1
    print(f"共用檔案 {len(now)} 筆全部相符。")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
