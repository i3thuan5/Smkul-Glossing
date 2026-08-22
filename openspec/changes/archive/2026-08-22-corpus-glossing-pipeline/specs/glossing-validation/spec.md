# glossing-validation Spec

## Purpose

驗證每組 glossing 標註是否符合規則:第二行(構詞切分)與第三行(gloss)對齊、切分符號呼應、構詞標記在原語會 ODS 清單內;不符合的組記錄原因供報告。

## ADDED Requirements

### Requirement: 原文嚴格檢查切分

第二行(切分)去掉構詞符號後,SHALL 與第一行(原文)逐字相同。**多一個或少一個字母、漢字、數字、撇號都算錯誤**,列入報告並附兩行內容。比對時 SHALL 忽略:空白、標點符號(原文保留句讀、切分照慣例不留)、英文大小寫(切分常把專有名詞大寫)。**標點差異雖然不算錯誤、不擋匯出,但 SHALL 記錄下來列入報告的討論事項**,讓對方確認切分行要不要保留句讀。撇號(喉塞音)SHALL NOT 忽略——排灣語 ODS 1-3 明定切分的 `[k]`/`[ʔ]` 要跟著原文的寫法。

#### Scenario: 原文與切分一致

- **WHEN** 驗證秀姑巒第 26 組:原文 `pisanoAmis a caciyaw awa to matini`、切分 `pi-sano-Amis a caciyaw awa=to matini`
- **THEN** 去掉 `-`、`=` 與空白後兩者逐字相同,通過驗證

#### Scenario: 標點與大小寫的差不算錯,但要記錄

- **WHEN** 驗證太魯閣 1 第 1 組:原文 `Kiya ha, Tku ita mnswayi` 有逗號、切分 `Kiya ha Tku ita mnswayi` 沒有
- **THEN** 通過驗證、照常匯出,同時記一筆「標點無仝」列入報告討論事項

#### Scenario: 差一個字母算錯

- **WHEN** 驗證中排灣 1 第 8 組:原文 `si'uda'udan`、切分 `si-'uda-'uda-an`(去符號後多一個 `a`)
- **THEN** 列為「原文佮切分無仝」錯誤,不匯出

#### Scenario: 差一個撇號算錯

- **WHEN** 驗證中排灣 2 第 7 組:原文 `a na ne'a`、切分 `'ana ne'a`(切分多一個撇號)
- **THEN** 列為「原文佮切分無仝」錯誤,不匯出

### Requirement: token 對齊

一組的構詞切分行與 gloss 行 SHALL 有相同的 token 數(token 以空白分隔),一一對應。數量不一致 SHALL 列為錯誤,記錄兩行的 token 數與內容。

#### Scenario: token 數不一致

- **WHEN** 驗證秀姑巒第 20 組:切分行 `ha-lafin=to kako itini na-itira i 89 年` 有 7 個 token,gloss 行 `HA-過夜=完成貌 我.主格 在這裡 從-在那裡 介系詞 八十九年` 只有 6 個
- **THEN** 該組列為錯誤,原因記「token 數不對齊(7 vs 6)」

### Requirement: 切分符號呼應

對應的 token 之間,構詞符號 SHALL 呼應:切分 token 內的 `-`(詞綴)、`=`(附著詞)、`<>`(中綴)、`~`(重疊)分出幾個詞素,gloss token SHALL 用相同符號分出相同數量的 gloss。不呼應 SHALL 列為錯誤並記錄該 token 對。

#### Scenario: 符號呼應

- **WHEN** 驗證秀姑巒第 20 組的 token 對 `ha-lafin=to` ↔ `HA-過夜=完成貌`(各為 1 個 `-`、1 個 `=`)
- **THEN** 通過驗證,拆出詞素 [ha=HA, lafin=過夜, to=完成貌]

#### Scenario: 中綴呼應

- **WHEN** 驗證 ODS 阿美語 sheet 範例的 token 對 `k<om>aen` ↔ `<主焦>吃`
- **THEN** 通過驗證,拆出詞素 [om=主焦(中綴), kaen=吃]

#### Scenario: 符號不呼應

- **WHEN** 驗證秀姑巒第 53 組的 token 對 `pitapal`(無切分符號)↔ `PI-發現`(1 個 `-`)
- **THEN** 該 token 對列為錯誤,原因記「切分符號不呼應」

### Requirement: 構詞標記查 ODS 清單

接在 `-`、`=`、`<>`、`~` 上的語法標記 gloss SHALL 存在於 `原語會提供-常用構詞標記清單_0713.ods` 中該語言 sheet 的標記集合;不在清單內 SHALL 列為錯誤並記錄標記與所屬語言。詞根的中文意譯 SHALL NOT 查表。語料目錄與 ODS sheet 的對應 SHALL 為:阿美族→阿美語、排灣族→排灣語、泰雅族→泰雅語、布農族→布農語、太魯閣族→太魯閣語、魯凱族/霧台→霧台魯凱語。

#### Scenario: 合法標記

- **WHEN** 驗證太魯閣 1 第 8 組 `tgsa-i=nisu` 的詞綴 gloss `受處焦.祈使`(接在 `-` 上),而 `受處焦.祈使` 在太魯閣語 sheet
- **THEN** 通過驗證

#### Scenario: 清單外標記

- **WHEN** 驗證太魯閣 1 第 8 組 `tgsa-i=nisu` 的附著詞 gloss `你.所有格`(接在 `=` 上),而 `所有格` 不在太魯閣語 sheet
- **THEN** 該組列為錯誤,原因記「標記不在清單:你.所有格(太魯閣語)」

#### Scenario: 詞根意譯不查表

- **WHEN** 驗證秀姑巒第 17 組的 `kyokay` gloss `教會`(獨立詞根,未接任何切分符號)
- **THEN** 不查表、不列為錯誤

### Requirement: 大寫「不確定」標記

依 ODS 備註欄 1-2 的慣例(「不確定是什麼時,用大寫或 ?」),全大寫拉丁字母的 gloss(如秀姑巒第 26 組 `pi-sano-Amis` 的 `PI`、第 20 組 `ha-lafin=to` 的 `HA`)SHALL 視為合法、不列「標記不在清單」錯誤,但 SHALL 在報告中單獨統計一區(標記、語言、出現次數)供對方檢視。

#### Scenario: 大寫標記合法

- **WHEN** 驗證秀姑巒第 20 組的詞綴 gloss `HA`(全大寫)
- **THEN** 不列為錯誤,計入報告的「不確定標記統計」

### Requirement: ODS 備註欄認可的特殊符號

ODS 備註欄定義的特殊符號 SHALL 視為合法、不列錯誤:`==`(字尾拉長音,ODS 阿美語範例 `wata==`)、`:`(拉長音,ODS 阿美語範例 `iti:raw`,置於倒數第二音節後)、`＠`(笑聲)、`...`(聽不清)、`^` 等,依 `docs/glossing-rules.md` 整理的清單為準。

#### Scenario: 拉長音符號

- **WHEN** 原文行含拉長音(如 `iti:raw` 的 `:`)
- **THEN** 不因該符號列為錯誤

### Requirement: 錯誤記錄原因與定位

每筆驗證錯誤 SHALL 記錄:檔案路徑、組編號、錯誤類別、具體原因(含出錯的 token 或行內容)。一組可有多筆錯誤;一組出錯不影響同檔其他組的驗證與匯出。

#### Scenario: 一檔多錯

- **WHEN** 驗證秀姑巒:第 20 組 token 不對齊(7 vs 6)、第 53 組符號不呼應(`pitapal` ↔ `PI-發現`)
- **THEN** 報告列出各自定位的錯誤,同檔其餘合規組照常匯出
