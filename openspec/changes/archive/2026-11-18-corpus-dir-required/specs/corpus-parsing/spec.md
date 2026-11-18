## MODIFIED Requirements

### Requirement: 語料來源為 docx

Parser SHALL 以**執行時指定的語料目錄**底下的所有 docx（`<語料目錄>/**/*.docx`）為語料來源，例如 `kithann/語料標註語料_20261118/`。語料目錄 SHALL NOT 有預設值：對方會陸續交付新版語料，一版一個目錄，每次執行都要明確指定用哪一版；沒指定時程式 SHALL 印出用法並以非 0 結束，SHALL NOT 自己挑一個目錄來跑。每個 `<w:p>` 段落視為一行，段落內的 `<w:br>` 視為換行、`<w:tab>` 視為一個空白。審閱註解的本文（`word/comments.xml`）與錨點標記（`commentRangeStart/End`、`commentReference`）SHALL NOT 出現在內文。txt 不再是語料來源。

#### Scenario: 沒指定語料目錄就停止

- **WHEN** 執行 `python -m scripts.validate_glossing`，沒有帶語料目錄
- **THEN** 程式印出用法、以非 0 結束，不產生報告、YAML 與校對表

#### Scenario: 指定新版語料目錄

- **WHEN** 執行 `python -m scripts.validate_glossing kithann/語料標註語料_20261118`
- **THEN** 只讀這個目錄底下的 docx，舊版 `kithann/giliau/` 的檔案不會混進來

#### Scenario: docx 內文不含註解

- **WHEN** 讀東排灣 2（26 條審閱註解）的 docx
- **THEN** 取得的內文行沒有任何 `[字母]` 錨點，也沒有註解本文行

#### Scenario: 只有 docx 的檔案也進語料

- **WHEN** 太魯閣 2 只有 docx、沒有 txt
- **THEN** 該檔照常解析，進入報告與 YAML

#### Scenario: 追蹤修訂視同已接受

- **WHEN** 布農巒群 2 第 1 段詞素翻譯段落含一處 `<w:ins>` 插入「記」
- **THEN** 取得的內文為 `主題標記=語氣詞`，`<w:del>` 的刪除文字不取
