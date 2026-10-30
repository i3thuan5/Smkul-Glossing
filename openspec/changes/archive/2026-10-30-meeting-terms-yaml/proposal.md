# Proposal: meeting-terms-yaml

## Why

2026.09 語料標註會議（`kithann/2026.09 語料標註語料會議議程.md`）有兩條決議：案由四確認了四行語料與單位的正式名稱（族語原句、詞素切割、詞素翻譯、華語翻譯；組→段），案由九決議「不需要知道哪些詞素是詞根還是詞綴」。現在的 YAML、報告、spec、feature、測試都還是舊用語，而且 YAML 還在輸出「檔案 → 句 → 詞 → 詞素」四層和「構詞」欄。程式已經先動了一部份（YAML 改成「檔案 → 段」、新增語言別代號），規格要補上，其餘的地方也要跟著改，全專案才會只有一套用語。

## What Changes

- **BREAKING（YAML）** 結構從「檔案 → 句 → 詞 → 詞素」改成「檔案 → 段」兩層。每段直接放四行原文：`族語原句`、`詞素切割`、`詞素翻譯`、`華語翻譯`，不再有 `詞`、`原詞`、`切分`、`詞素`、`形`、`義`、`構詞`。
- **BREAKING（YAML）** 檔案層的 `語別` 改成 `語言別`、`句` 改成 `段`，並新增 `語言別代號`：依 `kithann/規範/族語及語言別名稱 - 語言別名稱.csv` 查出代號（例如秀姑巒 → `ami-x-skl`），查不到的話寫空字串、不擋匯出。
- **全專案改用會議的用語**：報告、spec、feature（Scenario 名、Step 內文、例子的標籤）、測試名、README、程式的註解與訊息都改。對照表與不改的例外寫在 design.md。重點如下：
  - 第一行 族語／原文 → 族語原句；第二行 切分 → 詞素切割；第三行 gloss／glossing → 詞素翻譯；第四行 翻譯 → 華語翻譯
  - 組 → 段；語別 → 語言別；切分符號 → 切割符號
  - 長句分段 → 長句換行，一個長句拆成的「段」改叫「截」（兩截、三截）
- **BREAKING（報告）** 問題分類名跟著改，例如 `gloss 的詞比切分少` → `詞素翻譯的詞比詞素切割少`、`原文與切分不符-詞數不同` → `族語原句與詞素切割不符-詞數不同`、`缺 gloss 段` → `缺詞素翻譯行`。
- **feature 檔名跟著改**：`原文切分比對.feature` → `族語原句詞素切割比對.feature`、`切分與glossing對應.feature` → `詞素切割與詞素翻譯對應.feature`，`features/steps/` 下的同名檔一起改。
- **構詞判定暫停**：`features/構詞判定.feature` 留作內部草稿，用語跟著改，但規則暫停維護。報告和 YAML 不再出現任何構詞資訊：拿掉總覽的「構詞無法判斷」、「構詞判斷困難」專章、「不確定」標記統計章、「請對方處理」裡的「構詞判斷困難的詞素要怎麼處理」。glossing 驗證不再呼叫構詞判定。
- **拿掉報告「請對方處理」裡的「用語要不要換成語言學的標準說法」**：會上已經決議。
- **不在這次範圍**：會議的其他決議（案由二、三忽略註解與顏色；案由五標點算錯誤；案由六純華語句沒有四行要警告；案由八空組不警告、提供試算表）另外處理。

## Capabilities

### New Capabilities

（無）

### Modified Capabilities

- `corpus-export`：YAML 改成兩層、key 改名、新增語言別代號；報告拿掉構詞相關章節，用語改成會議的名稱。
- `corpus-parsing`：組 → 段、長句分段重組 → 長句換行重組、`缺 gloss 段` → `缺詞素翻譯行` 等用語；requirement 名稱跟著改。
- `glossing-validation`：族語原句與詞素切割的比對、詞素切割行與詞素翻譯行對應的分類名改成新用語；移除「構詞標記查 ODS 清單」「大寫「不確定」標記」「構詞判定的分類」「詞根判不出來時記無法判斷」四條。
- `docx-txt-consistency`：逐組 → 逐段等用語。

## Impact

- 程式：`scripts/smkul/entry.py`（YAML key、`IssueKind` 的分類名與說明、`NormKind` 指向的 feature 檔名）、`scripts/smkul/yamlout.py`（docstring）、`scripts/smkul/languages.py`（docstring 改成華語）、`scripts/smkul/report.py`（章節用語、拿掉構詞與不確定標記章節）、`scripts/validate_glossing.py`（總覽、統計表欄名、「請對方處理」、不再呼叫構詞判定）、`scripts/check_docx_txt.py`（統計表欄名、用語）、`scripts/smkul/rules.py`、`parser.py`、`pairing.py`、`markers.py`（訊息、註解、docstring）。
- feature：`features/*.feature` 7 份全部改用語，2 份改檔名；`features/steps/` 對應的 2 個檔改名。
- 測試：`tests/smkul/`、`tests/test_corpus_smoke.py` 的測試名、斷言與 YAML key；新增 `tests/smkul/test_languages.py`、`tests/test_validate_glossing.py`、`tests/test_check_docx_txt.py`。每支程式都先改測試再改程式。
- 文件：`README.md`；`CLAUDE.md` 裡「組數／筆數」等用語（要使用者同意才改）。
- 輸出：`kithann/out/corpus.yaml` 結構改變；`kithann/out/*.md` 報告用語改變、章節變少。
- 不動：語料檔案、ODS、CSV、`openspec/changes/archive/`、會議議程。
