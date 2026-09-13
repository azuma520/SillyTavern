# diary-presence-gate

## Purpose

讓 `character-diary` 只為**真正經歷了本段事件**的角色寫日記。誰能被寫日記原本完全由模型決定、寫入端沒有任何在場閘門，而 GM 敘述卡下程式又無法從 metadata 判斷誰在場；本能力把判定交給讀得懂文字的模型（四值 presence），把執行交給擋得住的程式（Presence Gate），並留下可對帳的稽核記錄，切斷「被提及 = 登場」的標籤洩漏。這是 Learned Self 讀日記時的前置保證：入庫的第一人稱 Experience 必須有其主人真的在場。

本能力的範圍限於 **prompt 契約 + 寫入閘門 + 稽核記錄**：不改日記 entry schema、不回填舊資料、不做完整感知系統、不動聊天注入與單篇重寫路徑。

## Requirements

### Requirement: 候選角色的 presence 判定契約
日記生成 prompt（`cdBuildDiaryPrompt` 的 system 要求清單與 JSON 範本）SHALL 要求模型為每個候選角色輸出 `presence` 欄位，取值 SHALL 限於 `participated`、`witnessed`、`mentioned_only`、`absent` 四者之一，並 SHALL 給出各值定義。當無法確認角色是否在場或是否感知到事件時，prompt SHALL 要求模型判為 `absent`。prompt SHALL 要求 `mentioned_only` 與 `absent` 的角色仍輸出 `name` 與 `presence`，但 `entry`、`secret` 為空字串、`key_events` 為空陣列。prompt SHALL 要求 `witnessed` 的角色只寫其在場時能看到、聽到或合理推知的內容。

#### Scenario: 角色實際參與
- **WHEN** 場景文字中某已知角色與玩家對話或行動
- **THEN** 模型輸出該角色 `presence` 為 `participated`，並附完整日記正文

#### Scenario: 角色在場旁聽未發言
- **WHEN** 場景文字明寫某已知角色在場、看著或聽著事件，但未發言也未行動
- **THEN** 模型輸出該角色 `presence` 為 `witnessed`，日記內容不含該角色無法感知的對話、動作或他人內心

#### Scenario: 角色只被提及
- **WHEN** 場景文字中某已知角色的名字只出現在他人的話語或敘述中，本人未出場
- **THEN** 模型輸出該角色 `presence` 為 `mentioned_only`，`entry`／`secret` 為空字串、`key_events` 為空陣列

#### Scenario: 無法確認是否感知
- **WHEN** 場景文字只暗示某已知角色可能在附近，但未確認其能看到或聽到事件
- **THEN** 模型輸出該角色 `presence` 為 `absent`，不寫正文

### Requirement: 寫入端的 Presence Gate
`mergeDiaries` SHALL 在黑名單檢查之後、重點角色判定、選擇性記憶、路人轉正（`is_minor`／`cameo`）與別名補充之前，依 `npc.presence` 決定是否繼續處理該候選。`presence` 為 `participated` 或 `witnessed` 時 SHALL 放行；為 `mentioned_only` 或 `absent` 時 SHALL 不寫入日記、不累計 `cameo`、不補充別名、不改 `promoted`。`presence` 缺失或不在四值之內時 SHALL 視同 `absent` 擋下。閘門 SHALL NOT 因角色屬於 `focusRoles` 而豁免。比對前 SHALL 對值做 trim 與小寫正規化。

#### Scenario: 放行 participated
- **WHEN** 模型回傳的 npc `presence` 為 `participated`
- **THEN** 該 npc 進入既有的重點角色／轉正／去重／寫入流程，行為與本 change 之前相同

#### Scenario: 擋下 mentioned_only
- **WHEN** 模型回傳的 npc `presence` 為 `mentioned_only`，且該角色尚未 `promoted`、`cameo` 為 2
- **THEN** 該角色的 `diaries` 陣列長度不變、`cameo` 仍為 2、`promoted` 不變、`aliases` 不變

#### Scenario: 欄位缺失視同 absent
- **WHEN** 模型回傳的 npc 沒有 `presence` 欄位，或值為 `"Present"`、`"在场"` 等四值之外的字串
- **THEN** 該 npc 不寫入，稽核記錄的 `reason` 為 `invalid_presence`

#### Scenario: 重點角色不豁免
- **WHEN** 某角色在 `focusRoles` 中，模型回傳其 `presence` 為 `absent`
- **THEN** 該角色不寫入

#### Scenario: 黑名單優先
- **WHEN** 某角色在 `diaryBlacklist` 中
- **THEN** 該角色在閘門之前即被跳過，不產生稽核記錄（維持既有行為）

### Requirement: presence 稽核記錄
每次 `mergeDiaries` 處理一個通過黑名單檢查的候選時，SHALL 在 store 頂層 `presenceAudit` 陣列追加一筆 `{message_id, name, main, presence, written, reason, ts}`，其中 `reason` 為 `ok`、`presence_blocked`、`invalid_presence` 之一；`written` 為該候選最終是否被 push 進 `diaries`。`presenceAudit` SHALL 只保留最近 200 筆。`presenceAudit` SHALL 隨 store 一起存入聊天檔 metadata。同一筆資訊 SHALL 同時走 `cdAddLog`。日記 entry 的鍵集合 SHALL NOT 因本能力改變（維持 `turn`、`date`、`entry`、`mood`、`attitude_to_user`、`secret`、`key_events`、`relationship_with_others`、`message_id` 九鍵）；`presence` SHALL NOT 寫入 entry。既有聊天檔缺 `presenceAudit` 時 SHALL 於首次合併時建立，SHALL NOT 回填。

#### Scenario: 每個候選一筆記錄
- **WHEN** 一次合併收到 3 個 npc（無黑名單），其中 2 個 `participated`、1 個 `absent`
- **THEN** `presenceAudit` 新增 3 筆，`written` 為 true、true、false，`reason` 為 `ok`、`ok`、`presence_blocked`；`diaries` 只有前兩者各增一篇

#### Scenario: 被 cameo 擋下的候選
- **WHEN** 某 npc `presence` 為 `participated`、`is_minor` 為 true、`cameo` 累計後未達門檻
- **THEN** 稽核記錄 `presence` 為 `participated`、`written` 為 false、`reason` 為 `ok`（閘門放行，後段既有邏輯跳過）

#### Scenario: 上限 200 筆
- **WHEN** `presenceAudit` 已有 200 筆，再追加 1 筆
- **THEN** 陣列長度仍為 200，最舊的一筆被移除

#### Scenario: entry 不含 presence
- **WHEN** 任一 npc 被寫入 `diaries`
- **THEN** 新篇的鍵集合為既有九鍵，不含 `presence`

### Requirement: 記憶注入標題不暗示在場
`cdBuildDiaryPrompt` 以 `cdCaptureCast` 抽取候選角色並注入其近期日記時，標題 SHALL 為「已知角色近期记忆（按名字提及抽取, 被提及不代表在场）」，SHALL NOT 使用「登场」字樣描述被抽取的角色。`cdCaptureCast` 的比對邏輯 SHALL NOT 改變。

#### Scenario: 被提及角色的舊日記注入
- **WHEN** 場景文字提及徐婷婷的名字，且她有既有日記
- **THEN** prompt 的 user 訊息含「已知角色近期记忆」區塊、列出她最近 `diaryCharLimit` 篇 entry，區塊標題不含「登场」

### Requirement: 驗收尺先於程式凍結
本能力的成功標準（`mentioned_only`／`absent`／uncertain 三類情境錯誤入庫各 = 0、`participated` 寫入 ≥ 16／20、`witnessed` 寫入 ≥ 3／5、`witnessed` 感知越界由人工 ground truth 判 = 0、entry schema 不變、稽核筆數對帳、`presenceAudit` 上限 200、舊資料相容）與其門檻數字 SHALL 在收第一筆正式資料前寫入 change 並凍結。驗收報告 SHALL 把「模型 presence 判定錯誤」與「presence 判定正確但程式 Gate 執行錯誤」分開統計，SHALL NOT 合計為同一種失敗。量測工具 `presence_audit.py` SHALL 先以合成 fixture 校準並 commit，其 commit SHALL 早於 `index.js` 的程式 commit。正式階段之前 SHALL 先在未修改的程式上跑基線，且基線 SHALL 在 C 或 D 情境至少誘發一篇不在場日記，否則情境 SHALL 重寫。

#### Scenario: 基線未誘發缺陷
- **WHEN** 舊碼基線在 4 個測試 branch 各跑 3 次後，C 與 D 情境的不在場角色寫入條數合計為 0
- **THEN** 判定情境無效，重寫場景文字後重跑基線，不得進入正式階段

#### Scenario: 兩種錯誤分開歸因
- **WHEN** 某個期望為不該寫的格子出現 `written=true`
- **THEN** 若該筆稽核記錄的 `presence` 為 `participated` 或 `witnessed`，計入「模型判定錯誤」；若為 `mentioned_only`、`absent` 或非法值，計入「Gate 執行錯誤」；兩個計數在報告中分列

#### Scenario: 凍結順序
- **WHEN** 檢視 elephantfish 的 `presence_audit.py` commit 時間與擴充 repo 的 `index.js` commit 時間
- **THEN** 前者早於後者，且兩者皆早於第一筆正式階段資料的產生時間
