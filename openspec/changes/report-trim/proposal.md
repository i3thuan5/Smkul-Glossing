# Proposal: report-trim

## Why

glossing_report.md 要轉成 docx 交給業務單位，校對表交給族語老師，翻譯訓練YAML 交給下游。三種產出的對象不一樣，可是現在的規則混在一起：校對表把純華語句、孤兒時間碼這類老師沒辦法處理的問題也列進去；報告還留著已經用不到的章節（問題明細、上次會議的討論、老師判斷兩章、構詞標記清單的對照）；docx／txt 一致性報告在會議決議「以 docx 為主」（案由一）、「審閱註解忽略」（案由二）之後也沒有用了。這次用**嚴重度**統一決定三種產出的行為，並把用不到的部分拿掉。

## What Changes

- **嚴重度決定三種產出**：
  | 嚴重度 | 翻譯訓練YAML | 報告舉例 | 請老師校對 |
  |---|---|---|---|
  | 錯誤 | 不匯出 | 舉例 | 要 |
  | 錯誤（照常匯出） | 匯出 | 舉例 | 要 |
  | 警告（照常匯出） | 匯出 | 舉例 | 不要 |
  | 現象 | 不匯出 | 舉例 | 不要 |
- **空段、孤兒時間碼從「錯誤」改成「現象」**：一樣不匯出，但不再算錯誤、不影響 exit code、不請老師校對。
- **BREAKING（校對表）只列「錯誤」與「錯誤（照常匯出）」**：純華語句、空段、孤兒時間碼、時間碼的警告不再列入。
- **報告總覽**：
  - 加上上面那張嚴重度對應表。
  - 問題表加兩欄，變成「編號、問題、嚴重度、筆數」；排序是先依嚴重度、同一級裡筆數多的在前。第 7 章「問題類型說明與例子」的小節照同一個順序排，所以「編號 3」就是「第 7.3 節」。
- **報告與 spec 裡的「YAML」改稱「翻譯訓練YAML」**。檔名 `kithann/out/corpus.yaml` 與 YAML 的 key 都不改。
- **BREAKING（報告）刪掉這些章節**：
  - 開頭的「標記清單：`…ods`」那行，以及語料格式說明的「語料目錄與標記清單 sheet 的對應」一節（構詞判定停用後已經沒有作用）。
  - 「問題明細」整章：有第 7 章的例子與校對表就夠了。
  - 「討論」整章：上次會議的議程，已經討論過。
  - 「老師標要討論的項目」「老師確認過、不是錯誤」兩章：老師的判斷只留在校對表；讀回校對表時的提醒改列在「校對流程」一節。
- **BREAKING 刪掉 docx／txt 一致性檢查**：`scripts/check_docx_txt.py`、它的測試與 README 說明、`kithann/out/docx_txt_report.md` 不再產生；`docx-txt-consistency` capability 整份退役。

## Capabilities

### New Capabilities

（無）

### Modified Capabilities

- `corpus-export`：新增「嚴重度決定三種產出」；「報告內容」換成只有 glossing 報告的新版本（總覽的對應表與編號、沒有問題明細與討論章）；「報告附校對資訊」換成只有「校對流程」一節；「語料格式說明專章」拿掉目錄與 sheet 的對應；「自動處理說明專章」「對照式差異分兩行呈現」只剩 glossing 報告；「只因註解殘留造成的差異不重複列出」移除；「YAML 匯出結構」「exit code」改用語與例子。
- `proofreading`：「產生校對表」只列錯誤兩級；「程式判斷錯的問題不再算問題」「要討論與 docx 要修改」不再寫進報告的章節。
- `docx-txt-consistency`：全部 requirement 移除，capability 退役。

## Impact

- 程式：`scripts/smkul/entry.py`（空段、孤兒時間碼的嚴重度；刪掉 docx／txt 比對的 4 種問題）、`scripts/smkul/report.py`（總覽問題表、第 7 章排序、刪掉的章節函式）、`scripts/validate_glossing.py`（總覽、刪章節、校對流程一節加讀取提醒、不再讀 ODS）、`scripts/smkul/proofreading.py`（只收錯誤兩級）；刪除 `scripts/check_docx_txt.py`、`scripts/smkul/pairing.py`（`split_kind()` 搬到 `languages.py`）、`docx2text.py` 的審閱註解抽取。
- 測試：`tests/test_check_docx_txt.py`、`tests/smkul/test_pairing.py` 刪除，`tests/smkul/test_docx2text.py` 拿掉審閱註解的測試；`tests/smkul/test_report.py`、`tests/test_validate_glossing.py`、`tests/smkul/test_proofreading.py`、`tests/smkul/test_entry.py` 跟著改。
- 文件：`README.md` 拿掉 check_docx_txt 的說明；`openspec/specs/docx-txt-consistency/` 退役；`corpus-export` spec 的 Purpose 改寫。
- 輸出：`kithann/out/docx_txt_report.md` 不再產生（舊檔已刪）；glossing_report.md 少了 5 個部分；校對表列數從 3650 降到 3327；YAML 段數不變；exit code 計數的錯誤從 3269 降到 3224。
- 不動：`features/*.feature`、YAML 檔名與 key、docx 內文不含審閱註解的檢查（corpus-parsing「語料來源為 docx」）。
