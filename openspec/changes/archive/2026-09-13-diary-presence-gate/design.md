## Context

`character-diary` v2.7.6 本地修補版（`D:/AI/SillyTavern/public/scripts/extensions/third-party/character-diary/index.js`，CRLF，獨立 git repo，`running` = `7b861d3`）。日記管線：`cdBuildDiaryPrompt`（746 行起）組 prompt → 獨立 API 生成 → `parseDiaryJson`（1800 行，`JSON.parse` 後取 `obj.npcs`，多餘欄位保留）→ `mergeDiaries`（2174 行）寫入 `chat_metadata.extensions['character-diary'].diaries[name][]`。

2026-09-13 對碼確認的現況：

| 位置 | 現況 | 與本 change 的關係 |
|---|---|---|
| sys 第一行 | 「为其中每个有名有戏份的登场角色…写一篇日记」 | 「登場」交模型判，無定義 |
| `diaryMemory`（788–806 行） | `cdCaptureCast(scene, data)` 以正則命中名字，命中者的最近 `diaryCharLimit=2` 篇日記以標題「登场角色近期日记（按登场人物抽取）」注入 | 標籤洩漏：被提及即被標為登場 |
| `usr` 的 `已知角色名单` | `Object.keys(data.diaries)` 全列 | 告訴模型這些角色存在，與在場無關 |
| `mergeDiaries` | 黑名單 → 重點角色 → 選擇性記憶 → is_minor／cameo 轉正 → 補別名 → 去重 → push | **無在場閘門**；cameo 累到 3 即轉正 |
| `cdAddLog` | 只存瀏覽器 localStorage、最多 500 條 | agent 讀不到（Chrome 連不到本機 ST），不能當對帳依據 |
| store 頂層 | `diaries`／`aliases`／`cameo`／`promoted`／`relations`／`focusRoles`／`snapshots`／… | 已有多個非 entry 的 metadata key，`presenceAudit` 放這一層 |
| 卡型 | `mainCardIsGM = true`，`[#樓 Assistant／银趴邮轮]` 說話者是卡名 | 程式無法從 metadata 判誰發言 |

實測基線（2026-09-13，正則找 entry／key_events／secret 含「沒有出現／未登場／置身事外／本段未…」等自述缺席詞）：Branch #12 98 篇中 4 篇、Branch #13 159 篇中 9 篇，全是徐婷婷，t1275→t1678 連續。這是動機證據，**不是**驗收儀器（正則名單是猜的、只抓老實承認的那種）。

前兩步已歸檔：Step 1 `diary-include-player-messages`（玩家樓層入場景、`玩家角色名：${_protNameDiary}`）、Step 2 `diary-key-events-actor`（`key_events` actor 前綴）。本步沿用 Step 1／2 的驗收慣例：ground truth 先寫再生成、Occurrence 讀聊天檔對帳、量測工具先校準凍結、工程措辭寫結論。

約束：CLAUDE.md 硬性要求（改 `index.js` 前備份、`node --check`、feature branch 從 `running` 開、reload 勾停用快取）；驗證前置 Gate 五問適用（本步結果決定 Step 3 是否接受、以及日記能否當 LS 的 Experience 來源）；擴充 UI 操作全由使用者執行、agent 讀檔對帳。

## Goals / Non-Goals

**Goals:**
- 每個候選角色都有一個由模型依場景文字判定的 presence，四值封閉。
- 只有 `participated`／`witnessed` 的日記入庫；`mentioned_only`／`absent`、缺欄位、非法值一律擋下且不累計 cameo。
- 每次合併留下可在聊天檔對帳的稽核記錄：角色、判定、是否寫入、原因。
- 切斷「被提及 = 登場」的標籤洩漏。
- `witnessed` 的日記不寫該角色感知不到的內容（輕量邊界：prompt 一條、人工驗）。
- 驗收尺在改碼前凍結；先證明情境能在舊碼上誘發缺陷，再證明新碼擋得住。

**Non-Goals:**
- 完整的視野／感知系統（誰看得到誰、距離、遮蔽）。
- 改 `cdCaptureCast` 的比對邏輯或 `diaryCharWindow`。
- 動 `relationship_with_others`、`mood`、`secret`、`is_minor` 的規格。
- 改 `focusRoles` 的「即使出场较少也要补全」prompt（P9）。
- 聊天注入路徑 `cdBuildDiaryInjectionText`（`injectDiary` 目前 false）。
- 單篇重寫路徑套閘門。
- 回填既有日記的 presence、清除既有的不在場日記（另案：使用者手動刪或另開清理 change）。
- 在 UI 顯示 `presenceAudit`。

## Decisions

**D1 判定者是模型、執行者是程式；不用正則判在場。**
三個方案：(a) 模型回 `presence`、程式擋；(b) 不動 prompt，合併時以「我沒出場」類詞彙的正則擋；(c) 改 `cdCaptureCast` 只認說話者名字。(c) 在 GM 卡下失效（說話者永遠是卡名）。(b) 只擋老實承認的那種，t1285 那篇編造內心狀態、沒有缺席詞的照樣入庫，且詞彙名單是猜的、違反 Step 2 剛記下的凍結原則。(a) 把判定放在唯一讀得懂文字的地方、執行放在唯一擋得住的地方，兩者都留記錄可對帳。選 (a)。代價：多一個欄位、判定品質要驗，這正是驗收要量的。

**D2 四個 presence 狀態；五個測試情境對到四個狀態，情境數 ≠ 狀態數。**

| 狀態（系統定義） | 定義 |
|---|---|
| `participated` | 角色實際參與本段事件或對話 |
| `witnessed` | 角色確實在場、能看到或聽到本段事件，但未直接參與 |
| `mentioned_only` | 角色只是被提到名字，本人沒有感知本段事件 |
| `absent` | 角色沒有參與也沒有感知本段事件（含：只因舊記憶／已知名單而成為候選、以及**無法確認是否感知**的情況） |

| 情境（測試構造） | 期望判定 | 期望寫入 |
|---|---|---|
| A 角色實際參與 | `participated` | 寫 |
| B 角色在場旁聽／目擊、未發言 | `witnessed` | 寫，內容不越界 |
| C 角色只被提到、不在場 | `mentioned_only` | **0** |
| D 角色完全不在場、文字未提及、只因已知名單或舊記憶成為候選 | `absent` | **0** |
| E 資訊不足、無法確認是否感知 | `absent`（保守規則） | **0** |

E 不是第五個狀態，它測的是保守規則有沒有被執行。閘門只看狀態，不知道情境；情境只存在於驗收表。

**D3 Presence Gate 的位置與行為。**
插在 `mergeDiaries` 的黑名單檢查之後、`_isFocus`／`_selective`／cameo／補別名之前。理由：cameo 與別名是「這個角色存在且有戲份」的累積證據，不在場的日記不該累積它們（徐婷婷就是這樣轉正的）。規則：
- 讀 `npc.presence`，`String().trim().toLowerCase()`；只接受四值之一。
- `participated`／`witnessed` → 放行，後續流程不變。
- `mentioned_only`／`absent` → `continue`，不寫、不累 cameo、不補別名。
- 欄位缺失或非法值 → 視同 `absent` 擋下，原因記 `invalid_presence`。**保守規則優先於相容性**：若模型整批漏欄位，A／B 會被全擋，這由驗收門檻「A／B 不得全部誤擋」抓出來，是 prompt 問題不是閘門問題。
- 重點角色（`focusRoles`）**不豁免**（使用者 2026-09-13 裁定）：`focusRoles` 只能影響候選／注意優先級，不能賦予角色不存在的 Experience。`focusRoles` 目前為空，這條只是定下順序，不改 P9 那句 prompt。
- 缺欄位或非法值視同 `absent`，**fail-closed**（使用者 2026-09-13 裁定）；過度阻擋由 A／B 的寫入門檻負責抓。
- 黑名單仍在閘門之前（黑名單角色連稽核記錄都不留，維持既有語意）。
- 單篇重寫路徑（8699）不經 `mergeDiaries`，不套閘門。

**D4 presence 不進 entry；稽核記錄落 store 頂層 `presenceAudit`。**
使用者定位 presence 為「生成資格／驗收稽核資訊」，不是角色的長期心理內容。三個落點：(a) 加進 entry（`diaries[name][].presence`）：最方便對帳，但污染 Step 2 剛守住的九鍵 schema，且 LS 讀 entry 時會拿到一個與 Experience 無關的欄位；(b) 只走 `cdAddLog`：不改資料，但 localStorage 對 agent 不可見、500 條上限、換瀏覽器就沒了，驗收無法對帳；(c) store 頂層有界陣列 `presenceAudit`：與 `focusRoles`／`snapshots` 同層，落聊天檔第一行，python 可讀，entry 不動。選 (c) 加 (b) 雙寫。**為什麼必須持久化**：驗收要對帳「每個候選的判定與去留」，尤其被擋下的那些沒有 entry 可看，不落檔就等於沒有觀察點（Observation 一問）。最小影響：每筆 `{message_id, name, main, presence, written, reason, ts}` 約 120 bytes，上限 200 筆（`slice(-200)`），約 24 KB，與 `processedFloors` 482 筆同量級。舊聊天檔沒有這個 key，首次合併時建立，不回填。`reason` 取值：`ok`／`presence_blocked`／`invalid_presence`（黑名單、選擇性記憶、cameo 未達的既有 skip 不記入，維持既有 `cdLog`）。

**D5 標籤中性化。**
`diaryMemory` 標題改為「已知角色近期记忆（按名字提及抽取, 被提及不代表在场）」。每行格式 `【角色】第N楼: entry` 不變。`usr` 的「各角色已有记忆(最近历史)」不動（它沒有「登場」語意）。`cdCaptureCast` 的函數註解由「登场人物捕获」改為「候选角色抽取（按名字提及）」，程式碼不改；`cdDiagCast` 診斷文字仍寫「登场」，屬 UI 文案、不在本 change 動（記入 Risks）。

**D6 `witnessed` 的輕量邊界。**
prompt 一條：「presence 为 witnessed 的角色, 日记只能写该角色在场时确实能看到、听到或合理推知的内容; 不得写其无法感知的对话、动作或他人内心。」不做程式層檢查（程式沒有感知模型）。驗收由人工 ground truth 判：B 情境的場景文字寫好後，使用者**先**寫下「該角色可感知的事實清單」，生成後逐篇比對 entry／secret／key_events 有沒有超出清單的具體事實（越界 = 寫出了清單外的具體事件、對話內容或他人內心；泛泛的情緒推測不算）。

**D7 Prompt 措辭（簡體、與既有 15 條同風格；定稿於 tasks 5.1）。**
sys 清單在 Step 2 的 key_events 契約之後加四條：

> `- 为每个候选角色判定 presence, 只能取以下四值之一: participated(实际参与本段事件或对话) / witnessed(确实在场, 能看到或听到本段事件, 但未直接参与) / mentioned_only(只是被他人提到名字, 本人没有感知本段事件) / absent(本段未出场、未感知)。`
> `- 无法确认角色是否在场、是否感知到事件时, 一律判 absent。不要为角色创造其没有经历的第一人称体验。`
> `- presence 为 mentioned_only 或 absent 的角色, 仍输出其 name 与 presence, 但 entry、secret 留空字符串, key_events 留空数组, 不写任何正文。`
> `- presence 为 witnessed 的角色, 日记只能写该角色在场时确实能看到、听到或合理推知的内容; 不得写其无法感知的对话、动作或他人内心。`

JSON 範本每個 npc 加 `"presence":"participated|witnessed|mentioned_only|absent"`。要求後兩級**仍輸出 name 與 presence**，是為了留下判定記錄（否則模型直接省略，稽核看不到它判了什麼）；代價是多幾十個 token。第一行「为其中每个有名有戏份的登场角色…」不動。

**D8 驗收設計：情境由使用者撰寫場景文字、先在舊碼跑基線、再在新碼重跑。**
- **場景來源**：從 Branch #12 **同一個最新乾淨 checkpoint**分出 4 個測試 branch（使用者 2026-09-13 裁定；#12 現況：1455 樓為未回覆的玩家訊息，最後一則 AI 樓層是 **#1454**，四支都從 #1454 分出，命名採 ST 自動編號、機械可辨識即可，對應表記入驗收檔），每個 branch 追加一組「玩家樓層 #1455 + AI 樓層 #1456」，**AI 樓層由使用者手動編輯成事先定稿的場景文字**（ST 可編輯訊息），使場景內容完全受控、ground truth 精確；補寫範圍固定為 #1455–#1456。場景草案由 agent 起草、使用者定稿，落 `RP記憶/實驗與驗證/Diary_PresenceGate_驗收_2026-09-13.md` §一。選 #12 head 而非 1244 凍結點：#12 的 store 已有徐婷婷 5 篇「我沒出場」日記，C 情境會吃到最強的自我強化注入，是最難的條件。
- **情境分配**（每個 branch 一組，A 在每個 branch 都成立以提供對照）：

  | branch | 場景要點 | 期望：范婼慧 | 期望：蘇芮萱 | 期望：徐婷婷 |
  |---|---|---|---|---|
  | S1 = A+B | 范與宇璽對話；蘇在旁看著、沒說話，場景明寫她在場 | participated／寫 | witnessed／寫、不越界 | 不出現於場景 → absent／0 |
  | S2 = A+C | 范與宇璽對話中**提到**徐（例：「徐婷婷今天請假」），徐不在場 | participated／寫 | 不出現 → absent／0 | mentioned_only／0 |
  | S3 = A+D | 范與宇璽獨處，**完全不提**蘇、徐 | participated／寫 | absent／0 | absent／0 |
  | S4 = A+E | 范與宇璽對話；場景暗示蘇「可能在隔壁」但未確認她聽得到 | participated／寫 | absent（保守）／0 | 不出現 → absent／0 |

  D 情境在 S1／S2／S4 也各出現一次（未出現於場景的角色），所以 D 的樣本不只 S3。
- **每個 run 從同一 snapshot 起跑（使用者 2026-09-13 律定）**：前一次生成的日記或 metadata 不得成為下一次生成的輸入；`presenceAudit` 可事後彙總，但不得造成 prompt 輸入差異。做法：每個情境一支**母 branch**（從 #1454 分出、加 #1455／#1456 定稿文字、**永不生成**）；每個 run 從母 branch 的 #1456 再開一支**子 branch**、只在子 branch 上執行一次「补写指定范围」#1455–#1456、agent 讀子 branch 檔收結果。每次收結果同時對帳母 branch 檔案 hash 未變。細節與退路（檔案還原）見驗收檔 §1.7。
- **基線階段（舊碼）**：每個情境 **3 個 run**（3 支子 branch），讀聊天檔記錄每個角色在 `message_id=1456` 被寫了幾篇。**基線必須在 C／D／E 至少誘發 1 篇不在場日記**，否則情境沒有構念效度，改場景重來（這是 CLAUDE.md Occurrence 構念層那條：「沒觀察到 X」要先確認 X 會被觸發）。
- **正式階段（新碼）**：每個情境 **5 個 run**（5 支子 branch）。讀每支的 `presenceAudit` 與 `diaries`，由 `presence_audit.py` 彙總。
- **樣本量**：C／D／E 期望寫入 = 0 的觀察格共 7 格（S1 徐、S2 蘇、S2 徐、S3 蘇、S3 徐、S4 蘇、S4 徐），每格 5 次，合計 **35 次**「不該寫」的機會（驗收檔 §1.1 對照表）。若新碼下真實誤寫率仍有 10%，35 次全 0 的機率約 0.03；若 5%，約 0.17。也就是這把尺能可靠抓到「還是常錯」，抓不到「偶爾錯」；偶爾錯留給 #12／#13 後續自然累積再量（Risks）。A 的機會 20 次、B 5 次。
- **人工判定**：(1) 標準 3 的越界，使用者對 B 情境每篇寫入的日記逐篇判，agent 只列表；(2) 判定分佈（模型給的 presence 對不對）由 agent 機械對照期望表，是**報告項不是門檻**，門檻只掛寫入。

**D9 成功標準（使用者 2026-09-13 定案；正式資料收第一筆前凍結）。**

| # | 標準 | 量法 | 門檻 |
|---|---|---|---|
| 1a | C 情境（`mentioned_only`）錯誤入庫條數 | `presence_audit.py` 對照期望表數 `written=true` 的不該寫格 | **= 0** |
| 1b | D 情境（`absent`）錯誤入庫條數 | 同上 | **= 0** |
| 1c | E 情境（uncertain，保守規則）錯誤入庫條數 | 同上 | **= 0** |
| 2 | A 情境（`participated`）正常寫入 | 同上，范婼慧在 4 個 branch × 5 次 | **≥ 16／20** |
| 2b | B 情境（`witnessed`）正常寫入 | 同上，蘇芮萱在 S1 × 5 次 | **≥ 3／5**（**MVP 第一輪防退化門檻**，不代表理想召回率） |
| 3 | B 情境感知越界篇數 | 使用者對 ground truth 清單逐篇判 | **= 0** |
| 4 | 不改 entry schema | 新篇鍵集合與舊篇相同（九鍵） | 相同 |
| 5 | 稽核記錄完整 | 每次合併，`presenceAudit` 新增筆數 = 模型回傳的 npc 數（黑名單除外） | 每次相等 |
| 5b | `presenceAudit` 上限 | 讀 store | 200 筆 |
| 6 | 舊資料相容 | 面板與編輯器對舊篇與新篇正常顯示（時間軸為死碼、搜尋框被上游 CSS 隱藏，本版 UI 不可達；編輯器只驗顯示、**不按保存**——上游 `split(/[,，、]/)` 會把含全形逗號的事件切裂，見 backlog `[bug]`） | 無錯誤、無空白 |

1a／1b／1c 與 3 是否決條件，2／2b 防「過度阻擋」，4／5／5b／6 是不變式。判定分佈（C 判成 `mentioned_only` 還是 `absent`、E 判成什麼）只報告；E 若被判 `mentioned_only`，記為「判定偏差、結果正確」，不計入否決。任一否決條件未達 → 記錄、不接受，調 prompt 措辭後以新版本重跑正式階段（新一輪是新資料，舊資料不重判；基線不重跑）。

**D10 量測工具 `presence_audit.py` 先校準凍結，commit 早於程式 commit。**
腳本放 `文檔/專案/Diary-Quality/tools/`（版控內，commit hash 即凍結標記）。輸入：聊天檔路徑、期望表（JSON，情境 × 角色 → 期望 presence、期望寫入）、可選 `--since <message_id>` 只看新資料。輸出：每格的判定分佈、`written` 條數、對照期望的達標與否、標準 1／2／2b／5 的計算。校準：內附合成 fixture（手寫的 `presenceAudit` 20 筆 + 對應 `diaries`，含每種 reason、一筆非法值、一筆黑名單缺席），`--selftest` 須輸出已知答案。凍結後量新資料不得改；發現缺陷只記錄。**校準單位是可重跑的腳本本體**（2026-09-13 backlog `[SOP 候選]`）。

**D11 兩種錯誤分開統計（使用者 2026-09-13 律定）：模型 presence 判定錯誤 vs 程式 Gate 執行錯誤，不得混成同一種失敗。**
`presenceAudit` 每筆同時記錄模型給的 `presence` 與程式的 `written`，所以每個「不該寫卻寫了」的格子都能歸因到其中一種：

| 模型判定 | 程式結果 | 歸類 |
|---|---|---|
| `participated`／`witnessed`，但期望表為不該寫 | `written=true` | **模型判定錯誤**（Gate 依判定放行，執行正確） |
| `mentioned_only`／`absent`／缺失／非法 | `written=true` | **Gate 執行錯誤**（判定已擋、程式沒擋住） |
| `participated`／`witnessed`，期望表為該寫 | `written=false` 且 reason 非 cameo／去重 | **Gate 執行錯誤**（放行卻沒寫） |
| `mentioned_only`／`absent`，期望表為該寫 | `written=false` | **模型判定錯誤**（過度保守） |

`presence_audit.py` 輸出這兩欄分開的計數；驗收報告的結論句必須分別寫「判定錯誤 x 條、執行錯誤 y 條」。Gate 執行錯誤預期為 0（它是確定性程式），若非 0 是 bug、不是 prompt 問題，修 Gate 後重跑正式階段；模型判定錯誤若超過門檻，修 prompt 後重跑。兩者的修法不同，所以不能合計。

## Risks / Trade-offs

- [模型整批不回 `presence`] → 閘門視同 absent 全擋；標準 2 抓到；修 prompt 重跑，不放寬閘門。
- [模型把 C 判成 `witnessed` 放行] → 這是本 change 的核心失敗模式，標準 1 直接否決；記錄判定分佈，改措辭重跑。
- [模型對 B 過度保守判 `absent`] → 標準 2b 抓到（≥ 3／5）；`witnessed` 本來就是四值裡最難的，門檻設得比 A 低。
- [基線誘發不出缺陷] → 場景無效，改寫場景；不得跳過基線直接跑新碼。
- [30 次抓不到低頻誤寫] → 接受；#12／#13 後續自然累積的 `presenceAudit` 可隨時用凍結腳本再量，登記為驗收節點候選。
- [`presenceAudit` 讓聊天檔變大] → 上限 200 筆約 24 KB，與 `processedFloors` 同量級；若使用者不接受，退為 50 筆。
- [被擋的角色仍在 `已知角色名单` 裡、下次仍成為候選] → 預期行為：候選不等於寫入，每次都判、每次都擋，稽核可見。自我強化鏈斷在寫入端，舊的 5 篇徐婷婷日記仍會經 `diaryMemory` 注入（標題已中性化），清除另案。
- [`cdDiagCast` 面板文字仍寫「登场」] → UI 文案，不影響 prompt；記入 README 待辦。
- [使用者編輯 AI 樓層來構造場景，與自然生成不同] → 這是實驗控制，目的是讓 ground truth 精確；場景文字風格請貼近該卡的敘述風格，避免模型因文風異常改變行為。長期效果由自然累積補。
- [前一 run 的日記進入下一 run 的 diaryMemory] → 每 run 一支子 branch、母 branch 永不生成（§1.7）；agent 每次對帳母 branch hash。若 ST 分支複製不帶 `character-diary` store，退為檔案還原（使用者以 `! cp` 執行，agent 對帳）。
- [**D／E 格是地板**（2026-09-13 基線實測）] → 舊碼在 S1／S3／S4 的不在場格全寫 0：沒被對話提及的角色本來就不寫、只在敘述暗示可能在隔壁的角色（E）也不寫。正式階段這些格的 0 只能證明「沒有退化」，不能證明閘門有效；**唯一有鑑別力的是 C 格（S2 徐，舊碼 3／3）**。E 的「保守規則」在本組場景只能看標籤分佈（報告項），寫入條數驗不到。凍結時未看出，屬設計缺口；是否另寫一個舊碼會寫的 E 場景由使用者決定，新場景為新凍結、不動既有四組。
- [子 branch 檔案數量：4 × (3+5) = 32 支] → 每支是母 branch 的完整複製（約數 MB），跑完由使用者決定刪不刪；刪前 agent 抄錄。
- [單篇重寫路徑不套閘門] → 使用者主動操作，在場性由人裁定；記入 spec 為明確排除。

## Migration Plan

1. 擴充 repo：`git status` 乾淨、目前在 `diary-key-events-actor`（= `running` = `7b861d3`）；`git switch -c diary-presence-gate running`。
2. 備份 `index.js` 為 `index.js.bak_presence_gate_<YYYYMMDD_HHMM>`（不進 commit）。
3. **驗收尺凍結**：使用者定案 D9 數字、寫好 4 組場景文字與 B 的可感知清單、期望表 JSON；`presence_audit.py` 校準、commit。
4. 建 4 個測試 branch、寫入場景、備份；**舊碼基線** 3 次／branch、對帳、還原備份。
5. 改 `index.js` 四處；`node --check`；commit、推 fork。
6. reload；測試路徑 smoke（`window.__cdLastDiaryTest.sys` 含四條新規則、`response` 每個 npc 有 `presence`）。
7. 正式階段 5 次／branch；對帳；跑凍結腳本；人工判標準 3；工程措辭寫結論到 `RP記憶/實驗與驗證/Diary_PresenceGate_驗收_<日期>.md`。
8. 回退：程式層 `git switch running`；`.bak` 為保險；資料層還原 4 個測試 branch 的 `.bak`（#12／#13 未動）。

## 驗證設計（CLAUDE.md 驗證前置 Gate 五問）

- **Observation**：觀察點是測試 branch 聊天檔第一行的 `presenceAudit[]`（判定與去留）與 `diaries[name][]`（實際寫入）。前者由本 change 建立，**smoke test 先確認它真的落檔**，再收正式資料。基線階段只有後者。
- **Discrimination**：主判準是寫入條數對照期望表，機械可數；門檻事前定死。樣本量鑑別力見 D8（30 次機會，可靠抓 ≥ 10% 的誤寫率）。基線階段證明情境不在地板上（舊碼會誤寫）。
- **Construct**：要驗的是「不在場角色的第一人稱 Experience 有沒有入庫」，量的是寫入條數，不是判定標籤的美觀、不是日記品質。B 的越界由人工對可感知清單判，量的是「內容有沒有超出感知」而非「寫得好不好」。
- **Instrument**：`presence_audit.py` 先以合成 fixture 校準（已知筆數、已知 reason 分佈、非法值處理），commit 凍結，hash 記入本檔與驗收檔；程式 commit 必須晚於它。凍結後不改；校準不符修的是腳本缺陷，不是門檻。**凍結 commit：elephantfish `9a69fce42`（2026-09-13 20:30:46 +0800），含 `presence_audit.py` 與 `presence_expect.json`。校準記錄：嘗試 1 selftest 失敗於 `label_mismatch`（fixture 期望值寫 1、實際 3——run2 蘇 absent／run3 徐 participated／run5 徐 mentioned_only 三處都是不符，是我數錯，判定邏輯正確），同時拿掉一個恆真的佔位檢查；嘗試 2 全部 17 項通過。判定邏輯自始未改。**
- **Occurrence**：每次「补写指定范围」後讀聊天檔對帳 `presenceAudit` 新增筆數與 `diaries` 長度變化，不看 toast；基線階段以 `diaries` 長度變化對帳。**構念層**：基線必須在舊碼誘發出不在場日記，才有資格說新碼「擋住了」。

## Open Questions

- ~~D9 的數字~~ 2026-09-13 使用者定案（見 D9）。
- 4 組場景文字與 B 的可感知清單：agent 已起草（`RP記憶/實驗與驗證/Diary_PresenceGate_驗收_2026-09-13.md` §一），**待使用者定稿**；定稿後才凍結 instrument。
- ~~測試 branch 的命名與分出樓層~~ 從 #1454 分四支、ST 自動編號（見 D8）。
- ~~fail-closed／focusRoles~~ 2026-09-13 使用者定案（見 D3）。
- 基線階段是否也記錄模型有沒有自發寫出「我沒出場」類句子：只觀察、不進門檻，記入驗收檔 §二。
