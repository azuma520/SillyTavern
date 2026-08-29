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
- [SOP 候選] [case-count: 2] 設計驗證前先驗證這個驗證：觀察點存不存在、判準能不能機械判讀、測的是不是你以為的那個東西
  → handoff 20260829 四（八題失憶測驗有兩題失效，答案就在世界書裡，測到的是世界書不是記憶）
  → handoff 20260829 四（世界書驗證：先查出三個 console 觀察點才設計得出可判讀的測試；另查出 4 個會讓測試測出錯誤結論的配置意外）
