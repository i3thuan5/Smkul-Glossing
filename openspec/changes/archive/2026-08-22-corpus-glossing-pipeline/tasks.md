# Tasks: corpus-glossing-pipeline

## 1. 環境

- [x] 1.1 `.devcontainer/devcontainer.json` 加 python:1 feature(version 3.10)、postCreateCommand 追加 `pip install tox`;請使用者 rebuild container 驗證 `python --version` 與 pip
- [x] 1.2 `requirements.in` 只加 `PyYAML`(依採購安全說明書審查,見 design D7),跑 `pip-compile` 重產 requirements.txt
- [x] 1.3 建立 `scripts/`、`scripts/smkul/`、`tests/`、`docs/`、`kithann/out/` 骨架(含 `__init__.py`),`.gitignore` 排除 `kithann/out/`,確認 `tox -e test` 綠燈(零測試也要能跑)

## 2. 規則文件(需求 2)

- [x] 2.1 撰寫 `docs/glossing-rules.md`:組結構(編號/時間碼/四行)、四種時間碼格式、第二行符號系統(`-`/`=`/`<>`/`~`)、第三行 gloss 對齊與 `.` 多屬性、ODS 備註欄特殊符號(`==`、`:`、`＠`、`...`、`^`)、大寫「不確定」標記慣例、長句分段排版、正規化規則
- [x] 2.2 讀 ODS 13 sheet 的備註欄,把特殊符號規則核對補進文件

## 3. 核心解析(corpus-parsing)

- [x] 3.1 `entry.py`:組/詞/詞素資料型別與異常分類列舉
- [x] 3.2 `tests/data/` fixture:典型四行組(各時間碼格式)+ 病態案例各一(黏行、缺 gloss 段、空組、孤兒時間碼、雜訊行、純華語句三種表法、長句 6/8 行、檔頭註記、全形＝、混用 apostrophe、缺空行、格式中途切換)
- [x] 3.3 `parser.py`:組界辨識(編號獨行/同行)、四種時間碼 split 保留原字串、字元正規化(BOM、＝、apostrophe、gloss/切分行 en-dash)+ unittest
- [x] 3.4 `parser.py`:行類型分類與長句分段重組 + unittest
- [x] 3.5 `parser.py`:結構異常偵測分類(黏行/缺段/空組/孤兒時間碼/雜訊行/純華語句)+ unittest
- [x] 3.7 `parser.py`:原文嚴格檢查切分(差一字母/撇號就算錯)、重複標註偵測(原文 vs 切分比長度)+ unittest
- [x] 3.6 全語料冒煙測試:30 txt 全解析不 crash,異常統計與探索階段數據(約 1,128 組)對得上

## 4. docx 一致性(需求 1,docx-txt-consistency)

- [x] 4.1 `docx2text.py`:docx → 段落文字(stdlib zipfile+ElementTree)+ unittest(小 docx fixture)
- [x] 4.2 檔案配對檢查:同名配對、單邊缺檔、已知檔名不一致(魯凱霧台 3、太魯閣 2)+ unittest
- [x] 4.3 逐組比對(同 parser、空白摺疊)+ unittest
- [x] 4.6 `docx2text.py`:抽 docx 審閱註解(依文件順序配字母)、`parser.py` 掠 txt 內底ê `[a]` 註解錨點殘骸 + unittest
- [x] 4.4 `scripts/check_docx_txt.py` CLI:輸出 `kithann/out/docx_txt_report.md`(含顏色標記層提醒)、exit code
- [x] 4.5 對全語料實跑,人工抽查報告合理性

- [x] 4.7 `report.py`:共用報告組件(表格、分組、嚴重度、自動處理章、tidy)+ unittest;`pairing.py` 改做逐行比對

## 5. glossing 驗證(需求 3,glossing-validation)

- [x] 5.1 `markers.py`:ODS → 各語言標記集合(stdlib 解析,注意 `table:number-columns-repeated`)、目錄→sheet 對應表 + unittest(鎖住抽取結果的抽樣)
- [x] 5.2 `rules.py`:token 對齊檢查 + unittest
- [x] 5.3 `rules.py`:切分符號呼應檢查(`-`/`=`/`<>`/`~`)+ unittest
- [x] 5.4 `rules.py`:構詞標記查表(只查詞綴/附著/中綴/重疊,詞根意譯不查)、大寫「不確定」標記放行+統計、特殊符號白名單 + unittest
- [x] 5.5 全語料實跑「標記不在清單」聚合統計,人工抽查 top 未匹配標記,必要時修 markers.py 抽取規則

## 6. 匯出與報告(corpus-export)

- [x] 6.1 `yamlout.py`:單一 YAML `kithann/out/corpus.yaml`、華語 key、檔案→句→詞→詞素結構 + unittest(對照 spec 範例)
- [x] 6.2 `report.py`:markdown 報告產生器——總覽統計、錯誤明細(依檔案分組定位組編號)、warning 區、「不確定」標記統計區、「標記不在清單」聚合統計區、依語別統計表、「我們做了什麼自動處理」專章(每項附真實例子與影響筆數)、「請對方處理」專章(缺檔/檔名/紅字/魯凱時間碼/純華語句)+ unittest
- [x] 6.3 `scripts/validate_glossing.py` CLI:串 parser→rules→yamlout/report、輸出 `kithann/out/glossing_report.md`、exit code
- [x] 6.4 全語料實跑:產出 `kithann/out/corpus.yaml` 與 `kithann/out/glossing_report.md`,人工抽查數組 YAML 與原文對照無誤

## 7. 收尾

- [x] 7.1 `tox -e flake8`、`tox -e test` 全綠;確認程式碼符合 CLAUDE.md(for 前置、無 comprehension)
- [x] 7.2 README 補 scripts 用法說明
- [x] 7.3 確認 `kithann/out/` 已被 .gitignore 排除(第 178 行 `kithann/` 已涵蓋)、`git status` 乾淨;`.yamllint.yml` 與 `tox.ini` 的 pymarkdown 也排除 `kithann/`
