## ADDED Requirements

### Requirement: 自動總結開關的面板控制
擴充 SHALL 在設定面板提供 `autoSummary` 的開關並保存，使使用者不需經瀏覽器主控台即可切換自動總結，且隨時看得出目前狀態。該設定 SHALL 沿用既有旗標語意：`false` 時不因收到新訊息而自動寫日記，手動寫日記與補寫不受影響。

> 旗標本身已存在於 `DEFAULT_SETTINGS`（預設 `true`）並被 `cdOnMessageReceived` 與 `cdCheckAutoTrigger` 尊重；本需求只新增面板控制與保存，不改變旗標語意。

#### Scenario: 面板關閉自動總結
- **WHEN** 使用者在設定面板關閉該開關並保存
- **THEN** 之後收到新的 AI 訊息不再觸發自動寫日記，且重新載入擴充後開關仍顯示為關閉

#### Scenario: 關閉期間手動寫日記
- **WHEN** `autoSummary` 為 `false`，使用者以「補寫指定範圍」或其他手動入口寫日記
- **THEN** 日記照常產生並寫入，`autoSummary` 不影響手動路徑

#### Scenario: 全新安裝的預設值
- **WHEN** 設定中不存在 `autoSummary`
- **THEN** 讀取設定時視為 `true`，自動總結照常運作

### Requirement: 自動總結關閉時的狀態可見性
當 `autoSummary` 為 `false` 時，擴充 SHALL 讓使用者能在不查閱瀏覽器主控台的情況下確認「目前處於關閉狀態」，而非靜默無回饋。

#### Scenario: 關閉狀態下查詢觸發情形
- **WHEN** `autoSummary` 為 `false`，使用者使用擴充內查詢自動觸發情形的入口
- **THEN** 回應明確指出自動總結目前為關閉狀態
