# docx-txt-consistency Specification

## Purpose

核對對方交付的 docx 與 txt 是否一致:檔案配對完整、逐組結構比對內容相同(空白差異忽略),差異列入報告。語料已經一律由 docx 產生(見 corpus-parsing),所以這是歷史核對——缺檔與檔名不一致只是提醒,不影響語料。

## Requirements

### Requirement: 檔案配對檢查

檢查 SHALL 以「同目錄同檔名（不含副檔名）」配對 docx 與 txt。只有單邊存在的檔案 SHALL 列為提醒（不是錯誤，因為語料以 docx 為準）：缺 docx 的 txt 請對方補 docx；缺 txt 的 docx 照常進語料。已知的檔名不一致配對（魯凱霧台 3：`包鳯嬌…月桃文化及製作上集.txt` vs `包鳳嬌…月桃的文化及製作_上集.docx`）SHALL 列為提醒，語料以 docx 檔名為準。

#### Scenario: 缺 txt

- **WHEN** 太魯閣 2 只有 docx、沒有 txt
- **THEN** 報告列出「缺 txt」提醒，該檔照常進語料

#### Scenario: 檔名異體字不一致

- **WHEN** 魯凱霧台 3 的 txt 與 docx 檔名不同（鳯/鳳、標題微差）
- **THEN** 報告列出「檔名不一致」提醒，YAML 的路徑用 docx 的檔名

### Requirement: 逐組結構比對

配對成功的檔案 SHALL 逐組比對:兩邊以相同規則解析成組後,比對組數、編號、時間碼、四行內容。比對 SHALL 忽略空白差異(空格/tab 的數量與種類、行內折行位置),其他任何差異(缺組、文字不同、時間碼不同)SHALL 列為錯誤並定位到組編號。

#### Scenario: 只有空白不同

- **WHEN** 比對中排灣 1 第 1 組:docx 段落為 `aicu a tucu a qadav avan cu`(單一空格),txt 同行用寬空白對齊欄位
- **THEN** 該組視為一致,不列錯誤

#### Scenario: 內容有差異

- **WHEN** docx 與 txt 某組的構詞切分行文字不同
- **THEN** 報告列出該檔該組的差異錯誤,並顯示兩邊內容

### Requirement: docx 審閱註解要抽出來列入報告

docx 的審閱註解(`word/comments.xml`)SHALL 抽出來,依文件順序編字母(a、b、c…),連同作者、日期、內容列入報告的「請對方處理」章節。這些是對方自己標的待辦修改指示(如「加 完成貌」「數字要寫出來，才知道他講的是族語還是國語」「第一行分開」),會議上可逐條處理。實測 7 個 docx 共 110 條註解。

#### Scenario: 抽出註解

- **WHEN** 讀南排灣 4 的 docx(30 條註解)
- **THEN** 依文件順序取得每條註解的字母、作者、日期、內容,列入報告

#### Scenario: 沒有註解的 docx

- **WHEN** 讀沒有 `word/comments.xml` 的 docx
- **THEN** 回傳空清單,不報錯

### Requirement: 逐行比對而非比對組裝後的欄位

docx↔txt 的內容比對 SHALL 逐行比對正規化後的內文行(含行數),不可比對組裝後的四行欄位——一邊組裝成功、另一邊失敗時,欄位會是空字串,產生誤導的差異訊息。

#### Scenario: 一邊組裝失敗

- **WHEN** 比對布農郡群 3 第 310 組:txt 有 6 行(多兩行註解本文)、docx 有 4 行
- **THEN** 報告顯示「內文行數不同:txt 6 行,docx 4 行」與逐行差異,而非「族語 txt 空的」

### Requirement: docx 顏色標記層不比對但須提醒

docx 內的文字顏色/標亮(如太魯閣 1 的 35 處紅字、檔頭「橘色」註記)SHALL NOT 納入比對與解析。報告 SHALL 在「請對方確認」章節固定說明:docx 有顏色標記層、txt 無此資訊,需對方說明紅字意義與是否需要保留。

#### Scenario: 紅字不影響一致性

- **WHEN** docx 某詞素是紅字、txt 同位置文字相同
- **THEN** 該組視為一致,但報告的「請對方確認」章節含顏色標記層說明
