# Proposal: report-filename

## Why

報告要轉成 docx 交給業務單位，檔名 `glossing_report.md` 是英文，對方看不出是什麼。檔名改成跟報告標題「Glossing 驗證報告」一樣，拿到檔案就知道內容。

## What Changes

- **BREAKING（輸出檔名）**：`kithann/out/glossing_report.md` 改名為 `kithann/out/Glossing驗證報告.md`。報告內容不變。
- `features/分析報告.feature` 的「報告的章節」加上檢查檔名，step 跟著改。
- 舊檔 `kithann/out/glossing_report.md` 在重新產生後刪掉，免得被誤用。

## Capabilities

### New Capabilities

（無）

### Modified Capabilities

- `corpus-export`：「glossing 報告的章節」寫的檔名改成 `kithann/out/Glossing驗證報告.md`。

## Impact

- 程式：`scripts/validate_glossing.py`。
- feature：`features/分析報告.feature`、`features/steps/分析報告.py`。
- 測試：`tests/test_validate_glossing.py`。
- 文件：`README.md`。
- 不動：翻譯訓練YAML 與校對表的檔名。
