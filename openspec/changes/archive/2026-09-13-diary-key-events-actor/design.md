## Context

`character-diary` v2.7.6 本地修補版（`D:/AI/SillyTavern/public/scripts/extensions/third-party/character-diary/index.js`，CRLF，獨立 git repo）。日記由 `cdBuildDiaryPrompt`（747 行）組 prompt、獨立 API 生成、`mergeDiaries`（2173 行）寫入 `chat_metadata.extensions['character-diary'].diaries[name][]`。每篇六個輸出欄位中，`key_events` 是字串陣列。

2026-09-06 audit（`RP記憶/實驗與驗證/Diary_機制與Prompt_Audit_2026-09-06.md`）對 Branch #12 當時的 76 篇日記、248 條 `key_events` 做主詞形態分類，結果：

| 分類 | 條數 | 佔比 |
|---|---|---|
| ① 開頭點名角色 | 52 | 21.0% |
| ② 開頭用代名詞 | 5 | 2.0% |
| ③ 名字在句中非開頭 | 19 | 7.7% |
| ④ 代名詞在句中非開頭 | 48 | 19.4% |
| ⑤ 完全無主詞 | 124 | 50.0% |

分類器規則（audit §3.2 記載）：「前 6 字內有無角色名」判①、起首字判②；規則凍結在跑之前、跑完未調參。**腳本本身沒有留檔**，只留了規則描述與結果。2026-09-13 重算：Branch #12 現已 98 篇、314 條；取每角色陣列前 60／13／3 篇（范婼慧／蘇芮萱／徐婷婷，turn ≤ 1348）恰為 248 條，與 audit 子集一致，可當**分類器凍結基線**（calibration fixture）。這 248 條證明的是「新落地的分類器能否重現 audit 當時的量測方式」，**不是**這 248 條在人工判讀上都分對了；真正的 ground truth 只有 Step 1 驗收檔裡人工寫下的「誰做了什麼」。

現行 prompt 對 `key_events` 的全部指示是 JSON 範本裡的 placeholder「关键事件」（846 行）。system 要求清單 15 條裡沒有一條提到它（audit §2.3）。

前一步（Step 1，change `diary-include-player-messages`，已歸檔）已把玩家樓層納入場景、行首標 `Player／Assistant`、system 加了 `玩家角色名：${_protNameDiary}`（`SillyTavern.getContext().name1`，缺省「主角」）。本步直接沿用這個變數當玩家主體詞。

Step 1 驗收在主線 1244 樓凍結後從主線開了 Branch #8–#12，各演一種玩家事件（請託／承諾／具體行動／揭露／拒絕），**每組都先寫了 ground truth 再產日記**，材料在 `RP記憶/實驗與驗證/Diary_玩家樓層_ON態驗收_2026-09-06.md`。#8–#11 自 9/6 後未再遊玩；#12 是使用者現行線（已推進到 1446 樓，另有 #13 從它分出）。

約束：
- CLAUDE.md 硬性要求：改 `index.js` 前備份、改後 `node --check`；`data.js` 等切片改了不生效；reload 需 DevTools 勾停用快取再 F5。
- 擴充 repo 分支規則：feature branch 從 `running` 開；`main` 只看不 checkout。目前 checkout 在 `diary-player-messages`（領先 `running` 兩個 commit、已推 `fork`）。
- 驗證前置 Gate 五問（Observation／Discrimination／Construct／Instrument／Occurrence）適用：本步結果決定 Step 2 是否接受、以及 `key_events` 能否當 LS 輸入。
- 驗收節點 2026-09-20「Instrument 一問有沒有真的被執行」：本步是期間內第一個撰寫量測工具的事件，需留下 (a) 已知答案校準記錄、(b) 校準後凍結標記，且凍結時間戳早於首則正式資料。

## Goals / Non-Goals

**Goals:**
- 新產出的每條 `key_events` 以「主体：事件」開頭，主體是角色主名或玩家角色名；日記主人自己的行為也寫主名。
- 量測工具先用 248 條已知答案校準、commit 凍結，再量新資料。
- 在同一段樓層上重跑，證明格式改變是 prompt 造成的，而不是劇情不同造成的。
- 舊資料零遷移、所有讀取點零改動。

**Non-Goals:**
- 改 `key_events` 為物件 schema（`[{actor, event}]`）。
- 為既有 314 條舊資料補主詞。
- 不在場角色（audit P2，候選 B）、`secret` 留空出口（P3）、`relationship_with_others` 去留（P5）、system 對「已有記憶」的職責說明（P4）：各自另開 change。
- 改 `cdBuildCombinedPrompt`（死碼）。
- 逐條判定舊資料的歸屬對錯。
- 修 `name1` 取不到時的退化行為（Step 1 D6 已定「主角」）。

## Decisions

**D1 維持字串陣列，actor 用「主体：事件」前綴表達；不改 schema。**
考慮過 `[{actor, event}]` 物件 schema：語意最乾淨，但 `index.js` 有 13 個讀取點全部把元素當字串 join／split（編輯器還以 `,，、` 切回陣列），改 schema 等於同時動 13 處加一次 314 條的資料遷移，而本 change 的單一變因是「prompt 有沒有要求主體」。前綴格式讓變因只落在 prompt 一處；LS 讀取時以第一個全形冒號切分即可得到 actor。代價：actor 是慣例而非型別保證，模型可能違反格式，這正是驗收要量的東西。

**D2 主體詞彙 = 「已知角色名单」主名 ∪ 玩家角色名；日記主人自己的行為也寫主名，不寫「我」。**
考慮過允許「我」（日記是第一人稱，「我」對日記主人是明確的）：但 LS 讀 `key_events` 時是跨角色彙整，「我」要回頭查這條屬於誰的日記才能解析；分類器也得為代名詞另開規則。統一用主名讓每條 `key_events` 脫離日記脈絡後仍可讀。多人共同行為寫主要發起者，避免「A与B：…」這種難切的形式。玩家名沿用 Step 1 注入的 `_protNameDiary`（執行期值待驗，見 Risks）。

**D3 只改 `cdBuildDiaryPrompt` 的 `sys` 陣列與其 JSON 範本；`cdBuildCombinedPrompt` 不動。**
2026-09-13 grep：`cdBuildCombinedPrompt` 只有定義、無呼叫點。`cdBuildDiaryPrompt` 的三個呼叫點（測試路徑 3192、正式生成 4430、單篇重寫 8674）共用同一份 sys，改一處三路生效。新增的要求放 system 要求清單、與 Step 1 的資料說明同一區；語言跟 prompt 既有風格用簡體。措辭（定稿於 tasks 4.1，此處為設計意圖）：

> `- key_events 每条必须以行为主体开头, 格式「主体：事件」。主体只能是"已知角色名单"中的主名或玩家角色名(${_protNameDiary}); 写日记的角色自己做的事也写主名, 不写"我"; 多人共同的行为写主要发起者。`

JSON 範本 placeholder 改為 `"key_events":["主体：事件"]`。

**D4 量測工具：重現 audit 的分類器，以 248 條凍結基線校準，commit 即凍結；分類器的 commit 必須早於 prompt 的 commit。**
腳本放 `文檔/專案/Diary-Quality/tools/classify_key_events.py`（在版控內，commit hash 就是凍結標記；`RP記憶/` 不進版控、放那裡凍不住）。校準目標：對 Branch #12 每角色陣列前 60／13／3 篇的 248 條，輸出恰為 52／5／19／48／124，且五類合計對帳 = 248。**順序硬性要求**（使用者 2026-09-13 律定）：分類器落版控 → 對 248 條重現 → commit 凍結 → 然後才改 prompt。理由：規則寫在設計文件裡不等於量尺沒被污染，「修改前真的跑過且有 commit」才是乾淨的工程證據。
分類器除五類外另輸出一個子計數 **①-strict**：字串以「名單內名字 + 全形冒號」開頭。它是①的子集、不影響五類對帳，用於標準 2（見 D6）。角色名清單是 audit 未記載的參數：校準時**只允許在「三位日記主人的主名 + 別名 + 玩家名」這個封閉集合內取子集**試到重現為止，重現的那組寫死進腳本並記錄；若封閉集合內沒有任何組合能重現，停手回報、不得放寬規則去湊數。校準通過後 commit；之後量新資料**不得**再改腳本，發現缺陷只能記錄、不能修了重量。
分類器同時要能把「主体：事件」判為①（名字在前 6 字內，冒號不影響），這在校準資料上不會被測到，所以在 tasks 3.3 加一組**合成樣本**的自我測試（5 條手寫的新格式、5 條舊格式），凍結前跑過。

**D5 驗收：在 Branch #8–#11 對 Step 1 的同一段樓層重跑「补写指定范围」，配對比較。**
考慮過三個做法：(a) 從主線再開新 branch 演新劇情：主線凍結在 1244，新劇情跟 Step 1 不同，格式差異會混進劇情差異；(b) 在 #12 現行線上自然累積：樣本到齊時間不可控，且 #12 是使用者的正史；(c) 在 #8–#11 對 Step 1 已驗收的樓層範圍重跑：同一段場景、同一份 ground truth、只有 prompt 不同，是最接近「同一批樓層重跑」的做法。選 (c)。#12 排除（現行線不污染），樣本為 4 個情境。`mergeDiaries` 以 `message_id + entry` 去重、新 entry 必然不同，所以會 append 一篇同 `message_id` 的新日記；讀取時以「陣列中 `message_id` 等於範圍頂樓、且位置在 Step 1 那篇之後」辨識新篇。重跑前逐檔 `.bak`。
已知混雜：重跑時 `diaryMemory` 會把 Step 1 那篇的 `entry` 當「已有記憶」注入（只注入 entry、不注入 key_events），可能影響 entry 的措辭、不影響本步量的 `key_events` 格式；歸屬判定（成功標準 3）由使用者對 ground truth 判，判時知道這個混雜。

**D6 成功標準（收第一份正式資料前凍結）。**

| # | 標準 | 量法 | 門檻 |
|---|---|---|---|
| 1 | 新產出 `key_events` 的「⑤ 完全無主詞」比例 | 凍結的分類器 | **≤ 10%**（基線 50.0%） |
| 2 | 「開頭明確指出該事件的實際行為者」比例：①-strict，字串以名單內名字（任一角色主名或玩家名，**不限日記主人**）加全形冒號開頭 | 同上 | **≥ 80%**（舊資料寬鬆① 為 21.0%，strict 為 0） |
| 3 | 玩家行為被歸給角色的條數 | 使用者逐條對 Step 1 ground truth 判 | **= 0** |
| 4 | 不新增任何 Meaning／Scope 層的欄位或表述 | 檢視 diff 與新日記的鍵集合 | 鍵集合與舊篇相同 |
| 5 | 舊資料相容 | 面板／時間軸／搜尋／編輯器對舊篇與新篇皆正常顯示 | 無錯誤、無空白 |

標準 2 量的是 **actor 是否自足**，不是「出現日記主人的名字」：「宇璽：拒绝邀请」與「徐婷婷：告诉范婼慧…」都算，「范婼慧」寫在句中或被動句裡不算。本輪驗證的問題是「prompt 能不能讓字串型 `key_events` 穩定帶有自足的 actor」；若字串契約證明難以穩定，再以這個證據討論 `{actor, event}` 結構化。
1 與 2 是主判準，3 是否決條件，4 與 5 是不變式。四個情境合起來一次判，**不逐情境判**。任一主判準未達 → 記錄、不接受，改 prompt 措辭後以新版本重跑一輪（新一輪是新資料，舊資料不重判）。

**D7 語言與措辭。** 新增指示用簡體、與 prompt 既有 15 條同風格；「主体：事件」用全形冒號，與繁簡無關、與既有分隔符 `,，、;·` 皆不衝突。

## Risks / Trade-offs

- [模型仍寫「我：…」或省略主體] → 這正是量測目標；分類器把「我」開頭判為②、不算①，標準 2 會顯示。若首輪未達，調措辭重跑，不放寬門檻。
- [`_protNameDiary` 執行期不是「宇璽」而是「主角」] → audit §八 指出 `name1` 未經執行期驗證。tasks 2.1 用測試路徑讀 `window.__cdLastDiaryTest.sys`，確認含「玩家角色名：宇璽」；若是「主角」，玩家主體詞就是「主角」，分類器名單要對應調整**且這要在凍結前做**，所以此驗證排在校準之前。
- [角色名清單的選擇變成調參] → D4 把名單限制在封閉集合內、只為重現已知答案、且在看到任何新資料之前完成；記錄試過哪些組合。
- [重跑會在 #8–#11 各多出一篇同樓層日記] → 這四個是 Step 1 的測試 branch、非正史；重跑前逐檔備份 `.bak_before_step2_rerun_<ts>`；Step 1 那四篇不受影響（append、不覆蓋）。
- [新舊格式混存] → 所有現有讀取點都當字串處理，顯示上只是多了「名字：」前綴；LS 未動工，其輸入契約註記在 proposal Impact。
- [`autoSummary` 在重跑期間若為 ON，#8–#11 沒有新樓層、不會觸發] → 仍依 Step 1 慣例在驗收期間關閉，結束後開回（單向風險，收尾步驟含它）。
- [分類器只量主詞有無與位置、不量歸屬對錯] → 與 audit 相同的工具界線；歸屬對錯由標準 3 的人工判讀補、樣本是 4 個情境的全部新條目，不抽樣。
- [4 個情境的鑑別力] → 預期新條目約 20–30 條。若真實比例仍是 50%，24 條裡「⑤ ≤ 10%」（≤ 2 條）的機率約 3×10⁻⁵；若真實比例已降到 10%，24 條裡超過 10% 的機率約 0.44，也就是門檻對「剛好達標」的 prompt 不友善、會偏向判未達。接受：寧可多跑一輪，不放寬。

## Migration Plan

1. 擴充 repo：確認 `git status` 乾淨、目前在 `diary-player-messages`；`git switch running && git merge --ff-only diary-player-messages && git push fork running`；`git switch -c diary-key-events-actor`。記錄 HEAD。
2. 備份 `index.js` 為 `index.js.bak_key_events_actor_<YYYYMMDD_HHMM>`（不進 commit）。
3. 寫分類器、校準、自我測試、commit 凍結（本 repo elephantfish）。
4. 改 `cdBuildDiaryPrompt` 的 sys 與範本；`node --check`；commit（擴充 repo）。
5. DevTools 勾停用快取、F5；測試路徑確認 sys 含新要求與玩家名。
6. 驗收（D5／D6）；材料寫 `RP記憶/實驗與驗證/Diary_KeyEvents_Actor_驗收_<日期>.md`。
7. 回退：程式層 `git switch running`（或 `diary-player-messages`）；`.bak` 為最後保險；資料層還原四個 branch 的 `.bak`。

## 驗證設計（CLAUDE.md 驗證前置 Gate 五問）

- **Observation**：觀察點是 #8–#11 重跑後聊天檔第一行 `diaries[name][]` 中新 append 的那篇的 `key_events`，以及 Step 1 已落檔的 ground truth。兩者路徑已知、可用 python 讀取。
- **Discrimination**：主判準是機械分類的比例，門檻事前定死（D6），不是主觀判讀；基線 50.0% 來自同一把分類器對 248 條的結果。樣本量鑑別力見 Risks 末條。地板／天花板：舊資料 21%／50% 離 0 與 100 都遠。
- **Construct**：要驗的是「prompt 要求主體之後，`key_events` 是否機械可歸屬」。量的是主體的有無與位置（可歸屬性），加人工判「歸屬是否正確」；不是日記好不好看、不是重複率。
- **Instrument**：分類器先對 248 條凍結基線校準（52／5／19／48／124、合計對帳），加合成樣本測新格式；commit hash 為凍結標記，記入本檔與 handoff；凍結後不改。校準若不符，修的是規則實作與名單（封閉集合內），不是把門檻或分類定義改到吻合。凍結 commit：elephantfish `21250a3`（2026-09-13 14:16:21）。校準結果 52/5/18/48/125，與 audit 差 1 條（使用者選項 A 接受，代名詞納入「主人」）；凍結基線以此為準。prompt commit：擴充 repo `7b861d3`（14:2x），晚於凍結。
- **Occurrence**：每個 branch 重跑後，讀聊天檔對帳「該角色 `diaries` 陣列長度 +1、新篇 `message_id` = 範圍頂樓」，不看面板 toast。四個 branch 都對帳過才開始跑分類器。

## Open Questions

- 玩家名執行期值（「宇璽」或「主角」）：tasks 2.1 驗，結果決定分類器名單，凍結前解決。
- 首輪未達標時：agent 提兩個措辭版本、使用者選一個；agent 不得自行擴 scope（使用者 2026-09-13 拍板）。
