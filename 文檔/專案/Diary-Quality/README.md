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
- 2026-09-06 — **驗收設計重新收斂**：廢除 OFF／ON 對照，改為 ON 態 solution acceptance（5 個自然情境 × 從主線最新位置建立的同起點 branch、先寫 ground truth 再用「补写指定范围」產生真實日記）；第 1 組材料降級為 pilot。判準定為必要能力（玩家言行／角色回應／因果連結）+ 否決條件（與玩家有關的無證據推論，以既有 50 篇 OFF 態日記為基線）。觀察模式 UI 完成（既有 `autoSummary` 接面板，`index.js` +2 行、實測通過）。查 call path 查出三條 bug 並登記（branch 繼承幽靈 `processedFloors`／localStorage 備份池不記來源／「检查自动触发」計數不一致） → [handoff](../../handoff/session-handoff-20260906.md)
- 2026-09-06 — **Step 1 驗收完成、使用者接受**：5 個同起點 branch（#8–#12）各演一種玩家事件（請託／承諾／具體行動／揭露／拒絕），先寫 ground truth 再用「补写指定范围」產生真實日記。**15/15 子項通過、0/5 觸發否決條件**；其中情境 3 為刻意極端＋未交代動機的設計組，在最有利於編造的條件下日記未補造玩家動機。`tasks.md` 36/36 全勾。材料與判讀存 `RP記憶/實驗與驗證/Diary_玩家樓層_ON態驗收_2026-09-06.md`，另產出對外討論版 `Diary_Step1_實驗報告_對外版_2026-09-06.md`。額外取得一組 OFF／ON 對照（不列入驗收樣本）。順帶登記兩條日記管線既有缺陷（替不在場角色寫「我沒出場」的日記／`relationship_with_others` 無下游消費者） → [handoff](../../handoff/session-handoff-20260906.md)
- 2026-09-06 — **Step 1 change 歸檔、日記管線四層 audit 完成**：`diary-include-player-messages` 兩份 delta spec 同步進主 specs（`diary-scene-player-messages`／`diary-auto-summary-toggle`，本 repo 首次寫主 specs、`openspec validate --all` 2 passed），change 移入 `openspec/changes/archive/2026-09-06-…`。另完成 read-only 四層 audit（輸入機制／Prompt 職責／輸出欄位與 consumer／問題分層），產出 11 條問題地圖存 `RP記憶/實驗與驗證/Diary_機制與Prompt_Audit_2026-09-06.md`。**關鍵結果**：① `key_events` 無 actor 槽位且 prompt 對它零要求，248 條實測 50.0% 完全無主詞——驗收時的主詞錯置是結構性質而非筆誤；② 不在場角色是 mechanism 問題且**會編造內心狀態**，`cdCaptureCast` 以「被提及」而非「有出場」判定，並經 `diaryMemory` 自我強化；③ `relationship_with_others` 零讀取點確認，附帶查出 key 未經別名正規化（`大老闆`/`大老板` 簡繁分裂）；④ system prompt **從未定義「已有記憶」的角色**（對應本檔 In Scope「資料塊職責說明」）；⑤ 2026-09-05 缺陷 A 部分推翻——複製污染只在 t753–t801、之後 55 篇零復發；缺陷 D 簡繁已由 `38dd3ec` 修掉但資訊量惡化（开心 78.9%）；⑥ 世界書同步為死碼（本版 ST 無該組 API），列為誤判來源。本檔第 22 行「現況為零 overlap」經獨立確認成立。下一個 change 未定，候選見 audit §七 → [handoff](../../handoff/session-handoff-20260906.md)
- 2026-09-13 — **Step 2 change `diary-key-events-actor` 實作並驗收接受**：prompt 加一條 `key_events` actor 契約（「主体：事件」、日記主人也寫主名）、schema 不改；量測工具 `tools/classify_key_events.py` 先以 248 條凍結基線校準（52/5/18/48/125，與 audit 差 1 條、使用者接受）並 commit 凍結（`21250a3`）再改 prompt（擴充 repo `7b861d3`，分支 `diary-key-events-actor`，`running` 已快轉到 Step 1 的 8d19c7f）。驗收在 Branch #8–#11 對 Step 1 同段樓層重跑：19 條 `key_events` 無主詞 0%（基線 50.4%）、名字＋冒號開頭 100%、歸屬錯誤 0 條、鍵集合不變、面板新舊混存正常，五項標準全達標。材料 `RP記憶/實驗與驗證/Diary_KeyEvents_Actor_驗收_2026-09-13.md`。同時提早結清驗收節點 9/20 Instrument 一問 → [handoff](../../handoff/session-handoff-20260913.md)
- 2026-09-13 — **Step 3 change `diary-presence-gate` 實作並驗收接受**（audit 候選 B／P2）：模型判 presence（participated／witnessed／mentioned_only／absent）、`mergeDiaries` 加 Presence Gate 只放行前兩級、缺失或非法值 fail-closed、重點角色不豁免；稽核記錄落 store 頂層 `presenceAudit`（≤200 筆）、entry 九鍵不變；記憶注入標題改「已知角色近期记忆」。擴充分支 `diary-presence-gate` commit `c73b6a3`（21:13，晚於 instrument `9a69fce42` 20:30）；`running` 快轉至此。驗收：4 情境母 branch（#14–#17，從 #12 的 #1454 分出、場景文字受控）、每 run 一支複本子 branch；舊碼基線 12 run（只有 S2「只被提及」誘發缺陷 3／3）；新碼 20 run：C／D／E 誤寫 0／0／0、模型判定錯誤 0、Gate 執行錯誤 0、A 20／20、B 5／5、越界 0。**鑑別力限制**：只有 S2 徐一格有鑑別力，其餘不在場格舊碼即為 0；E 只能看標籤。材料 `RP記憶/實驗與驗證/Diary_PresenceGate_驗收_2026-09-13.md`。**順帶查出**：Step 2 標準 5 的四個讀取點只有兩個可達——時間軸 `cdRenderTimeline` 為死碼、搜尋框被上游 `style.css:1650` 隱藏；編輯器儲存用 `split(/[,，、]/)` 會把含全形逗號的 `key_events` 切裂（backlog `[bug] [P3]`，Branch #8 一篇 3→5 條、使用者裁定不還原）。待辦：`cdDiagCast` 面板「登场」文案；E 情境加強場景（使用者決定）；徐婷婷既有 5 篇「我沒出場」日記清理（另案）；#12／#13 自然累積後用凍結腳本再量 `presenceAudit`（驗收節點 2026-09-27，只驗 #13）→ [handoff](../../handoff/session-handoff-20260913.md)
