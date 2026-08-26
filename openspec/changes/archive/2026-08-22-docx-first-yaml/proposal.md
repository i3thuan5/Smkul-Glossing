# Proposal: docx-first-yaml

## Why

實測證明 txt 的註解殘留（105 個 `[字母]` 錨點、114 行註解本文）全部可以用同名 docx 的 110 條審閱註解一對一解釋，而 docx 本身的內文（`word/document.xml`）從來沒有混進註解——註解本文在 `word/comments.xml`，錨點只是零文字的 `commentRangeStart/End` 標記。所以與其對照 docx 去清 txt，不如直接從 docx 產生語料，整條「註解殘留」的處理鏈都可以拿掉。同時，「標記不在清單」的 872 筆經分析有大半不是清單缺漏，而是程式的詞根判定規則判錯（`=` 後面的實詞被當成附著詞去查表）或一個詞裡不只一段是實詞，這些應該當成「構詞判斷困難」而不是擋匯出的錯誤。

## What Changes

- **BREAKING** 語料來源從 txt 改為 docx：`validate_glossing.py` 走 `kithann/giliau/**/*.docx`，YAML 的「路徑」欄變成 `.docx`。太魯閣 2（只有 docx）因此進入語料；魯凱霧台 3 以 docx 的檔名為準。
- 移除「註解殘留」整條處理：`parser.strip_comments` 及其輔助函式、`features/註解殘留.feature`、報告 5.10/5.11 兩節。docx 審閱註解仍抽出來列在報告（條數與逐條內容），但**不進 YAML**。
- 「標記不在清單」降級：不再是擋匯出的錯誤。該詞素的「構詞」欄寫 `無法判斷`，整組若沒有其他錯誤照樣匯出。報告收掉 6.2、第 8 章聚合表、10.2，合併成新的一章「構詞判斷困難」，只寫摘要與統計，細節指向 `features/構詞判定.feature`。
- 依 `features/構詞判定.feature` 的「判斷方法」把構詞判定整個做出來：`構詞` 從 5 個值（詞根/詞綴/附著/中綴/重疊）細分成 8 個（詞根/前綴/後綴/環綴/中綴/依附詞/重疊/無法判斷），詞綴改成靠 gloss 查表反推詞根，不是看符號在哪一邊。
- 報告第 3 章改寫為「YAML 由 docx 產生」；第 4、5 章合併，每項只寫摘要並指向對應的 `features/*.feature`，例子不再複製進報告。第 9 章尾句加「建議補充到《常用構詞標記清單》」。
- 順序固定：先改 feature，再寫 steps，再改程式，最後 `python -m behave --no-skipped` 全綠。apply 過程中若覺得某條 feature 不合理，記在 tasks.md、先跳過，做完一併回報，不中途停。

## Capabilities

### New Capabilities

（無）

### Modified Capabilities

- `corpus-parsing`：輸入從 txt 改為 docx 段落；移除註解殘留的清除需求。
- `glossing-validation`：「構詞標記查 ODS 清單」從錯誤改為「無法判斷」標記；新增三種構詞判斷困難情形的分類。
- `corpus-export`：YAML 來源說明改為 docx；「構詞」欄多一個值 `無法判斷`；報告刪 5.10/5.11、6.2、第 8 章、10.2，新增「構詞判斷困難」章；自動處理章改為摘要＋指向 features。
- `docx-txt-consistency`：「txt 的註解錨點算差異」「txt 混入的註解本文」兩項需求作廢（txt 不再是語料來源）；配對檢查降為歷史核對。

## Impact

- 程式：`scripts/validate_glossing.py`（collect 走 docx）、`scripts/smkul/parser.py`（拔 strip_comments 一族、`parse_corpus_file` 吃 `docx_paragraphs`）、`scripts/smkul/rules.py`（check_markers 改回傳無法判斷、pick_root 的 A 類）、`scripts/smkul/entry.py`（Attachment 加 `無法判斷`、IssueKind 調整）、`scripts/check_docx_txt.py`、`scripts/smkul/report.py`。
- feature / steps：
  - 刪 `features/註解殘留.feature`。
  - `features/構詞判定.feature`：「判斷方法」第 3 點補「分不出詞根的，構詞記『無法判斷』，可以進 YAML」；加一條「2a 依附詞：= 在詞根前，詞根是華語借詞」（`tja=黑板`，全語料 413 個詞）。
  - `features/排版分析.feature`、`features/字元正規化.feature`：不用改——docx 段落的兩個特徵（組間無空行、寬空白成單一空白）已經被「組間缺空行照常切組」「多餘的空白合併成一個」兩條蓋住。
  - `features/steps/自動處理.py`：拔掉 `strip_comments` 的 import 與「docx 的審閱註解是」「讀入這幾行有註解殘留」「清掉註解後是」三個 step（註解殘留.feature 刪了就沒人用）。不用加新 step——「讀入這幾行」本來就是餵行序列，docx 段落也用它。
  - `features/steps/構詞判定.py`：`判定結果是` 的比對要認得新的構詞值 `無法判斷`（現在 feature 寫「（無法判斷）」是表格裡的佔位字，step 要把它對到 `Attachment.UNDECIDED`）。
- 測試：`tests/` 裡所有讀 txt 的 fixture 對應調整。
- 報告：`kithann/out/glossing_report.md` 章節重排。
- 語料檔案本身不修改。
