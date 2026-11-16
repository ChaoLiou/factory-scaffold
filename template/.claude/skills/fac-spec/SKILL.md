---
name: fac-spec
description: 規格站。把一筆複雜任務寫成功能層級規格：requirements、design、tasks 三份，三道核准各自是一個關卡。簡單任務不進這一站。帶 fac-needs-spec 標籤的任務用它。
---

# 規格站

這一站把一筆複雜任務寫成規格。

**三道核准依序推進。一次只推一道。** 每一道都是關卡。

<!-- fac:shared:start -->
<!-- 這一份由腳手架維護。不要改。改了升級會停下來回報。 -->

## 0. 先讀

| 讀什麼 | 拿什麼 |
|---|---|
| `CONTEXT.md` 的「工廠運作」那一節 | 名詞 |
| 這筆任務的內文 | 廠主要什麼 |
| `SPEC.md` | 不變量、核心能力、不做的事 |
| `docs/tech-spec.md` | 架構規則與目前的形狀 |
| `.factory/security.md` 第 3 節 | 碰資料之前 |

## 1. 邊界

| 做 | 不做 |
|---|---|
| 寫 `requirements.md`、`design.md`、`tasks.md` | 寫 code |
| 把需求對到設計 | 自己設 `approved` |
| 標出還沒決定的事 | 一次產出三份 |
| 拆出可以派工的任務 | 改 `SPEC.md` 的不變量 |

**`approved` 只有廠主能設。** 你只設 `generated`。

改不變量是產品決定。要改就另開一筆任務。

## 2. 產出的四個檔案

```
specs/<feature>/
  spec.json        狀態與三道核准
  requirements.md  要達成什麼
  design.md        怎麼做
  tasks.md         做哪些事
```

`spec.json`：

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

`phase` 依序：`initialized` → `requirements-generated` → `design-generated` → `tasks-generated` → `implementing` → `done`。

## 3. 第一道：requirements.md

```markdown
# 需求文件 — <feature>

## 專案描述
<一到三段。為什麼要做，以及要達成什麼>

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

### 3.1 驗收條件只有三種句型

| 句型 | 什麼時候用 |
|---|---|
| `The X shall Y` | 永遠成立的性質 |
| `When A, the X shall Y` | 事件觸發的行為 |
| `If A, then the X shall Y` | 條件成立時的行為 |

**寫不進這三種句型的，通常是願望，不是驗收條件。**

一條驗收條件只講一件事。要用「並且」就拆成兩條。

### 3.2 「不包含」那一節要寫理由

它防止範圍蔓延，而且它是實作站的禁區 —— `fac-implement` 只做寫明的事。

沒有理由的那一條，下一輪沒有人敢守。

### 3.3 驗收條件與不變量的關係

不變量在 `SPEC.md`，很少變。驗收條件在這裡，一個功能一組。

| | 哪裡 | 誰驗 |
|---|---|---|
| 不變量 | `SPEC.md` | 驗證站。它是證據的判準來源 |
| 驗收條件 | `requirements.md` | 審查站。它是「做到了沒」的判準 |

這次改動會動到不變量的時候，停下來。那是產品決定，要廠主先點頭。

## 4. 第二道：design.md

十二節，依序：

| | 節 | 內容 |
|---|---|---|
| 1 | Overview | 一段。要改什麼 |
| 2 | Goals / Non-Goals | 做與不做 |
| 3 | **Boundary Commitments** | 這次改動切成哪幾塊 |
| 4 | Architecture | 架構 |
| 5 | File Structure Plan | 哪些檔案會被改或新增 |
| 6 | Components & Interfaces | 每塊的介面 |
| 7 | Data Models | 資料模型 |
| 8 | System Flows | 一筆請求怎麼走 |
| 9 | Testing Strategy | 怎麼驗 |
| 10 | Integration & Migration Notes | 上線順序 |
| 11 | Open Questions / Risks | 還沒決定的、有風險的 |
| 12 | **Requirements Traceability** | 每條驗收條件對到哪一塊 |

### 4.1 Boundary Commitments

把這次改動切成幾塊，每塊是一個可以獨立完成的單位。

**沒有 Boundary，大功能拆不成能派工的任務。** 它的用途在 `tasks.md`：一個 Boundary 可以拆成一筆子任務。

### 4.2 Full Block 與 Summary Only

第 6 節的每一塊標一個深度：

| 深度 | 寫到什麼程度 | 哪些塊 |
|---|---|---|
| Full Block | 介面、型別、邊界條件都寫清楚 | 碰資料、碰授權、碰金流、有多種做法的 |
| Summary Only | 一段話說明意圖 | 其他 |

**不要全部寫 Full Block。** 那會把設計寫成實作，而且廠主在關卡上讀不完。

### 4.3 Requirements Traceability

一張表，把第 3 節的每條驗收條件對到第 6 節的某一塊。

| 對不到的東西 | 意思 |
|---|---|
| 驗收條件對不到塊 | **設計漏了** |
| 塊對不到驗收條件 | **在做沒人要的東西** |

這張表是這一道唯一的自檢。不要跳過它。

## 5. 第三道：tasks.md

```markdown
# 實作任務 — <feature>

- [ ] 1. <Boundary 名稱>
- [ ] 1.1 <任務標題>
  - <要做的事，一條一行>
  - 可觀察完成狀態：<做完之後，從外面看得到什麼>
  - _Requirements: 1.1, 1.2_
  - _Boundary: <Boundary 名稱>_
```

### 5.1 可觀察完成狀態

**這一行是這一道最重要的東西。**

它寫「做完之後，從外面看得到什麼」。不是「寫好了」，是一個可以被檢查的狀態。

| | 例子 |
|---|---|
| 好 | 「migration 內容包含 rename、add column、逐列 backfill，而且 NOT NULL 的順序在 backfill 之後」 |
| 壞 | 「migration 寫好了」—— 檢查不了 |

它是 `fac-implement` 開 PR 之前的自檢輸入。沒有它，「做完了」只是工人的自述。

### 5.2 兩個標籤都要寫

- `_Requirements: …_` —— 這個任務滿足哪幾條驗收條件。
- `_Boundary: …_` —— 這個任務屬於哪一塊。

它們讓三份文件互相咬住。少一個，`tasks.md` 就變成一張沒有來源的清單。

## 6. 三道核准怎麼走

| 一道寫完 | 你做 | 然後 |
|---|---|---|
| requirements | `generated: true`，`phase` 推一格 | **停下來。等廠主設 `approved`** |
| design | 同上 | 同上 |
| tasks | 同上 | 同上 |

三道都 `approved` 之後：把每個 Boundary 拆成子任務，各貼 `fac-ready`，然後把這一筆原任務改成 `fac-ready` 或關掉。

**前一道沒核准，不要產出下一道。** 設計建在沒核准的需求上，被退回的時候兩份一起重寫。

## 7. 硬規則

1. **一次只推進一道。**
2. **`approved` 只有廠主能設。** 你設了就是繞過關卡。
3. **驗收條件只用那三種句型。**
4. **「不包含」那一節每一條都要寫理由。**
5. **不要全部寫 Full Block。**
6. **不改 `SPEC.md` 的不變量。** 要改就另開一筆任務。
7. **不寫 code。** 連一行示範都不要寫進 `design.md` 之外的地方。

## 8. 修正訊號

| 廠主改了什麼 | 意思 |
|---|---|
| 退回 requirements | 「要什麼」理解錯了。看是哪一類需求一直寫歪 |
| 退回 design，但 requirements 過了 | 深度判斷錯了。Full Block 標太多或太少 |
| 自己改掉驗收條件的句型 | 那條寫成了願望 |
| 補上「不包含」的條目 | 範圍界定一直漏同一種相鄰的東西 |
| `tasks.md` 的「可觀察完成狀態」被改寫 | 那一行寫得檢查不了 |

`fac-implement` 在 `tasks.md` 寫的 `_偏離原計畫_` 也是這一站的訊號。一直偏離同一個地方，表示設計漏了一塊。

<!-- fac:shared:end -->
