## MODIFIED Requirements

### Requirement: glossing 報告的章節

驗證程式 SHALL 只產生一份報告 `kithann/out/Glossing驗證報告.md`（檔名跟報告標題一樣），SHALL NOT 產生 docx／txt 一致性報告。章節依序以 `features/分析報告.feature` 的「報告的章節」為準：總覽、依語言別統計、翻譯訓練YAML 輸出（含來源說明）、校對流程、語料格式說明、自動處理與比對政策、問題類型說明與例子、待討論：詞素切割的特殊符號。SHALL NOT 有問題明細、討論（請對方處理）、老師標要討論的項目、老師確認過、不是錯誤這幾章，也 SHALL NOT 有任何構詞資訊。

#### Scenario: 章節順序

- **WHEN** 產生報告
- **THEN** 報告的 `##` 章節依序是上面 8 章，章號由程式自動編

#### Scenario: 沒有刪掉的章節

- **WHEN** 產生報告
- **THEN** 報告裡沒有「問題明細」「討論」「老師標要討論的項目」「老師確認過、不是錯誤」，也沒有「標記清單」的檔名

#### Scenario: 報告沒有構詞資訊

- **WHEN** 語料有詞素判不出詞根，也有全大寫的不確定標記（如秀姑巒第 26 段的 `PI`）
- **THEN** 報告各章都沒有構詞判斷困難或不確定標記的統計

#### Scenario: 不產生 docx／txt 報告

- **WHEN** 執行驗證程式
- **THEN** `kithann/out/` 不會產生 `docx_txt_report.md`

#### Scenario: 報告的檔名

- **WHEN** 執行驗證程式
- **THEN** 報告寫到 `kithann/out/Glossing驗證報告.md`，不會產生 `glossing_report.md`
