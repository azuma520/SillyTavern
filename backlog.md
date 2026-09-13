<!-- backlog-schema: v2 -->
<!--
workflow-harness — backlog.md template
對應 capability：backlog-management（首次 spec land 於 refactor-observation-system change）
位置：使用者專案根 backlog.md

schema 版本：v2（檔頭 `backlog-schema: v2` HTML 註解標記；見 backlog-marker-integrity change）。
  v2 相對 v1 的差別：標籤一律「前置」——寫在條目標題**之前**的前綴區（見下）、不再句尾散落。
  無此標記的舊檔（v1）視為 legacy、狀態寫入 fail-closed、需經 `migrate` 升級（flat-v1）或
  `/init-harness --force-replace backlog.md`（4-heading 舊代）。

schema 哲學：不為結構而結構、flexible 標記取代僵化分區。對齊 TODOS L1/L2 同表 + 純文字 marker pattern。

結構規矩：
- 單一 `## 待辦` heading（**禁止**新增其他 H2 heading：不可有舊版 4-heading 軟分類「雜務 / 技術債 / 構想 / SOP 候選」、也不可有完成 archive 區「已修 / 已降級 / archive」；以上 7 個禁止名稱在本檔出現時不可冠 `## ` 前綴、避免 grep 誤匹配為實際 heading）
- 活條目 + 完成 ≤10 條目 mixed 在 `## 待辦` 下、靠 tag 區分（不靠 heading 區分）
- 本檔**不可**含驗收節點 sentinel 區段（sentinel 標記只屬於 驗收節點.md、見 observation-checkpoint capability R4）

標籤前置規約（v2 核心）：
- 每條目首行格式＝`- ` + **前綴區** + 標題散文。前綴區是首行 `- ` 之後、連續的 `[…]` 標籤序列，
  直到第一段非標籤文字（＝標題起點）為止。例：`- [優化建議] [case-count: 4] fast-track 閾值案例`。
- 所有主分類 / 修飾 tag 與狀態 marker **一律寫在前綴區**（標題之前）。寫在標題之後（句尾）的標籤 token
  不算數、且會被 lint 報 `outside-prefix`。
- 標題散文之後、後續子彈行、下一行的標籤長相文字，一律**不是**標籤。

引述規約（散文要提到標籤字面時）：
- 條目散文若要**講解 / 引用**某個標籤字面（例：說明「這條之前標過 `[done: ...]`」），
  用反引號把它包成 inline code span——`[done: 2026-07-07]` 這樣寫是引述、不會被當真標籤。
- 真標籤一律**裸寫**在前綴區（不包反引號）；agent MUST NOT 手拼標籤字串、狀態寫入一律經 validated writer。

tag 三類系統（封閉集、agent 不可自創 tag、改集合需開 OpenSpec change）：

主分類 tag（封閉、4 個、**必含 1 個**）：
  [構想]       新功能 / 新方向 / 新設計 idea、尚未評估要不要做
  [bug]        已知問題、有確定 root cause、待修
  [優化建議]   「先累積樣本、不預寫」類條目、累積 case 評估規則是否有效（B 路徑、N=5 surface）
  [SOP 候選]   工作流改善建議、未正式律定前的暫存

修飾 tag（封閉、**≤2 個**）：
  [P0] ~ [P3]  優先級（P0 最高、P3 最低）；缺省解讀為 P2；一個條目 MUST 有 0-1 個 P 級 tag
  [blocked]    卡點、需外部資源 / 拍板 / 工具修

狀態 marker（封閉、生命週期追蹤、subject to 互斥規則）：
  [case-count: N]                          累積 case 數（用於 [優化建議] tag）；舊式「[N case]」接受、agent 應 rewrite
  [mature: YYYY-MM-DD]                     累積成熟日期（N=5 觸發 SessionStart hook surface）
  [done: YYYY-MM-DD]                       完成日期、留原處不搬區
  [graduated: YYYY-MM-DD, → 載體]           賭注飛行中：升級日期 + 載體；賭注鏈終結（所有 exact-target 驗收節點 result 皆填妥）後整行刪除
  [paused: YYYY-MM-DD, revisit-by: <date>] 暫緩 + 可選回顧日期
  [deprecated: YYYY-MM-DD, reason: <text>] 廢除 + 原因

完成 marker 互斥群：[done:] / [graduated:] / [paused:] / [deprecated:] 彼此互斥、一個條目最多 1 個。搬家 / 拉走（換地方管、無賭注）不標 marker、直接刪行。
[case-count:] 跟 [mature:] 不是完成 marker、可與完成 marker 並存。

cap 10（超 cap loud、不自動刪）：
- 含 [done:] marker 的條目、本檔設計上維持同時 ≤10 個。
- 寫入使 done 總數超過 cap（第 11 個）時：validated writer **照寫**該筆、並 loud 通報「超 cap」、
  白話指示**立刻跑 backlog-triage runner confirm 掃最舊**——writer **不自動刪**任何條目、
  超 cap 是 transient 合法狀態、由 triage 再 surface + 使用者 confirm 後才刪。
- 刪除是不可逆動作、一律經 triage confirm 流程、**不**在寫入當下順手刪。
- 「fall off the bottom」歷史靠 git log / handoff / openspec archive / 文檔/專案/{name}/ 四備援
- cap 值預設 10；plugin default 在 config/defaults.yaml `backlog.done_cap`、user 可在專案 `.workflow-harness.yaml backlog.done_cap` 做 per-project override

tag dictionary 強制層：⚠️ Warn 層、不 block（plugin「感測器 + 提醒員、不是判官」哲學）

effort / impact 不收 tag：
effort（多難）/ impact（多重要）metadata MUST NOT 以 tag 形式存在於本檔（含 # 符號的方括號 metadata 也不行）；agent surface 時即時評（白話講「這條一下午能做完」「這條影響範圍最大」）、不寫進條目。
-->

# Backlog

> 未排程池。活條目 + ≤10 條 [done:] 完成 mixed 在「## 待辦」下、tag 區分。
> 標籤一律前置（寫在標題之前的前綴區）；散文引述標籤字面用反引號包。
> 排程 + 等觸發的驗收條目另見 驗收節點.md（observation-checkpoint capability、独立檔）。
> 累積成熟（N=5）會由 SessionStart hook 自動 surface、不必固定 triage 節奏。

---

## 待辦

- [SOP 候選] [case-count: 1] 啟用第三方一鍵包（預設＋綁定腳本）要當成部署來做：啟用前關掉不想被它寫的聊天、看它帶的上下文／輸出／取樣參數；啟用後對帳它宣稱寫入的每個產物的內容（條目數），不只看檔案在不在——檔案存在不等於裝好，切預設當下腳本就會往開著的聊天寫狀態
  → handoff 20260913 四（剑仙40：Core 世界書檔案存在但 0 條、對條目數才抓到；切預設當下腳本往開著的 Branch #12 寫了狀態 key；預設帶 2M 上下文／32k 輸出，token 暴增）
- [SOP 候選] [case-count: 1] 對一條已在進行的工作線開查之前，先讀它自己的專案 README／既有文件，把「已經回答過的部分」先標出來——否則會把已記錄的事重新查一次、並當成新發現報給使用者，虛報工作的新穎度
- [優化建議] Guardrail A4（多步驟工作必跑 TaskCreate）在某些 session 的工具集裡**沒有 TaskCreate 可用**，此時規則無法被滿足、也無法被判定違反。需要的是「工具不在時該怎麼算」的明文，而不是每次都記一筆違規
- [SOP 候選] [case-count: 1] 凍結判準不等於凍結判讀規則——判準的適用界線（邊界情況算不算觸發）若在判讀中途才定，它會被已看到的資料影響，效果等同事後調整判準
  → handoff 20260906 四（日記 Step 1 驗收：判準收材料前已凍結，但三條適用界線「斷言 vs 猜測」／「摘要 vs 逐字」／「②看心理表現」全在判讀中途才定，其中第一條直接決定否決條件的觸發難度。CLAUDE.md 的 Instrument 只涵蓋量測工具、未涵蓋判讀規則）
- [bug] [P3] character-diary 日記會**替不在場的角色產生一篇「我沒出場」的日記**。2026-09-06 OFF／ON 對照實測（Branch #12、樓層 #1243–#1255）：OFF 態多產生一篇徐婷婷日記，`entry` 寫「這段時間我沒有出現在泳池派對中，也沒有參與……」、`key_events` 為空陣列、`secret` 還編了一句「希望自己之後仍有機會加入他們的行程」。同批 ON 態沒有這篇。花 token 生成、產出零資訊，且為該角色累積了一筆語意上不存在的記憶
  → 2026-09-06 audit 補證據並**升級為 mechanism 問題**（`RP記憶/實驗與驗證/Diary_機制與Prompt_Audit_2026-09-06.md` §4.1）：Branch #12 資料裡徐婷婷三篇（t1275／t1285／t1308）全是缺席報告，且 t1285／t1308 **為不在場角色編造了具體內心狀態**（「其實想加入他們，只是擔心自己會顯得多餘」「我大概會好奇宇璽最後究竟選了誰」）——不只是浪費 token，是虛構 Experience 入庫。因果鏈：`cdCaptureCast` 用正則比對名字、命中條件是「文字裡被提及」而非「有出場」 → 該角色近期日記進 `diaryMemory` → 內容是「我沒出場」 → 模型再寫一篇「我沒出場」→ 又成為下次的 `diaryMemory`，**自我強化**。prompt 已寫「只为有名字、有实际戏份的角色写」、模型並未違反它，**改 prompt 補不了**
- [優化建議] character-diary 日記的 `relationship_with_others` 欄位**每次生成都寫、但沒有任何下游消費者**。查 `index.js` 只有兩處觸及：`:2247` 寫入、`:8700` 編輯時保留，**無任何讀取路徑**；且 `injectRelation` / `enableRelation` 現皆為 `false`。內容品質也不穩：2026-09-06 五組實測中，情境 1 為 `{}`、其餘各異，情境 2 寫「蘇芮萱：熟絡友好的老同學」與該 branch 起點（范婼慧 turn 1241「對她好奇又有些戒備，視作潛在競爭者」）矛盾。要嘛接上消費端，要嘛從 prompt 拿掉
  → 2026-09-06 audit 補兩項〔料〕：① key **未經別名正規化**——角色 `name` 會走 `mainName` 解析歸併別名，但 `relationship_with_others` 的 key 是模型自由生成原樣存入，范婼慧 49 篇裡出現 `大老闆`(5) 與 `大老板`(6)，**同一詞簡繁存成兩個 key**（與已修的 mood bug 同病）；`宇璽`(32) 另成一 key，而蘇芮萱 t1318 寫「宇璽：新認識但迅速親密的大老闆」→ 疑似同一人被拆成三個 key。② 與 `attitude_to_user` **功能重疊**：玩家在 32 篇裡是關係對象，但玩家態度本就有專欄
- [bug] [P2] character-diary 的 `key_events` **沒有 actor 槽位、prompt 對它零要求**——15 條 system 要求裡完全沒提這個欄位，模型收到的全部指示是 JSON 範本裡的「关键事件」四個字。實測 Branch #12 的 **248 條 `key_events` 有 124 條（50.0%）完全沒有主詞**（另 19.4% 只在句中帶代名詞、僅 21.0% 開頭點名角色）。這個欄位的預設寫法是省略主詞、由讀者補上「日記主人」——她自己做的事省略是對的，但**當行為者是玩家而主詞被省略時，欄位本身沒有任何機制阻止它被讀成她做的**。2026-09-06 Step 1 驗收情境 2 的主詞錯置不是偶發筆誤，是這個欄位在一半的時候都處在的狀態。`key_events` 是六個欄位裡唯一屬 Experience 核心、最接近結構化資料的一格，Learned Self 要讀的就是它
  → `RP記憶/實驗與驗證/Diary_機制與Prompt_Audit_2026-09-06.md` §3.2、§4 P1。量測工具界線：分類器只量主詞的有無與位置、**不量歸屬對錯**，規則跑前凍結、跑後未調參
- [bug] [P3] character-diary 的 `is_minor` **在存檔時被丟棄**。`mergeDiaries`（`index.js:2211`）讀 `npc.is_minor` 決定 `promoted`／`cameo`，但 `index.js:2242-2252` 推入 `data.diaries` 的物件裡沒有這個欄位。實測 76/76 全為 `None`。2026-09-05 audit 記的「0/50 全未標」成因不是模型不輸出、是存檔路徑不保存
- [優化建議] character-diary 的 system prompt **從頭到尾沒有定義「已有記憶」的角色**。`user` 訊息用三個標籤把材料分開（`已知角色名单`／`各角色已有记忆(最近历史)`／`本次剧情片段`），但 15 條要求裡沒有任何一條說明前者該怎麼用——沒有「已有記憶是背景，不得把其中事件寫成本次發生的事」這類句子。狀態不是「講得不夠清楚」而是**完全沒講**。這是複製污染（2026-09-05 缺陷 A）的結構條件，雖然 t801 之後 55 篇零復發、但條件仍在
- [構想] character-diary 的 `focusRoles` 一旦非空，prompt（`index.js:861-862`）會**明文要求**「即使这些角色在本次片段中出场较少，也要根据已有记忆与设定，为其补全完整、符合人设的日记」——這是直接指示模型脫離本次劇情證據去編造。目前 `focusRoles=[]` 故未觸發，屬**潛在**高風險。若要用重點角色功能，這段措辭必須先改
- [bug] [P4] character-diary 的世界書同步（`cdSyncWorldbook`、`index.js:2335`，每次日記成功後於 `:4727` 無條件呼叫）在本版 ST 是**死碼**：`cdEnsureWorldbook` 第一道 `typeof getWorldbookNames !== 'function'` 就 return null，而全 `public/`（排除 third-party）搜不到 `getWorldbookNames`／`createOrReplaceWorldbook`／`rebindCharWorldbooks`／`getCharWorldbookNames` 任何定義，`worlds/` 下也無任何 `*-日记记忆` 檔案。**列為 bug 是因為它是誤判來源**——只讀程式碼會得出「日記有常駐（`constant`、depth 4、role system）世界書回饋迴路、繞過 `injectDiary=false`」的錯誤結論；本次 audit 差點如此宣稱，是查 `worlds/` 目錄與 ST 本體 API 才擋下
- [bug] [P3] character-diary 的「检查自动触发」按鈕（`cdCheckAutoTrigger`、`index.js:3295`）計數與真實觸發邏輯不一致：它用 `data._baselineChatLength` 當基線且**不**跳過 `processedFloors`，而真正的 `cdOnMessageReceived`（`:4876`）在 v2.7.3 已修成用 `data.lastFloor` 且跳過 `processedFloors`（`:4911`）
  → 該函式的註解仍寫「与 cdOnMessageReceived 一致的逻辑」，是修改前留下的過期註解
  → 後果：使用者拿這個按鈕看「還差幾樓觸發」時，數字可能與實際不符；它是唯一不花 token 的待處理樓層計數器，卻不能當對帳依據（CLAUDE.md §驗證前置 Gate · Instrument）
  → 另有一個較小的問題：`autoSummary === false` 時（`:3298`）直接 return，連計數都不顯示，觀察模式下這個按鈕等於沒用
  → 2026-09-06 查證（讀 call path、未改程式）。`diary-include-player-messages` 的驗收流程已改為不依賴它（走 `补写指定范围` 指定樓號），故不阻塞
- [bug] [P2] 從歷史 checkpoint 建 SillyTavern branch 時，chat 內容被截斷但 `chat_metadata` 沒有——`createBranch`（`public/scripts/bookmarks.js:186`）只傳 `{main_chat}` 當 `withMetadata`，`saveChat`（`public/script.js:7347`）做 `{...chat_metadata, ...withMetadata}` 把當前完整 metadata 整份複製進新 branch。結果 character-diary 的 `lastFloor` 與 `processedFloors` 會帶著「該 branch 不存在的未來樓號」，`diaries` 也帶著從未發生的事件
  → 症狀：`lastFloor` 會被 `cdOnMessageReceived`（`index.js:4893`）的 `baseline > currentLen - 1` 自癒，但 `processedFloors` 不會清；branch 長回那些樓號時被 `cdGetNewFloors:2165` 與 `cdOnMessageReceived:4911` 的 `_pfSet.indexOf(i) >= 0 → continue` 靜默跳過，那批樓層永遠拿不到日記，log 只說「新增AI不足一整批」。繼承來的日記還會被注入，角色「記得」該分支沒發生過的事
  → 2026-09-06 查證（讀 call path、未改程式）。修法未定：可能是建 branch 後把 `processedFloors` 與 `lastFloor` 依 branch 末端裁切，也可能是擴充在偵測到 `max(processedFloors) > chat.length - 1` 時自癒
  → **邊界**：只發生在「從落後於 `lastFloor` 的 checkpoint 開 branch」；從主線最新位置開 branch 不會踩到。`补写指定范围`（走 `extraFloors`、`index.js:4405`）繞過 `cdGetNewFloors`，不受此坑影響
  → **不在 `diary-include-player-messages` 這個 change 修**（2026-09-06 使用者拍板）
- [bug] [P3] character-diary 的 localStorage 備份池 `cd-data-backups`（`index.js:1926`）跨 chat／branch 共用，但條目只記 `{time, label, diaryCount}`、不記來源聊天或 branch 身分。寫日記（`:4506`）／重新生成（`:8706`）／刪日記（`:8732`）都會推一筆、只留最近 10 筆
  → 風險：在 branch B 按「管理 → 备份/恢复」（`.cd-bk-restore`、`index.js:10570`）選到其實來自 branch A 的那格，會整組覆蓋 `diaries`／`relations`／`archive`／`liveTable`／`cards`，而列表上兩者外觀完全相同、分不出來
  → 手動 + confirm 才觸發，不會自動污染，故 P3。緩解：跨 branch 實驗期間不用備份/恢復，要保險走「導出 JSON」（會落成可自行命名的檔案）
  → 2026-09-06 查證，與上一條同一次 call path 追查

- [SOP 候選] [case-count: 1] 把含反斜線或跳脫序列的內容寫進檔案時走檔案寫入工具、不走 shell heredoc——引號 heredoc 在本環境仍會改寫反斜線，錨點字串在傳輸中就變了形，比對失敗但看不出原因
  → handoff 20260906 四（用 `<< 'PYEOF'` quoted heredoc 傳 python patch script 改 `index.js`，腳本裡的字面跳脫序列被轉成真換行，anchor 連兩次匹配失敗；改用檔案寫入工具寫同一份 patch 即一次通過。同一 session 前兩個不含反斜線的 patch 都成功，差別只在這）
  → **邊界**：只掛「內容含反斜線或跳脫序列」的情形；純文字 heredoc 照用無妨
- [SOP 候選] [case-count: 1] 改一個中間產物的格式或內容之前，先列出它有哪些下游消費者——對照實驗尤其要列，否則「唯一變因」的宣稱會在自己不知情的地方被破壞
  → handoff 20260906 四（日記 scene 納入玩家樓層，實作時才查到 scene 還餵給 `cdCaptureCast` 做登場角色捕獲：ON 態多出的玩家原話可能讓捕獲名單改變、連帶改變注入的「已有記憶」段。design 原本宣稱「兩態唯一差異是玩家行」並不完整，已補進 Risks。本批實測兩態記憶段逐字相同、沒踩到，但那是這批的事實、不是通則）
  → **邊界**：掛「該產物會流向 ≥2 個消費者」的改動；函式內部只用一次的中間變數不必

- [SOP 候選] [case-count: 2] 第三方設計共識／外部設計文件裡關於「程式現況」的事實前提，採用前先逐條對照程式碼與實際資料，再定 V1 範圍——共識常把已存在的機制寫成待新增、把上限寫成常態
  → handoff 20260906 四（使用者貼入的日記管線共識有兩個前提與程式碼不符：「需新增 checkpoint」而 `_lastDiaryChatLength`/`processedFloors`/`lastFloor` 早就存在且只在成功後推進；「每篇讀 40 輪」而實測九次生成每次恰 5 個 AI 樓層、40 只是積壓上限。照原文做會重做已存在的東西；對照後 V1 範圍縮成三件，並多查出一個共識沒看到的問題：日記從未讀過玩家樓層）
  → **邊界**：只掛「將決定實作範圍」的外部文件；純理念討論不必逐條對照。與 CLAUDE.md「引用既有數字前先跑 evidence audit」同源、但對象是外部文件的事實陳述而非 backlog 計數
  → handoff 20260906 四（提議中的「Observation Mode：暫停 auto Diary trigger」查下去發現 `autoSummary` 旗標早已存在於 `DEFAULT_SETTINGS:212`、兩個 gate 都已尊重它、且 `cdSaveSettings` 是 merge 所以主控台設一次就持久——「新功能」實際只缺面板接線 3 行。同一場討論裡我自己也犯了一次：先建議寫 120–180 行的一鍵採樣器，之後才查到 `补写指定范围`（`index.js:8310`）早就能指定樓號寫日記。兩次都是把已存在的機制當成待新增）
- [SOP 候選] [case-count: 1] 同一個 worktree 跑多個 session 時，git 管不到的檔案（gitignore／exclude 裡的，例：`character-diary/index.js`）沒有任何合併保護——改它之前先用跨 session 訊息交接 hash 與備份檔名、改完再通知，讓對方在現況之上改而不是拿舊副本蓋回
  → handoff 20260906 四（mood 修好後發現另一 session 同時在同 worktree 開日記品質線、目標同一個 index.js；用跨 session 訊息交接 hash／備份名／改動行號，對方回覆會在現況之上改、改動區段不重疊）
- [SOP 候選] [case-count: 2] 給盲任務的指示一律用正面表述——「不要做 X」形式的禁令本身就洩漏了 X 存在
  → handoff 20260905 四（本 session 三處洩漏全是我自己寫的禁令：「不要分類或歸群」「不要給出分組名單」「不要猜測生成方式」；另加標題帶家名）
- [SOP 候選] [case-count: 1] 新增一條約束之後，逐條檢查既有要求會不會因此變成無法滿足
  → handoff 20260905 四（修洩漏加的「不得輸出份號名單」讓同一份題幹的第 4 題「有哪幾份最不一樣」變成無法作答）
- [SOP 候選] [case-count: 1] 判讀者之間的多數一致不等於正確——當他們共享同一個設計產物（同一組 probe / 同一個題材分佈）時，會一致地把設計產物讀成發現。分歧的少數方反而可能是對的
  → handoff 20260905 四（第二輪質性層共-4「議題焦點分成可辨識的類別」三家皆指出，性質判定 2:1：Anthropic 與 Google 讀成材料性質差異，OpenAI 讀成「不是差異，是取樣」。開對照表後還原，三筆代表引用分屬三個不同 probe，「第三類」的兩筆同為 A probe——議題焦點跟著 probe 走。少數方是對的，共-4 應降級為 probe 產物）

- [SOP 候選] [case-count: 1] 多個判讀者若共用同一份材料順序，順序效應對他們完全共線——跨判讀者的一致就排除不掉順序假象
  → handoff 20260905 四（原設計三家吃同一份 shuffle，等於順序效應對三家共線；改為各家獨立 seed）

- [SOP 候選] [case-count: 2] 用單一判讀者的說明去定性一個維度會判錯——多來源的說明並列後才判，否則分不出那是判讀者的措辭傾向、還是材料本身的性質
  → handoff 20260905 四（OpenAI 家分析者系統性不記錄身體動作，只看該家會判定「收斂訊號不存在」；另兩家逐字都有）
  → handoff 20260905 四（盲分組三家依據：Google 那票關鍵詞是「情感牽絆／害怕失去聯繫」，正中登記檔寫的「照抄訊號」描述；若只有它一票，該層會被判成照抄。OpenAI 那票主動排除了這個解讀——「切線不是有沒有感情，而是是否影響她對未來的選擇與期待」）
- [SOP 候選] [case-count: 1] 診斷系統行為問題前，先盤點所有會影響該行為的輸入來源並量化佔比，再決定從哪下手
- [bug] [done: 2026-08-29] 角色卡開場白與世界書禁令互相矛盾：范婼慧開場白說「刚才远远看见还他妈以为是看错了」，世界書「絕對避免」寫著「他媽…不是她的詞彙」。修法是改開場白那一句；影響的是每一場**新聊天**的起手（現有 1226 樓那場開場白早已滾出 context）
  → 2026-08-29 量測：她在場 381 則裡禁用詞命中 4 則（≈1%），其中 1 則就是這句開場白（簡體、角色卡帶的，非模型生成）；允許詞「靠/哎呀」命中 182 則（≈48%），禁令大致有效
  → 通則：開場白是每場新聊天最權威的範例——它是「她說過的話」不是設定，具體範例會打贏抽象禁令（規律三）
- [SOP 候選] [case-count: 3] 診斷出根因不等於該修：決定要不要動手前，先回到實際要解決的問題，再過成本 / 風險 / 可歸因 / 效益 / 頻繁程度五關
  → 情色准则自鎖：診斷成立（key 與產物同源、ST 無「只掃使用者訊息」的乾淨解），但只觀察到 1 次、修法要付漏觸發代價 → 先量實際黏著輪數再定，不當場改
  → 不更新 LIWE v2.9.5：唯一有價值的修復非當前痛點，卻會打掉兩項本地修復且新版無替代品 → 診斷清楚但不動
  → 情色准则 key「乳」：只改誤觸發（換成乳房/乳頭/乳溝），不動自鎖——使用者判斷「反正都要玩 NSFW、目前沒影響體驗」，成本方向壓過診斷完整性
  → diary 三個機制缺陷（窗口重疊 75% / 每篇讀前兩篇正文的 inertia / 後 30 篇飽和）全部診斷出來，但建議不動：修窗口會影響現有日記品質，而 Learned Self 要做的正好是日記做不到的那件事
- [SOP 候選] [case-count: 3] 拿下游產物解釋上游行為之前，先確認兩者之間有沒有回饋路徑——沒有回饋就只是觀察紀錄，不是因果證據
  → handoff 20260905 四（把模型輸出的 liveTable 表格當成系統注入的狀態，據此判定污染風險；那段文字是模型根據自己剛寫完的答案編出來的下游產物）
  → handoff 20260829 四（我拿日記推出「角色內部形成了某條學習規則」，但 `injectDiary=false`、日記從未回到 RP，兩條鏈沒有箭頭相連。使用者當場擋下。日記能當指標，不能當解釋）
  → handoff 20260829 六（外部意見提出把 Diary 當 Influence 探針、擴充成 Storage→Injection→Influence→Expression。方向可用，但**成立前提是 `injectDiary` 保持 false**——一旦打開，RP 與 Diary 之間就有回饋路徑，Diary 立刻失去旁證資格。這條 SOP 從「別這樣解釋」升級成「這個工具的有效條件」）

- [SOP 候選] [case-count: 5] [mature: 2026-08-29] [deprecated: 2026-08-30, reason: case-count 5 不實、僅 2 件可稽核證據；已重開誠實計數新條目、本行留作 evidence audit 紀錄] 引用前一個 session 寫下的前提之前，先驗證那個前提本身——繼承來的結論不會因為是自己寫的就免檢
  → **audit 2026-08-30**：本條在 `b92d5e7be` 一次性以 count 4 開出、僅附 1 條證據子彈行，`2a72f3418` bump 至 5 並加第 2 條——5 這個數字沒有 5 條可稽核證據。發現路徑：升級前跑 evidence audit，`git log -p -- backlog.md`
  → 因 validated writer 無降級路徑（見本檔最末 `[bug]` 條），改以「廢舊行 + 開誠實計數新行」達成，**不是默默改數字**。證據子彈行已移至下方新條目

- [SOP 候選] [case-count: 2] 引用前一個 session 寫下的前提之前，先驗證那個前提本身——繼承來的結論不會因為是自己寫的就免檢
  → handoff 20260829 六（`LearnedSelf實驗_設計` 寫「A 組＝沒有告解室的版本、是現狀」，我原封不動抄進諮詢材料。外部 agent 指出 A 其實是「沒有顯式記憶、但保有數百則行為接力」的版本，不是 counterfactual。錯誤在上個 session 產生、在本 session 被放大成對外文件）
  → **與 `[優化建議]` 話講太滿那條同源但不同病**：那條是「講超過證據」，這條是「沒檢查繼承的前提」
  → handoff 20260829 四（**這次照做了、抓到兩個**：handoff 留的 D 組候選「先淡化再多說」正是基線本來就在做的事，用它當 positive control 等於保證測不出來；handoff【當日洞見】的「15/15 都拍墊子邀你坐」機械掃描後是 13/15、#13 完全沒有）
  → **observation（不計入 count）2026-08-30 triage**：要引用舊條的 `[case-count: 5]` 決定升不升級，引用前先查 git log，發現 5 無 5 條可稽核證據。結構完全吻合本 pattern，且把適用範圍從「散文前提」擴展到「機器可讀 metadata 前提」。**但不計入 count**：它由 triage 動作誘發、非自然發生（若今天沒排到 triage，大概率直接讀 5 就往下走），計入等於讓 triage 自己餵養升級門檻。2026-08-30 使用者裁定不算

- [優化建議] [case-count: 5] [mature: 2026-09-05] [deprecated: 2026-09-06, reason: case-count 5 不實、僅 3 件可稽核證據（第 1、2 件無任何 handoff 紀錄）；已重開誠實計數新條目、本行留作 evidence audit 紀錄] 把「在這個條件下觀察到 X」寫成「X 就是這樣」——陳述前先問這個結論的有效範圍多大
  → handoff 20260905 四（在主線聊天測出「注入落在蘇芮萱角色卡後方」，當成實驗分支上也成立；實際上分支的掃描窗口內沒有蘇芮萱、她的卡根本不載入）
  → 前三次記於 handoff 20260829（含「詮釋會錯而痕跡不會」被使用者擋下）
  → **evidence audit 2026-09-06：5 之中只有 3 件可稽核。** 本條在 `b92d5e7be` 一次性以 count 4 開出、
    僅附 2 顆子彈（其一是「前三次記於 handoff 20260829」這種指標而非逐條記載）。
    全文搜 handoff 20260829，「話講太滿」只出現一次實例（`:368`，且**自稱「第 3 次」**），
    加上 `:471` 的第 4 次與 20260905 的第 5 次——**可稽核者為第 3、4、5 三件；
    第 1、2 件在任何 handoff 裡都找不到**（handoff 制度本身始於 2026-08-29，兩件應在此之前、無紀錄）
  → **與 2026-08-30 查出的那條同一個 commit（`b92d5e7be`）、同一種病**：一次性開出高計數、
    證據子彈少於計數。**同一次寫入產生兩條灌水條目，這不是巧合而是當時的習慣**
  → handoff 20260829 六（我寫「近期 context 支配力遠大於新增世界書條目」。正確範圍是「**在這個 probe 下**，近期 context 剛好備有『玩太兇』的現成材料」。不可一般化成「世界書永遠撬不動 177 則 context」。**第 4 次，且這次是被外部 agent 擋下、不是使用者**——模式一樣：把條件句寫成全稱句）

- [優化建議] [case-count: 3] 把「在這個條件下觀察到 X」寫成「X 就是這樣」——陳述前先問這個結論的有效範圍多大
  → **誠實計數版**（上一條因 count 5 不實而 `[deprecated:]`、證據與 audit 過程留在該行）。
    以下三件逐條可稽核、皆有原始出處：
  → handoff 20260829 `:368`（第 3 次）：我說「詮釋會錯，而痕跡不會」，使用者指出**痕跡也會誤導**、
    只是錯的方式不同（t747 日記旁邊是鏡子房，只存那段會讓人以為改變來自性愛）
  → handoff 20260829 `:471`（第 4 次，**由外部 agent 擋下、非使用者**）：我寫「近期 context 支配力
    遠大於新增世界書條目」。正確範圍是「**在這個 probe 下**，近期 context 剛好備有現成材料」，
    不可一般化成「世界書永遠撬不動 177 則 context」
  → handoff 20260905 四（第 5 次）：在主線聊天測出「注入落在蘇芮萱角色卡後方」，當成實驗分支上也成立；
    實際上分支的掃描窗口內沒有蘇芮萱、她的卡根本不載入
  → **邊界**：本條管的是「把條件句寫成全稱句」。與 `[SOP 候選]` 引用前一 session 前提那條不同型——
    那條是沒檢查繼承的前提，這條是**講超過自己證據的範圍**

- [優化建議] [case-count: 7] [mature: 2026-09-05] [paused: 2026-09-06, revisit-by: 2026-12-06] `/end-session` 第一步的 `TaskList` 撈不到本 session 的 completed task（回 "No tasks found"），完成事項每次都得從 context 重建——Guardrail A4 要求跑 TaskCreate，但收工端接不到它的產物
  → **2026-09-06 根因查明（用不會騙人的計數器，非讀 log）**：task store 在 `~/.claude/tasks/<session-id>/`，
    失敗時該目錄下的 `<id>.json` 被清空、只留 `.highwatermark`——**該檔的存在本身就是事件的指紋**。
    本機 14 個 session 目錄普查：**8 個全滅**（有 highwatermark 記著配過 3–13 個 id、0 個 json）、
    **1 個部分清除**（`a40e6244`：hw=8，存活 id 為 1–5 與 9、10，**6/7/8 消失**，9 = hw+1）、
    **5 個完好且全部沒有 `.highwatermark`**。命中率 9/14——**這就是本條記了兩次的「間歇性」的來源**
  → **上游已在追：`anthropics/claude-code` #90709**「Task store silently cleared mid-session;
    new ids resume past the gap」。我方資料另補兩個該 issue 沒有的形態（全滅型、以及部分清除會放過早期 id）
  → **因此本條性質改變**：從「不明原因的工作流缺陷、累積 case 評估要不要立規則」變成
    「已知上游 bug、有 workaround（收工從 context 重建）、等修」。**再累積 case 不會讓它更接近解決**，
    故標 `[paused:]` 停止計數、屆時回顧上游修了沒。2026-09-06 使用者裁定
  → handoff 20260905 四（第 6 個 case：本 session 建 9 條全 completed，收工仍回 No tasks found）
  → handoff 20260830 四（**這條的真相是「間歇性」，不是「壞掉」**：2026-08-30 前兩個 session 收工都撈得到、本 session 又回到 "No tasks found"。原條目文字只描述「撈不到」，沒記到間歇這個性質——而間歇正是它難修也難驗證修好的原因）
  → handoff 20260905 四（本 session 建 4 條 task 並全部標 completed，收工跑 TaskList 仍回 "No tasks found"——第 5 個 case，間歇性再獲確認）

- [優化建議] [case-count: 1] `[case-count:]` 在數什麼未定義：混計「違反 pattern」與「遵守 pattern」，導致一條**越有效**的規則越快到 5、越快觸發升級 surface——計數器方向與它要衡量的東西（值不值得升級）不一致
  → 2026-08-30 triage 發現。實例：「引用前一 session 前提前先驗證」條的第 2 條證據明寫「**這次照做了、抓到兩個**」，遵守被計為 case
  → 連帶待審：已判定證據充足的「設計驗證前先驗證這個驗證」5 條 case 是否也混了「照做」型
  → **2026-09-06 查證：確實混了。** 該條 5 條 case 中至少 2 條屬遵守型——「先查出三個 console 觀察點**才設計得出**可判讀的測試」（做對了）與「Learned Self 實驗**差點**建在錯前提上」（擋下來了）。本條預言的「越有效的規則越快到 5」因此獲得實例證實，**不再只是理論疑慮**。原始 case 住 handoff 20260829 四；該條 backlog 原行若已刪除，逐條內容查 `git log -p -- backlog.md`
  → 附帶提案（**尚未律定**）：只計自然發生的 case；triage / 複盤 / 週報等「正在檢視這條規則」時誘發的觀察記為 observation、不計入
  → 2026-08-30 使用者裁定：先擱著不追，避免拖成大工程擠掉 A/D 實驗

- [SOP 候選] [case-count: 5] [mature: 2026-09-05] [graduated: 2026-09-06, → CLAUDE.md §驗證前置 Gate · Instrument] 量測工具寫完要先用已知答案校準；校準不符時修工具的缺陷、不是把參數調到吻合，且校準完就凍結（hash / commit）不得在看到新資料後再改
  → handoff 20260905 四（驗證腳本自己有 bug、回報 2 個假 FAIL；跑陰性對照對調 M01/M02 才證明那把尺抓得到錯）
  → handoff 20260905 四（三層對齊腳本把 `附 · fable（不計票）` 的票算進 Google，Google 顯示 4/18、實為 0/18，8 則家間分歧全部消失。是「逐家計數須等於 4/8/0」這道對帳擋下的，不是看出來的）
  → handoff 20260905 四（切片洩漏檢查未先跑陰性對照就解讀，2/75 命中差點誤判成資料洩漏；補跑對照後測出誤判基線本就約 1/75）
  → handoff 20260905 四（自寫的編碼包驗證腳本有一項寫成 `... or True`、恆真永遠 PASS；另有「23 項檢查」為硬寫常數、實際 19 項。檢查工具自己沒被任何已知答案校準過）
  → handoff 20260830 四（A/D 丟球判準腳本初版跑基線得 14/15、期望 13/15。查出是斷句沒把 `「」` 與換行當句界、旁白的「你」被黏進對白問句造成偽陽性——修的是斷句缺陷。修完 13/15 且組別分佈 A3/B5/C5 全中。同時記錄一個**不修**的保守偽陽性，偏誤方向對 positive control 安全）
  → 與已升級的 `CLAUDE.md §驗證前置 Gate` Observation 那一問相鄰但不同：Gate 問「觀察點存不存在」，這條問「儀器準不準、以及誰有權在什麼時候改它」。若累積更多 case，可考慮併入 Gate 而非另立載體

- [SOP 候選] [case-count: 5] [mature: 2026-09-05] [graduated: 2026-09-06, → CLAUDE.md §驗證前置 Gate · Occurrence] 驗證某個訊號「有沒有出現」之前，先確認會產生該訊號的事件真的發生過——否則 log 上的有與無都只代表什麼都沒跑
  → handoff 20260830 四（A/D 實驗驗 uid 21 注入：使用者貼的 log 結尾是 `--- DONE (DRY RUN) ---`，查聊天檔 swipes 仍為 5 → **當時尚未 swipe**。DRY RUN 在載入聊天時就會跑、不需生成。若採信，會在「注入從未經過真實生成」的狀態下開始收資料）
  → handoff 20260905 四（codex 與 agy 兩家外部判讀者呼叫皆回 exit code 0，輸出內容才是「額度耗盡」與「權限被自動拒絕」；只看回傳碼會把「根本沒跑」記成「跑過了」）
  → handoff 20260830 四（**同日鏡像版**：停用 uid 21 後回報「重啟後確認沒有」，查聊天檔 swipes 仍為 10 → 一樣還沒 swipe。上次是拿 DRY RUN 證明「有」，這次是在沒有生成的 console 裡證明「沒有」）
  → 兩次都是靠**查聊天檔 swipes 數**擋下的、不是靠更仔細讀 log。**在 UI 之外找一個不會騙人的計數器**，比加強判讀可靠
  → 與已升級的 `CLAUDE.md §驗證前置 Gate` Observation 不同：Gate 問「觀察點存不存在」（設計時），這條問「觀察的那一刻，該發生的事發生了沒」（執行時）
  → handoff 20260830 四（**第三個 case，搜尋層的變體**：判定「confession room 那件事在資料裡不存在」時只搜到第二段告解場景（`1082-1104`，蒙眼＋跳蛋），沒搜到第一段（`683-711`）。實際上 `uid 20` content 逐字對應 `697-701`。**否定性結論在宣告前要先確認搜尋範圍涵蓋了整個可能空間**——這條錯誤結論當時成了另一條 SOP 候選的唯一證據，該條已因此 `[deprecated:]`。前兩個 case 是「事件沒跑就讀 log」，這個是「沒找遍就說沒有」，同一句話的兩個層次）
  → handoff 20260830 六（**第四個 case，構念層的變體，也是代價最大的一次**：Learned Self 機制測試的 baseline
    ——「她不會在長期事情上投入自己的意願」——建立在歷史三個資料點全判 0（`347`／`695`／`1138`）。
    但回頭看提問側：`347` 問的是過去到現在、`1137` 是宇璽自己在想未來**根本沒問她**、`695` 與未來無關。
    **歷史上從來沒有人直接問過她長期的事並要她表態**，那個 0 不是她的傾向、是沒人問。
    今天三句直接 probe 一投，OFF 組 9 則有 8 則直接判 2，停止條件觸發、整輪作廢。
    前三個 case 是執行層與搜尋層，這個是**構念層**：把「沒觀察到 X」讀成「X 不存在的傾向」，
    而觀察條件下 X 從未被觸發過。原始記錄見 `RP記憶/實驗與驗證/LS_MechanismTest_原始記錄_2026-08-30.md` §五）
  → **代價對照**：前三次擋下的成本是幾則資料或一次誤判；這次沒擋下，成本是一整輪實驗設計
    （換靶、寫兩份事前登記、建四個 branch、收 9 則資料）。**同一條規則在不同層級的漏接，代價差一個數量級**

- [bug] [done: 2026-09-06] `character-diary` 日記的 `mood` 欄位簡繁未歸一——同一情緒被存成兩個 key（實測 `开心` 25 篇 vs `開心` 12 篇、`紧张`/`緊張`、`平静`/`平靜`）。prompt 的列舉值是簡體，但模型會跟隨劇情語言輸出繁體，落庫時未正規化。任何對 mood 做統計或篩選的功能都會少算一半
  → handoff 20260905 四（Diary audit：范婼慧 50 篇，8 個列舉值實際只出現 5 種，「開心」合計 74%。設計基礎記載「簡繁歸一」是本地既有修復之一，但顯然沒蓋到 mood 這格）
  → 2026-09-06 已修（程式層）：`index.js` 加 `cdNormalizeMood`（情緒用字的繁→簡字表），掛在三個寫入點（mergeDiaries／編輯器儲存／重生成替換）+ `cdGetData` 讀取時就地歸一既有資料。校準：14 條已知答案全過；真實聊天檔 8 個 jsonl 共 424 筆 mood，歸一前 8 個 key → 後 5 個，總數對帳一致。備份 `index.js.bak_mood_normalize_20260906_122359`。運行層已驗（ST 8500 重載後）：記憶體 `diaries['范婼慧']` 50 筆全簡體、硬碟同檔仍 15 筆繁體，差異只可能來自本次歸一。`cdGetData: mood 簡繁歸一` 那行 log 在 console 沒看到，原因未查（不影響判定）

- [SOP 候選] [case-count: 1] 一個欄位若有專用寫入器，就不要用 Edit / 字串替換去改它——寫入器維護的不變式不在你手上，繞過它不是省一步，是把檔案改成不合法狀態
  → handoff 20260905 四（我用字串替換把 backlog 的 `[case-count:]` 由 4 改 5、繞過 `backlog_mark.py`。走 writer 時達 5 會在同一交易自動補 `[mature:]`，手改沒補，lifecycle-invariant 破了、此後**所有**普通寫入被拒；是收工跑 list 診斷才發現，需用 `repair reconcile_mature` 才修得回）

- [SOP 候選] [case-count: 1] 一個動作若會讓自己從此非盲，先把所有依賴盲性的下游決策寫死並凍結，再做那個動作——順序決定證據價值，而順序不用花錢
  → handoff 20260905 四（原排程是先開第二輪質性 mapping、再寫第三輪事前登記。改為先凍結登記（sha256 542fa2a6）再開 mapping。開完發現機械層與質性層獨立指向同一個 probe（C 組）——而登記檔已在不知情下為 C 組寫死單獨門檻。順序反過來的話，那個門檻就變成「看過答案才補的」）

- [優化建議] [case-count: 4] 剛升級成規範的規則，同一個 session 內就沒擋住同型錯誤——規範層對「當下沒想到要套用它」無能為力，而那正是它要防的失敗模式
  → handoff 20260906 四（今天上午把 `Occurrence`（含「搜尋層：沒找遍就宣告不存在」）寫進 `CLAUDE.md §驗證前置 Gate`。
    同一天下午，我只看了 `work_status_register update --help` 就向使用者宣告「writer 不支援改 parent」——
    實際上 `repair --set-parent` 一直都在。**這是搜尋層的逐字複製：宣告一個否定性能力結論，而沒找遍可能空間**）
  → 對照組：同一天的另一次我**有**套用（讀 `backlog_mark.py` 得到降級 bug 的形狀後，改用 scratch 副本實跑，
    結果推翻了讀 code 的結論）。差別在那次我**當場想起**要驗，這次沒有——**規則本身沒有觸發機制**
  → 與 `[構想]` 驗證前置 Gate 第二層直接相關：該條刻意延後、等「這條規則被證實真的有幫助」。
    本 case 提供的是**反向證據**——規則有幫助（對照組），但只在被想起時有幫助
  → **邊界**：本條不是主張「所有規則都要 hook」。它要問的是「規範層的失效率有多高、值不值得為此付 enforcement 的成本」，
    在累積到足以回答之前不動作
  → handoff 20260906 四（第 2 件：CLAUDE.md 寫 ST 在 8000、curl 8000 得 000 就向使用者宣告「ST 沒在跑」，config.yaml 其實是 8500、ST 正開著——又是 Occurrence 搜尋層「沒找遍就宣告不存在」，離規則寫進 CLAUDE.md 不到一小時）
  → handoff 20260906 四（第 3 件、同 session：只查外層 git 的 gitignore 就斷定 `character-diary/index.js`「不在版控裡」、據此告訴使用者 worktree 隔離不到；該目錄自己就是 git repo，是另一 session 查出來的）
  → handoff 20260906 四（第 4 件、另一 session elephantfish-03、同日：把 `character-diary/index.js` 寫成「版控外、`.bak` 是唯一回退」進 openspec proposal/design，只憑外層 gitignore 沒跑 `git rev-parse --show-toplevel`；使用者要求先查證再定 rollback，一查是獨立 repo、且上游已到 v2.13.0。兩個 session 各自獨立犯同一件：規範層對「沒想到要套用」的失效率再添一筆）

- [SOP 候選] [case-count: 1] 給判讀者（人或 LLM）的示範例句必須與待判材料異場景——範例取自語料等於把答案示範出來，事後分不出一致性是獨立判斷還是 priming
  → handoff 20260830 四（A/D 盲編碼第一輪，我給編碼者的正例是「你剛才好像跟誰聊得很開心嘛。那是誰啊？」，幾乎是 `10-A` 原句。三人一致判該則為丟球，但有多少來自 priming、本輪分不出來）
  → 使用者 review 外部包時提的替代句「前面晃了這麼久，說說你都碰到什麼了」幾乎是 `6-A` 原句——**同一個坑差點踩第二次**，保留句型、換場景才解決
  → 已加機械檢查：範例區不得出現語料常用詞。**這種檢查可以在做包的當下就跑，不必靠人眼**

- [SOP 候選] [case-count: 1] [deprecated: 2026-08-30, reason: 唯一 case 經查為無效證據：2026-08-30 實查告解場景有兩段（683-711 / 1082-1104），當時只搜到後者即判定示意事件不存在，實際 uid 20 content 逐字對應 turn 697-701。pattern 邏輯仍成立但無有效 case，已另開誠實計數新行] 用來說明結構的示意例子，不可直接當成落地內容的素材——示意句的功能是講清楚形狀，不是提供事實；要落地前必須回原始資料查證它存不存在
  → handoff 20260830 四（Learned Self MVP：使用者舉 confession room「她第一次談起在美國那些孤單的日子，宇璽沒有同情她而是說她很勇敢」說明三層結構，我一路把它當成 LS-001 的來源事件。實查聊天檔——**那件事不存在**。真實的告解室事件是蒙眼＋跳蛋＋獎勵驅動下說「我不介意你跟別人」，與示意內容無一相符）
  → **差一步就寫進常駐注入**：一條憑空捏造的「經驗」會永久成為角色人格的一部分，且事後極難發現
  → **擋下它的不是我更謹慎，是使用者要求「先跑候選盤點、不要指定事件硬湊」**。盤點同時撈出真實可用的 `turn 1161`
  → 與 `[SOP 候選]` 引用前一 session 前提那條**不同源**：那條是自己寫的舊結論沒重驗，這條是**他人給的示意句被當成事實**——來源可信度高反而讓它更難擋
  → ⚠️ **上方 line 140 那條證據已於 2026-08-30 查明為錯誤**（留原文作 audit）：告解場景在聊天檔裡有**兩段**（`683-711` / `1082-1104`），當時只搜到後者（蒙眼＋跳蛋）就判定示意事件不存在。實際上 `uid 20` content 逐字對應 `turn 697-701`（「點餐都怕講錯」「怎麼都沒有人問我吃飯了沒」「不是要討拍啦」「你是第一個跟我說『不會可憐』的人」皆逐字命中）。**示意例子是真的，我當時沒查全**

- [SOP 候選] 用來說明結構的示意例子，不可直接當成落地內容的素材——示意句的功能是講清楚形狀，不是提供事實；要落地前必須回原始資料查證它存不存在
  → **狀態：合理的候選規則，尚無有效 case**（故不掛 `[case-count:]`——0 不是「數過是零」與「還沒開始數」的差別所在，兩者對 N=5 surface 的行為相同）
  → 原條目（line 139）因唯一 case 被查明為無效證據而 `[deprecated:]`，證據與歷史留在該行
  → **這次的錯誤本身不計入本條**：它是「搜尋不完整導致誤判不存在」，屬於**驗證覆蓋率**問題，與本條的「示意句被當成事實」不同型；歸入 `[SOP 候選]` 驗證訊號那條或另立更貼切

- [SOP 候選] [case-count: 1] 更新一個比例裡的某一項時，另一項也要重新量——只更新一半等於用一半過期的資料推新結論
  → handoff 20260830 四（設計基礎規律四：實測世界書常駐由 18,989 降到 5,346 字，我原本要沿用舊分母 liveTable 668 字直接寫成 1:8。實測 `liveTableData` 現為 844 字。且舊的 668 未載明量測方法、與 844 不必然同尺，最後寫成區間 1:6～1:8）
  → **同一事件的第二個教訓（不另開條目，避免一個 episode 灌兩次計數）**：規律四的「角色因經歷而改變在結構上不可能」是**由 1:28 推出來的**。前提換了就得回頭撤結論，不是把 28 改成 8 就算更新完

- [SOP 候選] [case-count: 1] 發現一個 observable 的那批資料，不可同時當成它的對照組——要用它下決策就另收一批乾淨的
  → handoff 20260830 四（機制測試第一輪 9 則 OFF 撞天花板後，逐則翻看才發現真正穩定的是「延後處理」。我提議直接拿那 9 則當第二輪的 OFF 對照，使用者擋下：即使換三位盲編碼者重判，也洗不掉「因為它在這批資料上特別漂亮才被選中」。改為那 9 則定位成 Discovery set、另收 9 則 Confirmatory OFF——結果 Confirmatory 也是 9/9，複製成功）
  → **Tier 1 依據是前瞻性的**（1 occurrence）：每次從資料裡看出新模式都會遇到，而代價是一整輪實驗設計的可信度。多收一批的成本遠低於「結論建立在選擇性發現上」
  → 與 `[SOP 候選]` 校準凍結那條**相鄰但不同型**：那條管「儀器不可在看到資料後被調整」，這條管「發現用的資料不可兼任證據」

- [bug] backlog validated writer 只有升級路徑、沒有降級路徑，count 由 5 降為 2 會留下自相矛盾行且 agent 無合法路徑修
  → root cause：`hooks/lib/backlog_mark.py` 三處——`_maybe_atomic_mature`（`:547`）在 N<5 時「unchanged」、不移除既有 mature 標籤；`repair` 的 `remove mature`（`:721`）**無條件**擋下（註解意圖是防「count≥5 卻無 mature」，但沒判斷 count，降級情境被一起擋）；`reconcile_mature`（`:693`）只刷新日期、不移除，且要求先存在 lifecycle-invariant 診斷
  → 症狀：`case-count set: 2` 後留下 `[case-count: 2]` + `[mature: 2026-08-29]` 併存
  → 2026-08-30 triage 遇到。繞道方案：舊行蓋 `[deprecated:]` + 另開誠實計數的新行
  → **2026-09-06 實跑更正（alpha.15 仍未修，且上面兩行的描述不準）**：在 backlog 副本上逐步實測四條路徑，
    結論是**降級這個操作根本不存在**、不是「降級會留下矛盾行」——
    ① `case-count` 只有 `bump`（+1）與 `set`，而 `set` 對已有計數的條目**直接拒絕**
    （「此條目已有 case-count、set 僅限尚無計數的 starter」），所以 5→2 連第一步都走不了；
    ② `repair remove mature` 無條件拒絕（同上行所述，確認未修）；
    ③ `repair reconcile_mature` 拒絕「無 lifecycle-invariant 診斷、無適用對象」；
    ④ 而 `backlog_parser.py:1013` 的 lifecycle-invariant **只判單向**（count≥5 缺 mature），
    反向的 `count<5 卻有 mature` **不會被診斷**——即使手改進去，`list` 也不會報。
    因此上面「症狀」那行描述的狀態，只可能發生在 starter 條目、不可能由已有計數的條目降級而來
  → **這次是「讀 code 得到的結論」與「拿已知答案實跑」不一致的實例**——`CLAUDE.md §驗證前置 Gate · Instrument`
    升級後第一次套用就抓到。若要當該注的證據，見 驗收節點.md 2026-09-20 那條

- [bug] `backlog_triage.py execute` 的 graduated 清理**只刪條目行、不刪其下的子彈行**，
  被刪條目的 `→ …` 子彈會靜默改掛到上一個條目底下，看起來像是那條的證據
  → 2026-09-06 實遇：刪 graduated 的「設計驗證前先驗證這個驗證」後，它的 7 顆子彈
    （5 條 handoff case + evidence audit + 升級形式）全部變成上一條「診斷系統行為問題前…」的子彈，
    而該條原本 `[case-count: 1]` 且沒有任何子彈——**憑空多出 7 條看似證據的東西**
  → 危險性在於它**朝著「證據變多」的方向錯**：正好是 evidence audit 要防的那種假象，
    且 `list --json` 的 `diagnostics` 回 `[]`、不會報
  → 本次處理：人工把 7 行刪掉（備份 `backlog.md.bak_before_l94_delete_20260906`）。
    **下次跑 graduated 清理後必須人工檢查上一條有沒有多出子彈**，直到 runner 修好

- [構想] 驗證前置 Gate 第二層：把 Preflight 做成 harness 的狀態轉移條件（contract 定義 + hook 最小機械 enforcement），沒過 gate 就不能往下走
  → **刻意延後**（2026-08-30 使用者裁定）：等「這條規則被證實真的有幫助」或「確定現行規範層需要 hook 輔助」時才開發。理由——現在直接設計 enforcement，等於在一個還沒跑過的流程上做 gate，違反規則自身
  → 已查證的設計約束：`hooks/hooks.json` 只有 `SessionStart` / `Stop` / `PreToolUse`(`Edit|Write`) 三個掛點；ST UI 裡 swipe 跑實驗**不產生任何 hook 事件**，gate 掛不到「執行前」。可機械擋的位置是**結果被兌現前**（寫結論 / 寫 `[graduated:]` 都是檔案寫入）
  → 現成範本：`hooks/backlog_write_guard.py`（PreToolUse 真 gate、官方 `permissionDecision: "deny"` 契約、目標未確認 fail-open / 確認後 fail-closed、薄殼 + 純 lib 分層）
  → 已知漏洞：「是不是 decision-bearing validation」是自我宣告，而要防的失敗模式正是 agent 沒認真想——擋在兌現端可緩解（兌現動作客觀可辨識，不依賴事前宣告）
  → hook **只做機械 enforcement**（三欄有沒有填），內容合不合理由 agent / reviewer 判斷——不可讓 LLM 判「你寫得對不對」，那本身又是個未驗證的儀器
  → 屬 plugin capability 變更，走 opsx change、不走 direct PR

- [優化建議] [case-count: 2] 今日 handoff 的存在性檢查掛在 Stop hook，但 handoff 語意上是 session 結束才產生的產物——兩者時機不對齊，開工盤點階段（第一次 yield）就會被 block，逼出「還沒做事就要寫完成事項」的兩難
  → handoff 20260905 四【當日洞見】（Session 10:57：只跑了開工三步驟，Stop hook 即要求今日 handoff 存在。當時處理為照六欄模板如實建首個區塊、不虛構完成事項；明記「待累積第二個 case 後再考慮開條目」）
  → handoff 20260906 四【當日洞見】（Session 09:57：完全同型復現，第 2 個 case，前述條件滿足）
  → 議題：檢查該掛 `SessionEnd` 而非 `Stop`；或 Stop 保留但改為 ⚠️ Warn、由 `/end-session` 承擔 block。**尚未查證** `SessionEnd` 在本 plugin 的 `hooks/hooks.json` 是否為可用掛點（現已知只有 `SessionStart` / `Stop` / `PreToolUse`），開發前須先確認
  → 邊界：append-only 的首區塊本身不是壞事（它讓開工盤點留下紀錄）。要修的是「被迫在無完成事項時交出六欄」這個時機錯配，不是取消檢查
