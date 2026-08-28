# Proposal: steps-follow-features

## Why

`features/*.feature` 已經是規格（見 CLAUDE.md「Gherkin feature」），但 `features/steps/` 是各自為政湊出來的：step 自己把幾支函式串起來、自己算答案，走的路跟 `scripts/validate_glossing.py` 不一樣。結果是 behave 63 條全綠，卻有三件事綠得不老實：（1）「結束時間早於開始」那條 step 自己比大小，再 assert 一個 enum 常數等於它自己，程式壞掉也不會紅；（2）feature 定的「切分與 glossing 對應」五種分類只有 step 在呼叫 `check_correspondence`，正式驗證還走舊的兩種分類，報告 §5 印的跟規格不同；（3）`validate_glossing._is_tie` 是已經廢掉的「比長短取詞根」殘骸，它比對的構詞值 `詞綴` 早已不存在，永遠回 False，報告那一節悄悄空掉。同時規格文件有兩份（`features/` 與 `docs/glossing-rules.md`），內容已經走精，`tests/` 又有一份跟 feature 重覆的 unittest。

## What Changes

- **steps 一個 feature 一個檔，同名**：`features/steps/自動處理.py` 拆成 `字元正規化.py`、`排版分析.py`、`時間碼.py`、`原文切分比對.py`；`切分與glossing對應.py`、`構詞判定.py` 照舊。每個 step 只呼叫**一支**函式，而且是 pipeline 呼叫的同一支；step 不串、不組、不算。
- **API 重整（配合上一條）**：`normalize_line(line)` 單行正規化；`compare_source(source, segmentation)` 回傳一個結果物件取代 `matches`／`mismatch_kind`／`mismatch_detail`／`punctuation_of` 四支散裝；`MarkerList.from_rows(rows)` 把 `allowed`／`circumfixes`／`affix_forms` 三個查表合成一個物件；`analyse_word(segmentation_token, gloss_token, markers)` 收兩個字串，不再要假造 `Entry`。pipeline 與 step 都改用這幾支。
- **BREAKING（報告）** `check_correspondence` 接進 `validate()`：報告「問題類型」的 `token 數不對齊`、`切分符號不呼應` 兩類改成 feature 的五類（`gloss 的詞比切分少`、`gloss 的詞比切分多`、`切分沒有切，gloss 有切`、`切分有切，gloss 沒有切`、`符號的種類不一樣`）。對方沒看過舊報告，不做前後對照。
- **刪「比長短」殘骸**：`validate_glossing._is_tie`、`collect()` 的 `ties`、報告「請對方處理」章「兩段一樣長，分不出誰是詞根」一節，以及同章「實詞的意思剛好就是某個詞綴的 gloss」那段（1f 已經解掉，`vaik-i` 現在判得出來）。
- **刪 `docs/glossing-rules.md`**，規格只留 `features/` 一份。它有、feature 沒有的四塊，依性質處理：排灣 `[k]`/`[ʔ]` 書寫取捨（ODS 本身就是來源）刪；特殊符號表（`:`、`＠`、`(咳嗽)`、`...`）、外來語 `.日語` 標籤、語料目錄↔ODS sheet 對應、四行結構與時間碼四種格式——這些不是判定規則而是「語料長什麼樣」，加進 `kithann/out/glossing_report.md` 新的一章「語料格式說明」。`README.md`、`openspec/specs/glossing-validation/spec.md`、`scripts/smkul/rules.py` 三處引用改指 feature 或報告。
- **`tests/` 只留 feature 測不到的**：`test_docx2text.py`、`test_yamlout.py`、`test_report.py` 留；`test_rules.py`、`test_parser.py`、`test_entry.py`、`test_markers.py`、`test_corpus_smoke.py` 裡凡是 feature 已有對應 scenario 的測試刪，剩下的（docx 讀取、YAML 排版、報告排版、ODS 讀取）留。
- 順序：先改 steps（behave 轉紅），再改程式與 API，最後 `behave` 全綠、`tox` 全綠。中途紅是預期的。

## Capabilities

### New Capabilities

（無）

### Modified Capabilities

- `glossing-validation`：「token 對齊」「切分符號呼應」兩條需求併入「切分行與 gloss 行對不起來的分類」，報告與問題類型一律用五類；「ODS 備註欄認可的特殊符號」的依據從 `docs/glossing-rules.md` 改為報告的「語料格式說明」章。
- `corpus-export`：報告新增「語料格式說明」章（四行結構、時間碼格式、切分符號、特殊符號與言談現象、外來語標籤、語料目錄↔ODS sheet 對應）；「請對方處理」章不再有「兩段一樣長」與「實詞撞到詞綴 gloss」兩項。

## Impact

- steps：`features/steps/自動處理.py` 刪，新增 `字元正規化.py`、`排版分析.py`、`時間碼.py`、`原文切分比對.py`；`構詞判定.py` 改用 `MarkerList` 與 `analyse_word`；`切分與glossing對應.py` 不動。
- 程式：`scripts/smkul/parser.py`（`normalize_line`、`compare_source` 與 `SourceCheck`；刪 `matches`／`mismatch_kind`／`mismatch_detail`／`punctuation_of` 的散裝用法）、`scripts/smkul/markers.py`（`MarkerList`）、`scripts/smkul/rules.py`（`analyse_word`、`validate()` 改用 `check_correspondence`、刪 `check_alignment`／`check_symbols`；docstring 改指 feature）、`scripts/smkul/entry.py`（`IssueKind` 的 `TOKEN_MISALIGNED`／`SEGMENT_SYMBOL_MISMATCH` 換成五類）、`scripts/validate_glossing.py`（`collect()` 拿 `MarkerList`、刪 `_is_tie`／`ties`、`todo_section` 縮）、`scripts/smkul/report.py`（新章 `format_section`）。
- 文件：刪 `docs/glossing-rules.md`；`README.md:48` 改指 `features/`。
- 測試：`tests/` 五個檔案瘦身；`tox -e test` 仍要過。
- 報告：`kithann/out/glossing_report.md` 問題類型改名、新增一章、「請對方處理」縮短。
- 語料檔案本身不修改。
