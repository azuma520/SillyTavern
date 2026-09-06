# Session Handoff — 20260906

## Session 09:57

### 一、本 session 主題

Session 開工：跑開工三步驟（`/work-status` → 讀 20260905 最新區塊 → 綜合提優先建議），
尚未進入實質工作。使用者開場輸入為誤貼的 CLI flag，本 session 主題待指定。

### 二、完成事項

- 跑 `/work-status`：主線「RP 記憶系統重構」維持**正在做** 8 天，底下 12 條子項
  （1 條「接下來要做」= LIWE 載體遷移、11 條「還沒開始」），**無完整性提醒**
- 查 `驗收節點.md`：**無到期條目**（09-06 那條驗證前置 Gate 已於 08-30 提前結案、3/3 達標、已打勾）
- 讀 `session-handoff-20260905.md` `## Session 22:26`（該日第 5 個、也是最新區塊），接上接力棒與五條紀律接力
- 掃 `backlog.md` `[mature:]`：**4 條待拍板**（有效範圍多大／`TaskList` 撈不到 completed／
  量測工具校準後凍結／驗訊號前先確認事件發生過）；另有 1 條 `[deprecated:]` 與 1 條 `[graduated:]` 為已收尾
- 提 3 條優先建議給使用者（Learned Self 方向討論／月首 backlog triage + 4 條拍板／研究訊息遮蔽版決策）
- 兌現 20260905 寫下的 propose action（條件「第 2 個 case」已滿足）：開 backlog `[優化建議]` 條目
  「今日 handoff 檢查掛 Stop 與 handoff 語意時機不對齊」，`case-count` 走 `backlog_mark.py` 設為 2、診斷 0 筆

### 三、未完事項 / 接力棒

- [#接力] 20260905 的接力棒**原封未動**：繼續 Learned Self 方向討論（使用者明示留給今天）。
  凍結起點：Production 走既有獨立 AI 管線、Production/Storage/Injection 分開決定、
  **不得**讓 Learned Self 的資料模型去配合 Diary 或 Relation 現成管線
- [#接力] Diary audit 的兩個硬需求要帶進設計討論：提煉層**讀序列不讀單篇**、必須**跨篇去重**
- [#待答] 研究訊息要不要出遮蔽版（成人向語料送外部的內容政策風險）。遮蔽時 MUST 保住
  §5-2「六篇事件不同、結尾句逐字相同」的結構
- [#接力] 月首 backlog triage 尚未執行（9 月已進入第二天、Guardrail #4 要求）
- [#接力] `mood` 簡繁 key 未歸一（`[bug]`，與 Learned Self 解耦、可獨立修）
- [#待確認] 使用者尚未指定本 session 主題（開場輸入為誤貼的 CLI flag `--dangerously-skip-permissions`）

### 四、洞見 / 反省

**【紀律接力】**

- 20260905 的五條紀律接力**尚未有新 case 驗證**，原樣往後帶：① 有專用寫入器的欄位不要用 Edit 改；
  ② 先寫下游登記再讓自己破盲；③ 判讀者之間的多數一致不等於正確（共享同一設計產物時會一致地把
  設計產物讀成發現）；④ 量測工具自己會有 bug、是對帳擋下的；⑤ `TaskList` 撈不到本 session 的 completed task
- 主線 11 條子項維持「還沒開始」7–8 天。這是**狀態維持天數、不等於停滯**（機制測試線本來就是單線推進，
  且該線昨天已收束結案）。但昨日轉向 Learned Self 開發後，這批子項有多條是**機制測試線的遺留**
  （換 probe／修 self-model 量表／修 liveTable／查 t701），下次 triage 該看有沒有該收該併的——
  這已是**連續第二個 session**記下同一則觀察

**【當日洞見】**

- [#反] Stop hook 再次在開工盤點階段 block：今日 handoff 未建立。attribute: `hooks/stop.py` 今日
  handoff 檢查 × Guardrail #6。與 20260905 `## Session 10:57` **完全同型**——本 session 只跑了開工盤點、
  還沒到收工，hook 卻在第一次 yield 就要求今日 handoff 存在。
  **這是第 2 個 case**，昨天寫的 propose action 條件（「待累積第二個 case 後再考慮開 backlog 條目」）**已滿足**。
  本次處理：照六欄模板如實建立首個區塊（append-only，稍後實質工作再 append 或走 `/end-session`），
  不虛構完成事項。propose action: 開 backlog `[優化建議]` 條目，議題為
  「今日 handoff 檢查該掛 Stop 還是掛 SessionEnd」——Stop 每個 turn 邊界都觸發，
  但 handoff 語意上是 session 結束才產生的產物，兩者時機不對齊
- 使用者連續兩天開場誤貼 `--dangerously-skip-permissions`（那是啟動 `claude` 時的 CLI 旗標、不是 prompt）。
  尚不構成需要處理的 pattern，記錄備查

### 五、檔案異動

**版控內**

- `文檔/handoff/session-handoff-20260906.md` — 新建，本區塊
- `backlog.md` — 新開 1 條 `[優化建議]`（L214，Stop hook 時機錯配）+ `case-count set: 2`
  （備份 `.bak_before_stophook_entry_20260906`）

（本 session 無程式改動、無世界書改動、無 ST 操作、無 commit。）

### 六、下一步建議

1. **等使用者指定主題**。三條優先建議已提出，依 impact 排序為：
   Learned Self 方向討論 > 月首 backlog triage + 4 條 `[mature:]` 拍板 > 研究訊息遮蔽版決策
2. 若走 Learned Self 討論：帶著 Diary audit 的兩個硬需求（讀序列、跨篇去重）進去；
   要動 `character-diary` 前**先讀 audit**，尤其 `diaryCharLimit=2` 那個
   「窄視窗同時造成看不到長程變化 + 製造複製污染」的兩難
3. 若走 backlog triage：引用任何 `[case-count:]` 前**先跑 evidence audit**
   （8/30 查出過一條標 5 實際只有 2 件可稽核）；改 `[case-count:]` 走 `backlog_mark.py`、**不要用 Edit**
4. Stop hook 時機錯配已開 backlog 條目（L214、`[case-count: 2]`），**尚未查證** `SessionEnd` 是否為本 plugin 可用掛點——要動手前先確認，別直接假設它在

---

## Session 12:01

### 一、本 session 主題

月首 backlog triage 結案 + `CLAUDE.md §驗證前置 Gate` 由三問擴充為五問 + Learned Self 專案成立。
接續 `## Session 09:57` 提出的三條優先建議，使用者依序拍板：先做 triage（建議 2）、
遮蔽版決策直接結案（建議 3）、最後開 Learned Self 開發線（建議 1）。

### 二、完成事項

**遮蔽版決策結案**

- 使用者表示討論已完成、不需遮蔽版 → `task-20260905-diary-briefing-redact` 標 DONE

**月首 backlog triage（`task-20260905-backlog-triage` DONE）**

- runner `plan` 抓到 3 筆（1 auto_cleanup + 2 mature `[優化建議]`）；另 grep `[mature:]`
  補上 runner 不涵蓋的 2 條 `[SOP 候選]`，共 4 條 mature 逐條做 evidence audit
- **B3 / B4 升級**：「量測工具校準後凍結」與「驗訊號前先確認事件發生過」證據皆 5/5 可稽核 →
  併入 `CLAUDE.md §驗證前置 Gate` 成為 **Instrument** 與 **Occurrence** 兩問（非另立載體），
  並補三者分工說明 + 證據鏈 pointer；backlog 兩行標 `[graduated: 2026-09-06, → …· Instrument / · Occurrence]`
- **驗收節點**新增 2 條（2026-09-20 到期），target 加 `· Instrument` / `· Occurrence` 後綴
  以避開 writer 的「飛行中 graduated target 撞名」擋板；各含「無可驗事件 → 不判未達」邊界條款
- **B1**（有效範圍多大）evidence audit：追到 `b92d5e7be` 一次性以 count 4 開出、僅 2 顆子彈。
  全文搜 handoff 20260829 只有 1 次實例（且自稱「第 3 次」）→ **5 之中僅 3 件可稽核**。
  舊行標 `[deprecated:]`、另開誠實計數新行 `[case-count: 3]` 附三顆逐條可追溯子彈
- **B2**（TaskList）：查上游發現 `anthropics/claude-code` #90709 逐字命中，**改為不開新 issue**。
  普查 `~/.claude/tasks/` 14 個 session 目錄——8 全滅 / 1 部分清除 / 5 完好且皆無 `.highwatermark`，
  命中率 9/14，解釋了本條記過兩次的「間歇性」。根因與上游 issue 寫進條目後標
  `[paused: 2026-09-06, revisit-by: 2026-12-06]` 停止計數
- **L94 刪除**（graduated 賭注鏈已終結），走 triage runner execute、回讀確認
- **L135 補錨點**：查證「設計驗證前先驗證這個驗證」5 條 case 中至少 2 條為遵守型
  （`:96` 做對了、`:99` 擋下來了），該條預言的計數器方向問題由此獲得實例

**Learned Self 專案成立**

- `文檔/專案/Learned-Self/README.md`（`task-20260906-learned-self`、DOING、parent 為主線）。
  `description` 寫死三個凍結起點；Out of Scope 列 5 條已拍板的否決項各附理由與日期
- 4 條相關工作經 `repair --set-parent` 改掛：LIWE 載體遷移（NEXT）、三條設計原則升級、
  LS-001 觀測、修 self-model 量表。主線由 11 條散裝子項變成 4 直屬 + 1 子專案
- `換 probe` 標 PAUSED（與第三輪【擱置·非作廢】同進退）

### 三、未完事項 / 接力棒

- [#接力] **Learned Self 設計討論尚未開始**（本 session 只做到專案成立）。凍結起點見專案
  README frontmatter `description`；下一步子項為「載體從世界書搬到 LIWE」（NEXT）
- [#接力] Diary audit 的兩個硬需求要帶進設計：提煉層**讀序列不讀單篇**、必須**跨篇去重**
- [#待決] **LS-001 觀測的內容需與載體決策一起重寫**——它寫的是「驗 `[WI] Entry 30`」（世界書 uid），
  而本專案已定調載體要搬到 LIWE。搬 parent 已做，內容待設計討論定案
- [#接力] `mood` 簡繁 key 未歸一（`[bug]`，與 Learned Self 解耦、可獨立修）
- [#待修] **triage runner 孤兒子彈 bug 未修**——下次跑 graduated 清理後
  **必須人工檢查上一條有沒有多出子彈**（已開 `[bug]` 條目）
- [#未做] `修 self-model 量表` 已改掛 Learned Self，但其內容是否仍適用（機制測試線已結案）未重審

### 四、洞見 / 反省

**【紀律接力】**

- 20260905 的五條紀律接力**今天有兩條被實際觸發**：① 「有專用寫入器的欄位不要用 Edit 改」——
  今天全程遵守（graduated / deprecated / case-count / paused / set-parent 全走 writer、readback 皆通過）；
  ⑤ 「`TaskList` 撈不到 completed task」——**今天的空結果不是那個 bug**，是我整個 session
  沒跑 TaskCreate（違反 Guardrail A4）。兩者長得一樣、成因完全不同，混為一談會讓 bug 的 case 數繼續灌水
- 其餘三條（先寫下游登記再破盲／多數一致不等於正確／量測工具自己會有 bug）本 session 無新 case、原樣往後帶
- **主線 11 條散裝子項的問題已結清**——連續兩個 session 記的那則觀察今天處理完：
  4 條移進 Learned Self 子專案、1 條標 PAUSED、2 條確認是獨立資料 bug 留原處

**【當日洞見】**

- **[#反] 剛升級成規範的規則，同一個 session 內就沒擋住同型錯誤。** 上午把 `Occurrence`
  （含「搜尋層：沒找遍就宣告不存在」）寫進 CLAUDE.md；下午我只看 `update --help` 就向使用者宣告
  「writer 不支援改 parent」，而 `repair --set-parent` 一直都在。**這是搜尋層的逐字複製。**
  對照組是同一天另一次我**有**套用（讀 code 得到降級 bug 形狀後改用 scratch 副本實跑、
  結果推翻讀 code 的結論）——差別在那次我當場想起要驗。已開 `[優化建議] [case-count: 1]`
- **[#正] Instrument 規則升級後第一次套用就抓到東西。** L194 記載的 bug 根因是錯的：
  原文說「降級會留下矛盾行」，實跑證明**降級這個操作根本不存在**（`set` 對已有計數的條目直接拒絕、
  `bump` 只能 +1、兩條 repair 路徑皆被擋）。且反向不一致（count<5 卻有 mature）連診斷都不會報
  （`backlog_parser.py:1013` 只判單向）
- **[#反] triage runner 有個朝「證據變多」錯的 bug。** graduated 清理只刪條目行、不刪其下子彈行，
  7 顆子彈靜默改掛到上一條——而那條原本零子彈、`[case-count: 1]`。`diagnostics` 回 `[]` 不會報。
  這正是 evidence audit 要防的假象，卻由清理工具自己製造
- **兩條灌水 backlog 條目追到同一個 commit `b92d5e7be`。** 8-30 查出一條、今天查出第二條，
  都是「一次性開出高計數、證據子彈少於計數」。**不是偶發、是當時的習慣**——這比單條的數字更值得記

### 五、檔案異動

**版控內**

- `CLAUDE.md` — §驗證前置 Gate 三問 → 五問（新增 Instrument / Occurrence）+ 三者分工 + 證據鏈 pointer
- `backlog.md` — graduated ×2、deprecated ×1、`case-count set` ×2（誠實計數新行 3、新開條目 1）、
  paused ×1、刪 L94（含人工清 7 顆孤兒子彈）、新開 `[bug]` ×1、prose 補記數處
- `驗收節點.md` — 遠期段新增 2 條（2026-09-20）
- `workflow-harness/work-map.jsonl` — status 更新 ×4、`set-parent` ×4
- `文檔/專案/Learned-Self/README.md` — 新建
- `文檔/handoff/session-handoff-20260906.md` — 本區塊

**備份（未進版控）**

- `backlog.md.bak_before_graduated_20260906` / `_l94_delete_` / `_dispositions_`
- `workflow-harness/work-map.jsonl.bak_before_redact_done_20260906` / `_reparent_`

（本 session 無程式改動、無世界書改動、無 ST 操作。）

### 六、下一步建議

1. **開始 Learned Self 設計討論**（專案已 DOING、下一步子項已現算為「載體從世界書搬到 LIWE」）。
   先讀 `RP記憶/實驗與驗證/LearnedSelf_MVP設計.md` §十一（ownership binding）與 §二（三層資料單位），
   帶著 Diary audit 的兩個硬需求進去
2. 討論的第一個岔路可能是 **LS-001 要不要再在世界書上觀測一輪**——它決定了 LS-001 觀測那條的內容怎麼改
3. **不要**在設計討論裡讓 Learned Self 的資料模型去配合 Diary 或 Relation 現成管線（凍結起點 ③）
4. 若動 `character-diary`，**先讀** `Diary_Audit_能否當LearnedSelf上游_2026-09-05.md`，
   尤其 `diaryCharLimit=2` 那個「窄視窗同時造成看不到長程變化 + 製造複製污染」的兩難
