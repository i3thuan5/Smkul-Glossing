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

`kithann/giliau/` 底下是對方提供的族語語料。語料一律以 docx 為準(2026.09 會議案由一),txt 不讀。程式檢查語料、產生報告,產出都放 `kithann/out/`(不進版控)。

標註規則寫在 [features/](features/) 的 `*.feature`,一條規則一份,程式與規格用同一份。嚴重度與三種產出(翻譯訓練YAML、報告、校對表)的關係寫在 [features/分析報告.feature](features/分析報告.feature)。語料的格式(四行結構、時間碼、切割符號、特殊符號、外來語標籤)寫在 `kithann/out/Glossing驗證報告.md` 的「語料格式說明」章,每次跑程式重新產生。

### 驗證標注並匯出翻譯訓練YAML

```bash
python -m scripts.validate_glossing
```

檢查每一段的詞素切割行與詞素翻譯行對不對得起來(詞數與切割符號),並用族語原句逐字檢查詞素切割。通過的段匯出到翻譯訓練YAML `kithann/out/corpus.yaml`(單一檔案,華語 key,結構是 檔案 → 段,每段放族語原句、詞素切割、詞素翻譯、華語翻譯四行,每個檔案另附語言別代號),報告寫到 `kithann/out/Glossing驗證報告.md`,需要族語老師校對的問題寫到 `kithann/out/校對表/`(一個語言別一個 xlsx)。老師填好的校對表放進 `kithann/校對/`,重跑時會讀回來。有「錯誤」時 exit code 非 0。

可以指定語料目錄:

```bash
python -m scripts.validate_glossing 別的語料目錄
```

### 程式結構

- `scripts/smkul/` 共用套件:`parser.py`(語料解析)、`docx2text.py`(docx 抽文字)、`markers.py`(讀 ODS 標記清單,只給 `構詞判定.feature` 草稿用)、`rules.py`(詞素切割與詞素翻譯的對應)、`languages.py`(族別、語言別與語言別代號查表,CSV 在 `scripts/smkul/data/`)、`yamlout.py`(翻譯訓練YAML 匯出)、`proofreading.py`(校對表)、`xlsx.py`(xlsx 讀寫)、`report.py`(報告)
- `tests/` 用 `python -m unittest`;`tests/data/` 的 fixture 都取自真語料
- 語料不在版控內,全語料的冒煙測試找不到語料時會自動 skip
- `features/` 是 behave 的 feature,用來跟語料提供方討論判定結果(例如詞素切割與詞素翻譯怎麼算對得起來)。`構詞判定.feature` 是暫停維護的內部草稿,報告與 YAML 不使用。跑 `tox -e behave`;格式檢查是 `npx gherkin-lint`(CI 也會跑)
