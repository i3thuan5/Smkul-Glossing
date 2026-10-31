# Tasks: segment-punctuation

順序依照 CLAUDE.md「feature 是規格，程式後壁才綴」：先寫 feature（behave 轉紅是預期），再改 step、測試、程式。每支程式都**先改測試，跑一次確認紅的原因對；再改程式，跑同一個測試確認轉綠**。Python 一律 `for` 放前面，不用 list comprehension。

## 0. 開工前確認現況

- [x] 0.1 跑 `tox -e behave`、`tox -e test`，把通過與失敗的數字記在本檔第 7 節當基準；有失敗的話先查清楚是不是跟這次無關

## 1. feature 規格（behave 會轉紅，預期）

- [x] 1.1 `features/族語原句詞素切割比對.feature`：描述的「比對時忽略兩項」改成「族語原句的標點、英文大小寫」，並註明詞素切割行本身不能有標點、見 `features/詞素切割標點.feature`；加一句「阿美語的 `^` 是喉塞音字母，跟單引號一樣不忽略；書寫系統的符號（`:`、`_` 等）跟切割符號一樣去掉」；第 3 行更新日期改成當天；`npx gherkin-lint` 0 錯
- [x] 1.2 同一份：「只差標點，算通過，另外記一筆待確認」改名為「只差標點，算通過，不記任何問題」，拿掉 `@規格要討論`，移到第一個 `@規格要討論` scenario 前面；註解改成會議決議（案由五），刪掉「請對方確認慣例」；`And 另外記一筆標點不同` 改成 `And 不記任何問題`；`npx gherkin-lint` 0 錯
- [x] 1.3 同一份：在「不符——只差單引號」後面新增「不符——阿美語的 ^ 是字母」，例子用海岸 3 第 126 段（`iya han tosa ko patang` → `iya=han tosa ko pa^tang`），Then 分類 `只差一個字母`、差異 `詞素切割多了「^」`；例子不夠三組就照實寫「全語料只有 2 段」；`npx gherkin-lint` 0 錯
- [x] 1.4 新增 `features/詞素切割標點.feature`，Feature 名「詞素切割行不能有標點」，第 3 行更新日期，描述寫允許的字元與例外（spec「詞素切割行不能有標點」）、提示格式（spec「詞素切割標點的錯誤提示」）、一段一筆、照常匯出
- [x] 1.5 同一份的 scenario，順序與例子照 CLAUDE.md 語言優先序（阿美→太魯閣→魯凱→排灣→布農、泰雅），每條附 3 組例（族語原句、詞素切割、詞素翻譯、華語翻譯、檔案、第幾段），When/Then 用例 1：沒有標點（通過）、詞頭詞尾的標點（太魯閣 `iq kiya.`）、一段好幾個詞只記一筆（太魯閣 1 第 418 段 `aji. uri. o brah`）、只有符號的詞（排灣 `＠`）、括號（魯凱 `(lu alra ngu-vaeva)`）、阿美語的 `^` 與 `:` 不算標點（海岸）、泰雅語的 `_` 不算標點（`k_yaqih`）、黏在詞前面的說話者標記當一般族語詞（泰雅 `Yu:m-uwah`，冒號算標點）；Then 寫完整提示字串（design 決策 2 的表）
- [x] 1.6 同一份檔尾三條 `@規格要討論`：`+` 先不算錯誤（泰雅）、詞中間的 `.` 先不算錯誤（太魯閣、魯凱、排灣）、獨立的說話者標記先不算錯誤（排灣、泰雅、布農；附一段說話者標記以外還有標點的例子：南排灣 4 第 114 段），註解寫出處、要跟承辦討論保留還是提示、程式現在怎麼判；Then 寫「不記詞素切割有標點，列入待討論」
- [x] 1.7 例子一律從 docx 解析結果抄（用 `parse_corpus_file`），反引號內的語料照原樣、不改半形全形；`npx gherkin-lint` 0 錯；`python -m behave --dry-run` 列出的 undefined step 只有新 step

## 2. step 跟上 feature

- [x] 2.1 `features/steps/族語原句詞素切割比對.py`：刪 `另外記一筆標點不同` step，新增 `不記任何問題`（斷言 `SourceCheck` 沒有標點相關欄位、`passed` 為真）；`python -m behave features/族語原句詞素切割比對.feature`，紅的只能是「^ 是字母」那條（程式還沒改）
- [x] 2.2 新增 `features/steps/詞素切割標點.py`：When「族別是 "X"，詞素切割是 "..."」呼叫標點檢查函式；Then「沒有標點問題」「提示是 "..."」「列入待討論 "+"／"詞中間的 ."／"說話者標記"」；`python -m behave --dry-run` 沒有 undefined step，執行時紅的原因都是「函式還沒有」

## 3. 嚴重度與問題種類

- [x] 3.1 先改測試：`tests/smkul/test_entry.py` 新增「錯誤（照常匯出）的段照常匯出」（`is_clean()` 為真）、「NOTICE 仍不匯出」；跑 `python -m unittest tests.smkul.test_entry` 確認紅在 `Severity.EXPORTED_ERROR` 不存在
- [x] 3.2 再改程式：`scripts/smkul/entry.py` 新增 `Severity.EXPORTED_ERROR = "錯誤（照常匯出）"`、`Severity.WARNING` 的值改成 `"警告（照常匯出）"`、`IssueKind.SEGMENT_PUNCTUATION = "詞素切割有標點"`（severity 是 `EXPORTED_ERROR`，`KIND_WHY` 寫會議決議案由五）；刪 `IssueKind.PUNCTUATION_DIFF` 與它的 `SEVERITY`、`KIND_WHY`；`is_clean()` 改成只擋 `ERROR` 與 `NOTICE`（design 決策 3）；`python -m unittest tests.smkul.test_entry` 全綠

## 4. parser：比對與標點檢查

- [x] 4.1 先改測試：`tests/smkul/test_parser.py` 的 `test_bare_form_留單引號_去掉標點大小寫` 加 `^` 要保留；刪 `test_標點不同是_warning_不擋匯出`、`test_標點相同就不記`（spec REMOVED「族語原句嚴格檢查詞素切割」的標點記錄），改成「族語原句有標點、詞素切割沒有，不記任何問題」；新增標點檢查的測試，每種現象（design 決策 2 的三列）一條、書寫系統符號依族別放行（阿美 `^` `:`、泰雅 `_`，以及非阿美的 `^`、非泰雅的 `_` 算標點）、`+`、詞中間的 `.`、獨立說話者標記、黏著說話者標記各一條、一段多詞只記一筆一條、`assemble_entry()` 記 `SEGMENT_PUNCTUATION` 且 `is_clean()` 為真一條；跑 `python -m unittest tests.smkul.test_parser` 確認紅的原因對
- [x] 4.2 再改程式：`scripts/smkul/parser.py` 的 `bare_form()` 保留 `^`；刪 `PUNCTUATION`、`_punctuation_of()`、`SourceCheck.punctuation_differs`；新增標點檢查函式（design 決策 1、2、4），`assemble_entry()` 用它記一筆並把待討論標記存到 `Entry`；`python -m unittest tests.smkul.test_parser` 全綠
- [x] 4.3 `python -m behave features/族語原句詞素切割比對.feature features/詞素切割標點.feature` 全綠

## 5. 報告

- [x] 5.1 先改測試：`tests/smkul/test_report.py` 拿掉 `PUNCTUATION_DIFF`，新增 `severity_split()` 回傳四組、`render_issue()` 對 `SEGMENT_PUNCTUATION` 不切冒號（detail 含 `Yu:m-uwah` 時整串保留）、待討論挑法（round-robin、最多 20 段、重跑一樣）；`tests/test_validate_glossing.py` 新增總覽有「錯誤（照常匯出）」「警告（照常匯出）」各一行、沒有「warning」與「標點不同」、有待討論章；跑 `python -m unittest tests.smkul.test_report tests.test_validate_glossing` 確認紅的原因對
- [x] 5.2 再改程式：`scripts/smkul/report.py` 的 `severity_split()`、`render_issue()`（design 決策 5）、新增待討論章的產生函式（design 決策 6）；`scripts/validate_glossing.py` 總覽分四類、拿掉比對政策裡「標點」那一項與 `counter.get("標點不同")` 那段、`collect()` 收集待討論標記、加上待討論章；exit code 仍只看 `ERROR`；上面的測試全綠
- [x] 5.3 `grep -rn "標點不同\|PUNCTUATION_DIFF\|punctuation_differs" scripts features tests` 沒有結果（剩下的 5 處都是斷言「沒有標點不同」的測試與 step）

## 6. 整體驗證與輸出

- [x] 6.1 `tox -e test`、`tox -e behave` 全綠（跟第 7 節基準比，只多不少）；`tox -e flake8`、`npx gherkin-lint` 0 錯
- [x] 6.2 跑 `python -m scripts.validate_glossing`，確認 `kithann/out/glossing_report.md`：總覽有「錯誤（照常匯出）」「警告（照常匯出）」、沒有「warning」與「標點不同」；「詞素切割有標點」是 103 段（筆數）；待討論章 `+` 寫 199 段、`.` 寫 427 段、說話者標記寫 46 段 63 處，各列 20 段而且來自不只一個檔案；中排灣 1 第 12 段的提示跟 spec 一樣；章節有編號、反引號外是全形逗號
- [x] 6.3 `kithann/out/corpus.yaml` 跟改之前比，段數只少了因為 `^` 保留而變成不符的段（預期只有海岸 3 第 126 段）；只有標點問題的太魯閣 1 第 9 段照常匯出，`詞素切割` 照原樣是 `iq kiya.`（中排灣 1 第 12 段另有「族語原句與詞素切割不符」，本來就不匯出）

## 7. 基準紀錄

- 6.1 結果：`tox -e test` 167 tests OK；`tox -e behave` 7 features、76 scenarios、207 steps 全過；`tox -e flake8` 0；`npx gherkin-lint` 0。
- 6.2／6.3 結果：報告總覽錯誤（不匯出）3269、錯誤（照常匯出）103、警告（照常匯出）6、現象 272；YAML 4292 → 4291 段，只少了海岸 3 第 126 段。
- 0.1 基準（2026-10-30）：`tox -e behave` 6 features、63 scenarios、176 steps 全過（1 個 feature skipped，是 `tshi.feature` 範例檔）；`tox -e test` 131 tests OK。

## Workflow follow-up

- 封存前跑 `openspec validate segment-punctuation --strict`
- `/opsx:archive segment-punctuation`，spec 照 delta 同步到 `openspec/specs/glossing-validation/spec.md`、`openspec/specs/corpus-export/spec.md`
