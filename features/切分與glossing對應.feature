Feature: 切分與 glossing 的對應

  更新日期：2026.8.22

  切分行與 gloss 行要**一個詞對一個詞**，而且每個詞裡面的構詞符號
  （- = <> ~）位置與個數也要一樣，詞素才對得起來。

  第一條是對應正常的情形，後面幾條是對不起來的細分類。
  標 @規格要討論 的排在最後面，那一條的規格還沒有共識。

  例子照語言優先序挑：阿美（秀姑巒→海岸→南勢）→太魯閣→魯凱→排灣，
  內容都照語料原樣，半形全形都不改。

Scenario: 對應正常：詞數一樣，符號位置也一樣
  # 切分的每一個符號，gloss 同一個位置也要有。
  # 例 1（下面用這一組比對）：阿美族/秀姑巒/陳美莉_阿星.阿曼_說族語在大漢部落的過.txt 第 147 組
  #   族語原文：masaromaay to
  #   切分：ma-sa-roma-ay=to
  #   glossing：受焦-工具焦-另外-實現=完成貌
  #   翻譯：就有改變了
  # 例 2：太魯閣族/1_黃麗俐Miring_胡月英Tku_生活中的氣候啟示.txt 第 169 組
  #   族語原文：Hmuya?
  #   切分：h<m>uya
  #   glossing：<主焦>如何
  #   翻譯：做什麼?
  # 例 3：魯凱族/霧台/2.包鳯嬌_Tuku_建築石板屋與傳說故事.txt 第 21 組
  #   族語原文：walibita
  #   切分：wa-alibi=ta
  #   glossing：主動-石板屋=我們.包含.屬格
  #   翻譯：石板屋
  When 切分行是 "ma-sa-roma-ay=to"，gloss 行是 "受焦-工具焦-另外-實現=完成貌"
  Then 對應通過

Scenario: 不對應——gloss 的詞比切分少
  # 全語料有 254 組是這一類。
  # 多半是 gloss 兩個詞黏成一個，或是漏標了一段。
  # 例 1（下面用這一組比對）：阿美族/秀姑巒/陳美莉_阿星.阿曼_說族語在大漢部落的過.txt 第 27 組
  #   族語原文：nawhani halafin to ko aro itini
  #   切分：nawhani ha-lafin=to ko aro itini
  #   glossing：因為HA-過夜=完成貌 主格 居住 在這裡
  #   翻譯：在這住很久了
  #   切分 5 個詞，gloss 4 個詞
  # 例 2：太魯閣族/1_黃麗俐Miring_胡月英Tku_生活中的氣候啟示.txt 第 140 組
  #   族語原文：Ha ha ha
  #   切分：ha ha ha
  #   glossing：擬聲
  #   翻譯：哈哈哈
  #   切分 3 個詞，gloss 1 個詞
  # 例 3：魯凱族/霧台/1.包鳯嬌_Ripunu_耆老的尊榮冠冕.txt 第 59 組
  #   族語原文：la papisadra nakwane
  #   切分：la pa-pisadra nakuane
  #   glossing：然後 使役-卸任-我.斜格
  #   翻譯：才讓我卸任
  #   切分 3 個詞，gloss 2 個詞
  When 切分行是 "nawhani ha-lafin=to ko aro itini"，gloss 行是 "因為HA-過夜=完成貌 主格 居住 在這裡"
  Then 對應不符，分類是 "gloss 的詞比切分少"

Scenario: 不對應——gloss 的詞比切分多
  # 全語料有 116 組是這一類。
  # 多半是 gloss 多切了一刀，或是切分兩個詞黏成一個。
  # 例 1（下面用這一組比對）：阿美族/海岸/3_阿索.該拿Aso.Kaynga_胡春蘭Omos_回憶童年.txt 第 311 組
  #   族語原文：mafana' ci mira
  #   切分：ma-fana' ci mira
  #   glossing：主焦-會 主格 主格 他.所有格
  #   翻譯：他都會
  #   切分 3 個詞，gloss 4 個詞
  # 例 2：太魯閣族/1_黃麗俐Miring_胡月英Tku_生活中的氣候啟示.txt 第 200 組
  #   族語原文："Aji su ka phuqil"
  #   切分：aji=su ka p-huqil
  #   glossing：否定=你.主格 主格 使動- 死
  #   翻譯："妳不至於餓死"母親說
  #   切分 3 個詞，gloss 4 個詞
  # 例 3：魯凱族/霧台/1.包鳯嬌_Ripunu_耆老的尊榮冠冕.txt 第 122 組
  #   族語原文：la sudalepaku sibengelray
  #   切分：la sudalepe=aku si-bengelray
  #   glossing：然後 資格=我.主格 戴- 花
  #   翻譯：所以我已配得戴百合花
  #   切分 3 個詞，gloss 4 個詞
  When 切分行是 "ma-fana' ci mira"，gloss 行是 "主焦-會 主格 主格 他.所有格"
  Then 對應不符，分類是 "gloss 的詞比切分多"

Scenario: 不對應——切分沒有切，gloss 有切
  # 全語料有 75 組是這一類。
  # 切分那個詞沒有構詞符號，gloss 卻切成好幾段。
  # 多半是切分漏切。
  # 例 1（下面用這一組比對）：阿美族/秀姑巒/陳美莉_阿星.阿曼_說族語在大漢部落的過.txt 第 53 組
  #   族語原文：o no mako a pitapal haw i
  #   切分：o no mako a pitapal haw i
  #   glossing：名詞標記 屬格 我.所有格 連繫詞 PI-發現 助詞 言談標記
  #   翻譯：據我的觀察
  #   對不起來的是：切分「pitapal」對 gloss「PI-發現」
  # 例 2：太魯閣族/1_黃麗俐Miring_胡月英Tku_生活中的氣候啟示.txt 第 391 組
  #   族語原文：Taan ta ga ida ki manu sdara kana quwaq dha
  #   切分：qita-an=ta ga ida ki manu sdara kana quwaq=dha
  #   glossing：看-處焦=他們.屬格 那 一定 填補詞 什麼 S-血 全部 嘴巴=他們.屬格
  #   翻譯：看見他們的嘴邊沾滿了山肉血
  #   對不起來的是：切分「sdara」對 gloss「S-血」
  # 例 3：魯凱族/霧台/3.包鳯嬌_Uselrepe_月桃文化及製作上集.txt 第 20 組
  #   族語原文：la kathiriri lu susaliane
  #   切分：la ka-thiriri lu su-sali-ane
  #   glossing：然後 靜態-非限定-好 如果 剝-月桃-名物化
  #   翻譯：剝開時才會很好
  #   對不起來的是：切分「ka-thiriri」對 gloss「靜態-非限定-好」
  When 切分行是 "o no mako a pitapal haw i"，gloss 行是 "名詞標記 屬格 我.所有格 連繫詞 PI-發現 助詞 言談標記"
  Then 對應不符，分類是 "切分沒有切，gloss 有切"
  And 對不起來的是切分 "pitapal" 對 gloss "PI-發現"

Scenario: 不對應——切分有切，gloss 沒有切
  # 全語料有 98 組是這一類。
  # 切分把詞切成好幾段，gloss 卻只寫一段。
  # 多半是 gloss 漏切。
  # 例 1（下面用這一組比對）：阿美族/秀姑巒/陳美莉_阿星.阿曼_說族語在大漢部落的過.txt 第 156 組
  #   族語原文：o malinahay itini o ciwawa to
  #   切分：o ma-linah-ay itini o ci-wawa=to
  #   glossing：名詞標記 主焦-搬遷 在這裡 名詞標記 有-孩子=完成貌
  #   翻譯：搬到這裡 所生下的小孩
  #   對不起來的是：切分「ma-linah-ay」對 gloss「主焦-搬遷」
  # 例 2：太魯閣族/1_黃麗俐Miring_胡月英Tku_生活中的氣候啟示.txt 第 5 組
  #   族語原文：Mmeenu karat o
  #   切分：m~meenu karat o
  #   glossing：什麼樣 天氣 主題
  #   翻譯：什麼樣的氣候變化
  #   對不起來的是：切分「m~meenu」對 gloss「什麼樣」
  # 例 3：魯凱族/霧台/1.包鳯嬌_Ripunu_耆老的尊榮冠冕.txt 第 13 組
  #   族語原文：kudra aningiaalupunga amia
  #   切分：kudra ani-ngi-a-alupu=nga amia
  #   glossing：那.不可見.遠指 願-打獵=完成貌 說
  #   翻譯：他說以後自己去打獵
  #   對不起來的是：切分「ani-ngi-a-alupu=nga」對 gloss「願-打獵=完成貌」
  When 切分行是 "o ma-linah-ay itini o ci-wawa=to"，gloss 行是 "名詞標記 主焦-搬遷 在這裡 名詞標記 有-孩子=完成貌"
  Then 對應不符，分類是 "切分有切，gloss 沒有切"
  And 對不起來的是切分 "ma-linah-ay" 對 gloss "主焦-搬遷"

Scenario: 不對應——符號的種類不一樣
  # 全語料有 82 組是這一類。
  # 個數一樣，可是切分用的符號與 gloss 用的不同，
  # 例如切分用 -、gloss 用 =。詞素的接法會對不起來。
  # 例 1（下面用這一組比對）：阿美族/秀姑巒/陳美莉_阿星.阿曼_說族語在大漢部落的過.txt 第 124 組
  #   族語原文：tangasa anini malamama to ina to i hato mahaen to
  #   切分：tangasa anini mala-mama=to ina=to i hato ma-haen=to
  #   glossing：到達 現在 成為=爸爸=完成貌 媽媽=完成貌 言談標記 好像 受焦-這樣=完成貌
  #   翻譯：現在都當爸爸 媽媽了 現在都這樣
  #   對不起來的是：切分「mala-mama=to」對 gloss「成為=爸爸=完成貌」
  # 例 2：太魯閣族/1_黃麗俐Miring_胡月英Tku_生活中的氣候啟示.txt 第 176 組
  #   族語原文：Uqun ta nanak kndaxan siida ga, kndaxan ta o
  #   切分：uq-un=ta nanak kndaxan siida ga k<n>dax-an=ta o
  #   glossing：吃-受焦=我們.包含.屬格 自己 下午 當時 那 下午=我們.包含.屬格 主題
  #   翻譯：我們要先溫飽午餐
  #   對不起來的是：切分「k<n>dax-an=ta」對 gloss「下午=我們.包含.屬格」
  # 例 3：魯凱族/霧台/1.包鳯嬌_Ripunu_耆老的尊榮冠冕.txt 第 21 組
  #   族語原文：la kainaku temimi
  #   切分：la kai-n=aku te<ming>ming
  #   glossing：然後 否定-N-我.主格 <重疊>得名.華語
  #   翻譯：所以名次我沒再拿到
  #   對不起來的是：切分「kai-n=aku」對 gloss「否定-N-我.主格」
  When 切分行是 "tangasa anini mala-mama=to ina=to i hato ma-haen=to"，gloss 行是 "到達 現在 成為=爸爸=完成貌 媽媽=完成貌 言談標記 好像 受焦-這樣=完成貌"
  Then 對應不符，分類是 "符號的種類不一樣"
  And 對不起來的是切分 "mala-mama=to" 對 gloss "成為=爸爸=完成貌"

@規格要討論
Scenario: 拉長音的 == 被當成構詞符號
  # 全語料有 5 組是這一類。
  # 《常用構詞標記清單》各語言都有定義拉長音寫 ==（排灣語 1-5、
  # 阿美語 1-4、太魯閣語 1-4、布農語 1-6、泰雅語 1-4、霧台魯凱語 1-4）。
  # 排灣語 1-5 的「族語範例」與「詞素翻譯」兩欄都寫「不用標」，
  # 也就是 == 只該出現在第一行，第二、三行不用標。
  #
  # 語料的實際情形：== 出現在第一行 110 組（合規），
  # 可是第二行（切分）有 7 組、第三行（gloss）有 5 組。
  # 114 組裡有 109 組是排灣語。
  #
  # 所以這裡有兩件事要決定：
  #   1. 語料要不要把第二、三行的 == 拿掉（照 ODS 是要拿掉）。
  #   2. 在拿掉以前，程式看到 = 就當成依附詞，lja== 會被判成
  #      「符號不呼應」。程式要不要先把拉長音的 == 排除？
  # 例 1（下面用這一組比對）：排灣族/南排灣/4_華加婧kivi_張枝妹_我來到牡丹的故事.txt 第 58 組
  #   族語原文：azua gaku lja== tutang, 'ata valji.
  #   切分：azua gaku lja== tutang 'ata valji
  #   glossing：主格.那 學校 XX 鐵皮 和 木板
  #   翻譯：那個學校啊...是用鐵皮和木板蓋的
  #   對不起來的是：切分「lja==」對 gloss「XX」
  When 切分行是 "azua gaku lja== tutang 'ata valji"，gloss 行是 "主格.那 學校 XX 鐵皮 和 木板"
  Then 對應通過
