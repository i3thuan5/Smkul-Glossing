Feature: 排版分析

  更新日期：2026.11.19

  這一類會動到行的數量或段的切法，不改任何字。

  這一步只做排版分析：切出段、把折行接回四行（族語原句、詞素切割、詞素翻譯、
  華語翻譯）。四行的內容是族語還是華語都一樣分析，不在這一步判斷。
  「整段都是華語就不做詞素切割分析、整段丟掉」是下一步的事。

  附真實的例子當做討論的依據，
  例子照語言優先序挑：阿美（秀姑巒→海岸→南勢）→太魯閣→魯凱→排灣，
  內容都照語料原樣，半形全形都不改。只有一點：Gherkin 格式檢查不允許
  行尾空白與連續空行，所以區塊裡的這兩種空白有整理過，
  字本身沒有動。

Scenario: 檔頭註記收進 metadata
  # 全語料共 20 筆。
  # 例 1：魯凱族/霧台/3.包鳯嬌_Uselrepe_月桃文化及製作上集.txt
  #   原句子：1.
  #   處理後：收進檔頭註記 metadata
  # 例 2：排灣族/南排灣/3_華加婧kivi_阮久祥_口述石門部落家族遷移及領域.txt
  #   原句子：阮久祥 drumetj
  #   處理後：收進檔頭註記 metadata
  # 例 3：布農族/郡群/3.林美芳Abus_顏浩義_布農英雄Dahuali後裔對本家所遭遇之.txt
  #   原句子：.
  #   處理後：收進檔頭註記 metadata
  # 下面 When 用的是：排灣族/中排灣/1.廖桂香sakenge_劉清勇、李春花、曾秀玉_小米梗的用途.txt
  # 檔頭是該檔的前兩行，語料是同一個檔案的第 66 段（短句，詞素切割沒有換行）。
  # 檔頭的審閱進度、採集標題不是語料，但也不能丟掉。
  When 讀入這幾行
    """
    橘色 Megan 2026.3.5，
    Megan 檢視3.19
    66
    00:06:20,246 --> 00:06:22,849
    avan azua pay namaytazua
    avan         azua                 pay                 namaytazua
    就        主格.那        言談標記        這樣
    就是這樣
    """
  Then 檔頭註記是
    | 註記                  |
    | 橘色 Megan 2026.3.5， |
    | Megan 檢視3.19        |
  And 切出 1 段

Scenario: 短句照原樣切一段
  # 一般的四行段，沒有換行，不需要重組。
  # 出處：阿美族/秀姑巒/陳美莉_阿星.阿曼_說族語在大漢部落的過.txt 第 6 段
  When 讀入這幾行
    """
    6
    00:00:36,133 --> 00:00:39,428
    ca kahacowa ko tamdaw
    ca ka-hacowa ko tamdaw
    不 KA-多少 主格 人
    沒有多少人
    """
  Then 第 1 段重組後的詞素切割是 "ca ka-hacowa ko tamdaw"
  And 第 1 段重組後的詞素翻譯是 "不 KA-多少 主格 人"
  And 切出 1 段

Scenario: 長句換行重組——兩截
  # 全語料共 868 筆，其中兩截的有 806 筆，是最常見的排法。
  # 排法是：族語原句 +（詞素切割、詞素翻譯）× n + 華語翻譯，詞素切割與詞素翻譯交錯排。
  # 例 1：阿美族/秀姑巒/陳美莉_阿星.阿曼_說族語在大漢部落的過.txt 第 60 段
  #   原句子：pa-sowal=han to no wawa a o 要 那個=han ⏎ no wawa i
  #   處理後：pa-sowal=han to no wawa a o 要 那個=han no wawa i
  # 例 2：太魯閣族/1_黃麗俐Miring_胡月英Tku_生活中的氣候啟示.txt 第 50 段
  #   原句子：aw.bi hay=ta bi laqi ga hmut=ta ⏎ h<m>rapas ga
  #   處理後：aw.bi hay=ta bi laqi ga hmut=ta h<m>rapas ga
  # 例 3：魯凱族/霧台/1.包鳯嬌_Ripunu_耆老的尊榮冠冕.txt 第 115 段
  #   原句子：kai-n=aku 得名 kudra 個人的 ⏎ ai kudra 團體 第一名=nay
  #   處理後：kai-n=aku 得名 kudra 個人的 ai kudra 團體 第一名=nay
  # 下面 When 用的是：阿美族/秀姑巒/陳美莉_阿星.阿曼_說族語在大漢部落的過.txt 第 54 段
  When 讀入這幾行
    """
    54
    00:04:50,169 --> 00:04:58,317
    deng itini i picodadan minanam ano icuwa to a mapatireng to
    deng itini i pi-codad-an mi-nanam ano icuwa=to
    僅僅 在這裡 介系詞 PI-書-處焦 主焦-學習 如果 在哪裡=完成貌
    a ma-pa-tireng=to
    連繫詞 受焦-使動-站立=完成貌
    只在學校設立了學習管道
    """
  Then 第 1 段重組後的詞素切割是 "deng itini i pi-codad-an mi-nanam ano icuwa=to a ma-pa-tireng=to"
  And 第 1 段重組後的詞素翻譯是 "僅僅 在這裡 介系詞 PI-書-處焦 主焦-學習 如果 在哪裡=完成貌 連繫詞 受焦-使動-站立=完成貌"
  And 切出 1 段

Scenario: 長句換行重組——三截
  # 全語料共 57 筆。截數再多也是同一個規則，四截的有 3 筆。
  # 出處：排灣族/中排灣/4.廖桂香sakenge_李春花_往生者的處置.txt 第 91 段
  When 讀入這幾行
    """
    91
    00:06:39,999 --> 00:06:45,005
    iniya iniya e sipatevelj ta pacaceveljan azua mangudrangudrav auta,
    iniya iniya e si-pa-tevelj
    否定 否定 填補詞 參焦-使役-聚集
    ta pa-sa-cevelj-an azua
    斜格 使役-去-埋-處焦 主格.那
    ma-ngudra-ngudrav  auta
    主焦-重疊-神智不清 也
    不會將精神有問題的往生者同放在墓園，
    """
  Then 第 1 段重組後的詞素切割是 "iniya iniya e si-pa-tevelj ta pa-sa-cevelj-an azua ma-ngudra-ngudrav auta"
  And 第 1 段重組後的詞素翻譯是 "否定 否定 填補詞 參焦-使役-聚集 斜格 使役-去-埋-處焦 主格.那 主焦-重疊-神智不清 也"
  And 切出 1 段

Scenario: 全華語句照樣分析成四行
  # 受訪者講華語的句子，四行都是同一句華語。
  # 排版分析這一步只管切段與四行的對位，不管內容是族語還是華語，
  # 所以全華語句一樣分析成四行。「整段都是華語就不做詞素切割分析、
  # 整段丟掉」是下一步的事，不在這個 Feature 的範圍。
  # 出處：阿美族/海岸/1_阿索.該拿Aso.Kaynga_文健站長輩的故事_難忘的歌曲_歌曲故事.txt 第 56 段
  When 讀入這幾行
    """
    56
    0:03:53.960,0:03:55.560
    來!坐在我旁邊
    來!坐在我旁邊
    來!坐在我旁邊
    來!坐在我旁邊
    """
  Then 切出 1 段
  And 第 1 段重組後的詞素切割是 "來!坐在我旁邊"
  And 第 1 段重組後的詞素翻譯是 "來!坐在我旁邊"

Scenario: 短句、長句、華語排在一起也切得開
  # 三種排法接連出現時，長句的重組不可以影響到前後兩段的切法。
  # 出處：魯凱族/霧台/1.包鳯嬌_Ripunu_耆老的尊榮冠冕.txt 第 38～40 段，
  # 是同一個檔案裡連續的三段：短句、全華語句、長句換行。
  # 全語料三種連續出現的地方共 66 處（排灣 35、布農 22、泰雅 8、
  # 魯凱 1），阿美與太魯閣沒有，所以照語言優先序取魯凱這一段。
  When 讀入這幾行
    """
    38.
    02:30:29-02:34:21
    la takalranay ku siningdange ka swa  Adiri
    la takalra=nay ku singidange ka swa   Adiri
    然後 多=我們.排除.屬格 屬格 青年服務隊.日語  關係詞 來自 地名
    我們阿禮部落很多青年服務隊

    39.
    02:34:21-02:38:08
    有三個分隊集合時有一百多個人
    有三個分隊集合時有一百多個人
    有三個分隊集合時有一百多個人
    有三個分隊集合時有一百多個人

    40.
    02:38:08-02:43:05
    la amaniaku ka tarabulrubulru kwini sakengdridringane
    la         amani=aku         ka         tara-bulru-bulru
    然後         是=我.主格         斜格         專門-重疊-教
    kwini                 ta-keng<dri>dringi-ane
    那.可見.近指         非未來-<重疊>訓練-名物化
    訓練是我在教
    """
  Then 切出 3 段
  And 第 1 段重組後的詞素切割是 "la takalra=nay ku singidange ka swa Adiri"
  And 第 2 段重組後的詞素切割是 "有三個分隊集合時有一百多個人"
  And 第 3 段重組後的詞素切割是 "la amani=aku ka tara-bulru-bulru kwini ta-keng<dri>dringi-ane"

Scenario: 段間缺空行照常切段
  # 全語料共 131 筆。
  # 例 1：阿美族/海岸/1_阿索.該拿Aso.Kaynga_文健站長輩的故事_難忘的歌曲_歌曲故事.txt 第 207 段
  #   原句子：不知道我們是走到那個 ⏎ 208.
  #   處理後：視為兩段，不依賴空行
  # 例 2：太魯閣族/1_黃麗俐Miring_胡月英Tku_生活中的氣候啟示.txt 第 8 段
  #   原句子：好的, 我來教妳啦! ⏎ 9.
  #   處理後：視為兩段，不依賴空行
  # 例 3：魯凱族/霧台/2.包鳯嬌_Tuku_建築石板屋與傳說故事.txt 第 10 段
  #   原句子：我們如何才能擁有住的地方 ⏎ 12.
  #   處理後：視為兩段，不依賴空行
  # 下面 When 用的是：太魯閣族/1_黃麗俐Miring_胡月英Tku_生活中的氣候啟示.txt 第 8、9 段
  # 第 8 段的華語翻譯行後面直接接第 9 段的編號，中間沒有空行。
  # 段界看編號行與時間碼行，不依賴段間的空行。
  When 讀入這幾行
    """
    8.
    0:00:16.944,0:00:19.682
    Iq wa, tgsai nisu wa!
    Iq   wa             tgsa-i=nisu
    是  嘆詞         教導-受處焦.祈使=你.所有格   嘆詞
    好的, 我來教妳啦!
    9.
    0:00:19.682,0:00:20.816
    Iq, kiya.
    iq       kiya.
    是      好的
    是, 好的.
    """
  Then 切出 2 段

Scenario: 內文 5 行以上的段，排法彙總
  # 已經有規則的：
  #   806 族族華族華華          長句換行，兩截
  #    57 族族華族華族華華      長句換行，三截
  #     3 族族華族華族華族華華  長句換行，四截
  #    35 族族華華族族華華      對話段
  # 下面這些還沒有規則，程式一律判成「行黏在一起」或「缺詞素翻譯行」：
  #    48 族族華華華            詞素切割行或詞素翻譯行被折行，兩邊對不起來
  #    11 族族族華華            詞素翻譯行尾黏著下一截的詞素切割
  #    11 族族華華華華          詞素翻譯行折行，而且有重複
  #     7 族族華族族華          詞素翻譯行含大寫標記，被判成拉丁行
  #     4 族族華族華            五行，缺一行
  #     4 族族華族族華華
  #     3 族族華族華華華
  #     2 族族華華族
  # 下面 When 用的是 48 筆那一種：
  # 排灣族/東排灣/1_阮翠芳Gesi_高桂妹_80歲vuvu的傳說故事.txt 第 4 段
  # 詞素切割行是 "lu-kai-i=amen a"，被折成兩行；詞素翻譯也被折成兩行，
  # 而且兩邊的折點不一樣，所以接不回去。
  When 讀入這幾行
    """
    4
    0:00:09.960,0:00:12.280
    lukaivi amen a
    lu-kai-i=amen                           a
    習慣貌-話-V
    祈使=我們.主格  填補詞
    跟我們說啊
    """
  Then 切出 1 段
  And 第 1 段被判成「行黏在一起」

Scenario: 對話段——一段裡面兩位說話者各一套四行，切成 2 段
  # 排法是 四行 + 四行，每一行前面都有說話者標記（Y:／H:／Yu:／Ci:……），
  # 前四行是一位說話者，後四行是另一位。這不是長句換行，是兩個人各講一句，
  # 所以接受，切成 2 段，每段各自是一套四行。
  # 排版分析不改字，說話者標記照樣留在每一行。
  # 例 1：阿美族/南勢/3.陳美莉_張輝國 Huyku_水璉部落年齡.docx 第 13 段
  #   Y 問：pina kiya selal namu（你們年齡階級有幾個）
  #   H 答：siwa ku nu niyam nu Pangcah i naayaw（我們阿美族以前是九個）
  # 例 2：泰雅族/賽考利克/2_悠瑪阿給安_曾次妹Ciwas_我的媽媽(下).docx 第 157 段
  #   Yu：yasa blaq ru（這樣很好啊）
  #   Ci：aw ru（是啊）
  # 例 3：阿美族/海岸/1_阿索.該拿Aso.Kaynga_文健站長輩的故事_難忘的歌曲_歌曲故事.docx 第 166 段
  #   S：Nga'ay ho nga'ay=ho（您好! 您好!）
  #   A：Nga'ay ho nga'ay=ho（您好! 您好!）
  When 讀入這幾行
    """
    13
    00:00:47,680 --> 00:00:55,563
    Y: pina kiya selal namu
    Y: pina kiya selal namu
    Y: 多少 助詞 同輩 你們.所有格
    Y: 你們年齡階級有幾個
    H: siwa ku nu niyam nu Pangcah i naayaw
    H: siwa ku nu niyam nu Pangcah i na-ayaw
    H: 九 主格 屬格 我們.排除.屬格 屬格 族名 介系詞 從-前
    H:我們阿美族以前是九個
    """
  Then 切出 2 段
  And 第 1 段重組後的族語原句是 "Y: pina kiya selal namu"
  And 第 1 段重組後的詞素切割是 "Y: pina kiya selal namu"
  And 第 1 段重組後的詞素翻譯是 "Y: 多少 助詞 同輩 你們.所有格"
  And 第 1 段重組後的華語翻譯是 "Y: 你們年齡階級有幾個"
  And 第 2 段重組後的族語原句是 "H: siwa ku nu niyam nu Pangcah i naayaw"
  And 第 2 段重組後的詞素切割是 "H: siwa ku nu niyam nu Pangcah i na-ayaw"
  And 第 2 段重組後的詞素翻譯是 "H: 九 主格 屬格 我們.排除.屬格 屬格 族名 介系詞 從-前"
  And 第 2 段重組後的華語翻譯是 "H:我們阿美族以前是九個"

Scenario: 同一組，有2個發音人，算合法，切成 2 段
  # 全語料有 10 段是這種排法，都在排灣族/南排灣
  # 族語原句、華語翻譯各只有一行，詞素切割與詞素翻譯卻是一位說話者一組，
  # 每組前面有說話者標記（K:／Lj:／k:／dr:）。
  # 這是兩位發音人一問一答，接受，照說話者換手切段：
  #   詞素切割、詞素翻譯：照說話者標記分組，一組一段，標記照樣留著（排版分析不改字）。
  #   族語原句、華語翻譯：有說話者標記就照標記切；沒有標記的，括號裡是前一位說話者的話。
  # 說話者換手兩次以上的（例如 K → Lj → K → Lj）就切成更多段，這 10 段裡有 4 段是這樣。
  # 例 1（下面用這一段）：排灣族/南排灣/4_華加婧kivi_張枝妹_我來到牡丹的故事.docx 第 114 段
  #   族語原句：(anema aya tjen ta azua?) 電土 ayain sicuayan
  #   詞素切割：K: anema aya=tjen ta azua? ⏎ Lj: 電土 aya-in sicuayan
  #   詞素翻譯：K: 什麼 說=我們.主格 斜格 主格.那 ⏎ Lj: 電土 說-受焦 從前
  #   華語翻譯：(那是什麼?) 我們以前叫那個"電土"
  # 例 2：排灣族/南排灣/4_華加婧kivi_張枝妹_我來到牡丹的故事.docx 第 151 段（族語原句有說話者標記）
  #   族語原句：K: tu sikuda azua? Lj: 'u qentj-an== e 漫畫
  #   詞素切割：K: tu si-kuda azua? ⏎ Lj: 'u=qentj-an e 漫畫
  #   詞素翻譯：K: 補語連詞 參焦.工具-如何 斜格.那 ⏎ Lj: 我.屬格=看-AN 填補詞 漫畫
  #   華語翻譯：(那是做什麼的?) 我拿來看啊...漫畫
  # 例 3：排灣族/南排灣/3_華加婧kivi_阮久祥_口述石門部落家族遷移及領域.docx 第 10 段（華語翻譯有說話者標記）
  #   族語原句：(izua anga caceveljan tazua?) izua anga
  #   詞素切割：k: i.zua=anga ca-cevelja-an tazua ⏎ dr: i.zua=anga
  #   詞素翻譯：k: 存在=完成貌 重疊-埋-處焦 那時 ⏎ dr: 存在=完成貌
  #   華語翻譯：k: 當時已經有墳墓了嗎? dr: 已經有了
  When 讀入這幾行
    """
    114.
    0:09:55.806,0:09:58.812
    (anema aya tjen ta azua?) 電土 ayain sicuayan
    K: anema aya=tjen ta azua?
    K: 什麼 說=我們.主格 斜格 主格.那
    Lj: 電土 aya-in sicuayan
    Lj: 電土 說-受焦 從前
    (那是什麼?) 我們以前叫那個"電土"
    """
  Then 切出 2 段
  And 第 1 段重組後的族語原句是 "(anema aya tjen ta azua?)"
  And 第 1 段重組後的詞素切割是 "K: anema aya=tjen ta azua?"
  And 第 1 段重組後的詞素翻譯是 "K: 什麼 說=我們.主格 斜格 主格.那"
  And 第 1 段重組後的華語翻譯是 "(那是什麼?)"
  And 第 2 段重組後的族語原句是 "電土 ayain sicuayan"
  And 第 2 段重組後的詞素切割是 "Lj: 電土 aya-in sicuayan"
  And 第 2 段重組後的詞素翻譯是 "Lj: 電土 說-受焦 從前"
  And 第 2 段重組後的華語翻譯是 "我們以前叫那個"電土""

Scenario: 最後 1 行強制當成華語
  # 華語翻譯行夾著族語的人名、地名、家族名時，小寫拉丁字母可能比漢字多，
  # 照字數會被判成族語行。可是段的最後 1 行一定是華語翻譯，所以強制當成華語。
  # 全語料有 25 段是這種排法（族族華族華族：長句換行兩截，最後 1 行被判成族語），
  # 布農 11 段、排灣 6 段、魯凱 4 段、泰雅 4 段，阿美、太魯閣沒有。
  # 例 1（下面用這一段）：魯凱族/霧台/3.包鳳嬌_Uselrepe_月桃的文化及製作_上集.docx 第 136 段
  #   原句子：早期我們去Kudrengedrenge、Lrukulruku（小寫拉丁 22 個、漢字 5 個）
  #   處理後：當成華語翻譯，詞素切割與詞素翻譯照兩截接回去
  # 例 2：排灣族/中排灣/1.廖桂香sakenge_劉清勇、李春花、曾秀玉_小米梗的用途.docx 第 5 段
  #   原句子：然後我記錄在kukubang上，（小寫拉丁 8 個、漢字 7 個）
  #   處理後：當成華語翻譯，詞素切割與詞素翻譯照兩截接回去
  # 例 3：布農族/郡群/5_林美芳Abus_韃虎‧伊斯瑪哈單‧伊斯立端_islituan家族.docx 第 356 段
  #   原句子：所以他的後代子孫叫takismaikilian家族（小寫拉丁 14 個、漢字 11 個）
  #   處理後：當成華語翻譯，詞素切割與詞素翻譯照兩截接回去
  When 讀入這幾行
    """
    136.
    0:13:03.923,0:13:11.600
    ku nadrwadruma amwanay kay kudrengedrenge Lrukulruku si
    ku  na<drwa>druma am-ua=nay
    斜格  <重疊>早期   限定-去=我們.排除.主格
    kay  Kudrengedrenge  Lrukulruku  si
    這  地名    地名   和
    早期我們去Kudrengedrenge、Lrukulruku
    """
  Then 切出 1 段
  And 第 1 段重組後的詞素切割是 "ku na<drwa>druma am-ua=nay kay Kudrengedrenge Lrukulruku si"
  And 第 1 段重組後的詞素翻譯是 "斜格 <重疊>早期 限定-去=我們.排除.主格 這 地名 地名 和"
  And 第 1 段重組後的華語翻譯是 "早期我們去Kudrengedrenge、Lrukulruku"

Scenario: 判斷族語還是華語的時候，把大寫標記認為華語
  # 規格：判斷一行是族語行（族語原句、詞素切割）還是華語行（詞素翻譯、華語翻譯），
  # 因為詞素翻譯行有許多的寫寫標記（PI、KA、AN、SI'A……）照 ODS 1-2
  # 全語料有 13 段是靠這條規格才接得回去，例如：
  #   排灣族/中排灣/2.廖桂香sakenge_廖進花-tinaqetaq 芋頭粉加花生粉蔬菜飯.txt 第 176 段
  #     詞素翻譯行是 "PA-暫時"：大寫 2 個、漢字 2 個
  #   排灣族/中排灣/3.廖桂香Sakenge_Selep Ruviljivili_生活經歷.txt 第 203 段
  #     詞素翻譯行是 "SI'A-NA-好        斜格        身體"：大寫 5 個、漢字 4 個
  # 出處：排灣族/東排灣/1_阮翠芳Gesi_高桂妹_80歲vuvu的傳說故事.txt 第 268 段
  #   詞素翻譯行是 "探訪-AN"：小寫 0 個、大寫 2 個、漢字 2 個，算漢字行。
  When 讀入這幾行
    """
    268
    0:11:26.400,0:11:27.300
    paljiljian
    paljilji-an
    探訪-AN
    夫妻就去看
    """
  Then 切出 1 段
  And 第 1 段重組後的詞素切割是 "paljilji-an"
  And 第 1 段重組後的詞素翻譯是 "探訪-AN"
