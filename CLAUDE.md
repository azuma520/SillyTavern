# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

SillyTavern is an LLM frontend for power users: a Node.js Express server (`src/`) that serves a vanilla-JS single-page frontend (`public/`) and proxies requests to many LLM backends. AGPL-3.0 licensed. Requires Node >= 20; the whole codebase is ESM (`"type": "module"`).

## Commands

```bash
npm install               # install server deps (post-install also syncs default content)
npm run start             # start server (node server.js), serves http://127.0.0.1:8000
npm run debug             # start with --inspect
npm run start:no-csrf     # start with CSRF disabled (needed for some local testing)
npm run lint              # eslint over src/, public/, root *.js
npm run lint:fix
```

### Tests

Tests live in `tests/` with their own `package.json` — install and run from there:

```bash
cd tests
npm install
npm run test:unit         # Jest unit tests (*.test.js in tests/)
npm run test:e2e          # Playwright (*.e2e.js), expects a running server at http://127.0.0.1:8000
npm test                  # both
```

Run a single unit test file or case:

```bash
cd tests
node --experimental-vm-modules node_modules/jest/bin/jest.js --config jest.config.json util.test.js
node --experimental-vm-modules node_modules/jest/bin/jest.js --config jest.config.json -t "test name"
```

E2E tests (`tests/frontend/*.e2e.js`, mostly for the macro engine) require the server started first, e.g. with `npm run start:no-csrf` from the repo root.

## Architecture

### Server (`src/`)

- Boot chain: `server.js` → parses CLI args (`src/command-line.js`), sets `globalThis.DATA_ROOT` / `COMMAND_LINE_ARGS` → `src/server-main.js` (Express app, middleware, user storage init) → `src/server-startup.js` (route registration).
- **API endpoints**: each file in `src/endpoints/` exports a `router`, mounted in `src/server-startup.js` under `/api/<name>`. LLM backend proxies live in `src/endpoints/backends/` (`chat-completions.js` for OpenAI-compatible APIs, `kobold.js`, `text-completions.js`).
- **Multi-user system**: `src/users.js` — per-user data directories under `data/`, cookie sessions, optional login. Most endpoints operate on `request.user.directories` rather than global paths.
- **Config**: `config.yaml` at repo root (created on first run from `default/config.yaml`); parsing in `src/config-init.js`. User data root defaults to `data/` (overridable via `--dataRoot`).
- **Server plugins**: `plugins/` directory, loaded by `src/plugin-loader.js`; managed with `npm run plugins:install` / `plugins:update`.

### Frontend (`public/`)

- No build step for app code: `public/index.html` loads `public/script.js` (the huge main module) and modules in `public/scripts/` directly as ES modules. jQuery is used throughout.
- The only bundled artifact is `public/lib.js` (third-party libs), webpacked at runtime by a serve middleware (`src/middleware/webpack-serve.js`) — don't import npm packages directly in frontend code; go through `lib.js`.
- **Extensions**: built-in extensions live in `public/scripts/extensions/<name>/`; user-installed ones go to `public/scripts/extensions/third-party/` (gitignored). Extension docs: https://docs.sillytavern.app/for-contributors/writing-extensions/
- Frontend/backend API-specific settings pairs: e.g. `public/scripts/openai.js` (Chat Completion UIs), `nai-settings.js`, `kai-settings.js` correspond to their server-side endpoint counterparts.

### Data

- `data/` — runtime user data (characters, chats, settings); never commit.
- `default/` — templates for config and initial content, synced by `src/server-init.js` / content-manager.

## Contribution Rules (from CONTRIBUTING.md)

- **Target branch: `staging`** for 99% of PRs. `release` only for README updates, GitHub Actions, or critical hotfixes.
- Keep PRs small: soft limit ~200 changed lines; split larger work.
- English only for commit messages, PR descriptions, and code comments (localization files excepted).
- Run `npm run lint` before committing; follow existing naming conventions.

## RP 記憶系統工作（character-diary / LIWE / 世界書）

> 本 fork 的個人使用線，與 SillyTavern 上游無關。所有文件集中在 **`RP記憶/`**，
> 該目錄整個列入 `.git/info/exclude`——**不要 commit、不要進 PR**。
> 在 `RP記憶/` 底下新增檔案**不必**再加 exclude pattern（2026-08-29 由逐檔改為目錄級）。
> 目錄導覽見 `RP記憶/README.md`。

### 觸發：什麼時候必須先讀文件

以下任一情況，**動手前先讀 `RP記憶/RP記憶系統_設計基礎.md`**：

- 使用者提到：記憶系統／日記／填表／liveTable／世界書／劇情檔案／archive／
  角色記不住／角色前後矛盾／LIWE／HCDiary
- 要改 `public/scripts/extensions/third-party/character-diary/`
- 要改 `data/default-user/worlds/*.json`，或 `settings.json` 的 `extension_settings["character-diary"]`

**先看世界書的常駐注入量，再看擴充**——世界書是上游、擴充是下游（2026-08-29 實測：
常駐 18,989 字 vs 記憶注入 668 字，比例 1:28，記憶根本競爭不過）。不先解上游，改下游沒有意義。

### 文件索引

全部路徑相對於 repo 根。完整導覽見 `RP記憶/README.md`。

| 文件 | 內容 | 什麼時候讀 |
|---|---|---|
| `RP記憶/RP記憶系統_設計基礎.md` | **總綱**：五條記憶線、四條實測規律、六條設計原則、診斷手冊、已知的坑、待辦優先序 | **每次動這條線之前** |
| `RP記憶/世界書設計方法_調度篇.md` | 世界書調度欄位、六類知識配置對照、配置矛盾表、檢查清單 | 做或改任何世界書時 |
| `RP記憶/實驗與驗證/記憶體檢_測題與基準_2026-08-29.md` | 失憶測驗八題、標準答案、判分與判讀矩陣 | 要驗證記憶改動的效果時 |
| `RP記憶/實驗與驗證/世界書調度_驗證結果_2026-08-29.md` | 調度改動的三指標實測結果（含已劃掉的錯誤推論與更正框） | 要引用世界書調度的實測數字時 |
| `RP記憶/實驗與驗證/LearnedSelf實驗_原始記錄_2026-08-29.md` | 三組因果實驗逐則編碼、判準閘門、地板效應與驗證漏洞 | 要設計任何注入實驗之前 |
| `RP記憶/結案報告/HCDiary修復結案報告_2026-08-24.md` | 2026-08-24 六項修復、三層防線、關鍵位置備忘 | 需要前次修復的脈絡時 |

### 硬性要求

- **改 `index.js` 前先備份**（`index.js.bak_<原因>_<時間戳>`），改後跑 `node --check`
- **改世界書前先備份**，改後驗證 JSON 可解析
- `data.js` / `engine.js` / `api.js` / `prompts.js` 只是源碼切片，**改它們不生效**，必須改 `index.js`
- Windows 下用 python 讀這些資料**必須**帶 `PYTHONIOENCODING=utf-8`，否則 cp950 編碼會炸
- 擴充改完要 reload：DevTools 開著 + 勾「停用快取」再 F5（`import()` 模組快取，一般重整擋不住）；
  世界書改完要**完全重啟** ST
- **ST 開著時不要在 UI 碰被外部改過的世界書**——前端 `worldInfoCache`
  （`public/scripts/world-info.js:882`）持有舊版，此時在 UI 動任一欄位，
  `saveWorldInfo` 會把記憶體舊版寫回檔案、抹掉外部改動。先重啟、再碰面板
- **驗世界書有沒有注入要看實際生成 log，不是 DRY RUN**——DRY RUN 不套用 sticky，
  看不到真實 prompt 全貌（2026-08-29 實測：同一次生成，實際 9 條 vs DRY RUN 6 條）
- RP 工作文件與素材一律放 `RP記憶/`、不進版控

<!-- workflow-harness:start -->
<!-- 由 workflow-harness plugin 自動加入。本區由 plugin 管理，**請勿手改**。升級用 /init-harness、卸載用 /uninstall-harness（v1.x 後期加）。 -->

## Workflow Harness 規則（plugin 注入）

> 健檢：`/doctor-harness`

### 6 條核心 Guardrails

1. **驗收節點必進 `驗收節點.md` sentinel 區段**（E2）— 時間觸發 + 明確驗收標準走 A 路徑、不可散 backlog / 散別處
2. **多步驟工作（≥3 步 / 跨 tool call）必跑 TaskCreate**（A4）— 開工後新增的子任務用 `TaskUpdate` append、不另開新 list
3. **Handoff 六欄 append-only**（A6）— 同日多 session 寫同檔；前 session 內容不可改；第四欄含【紀律接力】+【當日洞見】sub-segments
4. **Session 開工三步驟順序不可跳**（A3）— 不可在沒讀 handoff 前直接動工；① 跑 `/work-status` 看現況 + 讀最新 handoff、② 讀最新區塊了解進度、③ 綜合現況 + 成熟 backlog 提優先建議；月首 / 週首先 backlog triage、動工前確認本 session 主題
5. **新事件必走 Decision Tree 5 問**（F1）— 不可直接寫進任意 markdown 檔
6. **Session 收工必透過 `/end-session` 寫 handoff**（A5+A6+L9）— 不可只手寫繞過 schema 檢查

### 工作完整性（交接點結清 handoff）

一個工作單位 = 程式改動 + next actor 需要的接力 context（diff 看不出的決策 / 否決的選項 / 風險）。
本地 WIP commit 可不綁 handoff；但**撞到交接點前、未清的 handoff debt 必須結清**：

> 切換 task ・ 停手或 session 結束 ・ push ・ PR ・ shared branch ・ review ・ 改方向 ・ 交另一 session

「交付才算做完」——紀錄是工作的最後一步、不是 commit 尾巴。Plugin 提醒、不擋。

**完成同步**：完成一個工作單位（change 歸檔 / backlog 標完成）時、順手清掉 `next-actions` 與專案 README「Next Actions」裡對應的、已做完的過時條目——這也是完成工作的一部分、在該工作單位的交接點一起收、不事後補。

### 主動 surface 優先建議（感測器、不是判官）

agent 在兩個場景主動提 1-3 條優先建議：

- **開工**：跑完開工步驟、等使用者輸入前
- **被問**：使用者問「先做哪個 / 接下來做什麼 / 排個順序」

effort / impact 當場白話評（「這條一下午能做完」「這條影響最大」）、不寫進條目、不替使用者拍板。

### 「task」這個詞怎麼理解（進出兩個方向）

<!-- 本段是這個詞的辨義規矩本身，指名它才講得清楚；禁用詞掃描 MUST 排除本段。 -->

| 方向 | 規矩 |
|---|---|
| **agent 輸出**（對話、範本、命令說明、hook 訊息） | 一律中文。工作地圖的單位稱「**任務**」；OpenSpec `tasks.md` 內的項目稱「**步驟**」；Claude Code 內建的同名工具 MUST NOT 出現在對外文字中 |
| **使用者輸入**（口語） | **句中同時出現登記動詞時**（清單見登記流程 `work-status-registration`、本處不重抄），該詞指涉之事即為**登記對象**，agent 走登記流程、**不套下方預設**。**句中無登記動詞時**，agent **預設理解為「步驟／逐項執行」**、**MUST NOT** 逕自視為登記請求 |
| 無法判別時 | agent 問一句確認，MUST NOT 猜著做 |

**預設值偏向「不做」**，理由是錯誤成本不對稱：猜成「步驟」而錯 → 少登記一條、使用者補一句即可；猜成「任務」而錯 → agent 擅自寫進使用者的工作地圖，需回頭清理。

**登記動詞優先於預設值**：句中出現登記動詞時意圖已由使用者明示，成本方向反轉——此時不登記才是那個要使用者回頭補的錯。

### 5 問 Decision Tree

新事件來了 → 依序問五題，**遇到 Yes 立刻定位**：

```
Q1: 是「今天做的事」或「session 內進度」？
    → handoff 二、完成事項 / TaskCreate

Q2: 有明確時間觸發（X 月 Y 日要做 / 看）+ 明確驗收標準？
    → 驗收節點.md sentinel 區段（observation-checkpoint V1-V3）；用 `/pending-verify`（別名 `/observe`）建 4 欄 SMART schema

Q3: 是某個 active 專案的事？（≥3 步 / 跨 ≥2 session 才算專案、開資料夾；1-2 步 / 1 session 內結束 → 不開、走 next-actions）
    → 該專案 README.md「Next Actions」或 tasks.md（D4）

Q4: 是規則改動 / SOP 候選 / 累積觀察 / 技術債 / 構想 / bug？
    → backlog.md `## 待辦` heading + 對應主分類 tag（`[SOP 候選]` / `[優化建議]` / `[bug]` / `[構想]`）

Q5: 「想累積樣本評估規則是否有效」（沒明確 deadline、沒明確驗收）？
    → backlog.md `[優化建議]` tag（B 路徑、N=5 surface）

以上都不是 → 問用戶（不可自主裁量）
```

### Slash Commands

- `/init-harness` — 安裝 / 升級 plugin 骨架（含撞檔 matrix）
- `/new-project <name>` — 建專案資料夾（D1 schema）
- `/end-session` — 半自動寫 handoff（對應 Guardrail #6）
- `/doctor-harness` — 自我健檢（hook / template / config）

### Subagent / Tool 慣例

- **動工前先診斷問題**（G4）：repro → root cause → scope → 動手方式

### 優先級

若本區規矩與本檔上方「個人化區段」衝突，**以使用者個人化區段為準**（spec §Risks R4）。
若本區規矩與其他 plugin 衝突（superpowers / sd0x-dev-flow），**以使用者明示優先級為準**（spec §Risks R6）。

<!-- workflow-harness:end -->

<!-- Source: superpowers-bridge/templates/adopters/CLAUDE.md.fragment.md -->
<!-- Drop this section into your project's CLAUDE.md so Claude routes future work using this schema correctly. -->
<!-- Adjust the schema name and bridge repo URL if you customized them; otherwise keep as-is. -->

## Workflow routing (read on session start)

This repo uses [`superpowers-bridge`](https://github.com/JiangWay/openspec-schemas/tree/main/superpowers-bridge) to bridge OpenSpec and Superpowers. Integration rules (language, artifact paths, PRECHECK) follow that bridge's README; this section is the routing guidance for Claude.

### Entry routing

| Trigger you observe | What to do |
|---|---|
| User starts a narrative "design discussion / let's brainstorm" | Run verbal `superpowers:brainstorming`, but **do NOT** write to `docs/superpowers/specs/`. Once the conversation converges per the 5 criteria below, promote to `/opsx:propose` |
| User invokes `/opsx:new` / `/opsx:ff` / `/opsx:propose` directly | Follow the schema's flow; artifact instructions inject at each step |
| User explicitly says bug fix / typo / config tweak / doc update | Direct PR — **do NOT** open a change (see skip rules below) |
| User is mid-change | Advance with `/opsx:continue`, `/opsx:apply`, `/opsx:verify`, or `/opsx:archive` |

### When NOT to use opsx (direct PR)

| Scenario | Direct PR? |
|---|---|
| New feature / new capability / architectural change / breaking change | ❌ Use opsx |
| Bug fix (no contract change) / test backfill / linter tweak / non-breaking upgrade / typo / docs / config value tweak | ✅ Direct PR |

Principle: **process ceremony scales with risk**. External contracts / schema / cross-system integration / compliance → opsx. Otherwise → direct PR.

### Verbal brainstorm → opsx promotion criteria

All 5 must hold before promoting (any missing → keep brainstorming, **never** write to `docs/superpowers/specs/`):

1. **Scope locked** — one sentence describes what's in / out
2. **Major design forks resolved** — alternatives weighed; remaining TBDs have an owner and impact-scope statement
3. **Cross-system dependencies mapped** — ready / mockable / genuinely unknown — pick one per dep
4. **Acceptance criteria stateable** — concrete pass conditions (e.g., `./mvnw clean verify` passes + N deliverables)
5. **Conversation converging** — recent turns are confirmations, not new alternatives

When all 5 hold → proactively suggest "ready to `/opsx:propose`?" — wait for user ack. Never auto-trigger.

### Front-door anti-patterns (don't do)

- Letting brainstorming write to `docs/superpowers/specs/`
- Letting writing-plans write to `docs/superpowers/plans/`
- Promoting to opsx with unresolved blocking TBDs
- Opening a change for bug fix / typo

Full detail: [superpowers-bridge README §Entry & exit gates](https://github.com/JiangWay/openspec-schemas/blob/main/superpowers-bridge/README.md#entry--exit-gates).
