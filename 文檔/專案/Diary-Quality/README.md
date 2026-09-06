---
id: task-20260906-diary-quality
name: 日記品質線 V1
status: DOING
parent: task-20260829-rp-memory-rebuild
status_changed: 2026-09-06
harness_schema: 1
description: 做到什麼算完——日記生成的 prompt 讓模型機械地知道三塊輸入各自的身分與職責：近期日記只供心理連續性、前情語境只供理解、本次新增經歷才是本篇證據；沒有新變化時能自然延續既有狀態而不硬造成長。改動限於 prompt 組裝與少量前情 overlap，不動 interval=5、maxWindowFloors=40、日記 schema、模型、temperature；不做向量檢索、不做 AI 事件切分、不強制輸出「變化」欄位、不加去重規則。2026-09-06 查證現況：checkpoint 三欄位（_lastDiaryChatLength / processedFloors / lastFloor）已存在且只在批次成功後推進、失敗會回滾；每篇實際只讀 5 個 AI 樓層（最近九次生成皆為 5），40 只是積壓上限；使用者樓層從未進入日記輸入（篩選條件排除 is_user，已處理集合中使用者樓層為 0）。設計依據為第三方討論共識，原文與更正註記收在本資料夾 討論共識_2026-09-06.md。與 Learned Self 開發平行、驗證分開；本線凍結前不動 Learned Self 的觀測。
---

# Diary-Quality

> 讓日記生成擁有有明確時間邊界與證據角色的 context：系統機械知道哪些劇情已處理、哪些尚未處理；舊日記與前情只提供連續性與理解，本次新增劇情才是本篇主要證據。先以最小改動驗證這個資訊分層是否提升日記品質，再決定要不要更複雜的事件切分或檢索。

---

## 範圍

### In Scope

- **資料塊職責說明**：prompt 至少分成「近期心理背景｜歷史參考」「前情語境｜已處理、只供理解」「本次新增經歷｜本篇主要依據」三塊，並明確告訴模型各塊怎麼用；核心語意是「本篇消化新增經歷、無新發展時自然延續、不必製造變化」，不是「禁止重複」
- **前情語境 overlap**：現況為零 overlap、場景從 checkpoint 冷開始；V1 用固定少量已處理樓層當前情，明確標示只供理解
- **使用者樓層是否進入場景**：2026-09-06 新查到的岔路，共識未涵蓋；V1 設計討論要決定
- **驗證設計**：依 CLAUDE.md 驗證前置 Gate 五問先寫驗證設計再跑；`processedFloors` 是不會騙人的 Occurrence 計數器
- **改 `index.js` 前備份、改後 `node --check`**（CLAUDE.md 硬性要求）

### Out of Scope

- **刪舊日記、把 40 改 5、強制 `new_change` 欄位、regex 禁「越來越」、去重規則**（共識 §12：問題定義不是「句子不重複」）
- **向量檢索、AI 事件切分**（共識 §10：先驗證資訊分層單獨的效果，多變因疊加無法歸因）
- **Character Baseline 自動歸納**（共識 §6A：後續方向，非 V1 前置）
- **把 Learned Self 判斷塞回日記**（共識 §3；跨篇長期變化歸 Learned Self 線）
- **重複率當主要 KPI**（共識 §2、§13）

---

## Changelog

> 每條連結到當天 handoff 檔的對應時間戳區塊

- 2026-09-06 — 專案成立 → [handoff](../../handoff/session-handoff-20260906.md)
- 2026-09-06 — Step 1 change `diary-include-player-messages` 開立（proposal/design/specs/tasks 齊）；擴充 repo 建 fork 並重整為 main（上游）／running（實跑）結構 → [handoff](../../handoff/session-handoff-20260906.md)
- 2026-09-06 — Step 1 實作完成並通過 Gate：分支 `diary-player-messages`、commit `63a6537`（已推 `fork`）；Instrument 校準 PASS（ON 玩家樓號 `[1242,1244,1246,1248]` = 獨立算出的預期；OFF 0 筆）、Occurrence 對帳 PASS（metadata sha1 前後同為 `d76560233e1cff84`）；第一組 OFF／ON 材料存 `RP記憶/實驗與驗證/Diary_玩家樓層_OFFON觀測_2026-09-06.md`，**5 組前不判讀** → [handoff](../../handoff/session-handoff-20260906.md)
