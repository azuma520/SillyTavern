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
