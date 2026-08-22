# Design: corpus-glossing-pipeline

## Context

動機見 proposal.md。關鍵現況:

- 語料 31 docx + 30 txt、約 7,400 組;29 對同名配對、2 個配對異常。
- txt 格式變體:四種時間碼、編號同行/獨行、檔頭註記(8 檔)、組內行數≠4 者約 1,128 組(86% 是長句分段交錯的刻意排版,已用 docx 驗證分段在原稿就存在)。
- ODS 標記清單分 13 個語言 sheet,備註欄另藏特殊符號規則。
- devcontainer 只有 python3.12-minimal(無 pip/venv,stdlib 缺 `shutil`、`json` 等),tox 跑不動,需先補環境。
- CI:`tox -e test` 跑 `python -m unittest`(自動 discovery)、flake8 max-line-length 79。
- CLAUDE.md 規定:`for` 置前,禁止 list/generator comprehension。
- 語料之後會持續交付,全部程式必須可重複執行於長大的語料庫。

## Goals / Non-Goals

**Goals:**

- 寬容收語料、嚴格驗證:parser 吃下所有已知變體並分類異常,驗證層嚴格查規則,錯誤全部進報告而非中斷。
- 單一共用解析邏輯:docx↔txt 比對與 glossing 驗證共用同一 parser,兩邊行為一致。
- 報告直接可用於與對方的會議(「請對方處理」專章依檔案分組)。

**Non-Goals:**

- 不修改語料檔案本身(不自動修錯,錯誤請對方重產)。
- 不解析 docx 顏色/標亮語意(只在報告提醒)。
- 不換算時間碼(保留原字串)。
- 不處理尚未交付的族別(鄒、賽夏等 ODS 有 sheet 但語料還沒來;目錄對應表先只建現有六種)。

## Decisions

### D1: 目錄結構——library 與 CLI 分離

```text
scripts/
  check_docx_txt.py          # CLI,python -m scripts.check_docx_txt
  validate_glossing.py       # CLI,python -m scripts.validate_glossing
  smkul/
    __init__.py
    entry.py                 # 組/詞/詞素 資料型別
    parser.py                # txt → 組(核心)
    docx2text.py             # docx → 段落文字(stdlib zipfile+ElementTree)
    markers.py               # ODS → 各語言標記集合
    rules.py                 # glossing 驗證(與 docs 規則文件同源)
    report.py                # markdown 報告 + exit code
    yamlout.py               # YAML 匯出
docs/glossing-rules.md       # 需求 2 的規則文件
tests/
  __init__.py
  test_parser.py test_rules.py test_markers.py
  test_docx2text.py test_report.py
  data/                      # 小 fixture:典型組+每種病態各一
kithann/out/                 # 全部程式產出:報告與 corpus.yaml(不進版控)
```

CLI 一律從 repo 根目錄以 `python -m scripts.<name>` 執行,import `scripts.smkul`,免動 `sys.path`。理由:使用者指定 library 放 `scripts/smkul/`;`python -m unittest` 從根目錄 discovery 找到 `tests/`(有 `__init__.py`),CI 不用改。

### D2: parser 策略——行類型分類 + 狀態機

組界靠「編號行(+時間碼行)」辨識,不靠空行。組內行的類型判斷:

- **切分行**:以拉丁字母與構詞符號為主(可含華語借詞 token)
- **gloss 行**:含 CJK 標記詞彙、有欄位式空白分隔
- **翻譯行**:CJK 自由文本,無欄位分隔

長句分段重組:內文行數為偶數且 >4 時,嘗試「原文 + (切分, gloss) 配對 × n + 翻譯」的交錯配對;配得起來→重組,配不起來→依黏行/缺 gloss 段分類為異常。判斷依據是行類型而非行數,因此 3/5 行的黏行與缺段也能歸類。理由:86% 的 ≠4 行組是規律排版,重組可讓約 965 組免於誤判為錯誤;其餘真錯誤靠類型配對失敗自然浮出。替代方案(固定行數切割)無法同時處理兩者,棄。

### D3: docx 比對走「同一 parser」

docx 先抽段落純文字(stdlib 解析),得到與 txt 同構的行序列,餵**同一個** parser,再逐組比對正規化後的內容(空白摺疊)。理由:避免兩套解析邏輯漂移;空白差異天然被正規化吸收。替代方案(整檔正規化字串 diff)無法定位到組編號,棄。

### D4: ODS 標記集合的建立

stdlib 解析 ODS 讀 13 個 sheet,每 sheet 取「詞素翻譯」欄拆出語法標記(依 `-`/`=`/`<>` 切開後的 CJK 標記單元),連同「詞綴或詞」欄建立每語言的合法標記集合。備註欄的特殊符號規則(`==`、`:`、`＠`、`...`、`^`)整理進 `docs/glossing-rules.md` 並硬編碼為 rules.py 的合法符號表。理由:ODS 是對方權威清單,但格式鬆散,啟動時解析一次、測試鎖住解析結果,格式變動時測試會先叫。

### D5: 正規化與錯誤的分界(已與使用者逐項定案)

- 靜默轉換:BOM、全形 `＝`→`=`、`'`/`'`→U+0027、切分/gloss 行內 en-dash `–`→`-`(時間碼行不轉,`–` 是合法分隔符)、空白摺疊、長句分段重組、缺空行、檔頭/元註記收 metadata
- warning(不影響 exit code):同檔時間碼格式混用、魯凱時間碼單位不明
- 錯誤(exit code 非 0、進報告):黏行、缺 gloss 段、缺翻譯行、空組、孤兒時間碼、孤立雜訊行、token 不對齊、符號不呼應、標記不在清單、docx↔txt 差異、缺檔、檔名不一致
- 純華語句:不算錯誤也不匯出,報告以「格式不一致現象」呈現
- 大寫「不確定」標記(ODS 備註 1-2 慣例,如 `PI`、`KA`、`HA`):合法、不查表列錯,但報告單獨統計一區供對方檢視

### D6: 環境——devcontainer 加 Python feature

`.devcontainer/devcontainer.json` 加:

```json
"ghcr.io/devcontainers/features/python:1": { "version": "3.10" }
```

`postCreateCommand` 追加 `pip install tox`。版本對齊 .travis.yml 的 3.10。理由:官方 feature 含 pip/venv,與 CI 同版;替代方案 apt 裝 python3-pip 會裝到 3.12 與 CI 不一致,棄。

### D7: 依賴——依「採購安全說明書 v2.0」審查,只留 PyYAML

依 `kithann/採購安全說明書_v2.0.txt` 第三章審查開源套件(非中國團隊、搜「security issue」名聲、GitHub 三個月內有維護、issue/PR 有處理),2026-08 審查結果:

| 套件 | 團隊 | 維護 | 安全 | 判定 |
|---|---|---|---|---|
| PyYAML | yaml org(非中國) | Sustainable | CVE 皆為 unsafe load 不信任輸入;本案只 dump | **採用** |
| python-docx | 個人(非中國) | 12 個月無 release | 本體無 CVE;依賴 lxml 有 CVE-2026-41066 | **不採用** |
| odfpy | 個人(非中國) | 2020 起無 release,70 開放 issue | 無 CVE 但形同棄置 | **不採用** |

docx 與 ODS 都是 zip+XML,本案只需**讀取文字**,依說明書「盡量用內建功能」原則改用 stdlib `zipfile` + `xml.etree.ElementTree` 自行解析(探索階段已驗證可行)。注意 ODS 的 `table:number-columns-repeated` 屬性須正確展開。`requirements.in` 只加 `PyYAML`,之後 `pip-compile` 重產 requirements.txt。YAML 匯出約 7,400 組、預估數 MB,PyYAML 一次 dump 可承受。替代方案(python-docx-ng、odfdo 等較活躍 fork)在只需讀文字的前提下仍不如零依賴,棄。若未來需求擴到寫檔或樣式解析再重審。

### D8: 程式風格約束

依 CLAUDE.md:所有迴圈用前置 `for`,不用 comprehension;flake8 79 字元;git 操作(add/commit 等)一律留給使用者。

## Risks / Trade-offs

- [行類型判斷誤判:含大量華語借詞的切分行被當成 gloss 行] → 判斷用多特徵(構詞符號、拉丁比例、欄位分隔),fixture 收錄海岸 2、中排灣 1 的混語實例做回歸測試。
- [ODS「詞素翻譯」欄格式鬆散,標記集合抽取不全→大量假錯誤] → 報告把「標記不在清單」依標記聚合統計,實作時先跑全語料人工抽查 top 未匹配標記,必要時調整抽取規則。
- [魯凱時間碼、紅字意義等外部未知] → 不擋 pipeline,固定寫入報告「請對方確認」章節。
- [對方重新交付格式又變] → parser 對未知格式行歸「孤立雜訊行」錯誤而非 crash;fixture 制回歸。

## Open Questions

(無。原有兩題已定案:產出都放 `kithann/out/`(`docx_txt_report.md`、`glossing_report.md`、`corpus.yaml`),且 `kithann/out/` **不進版控**——.gitignore 排除。)
