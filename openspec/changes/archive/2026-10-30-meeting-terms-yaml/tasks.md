# Tasks: meeting-terms-yaml

用語對照與不能動的例外見 design.md 決策 1、2。改名一律人工逐處判斷，不用 sed 整批取代；改完看 diff，反引號內的語料不能變。

第 3 到 5 節的順序是：**先改測試，跑一次確認紅的原因對；再改程式，跑同一個測試確認轉綠**，一支程式改完、它的測試過了，才換下一支。刪掉的測試要寫出是哪一條規格不要了。

## 0. 開工前確認現況

- [x] 0.1 跑 `tox -e behave`，結果要跟第 8 節的基準一樣（63 scenarios 全綠）；不一樣的話先查清楚原因，再開始第 1 節
- [x] 0.2 跑 `tox -e test`，失敗的測試要跟第 8 節的基準一樣（9 個，全是 staged 的 YAML 改動造成、第 3 節會處理）；多出來的失敗先查清楚

## 1. feature 改用語與檔名（behave 會轉紅，預期）

- [x] 1.1 `features/原文切分比對.feature` 改名為 `features/族語原句詞素切割比對.feature`（用 `mv`，不用 `git mv`），Feature 名、Scenario 名、Step 內文、註解裡的例子標籤（`族語原文：`→`族語原句：`、`切分：`→`詞素切割：`、`glossing：`→`詞素翻譯：`、`翻譯：`→`華語翻譯：`）、分類名照決策 1 改；第 3 行更新日期；`npx gherkin-lint` 0 錯
- [x] 1.2 `features/切分與glossing對應.feature` 改名為 `features/詞素切割與詞素翻譯對應.feature`，五個分類名的 Scenario 照決策 1 改，其餘同 1.1；`npx gherkin-lint` 0 錯
- [x] 1.3 `features/排版分析.feature`：長句分段 → 長句換行、兩段／三段 → 兩截／三截（`長句換行重組——兩截`）、`缺 gloss 段` → `缺詞素翻譯行`、`缺翻譯行` → `缺華語翻譯行`、`空組` → `空段`、組 → 段，其餘同 1.1；`npx gherkin-lint` 0 錯
- [x] 1.4 `features/字元正規化.feature`、`features/時間碼.feature` 同 1.1 的用語；`npx gherkin-lint` 0 錯
- [x] 1.5 `features/構詞判定.feature` 同 1.1 的用語，Feature 描述開頭加一段「草稿，暫停維護，報告與 YAML 不使用」（決策 4）；拿掉「照樣寫進 YAML 的「構詞」欄」這類跟 YAML 有關的句子；`npx gherkin-lint` 0 錯
- [x] 1.6 `grep -n "組\|切分\|gloss\|原文\|分段" features/*.feature` 剩下的每一筆都在決策 2 的例外裡（反引號內的語料、ODS 原文、檔名）；`git diff features/` 裡反引號內的字沒有變動

## 2. steps 跟上 feature（behave 回綠）

- [x] 2.1 `features/steps/原文切分比對.py` 改名為 `族語原句詞素切割比對.py`、`features/steps/切分與glossing對應.py` 改名為 `詞素切割與詞素翻譯對應.py`；所有 step 檔的 step 文字、註解、docstring 照第 1 節的 feature 改；`python -m behave --dry-run` 沒有 undefined step
- [x] 2.2 step 裡 assert 的分類名會跟著第 5 節的 `IssueKind` 改名，這時先跑 `python -m behave`，把紅的 scenario 記在本檔第 8 節，確認紅的原因都是「程式的分類名還沒改」

## 3. YAML 與語言別代號

- [x] 3.1 先改測試：`tests/smkul/test_entry.py` 的 YAML 測試照 corpus-export「YAML 匯出結構」改，測試名 `test_句_yaml_的_key` → `test_段_yaml_的_key`、`test_檔案_yaml_只收乾淨的組` → `test_檔案_yaml_只收乾淨的段`，斷言改查 `段`、`族語原句`、`詞素切割`、`詞素翻譯`、`華語翻譯`，並斷言沒有 `詞`；刪 `test_詞素_yaml`（YAML 不再有詞素，見 corpus-export REMOVED「單一 YAML 匯出」）；跑 `python -m unittest tests.smkul.test_entry`，確認紅的只剩 `詞素切割` 這個 key（staged 程式還是 `詞素切分`）
- [x] 3.2 再改程式：`scripts/smkul/entry.py` 的 `Entry.to_yaml()` key `詞素切分` → `詞素切割`，刪 `Word.to_yaml()`、`Morpheme.to_yaml()`；`python -m unittest tests.smkul.test_entry` 全綠
- [x] 3.3 先改測試：`tests/smkul/test_yamlout.py` 改查 `語言別`、`語言別代號`、`段` 與四行 key，測試名照新用語（`test_句層的_key` → `test_段層的_key`、`test_只收通過驗證的組` → `test_只收通過驗證的段`）；刪 `test_詞與詞素四層`、`test_附著詞的原詞會併寫`、`test_一個詞一行`（YAML 不再有詞，見 corpus-export REMOVED「單一 YAML 匯出」）；跑 `python -m unittest tests.smkul.test_yamlout`，記下紅的原因（staged 程式已經做了大部分，可能只有 `詞素切割` 會紅）
- [x] 3.4 再改程式：`scripts/smkul/yamlout.py` docstring 改成「檔案 → 段 兩層」；`python -m unittest tests.smkul.test_yamlout` 全綠
- [x] 3.5 先寫測試：新增 `tests/smkul/test_languages.py`，涵蓋 corpus-export「語言別代號」的 5 個 scenario（秀姑巒 → `ami-x-skl`、中排灣 → `pwn-x-pnvn`、太魯閣 → `trv-x-truku`、霧台 → `dru-x-ngdr`、查不到回空字串），另外斷言 `languages.CSV_PATH` 指向 `scripts/smkul/data/` 裡的檔案而且存在（design 決策 6：CSV 要在版控內）；跑 `python -m unittest tests.smkul.test_languages`，確認紅的原因只有 CSV 路徑還在 `kithann/`
- [x] 3.6 再改程式：把 `kithann/規範/族語及語言別名稱 - 語言別名稱.csv` 複製到 `scripts/smkul/data/`；`scripts/smkul/languages.py` 的 `CSV_PATH` 改成以模組所在目錄為準的那份，docstring 裡的台語（「佮」「這款」）改成華語，`_table()` 補 docstring（實作時 staged 版本已經沒有 `_table()`，這項不適用）；`python -m unittest tests.smkul.test_languages tests.smkul.test_entry tests.smkul.test_yamlout` 全綠

## 4. 構詞判定退出流程

- [x] 4.1 先改測試：`tests/smkul/test_rules.py` 的 `test_整組驗證` 改成 `validate()` 只回傳問題清單；刪 `test_大寫的不確定標記放行且統計`（見 glossing-validation REMOVED「大寫「不確定」標記」）；`test_兩個中綴`、`test_原詞是切分提掉符號`、`test_不確定標記的樣式` 測的是 `構詞判定.feature` 還在用的函式，保留；`tests/smkul/test_yamlout.py` 呼叫 `validate()` 的地方跟著改；跑 `python -m unittest tests.smkul.test_rules`，確認紅的原因是 `validate()` 還回傳三個值
- [x] 4.2 再改程式：`scripts/smkul/rules.py` 的 `validate()` 只做詞素切割行與詞素翻譯行的對應檢查，不再呼叫 `build_words`／`collect_undecided`／`collect_uncertain`；`analyse_word`、`classify`、`MarkerList` 保留；`python -m unittest tests.smkul.test_rules tests.smkul.test_yamlout` 全綠、`python -m behave features/構詞判定.feature` 全綠
- [x] 4.3 先改測試：`tests/smkul/test_report.py` 刪 `test_不確定標記統計`、`test_不確定標記無資料`、`test_構詞判斷困難依次數排序`、`test_構詞判斷困難最多列三個實例`、`test_構詞判斷困難無資料`（見 corpus-export「報告內容」：報告不出現構詞資訊）；新增 `tests/test_validate_glossing.py`，斷言 `overview()` 沒有「構詞」、`todo_section()` 沒有「構詞判斷困難的詞素要怎麼處理」與「用語要不要換成語言學的標準說法」；跑 `python -m unittest tests.test_validate_glossing`，確認紅的原因是這三處還在
- [x] 4.4 再改程式：`scripts/smkul/report.py` 刪 `hard_morphology_section`、`uncertain_section`；`scripts/validate_glossing.py` 的 `collect()` 拿掉 `uncertain`、`undecided`，`overview()` 拿掉「構詞無法判斷」那行，`todo_section()` 拿掉那兩節，`run()` 不再組這兩章；`python -m unittest tests.smkul.test_report tests.test_validate_glossing` 全綠

## 5. 程式與報告用語

- [x] 5.1 先改測試：`tests/smkul/test_entry.py` 新增斷言，五個對應分類、`缺詞素翻譯行`、`缺華語翻譯行`、`空段`、`族語原句與詞素切割不符-…` 六類的 `IssueKind` 值照決策 1（要跟第 1 節 feature 的 Scenario 名一字不差），並檢查每個 `NormKind` 指向的 feature 檔存在、Scenario 名在那個檔裡找得到；`tests/smkul/test_parser.py`、`tests/test_corpus_smoke.py` 的測試名與斷言照決策 1 改（`test_缺gloss段` → `test_缺詞素翻譯行`、`test_空組` → `test_空段`、`test_黏行` → `test_行黏在一起`、`test_組數` → `test_段數` 等）；跑這三個測試，確認紅的原因是 `IssueKind`／`NormKind` 還是舊名稱
- [x] 5.2 再改程式：`scripts/smkul/entry.py` 的 `IssueKind` 值、`KIND_WHY` 說明、`MISSING_GLOSS_SEGMENT` → `MISSING_GLOSS_LINE`、`NormKind` 指向的 feature 檔名與 Scenario 名；`scripts/smkul/parser.py` 的訊息、註解、docstring；`python -m unittest tests.smkul.test_entry tests.smkul.test_parser tests.test_corpus_smoke` 全綠，`python -m behave` 全綠（第 8.2 節記下的紅 scenario 全部轉綠）
- [x] 5.3 先改測試：`tests/smkul/test_report.py` 的斷言照決策 1 改（「依語言別統計」、「切割符號表」、`test_自動處理逐項指去_feature` 指向新 feature 檔名、四行結構的名稱）；跑 `python -m unittest tests.smkul.test_report`，確認紅的原因是 `report.py` 還是舊用語
- [x] 5.4 再改程式：`scripts/smkul/report.py` 的章節標題與說明文字照決策 1 改；`python -m unittest tests.smkul.test_report` 全綠
- [x] 5.5 先寫測試：`tests/test_validate_glossing.py` 加斷言，依語言別統計表的欄名是 `語言別`、`段數`，總覽寫「段」不寫「組」；新增 `tests/test_check_docx_txt.py`，斷言 `variant_table()` 的欄名是 `語言別`、`有差異的段數`，`overview()` 用新用語；跑這兩個測試，確認紅的原因是程式還是舊用語
- [x] 5.6 再改程式：`scripts/validate_glossing.py`、`scripts/check_docx_txt.py` 的統計表欄名、說明文字、`yaml_sentences`／`exported_sentences` → `yaml_segments`／`exported_segments`（決策 5）；`python -m unittest tests.test_validate_glossing tests.test_check_docx_txt` 全綠；兩支各跑一次，exit code 與改名前相同
- [x] 5.7 先改測試：`tests/smkul/test_rules.py`、`tests/smkul/test_markers.py`、`tests/smkul/test_docx2text.py` 的測試名與斷言照決策 1 改；`pairing.py` 的訊息原本沒有測試，新增 `tests/smkul/test_pairing.py` 蓋住段數訊息；跑這四個測試，記下紅的原因（`rules.check_entry_correspondence` 的說明與對照標籤、`pairing.compare_entries` 的段數訊息還是舊用語）
- [x] 5.8 再改程式：`scripts/smkul/rules.py`、`markers.py`、`pairing.py` 的訊息、註解、docstring 照決策 1 改（`docx2text.py` 的「段落」不改）；只改註解、docstring 的地方不需要新測試，有改到輸出字串的要有 5.7 的測試蓋到；`python -m unittest tests.smkul.test_rules tests.smkul.test_markers tests.smkul.test_docx2text` 全綠、`flake8` 0 錯

## 6. 文件

- [x] 6.1 `README.md`：YAML 結構改成「檔案 → 段」、拿掉「構詞標記是否在原語會清單內」、用語照決策 1、feature 檔名改成新的；`pymarkdown --strict-config --disable-rules md013,md029 scan README.md` 0 錯
- [x] 6.2 4 份主 spec（`openspec/specs/*/spec.md`）的 `## Purpose` 改用新用語，glossing-validation 的 Purpose 拿掉「構詞標記在原語會 ODS 清單內」；`pymarkdown` 0 錯
- [x] 6.3 **先問使用者同意**，再改 `CLAUDE.md` 裡的用語：「組數」→「段數」、「逐組」→「逐段」、「第幾組」→「第幾段」；「3 組例」的「組」是「一組例子」，不改

## 7. 整體確認

- [x] 7.1 重跑 `python -m scripts.validate_glossing` 與 `python -m scripts.check_docx_txt`，抽看 `kithann/out/corpus.yaml`：每個檔案有 `語言別`、`語言別代號`（11 個語料目錄都不是空字串）、`段`，每段只有 `編號`、`開始`、`結束`、`族語原句`、`詞素切割`、`詞素翻譯`、`華語翻譯`
- [x] 7.2 抽看 `kithann/out/glossing_report.md`：沒有「構詞判斷困難」「不確定」標記統計、「構詞無法判斷」、「用語要不要換」；`grep -n "構詞" kithann/out/*.md` 只剩《常用構詞標記清單》（兩份報告符合；另一處是 docx 審閱註解原文。`kithann/out/` 另有 8/28 從舊 feature 轉出的 7 份 md，目前程式不會產生，是否刪除待使用者決定）
- [x] 7.3 `grep -rn "組\|切分\|gloss\|原文\|語別\|分段" features scripts tests openspec/specs README.md` 剩下的每一筆都在決策 2 的例外裡（另外記得「組裝」不是語料單位，不改）（`features`、`scripts`、`tests`、`README.md` 符合；`openspec/specs/*` 的內文要等 archive 套用 delta 才會換，現在不手改）
- [x] 7.4 `tox -e test` 全部通過：0 failures、0 errors；第 8.1 節基準的 9 個失敗都已修好，而且沒有用刪測試的方式讓它過（被刪掉的測試要說得出是哪一條規格不要了）
- [x] 7.5 `tox -e flake8`、`tox -e pymarkdown`、`tox -e behave`、`npx gherkin-lint` 全部通過

## 8. 紀錄

### 8.1 基準（2026-10-30，change 建立時）

`tox -e behave`：6 features passed、1 skipped（`tshi.feature` 是空的範例檔）；63 scenarios passed、0 failed；176 steps passed。

`tox -e test`：111 個測試，2 failures、7 errors，全部是 staged 的 YAML 改動（`句`→`段`、拿掉詞與詞素）造成，測試還沒跟上：

- `test_entry`：`test_句_yaml_的_key`（KeyError `詞`）、`test_檔案_yaml_只收乾淨的組`（KeyError `句`）
- `test_yamlout`：`test_句層的_key`、`test_只收通過驗證的組`、`test_詞與詞素四層`、`test_附著詞的原詞會併寫`、`test_讀得回來`（KeyError `句`）；`test_檔案層的_key`、`test_一個詞一行`（FAIL）

### 8.2 第 2.2 節的紅 scenario

`python -m behave`：56 scenarios passed、7 failed，沒有 undefined step。7 條紅的原因都是程式的輸出還是舊用語，第 5.2 節會處理：

- `族語原句詞素切割比對.feature`：`不符——只差單引號`（:82）、`不符——差 2-3 個字母`（:128）、`不符——長度差很多`（:150）。預期 `詞素切割多了「'」`，實際 `切分多了「'」`；差異訊息來自 `parser.compare_source`
- `詞素切割與詞素翻譯對應.feature`：`不對應——詞素翻譯的詞比詞素切割少`（:34）、`…多`（:58）、`不對應——詞素切割沒有切，詞素翻譯有切`（:82）、`不對應——詞素切割有切，詞素翻譯沒有切`（:108）。預期新分類名，實際 `gloss 的詞比切分少` 等舊名稱；分類名來自 `rules.check_correspondence`

## Workflow follow-up

- 使用者確認後 archive 這個 change，archive 後確認 4 份主 spec 已套用 delta，`openspec validate --specs` 通過。
