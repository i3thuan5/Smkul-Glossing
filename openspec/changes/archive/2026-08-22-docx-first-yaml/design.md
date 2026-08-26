# Design: docx-first-yaml

## Context

動機見 proposal.md。關鍵現況：

- `docx2text.docx_paragraphs()` 已能把 docx 變成與 txt 同構的行序列（`<w:tab>` → 空白、`<w:br>` → 換行），只抓 `<w:t>`，所以註解本文與錨點天生進不來；`<w:delText>` 也不抓，等於追蹤修訂全部接受（布農巒群 2 有 1 處 `<w:ins>`）。
- 實測 docx 段落與 txt 的差別只有兩種：沒有組間空行（中排灣 1：1606 行 vs 1825 行）、寬空白變單一空白。組界本來就靠編號＋時間碼，不受影響。
- 31 個 docx / 30 個 txt；太魯閣 2 只有 docx，魯凱霧台 3 兩邊檔名不同。
- `rules.split_morphemes` 把 `=` 後段一律標 `CLITIC`，`pick_root` 跳過 `CLITIC` 候選，所以前附著詞（`tja=`、`'u=`）的詞根永遠判錯；這是 872 筆「標記不在清單」裡約 275 筆的來源。**照 feature 的判斷方法（靠 gloss 查表反推詞根）實作以後，這一類自己就對了**，不必另外修。
- 現有 feature/steps 架構：每個 scenario 自帶資料，不讀語料、不讀 ODS，`behave --no-skipped` 在 tox 跑。
- `scripts/` 的 Python 還沒被 review 過，可以大改、可以重寫；feature 與 steps 才是合約。

## Goals / Non-Goals

**Goals：**

- 單一語料來源（docx），整條註解殘留處理鏈歸零。
- 「標記不在清單」不再擋匯出，改成詞素層的 `無法判斷`，讓 YAML 多收回幾百組。
- 報告瘦身：例子與規則只在 feature 一份，報告指過去。
- feature → steps → 程式 → behave 綠燈的順序。

**Non-Goals：**

- 不解析 docx 顏色層、不處理 `<w:del>` 的保留。
- 註解條數、內容不進 YAML。
- 不刪 `check_docx_txt.py`，它降為歷史核對工具。

## Decisions

### D0：程式可以重寫，feature 是合約

`scripts/` 尚未 review，不需要保留現有函式名或模組切法；唯一要守的是 `features/*.feature` 與 steps 的介面（`parse_text`、`normalize_text`、`build_words`、`markers_of` 這幾個 steps 會 import 的進入點，名字可改但 steps 要跟著改）、CLAUDE.md 的風格（`for` 置前、華語註解、79 字元）、以及 `docs/glossing-rules.md` 的規則。模組仍放 `scripts/smkul/`，CLI 仍是 `python -m scripts.validate_glossing` / `python -m scripts.check_docx_txt`。

### D1：語料只有 docx 一個來源，parser 吃行序列

語料走訪只認 `*.docx`；docx → 段落行序列 → parser，中間沒有 txt、沒有註解相關的任何步驟。txt 只在 `check_docx_txt.py` 的歷史核對裡出現。理由：單一來源，報告的「路徑」欄與配對邏輯不用雙軌。

### D2：`無法判斷` 是 `Attachment` 的一個值，不是 `IssueKind`

連帶把 `Attachment` 從 5 個值細分成 8 個（詞根/前綴/後綴/環綴/中綴/依附詞/重疊/無法判斷）——`features/構詞判定.feature` 的「判斷方法」2a–2d 本來就要求這個粒度，程式一直沒跟上，整份 feature 因此全紅。

`Attachment` 加 `UNDECIDED = "無法判斷"`。`check_markers()` 查不到時不產生 `Issue`，改把該 `Morpheme.attachment` 設成 `UNDECIDED`，並回傳 `(gloss, sheet)` 清單給報告統計（與既有的 `uncertain` 同型）。`IssueKind.MARKER_NOT_IN_LIST` 刪除。理由：使用者定案「只有這個現象就可以進 YAML」，所以它不是錯誤，放在詞素上才會出現在 YAML。替代方案（保留 IssueKind 但 severity 改 WARNING）還是會讓總覽把它當問題列，棄。

分類直接照 feature 判斷方法第 3 點的兩種情形：`不只一段沒被標成詞綴`（3b）、`每一段都被標成詞綴`（3c）。分類只用於報告統計，YAML 一律 `無法判斷`。

另外補一條 feature 已寫、程式漏掉的規則：**沒有任何切分符號的詞，整段就是詞根**（詞綴要有東西可黏才成立）。少了這條，`a`／連繫詞、`ta`／斜格 這種單詞會全部落進 3c，`無法判斷` 佔到 36.8%；補上以後降到 9.3%。

### D3：報告章節重排

```text
1 總覽（加「構詞無法判斷：N 個詞素，見第 7 章」）
2 依語別統計
3 YAML 輸出（由 docx 產生）
4 自動處理與比對政策（每項摘要＋筆數＋feature 指向；原 4、5 合併）
5 問題類型說明與例子（刪 6.2）
6 問題明細
7 構詞判斷困難（A/B/C 摘要＋統計表；原 8 章併入）
8 「不確定」標記統計（尾句加建議）
9 討論（刪 10.2，加一條指回第 7 章）
```

編號由 `report.number_headings()` 自動加，程式裡不寫死。自動處理章的 feature 指向用 `NormKind` → feature 檔名的對照表放在 `report.py`。

### D4：feature 先行

順序：`features/構詞判定.feature` 加 A/B/C 三條、刪 `features/註解殘留.feature`（排版分析、字元正規化既有的「組間缺空行」「多餘空白合併」已涵蓋 docx 段落的特徵，不加）；`features/steps/自動處理.py` 只拔註解殘留的三個 step，docx 段落的 scenario 沿用既有的「讀入這幾行」；`features/steps/構詞判定.py` 讓「（無法判斷）」對到 `Attachment.UNDECIDED`；然後才改程式。每條 feature 都要過 `npx gherkin-lint`。

### D5：apply 時的跳過規則

apply 過程中若某條 feature 覺得不合理（例子與規則矛盾、Then 寫不出來、與 CLAUDE.md 衝突），在 `tasks.md` 的「apply 時跳過」清單記一行（哪條、為什麼），該條先不處理，繼續做下一項，全部做完一次回報，不中途停。

### D6：標點

change 文件內文一律全形標點（CLAUDE.md 新增的規定）；openspec 結構標頭與反引號內保留半形。

## Risks / Trade-offs

- [docx 段落與 txt 仍有未發現的差別，行類型判斷漂移] → 改完後跑全語料，把總覽各問題類型的筆數與現在的報告逐項比對，差異逐項解釋；tests 的 fixture 從 `tests/data/*.docx` 讀。
- [`無法判斷` 讓幾百組進 YAML，下游以為構詞已定] → YAML 欄位值本身就是 `無法判斷`，報告第 7 章明講。
- [`詞數不同` 這條新規格讓 483 組從通過變成不符] → 這是 `features/原文切分比對.feature`「只差空白，先算不通過」已經定案的規格，程式本來沒跟上；報告的問題類型表會多這一列。
- [太魯閣 2 首次進語料，可能冒出新格式] → 未知行歸「孤立雜訊行」，不 crash。

## Open Questions

（無。註解數不進 YAML、A 類不修、報告只放摘要三題已定案。）
