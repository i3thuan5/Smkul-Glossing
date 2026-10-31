## REMOVED Requirements

### Requirement: 檔案配對檢查

**Reason**: 2026.09 會議案由一決議以 docx 為主，txt 不再核對，docx／txt 一致性報告不再產生。

**Migration**: 語料一律由 docx 產生（corpus-parsing「語料來源為 docx」），不需要配對 txt。

### Requirement: 逐段結構比對

**Reason**: 同上，txt 不再核對。

**Migration**: 無；docx 的內容問題由 glossing 驗證報告列出。

### Requirement: docx 審閱註解要抽出來列入報告

**Reason**: 2026.09 會議案由二決議 docx 審閱註解全部忽略。

**Migration**: 無；docx 內文本來就不含審閱註解（corpus-parsing「語料來源為 docx」）。

### Requirement: 逐行比對而非比對組裝後的欄位

**Reason**: txt 不再核對，這條比對規則沒有對象。

**Migration**: 無。

### Requirement: docx 顏色標記層不比對但須提醒

**Reason**: 2026.09 會議案由三決議 docx 顏色標記層忽略。

**Migration**: 無。
