---
id: task-20260906-learned-self
name: Learned Self 開發
status: DOING
parent: task-20260829-rp-memory-rebuild
status_changed: 2026-09-06
harness_schema: 1
description: 做到什麼算完——角色能在故事推進後，形成一份「因經歷而來的理解」，該理解由結構保證屬於她本人（不靠文字裡寫了角色名、不靠注入位置巧合），能被關掉也能被更新，且注入後不出現四個失敗模式（照抄記憶 / 元指令洩漏 / 過度服從 / 行為抑制）。設計權威為 RP記憶/實驗與驗證/LearnedSelf_MVP設計.md（八條核心原則、Experience / Meaning / Scope 三層、§十一 ownership binding）。三個凍結起點（2026-09-05 使用者明示）：① Production 走既有獨立 AI 管線，這是產品需求、不是實作偏好；② Production / Storage / Injection 分開決定，不得因為某一格好做就綁住另外兩格；③ 不得讓 Learned Self 的資料模型去配合 Diary 或 Relation 現成管線——反過來才對。上游判定已完成：Diary audit（2026-09-05）判 Diary 為「必要輸入但單獨不足」，提煉層因此必須讀序列不讀單篇、且必須跨篇去重。
---

# Learned Self

> 讓角色能因為經歷而形成新的理解，並且那份理解在系統裡有一個說得清楚「屬於誰、從哪來、到哪為止」的位置。

---

## 範圍

### In Scope

- **資料模型**：Experience / Meaning / Scope 三層的欄位定義與硬性限制（Scope 必填、Meaning 不得出現行為描述）
- **Ownership binding**：owner（`target_character`）由組裝進 prompt 時的結構保證，不靠文字約定、不靠位置相鄰
- **載體遷移**：世界書（實驗腳手架）→ LIWE（逐行結構天生帶 `target_character`）。Base Character 與 Learned Self 分層、不得合併回原始角色卡
- **提煉層（Production）**：輸入至少為「日記序列 + 對應原文」；必須讀序列不讀單篇、必須跨篇去重（否則把「抄了六次」讀成「反覆確認六次」）；候選必須能回原始對話查證
- **Injection**：注入時機、位置、可關閉性
- **觀測**：四個失敗模式的判準與反向行為證據

### Out of Scope

- **讓 Learned Self 的資料模型去配合 Diary 或 Relation 現成管線**（2026-09-05 使用者明示否決；Relation 可借骨架，但 `from === to` 被硬擋、`note` 單一字串覆蓋而 Experience 是 LEDGER 語意、且全自動無審核關違反原則 4）
- **人工提煉當作產品架構的一格**（2026-09-05 使用者否決「先人工、管線後補」：產品目標是 AI 自動形成，人工那格會固化成架構）
- **建 `LearnedSelf_登記簿.md`**（每一欄都能從既有資料取得或推導，建了就是抄資料並產生同步問題——違反設計原則 2「一個語意一個權威」）
- **修 `character-diary` 的窗口機制**（三個機制缺陷已全部診斷出來，但決定不動：修窗口會影響現有日記品質，而 Learned Self 要做的正好是日記做不到的那件事）
- **機制測試線第三輪**（2026-09-05 標【擱置·非作廢】，登記檔維持凍結）

---

## Changelog

> 每條連結到當天 handoff 檔的對應時間戳區塊

- 2026-09-06 — 專案成立 → [handoff](../../handoff/session-handoff-20260906.md)
