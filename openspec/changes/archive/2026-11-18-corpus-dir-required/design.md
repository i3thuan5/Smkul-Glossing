## Context

`kithann/giliau` 寫死在三個地方：

| 位置 | 用途 | 現況 |
| --- | --- | --- |
| `scripts/validate_glossing.py` | 產生報告、YAML、校對表的語料目錄 | 已改成必填（這次補規格） |
| `tests/test_corpus_smoke.py` | 全語料冒煙測試的語料目錄 | 寫死 `BASE`，找不到就 skip |
| `scripts/smkul/markers.py` | 《常用構詞標記清單》ODS 的預設路徑 | `ODS_PATH` 當 `read_sheets()`、`load_marker_lists()` 的預設值 |

`kithann/` 不進版控，CI 沒有語料。冒煙測試的斷言有一半是舊版語料的「指紋」：用新版語料跑，「剛好 31 個檔案」就失敗（49 ≠ 31）；其他數字這次剛好沒變，是因為新版是舊版再加新檔，對方之後修語料就會變。

`markers.py` 的預設值沒有人用：`validate_glossing.py` 不讀標記清單；`tests/smkul/test_markers.py`、`test_rules.py` 傳 `tests/data/標記清單範例.ods`；`features/steps/構詞判定.py` 用 `MarkerList.from_rows()` 讀 Given 表格。

## Goals / Non-Goals

**Goals:**

- 程式與測試都不再自己挑語料目錄，每次都要執行的人指定。
- 冒煙測試換版不用改，只驗程式的性質，不驗某一版語料的內容。

**Non-Goals:**

- `markers.py` 支援 `.xlsx` 標記清單。構詞判定暫停維護，等重新啟用再說。
- 自動找 `kithann/` 底下最新一版語料。
- 保存各版語料的預期數字（版本基準表）。

## Decisions

### 冒煙測試用環境變數 `SMKUL_CORPUS`

```bash
SMKUL_CORPUS=kithann/語料標註語料_20261118 python -m unittest tests.test_corpus_smoke
```

沒設 `SMKUL_CORPUS` 就 skip，訊息「沒指定語料目錄（環境變數 SMKUL_CORPUS）」；有設但目錄不存在 SHALL 讓測試失敗（不是 skip），免得打錯字卻以為測過了。相對路徑以專案根目錄為準，跟 CLI 一樣在專案根目錄執行。

- 替代方案：自動挑 `kithann/語料標註語料_*` 最新的一版。不採用：又變成程式自己猜，跟「每次都要問」相反。
- 替代方案：自訂 unittest 參數。`python -m unittest` 不方便帶自訂參數，tox 的 `{posargs}` 也是傳給 unittest，環境變數最簡單。

### 冒煙測試只留通用性質

| 留下 | 拿掉 |
| --- | --- |
| 至少有一個 docx，每個 docx 都解析得出段 | 剛好 31 個檔案 |
| 每段都有開始與結束時間碼 | 段數 > 7000、過半通過 |
| 已知的問題種類都偵測得到（> 0） | 重複標註 = 13、單位不明 = 2、混用 = 1 |
| 自動處理有記錄（長句換行重組、引號、en-dash > 0；BOM = 0） | 重複標註都在南排灣 4 |
| | 海岸 2 有 12 個孤兒時間碼 |
| | 長句換行重組 > 800 |

「已知的問題種類都偵測得到」是全語料層級的檢查：對方把所有黏行都修好，這條就會紅。目前兩版都還有，先保留；真的修好了再拿掉那一種，那時候是好消息。

「BOM = 0」留著，因為這是 docx 抽文字的性質（docx 內文不會有 BOM），不是語料的內容。

- 替代方案：通用性質加上版本基準表（目錄名 → 預期數字）。不採用：每次換版都要維護，使用者決定只留通用性質。

### `markers.py` 路徑必填

拿掉 `ODS_PATH` 常數，`read_sheets(path)`、`load_marker_lists(path)` 的 `path` 改成必填參數。呼叫端本來就都有傳，不用改。

## Risks / Trade-offs

- [冒煙測試抓不到「同一版語料，數字悄悄變了」的回歸] → 報告本身有各問題的筆數，換程式時拿新舊報告比對就看得到；需要的話之後再加版本基準表。
- [開發者忘了設 `SMKUL_CORPUS`，冒煙測試一直 skip] → skip 訊息寫明要設什麼；README 寫用法。
- [新版的標記清單是 xlsx，`kithann/giliau/` 刪掉後就沒有 ODS] → 不影響報告與 YAML；構詞判定重新啟用時再處理 xlsx。
