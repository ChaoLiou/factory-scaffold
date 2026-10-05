# 技術規格 — {{PRODUCT_NAME}}

白話規格在 `../SPEC.md`。這一份描述架構與程式碼的形狀，會隨實作反覆調整。

---

## 技術棧

{{TECH_STACK}}

由建廠產線第二站的五題查對照表決定，不是自己挑的。

{{STACK_OVERRIDE_REASON}}

<!-- L3 覆寫對照表的結果時，在上面寫原因。沒覆寫就刪掉這一行。 -->

---

## 架構規則

這些規則不能改。它們限制架構，不限制技術棧。

1. **前端不持有任何可以直接存取資料的憑證。** 只准 PKCE flow，session 存 HttpOnly cookie。
2. **預覽與生產是不同的專案、不同的帳號。** 不是同一個專案的兩組環境變數。
3. **測試帳號的登入方式只開在預覽專案。**
4. **預覽的位置不可猜測**，並用 service token 擋陌生人。
5. **生產密鑰不進 agent 的執行層。** agent 只能觸發部署，不能讀密鑰。

第 5 題答「會」時再加三條，見 `.factory/security.md`。

---

## 部署

| | |
|---|---|
| 平台 | {{DEPLOY_PLATFORM}} |
| 預覽 | {{PREVIEW_MECHANISM}} |
| 生產 | {{PRODUCTION_TARGET}} |

---

## 資料

| | 預覽專案 | 生產專案 |
|---|---|---|
| 位置 | {{PREVIEW_DB}} | {{PRODUCTION_DB}} |
| email + password | 開（給 agent） | **關** |
| 第三方 OAuth | 關 | {{PRODUCTION_OAUTH}} |

初始資料在 `{{SEED_PATH}}`。重置指令是 `{{RESET_COMMAND}}`。

**所有預覽共用一個資料庫，每輪跑證據之前重置。** 已知缺陷：並行的 PR 會互相污染。廠主變多或同時跑的 PR 變多時，這一項要重新決定。

---

## 資料模型

{{DATA_MODELS}}

---

## 目錄結構

{{FILE_STRUCTURE}}
