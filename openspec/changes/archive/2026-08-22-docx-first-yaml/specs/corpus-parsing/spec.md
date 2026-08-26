# corpus-parsing Delta

## ADDED Requirements

### Requirement: 語料來源為 docx

Parser SHALL 以 `kithann/giliau/**/*.docx` 為語料來源，每個 `<w:p>` 段落視為一行，段落內的 `<w:br>` 視為換行、`<w:tab>` 視為一個空白。審閱註解的本文（`word/comments.xml`）與錨點標記（`commentRangeStart/End`、`commentReference`）SHALL NOT 出現在內文。txt 不再是語料來源。

#### Scenario: docx 內文不含註解

- **WHEN** 讀東排灣 2（26 條審閱註解）的 docx
- **THEN** 取得的內文行沒有任何 `[字母]` 錨點，也沒有註解本文行

#### Scenario: 只有 docx 的檔案也進語料

- **WHEN** 太魯閣 2 只有 docx、沒有 txt
- **THEN** 該檔照常解析，進入報告與 YAML

#### Scenario: 追蹤修訂視同已接受

- **WHEN** 布農巒群 2 第 1 組 gloss 段落含一處 `<w:ins>` 插入「記」
- **THEN** 取得的內文為 `主題標記=語氣詞`，`<w:del>` 的刪除文字不取

## MODIFIED Requirements

### Requirement: 組結構辨識

Parser SHALL 把 docx 段落序列切成「組」，每組含編號、時間碼、內文行（標準為四行：族語原文、構詞切分、gloss、華語翻譯）。組界 SHALL 以編號行+時間碼行辨識，不依賴組間空行——docx 段落序列通常沒有組間空行（中排灣 1 docx 1606 行 vs txt 1825 行）。編號與時間碼在同一行（如東排灣 1 的 `1. 0:00:00.000,0:00:01.480`）或編號獨立一行，兩種 SHALL 都支援。

#### Scenario: 組間缺空行

- **WHEN** 解析中排灣 1 的 docx，第 1 組翻譯行之後直接接第 2 組的編號行
- **THEN** parser 正確切出兩組，不視為錯誤

#### Scenario: 編號與時間碼同行

- **WHEN** 解析東排灣 1（編號與時間碼同行）
- **THEN** parser 解析出編號與時間碼，結果與編號獨行的檔案同構

### Requirement: 字元正規化

Parser SHALL 執行：移除 BOM（U+FEFF；docx 來源通常沒有，規則保留）、全形 `＝`（U+FF1D）轉半形 `=`（如南排灣 4 的 `’u＝izua`/`我.屬格＝處所.那裡`）、`'` 一律統一為 U+0027（秀姑巒同檔混用 U+0027 與 U+2019 `'`）、切分行與 gloss 行內的 en-dash `–` 轉半形 `-`（秀姑巒第 79 組 `PI–書-處焦`、海岸 1 第 71 組 `SA–重疊`；時間碼行的 `–` 是合法分隔符，不轉）、連續空白摺疊成一個（docx 的 `<w:tab>` 已轉成單一空白，仍可能連續）。正規化為靜默轉換，不算錯誤；每項 SHALL 計數，筆數為 0 也列出。

#### Scenario: 全形等號

- **WHEN** 解析南排灣 4 的切分 token `’u＝izua`
- **THEN** 解析結果為 `'u=izua`（半形 `=`、U+0027），附著詞切分照常運作

#### Scenario: gloss 行內 en-dash

- **WHEN** 解析秀姑巒第 79 組的 gloss token `PI–書-處焦`
- **THEN** 解析結果為 `PI-書-處焦`，與切分 token `pi-codad-an` 的符號呼應檢查照常通過

#### Scenario: 寬空白已成單一空白

- **WHEN** 解析中排灣 1 第 1 組 docx 段落 `aicu   a  tucu  a  qadav`（tab 已轉空白，仍有連續空白）
- **THEN** token 化得到 `aicu`、`a`、`tucu`、`a`、`qadav` 五個 token
