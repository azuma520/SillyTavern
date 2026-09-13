## Why

`character-diary` 會為**不在場的角色**寫日記，並為了填滿必填欄位而編造第一人稱的內心狀態。2026-09-06 的機制與 prompt audit（`RP記憶/實驗與驗證/Diary_機制與Prompt_Audit_2026-09-06.md` §4.1，問題地圖 P2）以徐婷婷三篇日記為證：t1275「這段時間我沒有出現」、t1285「其實想加入他們，只是擔心自己會顯得多餘」、t1308「若聽見她們事後炫耀，我大概會好奇宇璽最後究竟選了誰」，這些心理內容在劇情裡沒有任何來源。2026-09-13 重數：Branch #12 有 4 篇、Branch #13 有 9 篇徐婷婷自述缺席的日記（t1275 到 t1678），自我強化仍在跑。對 Learned Self 而言這比 `key_events` 缺主詞更危險：污染的不是一個欄位，是整篇 Experience 直接入庫。這是「日記品質線 V1」的 Step 3、audit §七 的候選 B。

2026-09-13 對碼確認因果鏈比 audit 多一層：**誰能被寫日記，目前完全由模型決定**。sys prompt 只說「为其中每个有名有戏份的登场角色…写一篇日记」，模型回傳誰，`mergeDiaries` 就收誰，沒有任何在場閘門（只有 `is_minor`／`cameo` 門檻，徐婷婷正是靠 cameo 累到 3 篇「我沒出場」轉正的）。`cdCaptureCast` 的角色是**標籤洩漏**：它以「名字在文字裡出現」命中，就把該角色的舊日記以「登场角色近期日记」為標題餵回 prompt，等於事前告訴模型「她在場」。而這張卡是 GM 敘述卡（`mainCardIsGM` 為真），每個樓層的說話者名字都是卡名，程式從 metadata 讀不出誰發言、誰旁聽，「在場」的資訊只存在於文字裡。因此 audit 提的「`cdCaptureCast` 只認說話者 name」在本卡下無效；判定必須交給讀得懂文字的模型，執行必須交給擋得住的程式。

## What Changes

- **Prompt 加 presence 契約**：`cdBuildDiaryPrompt` 的 system 要求清單新增四值定義（`participated`／`witnessed`／`mentioned_only`／`absent`）、保守規則（無法確認是否感知 → `absent`）、後兩級不寫正文、`witnessed` 只能寫自身可感知的內容；JSON 範本每個 npc 多一個 `presence` 欄位。
- **寫入端加 Presence Gate**：`mergeDiaries` 在黑名單檢查之後、重點角色／選擇性記憶／路人轉正／別名補充**之前**加閘門，只有 `participated`／`witnessed` 進入後續流程；`mentioned_only`／`absent`、欄位缺失或非法值一律不寫入、不累計 cameo、不補別名。
- **presence 不進日記 entry schema**：entry 的九個鍵不變。每次合併把每個候選的判定與去留寫進 store 頂層新 key `presenceAudit`（有界陣列，最近 200 筆，每筆含樓層、角色、判定、是否寫入、原因），同時走 `cdAddLog`。`presenceAudit` 落在聊天檔第一行的 metadata，事後可用 python 對帳；它是稽核資料，不是角色的長期心理內容。
- **切斷標籤洩漏**：`diaryMemory` 的標題由「登场角色近期日记（按登场人物抽取）」改為「已知角色近期记忆（按名字提及抽取, 被提及不代表在场）」。`cdCaptureCast` 本身不改，定位由「登場判定器」降為「候選角色抽取器」。
- **量測工具**：新增 `文檔/專案/Diary-Quality/tools/presence_audit.py`，讀聊天檔的 `presenceAudit` 與 `diaries`，對照事前凍結的情境期望表輸出每情境的判定分佈與寫入條數；先以合成 fixture 校準、commit 凍結，再收正式資料。
- **驗收設計先於程式**：五個測試情境（A–E）對應四個 presence 狀態，場景文字由使用者事先撰寫、ground truth 先寫再生成；先在**未改的程式**上跑基線確認情境真的能誘發缺陷，再改程式重跑。硬門檻：C／D 錯誤入庫 = 0；A／B 不得被全部誤擋；`witnessed` 的感知越界由人工 ground truth 判。**驗收尺凍結前不 apply**。

## Capabilities

### New Capabilities
- `diary-presence-gate`: 日記候選角色的 presence 判定契約（四值、保守規則、後兩級不寫正文、witnessed 感知邊界）、寫入端的 Presence Gate、`presenceAudit` 稽核記錄、記憶注入標題中性化。

### Modified Capabilities
<!-- 無。`diary-key-events-actor`／`diary-scene-player-messages` 的既有 requirement 行為不變：本 change 只在同一個 sys 清單再加數條、範本多一個欄位、合併流程前段加閘門。 -->

## Impact

- **程式**：`D:/AI/SillyTavern/public/scripts/extensions/third-party/character-diary/index.js`（CRLF、獨立 git repo，`running` 現在 `7b861d3`）。觸及四處：(1) `cdBuildDiaryPrompt` 的 `diaryMemory` 標題（約 803 行）；(2) 同函數 `sys` 陣列（約 830–848 行）與 JSON 範本；(3) `mergeDiaries`（2174 行起）在黑名單檢查（約 2190 行）之後插入閘門；(4) `cdGetData`／store 初始化補 `presenceAudit` 預設值（若既有 store 缺此 key 則在合併時建立）。`cdBuildDiaryPrompt` 三個呼叫點（測試路徑 3233、正式生成 4504、單篇重寫 8678）同時吃到新 prompt；閘門只在正式生成走的 `mergeDiaries` 生效，單篇重寫路徑（8699 的獨立合併）**不套閘門**（使用者對既有日記主動重寫，在場性已由使用者裁定）。`cdBuildCombinedPrompt` 為死碼不動。`cdBuildDiaryInjectionText`（聊天注入，2434 行）也用 `cdCaptureCast`，但 `injectDiary` 目前為 false 且不在本 change 範圍，不動。
- **分支**：從 `running`（`7b861d3`）開 `diary-presence-gate`。ST 目前 checkout 在 `diary-key-events-actor`，與 `running` 同一 commit，切到新分支內容不變。
- **資料**：驗收在從 Branch #12 現行 head 分出的 4 個新測試 branch 上進行（各代表一組情境），#12／#13 本身不重跑。`presenceAudit` 是 store 新增的頂層 key，舊聊天檔沒有它，首次合併時建立；不遷移、不回填。
- **下游讀取點**：entry schema 不變，13 個 `key_events` 讀取點與所有面板／時間軸／搜尋／編輯器／匯出零改動。`presenceAudit` 目前無任何 UI 讀取點，只供 python 對帳與 `cdAddLog` 面板日誌。
- **不受影響**：`relationship_with_others`（P5）、`mood`（P6）、`secret` 留空出口（P3）、「已有記憶」職責說明（P4）、`focusRoles` 的「即使出场较少也要补全」指示（P9，目前 `focusRoles=[]` 未觸發，本 change 只規定閘門對重點角色**不豁免**、不改那句 prompt）、`interval`／`maxWindowFloors`／模型／temperature。
- **下游線**：Learned Self 讀 `diaries[name][]` 時可視 `presenceAudit` 為「這篇有沒有通過在場閘門」的旁證（依 `message_id` 對得上），但 LS 尚未動工，此為註記。
