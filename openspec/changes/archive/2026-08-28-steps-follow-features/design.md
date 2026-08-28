# Design: steps-follow-features

## Context

見 proposal.md「Why」。現況是每個 step 檔各自組合內部函式，跟 `validate_glossing.py` 走不同路；feature 全綠不代表報告照規格。要改的不是 feature（feature 是規格、是標準答案），而是 step 與 step 呼叫的 API。

限制：Python 不用 list comprehension；程式註解、docstring、變數名用華語；每個 feature 都要能不靠語料、不靠 ODS 檔案就跑（scenario 自帶資料）；`tox -e flake8,test,behave,yamllint,pymarkdown` 與 `npx gherkin-lint` 都要過。

## Goals / Non-Goals

**Goals:**

- 一個 step 只呼叫一支函式，而且是 pipeline 用的同一支。看 step 檔就知道「這條規格對應哪支 API」。
- behave 綠 ⇒ 報告照規格。做不到這點的 step 視為假測試。
- API 的參數只收規格提到的東西：字串、清單的列。不要為了呼叫而假造 `Entry`。
- 規格一份（`features/`），程式行為的說明一份（報告）。

**Non-Goals:**

- 不改任何 feature，Scenario 與說明文字都不動。
- 不改構詞判定的規則本身，不改 YAML 欄位。
- 不改 `check_docx_txt.py` 與 docx 報告。

## Decisions

### D1. Step 檔一個 feature 一個，同名

`自動處理.py` 現在裝四個 feature 的 step，找 step 要用 grep。改成 `features/steps/<feature 名>.py`，behave 本來就會全部載入，檔名只是給人看的。

替代：留一個大檔、用區段註解分——review 時 diff 會混在一起，不採。

### D2. 每個 step 的唯一入口

| feature | step 呼叫的唯一入口 | 回傳 | pipeline 在哪裡呼叫 |
|---|---|---|---|
| 字元正規化 | `parser.normalize_line(line)` | `str` | `normalize_text` 逐行呼叫它 |
| 排版分析 | `parser.parse_text(text)` 後 `build_entry` | `CorpusFile` | `parse_corpus_file` |
| 時間碼 | `parser.parse_timecode(line)`；顛倒那條走 `parse_text` 看 `entry.issues` | `Timecode` / issues | `split_entries`、`assemble_entry` |
| 原文切分比對 | `parser.compare_source(source, segmentation)` | `SourceCheck` | `assemble_entry` |
| 切分與glossing對應 | `rules.check_correspondence(seg, gloss)` | `(分類 \| None, token, token)` | `rules.validate` |
| 構詞判定 | `markers.MarkerList.from_rows(rows)`、`rules.analyse_word(seg_token, gloss_token, markers)` | `[Morpheme]` | `rules.build_words` |

「顛倒時間碼」不再由 step 自己算。step 用 `parse_text` 餵一組最小的四行，然後檢查 `entry.issues` 裡有 `IssueKind.REVERSED_TIMECODE`——這樣程式沒記就會紅。

替代：讓 `parse_timecode` 自己回傳「顛倒」旗標——但 feature 說的是「這一組記成…」，是組層級的 issue，不是時間碼層級的屬性，照 feature 走。

### D3. `normalize_line` 要不要管「這是哪一行」

feature 說 en-dash 只換切分/gloss 行、時間碼行不換。現在 `normalize_text` 全文做 BOM／全形＝／引號，en-dash 在 `assemble_entry` 才對切分/gloss 行做。`normalize_line(line)` 做的是**不看行別**的那幾項（BOM、全形＝、引號、空白摺疊）；en-dash 留給 `normalize_en_dash`，由 `assemble_entry` 對切分/gloss 行呼叫。

字元正規化.feature 的 en-dash scenario（第 58 行）給的是一行 gloss，step 對它呼叫的是 `normalize_en_dash`，不是 `normalize_line`——這是唯一一個 feature 裡兩種 When 共用同一句「原本的一行是」的情況。處理方式：step 檔裡 `原本的一行是` 一律走 `normalize_line`，`normalize_line` 內部**也**換 en-dash；時間碼行不受影響是因為 `parse_timecode` 在 `normalize_line` 之前就已經認出時間碼行（`split_entries` 先切組再正規化四行）。設計上把「en-dash 只動切分/gloss 行」從「兩支函式」變成「呼叫順序」。實作時要驗證 `parse_timecode` 認 en-dash 式時間碼不受影響（`時間碼.feature` en-dash 式那條會顧到）。

替代：`normalize_line(line, role)` 加參數——step 要多傳一個 feature 沒提的東西，不採。

### D4. `compare_source` 回傳結果物件

```text
SourceCheck
  passed              bool
  kind                str | None   （詞數不同／只差單引號／只差一個字母／差 2-3 個字母／多處不同／長度差很多）
  detail              str          （「l」→「r」／切分多了「'」…）
  punctuation_differs bool
```

`assemble_entry` 用它產生 `SOURCE_SEGMENT_MISMATCH` 與 `PUNCTUATION_DIFF` 兩種 issue；step 直接讀欄位。`matches`／`mismatch_kind`／`mismatch_detail`／`punctuation_of` 從公開 API 退場（可以留做 `compare_source` 的內部函式）。

### D5. `MarkerList`

```text
MarkerList
  from_rows(rows)      ← ODS 的列（step 的 Given 表格、markers.read_sheets 都給這個）
  allowed              set[str]
  circumfixes          set[(head, tail)]
  affix_forms          dict[str, set[str]]
  is_marker(form, gloss)
  circumfix_pair(glosses)
```

`load_markers`／`load_circumfixes`／`load_affix_forms` 併成 `load_marker_lists(path) → dict[sheet, MarkerList]`。`collect()` 只做一次 `.get(sheet, MarkerList.empty())`。

`analyse_word(seg_token, gloss_token, markers)` 回 `[Morpheme]`；`build_words(entry, markers)` 對每個 token 對呼叫它。`classify` 的簽名跟著縮成 `(forms, glosses, markers)`。

### D6. `check_correspondence` 接進 `validate()`

`validate()` 的 `check_alignment`＋`check_symbols` 換成 `check_correspondence`，五類各對應一個 `IssueKind`（`GLOSS_FEWER`、`GLOSS_MORE`、`GLOSS_CUT_MORE`、`GLOSS_CUT_FEWER`、`SYMBOL_KIND_DIFF`），值就是 feature 的分類名。`KIND_WHY` 補五段華語說明。`TOKEN_MISALIGNED`、`SEGMENT_SYMBOL_MISMATCH` 刪。

### D7. `docs/glossing-rules.md` 的去向

「規則」只留 feature。「語料長什麼樣」（四行結構、時間碼四種格式與檔數、切分符號表、特殊符號與言談現象、外來語標籤、語料目錄↔ODS sheet）進報告新章「語料格式說明」，由 `report.format_section()` 產生，檔數之類的數字從執行結果算、不寫死；符號表與 sheet 對應這種靜態內容寫在 `report.py` 的常數裡。排灣 `[k]`/`[ʔ]` 那段不留（ODS 是來源，程式沒做任何事）。

替代：把這些寫成 feature 的 Feature 說明文字——但它們不是可測的行為，塞進 feature 只會讓 feature 變厚，不採。

### D8. `tests/` 的取捨

判準：feature 有對應 scenario 的 unittest 刪，其餘留。留的預期是 `test_docx2text.py`、`test_yamlout.py`、`test_report.py` 全部，`test_markers.py` 的 ODS 讀取、`test_parser.py` 的 docx 相關與病態組（feature 沒寫的錯誤分類：孤兒時間碼、雜訊行、重複標註、缺翻譯行…），`test_corpus_smoke.py` 看實作時是否還讀得到 fixture。刪的時候逐個對 scenario 名，在 tasks.md 記對應表，review 才看得出沒刪錯。

## Risks / Trade-offs

- [D3 的 en-dash 順序依賴] → `時間碼.feature` en-dash 式那條就是守門員；另外在 `排版分析.feature` 沒有 en-dash 時間碼的例子，實作時用 `tests/` 留的 `test_endash式` 補守。
- [問題類型改名，報告 §5 與 `KIND_WHY` 的華語說明要重寫] → 說明文字直接引 feature 的 Scenario 名，少寫一次。
- [`tests/` 刪太多，docx/YAML/報告排版失守] → 判準寫死「feature 有對應才刪」，對應表進 tasks.md。
- [中途 behave 紅一段] → 使用者已接受；tasks 的順序先 steps 再程式，紅的時間最短。
- [`analyse_word` 少了 `Entry.source`，`Word.raw`（原詞）算不出來] → `build_words` 仍拿 `entry`，自己對 `source_tokens`；`analyse_word` 只負責詞素，不負責原詞。
