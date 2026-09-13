## 1. 驗收尺凍結（本節全部完成前不得進入第 4 節以後）

- [x] 1.1 使用者定案 design D9 的門檻數字（C／D／E 錯誤入庫各 = 0、A ≥ 16／20、B ≥ 3／5 為 MVP 防退化門檻、越界 = 0、`presenceAudit` 上限 200）、fail-closed、focusRoles 不豁免、兩種錯誤分開統計（D11）；2026-09-13 已寫回 design.md（凍結標記待 1.2 定稿後一併打）
- [x] 1.2 （2026-09-13 使用者定稿：S1 依指示改寫在場條件與耳語錨句、S2–S4 原案通過；§一 凍結）agent 起草 4 組場景文字（S1 A+B、S2 A+C、S3 A+D、S4 A+E，各含一則玩家樓層與一則 AI 樓層，文風貼近该卡敘述），使用者修改定稿；S1 另附「蘇芮萱可感知事實清單」；全部落 `RP記憶/實驗與驗證/Diary_PresenceGate_驗收_<日期>.md` 的「一、情境與 ground truth」節
- [x] 1.3 （2026-09-13，隨 instrument 一起 commit `9a69fce42`）寫期望表 `文檔/專案/Diary-Quality/tools/presence_expect.json`：情境 × 角色 → 期望 presence、期望寫入；含 S1／S2／S4 各自「未出現於場景的角色」的 absent／0 格
- [x] 1.4 （2026-09-13 記入驗收檔 §〇）讀 Branch #12 現行 head 的 `diaries` 各角色長度、`cameo`、`promoted`、`lastFloor`，記入驗收檔當測試 branch 的起點狀態

## 2. 量測工具（Instrument；本節 commit 必須早於第 5 節的程式 commit）

- [x] 2.1 寫 `文檔/專案/Diary-Quality/tools/presence_audit.py`：讀聊天檔第一行的 `presenceAudit` 與 `diaries`，依 `--expect presence_expect.json --scenario S1` 對照，輸出每格判定分佈、`written` 條數、達標與否，並依 design D11 把「模型判定錯誤」與「Gate 執行錯誤」分兩欄計數；支援 `--baseline`（無 `presenceAudit` 時只數 `diaries` 新增篇數）、`--selftest`、`--json`。**實作差異（凍結後照實記）**：不用 `--since`，改以 `--parent <母 branch 檔> --run <子 branch 檔>…` 對照，只計 `message_id == range_top`（1456）的新篇與稽核記錄
- [x] 2.2 （嘗試 1 失敗於 fixture 期望值數錯、嘗試 2 通過 17 項）合成 fixture：腳本內附 5 個 run × 3 角色 = 15 筆 `presenceAudit`（四種 presence、`ok`／`presence_blocked`／`invalid_presence` 三種 reason、一筆非法值、一筆放行卻未寫入的 `written=false`）與對應 `diaries`；`--selftest` 輸出 17 項已知答案（各情境寫入數、model／gate 錯誤數、標準 1a／1b／1c／2／2b、標籤狀態、稽核一致性、上限、baseline 有效性、S4 偏差）。**實作差異**：「放行卻未寫入」在腳本裡一律歸 Gate 執行錯誤——測試三角色皆已 `promoted`、cameo 不可能觸發，這個歸類在本驗收範圍內成立；若日後用於未轉正角色，需人工排除 cameo 原因
- [x] 2.3 （`9a69fce42`，2026-09-13 20:30:46）在 elephantfish commit 腳本與期望表（英文訊息），記錄 commit hash 到 design.md「驗證設計・Instrument」與驗收檔；此後腳本不得修改

## 3. 舊碼基線（Occurrence 構念層）

- [x] 3.1 （2026-09-13 20:47 對帳通過：S1 #14／S2 #15／S3 #16／S4 #17，場景由 agent 腳本寫入、使用者事先刪除多帶的 1455 樓）使用者從 Branch #12 的 **#1454**（最後一則 AI 樓層）分出 4 個測試 branch（ST 自動編號，S1–S4 對應表記入驗收檔）；每個 branch 追加玩家樓層 #1455、AI 樓層 #1456，並把 #1456 編輯成 1.2 定稿的場景文字；agent 讀聊天檔確認四支的 #1454 相同、#1455／#1456 文字與定稿一致
- [x] 3.2 （autoSummary=false 20:44；四支 hash 記入驗收檔 §2.1；子 branch 複製是否含 store 待第一支驗）設定面板關閉「自动总结」；agent 記錄 4 支母 branch 的檔案 hash 與 `diaries` 長度（母 branch 永不生成，之後每次收結果都對帳 hash 未變）；第一支子 branch 建好後 agent 讀檔驗證分支複製含 `character-diary` store，否則啟用驗收檔 §1.7 的檔案還原退路
- [x] 3.3 （12 run 全有效：S1 #18–#20、S2 #21／#27／#28、S3 #24–#26、S4 #32–#34；S2 首輪 #22／#23 因母 branch 被按补写而作廢、#15 已還原；後半改為預製複本＋主控台腳本）每個情境 3 個 run：使用者從母 branch #1456「建立分支」→ 在子 branch 執行「补写指定范围」#1455–#1456 一次；agent 讀子 branch 檔對帳 `message_id=1456` 的新篇數（每角色）、母 branch hash 未變，記入驗收檔「二、基線」（情境 × run → 子 branch 檔名對應表）
- [x] 3.4 （有效：四支合計不在場寫入 3，全來自 S2 徐；S1／S3／S4 的 D／E 格舊碼為 0 = 地板，正式階段只有 C 格有鑑別力，記入驗收檔 §2.3 與 design Risks）判定基線有效性：C／D／E 格的不在場角色寫入條數合計 ≥ 1 → 有效；= 0 → 情境無效，回 1.2 重寫場景、重跑 3.1–3.3
- [x] 3.5 （保留；#22／#23 作廢但保留作污染證據）基線的子 branch 是否刪除由使用者決定；刪前 agent 已抄錄所需記錄

## 4. 分支與備份

- [x] 4.1 （21:11：`git switch -c diary-presence-gate running`，HEAD `7b861d3`）擴充 repo 確認 `git status` 乾淨、目前在 `diary-key-events-actor`（= `running` `7b861d3`）；`git switch -c diary-presence-gate running`；記錄 HEAD
- [x] 4.2 （`index.js.bak_presence_gate_20260913_2111`，CRLF 確認）備份 `index.js` 為 `index.js.bak_presence_gate_<YYYYMMDD_HHMM>`（不進 commit）；確認 CRLF

## 5. 程式改動（只動四處）

- [x] 5.1 （commit `c73b6a3`）`cdBuildDiaryPrompt` sys 清單在 key_events 契約行之後新增四條 presence 規則（措辭依 design D7）；JSON 範本每個 npc 加 `"presence":"participated|witnessed|mentioned_only|absent"`
- [x] 5.2 （同上）`cdBuildDiaryPrompt` 的 `diaryMemory` 標題改為「已知角色近期记忆（按名字提及抽取, 被提及不代表在场）」；`cdCaptureCast` 函數註解改為「候选角色抽取（按名字提及）」，邏輯不動
- [x] 5.3 （同上；`_audit.written` 於 push 後回填）`mergeDiaries` 在黑名單檢查之後插入 Presence Gate：正規化 `npc.presence`；四值外或缺失 → `invalid_presence` 擋下；`mentioned_only`／`absent` → `presence_blocked` 擋下；放行者記 `ok`；每個候選寫一筆 `presenceAudit`（`slice(-200)`）並 `cdAddLog`；`written` 在 push 成功後回填為 true（被 cameo／去重跳過者維持 false）
- [x] 5.4 （`emptyData()` 第 408 行加 `presenceAudit: []`；合併時缺則建）store 缺 `presenceAudit` 時於合併時建立為 `[]`；確認 `cdGetData` 的預設 store 結構若有集中定義處也補上
- [x] 5.5 （`node --check` OK；diff +24 −3、7 個 hunk 全在預期位置；commit `c73b6a3` 2026-09-13 21:13:42，晚於 instrument `9a69fce42` 20:30:46；已推 `fork/diary-presence-gate`）`node --check index.js` 通過；`git diff running` 只落在上述四處；commit（英文訊息）、`git push -u fork diary-presence-gate`，記錄 hash；確認 hash 時間晚於 2.3

## 6. Smoke test（不記入驗收）

- [x] 6.1 （未直接讀 `__cdLastDiaryTest`；以 6.2 的 `presenceAudit` 三筆皆帶四值內 presence 為 prompt 生效證據，記為間接驗證）DevTools 勾停用快取後 F5；使用者在任一測試 branch 按「三路API调试」；agent 讀 `window.__cdLastDiaryTest`（由使用者貼出）確認 `sys` 含四條新規則、`response` 每個 npc 有 `presence` 且值在四值內
- [x] 6.2 （#35，21:19：`presenceAudit` 3 筆 = 3 npc；范 participated／written、蘇與徐 absent／presence_blocked／written=false；范新篇九鍵無 presence；母 branch hash 未變；#35 保留、不計正式）使用者從 S3 母 branch 開一支 smoke 子 branch、執行一次「补写指定范围」；agent 讀該子 branch 檔確認 `presenceAudit` 已建立且筆數 = 回傳 npc 數、被擋者 `written=false`；這一支不算正式資料，母 branch 未動

## 7. 正式階段（新碼）

- [x] 7.1 （autoSummary=false 21:19；母 branch hash 與 3.2 相同）確認「自动总结」仍關；agent 重新記錄 4 支母 branch 的 hash（應與 3.2 相同）
- [x] 7.2 （#36–#40，21:24–21:25）S1：5 個 run，每 run 從母 branch #1456 開子 branch、執行一次「补写指定范围」；agent 每次讀子 branch 檔對帳 `presenceAudit` 新增筆數與 `message_id=1456` 的新篇、母 branch hash 未變，記入驗收檔「三、正式階段」對應表
- [x] 7.3 （#41–#45）S2：同 7.2
- [x] 7.4 （#46–#50）S3：同 7.2
- [x] 7.5 （#51–#55；#55 模型省略蘇、徐，記為遵循偏差）S4：同 7.2
- [x] 7.6 （合計：1a／1b／1c = 0、2 = 20／20、2b = 5／5、5 一致、5b max 3；模型判定錯誤 0、Gate 執行錯誤 0；腳本逐情境印的 2／2b FAIL 為門檻是合計的緣故，人工加總記入驗收檔 §3.2）四個 branch 對帳全過後，用凍結的 `presence_audit.py` 跑標準 1a／1b／1c／2／2b／5／5b；記錄判定分佈（報告項）；「模型判定錯誤」與「Gate 執行錯誤」兩欄分開列（D11），Gate 執行錯誤若非 0 視為 bug、修 Gate 後重跑本節
- [x] 7.7 （使用者判 0 篇越界）標準 3：agent 列出 S1 中蘇芮萱每篇寫入日記的 entry／secret／key_events，使用者對「可感知事實清單」逐篇判越界條數；agent 不代判
- [x] 7.8 （25 篇九鍵無 presence；使用者在 #36 面板與編輯器看顯示正常、按取消）標準 4：新篇鍵集合為九鍵、不含 `presence`；標準 6：面板與編輯器對 S1 的新篇正常顯示（編輯器只看不存；時間軸、搜尋在本版 UI 不可達）
- [x] 7.9 （驗收檔 §四：C／D／E 誤寫 0／0／0、模型判定錯誤 0、Gate 執行錯誤 0、A 20／20、B 5／5、越界 0；接受）結論以工程措辭寫入驗收檔（「4 情境共 N 次合併，C 誤寫 x1 條、D 誤寫 x2 條、E 誤寫 x3 條（其中模型判定錯誤 m 條、Gate 執行錯誤 g 條）、A 寫入 y／20、B 寫入 z／5、越界 w 篇；依此接受／不接受」）
- [x] 7.10 （settings.json autoSummary=true，21:46:33）設定面板開回「自动总结」，讀 `settings.json` 確認值與 mtime

## 8. 交接

- [x] 8.1 （README Changelog +1 已寫；handoff 於 /end-session 寫；`cdDiagCast` 文案已列 README 待辦）`文檔/專案/Diary-Quality/README.md` Changelog 加一行；handoff 記錄分支、兩個 commit hash（腳本／程式）、備份檔名、基線結果、正式結果；`cdDiagCast` 面板「登场」文案列入 README 待辦
- [x] 8.2 （接受；`running` → `c73b6a3`、已推 `fork/running`）若接受：`running` 快轉到本分支並推 fork；未接受：agent 提兩個措辭版本讓使用者選、不自行擴 scope；下一輪登記為本 change 的新 tasks 段，只重跑第 7 節，不重判舊資料、不重跑基線
- [x] 8.3 （2026-09-13 已登記 驗收節點.md 遠期段，到期 2026-09-27，只驗 Branch #13、≥20 次合併後再量；使用者裁定）登記驗收節點候選：#12／#13 自然累積 N 次合併後用凍結腳本再量 `presenceAudit` 的 `presence_blocked` 比例與是否仍有自述缺席日記入庫
