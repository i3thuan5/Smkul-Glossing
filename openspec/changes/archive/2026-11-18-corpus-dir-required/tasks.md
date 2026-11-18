## 1. CLI 語料目錄必填（已先做好）

- [x] 1.1 `scripts/validate_glossing.py` 拿掉 `BASE`，`base` 改成必填參數，說明文字的範例改成 `kithann/語料標註語料_20261118`
- [x] 1.2 `tests/test_validate_glossing.py` 加 `TestMain.test_沒指定語料目錄就停止`：`main([])` 丟 `SystemExit`，code 非 0
- [x] 1.3 `README.md` 的 CLI 用法改成要帶語料目錄，註明沒有預設值

## 2. 冒煙測試改用 `SMKUL_CORPUS`

- [x] 2.1 `tests/test_corpus_smoke.py` 的語料目錄改讀環境變數 `SMKUL_CORPUS`（相對路徑以專案根目錄為準）；沒設就 skip，訊息「沒指定語料目錄（環境變數 SMKUL_CORPUS）」；有設但目錄不存在，測試失敗、不 skip
- [x] 2.2 拿掉版本指紋的斷言：`test_三十一個檔案都解析得過` 改成「至少一個 docx，每個都解析得出段」並改測試名；刪 `test_段數`、`test_重複標註都在南排灣四`、`test_海岸二有十二個孤兒時間碼`；`test_已知的異常都找得到` 拿掉三個固定數字，只留「> 0」；`test_自動處理都有記下來` 的長句換行重組改成 `> 0`
- [x] 2.3 不設 `SMKUL_CORPUS` 跑 `python -m unittest tests.test_corpus_smoke`，確認是 skip，訊息正確
- [x] 2.4 `SMKUL_CORPUS=kithann/giliau` 與 `SMKUL_CORPUS=kithann/語料標註語料_20261118` 各跑一次，兩版都全綠
- [x] 2.5 `SMKUL_CORPUS=不存在的目錄` 跑一次，確認是失敗、不是 skip
- [x] 2.6 `README.md` 「程式結構」的冒煙測試說明補上 `SMKUL_CORPUS` 的用法

## 3. `markers.py` 路徑必填

- [x] 3.1 `scripts/smkul/markers.py` 拿掉 `ODS_PATH`，`read_sheets(path)`、`load_marker_lists(path)` 的 `path` 改成必填
- [x] 3.2 `grep -rn "ODS_PATH\|kithann.*giliau" scripts tests features` 沒有結果（順手把 `scripts/smkul/entry.py` 的 `Issue` docstring 從 `kithann/giliau/` 改成「語料目錄」）

## 4. 全部檢查

- [x] 4.1 `tox -e test`、`tox -e behave`、`tox -e flake8` 全綠
- [x] 4.2 `openspec validate corpus-dir-required` 通過
