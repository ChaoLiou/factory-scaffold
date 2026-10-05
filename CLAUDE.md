# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## 先讀 CONTEXT.md

`CONTEXT.md` 是這個專案的名詞表，而且是強制的。

寫這個 repo 的任何文件、技能檔、程式碼註解、commit 訊息之前，先讀它。規則：

1. 只用表上的詞。
2. 用表上定義的詞性與意思。
3. 不要替換成同義詞。
4. 不要在行文中重新定義表上的詞。要改定義就改那份表。
5. `_避免_` 列出的詞不要用。

加新詞時連同 `_避免_` 一起寫。

文件用繁體中文，句子短。中文字後面用全形逗號。

## 資安規則往上推

一條規則能放在**架構層**就不要放 CI 層，能放 CI 層就不要放 rules 層。四層強度遞減：架構 > CI／靜態分析 > rules > 技能檔。

理由：民眾不審 code，所以不會發現資料外洩 —— 它不出現在錄影裡。下兩層依賴 agent 記得，而 agent 會忘。

第一條架構規則是**前端不持有任何可以直接存取資料的憑證**。寫任何碰資料的程式碼之前先讀 `docs/security.md` 第 3 節。

---

## 這個 repo 是什麼

**這個 repo 是腳手架。它不是工廠，也不是產品。**

三層產出，依序：

1. **腳手架** = 這個 repo。產出是工廠。
2. **工廠** = 交付給廠主的東西。產出是產品。
3. **產品** = 廠主真正想要的那個網站或服務。

這三層最容易被講混，而且混了之後整段討論會失準。寫任何句子之前先確認你在講哪一層。

工廠產生到隔壁目錄，**不在這個 repo 裡**。這個 repo 只有腳手架與範本。

### 兩份 CLAUDE.md

- 本檔 — 給在腳手架裡工作的 Claude。
- `template/CLAUDE.md` — 給在工廠裡工作的 Claude。範本的一部分。

這兩份很容易寫混。改之前先確認你改的是哪一份。

---

## 目前沒有程式碼

這個 repo 現在只有文件。沒有 `package.json`、沒有建置、沒有測試、沒有 lint。

所以沒有 build、test、lint 指令可以跑。不要編一個。

程式碼出現之後，第一批會是 `template/` 底下的技能檔與 `scripts/` 的派工腳本。那時這一節要改寫。

---

## 文件地圖

| 檔案 | 內容 |
|---|---|
| `CONTEXT.md` | 名詞表。強制。先讀 |
| `docs/factory.md` | **產品產線**：四個元件、四層架構、八站、層級、自我改善、量測 |
| `docs/factory-setup.md` | **建廠產線**：七站、四題問需求、技術棧對照表、驗收標準 |
| `docs/product-contract.md` | 產品合約的三項要求，以及合約不管什麼 |
| `docs/security.md` | 四層防線的排序，以及五條架構層規則 |
| `docs/codeshore.md` | CodeShore 的調查紀錄。**最重要的外部參考** |
| `docs/openclaw.md` | OpenClaw 的調查紀錄，含聊天管道的平台限制 |

兩份調查紀錄（`codeshore.md`、`openclaw.md`）開頭都寫明「是紀錄，不是解法」。不要把它們當成已經決定的事。

**有兩條產線，意思完全不同。** 建廠產線是腳手架產生工廠，七站。產品產線是工廠產生產品，八站。不要單寫「產線」。

---

## 已經決定的事

決定日期 2026-10-05。

| 決定 | 理由 |
|---|---|
| 第一座工廠的廠主是 **L3 工程師** | L1 要「審 code 完全不需要人」，是最難的一塊，而且修正訊號的假設還沒驗證 |
| 第一個實驗**新建一座工廠**，不改 CodeShore | CodeShore 的工廠跟它的產品纏在一起。在乾淨的地方重建比從纏繞的地方拆更清楚 |
| 產線的第一站是**驗證站** | 廠主最大的恐懼是「我不知道它做對了沒」。沒有證據，整座工廠不可信 |
| 驗證站第一版只做**證據產生器**，不做判定者 | 不決定任何事的站，判錯成本趨近於零。守住「從最可逆的那一站開始」 |
| 第一個產品是**廠主真的想要的小產品** | 廠主會真的在意產出對不對。那是這個選項唯一的價值 |
| 建廠本身是一條**產線**，不是複製指令 | 它有站、有關卡、有回頭箭頭、需要證據、失敗可以學 |
| 建廠產線第二站**問需求，不問技術** | 廠主答得出「手機桌面點圖示」，答不出「React Native」 |
| 五種產品型態用**三套技術棧** | 一份技能檔要服務所有工廠。技術棧越少，改善越快 |
| 廠主說「我要 APP」預設給 **PWA** | 不過審核、不建兩包、不要 macOS，而且合約三項完全不用改 |
| 要求二走**共用一個資料庫，每輪重置** | 免費。接受並行污染，因為第一座工廠只有一個廠主 |
| **前端不持有任何憑證** | 民眾不審 code，所以不會發現資料外洩。資安靠架構擋，不靠關卡擋 |
| 只准 **PKCE flow**，session 存 HttpOnly cookie | token 進 `localStorage` 會被 XSS 偷走 |
| 接受**沒有 Realtime 訂閱** | 它需要前端持有 token。那與上一條衝突 |
| 預覽與生產是**不同專案、不同帳號** | 同一個專案不同環境變數是 rules 層，agent 會寫錯 |
| 聊天管道**先不做** | 入口層的決定依賴廠主層級。L3 不需要聊天入口 |

---

## 還沒決定的事

1. **第一座工廠要生產什麼產品。** 阻塞中。廠主要說那個小產品是什麼。
2. 這個專案要不要蓋在 OpenClaw 上。見 `docs/openclaw.md` 第 5 節。
3. 合約宣告的檔案格式與欄位名稱。見 `docs/product-contract.md` 第 7 節。
4. 建廠產線第 3 到第 5 站的實際指令。見 `docs/factory-setup.md` 第 7 節。
5. 層級要怎麼加進一個本來假設廠主是工程師的產品產線。
6. 影像證據與文字證據是取代關係還是並存關係。
7. 腳手架自己的帳本檔名與格式。見 `docs/factory-setup.md` 第 6 節。
8. 驗證站要不要包含資安驗證，以及它是關卡還是只是資訊。
9. 產品會不會存別人的資料。會的話進入個資範圍。
10. 廠主自己的帳號安全。見 `docs/security.md` 第 6 節。
11. 責任歸屬。民眾三句話做出一個收集客戶電話的網站，責任是誰的。

---

## 外部參考

### CodeShore

`/home/chaol/CodeShore`

一座**已經在跑**的 L3 工廠。它的 `docs/factory-flow.mmd` 出自同一場演講，而且已經跑過真實任務，有 `docs/pacer-log.md` 當帳本。

**產線的設計以 CodeShore 為底，不要從演講重推。** 它經過實作了，演講沒有。

跟產品無關、可以搬的：`kiro-review`、`kiro-debug`、`kiro-verify-completion`、`orca-pr-review` 的判準、`orca-retro` 的五種訊號、`pacer-log` 的漏記查核與四層防線、`orca-issue-work` 的硬規則、label 當狀態機、`git worktree` 隔離。

搬不走的：`.kiro/steering/` 的內容、Orca 瀏覽器圈選入口、`intake.yml` 的四格。

細節見 `docs/codeshore.md`。

### 演講解析

`/home/chaol/TheWayToLearn/workspace/Software Engineering Is Becoming Factory Engineering — Zach Lloyd, Warp/`

工廠模型的原始出處。本機已有逐段中文解析，不必重看影片。

查特定主題時用 `python3` 讀 `analysis.json` 的 `segments`（每段有 `reasoning` 與 `explanation`），不要整檔讀入。`_overview.json` 與 `notes.json` 是摘要。

---

## 計畫中的結構

還沒建。建的時候照這個形狀：

```
chaol/
  CONTEXT.md
  CLAUDE.md                 本檔
  docs/
  template/                 工廠範本。腳手架的產出就是它的複製品
    CLAUDE.md               工廠自己的操作手冊
    .claude/skills/         八站加外迴圈的技能檔
    config/
      contract.yaml         合約宣告
      allowance.yaml        容許清單
    scripts/                派工、審查派工、清理 worktree
  scripts/
    new-factory.sh          產生一座工廠

../<工廠名>/                 產生出來的工廠，在隔壁
```

產品產線八站依序是：入口、分辨、規格、實作、審查、驗證、上線、監控。

建廠產線七站依序是：問清產品、定產品型態、開 repo、接合約、寫合約宣告、驗收、交付。

**第一版只蓋驗證站。** 不要一次把八站都寫出來。

驗證站同時是建廠產線的量規：驗收的標準就是它跑得出證據。所以它不是「八站裡先蓋哪一站」的偏好，它是建廠的必要條件。
