# Tasks: hint-backticks

順序依照 CLAUDE.md「feature 是規格，程式後壁才綴」。

## 1. feature

- [x] 1.1 `features/詞素切割標點.feature` 的 Then 提示字串與描述改成反引號格式；`npx gherkin-lint` 0 錯；`python -m behave features/詞素切割標點.feature` 紅的都是提示字串那幾條（程式還沒改）

## 2. 測試與程式

- [x] 2.1 先改測試：`tests/smkul/test_parser.py`、`tests/smkul/test_report.py` 的提示字串改成新格式；跑測試確認紅在程式還是舊格式
- [x] 2.2 再改程式：`scripts/smkul/parser.py` 的 `_quoted()` 改成反引號、用「、」隔開，`_sentence()` 的括號也改成反引號；2.1 的測試與 1.1 的 feature 轉綠

## 3. 整體驗證

- [x] 3.1 `tox -e test`、`tox -e behave`、`tox -e flake8`、`npx gherkin-lint` 全綠
- [x] 3.2 跑 `python -m scripts.validate_glossing`，報告裡反引號外沒有半形逗號；`grep -rn "有標點「\|有符號「\|有括號「" features scripts tests` 沒有結果

## Workflow follow-up

- `/opsx:archive hint-backticks`，spec 同步到 glossing-validation、corpus-export
