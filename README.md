# PangBoo

專案開發枋模

## 建立 Python virtual environment

```bash
python -m venv venv
```

## 載入 Python virtual environment

Ta̍k-kái攏ài開，才來開發。

```bash
source venv/bin/activate
```

## 安裝tox

tox是tī本機走test用--ê。

```bash
pip install tox
```

## 更新套件版本

`requirements.in`是記專案有直接用ê第三方套件。`requirements.txt`是管kui專案全部第三方套件koh對應版本，保證開發、CI試驗、上線版本一致。

1. 請先 `pip install pip-tools` tàu [pip-tools](https://github.com/jazzband/pip-tools) 自動管理套件版本。
2. 手動更新`requirements.in`。
3. 揀一款指令自動更新套件版本。

      ```bash
      # 有必要--ê才更新
      pip-compile
      # 盡量更新
      pip-compile --upgrade
      ```

4. 檢查`requirements.txt`更新狀態。

## 族語語料檢查

`kithann/giliau/` 底下是對方提供的族語語料(docx 與 txt 成對)。兩支程式檢查語料、產生報告,產出都放 `kithann/out/`(不進版控)。

標註格式與符號規則整理在 [docs/glossing-rules.md](docs/glossing-rules.md)。

### 檢查 docx 與 txt 是否一致

```bash
python -m scripts.check_docx_txt
```

逐組比對配對成功的 docx 與 txt(空白差異忽略),另外抽出 docx 的審閱註解。產出 `kithann/out/docx_txt_report.md`。有錯誤時 exit code 非 0。

### 驗證 glossing 並匯出 YAML

```bash
python -m scripts.validate_glossing
```

檢查每一組的 token 對齊、切分符號呼應、構詞標記是否在原語會清單內,並用原文逐字檢查切分。通過的組匯出到 `kithann/out/corpus.yaml`(單一檔案,華語 key,結構是 檔案 → 句 → 詞 → 詞素),不通過的列進 `kithann/out/glossing_report.md`。有錯誤時 exit code 非 0。

兩支程式都可以指定語料目錄:

```bash
python -m scripts.validate_glossing 別的語料目錄
```

### 程式結構

- `scripts/smkul/` 共用套件:`parser.py`(txt 解析)、`docx2text.py`(docx 抽文字)、`pairing.py`(配對與比對)、`markers.py`(讀 ODS 標記清單)、`rules.py`(glossing 驗證)、`yamlout.py`(YAML 匯出)、`report.py`(報告)
- `tests/` 用 `python -m unittest`;`tests/data/` 的 fixture 都取自真語料
- 語料不在版控內,全語料的冒煙測試找不到語料時會自動 skip
- `features/` 是 behave 的 feature,用來跟語料提供方討論判定結果(例如詞根/詞綴怎麼判)。跑 `tox -e behave`;格式檢查是 `npx gherkin-lint`(CI 也會跑)
