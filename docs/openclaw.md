# OpenClaw 調查紀錄

**這份文件是紀錄，不是解法。** 它寫下查到的事實與還沒確認的事，不下結論，不提建議。

名詞照 `../CONTEXT.md`。查詢日期 2026-10-05。

---

## 1. OpenClaw 是什麼

OpenClaw 是一個開源、自架的 agent 閘道器（gateway）。作者是 Peter Steinberger。GitHub 上約 199k stars。

核心是一個 Node.js 的 Gateway process，預設跑在 `localhost:18789`。它做四件事：

1. 管理聊天頻道的連線
2. 把訊息路由到對應的 agent
3. 維護 session 狀態與對話歷史
4. 協調工具執行（檔案、shell、瀏覽器自動化）

一個 Gateway 後面可以跑多個 agent，每個 agent 有自己的工作區、模型與工具權限。

skill 與記憶存成純 Markdown 與 YAML，放在 `~/.openclaw/workspace`。檔案包含 `AGENTS.md`、`SOUL.md`、`IDENTITY.md`、`USER.md`、`MEMORY.md`。session 與逐字稿存在 SQLite。

支援的頻道（官方清單）：Discord、Google Chat、iMessage、Matrix、Microsoft Teams、Signal、Slack、Telegram、WhatsApp、Zalo。**清單裡沒有 LINE。**

---

## 2. 與四層架構的重疊

對照 `factory.md` 第 4 節：

| 我們寫的 | OpenClaw | 狀態 |
|---|---|---|
| 入口層 | 十種以上聊天頻道 | 已有 |
| 分派層 | Gateway router、Task flow、Lobster 工作流引擎 | 部分已有 |
| 執行層 | shell、檔案、瀏覽器自動化 | 已有 |
| 記憶層 | Markdown／YAML skill 與記憶，SQLite session | 已有 |
| 關卡 | 暫停工作流、送結構化核准請求到人的頻道、等幾小時或幾天 | 已有 |
| 24 小時 | cron、heartbeat、wakeup | 已有 |
| 回頭箭頭 | Lobster 可恢復、可暫停、可回滾 | 部分已有 |

---

## 3. 查到的硬限制

### 3.1 Lobster 不能分支，也不能迴圈

Lobster 是 OpenClaw 的工作流引擎。YAML DSL，副檔名 `.lobster`、`.yaml`、`.json`。

頂層欄位：`name`、`args`、`env`、`steps`。步驟欄位：`id`、`command`、`stdin`、`approval`、`condition`。

步驟之間用 `stdin: $step.stdout` 或 `stdin: $step.json` 傳資料。`condition: $approve.approved` 可以擋住後續步驟。

**文件明確說它不能分支、不能迴圈、不能執行任意程式碼。** 那是它確定性的來源。

**資料衝突：** 另一個來源說 Lobster 有 sub-workflow 步驟且支援 loop，有人貢獻了這一塊。兩邊說法不一致。要讀原始碼或原始文件確認。

### 3.2 Approval 只帶文字

Approval gate 回一個 `needs_approval` 的 JSON 加一個 `resumeToken`。prompt 欄位是文字。

有一個 `approve --preview-from-stdin --limit N` 可以附 JSON 預覽。

**文件沒有提到圖片或檔案附件。**

### 3.3 Gateway 重啟會中斷執行中的工作流

Checkpoint 存成檔案，放在 `~/.lobster/state`。resume token 只存指標，不存完整狀態。

執行中的工作流在 gateway 重啟時會停住。有 `resumeToken` 可以恢復，恢復的實際行為沒查到。

---

## 4. 還沒確認的事

1. Lobster 到底能不能迴圈。見 3.1 的資料衝突。
2. 瀏覽器自動化的實作是什麼。能不能錄影。Playwright 在不在工具箱裡。
3. 多個 agent 能不能共享工作區檔案。一個 agent 寫的白話規格，另一個 agent 讀不讀得到。
4. 關卡等待期間跨 gateway 重啟的可靠性。
5. 有沒有 LINE 頻道，或有沒有第三方的 LINE plugin。
6. 安裝的實際門檻。官方的個人助理設定建議一支專用電話號碼與 SIM，甚至兩支手機。

---

## 5. 未決的問題

這些還沒討論，先列著。

1. 這個專案要不要蓋在 OpenClaw 上。
2. 如果要，哪幾層不自己寫。
3. 如果 Lobster 表達不了產線，分派層自己寫要寫多厚。
4. 證據（錄影與截圖）要走哪一條路送到廠主眼前。
5. OpenClaw 自己往產線方向長的話，這個專案剩下什麼。
6. CloudClaw 這類托管平台把「民眾裝得起來」解掉的話，這個專案剩下什麼。

---

## 6. 管道調查的結論還有效的部分

查頻道限制那幾輪，有一半結論不受 OpenClaw 影響，因為它們是平台限制。

| | LINE | Telegram | Teams |
|---|---|---|---|
| 月額度 | 200 則 push（台灣免費方案） | 無 | 無 |
| 之後的費用 | NT$800／3,000 則 | 免費 | 免費，但要付主機 |
| 回覆訊息 | 免費，但 reply token 只有 1 分鐘 | — | — |
| 檔案托管 | 不托管，要自備公開 HTTPS 網址 | 自己托管，50 MB | 自己托管，100 MB × 10 |
| 影片 | 200 MB，查到 60 秒上限 | 50 MB，無長度上限 | 當附件 |
| 關卡 UI | Flex Message，30 KB | Inline keyboard，`callback_data` 64 bytes | Adaptive Cards，100 KB |
| 台灣民眾有裝 | 幾乎所有人 | 很少 | 很少 |

LINE 有一條結構性問題，不管誰寫 client 都存在：**工廠是非同步的，非同步只能用 push，push 計費。** reply token 的 1 分鐘有效期讓免費路線走不通，因為驗證站跑錄影要好幾分鐘。

四題打分表，用來評估任何新頻道：

1. 能不能非同步主動送訊息，而且不計費？
2. 送一段操作錄影，要不要自己架 host？
3. 從零到送出第一則訊息，要多久？
4. 目標廠主的裝置上已經裝了嗎？

前三題決定驗證假設的成本。第四題決定交付給廠主的成本。

---

## 7. 來源

- <https://docs.openclaw.ai/start/openclaw>
- <https://docs.openclaw.ai/tools/lobster>
- <https://docs.openclaw.ai/automation/taskflow>
- <https://clawdocs.org/guides/lobster-workflows>
- <https://github.com/amittell/openclaw-scheduler>
- <https://yowox.com/posts/openclaw-guide-ai-gateway/>
- <https://zedly.ai/blog/openclaw-human-approval-for-sensitive-actions>
- <https://developers.line.biz/en/reference/messaging-api/nojs/>
- <https://linebot.pro/blog/line-official-account-pricing-guide>
- <https://core.telegram.org/bots/api>
- <https://www.conferbot.com/limits/telegram>
- <https://www.conferbot.com/limits/teams>
- <https://learn.microsoft.com/en-us/microsoftteams/platform/concepts/bots/rate-limit>
