# Tasks：spec-2026-11-severity-and-checks

feature 已經定案（`features/*.feature` 2026.11.23 版），這次只改 `features/steps/`、`tests/`、`scripts/`，**不改 feature**；改到一半發現 feature 寫錯，停下來問使用者。每支程式都**先改測試，跑一次確認紅的原因對；再改程式，跑同一個測試確認轉綠**。Python 一律 `for` 放前面，不用 list comprehension；註解、docstring、測試名用華語。改檔用 Edit／Write，不用 bash 改。

## 0. 開工前確認現況

- [x] 0.1 跑 `tox -e behave`、`tox -e test`、`tox -e flake8`，把通過與失敗的數字記在本檔第 9 節當基準（behave 預期：91 條裡 10 條失敗、8 條 error）

## 1. 嚴重度架構（design 決策 1、2）

- [x] 1.1 `entry.Severity` 新增 `UNSURE = "不確定，待檢查"`；`Entry.is_clean()` 把它當不匯出；exit code 照舊只看 `ERROR`；`proofreading.PROOFREAD_SEVERITIES` 加上它
- [x] 1.2 「族語原句與詞素切割不符」拆成 9 個 `IssueKind`（值是 `族語原句與詞素切割不符-<小類>`）；`MISMATCH_WHY` 改成照 `IssueKind` 查；`detail` 不再放「分類:」前綴，`report.render_issue` 跟著改
- [x] 1.3 新增 `IssueKind`：`詞素切割第一個詞有冒號，可能是語者標記沒空白`、`非泰雅語的詞素切割不應該用 + 符號`、`詞根放在中綴前面`、`詞綴黏在中綴前面，切割符號在中綴後面`
- [x] 1.4 `SEVERITY` 改成跟 `features/分析報告.feature` 嚴重度表同順序的有序 dict；`report.py`、`validate_glossing.py` 拿掉展開不符小類的特例，問題表與第 7 章直接照 `SEVERITY` 排
- [x] 1.5 `IssueKind` 加「ID 用的大類」；`proofreading.id_source` 改用大類，內文行的 U+02BC 折回 U+0027 再算；`tests/smkul/test_proofreading.py` 補「拆分後 ID 不變」「引號正規化後 ID 不變」
- [x] 1.6 `features/steps/分析報告.py` 跟上：`_program_labels` 直接照 `SEVERITY`；`各嚴重度的產出是：` 認得新的一級；`tox -e behave` 跑 `features/分析報告.feature` 全青

## 2. 共用 step（design 決策 6）

- [x] 2.1 新增 `features/steps/共用.py`：`嚴重度是 "{severity}"` 取 `context.issues` 最後一筆比
- [x] 2.2 比對、標點、對應三個 feature 的 When 都把問題清單放進 `context.issues`
- [x] 2.3 標點的 `族別是 "{ethnic}"，詞素切割是 "{segmentation}"` 改用 regex matcher（族別不含 `"`）；新增比對的 `族別是 "{ethnic}"，族語原句是 "{source}"，對應詞素切割是 "{segmentation}"`；`python -m behave --dry-run` 沒有 ambiguous、沒有 undefined 的比對 step

## 3. 字元正規化（feature：字元正規化）

- [x] 3.1 測試：引號 U+0027、U+2018、U+2019 轉成 U+02BC；四條「引用符號不轉」各一組；三條 `@規格要討論` 照規則轉（規則本身由 feature 測，單元測試補計數）
- [x] 3.2 `parser` 的正規化改成 U+02BC，加「當引用符號用的引號不轉」的判斷函式；計數改成「轉了幾筆」
- [x] 3.3 所有認喉塞音的地方認 U+02BC：`bare_form`、`SEGMENT_SYMBOLS`、`markers.UNCERTAIN`；`tox -e behave` 跑 `features/構詞判定.feature` 照舊全青。ODS 清單沒有正規化：構詞判定已經暫停，正式流程用 `MarkerList.empty()`，沒有讀 ODS
- [x] 3.4 `tox -e behave` 跑 `features/字元正規化.feature` 全青（「全形 ＝」那條的 Then 有 `'I`，使用者決定改成 `ʼI`，feature 已改）

## 4. 族語原句與詞素切割比對（feature：族語原句詞素切割比對；design 決策 4）

- [x] 4.1 `compare_source` 加 `ethnic` 參數；`parser.assemble_entry` 傳族別進去；沒給族別時限定語言的規則都不套用
- [x] 4.2 `_word_counts_fit`：`=`、`.` 都可以併詞，泰雅另外加 `+`；`-` 不行
- [x] 4.3 阿美語保留 `:`；新增小類「只差長音符號」，差異寫 `詞素切割多了「:」`／`詞素切割少了「:」`（只認詞中間的 `:`，句讀的冒號不算）
- [x] 4.4 新增小類「詞素切割有拉長音」，差異寫 `詞素切割的「<詞>」有拉長音「==」`
- [x] 4.5 新增小類「族語和華語不一致」：兩行詞數一樣時逐詞對位，一邊全是拉丁字母、另一邊全是漢字
- [x] 4.6 小類先後：拉長音 → 族語和華語不一致 → 只差長音符號 → 原本的 6 類
- [x] 4.7 泰雅、太魯閣、賽德克的「只差一個字母」「差 2-3 個字母」「長度差很多」算通過
- [x] 4.8 `tests/smkul/test_parser.py` 每一項各補測試；`tox -e behave` 跑 `features/族語原句詞素切割比對.feature` 全青

## 5. 詞素切割標點（feature：詞素切割標點）

- [x] 5.1 全形 `＠` 合法；詞中間的 `.`、獨立的說話者標記、泰雅語的 `+` 合法，不再記進 `entry.discuss`
- [x] 5.2 泰雅語第一個詞有 `:`（不是說話者標記）記「詞素切割第一個詞有冒號，可能是語者標記沒空白」，提示建議刪掉冒號
- [x] 5.3 泰雅語以外的 `+` 記「非泰雅語的詞素切割不應該用 + 符號」，提示「程式判斷要改成 `.`，因為只有泰雅語可以用 + 標示詞組」
- [x] 5.4 同一段三種各記一筆，同一種只記一筆
- [x] 5.5 新增 step `不用列入待討論`（斷言沒有待討論的收集）；刪掉沒人用的 `列入待討論 "{label}"`
- [x] 5.6 `tox -e behave` 跑 `features/詞素切割標點.feature` 全青

## 6. 詞素切割與詞素翻譯對應（feature：詞素切割與詞素翻譯對應；design 決策 5）

- [x] 6.1 `tests/smkul/test_rules.py` 補 design 決策 5 列的 12 組例子
- [x] 6.2 `check_correspondence` 逐個 token 先判中綴：詞素切割中綴後面沒有詞根 → 通過；詞素翻譯中綴後面沒有詞根 → 「詞根放在中綴前面」或「詞綴黏在中綴前面，切割符號在中綴後面」；詞素翻譯中綴前後都有字母、中間沒有符號 → 通過；其他照符號比
- [x] 6.3 `CORRESPONDENCE_KIND` 加兩個新分類；`tox -e behave` 跑 `features/詞素切割與詞素翻譯對應.feature` 全青（含兩條 `@規格要討論` 照現在判通過）

## 7. 排版分析（feature：排版分析；design 決策 7）

- [x] 7.1 新增 step：`第 {order:d} 段的段號是 "{number}"`、`第 {order:d} 段重組後的族語原句是 "{expect}"`、`第 {order:d} 段重組後的華語翻譯是 "{expect}"`
- [x] 7.2 `tests/smkul/test_parser.py` 補測試。對話段、第 114 段、第 110 段 feature 已經有例子；單元測試補 feature 沒有的：行內說話者標記（第 151 段）、換手兩次以上（第 23 段）、華語翻譯少一份、同一組寫兩次（第 169 段）、只有一位說話者、時間碼的問題留在第一段
- [x] 7.3 `parser` 認說話者標記，對話段與兩位發音人一組照說話者切段，段號 `13-1`、`13-2`；切不成同樣份數的整段不切、記「行黏在一起」
- [x] 7.4 段號排序（報告、校對表）能排 `13-1`：`proofreading._number_key` 等補測試
- [x] 7.5 `tox -e behave` 跑 `features/排版分析.feature` 全青

## 8. 報告與收尾

- [x] 8.1 刪掉待討論章：`validate_glossing.discuss_chapter`、`DISCUSS_*`、`report.discuss_section`、`report.DISCUSS_LIMIT`、`entry.discuss` 與相關測試
- [x] 8.2 總覽的嚴重度筆數改成五級；「自動處理」章的引號一項改寫成轉 U+02BC
- [x] 8.3 `tox -e behave`、`tox -e test`、`tox -e flake8`、`npx gherkin-lint` 全過
- [x] 8.4 **先問使用者用哪一版語料**，再跑 `python -m scripts.validate_glossing <語料目錄>`；把報告的問題表筆數、匯出段數、校對表列數跟改版前比，寫在第 9 節，給使用者確認

## 9. 紀錄

### 9.1 開工前的基準（2026-11-23）

本機沒有 tox，用同樣的 deps 建 venv 跑同樣的指令。

- behave：97 條 scenario，68 條通過、18 條失敗、11 條 error（feature 這輪又補了幾條，比 proposal 寫的 91 條多）
- unittest：199 個測試，1 個失敗（`test_entry` 的「自動處理指向的 scenario 都找得到」：字元正規化的引號 scenario 改了名稱）、4 個 skip
- flake8：0

### 9.2 第 1～8.2 節做完以後（2026-11-23）

- behave：97 條 scenario，96 條通過、1 條失敗——`features/字元正規化.feature`「全形 ＝ 換成半形 =」：Then 寫 `使役-'I-讀書.台語`，照新的引號規則 `'I` 會轉成 `ʼI`。feature 自己前後不一致，等使用者決定（3.4、8.3 先不勾）
- unittest：229 個測試全過、4 個 skip（語料的 smoke test，要指定語料目錄才跑）
- flake8：0；`npx gherkin-lint`：0

### 9.3 全部做完（2026-11-23）

- behave：97 條全過；unittest：229 個全過、4 個 skip；flake8：0；`npx gherkin-lint`：0

### 9.4 語料 `kithann/語料標註語料_20261118` 改版前後

改版前用 `git show HEAD:` 匯出的程式跑，兩版的輸出都寫到 scratchpad，沒有動 `kithann/out/`。

| 項目 | 改版前 | 改版後 |
|---|---|---|
| 段數 | 12815 | 12967 |
| 匯出翻譯訓練YAML 的段數 | 6985 | 8378 |
| 錯誤（不匯出，影響 exit code） | 5355 | 2487 |
| 錯誤（照常匯出） | 159 | 139 |
| 警告（照常匯出） | 6 | 6 |
| 不確定，待檢查 | 0 | 1631 |
| 現象 | 521 | 526 |
| 校對表列數 | 5514 | 4257 |

段數多 152 段：285 段是照說話者切開的（阿美〈阿嬤的祕密基地〉151、〈ina〉39、〈水璉部落年齡〉34、南排灣 4_張枝妹 26、泰雅俚語 16……），原本整段判成「行黏在一起」（376 → 261 筆）。

| 問題 | 改版前 | 改版後 |
|---|---|---|
| 族語原句與詞素切割不符-只差一個字母 | 1528（錯誤） | 1043（不確定，待檢查） |
| 族語原句與詞素切割不符-差 2-3 個字母 | 1149（錯誤） | 549（不確定，待檢查） |
| 族語原句與詞素切割不符-長度差很多 | 45 | 17 |
| 族語原句與詞素切割不符-詞數不同 | 807 | 551 |
| 族語原句與詞素切割不符-多處不同 | 587 | 564 |
| 族語原句與詞素切割不符-只差單引號 | 243 | 226 |
| 族語原句與詞素切割不符-族語和華語不一致 | － | 29 |
| 族語原句與詞素切割不符-詞素切割有拉長音 | － | 10 |
| 族語原句與詞素切割不符-只差長音符號 | － | 2 |
| 詞素切割有標點 | 159 | 137 |
| 詞素切割第一個詞有冒號，可能是語者標記沒空白 | － | 39 |
| 非泰雅語的詞素切割不應該用 + 符號 | － | 0 |
| 詞根放在中綴前面 | － | 15 |
| 詞綴黏在中綴前面，切割符號在中綴後面 | － | 2 |
| 詞素切割的詞比詞素翻譯多／少 | 217／105 | 292／160 |
| 詞素切割沒有切，詞素翻譯有切／有切，沒有切 | 97／98 | 130／127 |

對應的幾類變多，是因為比對放寬（泰雅語群、`.`、`+`）與說話者切段之後，更多段走到對應檢查。引號正規化 5462 筆。
