# Tasks: steps-follow-features

## 1. 先讓 steps 照規格（behave 會轉紅，預期）

- [x] 1.1 `features/steps/自動處理.py` 拆成 `字元正規化.py`、`排版分析.py`、`時間碼.py`、`原文切分比對.py`，每檔只留該 feature 用到的 step；`behave --dry-run` 沒有 undefined step
- [x] 1.2 `字元正規化.py`：`原本的一行是` 只呼叫 `parser.normalize_line`；step 檔裡沒有第二個 parser 函式的 import
- [x] 1.3 `時間碼.py`：`這一組記成結束時間早於開始` 改成用 `parse_text` 餵最小四行組、檢查 `entry.issues` 含 `IssueKind.REVERSED_TIMECODE`；step 裡不再有 `timecode_parts` 與自己比大小的邏輯
- [x] 1.4 `原文切分比對.py`：`原文是…切分是…` 只呼叫 `parser.compare_source`，`Then` 讀 `SourceCheck` 的欄位；step 檔裡沒有 `matches`／`mismatch_kind`／`mismatch_detail`／`punctuation_of` 的 import
- [x] 1.5 `構詞判定.py`：Given 用 `MarkerList.from_rows`，When 用 `rules.analyse_word(seg, gloss, markers)`；沒有 Given 的 scenario 用 `MarkerList.empty()`；step 裡不再造 `Entry`
- [x] 1.6 `排版分析.py`、`切分與glossing對應.py` 只搬檔／確認不變；`npx gherkin-lint` 0 錯
- [x] 1.7 跑 `behave`，把紅的 scenario 清單記在本檔 §6，確認紅的原因全是「API 還不存在」而不是 step 寫錯

## 2. API 重整（讓 steps 綠）

- [x] 2.1 `parser.normalize_line(line)`：BOM、全形＝、引號、en-dash、空白摺疊；`normalize_text` 改成逐行呼叫它；`字元正規化.feature` 5 條綠、`時間碼.feature` en-dash 式綠
- [x] 2.2 `parser.compare_source(source, segmentation) → SourceCheck(passed, kind, detail, punctuation_differs)`；`assemble_entry` 改用它產生 `SOURCE_SEGMENT_MISMATCH`、`PUNCTUATION_DIFF`；`原文切分比對.feature` 11 條綠；舊四支從公開 API 移除（`grep -rn "mismatch_kind\|punctuation_of" scripts features` 只剩 parser 內部）
- [x] 2.3 `markers.MarkerList`（`from_rows`、`empty`、`allowed`、`circumfixes`、`affix_forms`、`is_marker`、`circumfix_pair`）與 `load_marker_lists(path) → dict[sheet, MarkerList]`；`load_markers`／`load_circumfixes`／`load_affix_forms` 刪；`validate_glossing.collect` 只做一次 `.get(sheet)`
- [x] 2.4 `rules.analyse_word(seg_token, gloss_token, markers) → [Morpheme]`；`build_words(entry, markers)`、`classify(forms, glosses, markers)`、`collect_undecided(entry, markers, sheet)` 跟著縮簽名；`構詞判定.feature` 26 條綠
- [x] 2.5 `rules.validate(entry, markers, sheet_name)` 改用 `check_correspondence`；`entry.IssueKind` 加五類（值＝feature 分類名）、刪 `TOKEN_MISALIGNED`／`SEGMENT_SYMBOL_MISMATCH`；`check_alignment`／`check_symbols` 刪；`KIND_WHY`、`SEVERITY` 補齊；`切分與glossing對應.feature` 7 條綠
- [x] 2.6 `python -m behave` 6 features 63 scenarios 全綠

## 3. 刪「比長短」殘骸與過時說明

- [x] 3.1 刪 `validate_glossing._is_tie`、`collect()` 的 `ties`、`todo_section` 的「兩段一樣長」節與「實詞的意思剛好就是某個詞綴的 gloss」段；該節只留一句指向「構詞判斷困難」章；`grep -n "tie\|最長" scripts/` 無殘留
- [x] 3.2 `rules.py` 模組 docstring 改指 `features/構詞判定.feature`；`grep -rn "glossing-rules" scripts features openspec/specs README.md` 只剩 README 待 4.3 處理

## 4. 規格文件只留一份

- [x] 4.1 `report.format_section(files)` 產生「語料格式說明」章：四行結構、時間碼四種格式（檔數從 `files` 算）、切分符號表、特殊符號表（用 `rules.SPECIAL` 同一份常數）、外來語標籤、目錄↔sheet 對應（用 `markers.SHEET_OF`）；插在「YAML 輸出」章之後；`test_report.py` 加一個測試驗證檔數是算出來的
- [x] 4.2 刪 `docs/glossing-rules.md`；`git status` 顯示 `docs/` 已空（目錄一併移除）
- [x] 4.3 `README.md:48` 改成指向 `features/`（規則）與 `kithann/out/glossing_report.md` 的「語料格式說明」章（格式）
- [x] 4.4 重跑 `validate_glossing.py`，確認 `glossing_report.md` 有新章、問題類型用五類名、「請對方處理」章縮短；`pymarkdown` 過

## 5. tests/ 瘦身

- [x] 5.1 列對應表（unittest 名 → feature Scenario 名）記在本檔 §7，只有表上有的才刪
- [x] 5.2 刪 `test_rules.py`、`test_parser.py`、`test_entry.py`、`test_markers.py`、`test_corpus_smoke.py` 裡表上的測試；改剩下的測試用新 API（`MarkerList`、`compare_source`）；`tox -e test` 過
- [x] 5.3 `tox -e flake8,test,behave,yamllint,pymarkdown` 與 `npx gherkin-lint features/*.feature` 全綠

## 6. 第 1 步後的紅單（apply 時填）

behave 在載入 step 檔時就 ImportError，跑不到單一 scenario，所以紅的
是全部 6 個 feature、63 條 scenario。逐一確認缺的是 API，不是 step 寫錯：

| 缺的名稱 | 由哪一個任務補 |
| --- | --- |
| `parser.normalize_line` | 2.1 |
| `parser.compare_source` | 2.2 |
| `markers.MarkerList` | 2.3 |
| `rules.analyse_word` | 2.4 |

step 用到的其他名稱（`parse_text`、`parse_timecode`、`IssueKind`、
`check_correspondence`）都已經存在。`gherkin-lint` 0 錯、
`flake8 features/steps/` 0 錯，所以不是 step 語法或 feature 的問題。

## 7. unittest → Scenario 對應表（apply 時填）

只有這張表上的測試才刪——feature 已經有對應的 Scenario，留著會變成
兩份規格。表上沒有的一律留，包括 `test_entry.py`（YAML 形狀與 severity）、
`test_markers.py`（ODS 讀取）、`test_corpus_smoke.py`（全語料不變量）、
`test_docx2text.py`、`test_yamlout.py`、`test_report.py` 整份。
（路徑是 apply 之後重排過的，見 8.4。）

### 7.1 tests/smkul/test_rules.py

| unittest | 對應的 Scenario |
| --- | --- |
| `test_數目一樣就過` | 切分與glossing對應：對應正常 |
| `test_數目無仝就是錯` | 切分與glossing對應：gloss 的詞比切分少 |
| `test_符號長相` | 切分與glossing對應：拉長音的 == 被當成構詞符號 |
| `test_呼應就過` | 切分與glossing對應：對應正常 |
| `test_中綴呼應` | 構詞判定：1a 中綴 |
| `test_不呼應就是錯` | 切分與glossing對應：切分沒有切，gloss 有切 |
| `test_詞綴` | 構詞判定：2c 前綴 |
| `test_附著` | 構詞判定：2a 依附詞（= 在詞根後） |
| `test_重疊` | 構詞判定：2b 重疊（跨過 ~） |
| `test_中綴抽出來排頭前` | 構詞判定：1a 中綴 |
| `test_拉長音的等號毋是切分符號` | 切分與glossing對應：拉長音的 == 被當成構詞符號 |
| `test_gloss_用同一套規則` | 構詞判定：1a 中綴 |
| `test_詞根用_gloss_判斷` | 構詞判定：3a 剛好一段沒被標成詞綴 |
| `test_後綴的詞根嘛掠會著` | 構詞判定：2d 後綴 |
| `test_清單內的標記判做前綴` | 構詞判定：2c 前綴 |
| `test_兩段攏查無就判袂出詞根` | 構詞判定：3b 不只一段沒被標成詞綴 |
| `test_詞根的意譯免查表` | 構詞判定：1f 形也要對得上 |
| `test_無切分符號ê詞規个就是詞根` | 構詞判定：3a 沒有切分符號的詞 |
| `test_對應通過` | 切分與glossing對應：對應正常 |
| `test_gloss_ê詞較少` | 切分與glossing對應：gloss 的詞比切分少 |
| `test_切分無切_gloss有切` | 切分與glossing對應：切分沒有切，gloss 有切 |
| `test_符號種類無仝` | 切分與glossing對應：符號的種類不一樣 |

留下來的：`test_兩個中綴`（feature 沒有兩個中綴的例子）、
`test_原詞是切分提掉符號`（`Word.raw`，feature 只看詞素）、
`test_大寫的不確定標記放行且統計`、`test_不確定標記的樣式`、
`test_整組驗證`（`validate()` 整合）。

### 7.2 tests/smkul/test_parser.py

| unittest | 對應的 Scenario |
| --- | --- |
| `test_逗號式`、`test_典型_逗號式` | 時間碼：逗號式 |
| `test_srt式`、`test_典型_srt式` | 時間碼：SRT 式 |
| `test_endash式` | 時間碼：en-dash 式 |
| `test_連字號式無毫秒` | 時間碼：連字號式 |
| `test_掠著顛倒ê時間碼` | 時間碼：結束時間比開始還早 |
| `test_bom` | 字元正規化：移除 BOM（U+FEFF） |
| `test_全形等號` | 字元正規化：全形 ＝ 換成半形 = |
| `test_引號統一` | 字元正規化：引號統一成 U+0027 |
| `test_endash_gloss_換成半形` | 字元正規化：切分行與 gloss 行的 en-dash |
| `test_空白摺疊` | 字元正規化：多餘的空白合併成一個 |
| `test_缺空行也切得出兩組` | 排版分析：組間缺空行照常切組 |
| `test_檔頭註記收成_metadata` | 排版分析：檔頭註記收進 metadata |
| `test_行類型` | 排版分析：認拉丁行只算小寫字母，大寫標記不算 |
| `test_四行組` | 排版分析：短句照原樣切一組 |
| `test_六行長句重組` | 排版分析：長句分段重組——兩段 |
| `test_八行長句重組` | 排版分析：長句分段重組——三段 |
| `test_原文與切分相同_沒問題` | 原文切分比對：一般情形 |
| `test_標點與大小寫的差異不算錯` | 原文切分比對：只差英文大小寫 |
| `test_差一個字母就算錯`、`test_只差一個字母` | 原文切分比對：不符——只差一個字母 |
| `test_差一個單引號就算錯`、`test_只差單引號` | 原文切分比對：不符——只差單引號 |
| `test_長度差很多` | 原文切分比對：不符——長度差很多 |
| `test_差異描述看得出差在哪` | 原文切分比對：差異是 |
| `test_punctuation_of` | 原文切分比對：只差標點，算通過 |

留下來的是 feature 沒有的錯誤分類與 log 計數：`test_空組`、
`test_孤兒時間碼`、`test_雜訊行`、`test_布農的_0000_也是雜訊`、
`test_缺翻譯行`、`test_黏行`、`test_缺gloss段`、`test_重複標註`兩條、
`test_純華語句_三種表法`（feature 只有 4 行那一種）、
`test_缺翻譯行`、`test_標點不同是_warning_不擋匯出`、
`test_標點相同就不記`、`test_病態組都組不起來`、
`test_格式中途切換會記_warning`、`test_典型_連字號式_會記單位不明`、
`test_編號同行`、`test_編號與時間碼同行`、`test_不是時間碼`、
`test_沒有_endash_就不計數`、`test_全形等號_解析後沒有全形`、
`test_endash_gloss_重組後換半形`、`test_bare_form_留單引號_去掉標點大小寫`、
`test_時間碼拆做數字`、`test_正常ê時間碼無代誌`、`test_正常的組沒問題`。

## 8. 覺得不合理、先跳過的項目（apply 時填，做完一併回報）

沒有跳過任何一項，22 項全做完。feature 沒有發現不合理的地方——
這次動的是 steps 與程式，feature 一個字都沒改。

### 8.1 與任務字面不同的一處做法

**2.1 的「`normalize_text` 改成逐行呼叫它」沒有照字面做。**

照字面做會壞掉:`normalize_line` 依 feature 必須換 en-dash
（`features/字元正規化.feature` 的「切分行與 gloss 行的 en-dash –
換成半形 -」走的就是這一支），而 `normalize_text` 在切組之前跑，
時間碼行的 en-dash 是**合法的分隔符號**
（`features/時間碼.feature` 的「en-dash 式」）。先換掉的話，
`0:00:00.000–0:00:05.000` 會被當成連字號式，多記一筆
「時間碼單位不明」的 warning。

改成:兩支共用一個私有的 `_fix_chars`（全形＝、引號），
`normalize_line` 再加上 BOM、en-dash、空白摺疊。分工照 design D3
講的「切組先做，四行的內容才正規化」——`assemble_entry` 對四行
呼叫 `normalize_line`。step 那一邊仍然只呼叫一支函式，
2.1 的驗收（`字元正規化.feature` 5 條綠、`時間碼.feature`
en-dash 式綠）都成立。

### 8.2 任務清單以外，順手做掉的三件

1. **`COMPARE_NOTE` 講反話**（`scripts/validate_glossing.py`）:報告
   原本寫「比對時忽略下列三項:1. 空白」，但
   `features/原文切分比對.feature` 定的是「空白也不忽略——空白會
   改變詞的個數」，程式也照 feature 做。已改成忽略兩項（標點、
   大小寫），並寫明空白不忽略、依附詞併詞是唯一例外。
2. **`排版分析.py` 的 step 呼叫兩支函式**:原本寫
   `parse_text(normalize_text(context.text))`，可是 `parse_text`
   內部本來就會呼叫 `normalize_text`，等於正規化做兩次。改成只
   呼叫 `parse_text`，符合 design D2「一個 step 只呼叫一支函式」。
3. **gloss 對表的小工具搬家**:`is_uncertain`、`head_of`、
   `_is_focus`、`REDUPLICATION_GLOSS` 從 `rules.py` 搬到
   `markers.py`。`MarkerList.is_marker()` 要用它們，留在 rules.py
   會讓 markers 反過來 import rules。搬過去之後
   markers.py 是「ODS 清單與怎麼查表」，rules.py 是「切分與判定」，
   分工比較乾淨。

### 8.3 驗證過、但值得記一筆的數字

`check_correspondence` 接進 pipeline 之後，YAML 匯出 4292 組。
用同一次執行同時算新舊兩種算法:**兩種都是 4532 組通過對應檢查**
（4532 − 240 組純華語句 NOTICE ＝ 4292），所以匯出的組沒有因為這次
改動而增減。問題筆數由 327 降到 321，是因為新做法一組只記第一個
對不起來的詞（規格就是這樣定的），舊做法會把同一組的每個詞各記一筆。

### 8.4 apply 之後追加的兩件（使用者當場交代）

1. **刪掉沒人讀的 context 變數**:`features/steps/排版分析.py` 的
   `context.raw`、`features/steps/構詞判定.py` 的 `context.language`，
   兩個都只寫不讀。六個 step 檔的 context 變數逐一對過寫與讀
   （含 `getattr` 那種間接讀），其餘 13 個都確實有用。
2. **`tests/` 照 `scripts/` 的層次重排**:
   `tests/smkul/` 對 `scripts/smkul/`（7 個模組測試），
   `tests/` 這一層留 `test_corpus_smoke.py`（跨模組的整合測試，
   對應的是 `scripts/validate_glossing.py` 走的那條路，不是單一模組）。
   測試資料仍在 `tests/data`，路徑常數 `DATA`、`ODS` 收進
   `tests/__init__.py`，原本五個檔各算一次的 `os.path.dirname(__file__)`
   都拿掉。`python -m unittest` 的自動探索照樣抓到 110 條。
