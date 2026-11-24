## Why

翻譯訓練YAML 的開始、結束現在是 docx 的原字串，語料裡至少有六種寫法（逗號式、SRT 式、`-->` 配小數點、en-dash 式、連字號的`分:秒:影格`、毫秒省略前面的 0），下游每次用都要自己解讀，很容易讀錯：統計各語言別秒數時，霧台被當成 `時:分:秒`、中排灣的 `,72` 被當成 0.72 秒，算出來都不對。另外有 17 行時間碼打錯（後面黏字、編號黏在前面、時間打錯），程式認不出來，會把下一段併進上一段，判成「行黏在一起」，兩段都不匯出，報告上的原因也不對。

## What Changes

- **BREAKING** 翻譯訓練YAML 的 `開始`、`結束` 一律轉成 SRT 字串（`HH:MM:SS,mmm`，例如 `00:00:27,880`），不再是原字串。
- 新增一種能轉的寫法「`-->` 配小數點」（南排灣 3，`0:01:07.227 --> 0:01:14.786`），跟其他四種一樣轉成 SRT 字串。
- 連字號式照`分:秒:影格`（30fps）換算，影格 ÷ 30 四捨五入到毫秒；「時間碼單位不明」照樣記，請對方確認。
- 時間有問題的段，開始、結束都記成數字 `-1.0`，另外記一筆警告（照常匯出），段照常匯出：
  - 新增「時間碼毫秒位數不對」：毫秒只有一位或兩位數（中排灣 1、2、4、5 共 148 行，泰雅 1 一行）。
  - 「結束時間早於開始」也改成記 `-1.0`。
  - 新增「時間碼行打錯」：編號行的下一行有`數字:數字`的樣子、卻解析不了，照樣當成這一段的時間碼行，段界照常切。
- **BREAKING** 刪掉「時間碼格式混用」：YAML 已經統一，寫法不一致對老師來說沒有要修的東西。
- 報告「語料格式說明」的時間碼表改成五種能轉的寫法，說明都轉成 SRT 字串；「自動處理」的時間碼一項改成「拆開始、結束並轉成 SRT 字串」。
- 難判斷的三種（編號黏在時間碼前面、時間碼拆成兩行、時間碼後面黏著族語原句）照 `features/時間碼.feature` 的 `@規格要討論` 處理，這次不做特別判斷。

## Capabilities

### New Capabilities

（無）

### Modified Capabilities

- `corpus-parsing`：時間碼格式的 requirement 改成「轉成 SRT 字串」，加「`-->` 配小數點」、連字號式 30fps 換算、毫秒位數不對、時間碼行打錯，刪掉格式混用；段結構異常加「時間碼行打錯」。
- `corpus-export`：YAML 的開始、結束改成 SRT 字串或 `-1.0`；語料格式說明章與自動處理章的時間碼說明改寫。

## Impact

- `scripts/smkul/parser.py`：時間碼解析、轉換、段界判斷（`parse_timecode`、`_entry_starts`、`split_entries`）。
- `scripts/smkul/entry.py`：`IssueKind` 加兩種、刪一種，`SEVERITY`、`KIND_WHY`、`NORM_WHY`；`Entry.start`、`Entry.end` 可能是字串或 `-1.0`。
- `scripts/smkul/report.py`：時間碼表、筆數說明。
- `features/steps/時間碼.py`：新 step（開始與結束都是 -1.0、記一筆…、讀入這幾行的段層級檢查）。
- 測試：`tests/smkul/test_parser.py`、`test_entry.py`、`test_report.py`、`tests/test_validate_glossing.py` 裡用到 `MIXED_TIMECODE_FORMAT` 的地方。
- 下游：讀 `kithann/out/corpus.yaml` 的人，開始、結束的格式變了，要用 `-1.0` 判斷時間不能用。
