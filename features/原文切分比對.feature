Feature: 原文與切分的逐字比對

  更新日期：2026.8.22

  切分行去掉構詞符號（- = <> ~）之後，要與原文逐字相同。
  **多一個或少一個字母、漢字、數字、單引號都算不符**。

  詞的個數也要一個對一個。**只有依附詞（= 這個符號）例外**：
  它會把原文的兩個詞併成切分的一個詞，這樣算通過。

  比對時忽略兩項：標點、英文大小寫。
  單引號不忽略——它是喉塞音，是音位。
  空白也不忽略——空白會改變詞的個數。

  例子照語言優先序挑：阿美（秀姑巒→海岸→南勢）→太魯閣→魯凱→排灣，
  內容都照語料原樣，半形全形都不改。

Scenario: 一般情形：逐字相同，詞也一個對一個
  # 全語料有 1075 組是這種沒有依附詞、詞數也一樣的。
  # 切分只是把詞拆成詞素，字母序列與詞的個數都沒有變。
  # 例 1（下面用這一組比對）：阿美族/秀姑巒/陳美莉_阿星.阿曼_說族語在大漢部落的過.txt 第 23 組
  #   原文：masamaan i to
  #   切分：masa-maan i to
  #   glossing：像-什麼 言談標記 斜格
  #   翻譯：現在的情況
  # 例 2：太魯閣族/1_黃麗俐Miring_胡月英Tku_生活中的氣候啟示.txt 第 272 組
  #   原文：Saw msibus ga
  #   切分：saw m-sibus ga
  #   glossing：像 主焦-甜 那
  #   翻譯：像是甜的飲料
  # 例 3：魯凱族/霧台/3.包鳯嬌_Uselrepe_月桃文化及製作上集.txt 第 112 組
  #   原文：maduay
  #   切分：ma-duay
  #   glossing：靜態.限定-容易
  #   翻譯：很容易的
  When 原文是 "masamaan i to"，切分是 "masa-maan i to"
  Then 逐字比對通過

Scenario: 依附詞把原文的兩個詞併成切分的一個詞，這樣算通過
  # 全語料有 1575 組是這種情形。
  # 原文的 awa to、masaromaay to 這種，切分會用 = 併成一個詞。
  # 比對時 = 會被拿掉，所以字母序列還是一樣，算通過。
  # 例 1（下面用這一組比對）：阿美族/秀姑巒/陳美莉_阿星.阿曼_說族語在大漢部落的過.txt 第 147 組
  #   原文：masaromaay to
  #   切分：ma-sa-roma-ay=to
  #   glossing：受焦-工具焦-另外-實現=完成貌
  #   翻譯：就有改變了
  # 例 2：太魯閣族/1_黃麗俐Miring_胡月英Tku_生活中的氣候啟示.txt 第 265 組
  #   原文：Snaw mu
  #   切分：snaw=mu
  #   glossing：男人=我.屬格
  #   翻譯：我的丈夫
  # 例 3：魯凱族/霧台/2.包鳯嬌_Tuku_建築石板屋與傳說故事.txt 第 164 組
  #   原文：agili ila kavay vaeva ka vai yai ta lrailri
  #   切分：agi=li ila kavay vaeva ka vai yai ta-lrailri
  #   glossing：弟弟=我.屬格 走 那.可見.禁止 一個 斜格 太陽 主題標記 我門.包含.屬格-射箭
  #   翻譯：弟弟我們去把一個太陽射下來
  When 原文是 "masaromaay to"，切分是 "ma-sa-roma-ay=to"
  Then 逐字比對通過

Scenario: 只差英文大小寫，算通過
  # 全語料有 125 組是這種情形（詞數一樣、只有大小寫不同）。
  # 切分常把專有名詞、未分類詞綴寫成大寫。
  # 例 1（下面用這一組比對）：太魯閣族/1_黃麗俐Miring_胡月英Tku_生活中的氣候啟示.txt 第 20 組
  #   原文：Iq
  #   切分：iq
  #   glossing：是
  #   翻譯：是
  # 例 2：魯凱族/霧台/1.包鳯嬌_Ripunu_耆老的尊榮冠冕.txt 第 182 組
  #   原文：lu ka wakela ki zinsiw ka kiathingathingale lripwa kay lialivarane
  #   切分：lu KA wa-kela ki zinsiw ka ki-a-thinga-thingale lri-pwa kay lialivarane
  #   glossing：如果 KA 主動-來到 斜格 全省 斜格 被動-限定-重疊-知道 未來-放 這 蝴蝶
  #   翻譯：插飾蝴蝶除非有參加全省賽
  # 例 3：阿美族/秀姑巒/陳美莉_阿星.阿曼_說族語在大漢部落的過.txt 第 69 組
  #   原文：ano haen ko demak saka o no mako a pi建議
  #   切分：ano haen ko demak saka o no mako a PI-建議
  #   glossing：如果 這樣 主格 工作 所以 名詞標記 屬格 我.所有格 連繫詞 PI-建議
  #   翻譯：如果這樣的情況持續著 我的建議是
  When 原文是 "Iq"，切分是 "iq"
  Then 逐字比對通過

Scenario: 不符——只差單引號
  # 全語料有 189 組是這一類。
  # 排灣語 ODS 1-3 規定切分的 [k] / ['] 要跟著原文的寫法，
  # 所以這一類多半是要決定哪一邊才對。單引號是喉塞音，
  # 是音位，不能忽略。
  # 例 1（下面用這一組比對）：阿美族/秀姑巒/陳美莉_阿星.阿曼_說族語在大漢部落的過.txt 第 91 組
  #   原文：ano caay kadodoen ita ko sowal no i fafaway
  #   切分：ano caay ka-do'do-en=ita ko sowal no i fafaw-ay
  #   glossing：如果 不 KA-跟-受焦=咱們.包含.所有格 主格 話 屬格 介系詞 上游-實現
  #   翻譯：如果我們沒有依著長官的
  # 例 2：排灣族/東排灣/3_阮翠芳Gesi_鄭玉英_生命故事.txt 第 142 組
  #   原文：na mareka u aya
  #   切分：na-mareka 'u=aya
  #   glossing：完成貌-一些 我.屬格=說
  #   翻譯：我的家人
  # 例 3：布農族/巒群/1_松念竹Akuan_全美玲_布農語近代影響及語言之重要和傳承.txt 第 153 組
  #   原文：haan
  #   切分：ha'an
  #   glossing：介係詞
  #   翻譯：在...
  When 原文是 "ano caay kadodoen ita ko sowal no i fafaway"，切分是 "ano caay ka-do'do-en=ita ko sowal no i fafaw-ay"
  Then 逐字比對不符，分類是 "只差單引號"
  And 差異是 "切分多了「'」"

Scenario: 不符——只差一個字母
  # 全語料有 944 組是這一類。
  # 多半是切分時多打或漏打一個音，或是照發音改寫了拼法。
  # 例 1（下面用這一組比對）：阿美族/秀姑巒/陳美莉_阿星.阿曼_說族語在大漢部落的過.txt 第 62 組
  #   原文：caay katama masa mahatila
  #   切分：caay ka-tama masa ma-ha-tira
  #   glossing：不 KA-正確 像 受焦-HA-那裡
  #   翻譯：這不是一個正確的方式
  # 例 2：太魯閣族/1_黃麗俐Miring_胡月英Tku_生活中的氣候啟示.txt 第 116 組
  #   原文：Shngiun da.
  #   切分：shungi-un da
  #   glossing：忘記-受焦 了
  #   翻譯：忘記了
  # 例 3：魯凱族/霧台/2.包鳯嬌_Tuku_建築石板屋與傳說故事.txt 第 21 組
  #   原文：walibita
  #   切分：wa-alibi=ta
  #   glossing：主動-石板屋=我們.包含.屬格
  #   翻譯：石板屋
  When 原文是 "caay katama masa mahatila"，切分是 "caay ka-tama masa ma-ha-tira"
  Then 逐字比對不符，分類是 "只差一個字母"
  And 差異是 "「l」→「r」"

Scenario: 不符——差 2-3 個字母
  # 全語料有 619 組是這一類。
  # 通常是拼法慣例不同。
  # 例 1（下面用這一組比對）：阿美族/秀姑巒/陳美莉_阿星.阿曼_說族語在大漢部落的過.txt 第 30 組
  #   原文：sakalahdaw lahdaw sato
  #   切分：saka lahedaw lahedaw sato
  #   glossing：所以 不見 不見 這樣
  #   翻譯：越來越嚴重了
  # 例 2：太魯閣族/1_黃麗俐Miring_胡月英Tku_生活中的氣候啟示.txt 第 117 組
  #   原文：Manu kido
  #   切分：manu kiya.do
  #   glossing：什麼 助詞
  #   翻譯：因此
  # 例 3：魯凱族/霧台/3.包鳯嬌_Uselrepe_月桃文化及製作上集.txt 第 16 組
  #   原文：asilwiyane yai
  #   切分：asi-lu-iya-ane yai
  #   glossing：為什麼-如果-說-名物化 主題標記
  #   翻譯：為何這樣說
  When 原文是 "sakalahdaw lahdaw sato"，切分是 "saka lahedaw lahedaw sato"
  Then 逐字比對不符，分類是 "差 2-3 個字母"
  And 差異是 "切分多了「e」、切分多了「e」"

Scenario: 不符——長度差很多
  # 全語料有 24 組是這一類。
  # 長度差四分之一以上，通常是切分少了一整段
  # （或多了一整段），內容可能遺失。
  # 例 1（下面用這一組比對）：阿美族/秀姑巒/陳美莉_阿星.阿曼_說族語在大漢部落的過.txt 第 107 組
  #   原文：matiya o no 原民會 nikaorira
  #   切分：ma-tiya o no 原民會
  #   glossing：主焦-那 名詞標記 屬格 原民會
  #   翻譯：像原民會
  # 例 2：太魯閣族/1_黃麗俐Miring_胡月英Tku_生活中的氣候啟示.txt 第 332 組
  #   原文：Maxun ta hida
  #   切分：gimax-un=ta hiya.da
  #   glossing：混合-受焦=我們.包含.屬格 那
  #   翻譯：搭配在一起
  # 例 3：布農族/巒群/2_松念竹Akuan_全英輝_早期布農族人生活分享(婚姻、食物、生活).txt 第 110 組
  #   原文：pau qabas tu
  #   切分：tupa'-un qabas tu
  #   glossing：說-受焦 以前 連繫詞
  #   翻譯：以前說
  When 原文是 "matiya o no 原民會 nikaorira"，切分是 "ma-tiya o no 原民會"
  Then 逐字比對不符，分類是 "長度差很多"
  And 差異是 "切分少了「nikaorira」"

@規格要討論
Scenario: 只差標點，算通過，另外記一筆待確認
  # 全語料有 628 組是這種情形。
  # 原文保留句讀、切分照慣例不留。這不算錯誤、不擋匯出，
  # 不過會另外記一筆「標點不同」列進報告，請對方確認慣例。
  # 例 1（下面用這一組比對）：阿美族/秀姑巒/陳美莉_阿星.阿曼_說族語在大漢部落的過.txt 第 21 組
  #   原文：tangasa anini wa.. 110 年
  #   切分：tangasa anini wa 110 年
  #   glossing：到達 現在 助詞 110年
  #   翻譯：直到現在110年
  # 例 2：太魯閣族/1_黃麗俐Miring_胡月英Tku_生活中的氣候啟示.txt 第 16 組
  #   原文：Ah!
  #   切分：ah
  #   glossing：嘆詞
  #   翻譯：啊!
  # 例 3：排灣族/東排灣/1_阮翠芳Gesi_高桂妹_80歲vuvu的傳說故事.txt 第 126 組
  #   原文：e.
  #   切分：e
  #   glossing：填補詞
  #   翻譯：呃
  When 原文是 "tangasa anini wa.. 110 年"，切分是 "tangasa anini wa 110 年"
  Then 逐字比對通過
  And 另外記一筆標點不同

@規格要討論
Scenario: 只差空白，先算不通過
  # 全語料有 222 組是這種情形。
  # 原文黏成一個詞、切分拆開（或相反），字母序列沒有變，
  # 可是詞的個數變了。依照「詞數要一個對一個、只有依附詞例外」，
  # 這種先算不通過。
  # 程式現在把空白當成忽略項、判成通過，所以這一條會紅——
  # 規格已經定了，程式還沒改。
  # 例 1（下面用這一組比對）：阿美族/秀姑巒/陳美莉_阿星.阿曼_說族語在大漢部落的過.txt 第 19 組
  #   原文：nikaorira
  #   切分：nika orira
  #   glossing：但是 那
  #   翻譯：但是
  # 例 2：魯凱族/霧台/3.包鳯嬌_Uselrepe_月桃文化及製作上集.txt 第 132 組
  #   原文：pakatharirimadu
  #   切分：pa-ka-thariri madu
  #   glossing：使役-靜態.非限定-好 某人要
  #   翻譯：要綁得很好
  # 例 3：排灣族/東排灣/2_阮翠芳Gesi_阮秀美_土坂派出所拘留所的故事.txt 第 139 組
  #   原文：masa na uli
  #   切分：masa na-uli
  #   glossing：也許 完成貌-非實現
  #   翻譯：也許可能
  When 原文是 "nikaorira"，切分是 "nika orira"
  Then 逐字比對不符，分類是 "詞數不同"

@規格要討論
Scenario: 不符——多處不同
  # 全語料有 280 組是這一類。
  # 可能是換了詞、或原文與切分根本不是同一句。
  # 下面例 1 是標注者在切分行寫詞源（原文的 moyi 寫成「母語」），
  # 不是拼寫差異。這種要不要算不符，要討論。
  # 例 1（下面用這一組比對）：阿美族/秀姑巒/陳美莉_阿星.阿曼_說族語在大漢部落的過.txt 第 111 組
  #   原文：awaay ko maan kita a caciyaw to no moyi
  #   切分：awa-ay ko maan kita a caciyaw to no 母語
  #   glossing：沒有-實現 主格 什麼 咱們.包含.主格 連繫詞 說話 斜格 屬格 母語
  #   翻譯：我們的長輩們說母語是沒有問題的
  # 例 2：太魯閣族/1_黃麗俐Miring_胡月英Tku_生活中的氣候啟示.txt 第 203 組
  #   原文："Tkani cih han"
  #   切分：cikan-i cicih han
  #   glossing：搗米-受處焦.祈使 一點點 助詞
  #   翻譯："妳先來搗米一下" 母親的命令句
  # 例 3：魯凱族/霧台/1.包鳯嬌_Ripunu_耆老的尊榮冠冕.txt 第 21 組
  #   原文：la kainaku temimi
  #   切分：la kai-n=aku te<ming>ming
  #   glossing：然後 否定-N-我.主格 <重疊>得名.華語
  #   翻譯：所以名次我沒再拿到
  When 原文是 "awaay ko maan kita a caciyaw to no moyi"，切分是 "awa-ay ko maan kita a caciyaw to no 母語"
  Then 逐字比對不符，分類是 "多處不同"
  And 差異是 "「moyi」→「母語」"
