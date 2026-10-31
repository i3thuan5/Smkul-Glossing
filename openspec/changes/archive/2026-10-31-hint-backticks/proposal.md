# Proposal: hint-backticks

## Why

CLAUDE.md 規定報告內文的逗號要用全形，只有反引號內的語料照原樣。「詞素切割有標點」的提示把出問題的字元寫成「有標點「,」」，那個 `,` 是引用語料，可是不在反引號裡，報告第 7 章就留下半形逗號，看起來像違反規定，也分不清是內文還是語料。

## What Changes

- **BREAKING（報告、校對表的提示文字）**：提示裡被引用的字元改用反引號包起來，跟其他語料的寫法一樣：
  - 「有標點「,」」→「有標點 `,`」
  - 一個詞有好幾種標點：「有標點「?」「!」」→「有標點 `?`、`!`」（用頓號隔開）
  - 「有符號「＠」」→「有符號 `＠`」
  - 「有括號「()」」→「有括號 `()`」
- `features/詞素切割標點.feature` 的 Then 提示字串跟著改。
- 判定規則、提示的其他部分（位置、原因、應該寫是）都不變。

## Capabilities

### New Capabilities

（無）

### Modified Capabilities

- `glossing-validation`：「詞素切割標點的錯誤提示」的格式與例子改用反引號。
- `corpus-export`：「問題類型說明與例子」的例子跟著改。

## Impact

- 程式：`scripts/smkul/parser.py` 的 `_quoted()` 與 `_sentence()`。
- feature：`features/詞素切割標點.feature`。
- 測試：`tests/smkul/test_parser.py`、`tests/smkul/test_report.py`。
- 輸出：報告第 7 章「詞素切割有標點」的例子、校對表的提示欄。問題 ID 不受影響（ID 不含提示文字）。
