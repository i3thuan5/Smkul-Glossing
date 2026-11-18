## Why

對方會陸續交付新版語料，一版一個目錄（舊版 `kithann/giliau/`，2026-11-18 交付 `kithann/語料標註語料_20261118/`）。程式、測試、規格卻把 `kithann/giliau` 寫死當預設值，結果新版到了，程式還是靜靜地跑舊版。語料目錄應該每次都由執行的人指定，不讓程式自己猜。

## What Changes

- **BREAKING（CLI）** `python -m scripts.validate_glossing` 的語料目錄改成必填，沒有預設值；沒指定時印出用法並以非 0 結束。（程式、README、測試已先改好，這次補規格。）
- 全語料冒煙測試 `tests/test_corpus_smoke.py` 改用環境變數 `SMKUL_CORPUS` 指定語料目錄；沒設就 skip，skip 訊息寫明「沒指定語料目錄」。
- 冒煙測試的斷言只留**換版也要成立的通用性質**：每個 docx 都解析得出段、每段都有時間碼、已知的問題種類都偵測得到、自動處理都有記錄。拿掉綁死某一版語料的斷言：「剛好 31 個檔案」、「重複標註 = 13」、「時間碼單位不明 = 2」、「時間碼格式混用 = 1」、「重複標註都在南排灣 4」、「海岸 2 有 12 個孤兒時間碼」、段數的固定下限。
- `scripts/smkul/markers.py` 拿掉 `ODS_PATH` 預設值，`read_sheets()`、`load_marker_lists()` 的路徑改成必填。這個預設值本來就沒有人用（報告不讀標記清單；單元測試傳 `tests/data/標記清單範例.ods`；behave 直接讀 Given 表格）。
- **不在這次範圍**：新版的標記清單是 `.xlsx`，`markers.py` 只讀 `.ods`。構詞判定暫停維護，報告與 YAML 用不到標記清單，所以這次不支援 xlsx。

## Capabilities

### New Capabilities

（無）

### Modified Capabilities

- `corpus-parsing`：「語料來源為 docx」不再寫死 `kithann/giliau/**/*.docx`，改成「執行時指定的語料目錄底下的所有 docx」，沒指定時程式停止。

## Impact

- 程式：`scripts/validate_glossing.py`（已改）、`scripts/smkul/markers.py`。
- 測試：`tests/test_validate_glossing.py`（已加「沒指定語料目錄就停止」）、`tests/test_corpus_smoke.py`。
- 文件：`README.md`（已改 CLI 用法；要補冒煙測試的 `SMKUL_CORPUS` 用法）。
- CI：CI 本來就沒有語料，冒煙測試一直是 skip，不受影響。
- 輸出：`kithann/out/` 的內容不變，只是產生時要明確指定語料目錄。
