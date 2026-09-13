# Session Handoff — 20260913

## Session 12:36

### 一、本 session 主題

Session 開工：跑開工三步驟（`/work-status` → 讀 20260906 最新區塊 19:05 → 提三條優先建議），
接著回答使用者一個獨立小問題：repo 根目錄新出現的兩個 JSON
（`夏瑾 V1.0 Beta.json`、`思维链转为details.json`）「怎麼更新」進 ST。**未改任何程式、設定或 RP 資料。**
本 session 主線主題尚未指定。

### 二、完成事項

- 跑 `/work-status`：主線「RP 記憶系統重構」維持正在做 15 天；日記品質線 Step 2 停在「候選 A／B 待挑」7 天；
  Learned Self 的 NEXT（載體搬 LIWE）8 天；6 條小任務「還沒開始」15 天；完整性提醒無
- 讀 20260906 handoff 19:05 區塊（四層 audit、Step 1 歸檔、Step 2 候選 A/B）
- 提三條優先建議：① Step 2 直接挑候選 A（`key_events` actor 契約，驗收可數、且能順便達標驗收節點第 58 行）；
  ② 若還沒跟第三方談，先整理對外版報告材料；③ 日記線等討論時切去 LS 的 LIWE 載體設計討論
- 鑑定兩個新檔：`夏瑾 V1.0 Beta.json` 是 Chat Completion 預設設定檔（DeepSeek R1、44 條 prompt）；
  `思维链转为details.json` 是 Regex 腳本（`<thinking>` → `<details>`，placement AI 輸出、markdownOnly+promptOnly）
- 對帳：live ST（`D:/AI/SillyTavern`，v1.18.0）`OpenAI Settings/` 現有 `夏瑾 天琴座 Beta 2.0 東杰修改版` 與
  `…現用預修版`（現用），與新檔共用同一批 prompt identifier 但 140 vs 44 條、共有 44 條中 27 條內容不同、
  順序與參數皆不同 → **新檔不是現用預設的新版本，匯入不會合併使用者自己的修改**。
  全域 regex 4 條中無同名腳本、`data/` 全文搜尋也無
- 給出匯入路徑（UI 操作、不重啟）：預設 → 「AI 回應設定」→「匯入預設設定檔」；
  Regex → 「擴充功能」→ Regex →「Import」→ 目標建議選 preset 綁在新預設上；提醒 ST 開著時不要手改 `settings.json`

### 三、未完事項 / 接力棒

- [#接力] 等使用者回答 `夏瑾 V1.0 Beta` 的來源（作者新一代？要不要換過去？）；若要換，
  下一步是列出「東杰修改版 vs 現用預修版」的差異當作使用者自改清單、再決定搬哪些進新預設
- [#接力] 本 session 主線主題未定；三條優先建議見上

### 四、洞見 / 反省

**【紀律接力】**

- （無新累積；開工 + 單題問答）

**【當日洞見】**

- 「怎麼更新」這種問句先查對象是什麼再答：兩個檔看名字像同一包，實際一個是預設、一個是 regex，
  進 ST 的路徑與存放位置完全不同；而且拿新檔跟現用預設對了 identifier 才知道它不是「升級版」，
  直接教匯入會讓使用者以為自己的修改跟得過去

### 五、檔案異動

- `文檔/handoff/session-handoff-20260913.md` — 新檔，本區塊
- 未追蹤（使用者放入、非本 session 產生）：`夏瑾 V1.0 Beta.json`、`思维链转为details.json`（repo 根目錄；不屬版控）

### 六、下一步建議

1. 先回答新預設來源與是否換用，再決定要不要做修改清單搬移
2. 主線仍建議挑候選 A（`key_events` actor 契約）開 Step 2 change；寫量測腳本時記得做已知答案校準 + hash 凍結（驗收節點第 58 行 2026-09-20 到期）


## Session 13:27

### 一、本 session 主題

開工三步驟後，主線暫放，處理使用者丟進來的三個第三方檔：鑑定 `夏瑾 V1.0 Beta`（作者新一代預設，使用者決定先不用）
與 `思维链转为details`（regex），安裝 `剑仙40`（預設＋綁定腳本＋兩本世界書）並修好 Core 世界書空殼、
把誤寫進 Branch #12 的狀態 key 清掉、把 token 暴增歸因到預設帶的 2M 上下文。**未改任何程式；改動全在 live ST 的 `data/`（不進版控）。**
（本 session 工具集無 TaskCreate，完成事項由對話重建。）

### 二、完成事項

- 鑑定 `夏瑾 V1.0 Beta.json`：Chat Completion 預設（DeepSeek R1 向、44 條 prompt）。與現用 `夏瑾 天琴座 Beta 2.0 東杰現用預修版` 共用 identifier 但 140 vs 44 條、
  共有 44 條中 27 條內容不同、順序與參數不同 → 不是升級版。對照 `Downloads/夏瑾 天琴座 Beta 1.0.json` 找出使用者自改的 **9 條 prompt**
  （字數 600–900／🖋️默认／✅基础创作准则／⚙️防抢话／⚙️人称／⚙️对白分离／🧭保守／📘写作指南／🛡️准则结束，全部改為繁中台灣＋自訂規則）與參數（OpenRouter gemini-3.7-flash、輸出 2500、上下文 64k）。
  使用者決定先不用，未動
- 鑑定 `思维链转为details.json`：ST regex 腳本（`<thinking>` → `<details>`，placement AI 輸出、markdownOnly＋promptOnly）。給了 UI 匯入路徑，未匯入
- **安裝 `剑仙40`**：`40.json` 以正確名稱 `cp -n` 進 `OpenAI Settings/剑仙40.json`（ST 匯入用檔名當預設名，`openai.js:4668`）。使用者選用後腳本自動綁定並建了兩本世界書
- **修 Core 世界書空殼**：`剑仙JX Native Core Source…json` 建出來是 21 bytes、0 條（Style 那本 37 條正常）。從腳本內嵌的 `JX_STABLE_CORE_RAW` 抽出 38 條、
  照 Style 檔的欄位形狀落檔；對過腳本後段那份 `jxNativeRowsValid`（≥38 條 + `JX16_MODE_DM`／`DM_FP_ACTOR`／`MODE_CHAT`／`MODULE_IMMERSIVE_EXPRESSION`／`EVENT_ADAPTER_NARRATOR`）。
  使用者 F5 後：檔案 mtime 未變（腳本認了 existing）、`settings.json` 有存 → 安裝完成。空殼備份 `…json.bak_empty_before_fill_20260913`
- 說明剑仙的使用者面：唯一入口是酒館助手腳本按鈕「剑仙40」→ 浮動「剑仙输入控制台」，五個模式（DM_FP_ACTOR／DM／DIRECTOR／CHAT／NARRATOR）各有填空槽，
  填完塞回 ST 輸入框再送；`JX16_SWITCH_TO_*` 是腳本內部世界書 key、不是給人打的
- **清 Branch #12**：切預設當下腳本往開著的 #12／#13 寫了 `chat_metadata.jx_rpr_rc01_state_isolation_v1`（空白草稿）。以 #11 為基準比對確認 #12 只多這一個 key，
  移除後 1456 則訊息 hash 相同、metadata 回到 13 個 key。備份 `…Branch #12.jsonl.bak_before_jxkey_strip_20260913`。#13 是今日 13:05 從 #12 分出的測試分支、保留
- **token 暴增歸因**：剑仙40 預設帶 `openai_max_context 2000000`（被模型壓到 350,000）、`openai_max_tokens 32007`，vs 夏瑾 64k／2500；#13 正文 56.5 萬字，35 萬會送出六成歷史。
  建議 64k／4k（ST 可用空間 = 上下文 − 輸出上限），使用者改後回報「好多了表現也正常」
- backlog 新開 `[SOP 候選] [case-count: 1]`「啟用第三方一鍵包要當成部署來做」（行 80）

### 三、未完事項 / 接力棒

- [#接力] 主線未動：日記品質線 Step 2 仍在「候選 A／B 待挑」；LS 的 LIWE 載體設計討論仍掛 NEXT
- [#接力] 夏瑾 V1.0 Beta 若要換用：做「東杰版」合併檔（9 條規則濃縮成 1–2 條新 prompt 插在「情节设计/文风细节」後、字數、API 選擇 DeepSeek vs OpenRouter 要先問）。使用者說先不用、未登記
- [#不重議] 剑仙 Core 空殼成因只推到「24 條 `before_character_definition` 型條目疑似被酒館助手欄位驗證擋下」、未看 console 證實；已用內嵌原始資料繞過，除非再空掉否則不追
- [#提醒] 剑仙40 只在 #13 玩；#13 上 character-diary 照跑（全域 interval=5），那些日記不算進日記線統計。回 #12 前先 F5（避免記憶體舊版把 key 寫回）
- [#提醒] 兩本剑仙世界書被腳本加進 `world_info.globalSelect`（全域啟用）；75 條全 disabled、不走 ST 掃描注入，但切回夏瑾時它們還在全域清單裡

### 四、洞見 / 反省

**【紀律接力】**

- Occurrence 規則今天第三種形態：**檔案存在 ≠ 裝好**。剑仙腳本宣稱裝了兩本世界書、`worlds/` 也真的多了兩個檔，但 Core 那本是 21 bytes、0 條。
  抓到它的是「對條目數 38/37」這個計數器，不是「檔案在不在」。前兩天是「事件沒跑就讀 log」「程式碼路徑存在就當行為發生」，
  今天是「產物存在就當內容完整」——同一條規則，計數器要選到內容層
- 切換一個帶腳本的預設**本身就是有副作用的動作**：腳本在切換當下就往開著的聊天寫 `chat_metadata`（#12 中招），沒有任何生成發生。
  已開 `[SOP 候選]`「啟用第三方一鍵包要當成部署來做」（backlog 行 80）

**【當日洞見】**

- 「怎麼更新」這種問句先查對象再答：兩個檔看名字像同一包，實際一個是預設、一個是 regex，入口不同；拿新檔跟現用預設對 identifier 才知道它不是升級版
  （44 vs 140 條、27 條內容不同），直接教匯入會讓使用者以為自己的 9 條繁中規則跟得過去
- 剑仙 Core 空殼的成因是推的（24 條 `before_character_definition` 型條目疑似被酒館助手欄位驗證擋下）、未看 console 證實；修法走腳本自己的第二條路
  （內嵌原始資料落檔），驗證用它後段那份 validator 的條件（≥38 條 + 5 個 key），F5 後檔案未被改寫 → 腳本認了
- token 變多的主因是預設的上下文上限（2M → 被模型壓到 35 萬 vs 原本 64k），而且 ST 是「上下文 − 輸出上限」算可用空間，32k 輸出先砍掉一半；建議 64k / 4k，使用者實測正常
- ST 匯入預設用**檔名**當名稱（`openai.js:4668`），不看檔內 `name`——`40.json` 要先改名再匯

### 五、檔案異動

**版控內（elephantfish，本 commit）**

- `backlog.md` — 新開一條 `[SOP 候選]`（行 80）＋證據行
- `文檔/handoff/session-handoff-20260913.md` — 本區塊（12:36 開工區塊為本日首塊）

**未進版控（使用者放入 repo 根、第三方內容）**：`40.json`、`夏瑾 V1.0 Beta.json`、`思维链转为details.json`

**live ST `D:/AI/SillyTavern/data/default-user/`（不在版控）**

- `OpenAI Settings/剑仙40.json` — 新增（`cp -n`）
- `worlds/剑仙JX Native Core Source｜Alpha04-SE03-RC01｜V16能力底座.json` — 由 0 條補為 38 條；備份 `.bak_empty_before_fill_20260913`
- `worlds/剑仙JX Style Distribution Source｜Alpha04-SE03-RC01.json` — 腳本自建（37 條，未動）
- `chats/银趴邮轮/…Branch #12.jsonl` — 移除 `jx_rpr_rc01_state_isolation_v1`；備份 `.bak_before_jxkey_strip_20260913`
- `settings.json` — 由 ST／腳本自行寫入（active preset、globalSelect、preset scripts）；使用者手動調上下文 64k／輸出 4k

**未進版控（備份）**：`backlog.md.bak_before_thirdparty_pack_20260913`

**擴充 repo（character-diary）**：未動

### 六、下一步建議

1. 主線不變：Step 2 挑候選 A（`key_events` actor 契約），寫量測腳本時做已知答案校準 + hash 凍結（驗收節點第 58 行 9/20 到期）
2. 剑仙40 只在 #13 玩、#12 保持乾淨；#13 產出的日記不算進日記線統計
3. 夏瑾 V1.0 Beta 要換用時再叫我做「東杰版」合併檔（9 條繁中規則 + 字數 + API 選擇）


## Session 16:32

### 一、本 session 主題

日記品質線 Step 2：開立、實作、驗收並歸檔 change `diary-key-events-actor`——給 `key_events` 加 actor 契約（「主体：事件」、日記主人也寫主名、不改 schema）。
順序守住「分類器先凍結、再改 prompt」。四個 Step 1 測試 branch 同段樓層重跑，五項標準全達標，使用者接受。順帶提早結清驗收節點 9/20 的 Instrument 一問。
（本 session 工具集無 TaskCreate，完成事項由 tasks.md 27/28 與對話重建；擴充 UI 的操作全由使用者執行，agent 讀檔對帳。）

### 二、完成事項

- **規劃**：`/opsx:propose` 產出 proposal／design／specs／tasks；使用者三點校正已落文件：分類器 commit 必早於 prompt commit、248 條改稱「凍結基線」非 ground truth、標準 2 定義為「開頭是實際行為者（不限日記主人）＋全形冒號」
- **查現況**：`cdBuildCombinedPrompt` 無呼叫點（死碼，不動）；`key_events` 13 個讀取點全為字串處理；`diaryMemory` 只注入 entry；Branch #12 每角色前 60／13／3 篇恰為 audit 的 248 條
- **擴充 repo 分支**：`running` 快轉到 Step 1 的 `8d19c7f` 並推 `fork/running`；新分支 `diary-key-events-actor`；備份 `index.js.bak_key_events_actor_20260913_1359`
- **分類器**：`文檔/專案/Diary-Quality/tools/classify_key_events.py`（五類＋①-strict、`--subset`／`--from`／`--selftest`）。校準 5 次嘗試逐一記錄；使用者選項 A：代名詞納入「主人」，基線 **52/5/18/48/125**、與 audit 差 1 條接受。凍結 commit elephantfish `21250a3`（14:16:21）
- **prompt**：`cdBuildDiaryPrompt` sys 清單新增一行 actor 契約（第 836 行）、JSON 範本 placeholder 改「主体：事件」（第 847 行）；`node --check` 過；擴充 repo commit `7b861d3`、已推 `fork/diary-key-events-actor`
- **smoke test**（使用者按「三路API调试」）：`rule: true`、`玩家角色名：宇璽`、6 條 key_events 全為「名字：事件」、不寫入（#12 仍 70/23/5）
- **驗收**（Branch #8–#11，使用者按「历史补写」，`autoSummary` 期間關閉、事後開回）：6 篇新日記、19 條 `key_events`：⑤ 無主詞 0%（基線 50.4%）、①-strict 100%（基線 0）、使用者判歸屬錯誤 0 條、鍵集合 9 鍵不變、面板新舊混存顯示正常 → **五項全達標、接受**。材料 `RP記憶/實驗與驗證/Diary_KeyEvents_Actor_驗收_2026-09-13.md`
- **歸檔**：主 spec `openspec/specs/diary-key-events-actor/spec.md` 新建、`openspec validate --all` 4 passed、change 移入 `archive/2026-09-13-diary-key-events-actor/`
- **驗收節點**：9/20 Instrument 一問提早結案為達標（校準記錄落檔 + 凍結 commit 早於首則正式資料）
- Diary-Quality README Changelog +1；backlog 新開 `[SOP 候選] [case-count: 1]`「量測工具的凍結單位是可重跑的腳本本體」（第 82 行）；memory 新增「claude-in-chrome 連不到本機 ST」

### 三、未完事項 / 接力棒

- [#接力] 日記品質線下一個 change 未開：建議 audit 候選 B（不在場角色，`cdCaptureCast` 以「被提及」判定、會編造內心狀態），smoke test 已見一篇空 `key_events` 的不在場日記；`relationship_with_others` 去留另案；P4「已有記憶」職責說明也還沒動
- [#接力] LS 的 LIWE 載體設計討論仍掛 NEXT（本 session 未動）
- [#提醒] 擴充 repo 現在 checkout 在 `diary-key-events-actor`（ST 正在跑這版）；`running` 落後它 1 個 commit（`7b861d3`），change 已接受、下次可快轉
- [#提醒] Branch #8–#11 各多一組同樓層新日記（append，Step 1 舊篇未動），備份 `.bak_before_step2_rerun_20260913_1416`；標準 5 只在面板驗過、時間軸／搜尋／編輯器未逐一操作
- [#提醒] 長期穩定性未驗：19 條來自同一段 Step 1 場景，#12 之後的新日記可隨時用凍結分類器 `--from` 再量
- [#不重議] 凍結基線與 audit 差 1 條的來源不追（使用者裁定）

### 四、洞見 / 反省

**【紀律接力】**

- 量測工具的凍結單位是可重跑的腳本本體，不是「規則描述＋結果數字」。9/6 audit 的分類器只留規則和 52/5/19/48/124，今天重建時名單和代名詞集合都得重猜，封閉集合內窮舉只能逼近到差 1 條。已開 `[SOP 候選]`（backlog 第 82 行）
- 「校準基準」和「ground truth」要分開叫。248 條證明的是新分類器重現了 audit 的量法，不證明那 248 條分對了；真正的 ground truth 只有人工寫下的「誰做了什麼」。使用者今天糾正的這點已寫進 design 與驗收檔
- 順序本身是證據：分類器 commit 14:16、prompt commit 14:2x、首則正式資料 16:05。三個時間戳排好，Instrument 那條驗收節點才能提早結清

**【當日洞見】**

- 對帳時間戳要看完整日期，不只看時分。把 9/6 的 15:47–16:28 讀成今天的，對使用者講了「四個 branch 都被開過」，錯了一輪才發現
- 大段中文內容不要走 shell heredoc，會在看不出原因的地方炸開（`unexpected EOF while looking for matching quote`），直接用檔案寫入工具
- 擴充控制的 Chrome 連不到本機 ST（127.0.0.1 與 localhost 皆拒連、curl 卻 200），這類 UI 步驟以後直接寫給使用者做、事後讀檔對帳（已存 memory）
- smoke test 時不在場的角色拿到一篇 `key_events` 為空的日記，就是 audit 候選 B 的問題，下一個 change 的自然起點

### 五、檔案異動

**版控內（elephantfish）**

- 已 commit：`21250a3` `文檔/專案/Diary-Quality/tools/classify_key_events.py`（新增，凍結）
- 本 commit：`openspec/changes/archive/2026-09-13-diary-key-events-actor/`（proposal／design／specs／tasks）、`openspec/specs/diary-key-events-actor/spec.md`（新增）、`文檔/專案/Diary-Quality/README.md`（Changelog）、`驗收節點.md`（Instrument 一條打勾＋result）、`backlog.md`（第 82–83 行新條目）、`文檔/handoff/session-handoff-20260913.md`（本區塊）、`workflow-harness/work-map.jsonl`（Step 2 DONE、Step 3 新增並標 NEXT）

**未進版控**：`RP記憶/實驗與驗證/Diary_KeyEvents_Actor_驗收_2026-09-13.md`（新增）；`文檔/專案/Diary-Quality/tools/__pycache__/`（不進）

**擴充 repo（character-diary，`D:/AI/SillyTavern/public/scripts/extensions/third-party/character-diary`）**

- `running` → `8d19c7f`（快轉，已推）；分支 `diary-key-events-actor` commit `7b861d3`（`index.js` +2 −1，已推 fork）；備份 `index.js.bak_key_events_actor_20260913_1359`

**live ST `D:/AI/SillyTavern/data/default-user/`（不在版控）**

- `chats/银趴邮轮/…Branch #8、#9、#10、#11.jsonl`：各 append 一組同樓層新日記；備份 `.bak_before_step2_rerun_20260913_1416`
- `settings.json`：`autoSummary` 16:05 關、16:24 開回；其餘未動

### 六、下一步建議

1. 日記品質線 Step 3：`/opsx:propose` 候選 B（不在場角色）。動手前先重讀 audit §4.1 的 P2 因果鏈與 §七 候選 B 段，驗收標準要能事前釘死（例：製造「被提及但未出場」情境、數有沒有產日記）
2. 擴充 repo：`running` 快轉到 `7b861d3` 並推 fork，再從 `running` 開 Step 3 分支
3. LS 的 LIWE 載體設計討論（NEXT 已久，與日記線平行、不互相擋）

## Session 21:55

### 一、本 session 主題

日記品質線 Step 3：開立、實作、驗收並歸檔 change `diary-presence-gate`（audit 候選 B／P2「不在場角色被寫日記並編造內心狀態」）。方案「模型判 presence、程式擋」，順序守住「場景與尺凍結 → instrument commit → 舊碼基線 → 改碼 → 新碼正式 20 run」。順帶把 Step 2 的尾巴（`running` 快轉、標準 5 三處讀取點）收掉。
（本 session 工具集無 TaskCreate，完成事項由 tasks.md 與對話重建；ST UI 操作由使用者執行，後半改為檔案層預製子 branch + DevTools 主控台 runner，agent 讀檔對帳。）

### 二、完成事項

- **Step 2 收尾**：擴充 `running` 快轉到 `7b861d3` 並推 fork。標準 5 逐一操作：時間軸為死碼（`cdRenderTimeline` 無呼叫點、按鈕不在 HTML）、搜尋框被上游 `style.css:1650` 隱藏、編輯器顯示正常但**儲存會把含全形逗號的 key_events 切裂**（`split(/[,，、]/)`，Branch #8 一篇 3→5 條）；使用者裁定不還原、不順手修，backlog 新開 `[bug] [P3]`（第 89 行），Step 2 驗收檔 7.3 補記
- **規劃**：`/opsx:propose` 產出四份 artifact；使用者七點核心設計 + 五項裁定（C／D／E 各 = 0、A ≥ 16／20、B ≥ 3／5 為 MVP 防退化門檻、越界 = 0、`presenceAudit` 上限 200；fail-closed；focusRoles 不豁免；兩種錯誤分開統計 D11；每 run 同 snapshot）全落 design／spec／tasks
- **查現況**：因果鏈比 audit 多一層——誰能被寫由模型決定、`mergeDiaries` 無在場閘門、`cdCaptureCast` 是標籤洩漏；GM 卡下說話者永遠是卡名，程式判不了在場；`cdAddLog` 只在 localStorage、稽核記錄必須落聊天檔 store 頂層
- **場景與尺**：四組場景（S1 A+B、S2 A+C、S3 A+D、S4 A+E）agent 起草、使用者兩處調整後定稿凍結；S1 附蘇芮萱可感知清單；期望表 `presence_expect.json`
- **Instrument**：`presence_audit.py` 寫完、合成 fixture selftest 17 項（嘗試 1 敗於 fixture 期望值數錯 + 拿掉一個恆真檢查；嘗試 2 全過，判定邏輯未改），commit **`9a69fce42`（20:30:46）**
- **母 branch**：#14–#17 從 #12 的 #1454 分出，場景兩樓由 agent 腳本寫入（使用者先刪多帶的 1455 樓）；四支逐字對帳、hash 記錄
- **舊碼基線 12 run**：S1 #18–#20、S2 #21／#27／#28、S3 #24–#26、S4 #32–#34。**只有 S2 徐（只被提及）誘發缺陷 3／3**，其餘不在場格舊碼即為 0。S2 首輪 #22／#23 因「补写」按在母 branch 上而作廢、#15 以 #14 的 metadata 還原（新 hash `fc8124a0…`）
- **改碼**：擴充分支 `diary-presence-gate` commit **`c73b6a3`（21:13:42）**，7 個 hunk +24 −3：sys 四條 presence 規則、範本 `presence` 欄位、`mergeDiaries` 閘門（黑名單之後、cameo／別名之前）、`presenceAudit` 雙寫、`emptyData` 預設、記憶注入標題中性化、`cdCaptureCast` 註解；已推 fork
- **smoke**（#35）：`presenceAudit` 3 筆、蘇／徐 `absent` 被擋、范正常、entry 九鍵
- **正式 20 run**（#36–#55，主控台 runner 連跑 5 分鐘）：C／D／E 誤寫 0／0／0（35 次機會）、模型判定錯誤 0、Gate 執行錯誤 0、A 20／20、B 5／5、越界 0（使用者判）、九鍵不變、稽核每次相符、上限 max 3；面板與編輯器顯示正常 → **十項全達標，接受**
- **歸檔**：主 spec `openspec/specs/diary-presence-gate/spec.md` 新建、change 移入 archive、`openspec validate --all` 4 passed；擴充 `running` → `c73b6a3` 已推；`autoSummary` 開回（21:46）
- **驗收節點**：2026-09-27「Presence Gate 長期效果」（只驗 #13、≥ 20 次合併後再量、不足順延）
- README Changelog +1；memory 新增「日記驗收機械化」；runner 與兩支輔助腳本存 `RP記憶/實驗與驗證/scripts/`

### 三、未完事項 / 接力棒

- [#接力] 日記品質線 Step 4 未定，候選：P4「已有記憶」職責說明／P5 `relationship_with_others` 去留／E 情境加強場景（舊碼會寫的版本）／徐婷婷既有 5 篇「我沒出場」日記清理／`cdDiagCast` 面板「登场」文案
- [#接力] LS 的 LIWE 載體設計討論仍掛 NEXT（本 session 未動）
- [#提醒] 擴充 repo checkout 在 `diary-presence-gate`（= `running` = `c73b6a3`）；ST 正在跑這版
- [#提醒] 測試資料全部保留：母 #14–#17（含備份）、基線 #18–#21／#24–#28／#32–#34、作廢 #22／#23、smoke #35、正式 #36–#55；刪不刪由使用者決定
- [#提醒] 注入日記（`injectDiary`）使用者要開回；唯一副作用是徐婷婷那 5 篇舊日記被提及時會注入 RP prompt
- [#不重議] Branch #8 編輯器切裂的 5 條不還原（使用者裁定）；E 情境是否加強場景由使用者決定

### 四、洞見 / 反省

**【紀律接力】**

- 「不該發生」的格子要在凍結前用舊碼基線逐格確認**不是地板**。這輪 7 個不在場格只有 1 格在舊碼會誤寫，其餘 6 格的正式 0 只證明無退化；E 情境的保守規則因此根本量不到。CLAUDE.md Discrimination 寫了「避免地板效應」，但設計時推想不出來、要實測——已開 `[優化建議]`
- 每個 run 從同一 snapshot 起跑，人工 UI 做不到：母 branch 被按「补写」污染一次、還原花兩輪。改成檔案層複製子 branch + 主控台 runner 後 25 run 零錯誤。重複性操作一旦超過 5 次就該機械化，不是叮嚀使用者小心
- 凍結的腳本有兩處與凍結後的需求不合（逐情境 vs 合計門檻、`--since` vs `--parent/--run`），處理方式是改文件說明實作、不改腳本——凍結的價值在「尺沒被資料影響過」，文件跟著實作走是對的方向
- 含中文錨點的 python 走 heredoc 三次都在看不出原因的地方失敗（字串找不到、路徑對不上），先 Write 成檔再跑一次都沒錯——backlog 第 116 行那條 SOP 候選今天 +1

**【當日洞見】**

- 舊碼只在角色被**對話**提及時亂寫（S2 3／3），敘述裡暗示「可能在隔壁」（S4）不會；「已知角色名单」本身不足以誘發。閘門的必要性由 S2 一格證明，其他格是保險
- 模型對 E 情境四次判 `mentioned_only`、一次 `absent`、一次乾脆不輸出——三種都被擋，但「無法確認就判 absent」的保守規則沒被照字面執行，只是結果碰巧一致
- ST 的分支 = 整份聊天檔複製（含 `character-diary` store），所以 `shutil.copy2` 等價；`openCharacterChat` 要先有選中的角色，F5 後直接跑會在 `characters[this_chid]` 上炸
- 擴充編輯器儲存用 `split(/[,，、]/)`，任何含「，」的 key_events 一存就裂——上游既有缺陷，Step 2 spec 的「儲存後不變」scenario 對這種資料不成立
- worktree 的 `RP記憶/` 與 `D:/AI/SillyTavern/RP記憶/` 已分岔：9/6 機制 audit 只在 D 槽、9/13 兩份驗收檔只在 worktree；今天把 audit 複製進 worktree，長期要定一份正本

### 五、檔案異動

**版控內（elephantfish）**

- 已 commit：`9a69fce42` `文檔/專案/Diary-Quality/tools/presence_audit.py`、`presence_expect.json`（凍結 instrument）
- 本 commit：`openspec/changes/archive/2026-09-13-diary-presence-gate/`（proposal／design／specs／tasks）、`openspec/specs/diary-presence-gate/spec.md`（新增）、`文檔/專案/Diary-Quality/README.md`（Changelog）、`backlog.md`（第 89 行 `[bug]`、第 116 行 bump、新 `[優化建議]`）、`驗收節點.md`（遠期 +1）、`文檔/handoff/session-handoff-20260913.md`（本區塊）、`workflow-harness/work-map.jsonl`（Step 3 DONE、Step 4 新增並標 NEXT）

**未進版控**：`RP記憶/實驗與驗證/Diary_PresenceGate_驗收_2026-09-13.md`（新增）、`Diary_KeyEvents_Actor_驗收_2026-09-13.md`（7.3 補記）、`Diary_機制與Prompt_Audit_2026-09-06.md`（自 D 槽複製）、`RP記憶/實驗與驗證/scripts/diary_backfill_runner_console.js`／`presence_gate_write_scenes.py`／`presence_gate_restore_mother15.py`（新增）

**擴充 repo（character-diary）**：`running` 7b861d3 → **c73b6a3**（已推 fork）；分支 `diary-presence-gate` = c73b6a3（已推）；備份 `index.js.bak_presence_gate_20260913_2111`

**live ST `D:/AI/SillyTavern/data/default-user/`（不在版控）**：`chats/银趴邮轮/` 新增 Branch #14–#55（#29–#31 已刪）、#14–#17 備份 `.bak_before_scene_write_20260913_2047`、#15 備份 `.bak_polluted_by_mother_run_20260913_2103`；`settings.json` `autoSummary` 20:44 關、21:46 開回

### 六、下一步建議

1. 日記品質線 Step 4：從候選裡挑一個開 `/opsx:propose`。若要補 E 的鑑別力，先寫一個舊碼會亂寫的 E 場景跑基線再說；若先清資料，徐婷婷那 5 篇在 #13 面板手動刪
2. 2026-09-27 驗收節點：#13 累積 ≥ 20 次日記合併後 agent 讀檔跑凍結腳本；不足順延
3. LS 的 LIWE 載體設計討論（NEXT 已久，與日記線平行）
4. `RP記憶/` 兩份副本要定正本（D 槽或 worktree），否則下次又找不到檔
