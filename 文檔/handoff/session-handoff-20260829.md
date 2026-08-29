# Session Handoff — 2026-08-29

<!--
本檔每個 session 結束時 append 一個 ## Session HH:MM 區塊。
六欄 heading 順序固定，缺漏會被 Stop hook block。
四欄內 sub-segment marker（**【紀律接力】** / **【當日洞見】**）缺漏會 Stop hook ⚠️ Warn（不 block）。
-->

## Session 08:09

### 一、本 session 主題

在 SillyTavern fork（elephantfish worktree）執行 `/init-harness`，安裝 workflow-harness plugin 骨架。

### 二、完成事項

- git preflight 確認在 git repo 內（branch `azuma520/dangerously-skip-permissions`、working tree 乾淨）
- 跑 runner plain init，七目標全數成功：`CLAUDE.md` append plugin 區段、`backlog.md` / `驗收節點.md` / `.workflow-harness.yaml` build、`文檔/handoff` / `文檔/專案` / `文檔/週報` mkdir

### 三、未完事項 / 接力棒

- [#接力] 跑 `/doctor-harness` 確認安裝健康
- [#接力] 決定 harness 新建檔案是否納入版控；此 repo 是 SillyTavern fork，若不想進上游 PR 可加進 `.git/info/exclude`
- [#接力] 開新 session 觀察 SessionStart hook 是否注入規矩

### 四、洞見 / 反省

**【紀律接力】**

- harness 檔案目前未 commit、也未決定排除策略，下個 session 開工前先處理，避免混進功能 branch 的 diff

**【當日洞見】**

- [#決策] 專案原有 `CLAUDE.md` 走 append 路徑（present-without-marker），原內容 byte 不動、plugin 區段以 marker 包在檔尾——無需 `--force-replace`

### 五、檔案異動

- `CLAUDE.md` — 檔尾 append workflow-harness plugin 規則區段（marker 包覆）
- `backlog.md` — 新建（`## 待辦` + tag schema）
- `驗收節點.md` — 新建（template copy）
- `.workflow-harness.yaml` — 新建（template copy、opt-in 標記）
- `文檔/handoff/`、`文檔/專案/`、`文檔/週報/` — 新建空目錄
- `文檔/handoff/session-handoff-20260829.md` — 本檔

### 六、下一步建議

- 先跑 `/doctor-harness` 健檢，再決定 harness 檔案的版控策略（commit 或 `.git/info/exclude`）
- 之後開新 session 驗證 SessionStart hook 注入行為，確認後即可正常開工

## Session 08:20

### 一、本 session 主題

三套工具鏈進場安裝：workflow-harness（/init-harness + /doctor-harness）、sd0x codex-setup（init + doctor）、openspec superpowers-bridge schema。

### 二、完成事項

- `/init-harness` 七目標全數成功；`/doctor-harness` 15 項 ✅ / 0 ⚠️ / 0 ❌
- `/codex-setup init`：AGENTS.md 產生（2149 bytes）、commit-msg + pre-push hooks direct 模式安裝、`.sd0x/` runner scripts + install-state.json；`doctor` 六項檢查零漂移
- superpowers-bridge schema 安裝：`openspec init` → clone JiangWay/openspec-schemas → `openspec/schemas/superpowers-bridge/`（VERSION 1.0.0）→ validate ✓ → `openspec schemas` 列出
- CLAUDE.md append 英文版 workflow-routing fragment（`## Workflow routing`）
- Superpowers plugin 確認已裝（5.1.0 enabled）、暫存 clone 已清理

### 三、未完事項 / 接力棒

- [#接力] 決定三套工具鏈產物的版控策略：`CLAUDE.md`（modified）、`AGENTS.md`、`.sd0x/`、`openspec/`、`.gemini/`、harness 檔案——commit 或 `.git/info/exclude`
- [#接力] 開新 session 驗證 SessionStart hook 注入
- [#接力] `.gemini/` 是 `openspec init` 非互動模式順帶產生的 Gemini CLI 整合，用不到可刪

### 四、洞見 / 反省

**【紀律接力】**

- 三套工具鏈（workflow-harness / sd0x codex / openspec superpowers-bridge）產物皆未 commit，版控策略（commit vs `.git/info/exclude`）尚未拍板
- SessionStart hook 注入行為尚未驗證（需開新 session 才看得到）

**【當日洞見】**

- [#決策] CLAUDE.md 三次疊加（專案說明 → harness marker 區段 → bridge routing 區段）依安裝順序 append、互不衝突；bridge fragment 用英文版
- Windows 下 git clone 的 pack 檔帶唯讀屬性，`shutil.rmtree` 需 onexc chmod 才刪得掉；`rm -rf` 被 permission 擋
- sd0x git hooks 裝在主 repo `D:/AI/SillyTavern/.git/hooks`，波及該 repo 所有 worktree

### 五、檔案異動

（本 session 無 commit、git log 1h 視窗為空；以下為 working tree 改動）

- `CLAUDE.md` — modified：append harness 區段 + bridge routing 區段
- `AGENTS.md`、`.sd0x/`（scripts + install-state.json）— 新增（codex-setup）
- `openspec/`（schemas/superpowers-bridge + init 骨架）、`.gemini/` — 新增（openspec）
- `backlog.md`、`驗收節點.md`、`.workflow-harness.yaml`、`文檔/` — 新增（init-harness）
- `D:/AI/SillyTavern/.git/hooks/commit-msg`、`pre-push` — 新增（repo 外部 state、不進版控）

### 六、下一步建議

- 拍板版控策略後收一個 commit（或整批進 `.git/info/exclude`）
- 開新 session 驗證 SessionStart hook；之後即可用 `/opsx:propose` 或 harness 流程正常開工

## Session 11:42

### 一、本 session 主題

RP 記憶系統診斷：從「日記怎麼優化」一路追到「世界書才是上游」，把世界書改為調度式，並產出三份可重複運用的基礎文件。

### 二、完成事項

- 前兩個 session 的接力棒結清：版控策略已於 `55f360bf6` 拍板（commit）、SessionStart hook 注入行為本 session 驗證正常
- 清掉 backlog 的 plugin template 範例條目（四條與本 repo 無關的假料）
- 補裝 Claude Code 的 openspec 整合（`openspec init --tools claude`），刪掉用不到的 Gemini 版；發現原先 `CLAUDE.md` 指向的 `/opsx:*` 命令在 Claude 端根本不存在（commit `d20e52c97`）
- 盤點 character-diary 五條記憶線的生產／注入狀態：確認日記是「純寫入零讀取」、archive 與 relations 已關閉、**世界書是唯一真正在工作的那條**
- 追出日記完整生產鏈路（觸發 → 抓取即鎖定 → 建 prompt → 呼叫 → mergeDiaries），並找到「失敗批次永久丟失」的 bug：鎖定在選定時、回滾只在拋例外時，而三種失敗形式都不拋例外
- 診斷 archive 四類語意的失敗根因：覆蓋式出口被「防 AI 漏輸出」的補救機制（`_overwriteKeepMissed`）反殺，退化成追加式
- 設計八題失憶測驗並實測（2/16），意外測出「模型在事實上誠實、在人物反應上虛構」
- 追出虛構來源：世界書的行為範例用記敘語氣寫成，被模型當史實逐字複述（關鍵詞全文搜尋 0 命中，證實為虛構而非錯記）
- 評估 LIWE v2.9.5，決定不更新（詳見四）
- 世界書改為調度式：常駐 18,989 → 5,346 字（-72%）。三個 NPC 改關鍵字觸發 + `sticky=4`、新增 204 字名冊（`preventRecursion`）維持存在感、敘事指南拆成「通用常駐／情色觸發」兩條
- 產出三份可重複運用的文件 + `CLAUDE.md` 新增 RP 記憶系統工作區段（觸發條件 / 文件索引 / 硬性要求）
- 更新記憶檔 `rp-memory-spec-decisions`，把 8/24 的架構定案改寫成反映本次轉折

### 三、未完事項 / 接力棒

- [#接力] **驗證世界書調度改動**（Task #7）：重啟酒館玩十來輪，看三個指標——注入量是否下降、三個 NPC 是否不再無故出現、她們登場時是否退化（`sticky=4` 夠不夠）。有問題調 `sticky` / `scanDepth`，或從三份備份逐級還原
- [#接力] 修 liveTable「持有物品」去重 + 漏記（優先序 1，現有線、已在注入、修好立刻見效）
- [#接力] 建懸念線（優先序 2，**出口用「逐條問是非」不用「重寫全貌」**）
- [#接力] 建劇情湧現設定線（優先序 3，資料現成、範圍限劇情長出來的）
- [#接力] 日記接出口（優先序 4，`diaryVectors` / `cdSearchVectors` / rerank 骨架現成、從未啟用）
- [#接力] 「敘事風格指南」拆分後尚未驗證是否影響寫作品質；NSFW 條目 key 開得寬，留意誤觸發
- [#接力] 行為範例仍是記敘語氣，改寫成條件語氣的工作量大，等記憶線建好後再評估是否仍有虛構

### 四、洞見 / 反省

**【紀律接力】**

- **診斷系統行為問題時，先盤點所有輸入來源並量化佔比再下手**——今天繞了三個版本的問題定義（日記沒接出口 → 容器形狀錯 → 記憶沒被注入）才發現世界書是上游。已開 backlog `[SOP 候選] [case-count: 1]`
- **驗證測驗要先確認答案不在其他來源**：八題裡 D 類兩題失效，因為答案就在世界書的常駐條目裡，測到的是世界書不是記憶

**【當日洞見】**

- **三個系統同一個病**：archive 缺出口、世界書缺調度、日記缺讀取——**都只設計了「進」，沒設計「出」和「用」**
- **archive 的教訓**：防禦措施（防 AI 漏輸出）反殺了原設計（覆蓋式出口）。根因是「重寫全貌」不可單點驗證 → 必須加防漏 → 防漏必然堵死出口。**解法是把 LLM 的工作降級成「逐條問是非」**
- **實測**：記憶的有無 = 有沒有被注入，跟資料存不存在無關。**沒有 Injection 的 Storage，價值是零**
- **實測**：模型在事實性問題上誠實說「不記得」，在「角色會怎麼反應」上虛構整段且不標記——因為後者有人設可推演。而那正是 RP 裡最常被問的問題類型
- **範例與史實在模型眼裡沒有區別**，唯一能分的是字面語氣（記敘 vs 條件）
- `[#決策]` **不更新 LIWE v2.9.5**——唯一有價值的回滾修復非當前痛點，卻會打掉 `cdLiveBatchGate` 與簡繁歸一兩項本地修復，且新版無替代品（其 batch 實作用易失的記憶體計數器，比本地版本差）
- **知識不放在會被讀到的地方等於零**——這條今天用在自己身上：把文件索引寫進 `CLAUDE.md`，而不是讓文件躺在磁碟上

### 五、檔案異動

**已 commit**（`d20e52c97` Switch OpenSpec integration from Gemini CLI to Claude Code）

- `.gemini/commands/opsx/*` + `.gemini/skills/openspec-*/` → `.claude/` 對應位置（git 識別為 rename）
- `.gitignore` — 新增 `.workflow-harness/`
- `backlog.md` — 清掉 template 範例條目

**working tree（待 commit）**

- `CLAUDE.md` — 新增「RP 記憶系統工作」區段（+37 行，未動兩個 plugin marker 區）
- `backlog.md` — 新增 `[SOP 候選] [case-count: 1]`

**非版控（已列入 `.git/info/exclude`）**

- `RP記憶系統_設計基礎.md` — 新建（總綱）
- `世界書設計方法_調度篇.md` — 新建（專題）
- `記憶體檢_測題與基準_2026-08-29.md` — 新建（工具）
- `Agent記憶設計解析.md` — 補列入 exclude

**repo 外**

- `D:/AI/SillyTavern/data/default-user/worlds/银趴邮轮世界书.json` — 三次改動（觸發式 / 名冊 / 拆敘事指南），三份對應備份 `.bak_before_keytrigger|roster|split_20260829`
- `C:/Users/user/.claude/projects/D--AI-SillyTavern/memory/rp-memory-spec-decisions.md` + `MEMORY.md` — 更新

### 六、下一步建議

- 重啟酒館玩十來輪驗證世界書改動，三個指標：注入量下降、NPC 無故出現、登場表現
- 確認無副作用後，第一刀砍 liveTable「持有物品」的去重 + 漏記——它現有、已在注入、修好立刻見效
- 之後依序：懸念線 → 劇情湧現設定線 → 日記接出口
