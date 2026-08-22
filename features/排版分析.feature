Feature: 排版分析

  更新日期：2026.8.22

  每一條是一個自動處理。Scenario 後面附真語料的例子當做討論的依據，
  When 是原本的內容，Then 是程式處理後的內容。

  例子照語言優先序挑：阿美（秀姑巒→海岸→南勢）→太魯閣→魯凱→排灣，
  內容都照語料原樣，半形全形都不改。只有一點：Gherkin 格式檢查不允許
  行尾空白與連續空行，所以 """ 區塊裡的這兩種空白有整理過，
  字本身沒有動。

  這一類會動到行的數量或組的切法，不改任何字。

  這一步只做排版分析：切出組、把折行接回四行（原文、切分、gloss、
  翻譯）。四行的內容是族語還是華語都一樣分析，不在這一步判斷。
  「整組都是華語就不做切分分析、整組丟掉」是下一步的事。

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
  # 檔頭是該檔的前兩行，語料是同一個檔案的第 66 組（短句，切分沒有換行）。
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
  And 切出 1 組

Scenario: 短句照原樣切一組
  # 一般的四行組，沒有分段，不需要重組。
  # 出處：阿美族/秀姑巒/陳美莉_阿星.阿曼_說族語在大漢部落的過.txt 第 6 組
  When 讀入這幾行
    """
    6
    00:00:36,133 --> 00:00:39,428
    ca kahacowa ko tamdaw
    ca ka-hacowa ko tamdaw
    不 KA-多少 主格 人
    沒有多少人
    """
  Then 第 1 組重組後的切分是 "ca ka-hacowa ko tamdaw"
  And 切出 1 組

Scenario: 長句分段重組——兩段
  # 全語料共 868 筆，其中兩段的有 806 筆，是最常見的排法。
  # 排法是：原文 +（切分、gloss）× n + 翻譯，切分與 gloss 交錯排。
  # 例 1：阿美族/秀姑巒/陳美莉_阿星.阿曼_說族語在大漢部落的過.txt 第 60 組
  #   原句子：pa-sowal=han to no wawa a o 要 那個=han ⏎ no wawa i
  #   處理後：pa-sowal=han to no wawa a o 要 那個=han no wawa i
  # 例 2：太魯閣族/1_黃麗俐Miring_胡月英Tku_生活中的氣候啟示.txt 第 50 組
  #   原句子：aw.bi hay=ta bi laqi ga hmut=ta ⏎ h<m>rapas ga
  #   處理後：aw.bi hay=ta bi laqi ga hmut=ta h<m>rapas ga
  # 例 3：魯凱族/霧台/1.包鳯嬌_Ripunu_耆老的尊榮冠冕.txt 第 115 組
  #   原句子：kai-n=aku 得名 kudra 個人的 ⏎ ai kudra 團體 第一名=nay
  #   處理後：kai-n=aku 得名 kudra 個人的 ai kudra 團體 第一名=nay
  # 下面 When 用的是：阿美族/秀姑巒/陳美莉_阿星.阿曼_說族語在大漢部落的過.txt 第 54 組
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
  Then 第 1 組重組後的切分是 "deng itini i pi-codad-an mi-nanam ano icuwa=to a ma-pa-tireng=to"
  And 第 1 組重組後的 gloss 是 "僅僅 在這裡 介系詞 PI-書-處焦 主焦-學習 如果 在哪裡=完成貌 連繫詞 受焦-使動-站立=完成貌"
  And 切出 1 組

Scenario: 長句分段重組——三段
  # 全語料共 57 筆。段數再多也是同一個規則，四段的有 3 筆。
  # 出處：排灣族/中排灣/4.廖桂香sakenge_李春花_往生者的處置.txt 第 91 組
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
  Then 第 1 組重組後的切分是 "iniya iniya e si-pa-tevelj ta pa-sa-cevelj-an azua ma-ngudra-ngudrav auta"
  And 切出 1 組

Scenario: 全華語句照樣分析成四行
  # 受訪者講華語的句子，四行都是同一句華語。
  # 排版分析這一步只管切組與四行的對位，不管內容是族語還是華語，
  # 所以全華語句一樣分析成四行。「整組都是華語就不做切分分析、
  # 整組丟掉」是下一步的事，不在這個 Feature 的範圍。
  # 出處：阿美族/海岸/1_阿索.該拿Aso.Kaynga_文健站長輩的故事_難忘的歌曲_歌曲故事.txt 第 56 組
  When 讀入這幾行
    """
    56
    0:03:53.960,0:03:55.560
    來!坐在我旁邊
    來!坐在我旁邊
    來!坐在我旁邊
    來!坐在我旁邊
    """
  Then 切出 1 組
  And 第 1 組重組後的切分是 "來!坐在我旁邊"
  And 第 1 組重組後的 gloss 是 "來!坐在我旁邊"

Scenario: 短句、長句、華語排在一起也切得開
  # 三種排法接連出現時，長句的重組不可以影響到前後兩組的切法。
  # 出處：魯凱族/霧台/1.包鳯嬌_Ripunu_耆老的尊榮冠冕.txt 第 38～40 組，
  # 是同一個檔案裡連續的三組：短句、全華語句、長句分段。
  # 全語料三種連續出現的地方共 66 處（排灣 35、布農 22、泰雅 8、
  # 魯凱 1），阿美與太魯閣沒有，所以照語言優先序取魯凱這一組。
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
  Then 切出 3 組
  And 第 1 組重組後的切分是 "la takalra=nay ku singidange ka swa Adiri"
  And 第 2 組重組後的切分是 "有三個分隊集合時有一百多個人"
  And 第 3 組重組後的切分是 "la amani=aku ka tara-bulru-bulru kwini ta-keng<dri>dringi-ane"

Scenario: 組間缺空行照常切組
  # 全語料共 131 筆。
  # 例 1：阿美族/海岸/1_阿索.該拿Aso.Kaynga_文健站長輩的故事_難忘的歌曲_歌曲故事.txt 第 207 組
  #   原句子：不知道我們是走到那個 ⏎ 208.
  #   處理後：視為兩組，不依賴空行
  # 例 2：太魯閣族/1_黃麗俐Miring_胡月英Tku_生活中的氣候啟示.txt 第 8 組
  #   原句子：好的, 我來教妳啦! ⏎ 9.
  #   處理後：視為兩組，不依賴空行
  # 例 3：魯凱族/霧台/2.包鳯嬌_Tuku_建築石板屋與傳說故事.txt 第 10 組
  #   原句子：我們如何才能擁有住的地方 ⏎ 12.
  #   處理後：視為兩組，不依賴空行
  # 下面 When 用的是：太魯閣族/1_黃麗俐Miring_胡月英Tku_生活中的氣候啟示.txt 第 8、9 組
  # 第 8 組的翻譯行後面直接接第 9 組的編號，中間沒有空行。
  # 組界看編號行與時間碼行，不依賴組間的空行。
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
  Then 切出 2 組

Scenario: 認拉丁行只算小寫字母，大寫標記不算
  # 規格：判斷一行是拉丁行（原文、切分）還是漢字行（gloss、翻譯），
  # 比的是「小寫拉丁字母」與「漢字」的數量，大寫拉丁字母不算。
  # 理由：gloss 行的「不確定」標記（PI、KA、AN、SI'A……）照 ODS 1-2
  # 一律寫大寫。大寫如果算進拉丁，大寫標記多的 gloss 行就會被誤判成
  # 拉丁行，整組跟著接不回去。族語原文與切分行本來就以小寫為主，
  # 只算小寫照樣分得出來。
  # 全語料有 13 組是靠這條規格才接得回去，例如：
  #   排灣族/中排灣/2.廖桂香sakenge_廖進花-tinaqetaq 芋頭粉加花生粉蔬菜飯.txt 第 176 組
  #     gloss 行是 "PA-暫時"：大寫 2 個、漢字 2 個
  #   排灣族/中排灣/3.廖桂香Sakenge_Selep Ruviljivili_生活經歷.txt 第 203 組
  #     gloss 行是 "SI'A-NA-好        斜格        身體"：大寫 5 個、漢字 4 個
  # 出處：排灣族/東排灣/1_阮翠芳Gesi_高桂妹_80歲vuvu的傳說故事.txt 第 268 組
  #   gloss 行是 "探訪-AN"：小寫 0 個、大寫 2 個、漢字 2 個，算漢字行。
  When 讀入這幾行
    """
    268
    0:11:26.400,0:11:27.300
    paljiljian
    paljilji-an
    探訪-AN
    夫妻就去看
    """
  Then 切出 1 組
  And 第 1 組重組後的切分是 "paljilji-an"
  And 第 1 組重組後的 gloss 是 "探訪-AN"

@規格要討論
Scenario: 對話組——一組裡面兩位說話者各一套四行
  # 全語料共 38 筆，集中在阿美族三個檔案：
  #   19 筆 阿美族/南勢/陳美莉_Mariya Panay_ina.txt
  #   18 筆 阿美族/南勢/3.陳美莉_張輝國 Huyku_水璉部落年齡.txt
  #    1 筆 阿美族/海岸/1_阿索.該拿Aso.Kaynga_文健站長輩的故事_難忘的歌曲_歌曲故事.txt
  # 排法是 四行 + 四行，每一行前面都有說話者標記（S:／A:／Y:／H:）。
  # 這不是長句分段，是兩個人各講一句。
  # 程式現在把這種組判成「行黏在一起」，這 38 組都不會匯出。
  # 要討論的是：這種組要拆成兩組、還是保留成一組、還是請對方改成兩組。
  # 出處：阿美族/海岸/1_阿索.該拿Aso.Kaynga_文健站長輩的故事_難忘的歌曲_歌曲故事.txt 第 166 組
  When 讀入這幾行
    """
    166
    0:09:05.720,0:09:07.200
    S: Nga'ay ho nga'ay=ho
    S: Nga'ay=ho nga'ay=ho
    S: 好=還 好=還
    S: 您好! 您好!
    A: Nga'ay ho nga'ay=ho
    A: Nga'ay=ho nga'ay=ho
    A: 好=還 好=還
    A: 您好! 您好!
    """
  Then 切出 1 組
  And 第 1 組被判成「行黏在一起」

@規格要討論
Scenario: 其他還沒有規則的排法
  # 內文 5 行以上的組，照「族＝拉丁行、華＝漢字行」統計出來的排法。
  # 上面幾條已經有規則的：
  #   806 族族華族華華          長句分段，兩段
  #    57 族族華族華族華華      長句分段，三段
  #     3 族族華族華族華族華華  長句分段，四段
  #    35 族族華華族族華華      對話組
  #     3 族族華華族族華族      對話組（末行被判成拉丁）
  #    13 族族華族華族          長句分段，翻譯行含外來語被判成拉丁，不影響重組
  # 下面這些還沒有規則，程式一律判成「行黏在一起」或「缺 gloss 段」：
  #    48 族族華華華            切分行或 gloss 行被折行，兩邊對不起來
  #    11 族族族華華            gloss 行尾黏著下一段的切分
  #    11 族族華華華華          gloss 行折行，而且有重複
  #     7 族族華族族華          gloss 行含大寫標記，被判成拉丁行
  #     4 族族華族華            五行，缺一行
  #     4 族族華族族華華
  #     3 族族華族華華華
  #     2 族族華華族
  # 下面 When 用的是 48 筆那一種：
  # 排灣族/東排灣/1_阮翠芳Gesi_高桂妹_80歲vuvu的傳說故事.txt 第 4 組
  # 切分行是 "lu-kai-i=amen a"，被折成兩行；gloss 也被折成兩行，
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
  Then 切出 1 組
  And 第 1 組被判成「行黏在一起」
