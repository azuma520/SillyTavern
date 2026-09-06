## ADDED Requirements

### Requirement: 玩家訊息開關
擴充 SHALL 提供設定 `includeUserMessagesInDiary`，預設值 `true`，並在設定面板以開關呈現與保存。

#### Scenario: 全新安裝的預設值
- **WHEN** 設定中不存在 `includeUserMessagesInDiary`
- **THEN** 讀取設定時視為 `true`，日記 prompt 納入玩家樓層

#### Scenario: 面板關閉開關
- **WHEN** 使用者在設定面板關閉該開關並保存
- **THEN** 之後每次組裝日記 prompt 都不納入任何玩家樓層，其餘行為不變

### Requirement: 玩家樓層的取用範圍
開關開啟時，日記 prompt 的「本次劇情片段」SHALL 納入以下範圍內的所有玩家樓層（`is_user === true`）：從「本批第一個 AI 樓層之前、聊天陣列中最近一個 AI 樓層」之後，到「本批最後一個 AI 樓層」為止。若本批第一個 AI 樓層之前沒有任何 AI 樓層，範圍起點為聊天陣列開頭。玩家樓層與 AI 樓層 SHALL 依原始樓號遞增交錯排列。

#### Scenario: 正常批次
- **WHEN** 本批 AI 樓層為 1233、1235、1237、1239、1241，且 1231 是 1233 之前最近的 AI 樓層
- **THEN** 場景包含 1232、1234、1236、1238、1240 五個玩家樓層，順序為 1232、1233、1234、…、1241

#### Scenario: 積壓被截到上限
- **WHEN** 待處理 AI 樓層超過 `maxWindowFloors`，`windowFloors` 被截為最後 40 個
- **THEN** 玩家樓層範圍以截後的第一個 AI 樓層為準向前找最近一個 AI 樓層，不擴及被截掉的部分

#### Scenario: 連續多個玩家樓層
- **WHEN** 兩個 AI 樓層之間存在兩個以上玩家樓層（例如玩家連發或刪除 AI 回覆）
- **THEN** 該區間內所有玩家樓層都納入，不合併、不略過

### Requirement: 場景行格式顯式標示來源
場景中每一行 SHALL 以 `[#樓號 來源／名字]` 開頭：玩家樓層來源為 `Player`，AI 樓層來源為 `Assistant`，名字取自該樓層的 `name`。此格式 SHALL 在開關開啟與關閉時皆適用，使開關兩態的唯一差異是有無玩家行。玩家樓層文字 SHALL 套用與 AI 樓層相同的 `filterTags` 過濾。

#### Scenario: 混合場景
- **WHEN** 開關開啟、玩家名為「宇璽」、AI 樓層名為「银趴邮轮」
- **THEN** 場景出現 `[#1232 Player／宇璽] …` 與 `[#1233 Assistant／银趴邮轮] …` 兩種行首

#### Scenario: 開關關閉時的行首
- **WHEN** 開關關閉
- **THEN** 場景只有 `[#樓號 Assistant／名字]` 行，沒有任何 `Player` 行

#### Scenario: 玩家樓層含被過濾標籤
- **WHEN** 某玩家樓層內含 `filterTags` 定義的標籤區段
- **THEN** 該區段從場景行中移除，與 AI 樓層的處理一致

### Requirement: system 提示的資料說明
日記 prompt 的 system 要求清單 SHALL 新增兩項：一行玩家角色名（取自 ST context `name1`，取不到時用「主角」），並註明不為其寫日記；一句中性資料說明，內容為「依訊息 speaker 與時間順序理解劇情；角色回覆可能包含對前一則玩家言行的描述」。system SHALL NOT 加入任何去重、發生次數計算或「轉述不得計為再次發生」類的約束。

#### Scenario: 玩家名可取得
- **WHEN** ST context 回傳 `name1` 為「宇璽」
- **THEN** system 含「玩家角色名：宇璽」字樣並註明不為其寫日記

#### Scenario: 玩家名取不到
- **WHEN** ST context 不可用或 `name1` 為空
- **THEN** system 以「主角」代替，不拋錯、不中斷組裝

### Requirement: 進度機制與其他 prompt 不受影響
玩家樓層 SHALL 只在日記 prompt 組裝時從聊天陣列讀取。`windowFloors`、`processedFloors`、`lastFloor`、`_lastDiaryChatLength` SHALL NOT 因本改動而含有或推進到任何玩家樓層；關係與劇情檔案兩路 prompt 的輸入 SHALL 與改動前完全相同。

#### Scenario: 成功批次後的已處理集合
- **WHEN** 開關開啟、一批日記成功寫入
- **THEN** 該批新增進 `processedFloors` 的樓號全部為 AI 樓層，玩家樓層數為 0

#### Scenario: 關係與檔案 prompt
- **WHEN** 開關開啟且 `enableRelation` 或 `enableArchive` 為 true
- **THEN** 該兩路 prompt 的場景文字與改動前逐字相同

### Requirement: 測試路徑保留完整對照材料
擴充既有的「三路 API 調試」測試路徑 SHALL 在不寫入資料的前提下，把本次日記 prompt 的完整 user 訊息與完整日記回應文字記錄到瀏覽器 console，並存到 `window.__cdLastDiaryTest`，使同一批待處理樓層可在開關兩態下各跑一次並取得未截斷的成對輸出。

#### Scenario: 同批 OFF 與 ON
- **WHEN** 對同一批待處理樓層先關閉開關跑測試、再開啟開關跑測試
- **THEN** 兩次都不改動 `processedFloors` 與日記資料，且兩次的完整 prompt 與回應皆可從 console 或 `window.__cdLastDiaryTest` 取得

#### Scenario: 日誌面板的截斷不影響對照
- **WHEN** 日誌面板的 detail 被截為 500 字
- **THEN** console 與 `window.__cdLastDiaryTest` 仍保有完整內容
