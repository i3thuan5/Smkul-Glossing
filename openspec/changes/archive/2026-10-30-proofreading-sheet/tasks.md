# Tasks: proofreading-sheet

前提：`segment-punctuation` 已經封存。每支程式都**先寫測試，跑一次確認紅的原因對；再寫程式，跑同一個測試確認轉綠**。Python 一律 `for` 放前面，不用 list comprehension；註解、docstring、測試名用華語。不加任何依賴。

## 0. 開工前確認現況

- [x] 0.1 確認 `openspec list` 沒有 `segment-punctuation`（已封存），`Severity` 有四級；跑 `tox -e test`、`tox -e behave`，數字記在第 6 節當基準

## 1. xlsx 讀寫（stdlib）

- [x] 1.1 先寫測試 `tests/smkul/test_xlsx.py`：寫一個兩分頁的檔再讀回來，字串（含中文、`<>`、`&`、開頭是 `=` 的字串、`ISSUE-12e45678`）原樣保留；儲存格內部分文字紅色粗體（rich text）寫出去、讀回來純文字不變；第一列凍結；指定欄有下拉選單、選項是那三個；讀得懂 sharedStrings（測試裡用手寫的最小 xlsx 模擬 Excel 存檔）；空儲存格讀成空字串；跑 `python -m unittest tests.smkul.test_xlsx` 確認紅在模組不存在
- [x] 1.2 寫 `scripts/smkul/xlsx.py`（design 決策 1）：`write(path, sheets)`、`read(path)`；用 `zipfile`、`xml.etree.ElementTree`；`python -m unittest tests.smkul.test_xlsx` 全綠
- [x] 1.3 用 1.2 產生一個樣本檔放到 scratchpad，檢查 zip 內的 XML 結構符合 OOXML（`[Content_Types].xml`、`xl/workbook.xml`、`xl/worksheets/sheet1.xml` 的 `dataValidations`）；環境裡有 LibreOffice 的話用 headless 轉成 csv 確認讀得開。Excel 與 Google 試算表的實機確認列為使用者驗證項目（Workflow follow-up），結果回報後再決定要不要照 design 的 Risks 改報告說明

## 2. 問題 ID

- [x] 2.1 先寫測試 `tests/smkul/test_proofreading.py`：同樣輸入同樣 ID、格式是 `ISSUE-` ＋ sha256 前 8 碼小寫十六進位；段內容改一個字 ID 就變；同一段不同問題種類 ID 不同；沒有段編號的問題也有 ID；重複 ID 會報錯；跑測試確認紅的原因對
- [x] 2.2 `scripts/smkul/entry.py` 的 `Issue` 加 `id` 欄位；新增 `scripts/smkul/proofreading.py` 的 ID 函式（design 決策 2）；2.1 的測試全綠，`python -m unittest tests.smkul.test_entry` 仍全綠

## 3. 讀回判斷與套用

- [x] 3.1 先寫測試：讀 `kithann/校對/` 不存在、空資料夾、一個檔、兩個檔同 ID 判斷不同（取修改時間較新、記一筆矛盾）、判斷欄寫錯字（當沒判斷、記檔名列號）；套用後「docx 正確，程式判斷錯」的問題從 `entry.issues` 移到確認清單、只剩這種問題的段 `is_clean()` 為真；「要討論」「程式對，docx 要修改」留在 `entry.issues`；ID 對不上的判斷不套用；測試用暫存資料夾，不碰真的 `kithann/`
- [x] 3.2 在 `scripts/smkul/proofreading.py` 寫讀回、合併、套用（design 決策 3）；3.1 的測試全綠

## 4. 產生校對表

- [x] 4.1 先寫測試：一個語言別一個檔、檔名 `校對表_<族別>_<語言別>.xlsx`；欄位順序照 spec（四行語料都有）；標紅位置：太魯閣 1 第 418 段的 `aji.`、`uri.`，秀姑巒第 62 段族語原句的 `l` 與詞素切割的 `r`，其他種類不標；照檔案、段編號排序（段編號照數字排，`9` 在 `10` 前面）；四級嚴重度的問題都有；舊判斷與備註帶入；對不到的舊判斷進「已不存在的紀錄」分頁、空白的不留；被確認是程式判斷錯的問題仍在校對表（判斷欄保留「docx 正確，程式判斷錯」），老師才看得到自己填過的
- [x] 4.2 `scripts/smkul/parser.py` 加上取得原字串位置的 `bare_form` 版本（原本的 `bare_form()` 行為不變，`tests.smkul.test_parser` 仍全綠）；寫產生校對表的函式（design 決策 4、5），輸出到 `kithann/out/校對表/`，每次先清掉舊的 xlsx 再寫；4.1 的測試全綠

## 5. 報告與串接

- [x] 5.1 先改測試：`tests/smkul/test_report.py` 的明細、例子每筆附 ID；`tests/test_validate_glossing.py` 有「校對流程」一節、「老師標要討論的項目」「老師確認過、不是錯誤」兩章（沒資料時寫「（無）」、後者是最後一章、開頭列讀取問題）、確認過的問題不算在總覽筆數；跑測試確認紅的原因對
- [x] 5.2 改 `scripts/smkul/report.py`（`render_issue()`、明細附 ID，新增兩章的產生函式）與 `scripts/validate_glossing.py`（`collect()` 算 ID、讀判斷、套用；產生校對表；報告加三個部分）；5.1 的測試全綠；報告內文用全形逗號、章節編號由 `number_headings()` 自動加

## 6. 整體驗證與紀錄

- [x] 6.1 `tox -e test`、`tox -e behave`、`tox -e flake8` 全綠（跟基準比，只多不少）
- [x] 6.2 跑 `python -m scripts.validate_glossing`（`kithann/校對/` 不存在）：`kithann/out/校對表/` 有 11 個 xlsx，筆數總和等於報告總覽四類筆數的總和；YAML 跟執行前一樣；報告兩章寫「（無）」
- [x] 6.3 模擬校對：複製一個產生的 xlsx 到 `kithann/校對/`，挑一筆「族語原句與詞素切割不符」標「docx 正確，程式判斷錯」、一筆標「要討論」並寫備註，重跑：前者的段出現在 YAML、總覽錯誤少一筆、最後一章列出它；後者出現在「老師標要討論的項目」；新校對表帶入兩筆判斷。做完把 `kithann/校對/` 的測試檔刪掉
- [x] 6.4 基準與 1.3 的結果：
  - 6.1 結果：`tox -e test` 209 tests OK；`tox -e behave` 76 scenarios 全過；`tox -e flake8` 0；`npx gherkin-lint` 0。
  - 6.2 結果：`kithann/out/校對表/` 11 個 xlsx 共 3650 列＝3269＋103＋6＋272；YAML 跟執行前一樣；報告第 11、12 章寫「（無）」，第 12 章是最後一章。
  - 6.3 結果：秀姑巒第 2 段（詞數不同）標「docx 正確，程式判斷錯」後進 YAML（4291 → 4292 段）、錯誤 3269 → 3268、列在第 12 章；第 14 段標「要討論」後列在第 11 章；新校對表帶入兩筆判斷。測試檔已刪、輸出已重新產生。
  - 1.3 結果：樣本檔的 7 個 part 都是 well-formed XML，worksheet 元素順序（sheetViews → cols → sheetData → dataValidations）照 OOXML schema；環境沒有 LibreOffice，headless 轉檔沒做，Excel／Google 試算表留給使用者驗證。
  - 0.1 基準（2026-10-30）：`segment-punctuation` 已封存、`Severity` 四級；`tox -e test` 167 tests OK；`tox -e behave` 76 scenarios 全過。

## Workflow follow-up

- 使用者驗證：把 `kithann/out/校對表/` 任一個 xlsx 用 Excel 打開、再上傳 Google 雲端硬碟用 Google 試算表打開，確認判斷欄的下拉選單、語料格裡的紅色粗體兩邊都看得到
- 封存前跑 `openspec validate proofreading-sheet --strict`
- `/opsx:archive proofreading-sheet`，spec 同步：新增 `openspec/specs/proofreading/spec.md`，`openspec/specs/corpus-export/spec.md` 加「報告附校對資訊」
