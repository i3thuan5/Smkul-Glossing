Feature: 字元正規化

  更新日期：2026.11.23

  每一條是一個自動處理。附真實例子當做討論的依據，

  例子照語言優先序挑：阿美（秀姑巒→海岸→南勢）→太魯閣→魯凱→排灣，
  內容都照語料原樣，半形全形都不改。只有一點：Gherkin 格式檢查不允許
  只有行尾空白與連續空行有整理過，字本身沒有動。

  這一類是一行之內的字元替換，不會動到行的數量。

Scenario: 移除 BOM（U+FEFF）
  # 全語料共 2 筆，都在 docx 第一段時間碼行的最前面。
  # docx 也需要這一條：BOM 看不見，可是它擋在時間碼前面，
  # 時間碼就認不出來，第一段會切錯。拿掉 BOM 以後時間碼才能正常解析。
  # 例 1：魯凱族/霧台/3.包鳳嬌_Uselrepe_月桃的文化及製作_上集.docx 第 1 段
  #   原句子：﻿0:00:00.000,0:00:05.580
  #   處理後：0:00:00.000,0:00:05.580
  # 例 2：泰雅族/賽考利克/5_悠瑪阿給安_謝森祿_泰雅俚語(上).docx 第 1 段
  #   原句子：﻿0:00:03.244,0:00:08.163
  #   處理後：0:00:03.244,0:00:08.163
  # 注意：上面「原句子」與下面 When 的引號裡，時間碼的前面有一個看不見的 BOM。
  When 原本的一行是 "﻿0:00:00.000,0:00:05.580"
  Then 處理後是 "0:00:00.000,0:00:05.580"

Scenario: 全形 ＝ 換成半形 =
  # 全語料共 6 筆。
  # 例 1：排灣族/南排灣/2_華加婧kivi_趙美英_我們是這樣來的.txt
  #   原句子：否定＝完成貌 非實現 使役-'I-讀書.台語
  #   處理後：否定=完成貌 非實現 使役-ʼI-讀書.台語
  # 例 2：排灣族/南排灣/4_華加婧kivi_張枝妹_我來到牡丹的故事.txt
  #   原句子：venelid＝＝ mara kumuapi
  #   處理後：venelid== mara kumuapi
  # 例 3：排灣族/南排灣/2_華加婧kivi_趙美英_我們是這樣來的.txt
  #   原句子：neʼa＝anga uri pa-'i-taqeci
  #   處理後：neʼa=anga uri pa-ʼi-taqeci
  # 例 1、例 3 的單引號同時照「資料寫 U+0027、U+2018、U+2019、U+02BC 都接受」那條轉成 U+02BC。
  When 原本的一行是 "否定＝完成貌 非實現 使役-'I-讀書.台語"
  Then 處理後是 "否定=完成貌 非實現 使役-ʼI-讀書.台語"

Scenario: 資料寫 U+0027、U+2018、U+2019、U+02BC 都接受。之後使用時引號再統一轉成 U+02BC
  # 全語料（docx）要轉的有 5462 行、8048 個引號。
  # 當引用符號用的引號不轉，見下一條「當引用符號用的引號不轉」。
  # 例 1：阿美族/秀姑巒/陳美莉_阿星.阿曼_說族語在大漢部落的過.txt
  #   原句子：nika orira o no mako haw i mi-do’do to i loma'
  #   處理後：nika orira o no mako haw i mi-doʼdo to i lomaʼ
  # 例 2：太魯閣族/1_黃麗俐Miring_胡月英Tku_生活中的氣候啟示.txt
  #   原句子：‘Tai ta na bi mapa wah!' msa ni
  #   處理後：ʼTai ta na bi mapa wah!' msa ni
  #   （wah!' 的 ' 是引用的結尾，不轉；開頭的 ‘ 程式分不出來，還是轉，見上尾「單獨一個 ‘ 開頭的引用」）
  # 例 3：排灣族/南排灣/1_華加婧kivi_黃富_東源部落誌.txt
  #   原句子：Vacu’u
  #   處理後：Vacuʼu
  When 原本的一行是 "nika orira o no mako haw i mi-do’do to i loma'"
  Then 處理後是 "nika orira o no mako haw i mi-doʼdo to i lomaʼ"

Scenario: 當引用符號用的引號不轉
  # 喉塞音常出現在詞頭（ʼama、ʼu）與詞尾（lomaʼ），所以只看位置分不出是喉塞音還是引用符號。
  # 下面四種程式分得出來，是引用符號，不轉：
  #   一、兩個 ‘ 連在一起（‘‘），是雙引號的開頭；
  #   二、兩個引號連在一起，接在字母後面、後面不是字母（gagu’’、ljameljam’’），是雙引號的結尾；
  #   三、緊接在 ! ? 後面（wah!'），是引用的結尾；
  #   四、單獨一個，前後都是空白。
  # 全語料（docx）照這四條不轉的有 65 個（一 28 個、二 32 個、三 2 個、四 3 個），
  # 一、二多半在排灣族/中排灣/5.廖桂香sakenge_藍石化_生活甘苦談。
  # 逗號後面的不算：排灣 ,’emeljang 的 ’ 是喉塞音，只是逗號後面沒有空白。
  # 南排灣 4_華加婧kivi_張枝妹_我來到牡丹的故事 第 156～171 段有 ’’u、ne’’a 這種寫兩個的，
  # 後面接字母，不合第二條，照樣轉。
  # 例 1：太魯閣族/1_黃麗俐Miring_胡月英Tku_生活中的氣候啟示.docx 第 139 段（第三條）
  #   原句子：‘Tai ta na bi mapa wah!' msa ni
  #   處理後：ʼTai ta na bi mapa wah!' msa ni
  # 例 2：太魯閣族/2_黃麗俐Miring_張愛珠Imay_為孩子以身作則.docx 第 143 段（第四條）
  #   原句子："Bikuy ' sun mu.
  #   處理後："Bikuy ' sun mu.
  # 例 3：排灣族/中排灣/5.廖桂香sakenge_藍石化_生活甘苦談.docx 第 149 段（第一、二條）
  #   原句子：‘‘a gagu a tima cu gagu’’ aya ’u ama?
  #   處理後：‘‘a gagu a tima cu gagu’’ aya ʼu ama?
  When 原本的一行是 "‘Tai ta na bi mapa wah!' msa ni"
  Then 處理後是 "ʼTai ta na bi mapa wah!' msa ni"
  When 原本的一行是 ""Bikuy ' sun mu."
  Then 處理後是 ""Bikuy ' sun mu."
  When 原本的一行是 "‘‘a gagu a tima cu gagu’’ aya ’u ama?"
  Then 處理後是 "‘‘a gagu a tima cu gagu’’ aya ʼu ama?"

Scenario: 詞素切割行與詞素翻譯行的 en-dash – 換成半形 -
  # 全語料共 11 筆。
  # 例 1：阿美族/秀姑巒/陳美莉_阿星.阿曼_說族語在大漢部落的過.txt 第 80 段
  #   原句子：有=完成貌 介系詞 PI–書-處焦 主焦-學習 斜格 話 屬格 族名 言談標記
  #   處理後：有=完成貌 介系詞 PI-書-處焦 主焦-學習 斜格 話 屬格 族名 言談標記
  # 例 2：排灣族/南排灣/4_華加婧kivi_張枝妹_我來到牡丹的故事.txt 第 28 段
  #   原句子：車子 連繫詞 重疊–巨大
  #   處理後：車子 連繫詞 重疊-巨大
  # 例 3：布農族/郡群/3.林美芳Abus_顏浩義_布農英雄Dahuali後裔對本家所遭遇之.txt 第 205 段
  #   原句子：pan-cina–un                 iahai
  #   處理後：pan-cina-un                 iahai
  When 原本的一行是 "有=完成貌 介系詞 PI–書-處焦 主焦-學習 斜格 話 屬格 族名 言談標記"
  Then 處理後是 "有=完成貌 介系詞 PI-書-處焦 主焦-學習 斜格 話 屬格 族名 言談標記"

Scenario: 多餘的空白合併成一個
  # 全語料共 4458 筆。
  # 例 1：阿美族/秀姑巒/陳美莉_阿星.阿曼_說族語在大漢部落的過.txt 第 61 段
  #   原句子：長輩回說  那個什麼
  #   處理後：長輩回說 那個什麼
  # 例 2：太魯閣族/1_黃麗俐Miring_胡月英Tku_生活中的氣候啟示.txt 第 328 段
  #   原句子：龍葵
  #   處理後：龍葵
  # 例 3：魯凱族/霧台/1.包鳯嬌_Ripunu_耆老的尊榮冠冕.txt 第 105 段
  #   原句子：但 這 否定  這
  #   處理後：但 這 否定 這
  When 原本的一行是 "長輩回說  那個什麼"
  Then 處理後是 "長輩回說 那個什麼"

@規格要討論
Scenario: 單獨一個 ‘ 開頭的引用，程式分不出來，還是轉
  # 出處：太魯閣族/1_黃麗俐Miring_胡月英Tku_生活中的氣候啟示.docx 第 139 段
  # 為什麼難判斷：開頭的 ‘ 跟排灣語喉塞音開頭的 ’ama 一樣，都是詞頭、後面接字母。
  # 照「當引用符號用的引號不轉」的規則，結尾的 wah!' 不轉，開頭的 ‘ 會轉成 ʼ（下面的 Then）。
  # 應該是兩個都不轉：‘Tai ta na bi mapa wah!' msa ni。
  When 原本的一行是 "‘Tai ta na bi mapa wah!' msa ni"
  Then 處理後是 "ʼTai ta na bi mapa wah!' msa ni"

@規格要討論
Scenario: 雙引號的開頭不是兩個 ‘，程式分不出來，還是轉
  # 出處：排灣族/中排灣/3.廖桂香Sakenge_Selep Ruviljivili_生活經歷.docx 第 64 段
  # 同一類還有：排灣族/中排灣/5.廖桂香sakenge_藍石化_生活甘苦談.docx 第 108 段的 ‘’vaqar。
  # 為什麼難判斷：開頭寫成兩個 U+0027（''）或 ‘’，不是兩個 ‘，
  # 跟南排灣 ’’u 那種寫兩個的喉塞音分不開。
  # 照規則，開頭的 '' 會轉成 ʼʼ，結尾的 '' 接在字母後面、後面是逗號，不轉（下面的 Then）。
  # 應該是開頭結尾都不轉：''nanguaq cu aravac a siputjabel ta ʼula'',。
  When 原本的一行是 "''nanguaq cu aravac a siputjabel ta ’ula'',"
  Then 處理後是 "ʼʼnanguaq cu aravac a siputjabel ta ʼula'',"

@規格要討論
Scenario: 雙引號的結尾後面沒有空白，程式分不出來，還是轉
  # 出處：排灣族/中排灣/5.廖桂香sakenge_藍石化_生活甘苦談.docx 第 249 段
  # 為什麼難判斷：結尾的 ’’ 後面直接接下一個詞（sipucemel’’ayain），
  # 後面是字母，不合「後面不是字母」，跟 ne’’a 這種寫兩個的喉塞音一樣。
  # 另外排灣族/中排灣/1.廖桂香sakenge_劉清勇、李春花、曾秀玉_小米梗的用途.docx 第 55 段的 4’’58
  # （4 分 58 秒）前後都是數字，也會轉。
  # 照規則，開頭的 ‘‘ 不轉，結尾的 ’’ 轉成 ʼʼ（下面的 Then）。
  # 應該是：e ‘‘tasicuayan saqetju a caucau a sicuayan, anema sipucemel’’ayain aʼen,。
  When 原本的一行是 "e ‘‘tasicuayan saqetju a caucau a sicuayan, anema sipucemel’’ayain a’en,"
  Then 處理後是 "e ‘‘tasicuayan saqetju a caucau a sicuayan, anema sipucemelʼʼayain aʼen,"
