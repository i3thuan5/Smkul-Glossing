Feature: 構詞的判定

  更新日期：2026.8.22

  每一個 Scenario 是一個判定情境。Scenario 後面附 3 組真語料的例子當做討論的依據，
  例子照語言優先序挑：例 1 阿美（秀姑巒→海岸→南勢）、例 2 太魯閣、
  例 3 魯凱；不夠的話才用排灣。三組例子盡量是三種不同語言。
  例子與清單裡的內容都照語料、ODS 原樣，半形全形都不改。

  規格依照《常用構詞標記清單》，只列出「拿掉就會改變判定結果」的那幾列。
  若規格沒有列出《常用構詞標記清單》，代表判定只看切分符號的結構。

  判斷方法，照這個流程：

  1. 先標註詞綴：
     a. <> 裡面的是中綴，標記為「中綴」。
     b. 全大寫的 gloss（PI、KA、'I）依《常用構詞標記清單》言談標記
        是「大寫」標記，標記為「未分類詞綴」。
     c. 《常用構詞標記清單》有登記的環綴（pi-...-i、ki-...-an 等），
        前後兩段各自判成「環綴」。
     d. 《常用構詞標記清單》有登記的焦點（主焦、受焦、處焦……等）的，標記為「未分類詞綴」；
        焦點後面還有其他內容的（例如「主焦.去」），那一段可能是詞根。
     e. gloss 寫「重疊」的，標記為「重疊」。
     f. 查《常用構詞標記清單》的時候，gloss 與形都要對得上才算詞綴。

  2. 如果剛好只有一段沒被標成詞綴，那一段就是詞根，其餘的「未分類詞綴」
     每一段看它與詞根之間跨過什麼符號：
     a. 跨過 = 的，標記為「依附詞」。
     b. 跨過 ~ 的，標記為「重疊」。
     c. 在詞根前，標記為「前綴」。
     d. 在詞根後，標記為「後綴」。

  3. 所以每個詞會有下列 3 種情形，詞根分不出來的，需一一討論：
     a. 如果剛好只有一段沒被標成詞綴，那一段就是詞根。
     b. 若不只一段沒被標成詞綴：詞根分不出來。
     c. 若每一段都被標成詞綴：詞根分不出來。

  詞根分不出來的時候（3b、3c），只有分不出來的那幾段記「無法判斷」：
  第 1 步就認出來的（中綴、環綴、重疊）照留，其餘的詞綴若不管詞根
  是哪一段都判成一樣，那一段照樣判得出來。「無法判斷」不算錯誤，
  也不擋匯出，照樣寫進 YAML 的「構詞」欄。

Scenario: 1a 中綴：<> 裡面的抽出來排在最前面
  # 例 1（下面用這一組判定）：阿美族/秀姑巒/陳美莉_阿星.阿曼_說族語在大漢部落的過.txt 第 96 組
  #   要判定的詞：s<om>owal
  #   族語原文：tangasa matini matoasay to mafokilay ho somowal tono Amilika
  #   切分：tangasa matini matoasay=to ma-fokil-ay=ho s<om>owal to no Amilika
  #   glossing：到達 現在 老人=完成貌 受焦-不懂-實現=還 <主焦>說 斜格 屬格 國名
  #   翻譯：一直到現在年紀大也不會講英文
  # 例 2：太魯閣族/1_黃麗俐Miring_胡月英Tku_生活中的氣候啟示.txt 第 54 組
  #   要判定的詞：r<m>ngaw
  #   族語原文：Manu rmngaw ka bubu mu da
  #   切分：manu r<m>ngaw ka bubu=mu da
  #   glossing：什麼 說<主焦> 主格 媽媽=我.屬格 助詞
  #   翻譯：母親說
  # 例 3：魯凱族/霧台/3.包鳯嬌_Uselrepe_月桃文化及製作上集.txt 第 32 組
  #   要判定的詞：p<a>iya
  #   族語原文：paiya madu kay si
  #   切分：p<a>iya madu kay si
  #   glossing：<限定>做 某人要 這 和
  #   翻譯：要這樣子
  When 切分是 "s<om>owal"，glossing 是 "<主焦>說"
  Then 判定結果是
    | 形    | 義   | 構詞 |
    | om    | 主焦 | 中綴 |
    | sowal | 說   | 詞根 |

Scenario: 1b 大寫：全大寫的 gloss 先標成未分類詞綴
  # 1f 的「形也要對得上」對這一條不適用：全大寫是「標注者不確定
  # 這個詞綴是什麼」的記號，清單 1-2 只寫得出 -AN、-? 這種樣式，
  # 登記不了實際的形，所以只看 gloss 就算詞綴。
  # 例 1（下面用這一組判定）：阿美族/秀姑巒/陳美莉_阿星.阿曼_說族語在大漢部落的過.txt 第 6 組
  #   要判定的詞：ka-hacowa
  #   族語原文：ca kahacowa ko tamdaw
  #   切分：ca ka-hacowa ko tamdaw
  #   glossing：不 KA-多少 主格 人
  #   翻譯：沒有多少人
  # 例 2：太魯閣族/1_黃麗俐Miring_胡月英Tku_生活中的氣候啟示.txt 第 33 組
  #   要判定的詞：t-gutu
  #   族語原文：Ringbu do qapal asi sqapal hmut tgutu hiya
  #   切分：ringbu do qapal asi s-qapal hmut t-gutu hiya
  #   glossing：蓮霧.日語 助詞 相連 立即 S-相連 任意 T-堆積 那裡
  #   翻譯：蓮霧的果實一串一串茂盛
  # 例 3：魯凱族/霧台/3.包鳯嬌_Uselrepe_月桃文化及製作上集.txt 第 88 組
  #   要判定的詞：t-ina
  #   族語原文：ku piyapiya ki tina madu waalra madu la ngialralraw madu
  #   切分：ku piya-piya ki t-ina madu wa-alra madu la ngialralraw madu
  #   glossing：斜格 重疊-做 屬格 T-媽媽 某人的 主動-拿 某人要 然後 模仿 某人要
  #   翻譯：媽媽所製作的都拿來然後學習
  Given 在阿美語常用構詞標記清單中
    | 編號 | 類別                     | 詞綴或詞 | 族語範例 | 詞素翻譯 | 備註 |
    | 1-2  | 不確定是什麼時 用大寫或? | -an      | -AN, -?  | -AN, -?  |      |
  When 切分是 "ka-hacowa"，glossing 是 "KA-多少"
  Then 判定結果是
    | 形     | 義   | 構詞 |
    | ka     | KA   | 前綴 |
    | hacowa | 多少 | 詞根 |

Scenario: 1c 環綴：清單有登記的，前後兩段各自標成環綴
  # 例 1（下面用這一組判定）：阿美族/南勢/4.陳美莉_張文良Puyar_新城鄉地名由來.txt 第 38 組
  #   要判定的詞：pi-surit-i
  #   族語原文：sisa marucekay tu kina suwal anu patelac sa kisu pisuriti may
  #   切分：sisa ma-rucek-ay=tu kina suwal anu patelac sa kisu pi-surit-i may
  #   glossing：所以 主焦-正確-實現=完成貌 主格.這 話 如果 錯誤 如此說 你.主格 PI-寫-祈使 助詞
  #   翻譯：所以 你講的沒有錯 你反對 你寫看看吧
  # 例 2：魯凱族/霧台/1.包鳯嬌_Ripunu_耆老的尊榮冠冕.txt 第 16 組
  #   要判定的詞：a-pasikay-ane
  #   族語原文：kay ki apasikayane ki cekele
  #   切分：kay ki a-pasikay-ane ki cekele
  #   glossing：這 斜格 未來-為-名物化 斜格 部落
  #   翻譯：為部落服務
  # 例 3：排灣族/中排灣/2.廖桂香sakenge_廖進花-tinaqetaq 芋頭粉加花生粉蔬菜飯.txt 第 125 組
  #   要判定的詞：si-'es-an
  #   族語原文：a si'esan ta tinaqetaq, ta vaqu,
  #   切分：a si-'es-an ta t<in>aqetaq ta vaqu
  #   glossing：連繫詞 參焦-烹煮-AN 斜格 <受焦.完成貌>芋頭粉花生粉蔬菜飯 斜格 小米
  #   翻譯：芋頭粉花生粉蔬菜飯、小米的煮法，
  Given 在阿美語常用構詞標記清單中
    | 編號 | 類別 | 詞綴或詞 | 族語範例    | 詞素翻譯   | 備註       |
    | 4-29 | 祈使 | pi-...-i | pi-tengil-i | PI-聽-祈使 | (南勢阿美) |
  When 切分是 "pi-surit-i"，glossing 是 "PI-寫-祈使"
  Then 判定結果是
    | 形    | 義   | 構詞 |
    | pi    | PI   | 環綴 |
    | surit | 寫   | 詞根 |
    | i     | 祈使 | 環綴 |

Scenario: 1d 只寫焦點：先標成未分類詞綴，之後再判斷詞綴類型——太魯閣語 uq-un
  # 出處：太魯閣族/1_黃麗俐Miring_胡月英Tku_生活中的氣候啟示.txt 第 304 組
  #   要判定的詞：uq-un
  #   族語原文：Ney kmalu uqun
  #   切分：Ney k-malu uq-un
  #   glossing：填補詞 祈使-好 吃-受焦
  #   翻譯：吃起來太美味了
  # 判斷方法：gloss 只寫焦點（主焦、受焦、處焦……）的就是詞綴；
  # 焦點後面還有其他內容的（例如「主焦.去」），那一段可能是詞根。
  # 程式現在沒有這條規則，是靠別的方式湊巧判對的，所以列出來討論。
  #   這一組：「受焦」只寫焦點，是詞綴；uq（吃）才是詞根。
  Given 在太魯閣語常用構詞標記清單中
    | 編號 | 類別 | 詞綴或詞 | 族語範例 | 詞素翻譯  | 備註  |
    | 4-4  | 受焦 | -un      | salu-un  | 製作-受焦 | sluun |
  When 切分是 "uq-un"，glossing 是 "吃-受焦"
  Then 判定結果是
    | 形 | 義   | 構詞 |
    | uq | 吃   | 詞根 |
    | un | 受焦 | 後綴 |

Scenario: 1d 只寫焦點：先標成未分類詞綴，之後再判斷詞綴類型——排灣語 ma-ka
  # 出處：排灣族/東排灣/1_阮翠芳Gesi_高桂妹_80歲vuvu的傳說故事.txt 第 233 組
  #   要判定的詞：ma-ka
  #   族語原文：pakamazau a maka ljavek
  #   切分：pa-ka-maza-u a ma-ka ljavek
  #   glossing：使役-經由-這裡-祈使 連繫詞 主焦-經由 海
  #   翻譯：你就靠海邊活動
  # 判斷方法：gloss 只寫焦點（主焦、受焦、處焦……）的就是詞綴；
  # 焦點後面還有其他內容的（例如「主焦.去」），那一段可能是詞根。
  # 程式現在沒有這條規則，是靠別的方式湊巧判對的，所以列出來討論。
  #   這一組：「主焦」只寫焦點，是詞綴；ka（經由）才是詞根。
  Given 在排灣語常用構詞標記清單中
    | 編號 | 類別 | 詞綴或詞 | 族語範例  | 詞素翻譯  | 備註             |
    | 4-5  | 主焦 | ma-      | ma-ljavar | 主焦-話語 | 整體意：「聊天」 |
  When 切分是 "ma-ka"，glossing 是 "主焦-經由"
  Then 判定結果是
    | 形 | 義   | 構詞 |
    | ma | 主焦 | 前綴 |
    | ka | 經由 | 詞根 |

Scenario: 1d 焦點加內容：那一段可能是詞根——布農語 ku-di
  # 出處：布農族/郡群/3.林美芳Abus_顏浩義_布農英雄Dahuali後裔對本家所遭遇之.txt 第 108 組
  #   要判定的詞：ku-di
  #   族語原文：maciskun kudi
  #   切分：ma-ciskun ku-di
  #   glossing：主焦-一起 主焦.去-DIP
  #   翻譯：一起去
  # 判斷方法：gloss 只寫焦點（主焦、受焦、處焦……）的就是詞綴；
  # 焦點後面還有其他內容的（例如「主焦.去」），那一段可能是詞根。
  # 程式現在沒有這條規則，是靠別的方式湊巧判對的，所以列出來討論。
  #   這一組：「主焦.去」是焦點加內容，可能是詞根；DIP 是全大寫的不確定標記。
  Given 在布農語常用構詞標記清單中
    | 編號 | 類別                     | 詞綴或詞 | 族語範例   | 詞素翻譯       | 備註 |
    | 3-2  | 主焦                     | m-       | m-un-'apav | 主焦-移動-出現 |      |
    | 1-2  | 不確定是什麼時 用大寫或? | ngu-     | NGU-, ?-   | NGU-, ?-       |      |
  When 切分是 "ku-di"，glossing 是 "主焦.去-DIP"
  Then 判定結果是
    | 形 | 義      | 構詞 |
    | ku | 主焦.去 | 詞根 |
    | di | DIP     | 後綴 |

Scenario: 2a 依附詞：跨過 = 的，= 在詞根前
  # 例 1（下面用這一組判定）：排灣族/中排灣/1.廖桂香sakenge_劉清勇、李春花、曾秀玉_小米梗的用途.txt 第 28 組
  #   要判定的詞：nia=si-tulu
  #   族語原文：sa avan cu a aicu a nia situlu
  #   切分：sa avan cu a aicu a nia=si-tulu
  #   glossing：然後 就 主格.這 連繫詞 主格.這 連繫詞 我們.屬格=參焦-教導
  #   翻譯：那我們要教導
  # 例 2：布農族/巒群/1_松念竹Akuan_全美玲_布農語近代影響及語言之重要和傳承.txt 第 57 組
  #   要判定的詞：na=ma-hau
  #   族語原文：na mahau a tina tu
  #   切分：na=ma-hau a tina tu
  #   glossing：非實現=主焦-罵 主格 母親 連繫詞
  #   翻譯：媽媽就會罵說
  Given 在排灣語常用構詞標記清單中
    | 編號 | 類別      | 詞綴或詞 | 族語範例                          | 詞素翻譯       | 備註 |
    | 5-15 | 我們.屬格 | nia=     | nia=kinacekeljan nia='inacekeljan | 我們.屬格=家庭 |      |
    | 4-15 | 參焦      | si-      | si-keljang                        | 參焦-知道      |      |
  When 切分是 "nia=si-tulu"，glossing 是 "我們.屬格=參焦-教導"
  Then 判定結果是
    | 形   | 義        | 構詞   |
    | nia  | 我們.屬格 | 依附詞 |
    | si   | 參焦      | 前綴   |
    | tulu | 教導      | 詞根   |

Scenario: 2a 依附詞：跨過 = 的，= 在詞根後
  # 例 1（下面用這一組判定）：阿美族/秀姑巒/陳美莉_阿星.阿曼_說族語在大漢部落的過.txt 第 26 組
  #   要判定的詞：awa=to
  #   族語原文：pisanoAmis a caciyaw awa to matini
  #   切分：pi-sano-Amis a caciyaw awa=to matini
  #   glossing：PI-像-族名 連繫詞 說話 沒有=完成貌 現在
  #   翻譯：使用族語的情況已經少見了
  # 例 2：太魯閣族/1_黃麗俐Miring_胡月英Tku_生活中的氣候啟示.txt 第 4 組
  #   要判定的詞：nkla=su
  #   族語原文：Saw qnita su nkla su karat quri saw karat ga
  #   切分：saw q<n>ita=su nkla=su karat quri saw karat ga
  #   glossing：像 看<完成貌>=你.屬格 知識=你.屬格 天氣 關於 像 天氣 那
  #   翻譯：您對氣候的認知
  # 例 3：魯凱族/霧台/1.包鳯嬌_Ripunu_耆老的尊榮冠冕.txt 第 28 組
  #   要判定的詞：kai=nay
  #   族語原文：kudra kainay mwagaku
  #   切分：kudra kai=nay mwa-gaku
  #   glossing：那.不可見 否定=我們.排除.屬格 去-學校
  #   翻譯：因為我們沒有讀書
  Given 在阿美語常用構詞標記清單中
    | 編號 | 類別   | 詞綴或詞 | 族語範例       | 詞素翻譯             | 備註 |
    | 4-20 | 完成貌 | =to      | k<om>aen-ay=to | <主焦>吃-實現=完成貌 |      |
  When 切分是 "awa=to"，glossing 是 "沒有=完成貌"
  Then 判定結果是
    | 形  | 義     | 構詞   |
    | awa | 沒有   | 詞根   |
    | to  | 完成貌 | 依附詞 |

Scenario: 2a 依附詞：= 在詞根前，詞根是華語借詞
  # 這一條與上面兩條 2a 是同一個規則，差別在詞根是華語借詞、直接
  # 寫漢字。全語料這種「前依附詞＋漢字詞根」共 413 個詞，集中在
  # 排灣語，所以三個例子都用排灣語（其他語言不夠）。
  # 例 1（下面用這一組判定）：排灣族/中排灣/1.廖桂香sakenge_劉清勇、李春花、曾秀玉_小米梗的用途.txt 第 5 組
  #   要判定的詞：tja=黑板
  #   族語原文：sa 'u sipuveci' a pizua ta tja 黑板 tisun anga temulu,
  #   切分：sa 'u=si-pu-veci' a pi-zua ta tja=黑板 tisun=anga t<em>ulu
  #   glossing：然後 我.屬格=參焦-使役-字 連繫詞 放-主格.那 斜格 我們.包含.屬格=黑板 你.主格=完成貌 <主焦>教導
  #   翻譯：然後我記錄在kukubang上，
  # 例 2：排灣族/中排灣/3.廖桂香Sakenge_Selep Ruviljivili_生活經歷.txt 第 165 組
  #   要判定的詞：tja=穴道
  #   族語原文：aicu a tja 'ula masan liav tua aicu a tja 穴道,
  #   切分：aicu a tja='ula ma-san liav tua aicu a tja=穴道
  #   glossing：主格.這 連繫詞 我們.包含.屬格=腳 主焦-製作 多 斜格 主格.這 連繫詞 我們.包含.屬格=穴道
  #   翻譯：我們腳中的穴道很多，
  # 例 3：排灣族/中排灣/1.廖桂香sakenge_劉清勇、李春花、曾秀玉_小米梗的用途.txt 第 62 組
  #   要判定的詞：tja=vuvu
  #   族語原文：pecevulj sicevulj ta e tja vuvu, maru pecevulj sa 'emeljang a tja vuvu
  #   切分：pe-cevulj si-cevulj ta e tja=vuvu maru pe-cevulj sa '<em>eljang a tja=vuvu
  #   glossing：流-煙 參焦-煙 斜格 填補詞 我們.包含.屬格=祖父母 像 有-煙 然後 <主焦>知道 連繫詞 我們.包含.屬格=祖父母
  #   翻譯：起狼煙於祖先，誠如起狼煙告知祖靈
  #   例 3 的詞根是族語不是借詞，結構一樣，列出來對照。
  #
  # 判定靠的是 gloss 查不查得到，不是看它在 = 的哪一邊：
  # 「我們.包含.屬格」在清單裡（5-19 tja=），所以 tja 是詞綴；
  # 「黑板」查不到，剩下它一段沒被標，它就是詞根。
  Given 在排灣語常用構詞標記清單中
    | 編號 | 類別           | 詞綴或詞 | 族語範例         | 詞素翻譯                        | 備註 |
    | 5-19 | 我們.包含.屬格 | tja=     | tja=pa-vay-in    | 我們.包含.屬格=使役-給-受焦     |      |
  When 切分是 "tja=黑板"，glossing 是 "我們.包含.屬格=黑板"
  Then 判定結果是
    | 形   | 義             | 構詞   |
    | tja  | 我們.包含.屬格 | 依附詞 |
    | 黑板 | 黑板           | 詞根   |

Scenario: 2c 前綴：在詞根前
  # 例 1（下面用這一組判定）：阿美族/秀姑巒/陳美莉_阿星.阿曼_說族語在大漢部落的過.txt 第 38 組
  #   要判定的詞：pa-caof
  #   族語原文：pacaof sa ko matoasay sano Holam a pacaf to no pilicay no wawa
  #   切分：pa-caof sa ko matoasay sano-Holam a pacaf to no pi-licay no wawa
  #   glossing：使動-回覆 如此說 主格 老人 像-族名 連繫詞 回覆 斜格 屬格 PI-問 屬格 孩子
  #   翻譯：長輩回應給晚輩也是華語的話
  # 例 2：太魯閣族/1_黃麗俐Miring_胡月英Tku_生活中的氣候啟示.txt 第 25 組
  #   要判定的詞：m-tmay
  #   族語原文：Mha mtmay alang dga mtmay alang da.
  #   切分：mha m-tmay alang dga m-tmay alang da
  #   glossing：將要 主焦-進入 部落 助詞 主焦-進入 部落 助詞
  #   翻譯：侵襲部落
  # 例 3：魯凱族/霧台/3.包鳯嬌_Uselrepe_月桃文化及製作上集.txt 第 75 組
  #   要判定的詞：am-iya
  #   族語原文：malreme amiya madu lu kamamelre
  #   切分：ma-lreme am-iya madu lu ka-mamelre
  #   glossing：靜態.限定-成熟 限定-說 某人要 如果 靜態.非限定-軟
  #   翻譯：軟了就說成熟了
  Given 在阿美語常用構詞標記清單中
    | 編號 | 類別 | 詞綴或詞 | 族語範例 | 詞素翻譯 | 備註 |
    | 4-31 | 使動 | pa-      | pa-kaen  | 使動-吃  |      |
  When 切分是 "pa-caof"，glossing 是 "使動-回覆"
  Then 判定結果是
    | 形   | 義   | 構詞 |
    | pa   | 使動 | 前綴 |
    | caof | 回覆 | 詞根 |

Scenario: 2d 後綴：在詞根後
  # 例 1（下面用這一組判定）：阿美族/秀姑巒/陳美莉_阿星.阿曼_說族語在大漢部落的過.txt 第 46 組
  #   要判定的詞：awa-ay
  #   族語原文：awaay ko no Holam a caciyaw itini i loma' awaay
  #   切分：awa-ay ko no Holam a caciyaw itini i loma' awa-ay
  #   glossing：沒有-實現 主格 屬格 族名 連繫詞 說話 在這裡 介系詞 家 沒有-實現
  #   翻譯：在家裡從不說華語
  # 例 2：太魯閣族/1_黃麗俐Miring_胡月英Tku_生活中的氣候啟示.txt 第 384 組
  #   要判定的詞：qlal-i
  #   族語原文：Ini su na bi qlali.
  #   切分：ini=su=na bi qlal-i
  #   glossing：否定=你.主格=他.屬格 很 給-祈使
  #   翻譯：不會分享給你的.
  # 例 3：魯凱族/霧台/1.包鳯嬌_Ripunu_耆老的尊榮冠冕.txt 第 113 組
  #   要判定的詞：dangetay-ane
  #   族語原文：kathane ku dangetayane ku kipaelreli si 第一名nay
  #   切分：kathane ku dangetay-ane ku kipaelre=li si 第一名=nay
  #   glossing：只有 斜格 團體-名物化 屬格 參加=我.屬格 和 第一名=我們.排除.屬格
  #   翻譯：我只有參加團體的，我們icibange
  Given 在阿美語常用構詞標記清單中
    | 編號 | 類別 | 詞綴或詞 | 族語範例     | 詞素翻譯         | 備註                   |
    | 9-18 | 實現 | -ay      | matuas=tu-ay | 長大=完成貌-實現 | (南勢阿美)長大這件事情 |
  When 切分是 "awa-ay"，glossing 是 "沒有-實現"
  Then 判定結果是
    | 形  | 義   | 構詞 |
    | awa | 沒有 | 詞根 |
    | ay  | 實現 | 後綴 |

Scenario: 3a 剛好一段沒被標成詞綴：好幾個前綴串接
  # 例 1（下面用這一組判定）：阿美族/秀姑巒/陳美莉_阿星.阿曼_說族語在大漢部落的過.txt 第 7 組
  #   要判定的詞：mi-sa-rocod-ay
  #   族語原文：nika o rira o misarocoday ko tayal no mako itini
  #   切分：nika o rira o mi-sa-rocod-ay ko tayal no mako itini
  #   glossing：但是 名詞標記 那.屬格 名詞標記 主焦-工具焦-專注-名物化 主格 工作 屬格 我.所有格 在這裡
  #   翻譯：但是 我的工作就是在推廣
  # 例 2：太魯閣族/1_黃麗俐Miring_胡月英Tku_生活中的氣候啟示.txt 第 210 組
  #   要判定的詞：m-s-haya
  #   族語原文："Ey iya iya ma su mshaya bi, laqi manu saw nini"
  #   切分：ey iya iya ma=su m-s-haya bi laqi manu saw nini
  #   glossing：填補詞 否定 否定 為何=你.主格 主焦-S-那樣 很 孩子 什麼 像 這些
  #   翻譯："不用了，不用了，——這孩子真是的" 母親說
  # 例 3：魯凱族/霧台/1.包鳯嬌_Ripunu_耆老的尊榮冠冕.txt 第 32 組
  #   要判定的詞：ki-a-bulru
  #   族語原文：kainay kiabulru sakabanudunay la kainaku wathingale kay ciwkukukukane
  #   切分：kai=nay ki-a-bulru sa ka banudu=nay la kai-n-aku wa-thingale kay ciw<ku>kukukane
  #   glossing：否定=我們.排除.主格 被動-限定-學習 當 KA 學生=我們.排除.屬格 然後 否定-N-我.主格 主動-知道 這 <重疊>國語
  #   翻譯：學生時期我們沒學到所以我不會國字
  Given 在阿美語常用構詞標記清單中
    | 編號 | 類別   | 詞綴或詞 | 族語範例    | 詞素翻譯       | 備註 |
    | 4-1  | 主焦   | mi-      | mi-nanam    | 主焦-學習      |      |
    | 4-15 | 工具焦 | sa-      | sa-kadat    | 工具焦-梳      |      |
    | 9-16 | 名物化 | -ay      | mi-tilid-ay | 主焦-讀-名物化 |      |
  When 切分是 "mi-sa-rocod-ay"，glossing 是 "主焦-工具焦-專注-名物化"
  Then 判定結果是
    | 形    | 義     | 構詞 |
    | mi    | 主焦   | 前綴 |
    | sa    | 工具焦 | 前綴 |
    | rocod | 專注   | 詞根 |
    | ay    | 名物化 | 後綴 |

Scenario: 3a 剛好一段沒被標成詞綴：沒有切分符號的詞，整個就是詞根
  # 例 1（下面用這一組判定）：阿美族/秀姑巒/陳美莉_阿星.阿曼_說族語在大漢部落的過.txt 第 2 組
  #   要判定的詞：i
  #   族語原文：O na itiraay i Tokar i Poseko ko niyaro' no mako
  #   切分：Ona itira-ay i Tokar i Poseko ko niyaro' no mako
  #   glossing：屬格.這個 在那裡-實現 介系詞 地名 介系詞 地名 主格 部落 屬格 我.所有格
  #   翻譯：我的部落在Poseko(玉里)的Tokar(觀音里)
  # 例 2：太魯閣族/1_黃麗俐Miring_胡月英Tku_生活中的氣候啟示.txt 第 1 組
  #   要判定的詞：ha
  #   族語原文：Kiya ha, Tku ita mnswayi
  #   切分：Kiya ha Tku ita mnswayi
  #   glossing：好的 填補詞 人名 主格.咱們 兄弟姊妹
  #   翻譯：好的, Tku 姊妹
  # 例 3：魯凱族/霧台/1.包鳯嬌_Ripunu_耆老的尊榮冠冕.txt 第 1 組
  #   要判定的詞：ka
  #   族語原文：kunaku swa Adiriaku ka tai Abalrini
  #   切分：kunaku swa Adiri=aku ka tai Abalrini
  #   glossing：我.自由.主題格 來自 地名=我.主格 關係詞 屬於 家名
  #   翻譯：我是Abalrini 家的阿禮部落
  When 切分是 "i"，glossing 是 "介系詞"
  Then 判定結果是
    | 形 | 義     | 構詞 |
    | i  | 介系詞 | 詞根 |

Scenario: gloss 用 . 串幾個屬性，查表時看第一段
  # 這一組的 ni 是「重疊.主格」，第一段是「重疊」，照 1e 那條
  # 免比形，所以查得到清單就算詞綴；koni（這個）查不到，
  # 剛好一段沒被標成詞綴，它就是詞根。
  # 例 1（下面用這一組判定）：阿美族/秀姑巒/陳美莉_阿星.阿曼_說族語在大漢部落的過.txt 第 31 組
  #   要判定的詞：koni-ni-an
  #   族語原文：o kakalimelaan no mako i matini koninian
  #   切分：o ka-ka-limela-an no mako i matini koni-ni-an
  #   glossing：名詞標記 重疊-KA-可惜-AN 屬格 我.所有格 介系詞 現在 這個-重疊.主格-處焦
  #   翻譯：我覺得這是很遺憾的事
  # 例 2：太魯閣族/1_黃麗俐Miring_胡月英Tku_生活中的氣候啟示.txt 第 4 組
  #   要判定的詞：nkla=su
  #   族語原文：Saw qnita su nkla su karat quri saw karat ga
  #   切分：saw q<n>ita=su nkla=su karat quri saw karat ga
  #   glossing：像 看<完成貌>=你.屬格 知識=你.屬格 天氣 關於 像 天氣 那
  #   翻譯：您對氣候的認知
  # 例 3：魯凱族/霧台/1.包鳯嬌_Ripunu_耆老的尊榮冠冕.txt 第 28 組
  #   要判定的詞：kai=nay
  #   族語原文：kudra kainay mwagaku
  #   切分：kudra kai=nay mwa-gaku
  #   glossing：那.不可見 否定=我們.排除.屬格 去-學校
  #   翻譯：因為我們沒有讀書
  Given 在阿美語常用構詞標記清單中
    | 編號 | 類別 | 詞綴或詞 | 族語範例    | 詞素翻譯   | 備註                                                    |
    | 4-19 | 處焦 | -an      | pi-tilid-an | PI-書-處焦 | tilid多重詞意(書、文字、唸、紋樣、顏色), 依照當時的語境 |
    | 4-23 | 重疊 | 重疊-    | wawa-wawa   | 重疊-孩子  |                                                         |
  When 切分是 "koni-ni-an"，glossing 是 "這個-重疊.主格-處焦"
  Then 判定結果是
    | 形   | 義        | 構詞 |
    | koni | 這個      | 詞根 |
    | ni   | 重疊.主格 | 後綴 |
    | an   | 處焦      | 後綴 |

@規格要討論
Scenario: 1e 重疊：gloss 寫「重疊」的，標記為重疊——阿美語 cowa-cowa
  # 1f 的「形也要對得上」對重疊不適用：重疊的形是詞根自己的翻頭
  # （cowa-cowa 的 cowa、Vedai-Vedai 的 Vedai），每個詞都不一樣，
  # 清單登記不了固定的形（4-23 只寫得出「重疊-」這種位置說法），
  # 所以只看 gloss 就算重疊。
  # 例 1（下面用這一組判定）：阿美族/秀姑巒/陳美莉_阿星.阿曼_說族語在大漢部落的過.txt 第 10 組
  #   要判定的詞：cowa-cowa
  #   族語原文：hato o nani itiraay i cowacowa no niyaro'
  #   切分：hato o na-ni itira-ay i cowa-cowa no niyaro'
  #   glossing：好像 名詞標記 過去-NI 在那裡-實現 介系詞 重疊-四處 屬格 部落
  #   翻譯：都是還自各部落移居到這裡的
  # 例 2：魯凱族/霧台/1.包鳯嬌_Ripunu_耆老的尊榮冠冕.txt 第 5 組
  #   要判定的詞：Vedai-Vedai
  #   族語原文：amani ku kiathingathingale ki swa VedaiVedai
  #   切分：amani ku ki-a-thinga-thingale ki swa Vedai-Vedai
  #   glossing：是 斜格 被動-限定-重疊-知道 斜格 來自 重疊-霧台
  #   翻譯：是被全鄉所知道的
  # 例 3：排灣族/中排灣/1.廖桂香sakenge_劉清勇、李春花、曾秀玉_小米梗的用途.txt 第 3 組
  #   要判定的詞：ne<manga>manga
  #   族語原文：nusauni aicu a i cekuy a mare'a nemangamanga ui,
  #   切分：nusauni aicu a i cekuy a mare'a ne<manga>manga ui
  #   glossing：待會兒 主格.這 連繫詞 處所 桌子 連繫詞 所有 <重疊>物品 言談標記
  #   翻譯：等等呢桌上的這些物品，
  # 例 3 的重疊是用 <> 標的，1a 會先把它判成中綴，
  # 跟例 1、例 2 用 - 標的不一樣，一併列出來對照。
  Given 在阿美語常用構詞標記清單中
    | 編號 | 類別 | 詞綴或詞 | 族語範例  | 詞素翻譯  | 備註 |
    | 4-23 | 重疊 | 重疊-    | wawa-wawa | 重疊-孩子 |      |
  When 切分是 "cowa-cowa"，glossing 是 "重疊-四處"
  Then 判定結果是
    | 形   | 義   | 構詞 |
    | cowa | 重疊 | 重疊 |
    | cowa | 四處 | 詞根 |

@規格要討論
Scenario: 1e 重疊：gloss 寫「重疊」的，標記為重疊——阿美語 awa-ay-ay=ho
  # 例 1（下面用這一組判定）：阿美族/秀姑巒/陳美莉_阿星.阿曼_說族語在大漢部落的過.txt 第 166 組
  #   要判定的詞：awa-ay-ay=ho
  #   族語原文：nikaorira awaayay ho ko mokesi i matini
  #   切分：nika orira awa-ay-ay=ho ko mokesi i matini
  #   glossing：但是 那 沒有-重疊-實現=還 主格 牧師.日語 介係詞 現在
  #   翻譯：因為 現在沒有牧師
  # 例 2：魯凱族/霧台/1.包鳯嬌_Ripunu_耆老的尊榮冠冕.txt 第 11 組
  #   要判定的詞：ami-amia
  #   族語原文：kai kialrimu lridrusata kay amiamia
  #   切分：kai kialrimu lri-drusa=ta kay ami-amia
  #   glossing：否定 ? 未來-二=我們.包含.屬格 這 重疊-說
  #   翻譯：他不會說我們是兩個人獵的
  # 例 3：排灣族/東排灣/2_阮翠芳Gesi_阮秀美_土坂派出所拘留所的故事.txt 第 19 組
  #   要判定的詞：uma-umaq
  #   族語原文：mavan sinanguaq aicu a umaumaq
  #   切分：mavan si-na-nguaq aicu a uma-umaq
  #   glossing：就是 參焦-NA-好 這個 連繫詞 重疊-家
  #   翻譯：仍然把它保留的很完整
  Given 在阿美語常用構詞標記清單中
    | 編號 | 類別 | 詞綴或詞 | 族語範例       | 詞素翻譯         | 備註                   |
    | 9-18 | 實現 | -ay      | matuas=tu-ay   | 長大=完成貌-實現 | (南勢阿美)長大這件事情 |
    | 9-28 | 還   | ho       | k<om>aen-ay=ho | <主焦>吃=還      | 已實現                 |
  When 切分是 "awa-ay-ay=ho"，glossing 是 "沒有-重疊-實現=還"
  Then 判定結果是
    | 形  | 義   | 構詞   |
    | awa | 沒有 | 詞根   |
    | ay  | 重疊 | 重疊   |
    | ay  | 實現 | 後綴   |
    | ho  | 還   | 依附詞 |

Scenario: 2b 重疊：跨過 ~ 的——太魯閣語 q~qlahang
  # 語料裡用 ~ 標重疊的只有太魯閣語這 5 個詞，都出自同一個檔案，
  # 而且每一組都有別的驗證錯誤（見下面每一組的說明），所以沒有
  # 完全乾淨的例子可以用。
  #
  # 規格：重疊的位置要看 gloss 寫什麼（1e），不能看它在 ~ 的哪一邊。
  # 太魯閣語的重疊是加在前面的（q~、b~），所以看 ~ 的哪一邊會判反。
  #
  # 詞根一旦判到錯的那一段，真正的詞根（小心、風）就會被當成
  # 詞綴拿去查清單，當然查不到——這是連鎖反應，不是清單缺漏。
  # 例 1（下面用這一組判定）：太魯閣族/1_黃麗俐Miring_胡月英Tku_生活中的氣候啟示.txt 第 146 組
  #   要判定的詞：q~qlahang
  #   族語原文：Iyux qqlahang ga
  #   切分：iyux q~qlahang ga
  #   glossing：勉強 重疊~小心 那
  #   翻譯：提示我們要多小心 留意
  #   這一組：q~ 是重疊，qlahang（小心）是詞根。
  #   這一組的驗證錯誤：標記不在清單「小心」——因為詞根判到 q，
  #   真正的詞根「小心」被當成詞綴去查清單，查無（連鎖反應）。
  # 例 2：太魯閣族/1_黃麗俐Miring_胡月英Tku_生活中的氣候啟示.txt 第 109 組
  #   要判定的詞：b~bgihur
  #   族語原文：Bbgihur hug aji uri o saw ini pndka karat?
  #   切分：b~bgihur hug aj.uri.o saw ini p<n>dka karat
  #   glossing：複數~風 助詞 或者 像 否定 <完成>一樣 天氣
  #   翻譯：象徵不同的氣象啟示呢?
  #   這一組：b~ 是重疊，bgihur（風）是詞根。
  #   這一組的驗證錯誤有兩個：
  #   一、標記不在清單「風」（同上，連鎖反應）。
  #   二、標記不在清單「完成」——p<n>dka 的 <完成> 是中綴，程式也
  #   判成中綴了，判定沒問題；問題出在查表：太魯閣語清單 4-8 寫的是
  #   「完成貌」（<n>，例 q<n>ita → <完成貌>看），語料寫「完成」，
  #   少一個「貌」字。這是語料與清單的寫法不一致，要請對方統一。
  # 例 3：太魯閣族/1_黃麗俐Miring_胡月英Tku_生活中的氣候啟示.txt 第 11 組
  #   要判定的詞：m~m-iyah
  #   族語原文：Tai saw mmiyah ka bgihur dga
  #   切分：qita-i saw m~m-iyah ka bgihur dga
  #   glossing：看-受處焦.祈使 像 即將~主焦-來 主格 風 助詞
  #   翻譯：颱風來襲前
  #   這一組判對了：m~ 是重疊，iyah（來）是詞根。之所以會對，是因為
  #   這個詞有三段，被 ~ 剔掉一段以後還剩兩段，程式再從剩下的兩段
  #   取形較長的 iyah——是碰巧對的，不是規則對。
  #   這一組的驗證錯誤：標記不在清單「即將」。這個「即將」不是語料
  #   亂寫：太魯閣語清單 4-16 的類別就是「重疊」，範例 b~biqun 的
  #   詞素翻譯正是「即將-給-受焦」，重疊那一段就 gloss 成「即將」。
  #   查不到是因為程式只收「類別」欄，「即將」只出現在「詞素翻譯」欄。
  #   另外，清單 4-16 的詞素翻譯用的是 -（即將-給-受焦），語料用的是
  #   ~（即將~主焦-來），同一件事兩種寫法，也要請對方確認。
  When 切分是 "q~qlahang"，glossing 是 "重疊~小心"
  Then 判定結果是
    | 形      | 義   | 構詞 |
    | q       | 重疊 | 重疊 |
    | qlahang | 小心 | 詞根 |

  # 下面三條和上面的 2b 合起來，就是 ~ 在語料裡的四種用法：
  # 重疊（2b，太魯閣語 5 個詞）、拉長音、歌謠、擬聲詞。
  # 只有重疊與拉長音會讓 ~ 進到切分行；歌謠與擬聲詞的 ~ 只出現在
  # 第一行與第四行，切分行已經換成別的寫法了。
  #
  # 另外，《常用構詞標記清單》每一個語言的分頁都各自有一條拉長音的
  # 規定，寫法是 ==（阿美語另外還有一條 : ）。沒有一個語言的分頁
  # 說拉長音可以用 ~。

@規格要討論
Scenario: ~ 當拉長音：布農語 ung~
  # 例 1（下面用這一組判定）：布農族/郡群/1.林美芳Abus_林國仁_ 那瑪夏歷史演變.txt 第 389 組
  #   要判定的詞：ung~
  #   族語原文：ung~
  #   切分：ung~
  #   glossing：是
  #   翻譯：是
  # 例 2：泰雅族/賽考利克/1_楊淑貞Rimuy_姜玉粉Upah_生命故事.txt 第 181 組
  #   要判定的詞：o~~~laqi
  #   族語原文：o~~~laqi na Kbuta pqasun balay son mha ryax soni
  #   切分：o~~~laqi na Kbuta pqas-un balay son mha ryax soni
  #   glossing：孩子 屬格人名 高興-受焦 真的 稱作.受焦 補語連詞 日子 今天
  #   翻譯：o~~泰雅的子孫很感謝你們今天的到來
  #   這一組的 o~~~ 是拉長的語氣詞，黏在 laqi（孩子）前面，
  #   gloss 那一行沒有對應的段，所以整句的 token 數也對不齊。
  #
  # 這兩組的 ~ 都是拉長音，不是重疊。切分行有 ~ 但 gloss 行沒有，
  # 符號對不起來，判不出哪一段是詞根。
  When 切分是 "ung~"，glossing 是 "是"
  Then 判定結果是
    | 形   | 義 | 構詞         |
    | ung~ | 是 | （無法判斷） |

@規格要討論
Scenario: ~ 當歌謠的音節分隔：霧台魯凱語 ai~au~i
  # 例 1（下面用這一組判定）：魯凱族/霧台/2.包鳯嬌_Tuku_建築石板屋與傳說故事.txt 第 105 組
  #   要判定的詞：ai==au==i
  #   族語原文：ai~au~i
  #   切分：ai==au==i
  #   glossing：啊伊==啊烏==伊
  #   翻譯：阿伊~阿烏~伊
  # 例 2：魯凱族/霧台/2.包鳯嬌_Tuku_建築石板屋與傳說故事.txt 第 108 組
  #   要判定的詞：ai au i
  #   族語原文：ai~au~i
  #   切分：ai au i
  #   glossing：ai au i
  #   翻譯：阿伊~阿烏~伊
  #
  # 同一首歌在同一個檔案裡有三種寫法：第一行用 ~、第 105 組的切分行
  # 換成 ==、第 108 組的切分行又改成用空白分開。
  #
  # 霧台魯凱語清單 1-4 說拉長音用 ==，而且「不用標」——意思是只寫在
  # 第一行，第二行與第三行不標。這裡標到第二、三行去了，要請對方確認。
  #
  # == 是拉長音，不是切分符號，所以整串算一段（== 會撞到依附詞的 =，
  # 見下面那一條）。
  Given 在霧台魯凱語常用構詞標記清單中
    | 編號 | 類別   | 詞綴或詞 | 族語範例 | 詞素翻譯 |
    | 1-4  | 拉長音 | ==       | 不用標   | 不用標   |
  When 切分是 "ai==au==i"，glossing 是 "啊伊==啊烏==伊"
  Then 判定結果是
    | 形        | 義             | 構詞 |
    | ai==au==i | 啊伊==啊烏==伊 | 詞根 |

@規格要討論
Scenario: ~ 當擬聲詞的連接：太魯閣語 Sup~sup~
  # 例 1（下面用這一組判定）：太魯閣族/1_黃麗俐Miring_胡月英Tku_生活中的氣候啟示.txt 第 338 組
  #   要判定的詞：sup
  #   族語原文：Mey smngusul ni Sup~sup~ pwaela ka hnu uri o qnqan ta ga
  #   切分：mey s-m-ngusul ni sup sup p-waela ka hnu uri o ekan<n>-an =ta ga
  #   glossing：填補詞 S-主焦- 流鼻涕 和 擬聲 擬聲 使-帶領 主格 那樣 也 主題 吃<完成>-處焦 我們.包含.主格 那
  #   翻譯：滑溜溜的一口接一口
  # 例 2：太魯閣族/1_黃麗俐Miring_胡月英Tku_生活中的氣候啟示.txt 第 344 組
  #   要判定的詞：suq
  #   族語原文："Suq~suq " msa o  ha ha ha
  #   切分：suq suq msa o ha ha ha
  #   glossing：擬聲 擬聲 主焦.說 主題 擬聲 擬聲 擬聲
  #   翻譯：吞嚥聲~形容詞 哈 哈 哈
  #
  # 第一行用 ~ 把重複的擬聲詞連起來，切分行改成用空白拆成兩個 token。
  # ~ 沒有進到切分行，所以不影響構詞判定。
  # 不過第 344 組的翻譯行「吞嚥聲~形容詞」，那個 ~ 又是第四種意思
  # （連接說明），跟前面三種都不一樣。
  When 切分是 "sup"，glossing 是 "擬聲"
  Then 判定結果是
    | 形  | 義   | 構詞 |
    | sup | 擬聲 | 詞根 |

@規格要討論
Scenario: 3b 不只一段沒被標成詞綴：排灣語 z<em>e-liu-liulj=amen
  # 出處：排灣族/東排灣/3_阮翠芳Gesi_鄭玉英_生命故事.txt 第 47 組
  #   要判定的詞：z<em>e-liu-liulj=amen
  #   族語原文：zemeliuliulj amen ta dridri
  #   切分：z<em>e-liu-liulj=amen ta dridri
  #   glossing：<主焦>-重疊-工錢=我們.主格 斜格 豬
  #   翻譯：豬肉是我們的工錢
  #   為什麼分不出來：ze 的 gloss 是空的（glossing 的 <主焦> 後面直接
  #   接 -，沒有寫東西），liulj 的 gloss「工錢」也不在清單裡。兩段都
  #   不算詞綴，照判斷方法 3b，這兩段記（無法判斷）。
  #   其餘三段還是判得出來：em 是 1a 的中綴、liu 的 gloss 寫「重疊」
  #   是 1e 的重疊，兩條都不看詞根在哪；=amen 不管詞根是 ze 還是
  #   liulj 都跨過 =，所以是依附詞。
  #   全語料只有這一個詞是這種情形。
  Given 在排灣語常用構詞標記清單中
    | 編號 | 類別      | 詞綴或詞 | 族語範例       | 詞素翻譯       | 備註 |
    | 5-14 | 我們.主格 | =amen    | kakedrian=amen | 小孩=我們.主格 |      |
  When 切分是 "z<em>e-liu-liulj=amen"，glossing 是 "<主焦>-重疊-工錢=我們.主格"
  Then 判定結果是
    | 形    | 義        | 構詞         |
    | em    | 主焦      | 中綴         |
    | ze    |           | （無法判斷） |
    | liu   | 重疊      | 重疊         |
    | liulj | 工錢      | （無法判斷） |
    | amen  | 我們.主格 | 依附詞       |

Scenario: 1f 形也要對得上：太魯閣語 s-rngaw
  # 出處：太魯閣族/1_黃麗俐Miring_胡月英Tku_生活中的氣候啟示.txt 第 123 組
  #   要判定的詞：s-rngaw
  #   族語原文：Kiya kingal srngaw bubu mu ga
  #   切分：kiya kingal s-rngaw bubu=mu ga
  #   glossing：所以 一 周邊焦-說 媽媽=我.屬格 那
  #   翻譯：這是母親說的其中之一啟示
  #   「周邊焦」與「說」兩段的 gloss 都查得到清單，光看 gloss 判不出詞根。
  #   照判斷方法 1f 再比形就分得出來：清單 4-6 登記的前綴形是 s-，
  #   s 對得上所以是前綴；「說」是登記成詞（6-3 ksun），沒有詞綴的形，
  #   rngaw 對不上任何詞綴，所以 rngaw 是詞根。
  Given 在太魯閣語常用構詞標記清單中
    | 編號 | 類別   | 詞綴或詞 | 族語範例 | 詞素翻譯 | 備註 |
    | 4-6  | 周邊焦 | s-       |          |          |      |
    | 6-3  | 說     | ksun     | ksun     | 說       |      |
  When 切分是 "s-rngaw"，glossing 是 "周邊焦-說"
  Then 判定結果是
    | 形    | 義     | 構詞         |
    | s     | 周邊焦 | 前綴 |
    | rngaw | 說     | 詞根 |

Scenario: 1f 形也要對得上：阿美語 tayni-ay
  # 出處：阿美族/秀姑巒/陳美莉_阿星.阿曼_說族語在大漢部落的過.txt 第 122 組
  #   要判定的詞：tayni-ay
  #   族語原文：nga'ay tayniay kako
  #   切分：nga'ay tayni-ay kako
  #   glossing：讓 來-實現 我.主格
  #   翻譯：我來這裡覺得很好
  #   「來」與「實現」兩段的 gloss 都查得到清單，光看 gloss 判不出詞根。
  #   照判斷方法 1f 再比形就分得出來：清單 9-18 登記的後綴形是 -ay，
  #   ay 對得上所以是後綴；「來」那一列登記的形是 Ø-，tayni 對不上，
  #   所以 tayni 是詞根。
  Given 在阿美語常用構詞標記清單中
    | 編號 | 類別 | 詞綴或詞 | 族語範例     | 詞素翻譯         | 備註                   |
    | 4-5  |      | Ø-       | tayni        | 來               |                        |
    | 9-18 | 實現 | -ay      | matuas=tu-ay | 長大=完成貌-實現 | (南勢阿美)長大這件事情 |
  When 切分是 "tayni-ay"，glossing 是 "來-實現"
  Then 判定結果是
    | 形    | 義   | 構詞         |
    | tayni | 來   | 詞根 |
    | ay    | 實現 | 後綴 |

Scenario: 1f 形也要對得上：實詞的意思撞到清單裡的詞綴 gloss
  # 共同情形：實詞的意思有時候剛好就是某個詞綴的 gloss。光看 gloss
  # 會變成每一段都算詞綴，判不出詞根；照判斷方法 1f 再比形就分得
  # 出來——清單登記的是詞綴的形與意思，「去」在清單裡只代表前綴
  # ma- 的意思是「去」，不代表 vaik 這一段是詞綴。
  # 例 1（下面用這一組判定）：排灣族/東排灣/1_阮翠芳Gesi_高桂妹_80歲vuvu的傳說故事.txt 第 48 組
  #   要判定的詞：vaik-i
  #   族語原文：vaiki a sema qumaqan
  #   切分：vaik-i a s<em>a qumaqan
  #   glossing：去-主焦.祈使 連繫詞 <主焦>去 屋內
  #   翻譯：我們趕快躲進屋裡
  #   清單登記：排灣語 4-32「去 | ma- | 去-平地」把「去」登記成前綴 gloss；
  #             4-25「主焦.祈使 | -u;-i」把「主焦.祈使」登記成後綴 gloss。
  #   判定：清單登記「去」的前綴形是 ma-，vaik 對不上；「主焦.祈使」
  #   登記的後綴形是 -u;-i，i 對得上。所以 vaik 是詞根、-i 是祈使後綴。
  # 例 2：魯凱族/霧台/1.包鳯嬌_Ripunu_耆老的尊榮冠冕.txt 第 50 組
  #   要判定的詞：a-mwa
  #   族語原文：ku saka sabingkiwanenay ku nadrwadruma yai amwa madu ki mingcupusipang
  #   切分：ku saka sa-bingkiw-ane=nay ku na<drwa>druma yai a-mwa madu ki mingcupusipang
  #   glossing：x xx 當-讀書-名物化=我們.排除.屬格 斜格 <重疊>早期 主題標記 限定-去 某人要 斜格 民主補習班.華語
  #   翻譯：我們讀書時 早期要去民主補習班
  #   清單登記：霧台魯凱語 3-18「去 | mu- | 去-上面」把「去」登記成前綴 gloss；「限定」也在清單裡。
  #   判定：清單登記「去」的前綴形是 mu-，mwa 對不上，所以 mwa 是詞根、a- 是前綴。
  # 例 3：布農族/郡群/1.林美芳Abus_林國仁_ 那瑪夏歷史演變.txt 第 164 組
  #   要判定的詞：m-u-sasu
  #   族語原文：at musasu tu
  #   切分：at m-u-sasu tu
  #   glossing：然後 主焦-移至-SASU 連繫詞
  #   翻譯：再說
  #   清單登記：布農語 3-2「主焦 | m- | 主焦-移動-出現」；「移至」也在清單裡；SASU 是全大寫的不確定標記。
  #   判定：m- 與 u- 的形都登記在清單裡，sasu 對不上任何詞綴，所以 sasu 是詞根、m-u- 是前綴串。
  Given 在排灣語常用構詞標記清單中
    | 編號 | 類別      | 詞綴或詞 | 族語範例                 | 詞素翻譯       | 備註 |
    | 4-32 | 去        | ma-      | ma-pairang               | 去-平地        |      |
    | 4-25 | 主焦.祈使 | -u;-i    | tjaucikel-u, tjauci'el-u | 述說-主焦.祈使 |      |
  When 切分是 "vaik-i"，glossing 是 "去-主焦.祈使"
  Then 判定結果是
    | 形   | 義        | 構詞 |
    | vaik | 去        | 詞根 |
    | i    | 主焦.祈使 | 後綴 |

@規格要討論
Scenario: 難判斷：阿美語 na-ni 的 過去 在清單裡、NI 是全大寫
  # 出處：阿美族/秀姑巒/陳美莉_阿星.阿曼_說族語在大漢部落的過.txt 第 10 組
  #   要判定的詞：na-ni
  #   族語原文：hato o nani itiraay i cowacowa no niyaro'
  #   切分：hato o na-ni itira-ay i cowa-cowa no niyaro'
  #   glossing：好像 名詞標記 過去-NI 在那裡-實現 介系詞 重疊-四處 屬格 部落
  #   翻譯：都是還自各部落移居到這裡的
  #   規格上的判定：兩段都算詞綴——「過去」在清單裡，NI 是全大寫的
  #   不確定標記，照判斷方法 3c 判不出詞根。
  #   人看的答案：ni 才是詞根，na- 是前綴。
  #   加上「形也要對得上」就成立：清單 4-27 登記的前綴形正是 na-，
  #   所以 na 是前綴、ni 是詞根。
  Given 在阿美語常用構詞標記清單中
    | 編號 | 類別                     | 詞綴或詞 | 族語範例 | 詞素翻譯 | 備註 |
    | 4-27 | 過去                     | na-      | na-tayra | 過去-去  |      |
    | 1-2  | 不確定是什麼時 用大寫或? | -an      | -AN, -?  | -AN, -?  |      |
  When 切分是 "na-ni"，glossing 是 "過去-NI"
  Then 判定結果是
    | 形 | 義   | 構詞         |
    | na | 過去 | （無法判斷） |
    | ni | NI   | （無法判斷） |

  # 下面兩條是同一種情形：詞幹每一段的 gloss 都在清單裡，照判斷
  # 方法 3c 就是詞根分不出來。全語料有 350 個詞是這樣，其中 199 個
  # 就算套用「只寫焦點的是詞綴」也還是分不出來
  # （阿美 108、排灣 47、布農 33、魯凱 10、太魯閣 1）。
  # 這 350 個詞若加上「形也要對得上登記的詞綴」那條規則，
  # 多數判得出來——見下面「實詞的意思撞到清單裡的詞綴 gloss」。

@規格要討論
Scenario: 難判斷：霧台魯凱語 lri-pwa 的 lri 和 pwa 都不在構詞標記清單中
  # 出處：魯凱族/霧台/1.包鳯嬌_Ripunu_耆老的尊榮冠冕.txt 第 182 組
  #   要判定的詞：lri-pwa
  #   族語原文：lu ka wakela ki zinsiw ka kiathingathingale lripwa kay lialivarane
  #   切分：lu KA wa-kela ki zinsiw ka ki-a-thinga-thingale lri-pwa kay lialivarane
  #   glossing：如果 KA 主動-來到 斜格 全省 斜格 被動-限定-重疊-知道 未來-放 這 蝴蝶
  #   翻譯：插飾蝴蝶除非有參加全省賽
  #   為什麼難判斷：清單裡沒有單獨的「未來」，只有 lri-ki-
  #   這個環綴，登記成「未來-被動」；「放」也不在清單裡。
  #   程式是從「未來-被動-打」抽出「未來」當標記，才把 lri
  #   判成詞綴。這個抽法對不對，需要確認。
  Given 在霧台魯凱語常用構詞標記清單中
    | 編號 | 類別      | 詞綴或詞 | 族語範例      | 詞素翻譯     | 備註           |
    | 3-4  | 未來-被動 | lri-ki-  | lri-ki-lrumay | 未來-被動-打 | ai- 大武魯凱語 |
  When 切分是 "lri-pwa"，glossing 是 "未來-放"
  Then 判定結果是
    | 形  | 義   | 構詞 |
    | lri | 未來 | 前綴 |
    | pwa | 放   | 詞根 |
