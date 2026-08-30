# Session Handoff — 2026-08-30

## Session 10:58

### 一、本 session 主題

開工盤點：跑 `/work-status` 看現況 + 讀 20260829 handoff（三個 session 區塊）+ 提優先建議。
使用者尚未指定本 session 主題，等待選擇工作方向。

### 二、完成事項

- 跑 `/work-status`：確認 1 條 active 工作線（RP 記憶系統重構）+ 9 條子項，
  下一步已釘死為 `A/D positive control`（狀態「接下來要做」）
- 讀 `session-handoff-20260829.md` 三個 session 區塊，取回接力棒與紀律累積
- 提 3 條優先建議（見六）

### 三、未完事項 / 接力棒

<!-- 以下為 20260829 handoff 承接而來、本 session 尚未動的項目 -->

- [#接力] **A/D positive control 未跑**——照
  `RP記憶/實驗與驗證/AD_PositiveControl設計_2026-08-29.md`，成本 5 則 swipe
- [#接力] **動手前先確認 uid 19 / uid 20 都 `disable: true`** + 完全重啟 ST；
  驗注入看**實際生成 log**、不是 DRY RUN
- [#接力] **兩條 SOP 候選已 `[mature: 2026-08-29]`**，待 triage 決定要不要升載體
- [#接力] 量情色准则實際黏著輪數（**連五個 session 掛著未做**）
- [#接力] `t701`「腳踝褪色紅繩」是徐婷婷的特徵串到范婼慧身上，未查
- [#接力] `角色日记日志_... copy.txt` 與正本 md5 相同、可安全刪除

### 四、洞見 / 反省

**【紀律接力】**

- **量情色准则黏著輪數進入第五個 session 未做**——四次被實驗擠掉。
  這已不是「忘記」而是「排序上永遠排不到」，建議下次要嘛做掉（十分鐘）、
  要嘛從工作地圖劃掉，不再滾動

**【當日洞見】**

- 本 session 僅開工盤點、尚未進入實作，無當日洞見可記

### 五、檔案異動

**版控內（本 session 改動）**

- `文檔/handoff/session-handoff-20260830.md` — 本檔新建（本區塊）

**非版控 / repo 外**

- 無改動（全程唯讀）

### 六、下一步建議

- **跑 A/D positive control**（推薦先做）——成本 5 則 swipe，是所有後續分支的閘門：
  k≤1 保留 probe、改注入內容重跑 B/C；k≥3 才換 probe；k=2 加強 D 再測一次
- **triage 兩條 mature SOP 候選**——建議放在實驗跑完等結果的空檔，避免與實驗搶時間
- **量情色准则黏著輪數收掉或劃掉**——查 console `Adding sticky entry start=X end=Y`

---

## Session 11:51

### 一、本 session 主題

量情色准则實際黏著輪數（掛五個 session 未做，接上一 session 六、下一步建議第三條）。
併行開發 session——全程唯讀 ST，未碰世界書、未重啟，與另一 session 無資源衝突。

### 二、完成事項

- **驗證 `sticky` 單位**（不引用前 session 散文、重驗前提）：原始碼四段鏈
  `world-info.js:604-611`（`end = chat.length + sticky`）→ `:648`（到期判斷）→
  `script.js:4565`（`chatForWI` 每則訊息一元素）→ `:4437`（`coreChat` 含 user + AI）。
  官方 enum 自證 `:1586` `'Stays active for N messages'`
- **實測閉環**：`chat_metadata.timedWorldInfo` 四條條目 `end − start` 全等於世界書 `sticky` 值
  （uid18=12、uid2/5/6=8），聊天檔 1240 則全非 system 且 user/AI 嚴格交替
  → **一回合 = 2 則**與**填入值 = 訊息數**同時得證
- **結論：情色准则實際黏 6 個完整回合，與設計意圖一致**——8/29「全面 ×2」修正已生效，
  這條掛五個 session 的待辦是「早就修好、沒人回頭確認」
- **順帶量完誤觸發成本**（原任務真正的目的，見調度篇原「參數沒有依據」那行）：
  離線重演全場 1240 則，取代守 console。真正情色場景 319 則（25.7%）vs uid18 實際生效
  756 則（61.0%），超額約 2.4 倍；其中 key 當場命中 575、純靠 sticky 延長 181
- 文件回寫三處：調度篇「驗證方法」補讀檔法 + 「尚未處理」段填入誤觸發結果與三個折扣；
  設計基礎 §五「常用檢查」加 `timedWorldInfo` snippet、「已知的坑」加 swipe 條目
- 順手更正調度篇「20 個 key」→ 24（第二輪補繁體變體後未回寫的**現況**數字；
  案例段的 4/6 經查是**時序記錄、不動**）
- 工作地圖 `task-20260829-measure-nsfw-sticky` → `DONE`（已備份、JSON 全行可解析）
- backlog `[優化建議] TaskList 撈不到 completed task` case-count 2 → 3（本次又重現）

### 三、未完事項 / 接力棒

- [#新接力] **A/D positive control 的 uid 21 必須設 `constant`、不可靠 `sticky`**——
  `world-info.js:626` 的 `chat.length <= start && !protected → delete` 配上 swipe 的
  `script.js:4438` `coreChat.pop()`，會清掉「上一次生成剛建立的」sticky 窗口。
  該計畫要 swipe 5 次，靠 sticky 撐會在第一次 swipe 就掉、實驗未開始先污染
- [#未做] **人工判讀 20-30 則校準代理指標**——「該則含情色詞」高估誤觸發，85.6% 是上界。
  2026-08-30 決定「先知道就好」、不另立條目，文件已標「尚未做」
- [#接力] A/D positive control 未跑（成本 5 則 swipe）；動手前確認 uid 19 / 20 皆 `disable: true`
  + 完全重啟 ST；驗注入看**實際生成 log**、不是 DRY RUN
- [#接力] 兩條 mature SOP 候選待 triage
- [#接力] `t701`「腳踝褪色紅繩」是徐婷婷的特徵串到范婼慧身上，未查
- [#接力] `角色日记日志_... copy.txt` 與正本 md5 相同、可安全刪除

### 四、洞見 / 反省

**【紀律接力】**

- **「掛很久的待辦」的結局可能是「早就做完了，只是沒人回頭確認」**——量情色准则掛五個
  session、每次寫進 handoff、每次被擠掉，一查發現 8/29 第二輪修正就已修好，今天只是去確認。
  滾動中的待辦要定期回頭驗**它是否還成立**，不是只排序。
  （2026-08-30 決定不另立條目，等第二個 case 再走 A 路徑）
- **SessionStart hook 注入的信號本身也是「繼承來的前提」**——今天 hook 說兩條 SOP 候選
  「累積到 5 case」，實際上另一 session 當天已因「計數不實、僅 2 件可稽核證據」
  deprecate 舊條目、重開為 2。**hook 注入 ≠ 已驗證**，與 line 103 同一個形狀

**【當日洞見】**

- **主犯不是 `sticky`，是 `key`**——原假設「sticky 12 太長」不成立：sticky 只貢獻 24%
  的生效量，砍到 0 仍有 76% 由 key 當場命中。**修參數前要先量各來源佔比**，否則會修錯零件
- **自鎖迴圈第一次有全場量化證據**——含情色詞的訊息 AI 自己寫 284 則 vs 使用者 35 則（8:1）。
  以前只有單一案例（T2 那則零情色暗示卻不退）。倍數要打折（AI 訊息本就較長）
- **差點把「時序記錄」誤判成「錯誤」**——調度篇案例段寫 4/6、檔案是 8/12，我判定為漏回寫
  並正要動手改，讀到後面才發現「第二輪修正」段已記 ×2，那是有意的歷史層次。
  **動手改文件前先讀完整份的時序結構**
- **我自己犯了「引用前提沒驗證」**——模擬用的 `DEPTH=2` 抄自文件，跑完才想起沒驗，
  回頭確認 `settings.json`（`world_info_depth=2`、`scanDepth=null`）才成立。
  這條規則今天是我自己踩的
- 依 2026-08-30 判斷：三條「遵守 pattern」的 case **不 bump** case-count——
  line 115 已指出混計「違反」與「遵守」的語意問題未解，且 CLAUDE.md 新「驗證前置 Gate」
  第 136 行明文「衍生狀態不可直接當證據用」

### 五、檔案異動

**版控內（本 session 改動）**

- `workflow-harness/work-map.jsonl` — `task-20260829-measure-nsfw-sticky` 標 `DONE`
- `backlog.md` — line 113 case-count 2 → 3（**注意：本檔同時含另一 session 的改動**）
- `文檔/handoff/session-handoff-20260830.md` — 本區塊 append

**其他 session 的改動（本 session 未碰、勿混入 commit）**

- `CLAUDE.md` — 新增「驗證前置 Gate」規範層
- `驗收節點.md`
- `backlog.md` 的 line 99 deprecate + line 103 重開部分

**非版控 / repo 外**

- `RP記憶/世界書設計方法_調度篇.md` — 驗證方法補讀檔法；「尚未處理」段填入誤觸發實測 + 三折扣；key 數更正
- `RP記憶/RP記憶系統_設計基礎.md` — §五加 `timedWorldInfo` snippet；「已知的坑」加 swipe 條目
- `workflow-harness/work-map.jsonl.bak_before_nsfw_sticky_done_20260830` — 改動前備份

### 六、下一步建議

- **A/D positive control**（推薦先做）——成本 5 則 swipe，是所有後續分支的閘門。
  **uid 21 記得設 `constant`**（見三、新接力）
- **triage 兩條 mature SOP 候選**——注意其中一條（line 81）今天已由另一 session
  升級成 CLAUDE.md「驗證前置 Gate」，triage 前先確認現況、別重複升級
- **人工判讀 20-30 則校準代理指標**（低優先）——要把誤觸發的 85.6% 上界收成真值、
  才好定 `cooldown`

---

## Session 11:57

### 一、本 session 主題

Triage 兩條 `[mature: 2026-08-29]` 的 `[SOP 候選]`——一條升級成 `CLAUDE.md §驗證前置 Gate`、
一條因證據不實降級重開；接著用這條剛升級的 Gate 對 A/D positive control 跑**第一次 Validation Preflight**。
實驗本身未跑（依使用者決定留到下個 session），但事前登記已全部寫死。

### 二、完成事項

**Triage（Evidence Audit → Pattern Gate → Compile → Graduate → Acceptance）**

- **A 條「設計驗證前先驗證這個驗證」evidence audit 通過**：5 條證據子彈行齊備，
  抽驗 2 條原始出處對得上（`handoff:283` 分母錯 14 倍、`handoff:348` context 邊界），
  且橫跨 3 種失敗型態（觀察點不存在 1 / 判準不可判讀 1 / 測錯構念 3）
- **A 條升級**：編譯成 Trigger / Action / Boundary 三問 Gate（Observation / Discrimination / Construct）
  寫入 `CLAUDE.md §驗證前置 Gate`（放 harness sentinel 區段**之上**、避免被 `/init-harness` 改寫）；
  backlog 原句與 5 條案例保留作歷史，正式載體只放編譯後條文
- **開驗收節點**（due 2026-09-06）：acceptance 明寫「驗**規則有沒有被執行**、不是實驗有沒有成功」
  ——D 組推不動、實驗判 null 仍可達標
- **B 條「引用前一 session 前提前先驗證」evidence audit 未通過**：`git log -p` 查出該條在
  `b92d5e7be` 一次性以 count 4 開出、僅附 1 條證據，`2a72f3418` bump 至 5 加第 2 條。
  **count 5、可稽核證據 2**
- **B 條降級**：舊行蓋 `[deprecated: 2026-08-30]` 留作 audit 紀錄、另開誠實計數新行（`case-count: 2`），
  證據子彈行移至新行。**不是默默改數字**
- **裁定今天這次「發現 count 不實」不計入 B 的 case**：理由是**誘發性**（由 triage 動作誘發、
  非自然發生），計入等於讓 triage 自己餵養升級門檻。已寫成不計數的 observation 子彈行

**Validation Preflight（Gate 的第一次實戰，三欄各抓到一件事）**

- **Observation**：設計文件寫「與基線用完全相同的腳本判定」，查出**該腳本從未存在**。
  補寫 `RP記憶/工具/丟球判準.py`，用已知答案校準 → 13/15 ✅
  且組別分佈 A3/B5/C5 與設計文件記載全中
- **Discrimination 判定「未確認」→ 依 Gate 規定當場改設計**：pooled 基線 13/15 混三組，
  A 組單獨僅 3/5。D=0/5 對 pooled p=0.0014（顯著）、對 A-only p≈0.083（不顯著）
  ——**結論會因基線取法而翻面**。修法：今天同場加跑 5 則 A，成本由 5 則 swipe 增為 10 則
- **Construct 收窄措辭**：D 是指令式注入、B/C 是敘事式，`k≤1` 只證明指令通道通。
  原判讀矩陣「今天的 null 是內容問題」改寫為「也可能是敘事型注入本身不走這條通道，本輪分不開」
- **實查 uid 19 / 20 皆 `disable: true`**（handoff 遺留的疑慮不成立），uid 21 尚未存在

**事前登記（`AD_PositiveControl設計` §八之三，六項，早於任何實驗資料）**

1. 判準凍結 `sha256=b1e7e0ae…f5d6`，新資料後不得改
2. 主要基線改為 **A_today**，昨天 pooled 13/15 降為歷史參考
3. 檢定方向**事前宣告單尾**（單尾 0.083 / 雙尾 0.167，不得事後挑）
4. 執行順序 `secrets.choice` 丟硬幣得 **D 先**、不重擲（代價：重啟 ST 兩次）
5. 判讀護欄：**先看今天 A 還在不在，再解釋 D**；A_today 若也只剩 0–1/5 → **不得宣布 D 成功**
6. Construct 最終範圍：只回答「同一注入位置能不能用一條直接指令推動穩定行為」，不得推出「B/C 內容不好」

**backlog**

- 新開 `[優化建議]` `[case-count:]` 語意混計（count 1）、`[bug]` writer 無降級路徑（含 root cause 三處行號）、
  `[構想]` Gate 第二層 hook（含已查證的設計約束）、`[SOP 候選]` 量測工具校準與凍結（count 1）

### 三、未完事項 / 接力棒

- [#接力] **A/D positive control 未跑，但 Gate 已過、事前登記已鎖**——
  下個 session 照 `RP記憶/實驗與驗證/AD_PositiveControl設計_2026-08-29.md` **§八之三**執行
  （§七的舊步驟已被 §八之三取代）
- [#接力] **動手前先重算 `丟球判準.py` 的 sha256 比對**
  （`b1e7e0ae3bd1c048eee9e56d0ce68d3a94b57d5b78811c14448f8a23cb77f5d6`）；
  `RP記憶/` 在 exclude 內、無法 commit，hash 是唯一凍結證據
- [#接力] **work-map 的 `task-20260830-ad-positive-control` 描述仍寫「swipe 5 次」**——
  實際已改為 10 則（D 5 + A 5）。以設計文件為準
- [#不重議] uid 21 必須 `constant=true`、不可靠 `sticky`（另一 session 查證，見 11:51 區塊）
- [#不重議] Gate 第二層 hook **刻意延後**，等規則被證實有幫助或確定需要 hook 才開發
- [#接力] `[case-count:]` 混計「違反」與「遵守」的語意問題**已擱置不追**，但它影響所有
  `[case-count:]` 的解讀，包括 A 條那 5 條是否也混了「照做」型
- [#接力] `t701`「腳踝褪色紅繩」未查；`角色日记日志_… copy.txt` 可安全刪除

### 四、洞見 / 反省

**【紀律接力】**

- **升級規則的第一步必須是 Evidence Audit，不能信 `[mature:]` / `[case-count:]` 這些衍生狀態**
  ——B 條今天就是被這一步擋下的。使用者把它定為 Graduation 流程的固定第一步，
  已寫進 `CLAUDE.md §驗證前置 Gate` 末條
- **TaskList 這次撈得到 completed task**（前兩次收工回空、已累積到 `[case-count: 3]`）。
  **這是一個反例、不是修復證據**——沒有動過任何設定，行為卻不同。
  下次收工要再觀察一次才知道是間歇性還是已恢復。**沒有 bump、也沒有標 done**
- **不計入「誘發型」case 這條判準是今天新立的、尚未律定**——寫在 `[優化建議]` 條的提案欄。
  之後若有第二個 case 再考慮升載體
- **併行 session 共用 working tree**：`backlog.md` / `work-map.jsonl` 同時含兩個 session 的改動，
  commit 前必須攤開講清楚、不可默默一起收

**【當日洞見】**

- `[#決策]` **Gate 從「執行前」移到「兌現前」**——查 `hooks/hooks.json` 只有
  `SessionStart` / `Stop` / `PreToolUse(Edit|Write)` 三個掛點，而在 ST UI 裡 swipe 跑實驗
  **不產生任何 hook 事件**。gate 掛不到「執行前」那個時刻。可機械擋的位置是結果被兌現前
  （寫結論／寫 `[graduated:]` 都是檔案寫入）。而且這更忠於條文——觸發條件本來就掛在
  「結果**將被用來**做決定」，不是掛在測試的執行
- **harness 的 writer 是 fail-closed 的，今天擋了我一次**：先標 `[graduated:]` 被拒
  「驗收節點容器找不到對應載體」。**不允許開空頭支票**，必須先有驗收節點才准升級
- **校準抓到的是斷句缺陷、不是判準爭議**——初版 14/15，查出旁白「…朝你招了招手：」
  被黏進對白問句「站那麼遠幹嘛？」，讓問句繼承旁白的第二人稱。
  修 `「」`／換行當句界後 13/15。**分辨「修缺陷」與「調到吻合」的差別是這件事的全部價值**
- **設計文件自己寫了「本設計最脆弱的假設」然後就放著跑了**——§九-3 早就寫下 A-only 3/5 的問題，
  但沒有任何機制強迫在執行前處理它。Gate 的作用不是**發現**新問題，
  是**強迫已經寫下來的問題在執行前被結清**
- **丟硬幣的代價要當場認**：D 先意味著重啟兩次 ST。若當時選「哪個方便」，
  就會是 A 先（零世界書改動），而那個理由事後無法與「看了才決定」區分
- **`[graduated:]` 的配對是載體字串逐字相等**（`verification_parser.py:90`，
  且 code span 內的引述不算開獎證據）——兩邊差一個字就是真孤兒

### 五、檔案異動

錨來源：SessionStart 時間戳（N=1h）。git log 視窗內**無 commit**。

**版控內（本 session 改動）**

- `CLAUDE.md` — 新增 §驗證前置 Gate（規範層 + 「為什麼現在沒有 hook」的查證記錄）
- `backlog.md` — A 條標 `[graduated:]` + evidence 註記；B 條舊行 `[deprecated:]` + 新行 `case-count: 2`；
  新開 4 條（`[優化建議]` ×1、`[bug]` ×1、`[構想]` ×1、`[SOP 候選]` ×1）
- `驗收節點.md` — 新增 1 條（due 2026-09-06、載體 `CLAUDE.md §驗證前置 Gate`）
- `文檔/handoff/session-handoff-20260830.md` — 本區塊 append

**併行 session 的改動（本 session 未碰、同在 working tree）**

- `workflow-harness/work-map.jsonl` + 其 `.bak_before_nsfw_sticky_done_20260830`
- `backlog.md` 的 line 115（`TaskList` 條 case-count 2 → 3）
- `文檔/handoff/session-handoff-20260830.md` 的 `## Session 11:51` 區塊

**非版控（`RP記憶/`，整個目錄已 exclude）**

- **新建**：`工具/丟球判準.py`（判準腳本、已校準、已凍結 hash）
- **改動**：`實驗與驗證/AD_PositiveControl設計_2026-08-29.md`（新增 §八之二 Preflight、§八之三 事前登記）

**repo 外**

- 無改動（僅唯讀查 `银趴邮轮世界书.json` 的 uid 18–21 狀態）

### 六、下一步建議

- **下個 session 專做實驗**：照 `AD_PositiveControl設計` **§八之三**的 7 步走
  （§七已被取代）。動手第一件事是重算判準腳本 hash
- **順序不可改**：D 先、A 後。這是丟硬幣決定並登記過的，看到 D 結果後不得調整 A 的跑法
- **判讀第一句話一定是「今天 A 的 baseline 還在不在」**——A_today 若掉到 0–1/5，
  無論 D 多漂亮都不得宣布成功
- **不要碰 `injectDiary`**、不要在實驗結束前改 diary 系統
- 實驗跑完後可考慮：`[case-count:]` 語意混計那條要不要動（會連帶重審 A 條的 5 條證據）
