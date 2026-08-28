# glossing-validation Specification

## Purpose

驗證每組 glossing 標註是否符合規則:第二行(構詞切分)與第三行(gloss)對齊、切分符號呼應、構詞標記在原語會 ODS 清單內;不符合的組記錄原因供報告。

## Requirements

### Requirement: 原文嚴格檢查切分

第二行(切分)去掉構詞符號後,SHALL 與第一行(原文)逐字相同。**多一個或少一個字母、漢字、數字、撇號都算錯誤**,列入報告並附兩行內容。比對時 SHALL 忽略:標點符號(原文保留句讀、切分照慣例不留)、英文大小寫(切分常把專有名詞大寫)。空白本身不比,但**詞數 SHALL 對得起來**:原文黏成一個詞、切分拆開(或相反)雖然字母序列一樣,SHALL 列為「詞數不同」。唯一的例外是依附詞——切分用 `=` 把原文的兩個詞併成一個 token 是合法的,一個 token 最多可以吃(1 + `=` 的個數)個原文詞。**標點差異雖然不算錯誤、不擋匯出,但 SHALL 記錄下來列入報告的討論事項**,讓對方確認切分行要不要保留句讀。撇號(喉塞音)SHALL NOT 忽略——排灣語 ODS 1-3 明定切分的 `[k]`/`[ʔ]` 要跟著原文的寫法。

#### Scenario: 原文與切分一致

- **WHEN** 驗證秀姑巒第 26 組:原文 `pisanoAmis a caciyaw awa to matini`、切分 `pi-sano-Amis a caciyaw awa=to matini`
- **THEN** 去掉 `-`、`=` 與空白後兩者逐字相同,通過驗證

#### Scenario: 標點與大小寫的差不算錯,但要記錄

- **WHEN** 驗證太魯閣 1 第 1 組:原文 `Kiya ha, Tku ita mnswayi` 有逗號、切分 `Kiya ha Tku ita mnswayi` 沒有
- **THEN** 通過驗證、照常匯出,同時記一筆「標點無仝」列入報告討論事項

#### Scenario: 只差空白但詞數不同,算錯

- **WHEN** 驗證秀姑巒第 19 組:原文 `nikaorira`(1 個詞)、切分 `nika orira`(2 個 token,沒有 `=`)
- **THEN** 列為「原文與切分不符-詞數不同」錯誤,不匯出

#### Scenario: 依附詞併詞不算詞數不同

- **WHEN** 驗證秀姑巒第 147 組:原文 `masaromaay to`(2 個詞)、切分 `ma-sa-roma-ay=to`(1 個 token,含 1 個 `=`)
- **THEN** 通過驗證——一個 token 吃兩個原文詞是依附詞的合法寫法

#### Scenario: 差一個字母算錯

- **WHEN** 驗證中排灣 1 第 8 組:原文 `si'uda'udan`、切分 `si-'uda-'uda-an`(去符號後多一個 `a`)
- **THEN** 列為「原文佮切分無仝」錯誤,不匯出

#### Scenario: 差一個撇號算錯

- **WHEN** 驗證中排灣 2 第 7 組:原文 `a na ne'a`、切分 `'ana ne'a`(切分多一個撇號)
- **THEN** 列為「原文佮切分無仝」錯誤,不匯出

### Requirement: 切分行與 gloss 行對不起來的分類

切分行與 gloss 行對不起來時 SHALL 分成五類記錄，分類名稱與 `features/切分與glossing對應.feature` 的 Scenario 一致，而且報告的「問題類型」SHALL 直接用這五類，不另立「token 數不對齊」「切分符號不呼應」兩類。詞數不同時 SHALL 整行判斷，詞數相同時 SHALL 逐個 token 比切分符號、取第一個對不起來的 token 對：

- **gloss 的詞比切分少**、**gloss 的詞比切分多**：兩行的 token 數不同。
- **切分沒有切，gloss 有切**：某個 token 的切分符號比 gloss 少。
- **切分有切，gloss 沒有切**：某個 token 的切分符號比 gloss 多。
- **符號的種類不一樣**：符號個數相同但種類或順序不同。

拉長音的 `==`（ODS 1-4）SHALL NOT 當成切分符號，比對前先排除。

對不起來的組 SHALL 列為錯誤，記錄分類、兩行內容；逐 token 的三類另記對不起來的那一對 token。通過的組才進構詞判定。

#### Scenario: 對應通過

- **WHEN** 比對切分 `ma-sa-roma-ay=to` 與 gloss `受焦-工具焦-另外-實現=完成貌`
- **THEN** 兩行的 token 數與每個 token 的符號都呼應，通過，拆出詞素 [ma, sa, roma, ay, to]

#### Scenario: gloss 的詞比切分少

- **WHEN** 比對切分 `nawhani ha-lafin=to ko aro itini`（6 個）與 gloss `因為HA-過夜=完成貌 主格 居住 在這裡`（4 個）
- **THEN** 該組列為錯誤，分類記「gloss 的詞比切分少」

#### Scenario: gloss 的詞比切分多

- **WHEN** 比對切分 `ma-fana' ci mira`（3 個）與 gloss `主焦-會 主格 主格 他.所有格`（4 個）
- **THEN** 該組列為錯誤，分類記「gloss 的詞比切分多」

#### Scenario: 切分沒有切,gloss 有切

- **WHEN** 比對秀姑巒第 53 組，切分 token `pitapal` 沒有符號、對應的 gloss token `PI-發現` 有一個 `-`
- **THEN** 該組列為錯誤，分類記「切分沒有切，gloss 有切」，並指出是 `pitapal` 對 `PI-發現`

#### Scenario: 切分有切，gloss 沒有切

- **WHEN** 比對切分 token `ma-linah-ay`（兩個 `-`）與 gloss token `主焦-搬遷`（一個 `-`）
- **THEN** 該組列為錯誤，分類記「切分有切，gloss 沒有切」，並指出是 `ma-linah-ay` 對 `主焦-搬遷`

#### Scenario: 符號的種類不一樣

- **WHEN** 比對切分 token `mala-mama=to`（`-=`）與 gloss token `成為=爸爸=完成貌`（`==`）
- **THEN** 該組列為錯誤，分類記「符號的種類不一樣」

#### Scenario: 中綴呼應

- **WHEN** 比對 ODS 阿美語 sheet 範例的 token 對 `k<om>aen` ↔ `<主焦>吃`
- **THEN** 通過，拆出詞素 [om=主焦（中綴）, kaen=吃]

#### Scenario: 拉長音的 == 不算切分符號

- **WHEN** 比對切分 token `lja==` 與 gloss token `XX`
- **THEN** 兩邊都視為沒有切分符號，對應通過

### Requirement: 構詞標記查 ODS 清單

接在 `-`、`=`、`<>`、`~` 上的語法標記 SHALL 查 `原語會提供-常用構詞標記清單_0713.ods` 中該語言 sheet。查表 SHALL 同時比 gloss 與**形**：清單登記的是某一個詞綴的形與意思（4-32「去｜`ma-`」說的是「前綴 `ma-` 的意思是去」），所以 gloss 相同但形對不上的那一段 SHALL NOT 算詞綴，是詞根的候選。清單只登記成詞、沒有 `-`／`=`／`<>` 的（9-79「以後｜`anoayaw`」）沒有詞綴的形可比，同樣 SHALL NOT 算詞綴。全大寫的「不確定」標記與重疊 SHALL 免比形——前者是「標注者不確定」的記號、後者的形是詞根自己的重複，兩者都登記不了固定的形。

對不上 SHALL NOT 列為錯誤、SHALL NOT 擋匯出。詞根的中文意譯 SHALL NOT 查表。語料目錄與 ODS sheet 的對應 SHALL 為：阿美族→阿美語、排灣族→排灣語、泰雅族→泰雅語、布農族→布農語、太魯閣族→太魯閣語、魯凱族/霧台→霧台魯凱語。

#### Scenario: 合法標記

- **WHEN** 驗證太魯閣 1 第 8 組 `tgsa-i=nisu` 的詞綴 gloss `受處焦.祈使`（接在 `-` 上），而 `受處焦.祈使` 在太魯閣語 sheet
- **THEN** 通過驗證

#### Scenario: 清單外標記

- **WHEN** 驗證中排灣 1 第 5 組 `tja=黑板`（gloss `我們.包含.屬格=黑板`），`我們.包含.屬格` 登記的形是 `tja=`、`黑板` 不在排灣語 sheet
- **THEN** `tja` 判為 `依附詞`、`黑板` 判為 `詞根`，整組照常匯出 YAML

#### Scenario: gloss 對得上但形對不上

- **WHEN** 驗證排灣語 `vaik-i`（gloss `去-主焦.祈使`），清單 4-32 登記「去」的前綴形是 `ma-`、4-25 登記「主焦.祈使」的後綴形是 `-u;-i`
- **THEN** `vaik` 的形對不上 `ma-`，判為 `詞根`；`i` 的形對得上，判為 `後綴`

#### Scenario: 詞根意譯不查表

- **WHEN** 驗證秀姑巒第 17 組的 `kyokay` gloss `教會`（獨立詞根，未接任何切分符號）
- **THEN** 不查表、不列為錯誤

### Requirement: 大寫「不確定」標記

依 ODS 備註欄 1-2 的慣例(「不確定是什麼時,用大寫或 ?」),全大寫拉丁字母的 gloss(如秀姑巒第 26 組 `pi-sano-Amis` 的 `PI`、第 20 組 `ha-lafin=to` 的 `HA`)SHALL 視為合法、不列「標記不在清單」錯誤,但 SHALL 在報告中單獨統計一區(標記、語言、出現次數)供對方檢視。

#### Scenario: 大寫標記合法

- **WHEN** 驗證秀姑巒第 20 組的詞綴 gloss `HA`(全大寫)
- **THEN** 不列為錯誤,計入報告的「不確定標記統計」

### Requirement: ODS 備註欄認可的特殊符號

ODS 備註欄定義的特殊符號 SHALL 視為合法、不列錯誤：`==`（字尾拉長音，ODS 阿美語範例 `wata==`）、`:`（拉長音，ODS 阿美語範例 `iti:raw`，置於倒數第二音節後）、`＠`（笑聲）、`...`（聽不清）、`^` 等。完整的符號表 SHALL 列在 glossing 報告的「語料格式說明」章（見 corpus-export），程式與報告用同一份常數，不另外維護文件。

#### Scenario: 拉長音符號

- **WHEN** 原文行含拉長音（如 `iti:raw` 的 `:`）
- **THEN** 不因該符號列為錯誤

#### Scenario: 符號表與報告一致

- **WHEN** 產生 glossing 報告
- **THEN** 「語料格式說明」章列出的特殊符號與程式視為合法的符號相同

### Requirement: 錯誤記錄原因與定位

每筆驗證錯誤 SHALL 記錄:檔案路徑、組編號、錯誤類別、具體原因(含出錯的 token 或行內容)。一組可有多筆錯誤;一組出錯不影響同檔其他組的驗證與匯出。

#### Scenario: 一檔多錯

- **WHEN** 驗證秀姑巒:第 20 組 token 不對齊(7 vs 6)、第 53 組符號不呼應(`pitapal` ↔ `PI-發現`)
- **THEN** 報告列出各自定位的錯誤,同檔其餘合規組照常匯出

### Requirement: 構詞判定的分類

每個詞素的構詞 SHALL 依 `features/構詞判定.feature` 的「判斷方法」判定，值為 `詞根`、`前綴`、`後綴`、`環綴`、`中綴`、`依附詞`、`重疊`、`無法判斷` 之一。判定 SHALL 靠 gloss 與形查表反推詞根，不是靠詞素在切分符號的哪一邊——前附著詞（`tja=`、`'u=`）後面那一段才是詞根。

一個詞若沒有任何切分符號，那一整段 SHALL 判為 `詞根`：詞綴要有東西可黏才成立，gloss 查得到也不算詞綴。

#### Scenario: 前附著詞後面才是詞根

- **WHEN** 驗證 `tja=黑板` ↔ `我們.包含.屬格=黑板`
- **THEN** `黑板` 判為 `詞根`、`tja` 跨過 `=` 判為 `依附詞`

#### Scenario: 沒有切分符號的詞整個是詞根

- **WHEN** 驗證 `a` ↔ `連繫詞`，而 `連繫詞` 在該語言 sheet 裡
- **THEN** `a` 判為 `詞根`，不因為 gloss 查得到就判成詞綴

### Requirement: 詞根判不出來時記無法判斷

詞根判不出來的兩種情形——不只一段沒被標成詞綴（判斷方法 3b）、每一段都被標成詞綴（3c）——SHALL 記為 `無法判斷`。這 SHALL NOT 算錯誤、SHALL NOT 擋匯出，並 SHALL 依「詞素 × 語言」統計供報告「構詞判斷困難」章使用。

記 `無法判斷` 的 SHALL 只有真正判不出來的那幾段：第 1 步就認出來的中綴、環綴、重疊不看詞根位置，SHALL 照留；其餘詞綴若對每一個可能的詞根位置都算出同一個結果，SHALL 照樣判出來。

#### Scenario: 不只一段沒被標成詞綴

- **WHEN** 驗證 `'i-vaqu` ↔ `採-小米`，`採` 與 `小米` 都不在排灣語 sheet
- **THEN** 兩段都記 `無法判斷`，整組不因此擋匯出

#### Scenario: 每一段都被標成詞綴

- **WHEN** 驗證 `na-ni` ↔ `過去-NI`，`過去` 的形對得上 `na-`、`NI` 是全大寫的不確定標記
- **THEN** 兩段都記 `無法判斷`，計入統計

#### Scenario: 詞根不明但詞綴仍判得出來

- **WHEN** 驗證 `z<em>e-liu-liulj=amen` ↔ `<主焦>-重疊-工錢=我們.主格`，`ze` 與 `liulj` 都不算詞綴（兩個詞根候選）
- **THEN** `ze` 與 `liulj` 記 `無法判斷`；`em` 仍為 `中綴`、`liu` 仍為 `重疊`，`amen` 不論詞根是哪一段都跨過 `=`，判為 `依附詞`
