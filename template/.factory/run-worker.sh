#!/usr/bin/env bash
#
# 起一個工人。**這一份是這座工廠自己的，腳手架不碰它。**
#
# 它存在的理由是「怎麼起一個工人」綁 harness 與機器，而那是會變的東西。
# 派工只負責決定「哪一份 skill、哪一號任務」，怎麼起包在這裡。
#
# 工具權限不在這裡決定 —— 那是架構層的規則，共用的，住在 .factory/tools.json。
# 這支腳本只負責把那張表翻譯成這個 harness 吃得懂的旗標。
#
# 用法：.factory/run-worker.sh <skill 名> <任務編號>
# 派工從 .factory/factory.json 的 worker.command 叫它。

set -euo pipefail

[[ $# -eq 2 ]] || { echo "用法：$0 <skill 名> <任務編號>" >&2; exit 1; }
skill=$1
task=$2

here=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
tools_file="$here/tools.json"
[[ -f $tools_file ]] || { echo "找不到 $tools_file。那張表定每一站拿得到哪些工具。" >&2; exit 1; }

# 允許清單沒列的就是沒有。查不到那一站就停下來，不要給一個寬鬆的預設值。
#
# 一行一個模式，不要用空白分隔 —— 模式本身含空白與括號，
# 例如 Bash(gh issue:*)。用空白分隔會被 shell 切開，然後整張清單失效。
mapfile -t allowed < <(python3 -c '
import json, sys
table, skill = sys.argv[1], sys.argv[2]
d = json.load(open(table, encoding="utf-8"))
station = d.get("stations", {}).get(skill)
if station is None:
    sys.exit(f"{skill} 不在 tools.json 的清單裡。沒有清單就不給工具。")
for pattern in station["allow"]:
    print(pattern)
' "$tools_file" "$skill")

[[ ${#allowed[@]} -gt 0 ]] || { echo "$skill 的允許清單是空的或查不到。停下來。" >&2; exit 1; }

exec claude -p "載入 $skill 這份 skill，然後用它處理任務 #$task。

照那份 skill 的硬規則做。它沒寫的事不要做。
做不到的時候停下來回報，不要找替代寫法繞過去。" \
  --allowedTools "${allowed[@]}" \
  --permission-mode acceptEdits \
  --output-format text
