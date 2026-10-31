# Design: report-trim

## Context

動機見 proposal.md。現況：

- `scripts/smkul/entry.py` 的 `SEVERITY` 決定每種問題的嚴重度；`Entry.is_clean()` 擋「錯誤」與「現象」，決定翻譯訓練YAML 匯不匯出。
- 校對表（`proofreading.write_sheets()`）現在收**所有**問題，不看嚴重度。
- 報告第 7 章（`validate_glossing.kinds_section()`）照筆數排，再把「族語原句與詞素切割不符」的 6 個小類集中放到最後；總覽的問題表（`report.kind_table()`）只照筆數排，兩邊順序不一樣。
- 「語料格式說明」的目錄↔sheet 對應表與報告開頭的 ODS 檔名，是 `validate_glossing.run()` 讀 ODS（`load_marker_lists()`）之後唯一的用途；構詞判定停用後，ODS 已經不影響驗證結果。
- `scripts/check_docx_txt.py` 依賴 `pairing.py`（配對、逐段比對）與 `docx2text.docx_comments()`（抽審閱註解）。主程式只用到 `pairing.split_kind()`；`proofreading.py` 也用它。
- 使用者在 `kithann/問題種類對照.csv` 逐項決定了翻譯訓練YAML、報告舉例、校對表三欄，整理後剛好完全由嚴重度決定（見決策 1）。

## Goals / Non-Goals

**Goals：**

- 只要知道一種問題的嚴重度，就知道它在三種產出裡的行為，程式裡不另外維護「哪些問題進校對表」的清單。
- 總覽問題表的「編號 N」就是第 7 章的「7.N」節，開會時看表就能翻到說明。
- 刪掉的東西（章節、程式、spec）不留半套：沒有呼叫者的函式、測試、常數一起刪。

**Non-Goals：**

- 不改 YAML 的檔名與 key。
- 除了新增 `分析報告.feature`、`詞素切割與詞素翻譯對應.feature` 三個 Scenario 改名，不改其他 feature。
- 不改「詞素切割有標點」的判定與待討論章（`segment-punctuation` 定的規則照舊）。
- 不改校對表的欄位、ID、讀回規則，只改「哪些問題列入」。

## Decisions

### 決策 1：嚴重度是唯一的開關

| 嚴重度 | 翻譯訓練YAML | 報告第 7 章舉例 | 校對表 |
|---|---|---|---|
| 錯誤 | 不匯出 | 舉例 | 列 |
| 錯誤（照常匯出） | 匯出 | 舉例 | 列 |
| 警告（照常匯出） | 匯出 | 舉例 | 不列 |
| 現象 | 不匯出 | 舉例 | 不列 |

程式的對應：

- 翻譯訓練YAML：`Entry.is_clean()` 照舊（擋錯誤、現象）。
- 報告舉例：四級都舉例，第 7 章照舊列出每一種有發生的問題。
- 校對表：`write_sheets()` 只收 `Severity.ERROR` 與 `Severity.EXPORTED_ERROR`。判斷放在 `proofreading.py` 的一個常數（例如 `PROOFREAD_SEVERITIES`），不在 `validate_glossing.py` 判斷。

這張表同時寫進 spec（corpus-export 新增「嚴重度決定三種產出」）與報告總覽，三處說法一致。

**替代方案**：每種問題另外標「要不要進校對表」。缺點是多一份清單要維護；而且使用者逐項決定的結果剛好跟嚴重度一致，沒有例外。

### 決策 2：空段、孤兒時間碼改成現象

`SEVERITY` 裡這兩項從 `ERROR` 改成 `NOTICE`。影響：

- 翻譯訓練YAML：不變（現象一樣不匯出）。
- exit code：這 45 筆不再算錯誤，錯誤從 3269 筆變 3224 筆。語料裡還有其他錯誤，exit code 仍是非 0。
- 校對表：照決策 1 不列。
- `KIND_WHY` 的說明不改，只改嚴重度。

`corpus-export` spec「exit code」的 scenario 原本用「海岸 2 的孤兒時間碼」當錯誤的例子，改用「秀姑巒第 20 段詞素翻譯的詞比詞素切割少」。

### 決策 3：問題表與第 7 章照 feature 的固定順序

排序不看筆數，照 `features/分析報告.feature`「每一種問題的嚴重度，且照以下先後排序」那張表的先後（使用者決定）。那張表直接列出報告上的問題名稱，「族語原句與詞素切割不符」列的是 6 個小類，以後要調整順序只改 feature。

程式的做法：

- `entry.py` 的 `SEVERITY` 照 feature 的順序排（`IssueKind` 的定義順序不動，排序只看 `SEVERITY`）；6 個小類的順序也照 feature，`parser.MISMATCH_WHY` 跟著重排。step 檢查兩邊順序一致。
- `report.py` 新增一個排序函式（例如 `ordered_labels(issues)`）：依 `SEVERITY` 的順序走過每一種問題，「族語原句與詞素切割不符」展開成 `MISMATCH_WHY` 的 6 個小類，只留這次有發生的。
- `kind_table()` 用它產生「編號、問題、嚴重度、筆數」四欄，編號從 1 起；`kinds_section()` 用同一份清單當小節順序，拿掉「不符的小類集中放最後」的特例。第 7 章小節的章號由 `number_headings()` 自動編，兩邊順序一樣，所以「7.N」對應表上的「N」。
- 表格上方寫一句說明，告訴讀者編號對應第 7 章的第幾節。

**替代方案 A**：依嚴重度、再依筆數排（原本的設計）。缺點是每次重跑順序可能變，開會時「第 7.3 節」指的東西不固定。

**替代方案 B**：表上直接寫「7.3」。缺點是要知道第 7 章的章號，章節一增減就錯，所以只寫 N。

### 決策 4：總覽的嚴重度對應表放在筆數下面

總覽的順序：檔數、段數、匯出段數（改稱「已匯出翻譯訓練YAML」）、四級筆數 → 嚴重度對應表（決策 1 的表，加一句說明）→ 問題表。對應表是固定文字，由程式產生，不從資料計算。

統計表依 CLAUDE.md 的「統計欄位的定義」，在表格上方寫明「筆數」怎麼算：段層級的問題一段同一種只記一筆（所以筆數就是段數）；孤兒時間碼沒有段，以時間碼計；時間碼格式混用、時間碼單位不明以檔案計。因為沒有任何一種問題的段數與筆數不同，問題表只列「筆數」一欄。

### 決策 5：刪掉的章節與程式

報告：

| 刪掉的 | 程式 |
|---|---|
| 開頭「標記清單：`…ods`」 | `run()` 不再讀 ODS，`--ods` 參數拿掉 |
| 語料格式說明的目錄↔sheet 對應 | `format_section()` 的 `sheet_names` 參數與那一節拿掉 |
| 問題明細 | `run()` 不再呼叫 `report.detail_section()`；沒有其他呼叫者就刪掉函式 |
| 討論 | 刪 `todo_section()` |
| 老師標要討論的項目、老師確認過、不是錯誤 | 刪 `proof_chapters()`、`report.teacher_discuss_section()`、`report.confirmed_section()` |

刪掉這兩章後，讀回校對表時的提醒（判斷欄寫錯字、判斷互相矛盾）改列在「校對流程」一節的最後；沒有提醒就不寫。`Proof.confirmed`、`Proof.discussed` 沒有人用了，一起刪掉，只留校對表的 rows。

ODS 相關的 `markers.py` 仍有 `features/構詞判定.feature`（草稿）的 step 與 `rules.py` 在用，這次不刪。

docx／txt：

- 刪 `scripts/check_docx_txt.py`、`tests/test_check_docx_txt.py`、README 的使用說明。
- 刪 `scripts/smkul/pairing.py`、`tests/smkul/test_pairing.py`。`split_kind()` 搬到 `scripts/smkul/languages.py`（它本來就在處理族別、語言別），`validate_glossing.py`、`proofreading.py` 改從那裡 import；它的測試搬到 `tests/smkul/test_languages.py`。
- 刪 `docx2text.docx_comments()` 與相關常數、測試。保留「docx 內文不含審閱註解」的測試（corpus-parsing 的 requirement 還在）。
- 刪 `IssueKind` 裡 docx／txt 比對專用的 4 種：缺檔、檔名不一致、段數不同、內容差異，連同 `SEVERITY`、`KIND_WHY` 的項目。
- `report.py` 裡只給 docx 報告用的部分（例如審閱註解章），沒有呼叫者就刪掉。
- 報告的「翻譯訓練YAML 來源說明」保留，說明翻譯訓練YAML 由 docx 產生；刪掉跟 txt 比較的理由，改成引用會議決議（案由一「以 docx 為主」）。

`openspec/specs/docx-txt-consistency/` 在封存時整份刪除；`corpus-export` 的 Purpose 在封存時直接改寫主 spec，拿掉「請對方處理」專章。

### 決策 6：「翻譯訓練YAML」只改說法

報告的總覽、第 3 章標題（改成「翻譯訓練YAML 輸出」）、校對流程一節、spec 的描述都改稱「翻譯訓練YAML」，第一次出現時附上檔名 `kithann/out/corpus.yaml`。程式的變數名、模組名（`yamlout.py`）、檔名、key 都不改。

### 決策 7：嚴重度規則的正本是 `features/分析報告.feature`

嚴重度的資訊以前會散在三個地方：spec 的文字、`entry.py` 的 `SEVERITY`、報告的總覽。只改一邊就會對不上，而且沒人發現。所以：

- **正本**：`features/分析報告.feature`。對應表、每一種問題的嚴重度與先後順序（也是問題表與第 7 章的順序）、報告的章節都寫在這裡，跟其他規則一樣「feature 是規格，程式後壁才綴」。
- **spec**：`corpus-export` 只寫行為原則，名單與排序細節指向這份 feature，不重抄。
- **step**（`features/steps/分析報告.py`）檢查程式有沒有照 feature 跑：

| Scenario | step 檢查什麼 |
|---|---|
| 嚴重度決定三種產出 | 每一級各造一段只有一筆該級問題的段：`Entry.is_clean()` 跟「翻譯訓練YAML」欄一致；`kinds_section()` 有舉例；該級在不在 `proofreading.PROOFREAD_SEVERITIES` 跟「請老師校對」欄一致；`overview()` 的對應表跟 feature 的表一字不差 |
| 每一種問題的嚴重度 | 表跟 `entry.SEVERITY`（「族語原句與詞素切割不符」展開成 `MISMATCH_WHY` 的小類）雙向比對，內容與順序都一樣；`IssueKind` 沒有表外的種類；用每一種問題各造一筆，`report.kind_table()` 的列與 `kinds_section()` 的小節順序都跟表一樣 |
| 報告的章節 | 用 `tests/data/最小範例.docx` 在暫存資料夾跑一次 `run()`，`##` 章名依序跟表一樣，暫存的輸出資料夾裡沒有 `docx_txt_report.md` |

為了讓 step 不碰真的 `kithann/out/`，`run()` 與 `report.write()` 加一個輸出資料夾的參數，預設仍是 `kithann/out`。

**替代方案**：寫一支 unittest 去讀 spec 的 markdown 比對 `SEVERITY`。缺點是 spec 的句子格式不固定，解析容易壞；feature 的表格本來就是 behave 給 step 讀的。

### 決策 8：三個問題改名，詞素切割放前面

| 原本 | 改成 |
|---|---|
| 詞素翻譯的詞比詞素切割少 | 詞素切割的詞比詞素翻譯多 |
| 詞素翻譯的詞比詞素切割多 | 詞素切割的詞比詞素翻譯少 |
| 符號的種類不一樣 | 詞素切割和詞素翻譯的符號不一樣 |

規則：問題名稱同時提到兩行時，詞素切割一律放在詞素翻譯前面（跟語料的行序一樣）；「詞素切割沒有切，詞素翻譯有切」「詞素切割有切，詞素翻譯沒有切」本來就符合。

只改 `IssueKind` 的值（報告、校對表看得到的名稱）與 `KIND_WHY` 的說明；常數名稱（`GLOSS_FEWER`、`GLOSS_MORE`、`SYMBOL_KIND_DIFF`）不改，因為意思沒變，改了只會擴大 diff。`rules.check_correspondence()` 回傳的是 `IssueKind` 的值，跟著變；`features/詞素切割與詞素翻譯對應.feature` 的 Then 已經改成新名稱，step 不用改。

老師已經交回的判斷：問題 ID 由問題種類的值算出來，改名後 ID 會變，這三類舊的判斷會移到「已不存在的紀錄」分頁（判斷與備註不會不見）。

## Risks / Trade-offs

- [第 7 章的小節順序變了] → 順序固定寫在 feature，之後要調整只改 feature，step 會檢查程式跟上。
- [舊報告、會議紀錄裡的「第 7.x 節」、「第 8 章問題明細」會對不上] → 報告開頭有更新日期，可以分新舊；這是使用者要的刪減。
- [`kithann/out/docx_txt_report.md` 舊檔還在，可能被誤用] → 規劃時已經刪掉（2026-10-31）；程式之後不會再產生。
- [孤兒時間碼、空段改成現象後，不再出現在校對表，萬一有人想補內容就沒有管道] → 報告第 7 章仍舉例；使用者決定這兩類老師不需處理（會議案由八）。
- [刪掉 `--ods` 參數，若有人的腳本還帶這個參數會出錯] → 專案內只有 README 提到，一起改；這個參數只影響已刪的那一節。

## Migration Plan

照 tasks 的順序改完、跑完測試後重新產生報告與校對表。`kithann/校對/` 裡老師已經交回的判斷不受影響；嚴重度改成現象的那幾筆，ID 對不到這次任何一列，會出現在校對表的「已不存在的紀錄」分頁，判斷與備註不會不見。
