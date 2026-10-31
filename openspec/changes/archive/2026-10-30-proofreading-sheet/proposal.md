# Proposal: proofreading-sheet

## Why

2026.09 語料標註會議案由八決議：「提供 Google Sheet 或 Excel，給老師們註記『已修正』或『正常現象，誤報』」。glossing_report.md 會轉成 docx 交給業務單位，可是報告只能看、不能回填；老師發現程式判斷錯了，現在沒有地方記，下次重跑同樣的問題又會跳出來。

## What Changes

- **新增校對表**：`python -m scripts.validate_glossing` 每次都另外產生 Excel（`.xlsx`）校對表，一個語言別一個檔，放在 `kithann/out/校對表/`。可以直接用 Excel 開，也可以上傳 Google 雲端硬碟用 Google 試算表開。glossing 報告的**所有問題**都列進去，一個問題一列。
- **欄位**：ID、檔案、段、問題、提示（程式的判斷與建議）、族語原句、詞素切割、詞素翻譯、華語翻譯、判斷、備註。「判斷」是下拉選單，三個選項：「程式對，docx 要修改」、「docx 正確，程式判斷錯」、「要討論」。
- **標出問題的位置**：語料儲存格裡，程式認為有問題的地方用紅色粗體標出來——「詞素切割有標點」標有問題的詞，「族語原句與詞素切割不符」標兩邊不一樣的字母。
- **問題 ID**：由檔案、段編號、問題種類、那一段的內容算出來的短碼，例如 `ISSUE-3f9a2c1b`。docx 那一段改過以後，ID 會跟著變，舊的判斷自動失效、重新檢查。報告的每一筆問題都附上 ID，對得到校對表。
- **讀回老師填的表**：老師填好的校對表放進 `kithann/校對/`，程式重跑時讀進來：
  - 「docx 正確，程式判斷錯」：這筆不再算問題，**不列入總覽與問題章**，移到報告最後一章「老師確認過、不是錯誤」。如果一段的錯誤都被確認是程式判斷錯，這一段就照常匯出 YAML。
  - 「要討論」：照常列為問題，另外收進報告的「老師標要討論的項目」一章，給下次開會用。
  - 「程式對，docx 要修改」：照常列為問題。docx 改好以後，問題自然消失。
- **重跑時保留老師的紀錄**：新產生的校對表會帶入舊表同一個 ID 的判斷與備註；舊表有、這次已經沒有的列（問題修好了，或 docx 改過），移到「已不存在的紀錄」分頁，備註不會不見。
- **報告寫明校對流程**：glossing 報告新增一節，給業務單位看校對表在哪裡、怎麼填、怎麼交回。

## Capabilities

### New Capabilities

- `proofreading`：校對表的產生、問題 ID、老師判斷的讀回與合併，以及判斷對驗證結果的影響。

### Modified Capabilities

- `corpus-export`：報告的每筆問題附 ID，新增「校對流程」說明、「老師確認過、不是錯誤」「老師標要討論的項目」兩章；YAML 的合規段不計老師確認過的問題。

## Impact

- 程式：新增 `scripts/smkul/xlsx.py`（用 stdlib 的 `zipfile`、`xml.etree` 讀寫 xlsx，不加依賴）、`scripts/smkul/proofreading.py`（ID、合併、套用判斷）；修改 `scripts/smkul/entry.py`（`Issue` 有 ID）、`scripts/smkul/report.py`、`scripts/validate_glossing.py`。
- 測試：新增 `tests/smkul/test_xlsx.py`、`tests/smkul/test_proofreading.py`；修改 `tests/test_validate_glossing.py`、`tests/smkul/test_report.py`。
- 輸出：新增 `kithann/out/校對表/*.xlsx`；`kithann/out/glossing_report.md` 多三個部分（附 ID、兩章、校對流程）。
- 依賴：無新增。
- 前提：在 `segment-punctuation` 之後做，用它的四級嚴重度。
- 不動：語料檔案、docx／txt 一致性報告（`check_docx_txt.py`）、feature 檔。
