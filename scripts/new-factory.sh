#!/usr/bin/env bash
#
# 從範本產生一座工廠。它只做建廠產線第 2 站的機械部分。
#
# 它填得出來的只有三個佔位符：腳手架版本、腳手架 commit、時間戳。
# 其餘佔位符留著，由第 1 到第 4 站問廠主。腳手架不替廠主猜答案。
#
# 用法：scripts/new-factory.sh <工廠名>
# 產生到 ../<工廠名>/，不在這個 repo 裡。

set -euo pipefail

die() { printf '%s\n' "$*" >&2; exit 1; }

[[ $# -eq 1 ]] || die "用法：scripts/new-factory.sh <工廠名>"
name=$1
[[ $name =~ ^[a-z0-9][a-z0-9-]*$ ]] || die "工廠名只能用小寫、數字與連字號：$name"

here=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
template="$here/template"
target="$(dirname -- "$here")/$name"

[[ -d $template ]] || die "找不到範本：$template"
[[ -e $target ]] && die "$target 已經存在。這一步有副作用，所以它不覆蓋，直接停。"

command -v git >/dev/null || die "需要 git"
command -v python3 >/dev/null || die "需要 python3"

version=$(git -C "$here" describe --tags --always --dirty 2>/dev/null || echo unknown)
commit=$(git -C "$here" rev-parse HEAD 2>/dev/null || echo unknown)
stamp=$(date -u +%Y-%m-%dT%H:%M:%SZ)
[[ $version == *-dirty ]] && printf '提醒：腳手架有未 commit 的改動，版本記成 %s\n' "$version"

printf '產生 %s\n' "$target"
cp -R -- "$template" "$target"

# 只替換這三個。其餘佔位符是廠主要答的，留著。
python3 - "$target" "$version" "$commit" "$stamp" <<'PY'
import pathlib, sys
root, version, commit, stamp = pathlib.Path(sys.argv[1]), *sys.argv[2:]
subs = {
    "{{SCAFFOLD_VERSION}}": version,
    "{{SCAFFOLD_COMMIT}}": commit,
    "{{TIMESTAMP}}": stamp,
}
for path in root.rglob("*"):
    if not path.is_file() or path.suffix not in {".md", ".json"}:
        continue
    text = path.read_text(encoding="utf-8")
    new = text
    for old, value in subs.items():
        new = new.replace(old, value)
    if new != text:
        path.write_text(new, encoding="utf-8")
PY

python3 "$here/scripts/shared-hashes.py" write "$target"

git -C "$target" init -q
git -C "$target" add -A
git -C "$target" -c user.useConfigOnly=false commit -q -m "從腳手架 $version 建廠" || die "第一個 commit 失敗"

printf '\n工廠建好了，但它還不會動。剩下的事：\n\n'

printf '第 1 站 定產品型態。問廠主，然後填 SPEC.md\n'
printf '第 2 站 開 repo。這支腳本只做了本地的 git init。還缺：\n'
printf '        gh repo create、標籤、分支保護、CI 骨架\n'
printf '        標籤清單見腳手架的 docs/factory.md 5.3。名稱定死，不要改\n'
printf '第 3 站 接合約。挑平台之前先對五條，見 docs/factory-setup.md 4.2.4.1\n'
printf '第 4 站 寫合約宣告。填 .factory/contract.json\n'
printf '第 5 站 驗收。跑一次驗證站。標準只有一條：它跑得出證據\n\n'

printf '還沒填的佔位符：\n'
grep -rho '{{[A-Z0-9_]*}}' "$target" | sort | uniq -c | sort -rn | sed 's/^/  /'
