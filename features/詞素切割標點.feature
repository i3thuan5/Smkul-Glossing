Feature: 詞素切割行不能有標點

  更新日期：2026.10.31

  2026.09 會議案由五決議：第二行（詞素切割）不能有標點，有標點要視為錯誤、
  要有錯誤提示。這個錯誤**照常匯出**，報告上是「錯誤（照常匯出）」，
  **一段只記一筆**。純華語句與詞素翻譯行不檢查。

  詞素切割行可以有的字元：字母、漢字、數字、切割符號（- = <> ~）、
  單引號、空白，以及《原住民族語言書寫系統》（113 年修正）各語言明定的符號：
  阿美語的 ^（喉塞音字母）與 :（長音符號）、泰雅語的 _（音節區辨）、
  賽夏語的 :、邵語的 .。其他字元都算標點。

  錯誤提示一個有問題的詞寫一句，格式是：
  「詞素切割第 N 個詞的 <詞> 有<現象>，程式判斷要<原因>，應該寫是 <修改後>」。
  程式推不出正確寫法時，寫「程式無法判斷，請標注者確認」。

  + 、詞中間的 . 、獨立的說話者標記先不算錯誤，列進報告的待討論章，
  排在最後面，標「規格要討論」。

  例子照語言優先序挑：阿美（秀姑巒→海岸→南勢）→太魯閣→魯凱→排灣→布農、泰雅，
  內容都照語料原樣，半形全形都不改。

Scenario: 沒有標點，通過
  # 例 1（下面用這一段檢查）：阿美族/秀姑巒/陳美莉_阿星.阿曼_說族語在大漢部落的過.docx 第 23 段
  #   族語原句：masamaan i to
  #   詞素切割：masa-maan i to
  #   詞素翻譯：像-什麼 言談標記 斜格
  #   華語翻譯：現在的情況
  # 例 2：太魯閣族/1_黃麗俐Miring_胡月英Tku_生活中的氣候啟示.docx 第 1 段
  #   族語原句：Kiya ha, Tku ita mnswayi
  #   詞素切割：Kiya ha Tku ita mnswayi
  #   詞素翻譯：好的 填補詞 人名 主格.咱們 兄弟姊妹
  #   華語翻譯：好的, Tku 姊妹
  # 例 3：魯凱族/霧台/1.包鳯嬌_Ripunu_耆老的尊榮冠冕.docx 第 2 段
  #   族語原句：ku naganli sia Ripunu
  #   詞素切割：ku nagane=li sia Ripunu
  #   詞素翻譯：主格 名字=我.屬格 叫 人名
  #   華語翻譯：我的名字叫Ripunu
  When 族別是 "阿美"，詞素切割是 "masa-maan i to"
  Then 沒有標點問題

Scenario: 詞頭、詞尾的標點，刪掉就好
  # 全語料沒有阿美的例子。族語原句有標點，詞素切割也照抄，就會記這一筆。
  # 例 1（下面用這一段檢查）：太魯閣族/1_黃麗俐Miring_胡月英Tku_生活中的氣候啟示.docx 第 9 段
  #   族語原句：Iq, kiya.
  #   詞素切割：iq kiya.
  #   詞素翻譯：是 好的
  #   華語翻譯：是, 好的.
  # 例 2：魯凱族/霧台/3.包鳳嬌_Uselrepe_月桃的文化及製作_上集.docx 第 96 段
  #   族語原句：sanatudrusangasu tutadradraw yai ya! vaevanga kay sapanay ka maadraw amiamadu thingale
  #   詞素切割：sana tu-drusa=nga=su tu-ta-adra-draw yai ya! vaeva=nga kay sapa=nay ka ma-adraw am-iya madu thingale
  #   詞素翻譯：只要 做-二=完成貌=你.主格 做-複數-重疊-大 主題標記 呀 一=完成貌 這 草蓆=我們.排除.屬格 關係詞 靜態.限定-大 限定-說 某人要 知道
  #   華語翻譯：只要穿大的，穿兩個了，就會知道，哇！ 一個大的草蓆了
  # 例 3：排灣族/中排灣/1.廖桂香sakenge_劉清勇、李春花、曾秀玉_小米梗的用途.docx 第 12 段
  #   族語原句：avan cu a tja si'uda'udan a sicuayan a qemuqu,
  #   詞素切割：avan cu a tja=si-'uda-'uda-an a sicuayan a q<em>uqu,
  #   詞素翻譯：就 主格.這 連繫詞 我們.包含.屬格=參焦-重疊-如何-AN 連繫詞 從前 連繫詞 <主焦>洗頭
  #   華語翻譯：也就是以前洗頭的文化習俗。
  When 族別是 "太魯閣"，詞素切割是 "iq kiya."
  Then 提示是 "詞素切割第 2 個詞的 `kiya.` 有標點 `.`，程式判斷要刪掉，因為詞素切割不能有標點，應該寫是 `kiya`"

Scenario: 一段有好幾個詞有標點，只記一筆
  # 每個有問題的詞各寫一句，依位置排，用「；」接起來。
  # 例 1（下面用這一段檢查）：太魯閣族/1_黃麗俐Miring_胡月英Tku_生活中的氣候啟示.docx 第 418 段
  #   族語原句：Aji uri o brah
  #   詞素切割：aji. uri. o brah
  #   詞素翻譯：或者 胸部
  #   華語翻譯：或是 胸部的肉塊
  # 例 2：魯凱族/霧台/3.包鳳嬌_Uselrepe_月桃的文化及製作_上集.docx 第 99 段
  #   族語原句：adravane ka alranumi yumauma lu kalraycinga si (lualra nguvaeva)
  #   詞素切割：adravane ka alra=numi i-umauma lu ka-lrayci=nga si (lu alra ngu-vaeva)
  #   詞素翻譯：就算 KA 拿=你們.屬格 處所-田裡 如果 靜態.非限定-枯萎=完成貌 和 (當 拿 指數量-一)
  #   華語翻譯：就算在山上採收的，除非枯萎了
  # 例 3：泰雅族/賽考利克/2_悠瑪阿給安_曾次妹Ciwas_我的媽媽(下).docx 第 164 段
  #   族語原句：Yu:maki yang kya uzi kruma ga bsyaq maki Hugal lga,ini cinkita uzi la.
  #   詞素切割：Yu:m-kaki yan kya uzi kruma ga bsyaq m-kaki hugal la+ga ini cinkita uzi la.
  #   詞素翻譯：Yu:主焦-在 像 那裏 也 其他 主題標記 主焦.久 在 平地 助詞+這詞 否定詞 主焦.露臉 也 助詞
  #   華語翻譯：也有就是其他的住外面久之後，就不見面了
  When 族別是 "太魯閣"，詞素切割是 "aji. uri. o brah"
  Then 提示是 "詞素切割第 1 個詞的 `aji.` 有標點 `.`，程式判斷要刪掉，因為詞素切割不能有標點，應該寫是 `aji`；詞素切割第 2 個詞的 `uri.` 有標點 `.`，程式判斷要刪掉，因為詞素切割不能有標點，應該寫是 `uri`"

Scenario: 只有符號的詞，整個詞刪掉
  # 全語料只有 1 段是這一類。
  # 整個詞刪掉的時候，「應該寫是」寫整行。
  # 例 1（下面用這一段檢查）：排灣族/南排灣/4_華加婧kivi_張枝妹_我來到牡丹的故事.docx 第 195 段
  #   族語原句：pa'apazangal 哈哈
  #   詞素切割：pa-'a-pazangal ＠
  #   詞素翻譯：覺得-困難 ＠
  #   華語翻譯：覺得很難...哈哈
  When 族別是 "排灣"，詞素切割是 "pa-'a-pazangal ＠"
  Then 提示是 "詞素切割第 2 個詞的 `＠` 有符號 `＠`，程式判斷要整個詞刪掉，因為詞素切割不能有標點，應該寫是 `pa-'a-pazangal`"

Scenario: 括號，程式無法判斷
  # 括號裡可能是省略的音（a(ne)ma）、也可能是補充說明，程式不知道要留還是刪。
  # 例 1（下面用這一段檢查）：魯凱族/霧台/3.包鳳嬌_Uselrepe_月桃的文化及製作_上集.docx 第 99 段
  #   族語原句：adravane ka alranumi yumauma lu kalraycinga si (lualra nguvaeva)
  #   詞素切割：adravane ka alra=numi i-umauma lu ka-lrayci=nga si (lu alra ngu-vaeva)
  #   詞素翻譯：就算 KA 拿=你們.屬格 處所-田裡 如果 靜態.非限定-枯萎=完成貌 和 (當 拿 指數量-一)
  #   華語翻譯：就算在山上採收的，除非枯萎了
  # 例 2：排灣族/南排灣/3_華加婧kivi_阮久祥_口述石門部落家族遷移及領域.docx 第 118 段
  #   族語原句：nu neka su langeda ta tia'en nu amayamaya 'en, qeciin.
  #   詞素切割：nu neka su=langeda ta tia'en nu a(ne)ma.aya-a(ne)ma.aya='en qeci-in
  #   詞素翻譯：當 否定 你.屬格=聽 斜格 我.主格 當 重疊-什麼.說=我.主格 殺-受焦
  #   華語翻譯：如果你不聽我的話就把你殺掉
  # 例 3：泰雅族/賽考利克/2_悠瑪阿給安_曾次妹Ciwas_我的媽媽(下).docx 第 3 段
  #   族語原句：inlungan nya ga, aki yaya mu qani qu qrqan nya 高義 qta,
  #   詞素切割：in-lnglung-an=nya ga aki yaay=mu qani qu qroq-an=nya 高義 qani+(ki)ta
  #   詞素翻譯：完成貌-想-處焦=他.屬格 助詞 應該 媽媽=我.屬格 這個 主格 制止-處焦=他.屬格 地名 這裡+主焦.看.祈使
  #   華語翻譯：他的想法是應該是要把我媽媽留在高義這裡
  When 族別是 "魯凱"，詞素切割是 "adravane ka alra=numi i-umauma lu ka-lrayci=nga si (lu alra ngu-vaeva)"
  Then 提示是 "詞素切割第 8 個詞的 `(lu` 有括號 `(`，程式無法判斷，請標注者確認；詞素切割第 10 個詞的 `ngu-vaeva)` 有括號 `)`，程式無法判斷，請標注者確認"

Scenario: 阿美語的 ^ 與 : 不算標點
  # 《原住民族語言書寫系統》的阿美語，^ 是喉塞音字母，: 是長音符號，
  # 放在元音或輔音後面表示延長（iti:raw「遠處的那裡」）。
  # 例 1（下面用這一段檢查）：阿美族/海岸/1_阿索.該拿Aso.Kaynga_文健站長輩的故事_難忘的歌曲_歌曲故事.docx 第 7 段
  #   族語原句：Ono iti:yaay ho sanay
  #   詞素切割：O no iti:ya-ay=ho sanay
  #   詞素翻譯：名詞標記 屬格 那裡-實現=還 如此說
  #   華語翻譯：要分享早期(更早)的故事
  # 例 2：阿美族/海岸/1_阿索.該拿Aso.Kaynga_文健站長輩的故事_難忘的歌曲_歌曲故事.docx 第 219 段
  #   族語原句：Ma so^so haw
  #   詞素切割：Ma-so^so haw
  #   詞素翻譯：主焦-胖 助詞
  #   華語翻譯：胖胖的
  # 例 3：阿美族/海岸/1_阿索.該拿Aso.Kaynga_文健站長輩的故事_難忘的歌曲_歌曲故事.docx 第 155 段
  #   族語原句：Sa mahara:teng ako kona radiw i
  #   詞素切割：Sa ma-hara:teng=ako kona radiw i
  #   詞素翻譯：所以 主焦-想=我.屬格 這個.主格 歌 言談標記
  #   華語翻譯：所以每當我想到這首歌時
  When 族別是 "阿美"，詞素切割是 "O no iti:ya-ay=ho sanay"
  Then 沒有標點問題

Scenario: 泰雅語的 _ 不算標點
  # 《原住民族語言書寫系統》的泰雅語用 _ 區辨 n_g 與 ng，
  # 也區辨有沒有弱化央元音（m_yan「像」、myan「我們」）。
  # 例 1（下面用這一段檢查）：泰雅族/賽考利克/1_楊淑貞Rimuy_姜玉粉Upah_生命故事.docx 第 150 段
  #   族語原句：yaqih hi nya cikay ru mwah myan rgyax la
  #   詞素切割：k_yaqih hi=nya cikay ru m-uwah=myan rgyax la
  #   詞素翻譯：主焦.壞 身體=他.屬格 一些 和 主焦-去=我們.排除.屬格 山上 助詞
  #   華語翻譯：加上先生的身體出現狀況,所以我們就搬回山上老家住
  # 例 2：泰雅族/賽考利克/2_悠瑪阿給安_曾次妹Ciwas_我的媽媽(下).docx 第 30 段
  #   族語原句：lokah iyal tm_yase uzi.
  #   詞素切割：lokah iyal tm_yase uzi
  #   詞素翻譯：主焦.努力 很 採野香菇 也
  #   華語翻譯：她也很努力地採野香菇。
  # 例 3：泰雅族/賽考利克/2_悠瑪阿給安_曾次妹Ciwas_我的媽媽(下).docx 第 34 段
  #   族語原句：ga,n_gyut muya yaka tqinuw balay ka yuyut qasa lga,
  #   詞素切割：ga n_gyut muya yan+ka tqinuw balay ka yuyut qasa la+ga
  #   詞素翻譯：就 慢慢 主焦.種 像+連繫詞 香菇 真正 連繫詞 瓶子 那些 助詞+助詞
  #   華語翻譯：就慢慢種那個真正瓶裝的香菇
  When 族別是 "泰雅"，詞素切割是 "k_yaqih hi=nya cikay ru m-uwah=myan rgyax la"
  Then 沒有標點問題

Scenario: 黏在詞前面的說話者標記，當成一般的族語詞
  # 全語料有 20 處，都在泰雅。Yu: 黏在詞前面，不算說話者標記，
  # 當成一般的族語詞檢查；泰雅語沒有 : 這個符號，所以算標點。
  # 程式建議刪掉冒號，不一定對，請老師在校對表判斷。
  # 例 1（下面用這一段檢查）：泰雅族/賽考利克/1_悠瑪阿給安_曾次妹Ciwas_我的媽媽(上).docx 第 59 段
  #   族語原句：Yu:mwah kekong Smangus qani lga,
  #   詞素切割：Yu:m-uwah kekong Smangus qani la+ga
  #   詞素翻譯：Yu:主焦-來 結婚 地名 這 助詞+助詞
  #   華語翻譯：嫁來這司馬庫斯
  # 例 2：泰雅族/賽考利克/1_悠瑪阿給安_曾次妹Ciwas_我的媽媽(上).docx 第 188 段
  #   族語原句：Yu:han!
  #   詞素切割：Yu:han
  #   詞素翻譯：是
  #   華語翻譯：是
  # 例 3：泰雅族/賽考利克/2_悠瑪阿給安_曾次妹Ciwas_我的媽媽(下).docx 第 128 段
  #   族語原句：Yu:nanu ini ptnaq cikay ziray misu qu laqi ru arwa ra kawas yang sami qani ga,
  #   詞素切割：Yu:nanu ini p-tnaq cikay ziray misu qu laqi ru la+rwa ra kawas yan=sami Yu:qani ga
  #   詞素翻譯：Yu:所以 否定詞 未來-一樣 一些 時代.日語 現在 主格 孩子 助詞 助詞+助詞 助詞 年齡 像=我們.排除.主格 Yu:這些 助詞
  #   華語翻譯：Yu:所以現在一些時代不同，像我們這些年紀的小孩，
  When 族別是 "泰雅"，詞素切割是 "Yu:m-uwah kekong Smangus qani la+ga"
  Then 提示是 "詞素切割第 1 個詞的 `Yu:m-uwah` 有標點 `:`，程式判斷要刪掉，因為詞素切割不能有標點，應該寫是 `Yum-uwah`"

@規格要討論
Scenario: + 先不算錯誤，列入待討論
  # 全語料有 199 段，都在泰雅賽考利克（la+ga、yan+ka），詞素翻譯也用 +（助詞+助詞）。
  # 書寫系統沒有 + 這個符號，看起來是標注者用來表示縮約。
  # 要跟承辦討論：保留，還是提示要改。
  # 程式現在不記「詞素切割有標點」，只列進報告的待討論章。
  # 例 1（下面用這一段檢查）：泰雅族/賽考利克/1_悠瑪阿給安_曾次妹Ciwas_我的媽媽(上).docx 第 19 段
  #   族語原句：yaya mu qani ga, maki zikang nya yaka hngaw m_yugi qani lga,
  #   詞素切割：yaya=mu qani ga m-kaki zikang=nya yan+ka hngaw m-yugi qani la+ga
  #   詞素翻譯：媽媽=我.屬格 這個 助詞 主焦-在 時代=他.屬格 像+連繫詞 主焦.休息 主焦-跳舞 這 助詞+主題標記
  #   華語翻譯：我的媽媽啊，在她舞蹈休息之後，
  # 例 2：泰雅族/賽考利克/2_悠瑪阿給安_曾次妹Ciwas_我的媽媽(下).docx 第 34 段
  #   族語原句：ga,n_gyut muya yaka tqinuw balay ka yuyut qasa lga,
  #   詞素切割：ga n_gyut muya yan+ka tqinuw balay ka yuyut qasa la+ga
  #   詞素翻譯：就 慢慢 主焦.種 像+連繫詞 香菇 真正 連繫詞 瓶子 那些 助詞+助詞
  #   華語翻譯：就慢慢種那個真正瓶裝的香菇
  # 例 3：泰雅族/賽考利克/1_悠瑪阿給安_曾次妹Ciwas_我的媽媽(上).docx 第 9 段
  #   族語原句：nanu yasa yaya mu qani hiya lga,
  #   詞素切割：nanu.yasa yaya=mu qani hiya la+ga
  #   詞素翻譯：所以 媽媽=我.屬格 這個 助詞 助詞+助詞
  #   華語翻譯：所以我的媽媽
  When 族別是 "泰雅"，詞素切割是 "yaya=mu qani ga m-kaki zikang=nya yan+ka hngaw m-yugi qani la+ga"
  Then 沒有標點問題
  And 列入待討論 "+"

@規格要討論
Scenario: 詞中間的 . 先不算錯誤，列入待討論
  # 全語料有 427 段（535 處），排灣、泰雅、太魯閣最多。
  # 前後都緊接字母的 . 才算「詞中間」，看起來是把兩個詞連寫（i.maza、kiya.ga）。
  # 書寫系統只有邵語用 . 區辨字母，這幾個語言都沒有。
  # 要跟承辦討論：保留，還是提示要改。詞頭、詞尾的 . 照樣算標點。
  # 程式現在不記「詞素切割有標點」，只列進報告的待討論章。
  # 例 1（下面用這一段檢查）：太魯閣族/1_黃麗俐Miring_胡月英Tku_生活中的氣候啟示.docx 第 34 段
  #   族語原句：Kika lala bi bgihur kiga
  #   詞素切割：kika lala bi bgihur kiya.ga
  #   詞素翻譯：所以 多 很 風 那
  #   華語翻譯：這就是警示會有很多颱風來襲
  # 例 2：魯凱族/霧台/1.包鳯嬌_Ripunu_耆老的尊榮冠冕.docx 第 197 段
  #   族語原句：la kamani kudra sibengelraylraili kikay
  #   詞素切割：la.kamani kudra si-bengelray-lray=li kikay
  #   詞素翻譯：所以 那.不可見.遠指 戴-重疊-花=我.屬格 這
  #   華語翻譯：所以我才會配戴這樣的頭飾
  # 例 3：排灣族/中排灣/1.廖桂香sakenge_劉清勇、李春花、曾秀玉_小米梗的用途.docx 第 6 段
  #   族語原句：e pay masalu ta tja 'inateveteveljan imaza,
  #   詞素切割：e pay masalu ta tja='<in>a-teve-tevelj-an i.maza
  #   詞素翻譯：填補詞 言談標記 謝謝 斜格 我們.包含.屬格=<完成貌>KA-重疊-聚集-處焦 處所.這裡
  #   華語翻譯：在這要謝謝大家聚在這裡，
  When 族別是 "太魯閣"，詞素切割是 "kika lala bi bgihur kiya.ga"
  Then 沒有標點問題
  And 列入待討論 "詞中間的 ."

@規格要討論
Scenario: 獨立的說話者標記先不算錯誤，列入待討論
  # 全語料有 46 段（63 處），在排灣、泰雅、布農。
  # 整個詞是 1 到 3 個字母加冒號（G:、Lj:、Yu:）就算說話者標記，
  # 跟排版分析.feature 的「對話組」是同一個現象。
  # 要跟承辦討論：保留，還是提示要改。
  # 程式現在不記「詞素切割有標點」，只列進報告的待討論章。
  # 例 1（下面用這一段檢查）：排灣族/東排灣/1_阮翠芳Gesi_高桂妹_80歲vuvu的傳說故事.docx 第 323 段
  #   族語原句：G: aicu a paka
  #   詞素切割：G: aicu a paka
  #   詞素翻譯：G: 主格.這 連繫詞 關於
  #   華語翻譯：關於這個
  # 例 2：泰雅族/賽考利克/1_悠瑪阿給安_曾次妹Ciwas_我的媽媽(上).docx 第 93 段
  #   族語原句：Yu: tminun ga
  #   詞素切割：Yu: c<m>inun ga
  #   詞素翻譯：Yu: <主焦>編織 助詞
  #   華語翻譯：織布啊
  # 例 3：布農族/巒群/2_松念竹Akuan_全英輝_早期布農族人生活分享(婚姻、食物、生活).docx 第 12 段
  #   族語原句：A: na mahau i tama tina)
  #   詞素切割：A: na=mahau' i tama tina
  #   詞素翻譯：A: 非實現=主焦.罵 斜格 父親 母親
  #   華語翻譯：爸媽會罵
  When 族別是 "排灣"，詞素切割是 "G: aicu a paka"
  Then 沒有標點問題
  And 列入待討論 "說話者標記"

@規格要討論
Scenario: 說話者標記以外還有標點，標點照樣記
  # 說話者標記列進待討論，同一段其他的標點照樣記「詞素切割有標點」。
  # 出處：排灣族/南排灣/4_華加婧kivi_張枝妹_我來到牡丹的故事.docx 第 114 段
  #   族語原句：(anema aya tjen ta azua?) 電土 ayain sicuayan
  #   詞素切割：K: anema aya=tjen ta azua? Lj: 電土 aya-in sicuayan
  #   詞素翻譯：K: 什麼 說=我們.主格 斜格 主格.那 Lj: 電土 說-受焦 從前
  #   華語翻譯：(那是什麼?) 我們以前叫那個"電土"
  When 族別是 "排灣"，詞素切割是 "K: anema aya=tjen ta azua? Lj: 電土 aya-in sicuayan"
  Then 提示是 "詞素切割第 5 個詞的 `azua?` 有標點 `?`，程式判斷要刪掉，因為詞素切割不能有標點，應該寫是 `azua`"
  And 列入待討論 "說話者標記"
