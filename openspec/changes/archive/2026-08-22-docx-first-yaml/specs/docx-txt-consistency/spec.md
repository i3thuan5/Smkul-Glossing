# docx-txt-consistency Delta

## REMOVED Requirements

### Requirement: txt 的註解錨點算差異

**Reason**: txt 不再是語料來源，錨點殘留不再影響匯出。
**Migration**: docx 審閱註解仍由「docx 審閱註解要抽出來列入報告」需求呈現；`docx_txt_report.md` 只做歷史核對。

### Requirement: txt 混入的註解本文

**Reason**: 同上，txt 不再是語料來源。
**Migration**: 無需處理；註解本文仍在報告的審閱註解章逐條列出。

## MODIFIED Requirements

### Requirement: 檔案配對檢查

檢查 SHALL 以「同目錄同檔名（不含副檔名）」配對 docx 與 txt。只有單邊存在的檔案 SHALL 列為提醒（不是錯誤，因為語料以 docx 為準）：缺 docx 的 txt 請對方補 docx；缺 txt 的 docx 照常進語料。已知的檔名不一致配對（魯凱霧台 3：`包鳯嬌…月桃文化及製作上集.txt` vs `包鳳嬌…月桃的文化及製作_上集.docx`）SHALL 列為提醒，語料以 docx 檔名為準。

#### Scenario: 缺 txt

- **WHEN** 太魯閣 2 只有 docx、沒有 txt
- **THEN** 報告列出「缺 txt」提醒，該檔照常進語料

#### Scenario: 檔名異體字不一致

- **WHEN** 魯凱霧台 3 的 txt 與 docx 檔名不同（鳯/鳳、標題微差）
- **THEN** 報告列出「檔名不一致」提醒，YAML 的路徑用 docx 的檔名
