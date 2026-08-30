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

- [SOP 候選] [case-count: 1] 診斷系統行為問題前，先盤點所有會影響該行為的輸入來源並量化佔比，再決定從哪下手
- [SOP 候選] [case-count: 5] [mature: 2026-08-29] [graduated: 2026-08-30, → CLAUDE.md §驗證前置 Gate] 設計驗證前先驗證這個驗證：觀察點存不存在、判準能不能機械判讀、測的是不是你以為的那個東西
  → handoff 20260829 四（八題失憶測驗有兩題失效，答案就在世界書裡，測到的是世界書不是記憶）
  → handoff 20260829 四（世界書驗證：先查出三個 console 觀察點才設計得出可判讀的測試；另查出 4 個會讓測試測出錯誤結論的配置意外）
  → handoff 20260829 四（量禁令洩漏率時拿 617 則 AI 訊息當分母，該角色實際只出現 44 次——分母錯 14 倍，數字讀起來「沒問題」其實是稀釋出來的）
  → handoff 20260829 四（self-model 量表信度極高但測錯構念：三位盲編碼者一致把「泛用大學生人格替換」評為最高分。「測的是不是你以為的那個東西」這一問，儀器再準也擋不住）
  → handoff 20260829 四（Learned Self 實驗差點建在錯前提上：先查 `lastInContextMessageId=1059` 才知道要測的告解室早已掉出 context 358 樓；另兩處——原判準「像不像經歷過一千多樓的她」不可機械判讀、測題問「你記得嗎」測到的是 recall 不是延續）
  → **evidence 2026-08-30**：5 verified cases / 3 failure classes（觀察點不存在 1、判準不可判讀 1、測錯構念 3）。抽驗 2 條原始出處皆對得上（`handoff:283` 分母錯 14 倍、`handoff:348` context 邊界）
  → 升級形式：backlog 原句保留作歷史與證據，正式載體放**編譯後**的 Trigger / Action / Boundary，不搬整串案例
- [bug] [done: 2026-08-29] 角色卡開場白與世界書禁令互相矛盾：范婼慧開場白說「刚才远远看见还他妈以为是看错了」，世界書「絕對避免」寫著「他媽…不是她的詞彙」。修法是改開場白那一句；影響的是每一場**新聊天**的起手（現有 1226 樓那場開場白早已滾出 context）
  → 2026-08-29 量測：她在場 381 則裡禁用詞命中 4 則（≈1%），其中 1 則就是這句開場白（簡體、角色卡帶的，非模型生成）；允許詞「靠/哎呀」命中 182 則（≈48%），禁令大致有效
  → 通則：開場白是每場新聊天最權威的範例——它是「她說過的話」不是設定，具體範例會打贏抽象禁令（規律三）
- [SOP 候選] [case-count: 3] 診斷出根因不等於該修：決定要不要動手前，先回到實際要解決的問題，再過成本 / 風險 / 可歸因 / 效益 / 頻繁程度五關
  → 情色准则自鎖：診斷成立（key 與產物同源、ST 無「只掃使用者訊息」的乾淨解），但只觀察到 1 次、修法要付漏觸發代價 → 先量實際黏著輪數再定，不當場改
  → 不更新 LIWE v2.9.5：唯一有價值的修復非當前痛點，卻會打掉兩項本地修復且新版無替代品 → 診斷清楚但不動
  → 情色准则 key「乳」：只改誤觸發（換成乳房/乳頭/乳溝），不動自鎖——使用者判斷「反正都要玩 NSFW、目前沒影響體驗」，成本方向壓過診斷完整性
  → diary 三個機制缺陷（窗口重疊 75% / 每篇讀前兩篇正文的 inertia / 後 30 篇飽和）全部診斷出來，但建議不動：修窗口會影響現有日記品質，而 Learned Self 要做的正好是日記做不到的那件事
- [SOP 候選] [case-count: 2] 拿下游產物解釋上游行為之前，先確認兩者之間有沒有回饋路徑——沒有回饋就只是觀察紀錄，不是因果證據
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

- [優化建議] [case-count: 4] 把「在這個條件下觀察到 X」寫成「X 就是這樣」——陳述前先問這個結論的有效範圍多大
  → 前三次記於 handoff 20260829（含「詮釋會錯而痕跡不會」被使用者擋下）
  → handoff 20260829 六（我寫「近期 context 支配力遠大於新增世界書條目」。正確範圍是「**在這個 probe 下**，近期 context 剛好備有『玩太兇』的現成材料」。不可一般化成「世界書永遠撬不動 177 則 context」。**第 4 次，且這次是被外部 agent 擋下、不是使用者**——模式一樣：把條件句寫成全稱句）

- [優化建議] [case-count: 3] `/end-session` 第一步的 `TaskList` 撈不到本 session 的 completed task（回 "No tasks found"），完成事項每次都得從 context 重建——Guardrail A4 要求跑 TaskCreate，但收工端接不到它的產物

- [優化建議] [case-count: 1] `[case-count:]` 在數什麼未定義：混計「違反 pattern」與「遵守 pattern」，導致一條**越有效**的規則越快到 5、越快觸發升級 surface——計數器方向與它要衡量的東西（值不值得升級）不一致
  → 2026-08-30 triage 發現。實例：「引用前一 session 前提前先驗證」條的第 2 條證據明寫「**這次照做了、抓到兩個**」，遵守被計為 case
  → 連帶待審：已判定證據充足的「設計驗證前先驗證這個驗證」5 條 case 是否也混了「照做」型
  → 附帶提案（**尚未律定**）：只計自然發生的 case；triage / 複盤 / 週報等「正在檢視這條規則」時誘發的觀察記為 observation、不計入
  → 2026-08-30 使用者裁定：先擱著不追，避免拖成大工程擠掉 A/D 實驗

- [SOP 候選] [case-count: 1] 量測工具寫完要先用已知答案校準；校準不符時修工具的缺陷、不是把參數調到吻合，且校準完就凍結（hash / commit）不得在看到新資料後再改
  → handoff 20260830 四（A/D 丟球判準腳本初版跑基線得 14/15、期望 13/15。查出是斷句沒把 `「」` 與換行當句界、旁白的「你」被黏進對白問句造成偽陽性——修的是斷句缺陷。修完 13/15 且組別分佈 A3/B5/C5 全中。同時記錄一個**不修**的保守偽陽性，偏誤方向對 positive control 安全）
  → 與已升級的 `CLAUDE.md §驗證前置 Gate` Observation 那一問相鄰但不同：Gate 問「觀察點存不存在」，這條問「儀器準不準、以及誰有權在什麼時候改它」。若累積更多 case，可考慮併入 Gate 而非另立載體

- [bug] backlog validated writer 只有升級路徑、沒有降級路徑，count 由 5 降為 2 會留下自相矛盾行且 agent 無合法路徑修
  → root cause：`hooks/lib/backlog_mark.py` 三處——`_maybe_atomic_mature`（`:547`）在 N<5 時「unchanged」、不移除既有 mature 標籤；`repair` 的 `remove mature`（`:721`）**無條件**擋下（註解意圖是防「count≥5 卻無 mature」，但沒判斷 count，降級情境被一起擋）；`reconcile_mature`（`:693`）只刷新日期、不移除，且要求先存在 lifecycle-invariant 診斷
  → 症狀：`case-count set: 2` 後留下 `[case-count: 2]` + `[mature: 2026-08-29]` 併存
  → 2026-08-30 triage 遇到。繞道方案：舊行蓋 `[deprecated:]` + 另開誠實計數的新行

- [構想] 驗證前置 Gate 第二層：把 Preflight 做成 harness 的狀態轉移條件（contract 定義 + hook 最小機械 enforcement），沒過 gate 就不能往下走
  → **刻意延後**（2026-08-30 使用者裁定）：等「這條規則被證實真的有幫助」或「確定現行規範層需要 hook 輔助」時才開發。理由——現在直接設計 enforcement，等於在一個還沒跑過的流程上做 gate，違反規則自身
  → 已查證的設計約束：`hooks/hooks.json` 只有 `SessionStart` / `Stop` / `PreToolUse`(`Edit|Write`) 三個掛點；ST UI 裡 swipe 跑實驗**不產生任何 hook 事件**，gate 掛不到「執行前」。可機械擋的位置是**結果被兌現前**（寫結論 / 寫 `[graduated:]` 都是檔案寫入）
  → 現成範本：`hooks/backlog_write_guard.py`（PreToolUse 真 gate、官方 `permissionDecision: "deny"` 契約、目標未確認 fail-open / 確認後 fail-closed、薄殼 + 純 lib 分層）
  → 已知漏洞：「是不是 decision-bearing validation」是自我宣告，而要防的失敗模式正是 agent 沒認真想——擋在兌現端可緩解（兌現動作客觀可辨識，不依賴事前宣告）
  → hook **只做機械 enforcement**（三欄有沒有填），內容合不合理由 agent / reviewer 判斷——不可讓 LLM 判「你寫得對不對」，那本身又是個未驗證的儀器
  → 屬 plugin capability 變更，走 opsx change、不走 direct PR
