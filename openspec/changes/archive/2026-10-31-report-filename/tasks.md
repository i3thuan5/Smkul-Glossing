# Tasks: report-filename

## 1. feature 與 step

- [x] 1.1 `features/分析報告.feature`：描述的檔名改成 `Glossing驗證報告.md`，「報告的章節」加一行 `And 報告的檔名是 "Glossing驗證報告.md"`；`npx gherkin-lint` 0 錯
- [x] 1.2 `features/steps/分析報告.py`：新增檔名的 step，讀報告改用新檔名；`python -m behave features/分析報告.feature` 紅在程式還是舊檔名

## 2. 測試與程式

- [x] 2.1 先改測試：`tests/test_validate_glossing.py` 的檔名改成新的；確認紅在程式還是舊檔名
- [x] 2.2 再改程式：`scripts/validate_glossing.py` 的報告檔名改成常數 `REPORT_NAME = "Glossing驗證報告.md"`；`README.md` 跟著改；2.1 與 1.2 轉綠

## 3. 整體驗證與輸出

- [x] 3.1 `tox -e test`、`tox -e behave`、`tox -e flake8`、`npx gherkin-lint` 全綠；`grep -rn "glossing_report" scripts tests features README.md` 沒有結果（剩下的是 step 檢查舊檔名沒有再產生）
- [x] 3.2 跑 `python -m scripts.validate_glossing`，產生 `kithann/out/Glossing驗證報告.md`；刪掉舊的 `kithann/out/glossing_report.md`

## Workflow follow-up

- `/opsx:archive report-filename`，spec 同步到 corpus-export
