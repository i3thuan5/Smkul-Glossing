## MODIFIED Requirements

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

### Requirement: ODS 備註欄認可的特殊符號

ODS 備註欄定義的特殊符號 SHALL 視為合法、不列錯誤：`==`（字尾拉長音，ODS 阿美語範例 `wata==`）、`:`（拉長音，ODS 阿美語範例 `iti:raw`，置於倒數第二音節後）、`＠`（笑聲）、`...`（聽不清）、`^` 等。完整的符號表 SHALL 列在 glossing 報告的「語料格式說明」章（見 corpus-export），程式與報告用同一份常數，不另外維護文件。

#### Scenario: 拉長音符號

- **WHEN** 原文行含拉長音（如 `iti:raw` 的 `:`）
- **THEN** 不因該符號列為錯誤

#### Scenario: 符號表與報告一致

- **WHEN** 產生 glossing 報告
- **THEN** 「語料格式說明」章列出的特殊符號與程式視為合法的符號相同

## REMOVED Requirements

### Requirement: token 對齊

**Reason**: 併入「切分行與 gloss 行對不起來的分類」——token 數不同就是「gloss 的詞比切分少／多」兩類，不另立一類。

**Migration**: 報告「問題類型」的「token 數不對齊」改讀「gloss 的詞比切分少」「gloss 的詞比切分多」。

### Requirement: 切分符號呼應

**Reason**: 併入「切分行與 gloss 行對不起來的分類」——符號不呼應細分成「切分沒有切，gloss 有切」「切分有切，gloss 沒有切」「符號的種類不一樣」三類；「符號呼應」「中綴呼應」兩條 scenario 搬到那條需求下。

**Migration**: 報告「問題類型」的「切分符號不呼應」改讀上述三類。
