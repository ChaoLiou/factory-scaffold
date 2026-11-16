#!/usr/bin/env bash
#
# 起一個工人。**這一份是這座工廠自己的，腳手架不碰它。**
#
# 它存在的理由是「怎麼起一個工人」綁 harness 與機器，而那是會變的東西。
# 派工只負責決定「哪一份 skill、哪一號任務」，怎麼起包在這裡。
#
# 用法：.factory/run-worker.sh <skill 名> <任務編號>
# 派工從 .factory/factory.json 的 worker.command 叫它。

set -euo pipefail

[[ $# -eq 2 ]] || { echo "用法：$0 <skill 名> <任務編號>" >&2; exit 1; }
skill=$1
task=$2

# 每一輪一個新 process。乾淨 session 不需要別的機制 ——
# 只要不把上一輪的任何東西傳進來就是乾淨的。
exec claude -p "載入 $skill 這份 skill，然後用它處理任務 #$task。

照那份 skill 的硬規則做。它沒寫的事不要做。
做不到的時候停下來回報，不要找替代寫法繞過去。" \
  --permission-mode acceptEdits \
  --output-format text
