Feature: 族語原句與詞素切割的逐字比對

  更新日期：2026.11.19

  詞素切割行去掉切割符號（- = <> ~）之後，要與族語原句逐字相同。
  **多一個或少一個字母、漢字、數字、單引號都算不符**。

  詞素切割的個數也要和族語原句的詞一個對一個。
  但依附詞（=）、詞組（. +）例外，可以把族語原句的兩個詞併成詞素切割的一個詞。

  大小寫會影響到專有名詞、賽夏、噶瑪蘭的書寫。
  現在比對時先忽略兩項：族語原句的標點、英文大小寫。

  詞素切割行本身不能有標點，那是另一項檢查，見 詞素切割標點.feature。
  單引號不忽略——它是喉塞音、會厭塞音。
  阿美語的 ^ 是喉塞音字母，不忽略；
  泰雅語的 _ 如果有差異，可以接受，算通過。

  例子照語言優先序挑：阿美（秀姑巒→海岸→南勢）→太魯閣→魯凱→排灣，
  內容都照語料原樣，半形全形都不改。

Scenario: 一般情形：逐字相同，詞也一個對一個
  # 全語料有 1075 段是這種沒有依附詞、詞數也一樣的。
  # 詞素切割只是把詞拆成詞素，字母序列與詞的個數都沒有變。
  # 例 1（下面用這一段比對）：阿美族/秀姑巒/陳美莉_阿星.阿曼_說族語在大漢部落的過.txt 第 23 段
  #   族語原句：masamaan i to
  #   詞素切割：masa-maan i to
  #   詞素翻譯：像-什麼 言談標記 斜格
  #   華語翻譯：現在的情況
  # 例 2：太魯閣族/1_黃麗俐Miring_胡月英Tku_生活中的氣候啟示.txt 第 272 段
  #   族語原句：Saw msibus ga
  #   詞素切割：saw m-sibus ga
  #   詞素翻譯：像 主焦-甜 那
  #   華語翻譯：像是甜的飲料
  # 例 3：魯凱族/霧台/3.包鳯嬌_Uselrepe_月桃文化及製作上集.txt 第 112 段
  #   族語原句：maduay
  #   詞素切割：ma-duay
  #   詞素翻譯：靜態.限定-容易
  #   華語翻譯：很容易的
  When 族語原句是 "masamaan i to"，詞素切割是 "masa-maan i to"
  Then 逐字比對通過

Scenario: 依附詞把族語原句的兩個詞併成詞素切割的一個詞，是合法的寫法
  # 全語料有 1575 段是這種情形。
  # 族語原句的 awa to、masaromaay to 這種，詞素切割會用 = 併成一個詞。
  # 比對時 = 會被拿掉，所以字母序列還是一樣，算通過。
  # 例 1（下面用這一段比對）：阿美族/秀姑巒/陳美莉_阿星.阿曼_說族語在大漢部落的過.txt 第 147 段
  #   族語原句：masaromaay to
  #   詞素切割：ma-sa-roma-ay=to
  #   詞素翻譯：受焦-工具焦-另外-實現=完成貌
  #   華語翻譯：就有改變了
  # 例 2：太魯閣族/1_黃麗俐Miring_胡月英Tku_生活中的氣候啟示.txt 第 265 段
  #   族語原句：Snaw mu
  #   詞素切割：snaw=mu
  #   詞素翻譯：男人=我.屬格
  #   華語翻譯：我的丈夫
  # 例 3：魯凱族/茂林/1.陳雅苓Milrinu_劉勝記_茂林祈雨祭的由來.docx 第 108 段
  #   族語原句：putudru miti si sutépuru nga miti
  #   詞素切割：pu-tudru miti si su-tépuru=nga miti
  #   詞素翻譯：使役-實現-盛裝 我們.包含.主格 和 就-燒火=完成貌 我們.包含.主格
  #   華語翻譯：接雨水之後就要煮開它
  When 族語原句是 "masaromaay to"，詞素切割是 "ma-sa-roma-ay=to"
  Then 逐字比對通過

Scenario: 族語原句有可能把依附詞寫在一起，是合法的寫法
  # 全語料有 533 段是這種情形（布農 348 段、魯凱 134 段、排灣 41 段、阿美 9 段、太魯閣 1 段）。
  # 族語原句把依附詞跟前面的詞寫成一個詞（olito），詞素切割用 = 切開（oli=to），
  # 還是一個詞對一個詞，比對時 = 會被拿掉，字母序列一樣，算通過。
  # 例 1（下面用這一段比對）：阿美族/海岸/1_阿索.該拿Aso.Kaynga_文健站長輩的故事_難忘的歌曲_歌曲故事.docx 第 80 段
  #   族語原句：Olito milihay
  #   詞素切割：Oli=to mi-lihay
  #   詞素翻譯：去=完成貌 主焦-禮拜
  #   華語翻譯：去做禮拜了
  # 例 2：太魯閣族/2_黃麗俐Miring_張愛珠Imay_為孩子以身作則.docx 第 32 段
  #   族語原句：Ini usa miying saw ey hana ey mangalku lukih da
  #   詞素切割：ini usa miying saw ey hana ey m-angal=ku lukih da
  #   詞素翻譯：否定 去 主焦.尋找 像 填補詞 剛才 填補詞 主焦-拿=我.主格 傷口 了
  #   華語翻譯：我受傷了也不去就醫處理傷口
  # 例 3：魯凱族/霧台/1.包鳯嬌_Ripunu_耆老的尊榮冠冕.docx 第 12 段
  #   族語原句：lukai tadrusanay dringai
  #   詞素切割：lukai ta-drusa=nay dringai
  #   詞素翻譯：除非 數人-二=我們.包含.屬格 陷阱
  #   華語翻譯：除非我們一起放陷阱
  When 族語原句是 "Olito milihay"，詞素切割是 "Oli=to mi-lihay"
  Then 逐字比對通過

Scenario: 「.」在詞素切割時，可以把詞接在一起，當作詞組
  # 全語料有 250 段是這種情形（太魯閣 133 段、排灣 45 段、泰雅 72 段，阿美、魯凱沒有）。
  # 族語原句的兩個詞，詞素切割用 . 接成一個詞組（例如 kiya ni → kiya.ni），
  # 比對時 . 會被拿掉，字母序列一樣，詞數也照依附詞的方式算，所以通過。
  # 例 1（下面用這一段比對）：太魯閣族/1_劉珍玉_追述高添旺牧師（Wilang Takuh）.docx 第 1 段
  #   族語原句：kiya ni sayang o,
  #   詞素切割：kiya.ni sayang o
  #   詞素翻譯：所以 美好 助詞
  #   華語翻譯：所以，好喔
  # 例 2：排灣族/中排灣/2.廖桂香sakenge_廖進花-tinaqetaq 芋頭粉加花生粉蔬菜飯.docx 第 210 段
  #   族語原句：sa nu izua tja vurati ui,
  #   詞素切割：sa.nu izua tja=vurati ui
  #   詞素翻譯：然後 存在 我們.包含.屬格=地瓜 言談標記
  #   華語翻譯：那如有地瓜，
  # 例 3：泰雅族/賽考利克/1_悠瑪阿給安_曾次妹Ciwas_我的媽媽(上).docx 第 72 段
  #   族語原句：nanu yasa,
  #   詞素切割：nanu.yasa
  #   詞素翻譯：所以
  #   華語翻譯：所以
  When 族語原句是 "kiya ni sayang o,"，詞素切割是 "kiya.ni sayang o"
  Then 逐字比對通過

Scenario: 「+」在詞素切割時，可以把族語原句的詞接在一起，但僅限泰雅語
  # 全語料只有泰雅語的詞素切割有 +，共 352 段；其他語言都沒有，所以沒有反例。
  # 這 352 段裡，族語原句是兩個詞、詞素切割用 + 接成一個詞，其他字母都一樣的，只有 1 段（下面的例 1）。
  # 其他的 + 多半是族語原句發音現象合併、詞素切割寫完整形（lga → la+ga，246 個詞），
  # 字母本來就不一樣，不是這一條要處理的。
  # 例 1（下面用這一段比對）：泰雅族/賽考利克/2_黃美萍Sayta_翡束.寶給_泰雅族回娘家的四種回饋儀式.docx 第 62 段
  #   族語原句：satu "gayri, p'uma, pqlaq kawkna", saygu la ga, nanu la kya na ay!
  #   詞素切割：satu gayri p'uma p-qlaq kawkna saygu la+ga nanu la kya na ay
  #   詞素翻譯：主焦.送 回娘家.日語 主焦.回娘家 習俗名 最後.日語 助詞+助詞 所以 助詞 主焦.有 持續貌 驚嘆詞
  #   華語翻譯：satu geri, p'uma, pqlaq tawkan, 最後還有什麼呢？
  When 族別是 "泰雅"，族語原句是 "satu "gayri, p'uma, pqlaq kawkna", saygu la ga, nanu la kya na ay!"，對應詞素切割是 "satu gayri p'uma p-qlaq kawkna saygu la+ga nanu la kya na ay"
  Then 逐字比對通過

Scenario: 「-」在詞素切割時，不可以把族語原句的詞接在一起
  # 全語料有 169 段是這種情形（阿美 37 段、排灣 120 段、布農 11 段、魯凱 1 段）。
  # - 是詞綴的切割符號，詞綴跟詞根本來就是同一個詞；
  # 族語原句寫成兩個詞、詞素切割用 - 接起來，表示兩行對詞的認定不一樣，算不符。
  # 例 1（下面用這一段比對）：阿美族/秀姑巒/陳美莉_阿星.阿曼_說族語在大漢部落的過.docx 第 38 段
  #   族語原句：pacaof sa ko matoasay sano Holam a pacaf to no pilicay no wawa
  #   詞素切割：pa-caof sa ko matoasay sano-Holam a pacaf to no pi-licay no wawa
  #   詞素翻譯：使動-回覆 如此說 主格 老人 像-族名 連繫詞 回覆 斜格 屬格 PI-問 屬格 孩子
  #   華語翻譯：長輩回應給晚輩也是華語的話
  # 例 2：魯凱族/茂林/1.陳雅苓Milrinu_劉勝記_茂林祈雨祭的由來.docx 第 93 段
  #   族語原句：amua na 2點 iya amua tatédra na ico mring midra la sa druru mua mia
  #   詞素切割：a-mua na 2點 iya a-mua ta-tédra na ico mring-midra la sa druru mua mia
  #   詞素翻譯：實現-去 言談標記 2點 也 實現-去 TA-沒有 言談標記 人 靜悄悄-未來-他.不可見.屬格 然後 才 可以 去 那樣
  #   華語翻譯：有時2點才去，就是沒有任何聲音才去
  # 例 3：排灣族/東排灣/2_阮翠芳Gesi_阮秀美_土坂派出所拘留所的故事.docx 第 17 段
  #   族語原句：ika a'en na sepuwalan
  #   詞素切割：ika=a'en na-se-puwalan
  #   詞素翻譯：否定=我.主格 完成貌-屬-清楚
  #   華語翻譯：我也不太清楚
  When 族語原句是 "pacaof sa ko matoasay sano Holam a pacaf to no pilicay no wawa"，詞素切割是 "pa-caof sa ko matoasay sano-Holam a pacaf to no pi-licay no wawa"
  Then 逐字比對不符，分類是 "詞數不同"

Scenario: 只差英文大小寫，算通過
  # 全語料有 125 段是這種情形（詞數一樣、只有大小寫不同）。
  # 詞素切割常把專有名詞、未分類詞綴寫成大寫。
  # 例 1（下面用這一段比對）：太魯閣族/1_黃麗俐Miring_胡月英Tku_生活中的氣候啟示.txt 第 20 段
  #   族語原句：Iq
  #   詞素切割：iq
  #   詞素翻譯：是
  #   華語翻譯：是
  # 例 2：魯凱族/霧台/1.包鳯嬌_Ripunu_耆老的尊榮冠冕.txt 第 182 段
  #   族語原句：lu ka wakela ki zinsiw ka kiathingathingale lripwa kay lialivarane
  #   詞素切割：lu KA wa-kela ki zinsiw ka ki-a-thinga-thingale lri-pwa kay lialivarane
  #   詞素翻譯：如果 KA 主動-來到 斜格 全省 斜格 被動-限定-重疊-知道 未來-放 這 蝴蝶
  #   華語翻譯：插飾蝴蝶除非有參加全省賽
  # 例 3：阿美族/秀姑巒/陳美莉_阿星.阿曼_說族語在大漢部落的過.txt 第 69 段
  #   族語原句：ano haen ko demak saka o no mako a pi建議
  #   詞素切割：ano haen ko demak saka o no mako a PI-建議
  #   詞素翻譯：如果 這樣 主格 工作 所以 名詞標記 屬格 我.所有格 連繫詞 PI-建議
  #   華語翻譯：如果這樣的情況持續著 我的建議是
  When 族語原句是 "Iq"，詞素切割是 "iq"
  Then 逐字比對通過

Scenario: 不符——只差單引號
  # 全語料有 189 段是這一類。
  # 排灣語 ODS 1-3 規定詞素切割的 [k] / ['] 要跟著族語原句的寫法，
  # 所以這一類多半是要決定哪一邊才對。單引號是喉塞音，
  # 是音位，不能忽略。
  # 例 1（下面用這一段比對）：阿美族/秀姑巒/陳美莉_阿星.阿曼_說族語在大漢部落的過.txt 第 91 段
  #   族語原句：ano caay kadodoen ita ko sowal no i fafaway
  #   詞素切割：ano caay ka-do'do-en=ita ko sowal no i fafaw-ay
  #   詞素翻譯：如果 不 KA-跟-受焦=咱們.包含.所有格 主格 話 屬格 介系詞 上游-實現
  #   華語翻譯：如果我們沒有依著長官的
  # 例 2：排灣族/東排灣/3_阮翠芳Gesi_鄭玉英_生命故事.txt 第 142 段
  #   族語原句：na mareka u aya
  #   詞素切割：na-mareka 'u=aya
  #   詞素翻譯：完成貌-一些 我.屬格=說
  #   華語翻譯：我的家人
  # 例 3：布農族/巒群/1_松念竹Akuan_全美玲_布農語近代影響及語言之重要和傳承.txt 第 153 段
  #   族語原句：haan
  #   詞素切割：ha'an
  #   詞素翻譯：介係詞
  #   華語翻譯：在...
  When 族語原句是 "ano caay kadodoen ita ko sowal no i fafaway"，詞素切割是 "ano caay ka-do'do-en=ita ko sowal no i fafaw-ay"
  Then 逐字比對不符，分類是 "只差單引號"
  And 差異是 "詞素切割多了「'」"

Scenario: 不符——阿美語的 ^ 是字母
  # 《原住民族語言書寫系統》（113 年修正）的阿美語，^ 是喉塞音字母，
  # 不是標點，所以跟單引號一樣不能忽略，多一個少一個都算不符。
  # ^ 不是單引號，所以分類算「只差一個字母」。
  # 全語料只有 1 段是這一類（另一段 Ma-so^so 族語原句也有 ^，比對通過）。
  # 例 1（下面用這一段比對）：阿美族/海岸/3_阿索.該拿Aso.Kaynga_胡春蘭Omos_回憶童年.docx 第 126 段
  #   族語原句：iya han tosa ko patang
  #   詞素切割：iya=han tosa ko pa^tang
  #   詞素翻譯：助語=如此說.受焦 二 主格 水桶.台語
  #   華語翻譯：就用兩個桶子
  When 族語原句是 "iya han tosa ko patang"，詞素切割是 "iya=han tosa ko pa^tang"
  Then 逐字比對不符，分類是 "只差一個字母"
  And 差異是 "詞素切割多了「^」"

Scenario: 不符——只差一個字母，列為待檢查。泰雅、太魯閣、賽德克，列通過。
  # 全語料有 944 段是這一類。
  # 多半是詞素切割時多打或漏打一個音，或是照發音改寫了拼法。
  # 例 1（下面用這一段比對）：阿美族/秀姑巒/陳美莉_阿星.阿曼_說族語在大漢部落的過.txt 第 62 段
  #   族語原句：caay katama masa mahatila
  #   詞素切割：caay ka-tama masa ma-ha-tira
  #   詞素翻譯：不 KA-正確 像 受焦-HA-那裡
  #   華語翻譯：這不是一個正確的方式
  # 例 2：太魯閣族/1_黃麗俐Miring_胡月英Tku_生活中的氣候啟示.txt 第 116 段
  #   族語原句：Shngiun da.
  #   詞素切割：shungi-un da
  #   詞素翻譯：忘記-受焦 了
  #   華語翻譯：忘記了
  # 例 3：魯凱族/霧台/2.包鳯嬌_Tuku_建築石板屋與傳說故事.txt 第 21 段
  #   族語原句：walibita
  #   詞素切割：wa-alibi=ta
  #   詞素翻譯：主動-石板屋=我們.包含.屬格
  #   華語翻譯：石板屋
  When 族語原句是 "caay katama masa mahatila"，詞素切割是 "caay ka-tama masa ma-ha-tira"
  Then 逐字比對不符，分類是 "只差一個字母"
  And 差異是 "「l」→「r」"
  And 嚴重度是 "不確定，待檢查"

Scenario: 不符——差 2-3 個字母。泰雅、太魯閣、賽德克，列通過。
  # 全語料有 619 段是這一類。
  # 通常是拼法慣例不同。
  # 例 1（下面用這一段比對）：阿美族/秀姑巒/陳美莉_阿星.阿曼_說族語在大漢部落的過.docx 第 43 段
  #   族語原句：aka pahdawen itini i wawa no mita
  #   詞素切割：aka pa-lahedaw-en itini i wawa no mita
  #   詞素翻譯：不能 使動-消失-受焦 在這裡 介系詞 孩子 屬格 我們.所有格
  #   華語翻譯：我們的語言將再孩子這一代消失了
  # 例 2：太魯閣族/1_黃麗俐Miring_胡月英Tku_生活中的氣候啟示.txt 第 117 段
  #   族語原句：Manu kido
  #   詞素切割：manu kiya.do
  #   詞素翻譯：什麼 助詞
  #   華語翻譯：因此
  # 例 3：魯凱族/霧台/3.包鳯嬌_Uselrepe_月桃文化及製作上集.txt 第 16 段
  #   族語原句：asilwiyane yai
  #   詞素切割：asi-lu-iya-ane yai
  #   詞素翻譯：為什麼-如果-說-名物化 主題標記
  #   華語翻譯：為何這樣說
  When 族語原句是 "aka pahdawen itini i wawa no mita"，詞素切割是 "aka pa-lahedaw-en itini i wawa no mita"
  Then 逐字比對不符，分類是 "差 2-3 個字母"
  And 差異是 "詞素切割多了「la」、詞素切割多了「e」"
  And 嚴重度是 "不確定，待檢查"

Scenario: 不符——長度差很多。泰雅、太魯閣、賽德克，列通過。
  # 全語料有 24 段是這一類。
  # 長度差四分之一以上，通常是詞素切割少了一整串
  # （或多了一整串），內容可能遺失。
  # 例 1（下面用這一段比對）：阿美族/秀姑巒/陳美莉_阿星.阿曼_說族語在大漢部落的過.txt 第 107 段
  #   族語原句：matiya o no 原民會 nikaorira
  #   詞素切割：ma-tiya o no 原民會
  #   詞素翻譯：主焦-那 名詞標記 屬格 原民會
  #   華語翻譯：像原民會
  # 例 2：太魯閣族/1_黃麗俐Miring_胡月英Tku_生活中的氣候啟示.txt 第 332 段
  #   族語原句：Maxun ta hida
  #   詞素切割：gimax-un=ta hiya.da
  #   詞素翻譯：混合-受焦=我們.包含.屬格 那
  #   華語翻譯：搭配在一起
  # 例 3：布農族/巒群/2_松念竹Akuan_全英輝_早期布農族人生活分享(婚姻、食物、生活).txt 第 110 段
  #   族語原句：pau qabas tu
  #   詞素切割：tupa'-un qabas tu
  #   詞素翻譯：說-受焦 以前 連繫詞
  #   華語翻譯：以前說
  When 族語原句是 "matiya o no 原民會 nikaorira"，詞素切割是 "ma-tiya o no 原民會"
  Then 逐字比對不符，分類是 "長度差很多"
  And 差異是 "詞素切割少了「nikaorira」"

Scenario: 只差標點，算通過，不記任何問題
  # 全語料有 628 段是這種情形。
  # 族語原句保留句讀、詞素切割不留，這正是預期的寫法。
  # 2026.09 會議案由五決議：詞素切割行不能有標點，
  # 所以族語原句有標點、詞素切割沒有，算通過，不記任何問題。
  # 例 1（下面用這一段比對）：阿美族/秀姑巒/陳美莉_阿星.阿曼_說族語在大漢部落的過.txt 第 21 段
  #   族語原句：tangasa anini wa.. 110 年
  #   詞素切割：tangasa anini wa 110 年
  #   詞素翻譯：到達 現在 助詞 110年
  #   華語翻譯：直到現在110年
  # 例 2：太魯閣族/1_黃麗俐Miring_胡月英Tku_生活中的氣候啟示.txt 第 16 段
  #   族語原句：Ah!
  #   詞素切割：ah
  #   詞素翻譯：嘆詞
  #   華語翻譯：啊!
  # 例 3：排灣族/東排灣/1_阮翠芳Gesi_高桂妹_80歲vuvu的傳說故事.txt 第 126 段
  #   族語原句：e.
  #   詞素切割：e
  #   詞素翻譯：填補詞
  #   華語翻譯：呃
  When 族語原句是 "tangasa anini wa.. 110 年"，詞素切割是 "tangasa anini wa 110 年"
  Then 逐字比對通過
  And 不記任何問題

Scenario: 只差空白，先算不通過
  # 全語料有 222 段是這種情形。
  # 族語原句黏成一個詞、詞素切割拆開（或相反），字母序列沒有變，
  # 可是詞的個數變了。依照「詞數要一個對一個、只有依附詞例外」，
  # 這種先算不通過。
  # 程式現在把空白當成忽略項、判成通過，所以這一條會紅——
  # 規格已經定了，程式還沒改。
  # 例 1（下面用這一段比對）：阿美族/秀姑巒/陳美莉_阿星.阿曼_說族語在大漢部落的過.txt 第 19 段
  #   族語原句：nikaorira
  #   詞素切割：nika orira
  #   詞素翻譯：但是 那
  #   華語翻譯：但是
  # 例 2：魯凱族/霧台/3.包鳯嬌_Uselrepe_月桃文化及製作上集.txt 第 132 段
  #   族語原句：pakatharirimadu
  #   詞素切割：pa-ka-thariri madu
  #   詞素翻譯：使役-靜態.非限定-好 某人要
  #   華語翻譯：要綁得很好
  # 例 3：排灣族/東排灣/2_阮翠芳Gesi_阮秀美_土坂派出所拘留所的故事.txt 第 139 段
  #   族語原句：masa na uli
  #   詞素切割：masa na-uli
  #   詞素翻譯：也許 完成貌-非實現
  #   華語翻譯：也許可能
  When 族語原句是 "nikaorira"，詞素切割是 "nika orira"
  Then 逐字比對不符，分類是 "詞數不同"

Scenario: 不符——原句和切割要一致，要都是族語或都是華語。
  # 下面例 1 是標注者在詞素切割行寫詞源（族語原句的 moyi 寫成「母語」），
  # 例 1：阿美族/秀姑巒/陳美莉_阿星.阿曼_說族語在大漢部落的過.txt 第 111 段
  #   族語原句：awaay ko maan kita a caciyaw to no moyi
  #   詞素切割：awa-ay ko maan kita a caciyaw to no 母語
  #   詞素翻譯：沒有-實現 主格 什麼 咱們.包含.主格 連繫詞 說話 斜格 屬格 母語
  #   華語翻譯：我們的長輩們說母語是沒有問題的
  # 例 2：排灣族/南排灣/1_華加婧kivi_黃富_東源部落誌.docx 第 84 段
  #   族語原句：tjaivililj a sun-ciu
  #   詞素切割：tja-i-vililj a 村長
  #   詞素翻譯：比較-處所-後 主格 村長
  #   華語翻譯：後來的村長
  # 例 3：排灣族/南排灣/3_華加婧kivi_阮久祥_口述石門部落家族遷移及領域.docx 第 24 段
  #   族語原句：mamaw ta 'iningadanan nua sang-bu-tan,
  #   詞素切割：mamaw ta '<in>i-ngadan-an nua 上牡丹
  #   詞素翻譯：一樣 斜格 <受焦.完成貌>'I-名字-AN 屬格 上牡丹
  #   華語翻譯：像是取名上牡丹
  When 族語原句是 "awaay ko maan kita a caciyaw to no moyi"，詞素切割是 "awa-ay ko maan kita a caciyaw to no 母語"
  Then 逐字比對不符，分類是 "多處不同"
  And 差異是 "「moyi」→「母語」"

Scenario: 長音符號「:」，在詞素切割要保留
  # 兩行都保留（通過）：
  # 例 1（下面用這一段檢查）：阿美族/海岸/1_阿索.該拿Aso.Kaynga_文健站長輩的故事_難忘的歌曲_歌曲故事.docx 第 220 段
  #   族語原句：Raka:t sa haw
  #   詞素切割：Raka:t sa haw
  #   詞素翻譯：走 如此說 助詞
  #   華語翻譯：走(持續)著
  # 例 2：阿美族/海岸/1_阿索.該拿Aso.Kaynga_文健站長輩的故事_難忘的歌曲_歌曲故事.docx 第 155 段
  #   族語原句：Sa mahara:teng ako kona radiw i
  #   詞素切割：Sa ma-hara:teng=ako kona radiw i
  #   詞素翻譯：所以 主焦-想=我.屬格 這個.主格 歌 言談標記
  #   華語翻譯：所以每當我想到這首歌時
  # 例 3：阿美族/南勢/陳美莉_ 張輝國 Huyku_祭儀文化.docx 第 60 段
  #   族語原句：maha:en kiya kungku niya matuasay isaw
  #   詞素切割：ma-ha:en kiya kungku niya matuasay isaw
  #   詞素翻譯：主焦-這樣 助詞 故事 那.屬格 老人 助詞
  #   華語翻譯：長輩們說這些故事也久遠了
  #
  # 兩行不一致（錯誤，照常匯出）：
  # 例 1（下面用這一段檢查）：阿美族/秀姑巒/陳美莉_阿星.阿曼_說族語在大漢部落的過.docx 第 157 段
  #   族語原句：o wawa nangra haw mafokil to a caciyaw no mita o no Amis no Pangcah
  #   詞素切割：o wawa nangra haw ma-fo:kil=to a caciyaw no mita o no Amis no Pangcah
  #   詞素翻譯：名詞標記 孩子 他們.屬格 助詞 主焦-不會=完成 斜格 連繫詞 屬格 我們.包含.所有格 名詞標記 屬格 族名 屬格 族名
  #   華語翻譯：他們的孩子也不會說我們的阿美族語了
  # 例 2：阿美族/海岸/1_阿索.該拿Aso.Kaynga_文健站長輩的故事_難忘的歌曲_歌曲故事.docx 第 227 段
  #   族語原句：Tangic sa kako sa
  #   詞素切割：Ta-tangi:c kako sa
  #   詞素翻譯：重疊-哭 我.主格 這樣
  #   華語翻譯：我也一直這樣哭(持續哭)
  #   （這一段除了長音，還多了重疊的 ta、少了 sa，現在分類是「多處不同」）
  When 族語原句是 "Raka:t sa haw"，詞素切割是 "Raka:t sa haw"
  Then 逐字比對通過
  When 族語原句是 "o wawa nangra haw mafokil to a caciyaw no mita o no Amis no Pangcah"，詞素切割是 "o wawa nangra haw ma-fo:kil=to a caciyaw no mita o no Amis no Pangcah"
  Then 逐字比對不符，分類是 "只差長音符號"
  And 差異是 "詞素切割多了「:」"
  And 嚴重度是 "錯誤（照常匯出）"

Scenario: 詞素切割不應該寫拉長音的 == 符號
  # 全語料有 5 段是這一類。
  # 《常用構詞標記清單》各語言都有定義拉長音寫 ==（排灣語 1-5、
  # 阿美語 1-4、太魯閣語 1-4、布農語 1-6、泰雅語 1-4、霧台魯凱語 1-4）。
  # 排灣語 1-5 的「族語範例」與「詞素翻譯」兩欄都寫「不用標」，
  # 也就是 == 只該出現在第一行，第二、三行不用標。
  # 所以詞素切割看到拉長音的 == 就要回報。
  # 例 1：排灣族/南排灣/4_華加婧kivi_張枝妹_我來到牡丹的故事.txt 第 58 段
  #   族語原句：azua gaku lja== tutang, 'ata valji.
  #   詞素切割：azua gaku lja== tutang 'ata valji
  #   詞素翻譯：主格.那 學校 XX 鐵皮 和 木板
  #   華語翻譯：那個學校啊...是用鐵皮和木板蓋的
  #   對不起來的是：詞素切割「lja==」對詞素翻譯「XX」
  # 例 2：魯凱族/霧台/2.包鳯嬌_Tuku_建築石板屋與傳說故事.docx 第 105 段
  #   族語原句：ai~au~i
  #   詞素切割：ai==au==i
  #   詞素翻譯：啊伊==啊烏==伊
  #   華語翻譯：阿伊~阿烏~伊
  #   （族語原句用 ~，詞素切割與詞素翻譯都改寫成 ==）
  # 例 3：排灣族/中排灣/5.廖桂香sakenge_藍石化_生活甘苦談.docx 第 219 段
  #   族語原句：nu venangavangavang mun ta nu==
  #   詞素切割：nu v<en>anga-vangavang=mun ta nu==
  #   詞素翻譯：如果 <主焦>重疊-玩=你們.主格 斜格 你們.屬格
  #   華語翻譯：你們在照顧你們的…
  When 族語原句是 "azua gaku lja== tutang, 'ata valji."，詞素切割是 "azua gaku lja== tutang 'ata valji"
  Then 逐字比對不符，分類是 "詞素切割有拉長音"
  And 差異是 "詞素切割的「lja==」有拉長音「==」"
  And 嚴重度是 "錯誤"
