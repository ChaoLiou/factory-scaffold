# 規格格式

這份文件定義規格的格式。名詞一律照 `../CONTEXT.md`。

格式大部分從 CodeShore 搬來。它已經跑過真實任務，不要重新發明。見第 7 節。

---

## 1. 兩個層級

規格有兩個層級，不要混。

| 層級 | 描述什麼 | 檔案 | 變更頻率 |
|---|---|---|---|
| **產品層級** | 整個產品是什麼 | `SPEC.md`、`docs/tech-spec.md` | 很低 |
| **功能層級** | 一個功能怎麼做 | `specs/<feature>/` | 一個功能一份 |

產品層級由**建廠產線第 1 站**產出。範本在 `../template/`。

功能層級由**產品產線的規格站**產出。格式見下。

---

## 2. 功能層級的四個檔案

```
specs/<feature>/
  spec.json        狀態與三道核准
  requirements.md  要達成什麼
  design.md        怎麼做
  tasks.md         做哪些事
```

三道核准依序：requirements → design → tasks。**每一道都是關卡。**

一次只推進一道。前一道沒核准，不要產出下一道。

---

## 3. spec.json

```json
{
  "feature_name": "<feature>",
  "language": "zh-TW",
  "created_at": "<ISO 8601>",
  "updated_at": "<ISO 8601>",
  "phase": "initialized",
  "approvals": {
    "requirements": { "generated": false, "approved": false },
    "design":       { "generated": false, "approved": false },
    "tasks":        { "generated": false, "approved": false }
  }
}
```

`phase` 的值依序：`initialized` → `requirements-generated` → `design-generated` → `tasks-generated` → `implementing` → `done`。

`approvals` 是關卡的狀態機。`generated` 由 agent 設，**`approved` 只有廠主能設。**

---

## 4. requirements.md

```markdown
# 需求文件 — <feature>

## 專案描述
<一到三段。為什麼要做這件事，以及要達成什麼。>

## 範圍界定

**本次範圍包含：**
- <一條一行>

**本次範圍不包含（相鄰但不擁有）：**
- <那個東西>：<為什麼不做>

## Requirement 1: <標題>

**User Story:** 身為<角色>，我希望<能力>，以便<目的>。

#### Acceptance Criteria

1. The <主體> shall <行為>。
2. When <條件>, the <主體> shall <行為>。
3. If <條件>, then the <主體> shall <行為>。
```

### 4.1 「不包含」那一節要寫理由

寫「相鄰但不擁有」的東西，並說明為什麼不做。

這一節防止範圍蔓延，而且它是實作站的禁區 —— `fac-implement` 的硬規則是「只做 issue 寫明的事」。

### 4.2 驗收條件用 EARS 格式

三種句型，就這三種：

| 句型 | 什麼時候用 |
|---|---|
| `The X shall Y` | 永遠成立的性質 |
| `When A, the X shall Y` | 事件觸發的行為 |
| `If A, then the X shall Y` | 條件成立時的行為 |

EARS 的價值是**句型固定，所以讀得出來驗不驗得了**。寫不進這三種句型的，通常是願望，不是驗收條件。

一條驗收條件只講一件事。要用「並且」就拆成兩條。

---

## 5. design.md

十二節，依序：

| | 節 | 內容 |
|---|---|---|
| 1 | Overview | 一段。要改什麼 |
| 2 | Goals / Non-Goals | 做與不做 |
| 3 | **Boundary Commitments** | 這次改動切成哪幾塊。見 5.1 |
| 4 | Architecture | 架構 |
| 5 | File Structure Plan | 哪些檔案會被改或新增 |
| 6 | Components & Interfaces | 每塊的介面。見 5.2 |
| 7 | Data Models | 資料模型 |
| 8 | System Flows | 流程 |
| 9 | Testing Strategy | 怎麼驗 |
| 10 | Integration & Migration Notes | 上線順序 |
| 11 | Open Questions / Risks | 還沒決定的、有風險的 |
| 12 | **Requirements Traceability** | 每條需求對到哪一塊。見 5.3 |

### 5.1 Boundary Commitments

把這次改動切成幾塊，每塊是一個可以獨立完成的單位。

它的用途在 `tasks.md`：每個任務標 `_Boundary: X_`，然後一個 Boundary 可以拆成一張子 issue。沒有 Boundary，大功能就拆不成能派工的任務。

### 5.2 Full Block 與 Summary Only

第 6 節的每一塊標一個深度：

- **Full Block** —— 介面、型別、邊界條件都寫清楚。
- **Summary Only** —— 一段話說明意圖就好。

哪些要 Full Block：碰到資料、碰到授權、碰到金流、有多種做法的。其他 Summary Only。

**不要全部寫 Full Block。** 那會把設計寫成實作，而且審的人讀不完。

### 5.3 Requirements Traceability

一張表，把第 4 節的每條驗收條件對到第 6 節的某一塊。

對不到的驗收條件表示設計漏了。對不到的塊表示在做沒人要的東西。

---

## 6. tasks.md

```markdown
# 實作任務 — <feature>

- [ ] 1. <Boundary 名稱或階段名稱>
- [ ] 1.1 <任務標題>
  - <要做的事，一條一行>
  - 可觀察完成狀態：<做完之後，從外面看得到什麼>
  - _Requirements: 1.1, 1.2_
  - _Boundary: <Boundary 名稱>_
```

### 6.1 可觀察完成狀態

**這一行是最重要的。**

它寫「做完之後，從外面看得到什麼」。不是「寫好了」，是一個可以被檢查的狀態。

好的例子：「migration 檔案內容包含 rename、add column、逐列 backfill 三個步驟，且新欄位設定 NOT NULL 的順序在 backfill 之後。」

壞的例子：「migration 寫好了。」—— 檢查不了。

它是 `fac-verify-completion` 的輸入。沒有它，「做完了」只是 agent 的自述。

### 6.2 兩個標籤

- `_Requirements: 1.1, 1.2_` —— 這個任務滿足哪幾條驗收條件。接回 `requirements.md`。
- `_Boundary: X_` —— 這個任務屬於哪一塊。接回 `design.md` 第 3 節，用來拆子 issue。

兩個標籤都要寫。它們讓三份文件互相咬住。

### 6.3 偏離原計畫要寫在任務裡

實作跟設計不一樣的時候，在那個任務底下寫一行 `_偏離原計畫：<發生什麼、改成怎麼做>_`。

不要去改 `design.md` 假裝當初就這樣想。

這一行是外迴圈的訊號來源 —— 一直偏離同一個地方，表示規格站的技能檔漏了什麼。

---

## 7. 來源

格式出自 CodeShore 的 `.kiro/`：

- `spec.json` 的 `approvals` 狀態機
- `requirements.md` 的範圍界定與 EARS 驗收條件
- `design.md` 的十二節，含 Boundary Commitments、Full Block／Summary Only、Requirements Traceability
- `tasks.md` 的可觀察完成狀態、兩個標籤、偏離原計畫

路徑 `/home/chaol/CodeShore/.kiro/`。範例在 `specs/job-timestamp-separation/`。

本專案自己加的只有兩項：

1. 第 1 節的兩個層級切分。CodeShore 只有功能層級加 steering，沒有明確的「產品層級規格」。
2. 5.2 的「不要全部寫 Full Block」那條警告。
