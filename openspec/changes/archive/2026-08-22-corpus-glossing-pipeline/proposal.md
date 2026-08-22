# Proposal: corpus-glossing-pipeline

## Why

對方提供的族語語料(`kithann/giliau/`,31 docx + 30 txt,約 7,400 組 glossing 標註)需要整理成結構化格式才能後續使用。語料格式不統一(四種時間碼格式、長句分段、純華語句多種表法)且含多種標註錯誤(黏行、缺 gloss、孤兒時間碼、符號不一致),需要程式化檢查,把可用的部份轉出,把有問題的部份整理成報告供會議上與對方逐項討論。語料之後還會持續交付,pipeline 必須可重複執行。

## What Changes

- 新增 `scripts/smkul/` 共用套件:txt 語料 parser、docx 文字抽取、ODS 構詞標記清單讀取、glossing 規則驗證、報告與 YAML 輸出。
- 新增 `scripts/check_docx_txt.py`:逐組結構比對 docx 與 txt 的一致性(空白差異忽略),差異列為錯誤。
- 新增 `scripts/validate_glossing.py`:驗證 txt 的 glossing 規則與符號,合規的組匯出到單一 YAML(拆到詞素/gloss 配對層),不合規的組列入報告並記錄原因。
- 新增 `docs/glossing-rules.md`:整理第二行(構詞切分行)的符號系統與規則文件。
- 新增 `tests/`:`python -m unittest` 測試(對齊 `tox -e test`)。
- 修改 `.devcontainer/devcontainer.json`:加入 Python 3.10 feature(現有容器只有 python3.12-minimal,無 pip/venv/完整 stdlib)。
- 修改 `requirements.in`:加入 `PyYAML`(docx/ODS 用 stdlib 解析,依 `kithann/採購安全說明書_v2.0.txt` 審查,詳 design D7)。

## Capabilities

### New Capabilities

- `corpus-parsing`:族語語料 txt 的解析——組(編號/時間碼/四行)結構辨識、四種時間碼格式、長句分段重組、檔頭註記、正規化(全形＝→半形、apostrophe 統一 U+0027、BOM)。
- `docx-txt-consistency`:docx↔txt 逐組結構比對,含檔案配對檢查(缺檔、檔名不一致)。
- `glossing-validation`:glossing 規則驗證——第二/三行 token 對齊、切分符號呼應、構詞標記查 ODS 各語言清單、錯誤分類。
- `corpus-export`:合規語料匯出單一 YAML(華語 key,詞素/gloss 配對結構)與 markdown 報告(含「請對方處理」專章、exit code)。

### Modified Capabilities

(無——本專案尚無既有 specs)

## Impact

- 新增程式碼:`scripts/`、`tests/`、`docs/glossing-rules.md`。
- 依賴:`requirements.in` 加 `PyYAML` 後重新 `pip-compile`。
- 開發環境:`.devcontainer` 需 rebuild 一次。
- CI(.travis.yml/tox)不需改動:`tox -e test` 既有的 `python -m unittest` 會自動 discover `tests/`;flake8 會檢查新程式碼。
- 語料檔案本身**不修改**——所有錯誤只進報告,由對方確認後重新交付。
