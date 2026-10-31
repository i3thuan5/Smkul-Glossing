# Tasks: report-trim

每支程式都**先改測試，跑一次確認紅的原因對；再改程式，跑同一個測試確認轉綠**。刪掉的測試要寫出是哪一條規格不要了。Python 一律 `for` 放前面，不用 list comprehension；註解、docstring、測試名用華語。

## 0. 開工前確認現況

- [x] 0.1 跑 `tox -e test`、`tox -e behave`，數字記在第 8 節當基準；另外記下目前報告總覽的四級筆數、YAML 段數、校對表列數

## 1. feature 與 step（design 決策 7）

- [x] 1.1 `features/分析報告.feature`（規劃時已寫好）：再對一次 design 決策 1～5，`npx gherkin-lint` 0 錯
- [x] 1.2 `scripts/smkul/report.py` 的 `write()`、`scripts/validate_glossing.py` 的 `run()` 加輸出資料夾參數（預設 `kithann/out`），讓 step 能寫到暫存資料夾；`tox -e test` 仍全綠
- [x] 1.3 新增 `features/steps/分析報告.py`，照 design 決策 7 的表寫四個 Scenario 的檢查；`python -m behave --dry-run` 沒有 undefined step；跑 `python -m behave features/分析報告.feature`，把紅的 scenario 記在第 8 節，確認紅的原因都是「程式還沒改」（嚴重度、排序、章節、校對表），不是 step 寫錯

## 2. 嚴重度（design 決策 1、2）

- [x] 2.1 先改測試：`tests/smkul/test_entry.py` 新增空段、孤兒時間碼是「現象」；跑 `python -m unittest tests.smkul.test_entry` 確認紅在嚴重度還是「錯誤」
- [x] 2.2 再改程式：`scripts/smkul/entry.py` 的 `SEVERITY` 把 `EMPTY_ENTRY`、`ORPHAN_TIMECODE` 改成 `Severity.NOTICE`；1.1 的測試轉綠；`tox -e test` 其他測試若因此變紅，逐一確認是預期的（例如原本斷言「錯誤」），改測試並寫明依據

## 2b. 三個問題改名（design 決策 8）

- [x] 2.3 `features/詞素切割與詞素翻譯對應.feature`（規劃時已改好）：`npx gherkin-lint` 0 錯；`python -m behave features/詞素切割與詞素翻譯對應.feature` 紅的三條，原因都是程式的名稱還沒改
- [x] 2.4 先改測試：`tests/smkul/test_entry.py` 的分類名對照、`tests/test_validate_glossing.py` 用到舊名稱的斷言改成新名稱；確認紅在 `IssueKind` 的值還是舊的
- [x] 2.5 再改程式：`scripts/smkul/entry.py` 三個 `IssueKind` 的值與 `KIND_WHY` 說明改成新名稱（常數名不改）；`grep -rn "詞素翻譯的詞比\|符號的種類不一樣" scripts tests features` 沒有結果；2.3、2.4 轉綠

## 3. 校對表只列錯誤兩級（design 決策 1）

- [x] 3.1 先改測試：`tests/smkul/test_proofreading.py` 的 `TestWriteSheets` 改成：錯誤、錯誤（照常匯出）有列；警告、現象（純華語句、空段、孤兒時間碼、結束時間早於開始）不列；原本「四級嚴重度都有」那條改掉（proofreading spec「產生校對表」已改）；跑測試確認紅的原因對
- [x] 3.2 再改程式：`scripts/smkul/proofreading.py` 新增 `PROOFREAD_SEVERITIES`，`write_sheets()` 只收這兩級；2.1 的測試轉綠

## 4. 總覽與第 7 章的排序、編號（design 決策 3、4、6）

- [x] 4.1 先改測試：`tests/smkul/test_report.py` 新增排序函式的測試（照 `SEVERITY` 的順序、「族語原句與詞素切割不符」展開成 `MISMATCH_WHY` 的 6 個小類、沒有發生的不列、不看筆數）、`kind_table()` 是「編號、問題、嚴重度、筆數」四欄且編號從 1 起、表格上方有筆數定義與「編號對應第 7 章」的說明；`tests/test_validate_glossing.py` 新增總覽寫「已匯出翻譯訓練YAML」、有嚴重度對應表、`kinds_section()` 的小節順序與 `kind_table()` 一樣；跑測試確認紅的原因對
- [x] 4.2 再改程式：`scripts/smkul/entry.py` 的 `IssueKind`、`SEVERITY` 照 feature 的順序排；`scripts/smkul/report.py` 新增排序函式、改 `kind_table()`；`scripts/validate_glossing.py` 的 `overview()` 加對應表、改稱翻譯訓練YAML，`kinds_section()` 改用同一個排序、拿掉「不符的小類集中放最後」；3.1 的測試轉綠

## 5. 刪掉報告的章節（design 決策 5）

- [x] 5.1 先改測試：刪掉只測已刪章節的測試，逐條註明依據（corpus-export「glossing 報告的章節」）：`test_report.py` 的問題明細、老師兩章測試，`test_validate_glossing.py` 的 `todo_section`、`proof_chapters`、老師兩章相關測試；新增：校對流程一節在沒有讀回提醒時不寫提醒、有提醒時列在最後；`run()` 產生的章節依序是 8 章、沒有被刪的章名、沒有「標記清單」；`format_section()` 沒有目錄↔sheet 那一節；跑測試確認紅的原因對
- [x] 5.2 再改程式：`validate_glossing.py` 刪 `todo_section()`、`proof_chapters()`、問題明細的呼叫、開頭的標記清單那行、`--ods` 參數與讀 ODS；`proofreading_section()` 接收讀回提醒並列在最後；`Proof` 只留 rows；`report.py` 刪 `teacher_discuss_section()`、`confirmed_section()`、沒有呼叫者的 `detail_section()`，`format_section()` 拿掉 sheet 對應；「翻譯訓練YAML 輸出」章改標題、來源說明改引會議決議（design 決策 5、6）；4.1 的測試轉綠

## 6. 刪掉 docx／txt 一致性檢查（design 決策 5）

- [x] 6.1 `split_kind()` 搬到 `scripts/smkul/languages.py`：先在 `tests/smkul/test_languages.py` 加它的測試（`阿美族/秀姑巒/a.docx` → `阿美`、`秀姑巒`；`太魯閣族/a.docx` → `太魯閣`、`太魯閣`），確認紅；搬過去後 `validate_glossing.py`、`proofreading.py` 改 import，測試轉綠
- [x] 6.2 刪 `scripts/check_docx_txt.py`、`tests/test_check_docx_txt.py`、`scripts/smkul/pairing.py`、`tests/smkul/test_pairing.py`（依據：docx-txt-consistency 全部 REMOVED）
- [x] 6.3 刪 `docx2text.docx_comments()` 與它的常數、`tests/smkul/test_docx2text.py` 裡審閱註解的測試；保留「docx 內文不含註解」的測試
- [x] 6.4 刪 `IssueKind` 的缺檔、檔名不一致、段數不同、內容差異，連同 `SEVERITY`、`KIND_WHY`；`report.py` 只給 docx 報告用、沒有呼叫者的程式一起刪
- [x] 6.5 `README.md` 拿掉 `check_docx_txt` 的使用說明與 `--ods` 參數；`grep -rn "check_docx_txt\|pairing\|docx_txt_report\|docx_comments" scripts tests features README.md` 沒有結果（剩下的是分析報告 step 檢查這些檔案不存在、以及測試 docstring 說明刪除原因）

## 7. 整體驗證與輸出

- [x] 7.1 `tox -e test`、`tox -e behave`（含 `features/分析報告.feature` 全綠）、`tox -e flake8`、`npx gherkin-lint` 全綠
- [x] 7.2 跑 `python -m scripts.validate_glossing`，確認：總覽四級是 3224／103／6／317 筆、有嚴重度對應表、問題表四欄且順序跟 feature 的表一樣（第 1 列是「1｜行黏在一起｜錯誤｜195」）；第 7 章第 N 節與表上編號 N 同名（逐一比對）；章節依序是 8 章；沒有被刪的章與「標記清單」；反引號外是全形逗號
- [x] 7.3 YAML 段數跟 0.1 的基準一樣；`kithann/out/校對表/` 的列數總和是 3327（3224＋103），沒有純華語句、空段、孤兒時間碼、時間碼警告；`kithann/out/docx_txt_report.md` 不存在（舊檔在規劃時已刪，確認沒有被重新產生）

## 8. 基準紀錄

- 7.1 結果：`tox -e test` 201 tests OK；`tox -e behave` 8 features、79 scenarios、215 steps 全過；`tox -e flake8` 0；`npx gherkin-lint` 0。
- 7.2 結果：總覽 3224／103／6／317；問題表 23 列與第 7 章 23 節一一同名；8 章；沒有刪掉的章與「標記清單」。反引號外的半形逗號只剩「有標點「,」」引用語料本身的 2 處（segment-punctuation 定的提示格式，不在這次範圍）。
- 7.3 結果：YAML 4291 段（與基準相同）；校對表 11 個檔、3327 列，沒有純華語句、空段、孤兒時間碼、時間碼警告；沒有 `docx_txt_report.md`。
- 1.3 紅的 scenario（step 寫好、程式還沒改）：嚴重度決定三種產出（`proofreading.PROOFREAD_SEVERITIES` 不存在）、每一種問題的嚴重度（`SEVERITY` 的嚴重度與順序跟 feature 不同）、報告的章節（還是 12 章、第 3 章叫「YAML 輸出」）。
- 0.1 基準（2026-10-31）：`tox -e test` 209 tests，1 個失敗（`test_對應的五類與_feature_的_scenario_一字不差`，規劃時 feature 已改名，程式還沒改）；`tox -e behave` 73 scenarios 過、3 失敗（對應 feature 改名的三條）、3 錯誤（分析報告.feature 的 step 還沒寫）。報告總覽：錯誤 3269、錯誤（照常匯出）103、警告 6、現象 272；YAML 4291 段；校對表 3650 列。

## Workflow follow-up

- 封存前跑 `openspec validate report-trim --strict`
- `/opsx:archive report-trim`：spec 同步時刪除 `openspec/specs/docx-txt-consistency/`；`openspec/specs/corpus-export/spec.md` 的 Purpose 直接改寫，拿掉「請對方處理」專章，改成「翻譯訓練YAML 與 glossing 報告」
