## RENAMED Requirements

- FROM: `### Requirement: 逐組結構比對`
- TO: `### Requirement: 逐段結構比對`

## MODIFIED Requirements

### Requirement: 逐段結構比對

配對成功的檔案 SHALL 逐段比對：兩邊以相同規則解析成段後，比對段數、編號、時間碼、四行內容。比對 SHALL 忽略空白差異（空格、tab 的數量與種類、行內折行位置），其他任何差異（缺段、文字不同、時間碼不同）SHALL 列為錯誤並定位到段編號。

#### Scenario: 只有空白不同

- **WHEN** 比對中排灣 1 第 1 段：docx 段落為 `aicu a tucu a qadav avan cu`（單一空格），txt 同行用寬空白對齊欄位
- **THEN** 該段視為一致，不列錯誤

#### Scenario: 內容有差異

- **WHEN** docx 與 txt 某段的詞素切割行文字不同
- **THEN** 報告列出該檔該段的差異錯誤，並顯示兩邊內容

### Requirement: 逐行比對而非比對組裝後的欄位

docx 與 txt 的內容比對 SHALL 逐行比對正規化後的內文行（含行數），不可比對組裝後的四行欄位——一邊組裝成功、另一邊失敗時，欄位會是空字串，產生誤導的差異訊息。

#### Scenario: 一邊組裝失敗

- **WHEN** 比對布農郡群 3 第 310 段：txt 有 6 行（多兩行註解本文）、docx 有 4 行
- **THEN** 報告顯示「內文行數不同：txt 6 行，docx 4 行」與逐行差異，而非「族語原句 txt 空的」
