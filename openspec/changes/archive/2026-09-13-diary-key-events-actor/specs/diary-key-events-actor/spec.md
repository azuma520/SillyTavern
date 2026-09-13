## ADDED Requirements

### Requirement: key_events 每條以行為主體開頭
日記 prompt 的 system 要求清單 SHALL 包含一條對 `key_events` 的契約：每條關鍵事件 MUST 以行為主體開頭，格式為「主体：事件」（全形冒號）。JSON 範本中 `key_events` 的 placeholder SHALL 為 `["主体：事件"]`。

#### Scenario: 角色自己的行為
- **WHEN** 日記主人「范婼慧」在本批樓層中做了「主动索吻」
- **THEN** 該篇 `key_events` 含「范婼慧：主动索吻」，而非「主动索吻」或「我：主动索吻」

#### Scenario: 玩家的行為
- **WHEN** 玩家角色名為「宇璽」且玩家在本批樓層中「答应下周再来」
- **THEN** 記錄此事的 `key_events` 條目為「宇璽：答应下周再来」

### Requirement: 主體詞彙限定
主體 SHALL 只能是「已知角色名单」中的主名，或 system 中宣告的玩家角色名。日記主人自己做的事 SHALL 寫主名、SHALL NOT 用「我」。多人共同行為 SHALL 寫主要發起者一人。

#### Scenario: 別名歸併
- **WHEN** 劇情片段以「小秘書」稱呼已知主名為「范婼慧」的角色
- **THEN** `key_events` 的主體寫「范婼慧」

#### Scenario: 兩人共同行為
- **WHEN** 玩家提議、角色同意一起去某處
- **THEN** 該條主體為提議方一人，不寫「宇璽与范婼慧：」

### Requirement: schema 與既有資料不變
`key_events` SHALL 維持字串陣列；本能力 SHALL NOT 新增任何輸出欄位，也 SHALL NOT 修改既有日記資料。所有既有讀取點（面板、時間軸、搜尋、編輯器、匯出、收藏、單篇重寫）SHALL 對新舊格式皆正常運作。

#### Scenario: 新舊格式混存
- **WHEN** 同一角色的 `diaries` 陣列中同時有「介绍今晚压轴剧目」與「范婼慧：介绍今晚压轴剧目」兩條
- **THEN** 面板與時間軸以字串原樣顯示兩者，搜尋「压轴」兩條皆命中，編輯器以逗號分隔顯示、儲存後陣列元素不變

#### Scenario: 輸出鍵集合
- **WHEN** 新 prompt 產出一篇日記並寫入
- **THEN** 該篇的鍵集合與既有日記相同（turn／date／entry／mood／attitude_to_user／secret／key_events／relationship_with_others／message_id）

### Requirement: 單一 prompt 組裝點
本契約 SHALL 只加在 `cdBuildDiaryPrompt` 的 system 要求清單與其 JSON 範本，使測試路徑、正式生成、單篇重寫三個呼叫點同時生效。

#### Scenario: 測試路徑可見
- **WHEN** 使用者執行日記測試路徑
- **THEN** `window.__cdLastDiaryTest.sys` 含「key_events 每条必须以行为主体开头」字樣與「玩家角色名：<name1>」
