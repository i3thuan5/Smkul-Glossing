Feature: 清掉 docx 匯出留下的註解殘留

  更新日期：2026.8.22

  每一條是一個自動處理。Scenario 後面附真語料的例子當做討論的依據，
  When 是原本的內容，Then 是程式處理後的內容。

  例子照語言優先序挑：阿美（秀姑巒→海岸→南勢）→太魯閣→魯凱→排灣，
  內容都照語料原樣，半形全形都不改。只有一點：Gherkin 格式檢查不允許
  行尾空白與連續空行，所以 """ 區塊裡的這兩種空白有整理過，
  字本身沒有動。

  docx 匯出成 txt 的時候，審閱註解會留下兩種殘留：內文裡的
  [字母] 錨點，還有整段寫進內文的註解本文。兩種都對照 docx 的
  註解自動刪掉，不算錯誤。

Scenario: 刪掉內文裡的註解錨點
  # 全語料共 105 筆。
  # 例 1：排灣族/東排灣/2_阮翠芳Gesi_阮秀美_土坂派出所拘留所的故事.txt
  #   原本：[c]
  #   處理後：
  # 例 2：布農族/巒群/2_松念竹Akuan_全英輝_早期布農族人生活分享(婚姻、食物、生活).txt
  #   原本：181.   [e]
  #   處理後：181.
  # 例 3：排灣族/南排灣/4_華加婧kivi_張枝妹_我來到牡丹的故事.txt
  #   原本：[j]對話？
  #   處理後：對話？
  # 下面 When 用的是：排灣族/中排灣/2.廖桂香sakenge_廖進花-tinaqetaq 芋頭粉加花生粉蔬菜飯.txt
  Given docx 的審閱註解是
    | 字母 | 內容                                                                        |
    | a    | 1: ‘i tja vai' anga2: 'i tja=vai'=anga3: 疑問感嘆  我們.包含.屬格=去=完成貌 |
  When 讀入這幾行有註解殘留
    """
    pay, 'itja [a]vai' anga tjemuqetjuaq tucu,
    """
  Then 清掉註解後是
    """
    pay, 'itja vai' anga tjemuqetjuaq tucu,
    """

Scenario: 刪掉混進內文的註解本文
  # 全語料共 6 筆。
  # 例 1：排灣族/東排灣/3_阮翠芳Gesi_鄭玉英_生命故事.txt
  #   原本：[a]得，得到 ⏎ [b]ka ⏎ 當.過去式
  #   處理後：(刪掉 49 行註解本文)
  # 例 2：布農族/郡群/3.林美芳Abus_顏浩義_布農英雄Dahuali後裔對本家所遭遇之.txt
  #   原本：[a]待討論 ⏎ [b]疑似詞彙化
  #   處理後：(刪掉 2 行註解本文)
  # 例 3：排灣族/南排灣/4_華加婧kivi_張枝妹_我來到牡丹的故事.txt
  #   原本：[a]全中文的話要4行都一樣 ⏎ [b]用兩個對話的方式 ⏎ [c]主焦.來
  #   處理後：(刪掉 29 行註解本文)
  # 下面 When 用的是：排灣族/東排灣/2_阮翠芳Gesi_阮秀美_土坂派出所拘留所的故事.txt
  # 從第一行 [字母] 起，後面整段都是註解本文。
  Given docx 的審閱註解是
    | 字母 | 內容                                                                     |
    | a    | 所以的 "aicu" 標 “主格.這”                                               |
    | b    | =anan                                                                    |
    | c    | 言談標記？還是先大寫？                                                   |
    | d    | 加焦點                                                                   |
    | e    | 來.祈使                                                                  |
    | f    | 切                                                                       |
    | g    | 當.過去式                                                                |
    | h    | -                                                                        |
    | i    | 加完成貌                                                                 |
    | j    | 加主焦                                                                   |
    | k    | 跟第70的kadju不一致                                                      |
    | l    | ripun 還是dripung?                                                       |
    | m    | 也有 ku/'u 在裡面嗎？ ilu 'u keljang?感覺是有“我”的意思？                |
    | n    | 字根後面也有-a你們的方言是n 還是ng                                       |
    | o    | 也有重疊，第二行的e可以還原：k<in>i-la<ngeda>ngeda-an                    |
    | p    | 標“互相”如何？                                                           |
    | q    | ka當.過去式第一二三行都單獨                                              |
    | r    | 如果第二三行用 - （ki當前綴），第一行也應該寫在一起（kitjaisangas)才一致 |
    | s    | 少寫了母語，ljaki? ljiki?                                                |
    | t    | i-sangas                                                                 |
    | u    | 有navan 嗎？不是mavan? 還是na-avan?                                      |
    | v    | ka 在第一二三行單獨當.過去式                                             |
    | w    | kim-en                                                                   |
    | x    | k<em>im                                                                  |
    | y    | 第三行沒有標到                                                           |
    | z    | 加完成貌                                                                 |
  When 讀入這幾行有註解殘留
    """
    0:00:19.060,0:00:19.560
    na
    na
    完成貌
    [c]
    就

    8.
    0:00:21.080,0:00:23.660
    sikuvekuv ta napasaliw a  caucau
    si-kuvekuv          ta       na-pasaliw      a            caucau
    參焦-監獄  斜格  完成貌-過分        連繫詞     人

    聽說是關犯人的地方

    9.
    0:00:24.060,0:00:24.720
    izua
    izua
    存在

    那有

    10.
    0:00:25.760,0:00:27.820
    izua ita milimilingan
    izua  ita  mili-milingan
    存在 一 重疊-故事
    有一段故事比較

    11.
    0:00:30.160,0:00:31.060
    tjamapaula
    tja-ma-paula
    比較-主焦-可憐
    哀怨的

    12.
    0:00:32.660,0:00:33.480
    ulja
    ulja
    因為
    因為

    13.
    0:00:35.440,0:00:35.940
    tiamadju
    tiamadju
    他們.主格
    他們

    14.
    0:00:36.900,0:00:39.980
    kasicuayan izua aza madrusa maqacuvucuvung a vavayan kinuvekuv i taladj
    kasicuayan izua  aza         ma-drusa       ma-qa<cuvu>cuvung  a          vavayan k<in>uvekuv
    以前            存在 主格.那  主焦-二            主焦-<重疊>足夠      連繫詞  女生      <完成貌[d]>監獄
    i    taladj
    I   裡面

    曾經關著兩個年輕的婦女

    15.
    0:00:39.980,0:00:42.480
    saka navaleljevel aravac
    saka  na-valeljevel aravac
    然後 完成貌-漂亮  非常
    而且長的都非常漂亮

    16.
    0:00:44.740,0:00:46.640
    akumaya kuvekuven
    akumaya kuvekuv-en
    為何          監獄-受焦
    之所以為什麼被關

    17.
    0:00:47.320,0:00:48.780
    ika a'en na sepuwalan
    ika=a'en            na-se-puwalan
    否定=我.主格  完成貌-屬-清楚
    我也不太清楚

    18.
    0:00:49.220,0:00:51.240
    ljakua aza     hasisiu tucu.
    ljakua aza        hasisiu            tucu
    但是  主格.那 派出所.日語  現在
    不過我們派出所

    19.
    0:00:51.400,0:00:53.540
    mavan sinanguaq aicu a umaumaq
    mavan si-na-nguaq aicu    a            uma-umaq
    就是     參焦-NA-好  這個  連繫詞  重疊-家
    仍然把它保留的很完整

    20.
    0:00:55.260,0:00:58.320
    avansika neka kidadut sa kemapalak tjaimadju
    avansika neka ki-dadut  sa     k<em>a-palak    tjaimadju
    所以        否定   自己-近 然後  <主焦>KA-壞掉 他們.斜格
    所以沒人敢去觸碰它破壞它

    21.
    0:00:59.780,0:01:01.120
    azua niamen na i qinaljan
    azua      niamen         a              i         qinaljan
    主格.那 我們.屬格  連繫詞  處所   部落
    那也是我們族人

    22.
    0:01:02.140,0:01:02.820
    ita
    ita
    一
    一個

    23.
    0:01:03.220,0:01:04.460
    valeljevel a milimilingan
    valeljevelj a           mili-milingan
    美麗          連繫詞 重疊-故事
    很美麗的故事

    24.
    0:01:06.000,0:01:07.480
    tja pakata kinatjengelayan a milimilingan
    tja      paka-ta           k<in>a-tjengelay-an                a           mili-milingan
    比較  經由-斜格     <完成貌>KA-喜歡-AN        連繫詞   重疊-故事
    比較愛情故事

    25.
    0:01:10.360,0:01:11.540
    aicu i Tupan
    aicu    i         Tupan
    這個  處所  地名
    這土板村

    26.
    0:01:12.940,0:01:14.060
    Tupan a qinaljan
    Tupan   a            qinaljan
    地名   連繫詞   部落
    土板村

    27.
    0:01:20.760,0:01:21.760
    idu pacuni
    idu pacun-i
    來[e]   看-祈使

    來看看

    28.
    0:01:24.020,0:01:24.940
    patjavat-i
    patjavat-i
    移動-祈使
    移一下

    29.
    0:01:28.340,0:01:29.400
    djemaljun anga
    dj<em>aljun=anga
    <主焦>到達=完成貌

    到了

    30.
    0:01:30.120,0:01:30.760
    aicu
    aicu
    這是
    這是

    31.
    0:01:31.400,0:01:33.360
    aicu i tjaiteku a qinaljan
    aicu   i         tja-i-teku                a        qinaljan
    這是 處所  比較-處所-下面   主格  部落
    這是下面的部落

    32.
    0:01:34.480,0:01:36.120
    tjaiteku a qinaljan
    tja-i-teku              a       qinaljan
    比較-處所-下面 主格 部落
    下面的部落

    33.
    0:01:40.320,0:01:42.420
    aicu a su pacucunan sedjelj
    aicu   a        su=pa<cu>cun-an          sedjelj
    這是 主格  你.屬格=<重疊>看-AN   都是
    你看到的都是

    34.
    0:01:44.160,0:01:45.640
    cuni ca gadugaduan
    cun-i       ca     gadu-gadu-an
    看-祈使  這     重疊-山-AN
    看這個山脈

    35.
    0:01:46.660,0:01:47.620
    gadugaduan
    gadu-gadu-an
    重疊-山-AN
    山脈

    36.
    0:01:49.340,0:01:51.140
    aicu nia hisisiu
    aicu     nia              hisisiu
    這個  我們.屬格  派出所.日語
    這是我們的派出所

    37.
    0:01:54.060,0:01:54.760
    wi
    wi
    言談標記
    喴

    38.
    0:01:55.960,0:01:57.560
    sasingu sasingu
    sasing-u    sasing-u
    相片-祈使 相片-祈使
    ㄚ..你先錄你先錄

    39.
    0:01:59.240,0:02:00.760
    ai anga cuivan
    ai=anga                      Cuivan
    言談標記=完成貌   人名
    唉呀啊...翠芳

    40.
    0:02:01.840,0:02:06.480
    naizua za a ramaljemaljen a na ti sa Ljaljumegan
    na-izua          za     a           ra<malje>maljeng   a              na   ti       sa-Ljaljumegan
    完成貌-存在 那   主格    <重疊>前輩                連繫詞  XX  主格  已故-人名
    有一位老人叫"拉魯麼砍"

    41.
    0:02:06.860,0:02:09.280
    aza ti ubasan  Uwan anga
    aza          ti         ubasan  Uwan=anga
    主格.那  主格  歐巴桑.日語    人名=完成貌
    還有一位"砂島碗"

    42.
    0:02:09.560,0:02:12.300
    a natjaucikel na na ramaljemaljen
    a             na-tjaucikel    na  na     ra<malje>maljeng
    填補詞  完成貌-告訴  XX  屬格 <重疊>前輩

    以前老人家曾傳述的故事發生是這樣

    43.
    0:02:12.720,0:02:17.300
    ljakua na  uli namasan kumuing aza ti saUwan naika paqulid
    ljakua na   uli            na-masan[f]      kumuing  aza         ti       sa-Uwan        na-ika            paqulid
    但是   NA  非實現   完成貌-成為  公務員   主格.那  主格  已故-人名   完成貌-否定  正確

    但是他知道他會成為公務員沒有往壞的方面想

    44.
    0:02:18.080,0:02:20.700
    ti Saljalumegan namasiyaq a varung
    ti        sa-Ljalumegan na-masiyaq    a             varung
    主格  已故-人名         完成貌-害羞 連繫詞   心

    而"拉魯麼砍"覺得被關很丟臉

    45.
    0:02:21.040,0:02:23.440
    naikaui a paricungen na Dripung
    na-ika-ui                    a             pa-ricung-en       na      Dripung
    完成貌-否定-同意  連繫詞  使役-立正-受焦  屬格 日本
    不願意跟日本人承認妥協

    46.
    0:02:24.000,0:02:25.940
    nakipacay ta aza kuvekuv
    na-ki-pacay           ta       aza         kuvekuv
    完成貌-自己-死  斜格   主格.那  監獄

    就在派出所旁那間小屋自殺

    47.
    0:02:26.440,0:02:27.760
    aza hasisiu au
    aza          hasisiu           au
    主格.那  派出所.日語 然後

    就那派出所 .....然後

    48.
    0:02:28.940,0:02:32.560
    qadjaw kinatjailauz kanai ka tjaizaya  za ti Saljaljumegan aya
    qadjaw  ki-na-tja-i-lauz                         ka-na-ika                tja-i-zaya                za    ti
    不知道   KI-完成貌-比較-處所-下面   KA-完成貌-否定 比較-處所-上面     那   主格
    sa-Ljaljumegan aya
    已故-人名          說
    不知當時"拉魯麼砍"是在左邊還是右邊

    49.
    0:02:32.880,0:02:35.460
    na nakireqel ta huluseki aya
    na  na-ki-reqel                ta      huluseki aya
    XX  完成貌-自己-上吊 斜格  絲巾        說
    他用絲巾上吊自殺

    50.
    0:02:36.240,0:02:37.920
    ka ayain na Dripung
    ka ayain  na      Dripung
    當[g]  用         屬格  日本

    日本人發現他時

    51.
    0:02:38.580,0:02:39.680
    au timadju
    au               timadju
    言談標記  他.主格
    而她(拉魯麼砍)

    52.
    0:02:40.820,0:02:41.827
    navaleljevelj aravac
    na-valeljevelj    aravac
    完成貌-漂亮       非常
    長得非常漂亮.

    53.
    0:02:41.827,0:02:44.680
    natjuluvu  a natjengelay a maleka Dripung aya
    na-tjuluvu           a            na-tjengelay           a               maleka   Dripung aya
    完成貌-多         連繫詞        完成貌-喜歡         連繫詞     一些        日本        說
    當時有好多日本人追她

    54.
    0:02:44.780,0:02:45.460
    ljakua
    ljakua
    但是
    但是

    55.
    0:02:45.980,0:02:47.040
    ulja naika uli
    ulja   na=[h]ika              uli
    因為 完成貌=否定  非實現
    因為不可能

    56.
    0:02:47.540,0:02:49.000
    e masan anema
    e              ma-san       anema
    填補詞  主焦-成為  什麼
    會做甚麼大事

    57.
    0:02:50.040,0:02:53.060
    venalung ta kipacay kireqel ta huluseki aya
    v<en>alung   ta     ki-pacay  ki-reqel      ta      huluseki aya
    <主焦>心     斜格  自己-死  自己-上吊 斜格  絲巾        說
    所以失望的用絲巾選擇輕生

    58.
    0:02:53.300,0:02:55.960
    au ka ayaing na kisace i hasisu
    au               ka     ayain   na     kisace    i        hasisiu
    言談標記 當時  用        屬格 警察    處所  派出所.日語
    後來警察去查看

    59.
    0:02:56.860,0:02:59.180
    naaya anga sema
    na-aya=anga              sema
    完成貌-說=完成貌   舌
    她舌頭已伸出來

    60.
    0:03:01.520,0:03:02.020
    嗯
    嗯
    嗯
    嗯

    61.
    0:03:02.160,0:03:04.000
    au aza ti ubasan Uwan
    au                aza         ti        ubasan             Uwan
    言談標記  主格.那  斜格  歐巴桑.日語  人名
    然後就把"砂島碗"

    62.
    0:03:04.300,0:03:05.580
    napinasasaw
    na-p<in>a-sasaw
    完成貌-<受焦[i]>使役-外面
    有放出來

    63.
    0:03:07.340,0:03:10.220
    au ti basan Uwan ika kemeljang tu namacay a saladj aya yu
    au                ti      basan   Uwan ika   k<em>eljang    tu                na-macay        a             saladj  aya yu
    言談標記 主格 歐巴桑 人名  否定 <主焦>知道     補語連詞  完成貌-死亡[j]  連繫詞  同伴     說   助詞
    但在被關時她完全不知"拉魯麼砍"已經自殺身亡喔

    64.
    0:03:11.060,0:03:12.860
    lja izua azua viden
    lja              izua   azua       viden
    言談標記 存在  主格.那  隔間
    因為那房子有用水泥隔間

    65.
    0:03:13.180,0:03:16.460
    viden viden aya tjen ta azua
    viden viden aya=tjen                      ta      azua
    間隔   間隔   說=我們.包含.主格 斜格  主格.那
    我們說那是中間隔

    66.
    0:03:17.040,0:03:20.080
    namaya ta aza tja umaq izuwa tjailauz a qaqelengan au
    namaya ta      aza          tja=umaq                   izua    tja-i-lauz               a            qa-qeleng-an    au
    就像      斜格  主格.那 我們.包含.屬格=家  存在  比較-處所-下面 連繫詞   重疊-躺-AN      言談標記
    如同我們的家.房間有分左右旁邊

    67.
    0:03:20.780,0:03:22.700
    naika kemeljang aya au
    na-ika              k<em>eljang      aya  au
    完成貌-否定  <主焦>知道         說  言談標記
    "砂島碗"不知發生了什麼事..然後

    68.
    0:03:23.800,0:03:24.640
    na
    na
    ==

    就

    69.
    0:03:25.320,0:03:26.480
    aza ti ubasan Uwan
    aza           ti      ubasan Uwan
    主格.那 主格  歐巴桑  人名
    那位"砂島碗"

    70.
    0:03:27.100,0:03:28.600
    natjalja lukadjuan lja tauta
    na-tja-lja-lu-kadju-an                lja                tauta
    完成貌-比較-LJA-LU-貪戀-AN 言談標記   也
    當時年輕貌美情感豐富

    71.
    0:03:29.000,0:03:30.180
    namakadju aya
    na-ma-kadju            aya
    完成貌-主焦-貪戀  說
    也很多情

    72.
    0:03:30.620,0:03:32.840
    tja lukaian pai ta pacengecen
    tja=lu-kai-an                            pai              ta      pa-cengeceng
    我們.包含.屬格=LU-話-AN   言談標記 斜格 使役-正確

    沒關係!細述要確實...真正的

    73.
    0:03:33.140,0:03:35.640
    ui namakadju saka aza na Dripung a ziday
    ui                 na-ma-kadju            saka  aza          na        Dripung  a              ziday
    言談標記  完成貌-主焦-如何[k]  而且  主格.那  屬格    日本        連繫詞  時代.日語
    她很多情.而且在日本時代期間

    74.
    0:03:36.040,0:03:37.821
    naikaui ma aya itjen
    na-ika-ui               ma-aya=itjen
    屬格-否定-同意  主焦-說=我們.包含.主格
    他們嚴禁

    75.
    0:03:38.960,0:03:41.580
    a kisudju itjen kamaya tiamadju a ripun[l]
    a              ki-sudju=itjen                          ka-maya=tiamatju      a              Dripung
    連繫詞  KI-朋友=我們.包含.主格       KA-不要= 他們.主格  連繫詞   日本

    嚴禁村裡頭談戀愛

    76.
    0:03:41.760,0:03:45.340
    naikaui a tja kisudjuan na aya aza ramaljemaljeng
    na-ika-ui                   a             tja=ki-sudju-an                               na-aya  aza         ra<malje>maljeng
    完成貌-否定-肯定 填補詞  我們.包含.屬格=得到-情人-AN  完成貌-說  主格.那 <重疊>前輩
    而且老人家說那些日本人也不允許村裡婦女喜歡他們

    77.
    0:03:46.160,0:03:47.760
    au namaitazua
    au               na-maitazua
    言談標記 完成貌-這樣
    就是這樣

    78.
    0:03:47.980,0:03:50.200
    saka na valeljevelj angta aza
    saka  na-valeljevelj angata  aza
    而且  完成貌-漂亮   確實   主格.那
    不過流傳那兩位小姐

    79.
    0:03:50.440,0:03:53.000
    ti Ljalumegan kati ubasan Uwan na aya
    ti       Ljalumegan kati ubasan  Uwan na      aya
    主格 人名              跟     歐巴桑   人名  屬格 說
    "拉魯麼砍"跟"砂島碗"真的很美

    80.
    0:03:53.500,0:03:56.160
    aza tia kaka i Luliku  kaka i Draruy
    aza         tia      kaka           i  Luliku  kaka           i Draruy
    主格.那 主格  兄弟姊妹  I  人名     兄弟姊妹  I  人名
    聽我已世的姐姐"魯哩谷"和"拉蕊"他們說

    81.
    0:03:57.060,0:03:59.792
    tia kaka anga i Tjuku a tjadruigi
    tia      kaka=anga               i  Tjuku  a             Tjadruigi
    主格  兄弟姊妹=完成貌 I  人名   連繫詞    家族名
    還有我的嫂嫂tjuku

    82.
    0:04:00.660,0:04:02.440
    lja nu maljavaljavale aza tiamatju
    lja                nu     ma-ljava-ljaval aza         tiamatju
    言談標記  如果 主焦-重疊-討論        主格.那  他們.主格
    因為每當他們在閒聊時

    83.
    0:04:02.880,0:04:04.200
    nakisacalinga
    na-ki-sa-calinga
    完成貌-KI-去-耳朵
    我都會在旁邊豎耳傾聽

    84.
    0:04:04.480,0:04:05.880
    lja aicu a 'u calinga
    lja                aicu    a             'u=calinga
    言談標記 這個   連繫詞  我.屬格=耳朵
    因為我這耳朵

    85.
    0:04:06.140,0:04:09.040
    kemasi cuway angata ika a 'en a madrawdraw ta anema
    k<em>asi cuay  angata ika=a'en             a              ma-draudraw   ta      anema
    <主焦>從  久      確實   否定=我.主格   連繫詞   主焦-忘記          斜格  什麼
    從以前記性就很好不曾輕易忘記甚麼

    86.
    0:04:09.580,0:04:12.040
    ljakua meramaljeng anga  a'en
    ljakua me-ramaljeng=anga  a'en
    但是    主焦-老人=完成貌     我.主格

    但因為我變老了

    87.
    0:04:12.400,0:04:15.480
    izua tu 'u pinaqenetj izua tu ika 'u pinaqenetj tucu anga
    izua  tu                 'u=p<in>a-qenetj                                 izua   tu                ika    'u=p<in>a-qenetj
    存在 補語連詞  我.屬格=<受焦.完成貌>使役-記得 存在 補語連詞  否定 我.屬格=<完成貌>使役-記得
    tucu=anga
    現在=完成貌
    有時候經常會忘東忘西

    88.
    0:04:15.820,0:04:18.080
    au gemalal dri mama aza izua
    au               g<em>alal      dri          mama  aza          izua
    言談標記  <主焦>鬧鬼   語助詞   媽媽    主格.那  存在
    那裏會鬧鬼?

    89.
    0:04:18.420,0:04:19.380
    ilu keljang lja
    ilu[m]          keljang   lja
    怎麼會  知道      言談標記
    我怎麼知道

    90.
    0:04:19.640,0:04:21.520
    ini a su kinilandandan izua
    ini     a              su=k<in>i-landand[n][o]-an               izua
    否定 填補詞  你.屬格=<完成貌>KI-聽-AN   存在
    我意思是說:你有聽說過?

    91.
    0:04:21.860,0:04:22.700
    a gemalalj
    a             g<em>alalj
    連繫詞  <主焦>鬧鬼
    鬧鬼?

    92.
    0:04:24.340,0:04:28.220
    ilu ka gemalalj na lusiaqan aza ti sa Ljaljumegan aya
    ilu          ka   g<em>alalj   na-lu-siaq-an                         aza           ti     sa-Ljaljumegan aya
    怎麼會  KA <主焦>鬧鬼  完成貌-習慣貌-害羞-AN  主格.那  主格  已故-人名          說
    怎麼會鬧鬼.聽說"拉魯麼砍"本身是很內向溫婉

    93.
    0:04:28.540,0:04:29.060
    ui
    ui
    言談標記
    是喔!

    94.
    0:04:29.620,0:04:31.600
    nalusiyaqan saka navaleljevelj
    na-lu-siaq-an          saka   na-valeljevelj
    完成貌-習慣貌-害羞-AN  而且  完成貌-漂亮
    溫柔而且非常漂亮

    95.
    0:04:31.840,0:04:34.020
    qetji aza tia ina i Djasa a ngeruq
    qetji   aza         tia      ina     i Djasa   a             ngeruq
    你看  主格.那  主格  媽媽 I  人名   連繫詞   手足
    你看那些她的親戚們

    96.
    0:04:34.380,0:04:35.740
    ngeruq
    ngeruq
    手足
    親戚?

    97.
    0:04:37.160,0:04:40.080
    tima cinuljev ni ta  vuvuvuvu ni
    tima  cinuljev  ni               ta        vuvu-vuvu   ni
    誰      遺傳       言談標記  斜格  重疊-祖孫    助詞
    她的親戚不曉得誰比較像她?

    98.
    0:04:40.660,0:04:42.340
    kitima tja lja vulungan lja
    ki-tima tja-lja-vulung-an     lja
    KI-誰     比較-LJA-老人-AN  言談標記
    我忘了她的手足中誰最大

    99.
    0:04:44.120,0:04:47.560
    pai aza na ti Sakinu avan anga tja aya
    pai              aza          na          ti       Sakinu avan=anga      tja=aya
    言談標記  主格.那 屬格      主格 人名     就是=完成貌  我們.包含.屬格=說
    那個叫"沙基奴"就是她的親戚

    100.
    0:04:48.300,0:04:50.080
    malekaka tiamadju
    malekaka tiamadju
    姊妹           他們.主格

    拉魯麼砍跟砂島碗是姊妹?

    101.
    0:04:50.500,0:04:51.000
    malekaka
    malekaka
    姊妹
    姊妹

    102.
    0:04:51.720,0:04:54.200
    uh ti sa Tauwan a tjavulung a kaka avavayan
    uh                 ti         sa-Tauwan  a            tja-vulung   a              kaka           vavayan
    言談標記   主格   已故-人名  連繫詞 比較-老人   連繫詞   兄弟姊妹  女生
    喔 !而"砂島碗"是姊姊

    103.
    0:04:54.440,0:04:54.940
    tima
    tima
    誰
    誰?

    104.
    0:04:55.120,0:04:55.620
    aza
    aza
    主格.那

    那個

    105.
    0:04:55.900,0:04:57.140
    qaliqali nana
    qali-qali     nana
    重疊-外人  XX

    她們是不同家族

    106.
    0:04:57.820,0:05:00.040
    aya tua uli kisan kanguhu aya
    aya tua     uli            ki-san    kanguhu     aya
    說   斜格   非實現   KI-做     護士.日語   說
    "砂島碗"在構想要做護士

    107.
    0:05:00.240,0:05:02.100
    au aza tima za tiima azua a naki
    au                 aza         tima za   tiima   azua        a             na-ki
    言談標記   主格.那  誰     那   誰       主格.那  連繫詞    XX
    然後那位那位自殺的人

    108.
    0:05:02.280,0:05:03.020
    ti Ljaljumegan
    ti         Ljaljumegan
    主格  人名
    拉魯麼砍?

    109.
    0:05:03.240,0:05:05.040
    aza na macay ti Ljaljumegan
    aza          na-macay    ti        Ljaljumegan
    主格.那  完成貌-死  主格  人名
    自殺的叫拉魯麼砍?

    110.
    0:05:05.120,0:05:05.620
    ui
    ui
    言談標記
    是

    111.
    0:05:05.740,0:05:06.640
    ika kaka ni aya
    ika      kaka           ni       aya
    否定   兄弟姊妹  屬格  說
    不是"砂島碗"的姐姐喔

    112.
    0:05:06.780,0:05:07.580
    kinaka nu kanki
    ki-naka   nu       kanki
    KI-否定  如果   關係.日語
    沒有關係

    113.
    0:05:08.480,0:05:09.960
    nia nia ima  azua
    nia    nia    ima  azua
    屬格 屬格  誰   主格.那

    那她是屬於哪個家族?

    114.
    0:05:10.520,0:05:13.000
    aza nia qipu a ubasan
    aza          nia=Qipu                  a              ubasan
    主格.那   我們.屬格=人名   連繫詞    歐巴桑.日語

    就施家的阿姨啊

    115.
    0:05:14.480,0:05:16.120
    ui aza ti ina anga i Djasa
    ui                 aza            ti         ina=anga         i Djasa
    言談標記   主格.那   主格   母親=完成貌  I  人名
    是 那個ina"價沙"

    116.
    0:05:16.600,0:05:18.240
    tiamadju a malekaka
    tiamadju   a             male-kaka
    他們.主格 連繫詞  MALE[p]-兄弟姊妹

    是她們的姊妹

    117.
    0:05:18.420,0:05:19.640
    aza ti Sakinu ti
    aza            ti        Sakinu  ti
    主格.那    主格   人名    XX

    那個"沙基奴"

    118.
    0:05:20.680,0:05:22.380
    ti Sakinu a zua a  aya
    ti          Sakinu  azua        a              aya
    主格   人名     主格.那  連繫詞   說
    沙基奴是

    119.
    0:05:22.700,0:05:24.480
    na puvaljaw tjai Masayu
    na-pu-valjaw        tjai     Masayu
    完成貌-有-配偶   斜格  人名

    就娶朱家小姐叫"嗎沙優"的

    120.
    0:05:26.680,0:05:29.300
    tima anga aza 朱..朱 朱家的
    tima=anga   aza         朱 朱 朱家的
    誰=完成貌  主格.那  朱 朱 朱家的
    朱家的誰了

    121.
    0:05:30.000,0:05:31.360
    uh tiamadju a taqumaqan
    uh               tiamadju  a               taqumaqan
    言談標記  他.斜格     連繫詞  一家人
    喔 他們那一家的

    122.
    0:05:31.580,0:05:32.780
    'u pinaka melekaka aza
    'u=p<in>aka                   mele-kaka                       aza
    我.屬格=<受焦>經由  MALE-兄弟姊妹           主格.那
    我以為"拉魯麼砍"跟"沙島碗"是姊妹

    123.
    0:05:33.000,0:05:34.660
    tia Sauren avav anga aza tia Pinsiang
    tia    Sauren avan=anga         aza             tia       Pinsiang
    主格 人名     就是=完成貌   主格.那     主格   家屋名
    "拉魯麼砍"的親戚還有田家家族

    124.
    0:05:36.860,0:05:37.440
    'u pinaka
    'u=p<in>aka
    我.屬格=<受焦>覺得

    我以為

    125.
    0:05:37.540,0:05:39.974
    ti Sadengiyap a kama ni aya
    ti         Sadengiyap   a               kama  ni        aya
    主格  人名                連繫詞    父親   屬格   說
    "沙的哩牙蔔"是爸爸

    126.
    0:05:39.974,0:05:41.974
    ni Sauren kati Sakinu
    ni      Sauren  kati  Sakinu
    屬格 人名       跟    人名
    "Sauren 跟Sakinu的爸爸

    127.
    0:05:42.400,0:05:44.320
    G: 'u pinaka melekaka tiamadju
    G: 'u=p<in>aka                 mele-kaka           tiamadju
    G: 我.屬格=<受焦>覺得  互相-兄弟姊妹  他們.主格

    我以為她們是姊妹

    128.
    0:05:44.740,0:05:46.560
    au ti Ljaljumegan
    au               ti        Ljaljumegan
    言談標記  主格  人名
    然後拉魯麼砍

    129.
    0:05:47.740,0:05:49.540
    ti Ljaljumegan ti Sadjasa
    ti        Ljaljumegan   ti        Sadjasa
    主格  人名                主格  人名
    "拉魯麼砍" "沙家沙"

    130.
    0:05:50.860,0:05:51.480
    matu
    matu
    好像
    好像

    131.
    0:05:52.573,0:05:53.128
    tjalja
    tja-lja
    比較-LJA
    最

    132.
    0:05:53.350,0:05:54.829
    tjalja sipu
    tja-lja          sipu
    比較-LJA    XX

    133.
    0:05:55.460,0:05:58.600
    tjaljavulungan a ni Sauren a kama ti Sadengiyap
    tja-lja-vulung-an  a             ni      Sauren  a            kama   ti        Sadengiyap
    比較-LJA-老-AN  連繫詞  屬格  人名     連繫詞  父親    主格   人名
    他們是三兄妹.最大是田家的爸爸

    134.
    0:05:59.380,0:06:01.420
    tja silukai-an anan numaya aza kuvekuv
    tja=si-lu-kai-an=anan                              numaya    aza       kuvekuv
    我們.包含.屬格=參焦-LU-話-AN=還    不然        主格.那   監獄
    不然我們先回到那個監獄的故事

    135.
    0:06:01.620,0:06:03.380
    au kamacay
    au                 ka-[q]macay
    言談標記    當-死
    後來她死了

    136.
    0:06:04.960,0:06:07.720
    G: akumay kemeljang tu na kipacay aya anga
    G: akumay k<em>eljang  tu                na-ki-pacay          aya=anga
    G: 為何       <主焦>知道    補語連詞  完成貌-自己-死   說=完成貌
    G: 為什麼日本人知道他死掉了?

    137.
    0:06:08.520,0:06:09.900
    G: aza ti Ljaljumegan
    G: aza           ti        Ljaljumegan
    G: 主格.那  主格   人名
    G: 那位拉魯麼砍?

    138.
    0:06:10.320,0:06:12.400
    saka suqeljevan nua kisace
    sa-ka        su-qeljev-an          nua   kisace
    然後-KA  SU-開.關門-AN     屬格  警察

    警察會開門查看啊!

    139.
    0:06:12.660,0:06:13.740
    masa na uli
    masa na-uli
    也許  完成貌-非實現
    也許可能

    140.
    0:06:14.520,0:06:17.020
    pinasasasaw ki na uli ka pinakakanan
    p<in>a-sa-sasaw                   ki-na            uli            ka-p<in>a-ka-kan-an
    <完成貌>使役-重疊-外面   KI-完成貌  非實現   KA-<受焦>使役-重疊-吃-AN

    要放他出去或者要拿飯給他吃

    141.
    0:06:17.140,0:06:19.900
    lja nu i huin itjen pakanan nitjen dalu
    lja     nu       i      huin=itjen                               pa-kan-an      nitjen                    dalu
    因為 如果  在  法院.日語=我們.包含.主格  使役-吃-AN   我們.包含.屬格  DALU
    因為我們被關在監獄會給我們吃飯吧!

    142.
    0:06:21.240,0:06:22.960
    au neka anga aya
    au               neka=anga          aya
    言談標記  否定=完成貌     說
    結果沒有氣了這樣

    143.
    0:06:22.960,0:06:23.888
    uh
    uh
    言談標記
    喔

    144.
    0:06:24.640,0:06:26.320
    au pida qadaw a qineljevan
    au                pida   qadaw  a            q<in>eljev-an
    言談標記   多少   日子    連繫詞  <受焦>關-AN
    然後關幾天?

    145.
    0:06:26.660,0:06:28.840
    ilu 'u keljang ljakua na maitazua
    ilu          'u=keljang        ljakua  na-maitazua
    怎麼會  我.屬格=知道  但是   完成貌-這樣
    我不清楚.但事情就這樣

    146.
    0:06:29.380,0:06:30.780
    a na tjaucikel
    a             na-tjaucikel
    連繫詞  完成貌-告訴
    傳述的

    147.
    0:06:31.620,0:06:33.080
    naikaui i aya ma
    na-ika-ui               i aya   ma
    完成貌-不-肯定  I  說   言談標記

    過去就是不行

    148.
    0:06:33.340,0:06:34.440
    nai kaui  aya
    na-ika-ui               aya
    完成貌-不-肯定   說
    不准

    149.
    0:06:35.760,0:06:38.360
    Dripung tjanuitjen puvaljaw ta pailang tua
    Dripung  tjanuitjen            pu-valjaw   ta      pailang  tua
    日本        我們.包含.斜格  有-配偶      斜格  平地人  斜格

    日本人不准我們原住民嫁平地人

    150.
    0:06:38.360,0:06:38.860
    tua tjayamadju
    tua    tjayamadju
    斜格  他們.斜格
    或他們

    151.
    0:06:38.960,0:06:41.440
    na sa puvaljaw ta
    na-sa-pu-valjaw          ta
    屬格-然後-有-配偶   斜格
    可能想娶

    152.
    0:06:41.640,0:06:44.200
    aya dalu na tjengelay a Dripung ta aza tiamadju
    aya dalu    na-tjengelay   a             Dripung   ta      aza          tiamadju
    說   DALU  完成貌-喜歡  連繫詞  日本        斜格  主格.那   他們.主格

    153.
    0:06:44.560,0:06:45.960
    saka na valeljevelj aya
    saka  na-valeljevelj aya
    而且  完成貌-漂亮   說
    就是太漂亮了啦!

    154.
    0:06:46.560,0:06:47.500
    sa aya tjamadju
    sa      aya=tjaimadju
    想要 說=他們.主格
    想要給他

    155.
    0:06:47.500,0:06:48.480
    ui
    ui
    言談標記
    是

    156.
    0:06:48.480,0:06:52.580
    qetji aza na ti vuvu anga i Sakenge a kina ni Muljasan.
    qetji  aza          na      ti       vuvu=anga      i   Sakenge  a            kina    ni      Muljasan
    你看  主格.那 屬格  主格 奶奶=完成貌  I  人名         連繫詞  媽媽  屬格 人名
    你看那土坂有錢家族"Mliasan"的奶奶"Skenge

    157.
    0:06:52.700,0:06:54.700
    na puvaljaw ta ripun
    na-pu-valjaw       ta      dripung
    完成貌-有-配偶  斜格    日本
    有嫁給日本人

    158.
    0:06:55.300,0:06:56.440
    tia Muljasan ni
    tia   Muljasan ni
    XX  人名          言談標記

    目拉上(望族)

    159.
    0:06:56.600,0:06:59.201
    ljakua na anema na Dripung aza kama ni
    ljakua na=anema         na       Dripung  aza          kama  ni
    但是    完成貌=什麼   屬格   日本         主格.那  父親  屬格
    但是他爸爸好像是在當時的日本

    160.
    0:06:59.758,0:07:01.461
    kama ni Muljiasan kiaya
    kama   ni      Muljiasan ki-aya
    父親   屬格  人名          KI-說
    Muljasan當某個官差

    161.
    0:07:01.860,0:07:03.220
    na izua zua i
    na       i<zua>zua                i
    屬格  處所.那<重疊>      xx
    他們住在那裡..

    162.
    0:07:04.120,0:07:07.260
    qadjaw ki na uli kaizuanan a kisace tazua
    qadjaw ki-na-uli               kaizuanan   a                  kisace  tazua
    可能      KI-屬格-非實現  居住地       主格標記    警察      那時
    不知那時還有沒有日本警察

    163.
    0:07:07.640,0:07:09.880
    lja kinungida tazua ma
    lja      kinungida tazua  ma
    因為 何時           那時     言談標記
    因為不知什麼時候的那個嘛!.....

    164.
    0:07:10.400,0:07:12.260
    ki tjaisangas[r] a ziday  ki anemam
    ki-tja-isangas   a             ziday  ki-anema
    KI-比較-先前  連繫詞  時代    KI-什麼
    不知是民前或者是什麼

    165.
    0:07:13.180,0:07:15.620
    "民前" a tjai sangas ta Dripung dalu
    民前   a             tjai     sangas  ta       Dripung dalu
    民前  連繫詞  斜格   之前    斜格   日本       DALU
    民前比日本還前面?

    166.
    0:07:16.000,0:07:16.720
    ljki[s] Dripung
    ljki    Dripung
    還是 日本
    還是日本

    167.
    0:07:18.660,0:07:21.040
    日本喔 a 昭和...昭和吧
    日本喔   a 昭和 昭和吧
    日本喔   連繫詞  昭和 昭和吧
    日本喔  昭和 昭和吧

    168.
    0:07:22.360,0:07:23.380
    昭和
    昭和
    昭和
    昭和

    169.
    0:07:23.560,0:07:26.180
    昭和 a tjaisangas ta 日本
    昭和   a             tja-isangas[t]  ta      日本
    昭和 連繫詞   比較-之前   斜格 日本
    比日本昭和之前

    170.
    0:07:29.380,0:07:30.660
    ljavililj anga 昭和 qetji azua sinan
    lja-vililj=anga 昭和             qetji  azua      s<in>an
    比較-後面=完成貌  昭和  看     主格.那 <受焦>做
    昭和很後面了!你看那座的

    171.
    0:07:30.940,0:07:32.280
    qetji aza sinan tjakuran
    qetji  aza          s<in>an      tjakuran
    看     主格.那   <主焦>做  吊橋
    你看他們做的吊橋

    172.
    0:07:32.440,0:07:34.200
    哪民國14..13年
    哪民國14 13年
    哪民國14 13年
    哪民國14..13年

    173.
    0:07:34.960,0:07:38.060
    avan ka uli maqaqeci anga tjen vaik anga
    avan ka-uli           ma-qa-qeci=anga=tjen                                vaik=anga
    就是 當-非實現   主焦-重疊-殺=完成貌=我們.包含.這個   去=完成貌
    是我們快要戰爭時日本人才離開

    174.
    0:07:39.220,0:07:40.860
    navan[u] tazua
    navan tazua
    就是   那時
    就那時候

    175.
    0:07:40.860,0:07:41.505
    uh
    uh
    言談標記
    喔

    176.
    0:07:42.080,0:07:45.360
    ljakua  aza ti ubasan Uwan na ika mahuing
    ljakua  aza           ti       ubasan Uwan  na            ika   ma-huing
    但是    主格.那   主格  歐巴桑  人名  完成貌  否定 主焦-監獄
    但砂島婉並沒因此入獄

    177.
    0:07:45.920,0:07:48.440
    pai na kiniljingaljinga na  Dripung
    pai                na-k<in>i-ljinga-ljinga             na     Dripung
    言談標記    完成貌-<受焦>KI-重疊-罵    屬格  日本
    那時被日本罵得很慘

    178.
    0:07:48.900,0:07:51.340
    kamakadju ta aza kama ni Asaku
    ka-ma-kadju     ta      aza           kama  ni       Asaku
    KA-主焦-貪戀  斜格 主格.那  父親    屬格  人名
    她在喜歡包頭目的爸爸

    179.
    0:07:51.920,0:07:52.460
    Dripung
    Dripung
    日本
    日本

    180.
    0:07:52.794,0:07:53.400
    ui
    ui
    言談標記
    是

    181.
    0:07:53.400,0:07:55.220
    a ui  Dripung aza kama ni Asaku
    a             ui                Dripung   aza         kama  ni     Asaku
    填補詞 言談標記  日本        主格.那  父親    屬格 人名

    啊對! 包頭目"阿莎古"的爸爸

    182.
    0:07:56.080,0:07:58.760
    au sivaivaik anga  aza kama sema
    au                si-vai-vaik=anga             aza         kama  s<em>a
    言談標記  參焦-重疊-去=完成貌  主格.那 父親   <主焦>去
    他父親就丟下她們

    183.
    0:07:58.760,0:08:00.616
    aya kama aya
    aya ka-ma-aya
    說   KA-主焦-說
    跟中日

    184.
    0:08:01.140,0:08:02.494
    kapuamin namaqaqeci
    ka-[v]pu-amin  na-ma-qa-qeci
    KA-有-結束  完成貌-主焦-重疊-殺
    當戰爭結束

    185.
    0:08:02.494,0:08:03.223
    ui
    ui
    言談標記
    是

    186.
    0:08:03.520,0:08:07.320
    au tima au ika kinacu ti..ti ina i Asaku
    au               tima  au                ika    k<in>acu  ti        ti        ina      i  Asaku
    言談標記  誰     言談標記   否定 <受焦>帶 XX    主格   母親    I  人名
    然後那位..然後沒將"阿莎古"帶回日本?

    187.
    0:08:07.640,0:08:08.440
    ita ni
    ita      ni
    一個   助詞

    一個后

    188.
    0:08:08.520,0:08:09.020
    na ita
    na      ita
    屬格  一個
    嗯 只有一個

    189.
    0:08:10.060,0:08:13.200
    au napatigamigamiyanan aya yu
    au               na-pa-ti<gami>gami=anan  aya  yu
    言談標記  完成貌-使役-<重疊>信=還  說   助詞
    聽說那日本人曾來信多次

    190.
    0:08:13.300,0:08:15.515
    aza na kama ni Asaku a Dripung
    aza         na      kama   ni     Asaku  a           Dripung
    主格.那 屬格  父親   屬格 人名   連繫詞  日本
    那"阿莎古"的日本爸

    191.
    0:08:15.680,0:08:17.040
    ti ubasan Uwan
    ti       ubasan  Uwan
    主格 歐巴桑  人名
    及" 砂島婉"

    192.
    0:08:17.540,0:08:19.900
    tazua na makadjukadju anga tjai Sadjanau
    tazua na-ma-kadju-kadju=anga                tjai    Sadjanau
    那時  完成貌-主焦-重疊-戀愛=完成貌   斜格 人名
    那時候"砂島婉"正在跟"砂家腦"戀愛

    193.
    0:08:19.960,0:08:21.740
    kama ni Dasan
    kama ni      Dasan
    父親  斜格  人名
    包賜晶的爸爸

    194.
    0:08:22.200,0:08:24.120
    aza ti ubasan Uwan aya au
    aza         ti        ubasan Uwan aya au
    主格.那 主格  歐巴桑  人名   說  言談標記
    那"砂島婉"這樣然後

    195.
    0:08:24.460,0:08:26.720
    naika sinitjumatjumalj a tigami aya
    na=ika             s<in>i-tjuma-tjumalj             a             tigami aya
    完成貌=否定 <完成貌>參焦-重疊-告訴   連繫詞  信         說

    關於日本人寫信這件事情.

    196.
    0:08:26.720,0:08:29.960
    taza ti aya ti Sadjanau
    taza         ti        aya  ti       Sadjanau
    斜格.那  主格  說   主格 人名
    她瞞著王天量她先生

    197.
    0:08:30.480,0:08:32.180
    kama ni aya Dasan
    kama ni      aya Dasan
    父親  屬格 說   人名
    就"達上"的爸爸

    198.
    0:08:32.540,0:08:35.420
    ika vaiken a kimen, qadjaw ka izuanan
    ika    vaik-en   a            kimen[w]  qadjaw  ka   izua=anan
    否定 去-受焦 連繫詞   找         不知道  KA  存在句=還
    怎麼不去日本找， 也許還找的到

    199.
    0:08:35.600,0:08:37.860
    saka uli navinainaik a kemin a ma Dripung
    saka uli           na-v<in>ai-vaik     a kemin[x][y]  a            ma-Dripung
    而且 非實現 <完成貌>重疊-去 連繫詞   連繫詞  主焦-國名

    而且本來有說要去日本找

    200.
    0:08:38.020,0:08:40.280
    ljakua neka anga matu na aya aya
    ljakua neka=anga       matu na-aya         aya
    但是     否定=完成貌 好像 完成貌-說   說
    但聽說過世了這樣

    201.
    0:08:40.440,0:08:41.380
    a pasemalaw
    a              pasemalaw
    連繫詞   告訴
    告知的

    202.
    0:08:41.440,0:08:43.480
    uli kaizua malekakakaka
    uli           ka-izua         male-kaka-kaka
    非實現  KA-存在句   互相-重疊-兄弟姊妹
    也許日本還有他的親戚們

    203.
    0:08:44.640,0:08:45.640
    tjala izuwa lja
    tjala izua   lja
    應該 存在 言談標記
    可能有吧!

    204.
    0:08:51.580,0:08:52.600
    inu ca
    inu     ca
    那裡  這
    在那兒?

    205.
    0:08:53.820,0:08:54.600
    uduli
    uduli
    跳舞.日語
    跳舞

    206.
    0:08:55.400,0:08:57.160
    mama inu aza vuvuwa na
    mama inu    aza         vuvuwa  na
    媽媽    哪裡 主格.那  山上      屬格
    媽媽那山上在哪裡

    207.
    0:08:57.380,0:08:59.840
    na kase Tjuabalan a aya
    na     ka-se-Tjuabal-an     a           aya
    屬格 KA-屬-地名-AN      連繫詞  說
    真正土板在地的舊部落

    208.
    0:09:00.000,0:09:03.500
    azua pasu lizuk aza itua namatucu a gadu
    azua       pa-su-lizuk       aza          itua namaitucu      a              gadu
    主格.那  使役-SU-平原 主格.那  在    這樣                 連繫詞   山
    就那座比較平原的山脈

    209.
    0:09:03.500,0:09:04.000
    ainu
    ainu
    哪裡
    哪裡

    210.
    0:09:04.100,0:09:07.120
    azua zuazua anan a gadu namaitucu
    azua        zua-zua=anan       a              gadu   namaitucu
    主格.那   重疊-主格.那=還 連繫詞   山       這樣
    就後面那座這樣的山

    211.
    0:09:07.500,0:09:08.000
    avan azua
    avan azua
    就是 主格.那
    就那個...

    212.
    0:09:09.940,0:09:12.160
    qadjaw kipaljecaza su sasinki
    qadjaw  ki-pa-lje-caza     su           sasinki
    不知道   KI-使役-LJE-遠 你.屬格  相機.日語
    你的照相機可以照那麼遠?

    213.
    0:09:12.340,0:09:13.420
    dikilu ljakua keri
    dikilu          ljakua   keri
    可以.日語   但是    小
    可以但影目很小

    214.
    0:09:13.420,0:09:15.500
    aza aicu i caceveljan i pavavaw
    aza         aicu   i       ca-cevelj-an    i pa-vavaw
    主格.那  這   處所  重疊-埋-AN    I  使役-上面
    在這個墳墓的上面喔

    215.
    0:09:15.780,0:09:18.440
    ui aicu a sevesevec a paljezua i zaya
    ui                aicu a              seve-sevec a              pa-lje-zua                 i          zaya
    言談標記  這    連繫詞  重疊-直       連繫詞  使役-LJE-主格.那   處所  上方
    是,這直直的往上面

    216.
    0:09:18.640,0:09:20.440
    taza namaitucu a gadu lja
    taza         namaitucu  a              gadu  lja
    斜格.那  這樣             連繫詞   山       言談標記
    像這樣的山脈啦

    217.
    0:09:20.440,0:09:21.374
    tucu
    tucu
    這樣
    這樣

    218.
    0:09:21.374,0:09:22.224
    uh
    uh
    言談標記
    喔

    219.
    0:09:23.892,0:09:25.829
    aicu a quma nia Iki
    aicu  a            quma nia=Iki
    這    連繫詞  山上    我們.屬格=人名
    這Iki的山上

    220.
    0:09:26.220,0:09:27.960
    tinalem ta zulin
    t<in>alem     ta      zulin
    <受焦[z]>種植  斜格 造林

    有種造林

    [a]所以的 "aicu" 標 “主格.這”
    [b]=anan
    [c]言談標記？還是先大寫？
    [d]加焦點
    [e]來.祈使
    [f]切
    [g]當.過去式
    [h]-
    [i]加完成貌
    [j]加主焦
    [k]跟第70的kadju不一致
    [l]ripun 還是dripung?
    [m]也有 ku/'u 在裡面嗎？ ilu 'u keljang?感覺是有“我”的意思？
    [n]字根後面也有-a
    你們的方言是n 還是ng
    [o]也有重疊，第二行的e可以還原：
    k<in>i-la<ngeda>ngeda-an
    [p]標“互相”如何？
    [q]ka
    當.過去式
    第一二三行都單獨
    [r]如果第二三行用 - （ki當前綴），第一行也應該寫在一起（kitjaisangas)才一致
    [s]少寫了母語，ljaki? ljiki?
    [t]i-sangas
    [u]有navan 嗎？不是mavan? 還是na-avan?
    [v]ka 在第一二三行單獨
    當.過去式
    [w]kim-en
    [x]k<em>im
    [y]第三行沒有標到
    [z]加完成貌
    """
  Then 清掉註解後是
    """
    0:00:19.060,0:00:19.560
    na
    na
    完成貌

    就

    8.
    0:00:21.080,0:00:23.660
    sikuvekuv ta napasaliw a  caucau
    si-kuvekuv          ta       na-pasaliw      a            caucau
    參焦-監獄  斜格  完成貌-過分        連繫詞     人

    聽說是關犯人的地方

    9.
    0:00:24.060,0:00:24.720
    izua
    izua
    存在

    那有

    10.
    0:00:25.760,0:00:27.820
    izua ita milimilingan
    izua  ita  mili-milingan
    存在 一 重疊-故事
    有一段故事比較

    11.
    0:00:30.160,0:00:31.060
    tjamapaula
    tja-ma-paula
    比較-主焦-可憐
    哀怨的

    12.
    0:00:32.660,0:00:33.480
    ulja
    ulja
    因為
    因為

    13.
    0:00:35.440,0:00:35.940
    tiamadju
    tiamadju
    他們.主格
    他們

    14.
    0:00:36.900,0:00:39.980
    kasicuayan izua aza madrusa maqacuvucuvung a vavayan kinuvekuv i taladj
    kasicuayan izua  aza         ma-drusa       ma-qa<cuvu>cuvung  a          vavayan k<in>uvekuv
    以前            存在 主格.那  主焦-二            主焦-<重疊>足夠      連繫詞  女生      <完成貌>監獄
    i    taladj
    I   裡面

    曾經關著兩個年輕的婦女

    15.
    0:00:39.980,0:00:42.480
    saka navaleljevel aravac
    saka  na-valeljevel aravac
    然後 完成貌-漂亮  非常
    而且長的都非常漂亮

    16.
    0:00:44.740,0:00:46.640
    akumaya kuvekuven
    akumaya kuvekuv-en
    為何          監獄-受焦
    之所以為什麼被關

    17.
    0:00:47.320,0:00:48.780
    ika a'en na sepuwalan
    ika=a'en            na-se-puwalan
    否定=我.主格  完成貌-屬-清楚
    我也不太清楚

    18.
    0:00:49.220,0:00:51.240
    ljakua aza     hasisiu tucu.
    ljakua aza        hasisiu            tucu
    但是  主格.那 派出所.日語  現在
    不過我們派出所

    19.
    0:00:51.400,0:00:53.540
    mavan sinanguaq aicu a umaumaq
    mavan si-na-nguaq aicu    a            uma-umaq
    就是     參焦-NA-好  這個  連繫詞  重疊-家
    仍然把它保留的很完整

    20.
    0:00:55.260,0:00:58.320
    avansika neka kidadut sa kemapalak tjaimadju
    avansika neka ki-dadut  sa     k<em>a-palak    tjaimadju
    所以        否定   自己-近 然後  <主焦>KA-壞掉 他們.斜格
    所以沒人敢去觸碰它破壞它

    21.
    0:00:59.780,0:01:01.120
    azua niamen na i qinaljan
    azua      niamen         a              i         qinaljan
    主格.那 我們.屬格  連繫詞  處所   部落
    那也是我們族人

    22.
    0:01:02.140,0:01:02.820
    ita
    ita
    一
    一個

    23.
    0:01:03.220,0:01:04.460
    valeljevel a milimilingan
    valeljevelj a           mili-milingan
    美麗          連繫詞 重疊-故事
    很美麗的故事

    24.
    0:01:06.000,0:01:07.480
    tja pakata kinatjengelayan a milimilingan
    tja      paka-ta           k<in>a-tjengelay-an                a           mili-milingan
    比較  經由-斜格     <完成貌>KA-喜歡-AN        連繫詞   重疊-故事
    比較愛情故事

    25.
    0:01:10.360,0:01:11.540
    aicu i Tupan
    aicu    i         Tupan
    這個  處所  地名
    這土板村

    26.
    0:01:12.940,0:01:14.060
    Tupan a qinaljan
    Tupan   a            qinaljan
    地名   連繫詞   部落
    土板村

    27.
    0:01:20.760,0:01:21.760
    idu pacuni
    idu pacun-i
    來   看-祈使

    來看看

    28.
    0:01:24.020,0:01:24.940
    patjavat-i
    patjavat-i
    移動-祈使
    移一下

    29.
    0:01:28.340,0:01:29.400
    djemaljun anga
    dj<em>aljun=anga
    <主焦>到達=完成貌

    到了

    30.
    0:01:30.120,0:01:30.760
    aicu
    aicu
    這是
    這是

    31.
    0:01:31.400,0:01:33.360
    aicu i tjaiteku a qinaljan
    aicu   i         tja-i-teku                a        qinaljan
    這是 處所  比較-處所-下面   主格  部落
    這是下面的部落

    32.
    0:01:34.480,0:01:36.120
    tjaiteku a qinaljan
    tja-i-teku              a       qinaljan
    比較-處所-下面 主格 部落
    下面的部落

    33.
    0:01:40.320,0:01:42.420
    aicu a su pacucunan sedjelj
    aicu   a        su=pa<cu>cun-an          sedjelj
    這是 主格  你.屬格=<重疊>看-AN   都是
    你看到的都是

    34.
    0:01:44.160,0:01:45.640
    cuni ca gadugaduan
    cun-i       ca     gadu-gadu-an
    看-祈使  這     重疊-山-AN
    看這個山脈

    35.
    0:01:46.660,0:01:47.620
    gadugaduan
    gadu-gadu-an
    重疊-山-AN
    山脈

    36.
    0:01:49.340,0:01:51.140
    aicu nia hisisiu
    aicu     nia              hisisiu
    這個  我們.屬格  派出所.日語
    這是我們的派出所

    37.
    0:01:54.060,0:01:54.760
    wi
    wi
    言談標記
    喴

    38.
    0:01:55.960,0:01:57.560
    sasingu sasingu
    sasing-u    sasing-u
    相片-祈使 相片-祈使
    ㄚ..你先錄你先錄

    39.
    0:01:59.240,0:02:00.760
    ai anga cuivan
    ai=anga                      Cuivan
    言談標記=完成貌   人名
    唉呀啊...翠芳

    40.
    0:02:01.840,0:02:06.480
    naizua za a ramaljemaljen a na ti sa Ljaljumegan
    na-izua          za     a           ra<malje>maljeng   a              na   ti       sa-Ljaljumegan
    完成貌-存在 那   主格    <重疊>前輩                連繫詞  XX  主格  已故-人名
    有一位老人叫"拉魯麼砍"

    41.
    0:02:06.860,0:02:09.280
    aza ti ubasan  Uwan anga
    aza          ti         ubasan  Uwan=anga
    主格.那  主格  歐巴桑.日語    人名=完成貌
    還有一位"砂島碗"

    42.
    0:02:09.560,0:02:12.300
    a natjaucikel na na ramaljemaljen
    a             na-tjaucikel    na  na     ra<malje>maljeng
    填補詞  完成貌-告訴  XX  屬格 <重疊>前輩

    以前老人家曾傳述的故事發生是這樣

    43.
    0:02:12.720,0:02:17.300
    ljakua na  uli namasan kumuing aza ti saUwan naika paqulid
    ljakua na   uli            na-masan      kumuing  aza         ti       sa-Uwan        na-ika            paqulid
    但是   NA  非實現   完成貌-成為  公務員   主格.那  主格  已故-人名   完成貌-否定  正確

    但是他知道他會成為公務員沒有往壞的方面想

    44.
    0:02:18.080,0:02:20.700
    ti Saljalumegan namasiyaq a varung
    ti        sa-Ljalumegan na-masiyaq    a             varung
    主格  已故-人名         完成貌-害羞 連繫詞   心

    而"拉魯麼砍"覺得被關很丟臉

    45.
    0:02:21.040,0:02:23.440
    naikaui a paricungen na Dripung
    na-ika-ui                    a             pa-ricung-en       na      Dripung
    完成貌-否定-同意  連繫詞  使役-立正-受焦  屬格 日本
    不願意跟日本人承認妥協

    46.
    0:02:24.000,0:02:25.940
    nakipacay ta aza kuvekuv
    na-ki-pacay           ta       aza         kuvekuv
    完成貌-自己-死  斜格   主格.那  監獄

    就在派出所旁那間小屋自殺

    47.
    0:02:26.440,0:02:27.760
    aza hasisiu au
    aza          hasisiu           au
    主格.那  派出所.日語 然後

    就那派出所 .....然後

    48.
    0:02:28.940,0:02:32.560
    qadjaw kinatjailauz kanai ka tjaizaya  za ti Saljaljumegan aya
    qadjaw  ki-na-tja-i-lauz                         ka-na-ika                tja-i-zaya                za    ti
    不知道   KI-完成貌-比較-處所-下面   KA-完成貌-否定 比較-處所-上面     那   主格
    sa-Ljaljumegan aya
    已故-人名          說
    不知當時"拉魯麼砍"是在左邊還是右邊

    49.
    0:02:32.880,0:02:35.460
    na nakireqel ta huluseki aya
    na  na-ki-reqel                ta      huluseki aya
    XX  完成貌-自己-上吊 斜格  絲巾        說
    他用絲巾上吊自殺

    50.
    0:02:36.240,0:02:37.920
    ka ayain na Dripung
    ka ayain  na      Dripung
    當  用         屬格  日本

    日本人發現他時

    51.
    0:02:38.580,0:02:39.680
    au timadju
    au               timadju
    言談標記  他.主格
    而她(拉魯麼砍)

    52.
    0:02:40.820,0:02:41.827
    navaleljevelj aravac
    na-valeljevelj    aravac
    完成貌-漂亮       非常
    長得非常漂亮.

    53.
    0:02:41.827,0:02:44.680
    natjuluvu  a natjengelay a maleka Dripung aya
    na-tjuluvu           a            na-tjengelay           a               maleka   Dripung aya
    完成貌-多         連繫詞        完成貌-喜歡         連繫詞     一些        日本        說
    當時有好多日本人追她

    54.
    0:02:44.780,0:02:45.460
    ljakua
    ljakua
    但是
    但是

    55.
    0:02:45.980,0:02:47.040
    ulja naika uli
    ulja   na=ika              uli
    因為 完成貌=否定  非實現
    因為不可能

    56.
    0:02:47.540,0:02:49.000
    e masan anema
    e              ma-san       anema
    填補詞  主焦-成為  什麼
    會做甚麼大事

    57.
    0:02:50.040,0:02:53.060
    venalung ta kipacay kireqel ta huluseki aya
    v<en>alung   ta     ki-pacay  ki-reqel      ta      huluseki aya
    <主焦>心     斜格  自己-死  自己-上吊 斜格  絲巾        說
    所以失望的用絲巾選擇輕生

    58.
    0:02:53.300,0:02:55.960
    au ka ayaing na kisace i hasisu
    au               ka     ayain   na     kisace    i        hasisiu
    言談標記 當時  用        屬格 警察    處所  派出所.日語
    後來警察去查看

    59.
    0:02:56.860,0:02:59.180
    naaya anga sema
    na-aya=anga              sema
    完成貌-說=完成貌   舌
    她舌頭已伸出來

    60.
    0:03:01.520,0:03:02.020
    嗯
    嗯
    嗯
    嗯

    61.
    0:03:02.160,0:03:04.000
    au aza ti ubasan Uwan
    au                aza         ti        ubasan             Uwan
    言談標記  主格.那  斜格  歐巴桑.日語  人名
    然後就把"砂島碗"

    62.
    0:03:04.300,0:03:05.580
    napinasasaw
    na-p<in>a-sasaw
    完成貌-<受焦>使役-外面
    有放出來

    63.
    0:03:07.340,0:03:10.220
    au ti basan Uwan ika kemeljang tu namacay a saladj aya yu
    au                ti      basan   Uwan ika   k<em>eljang    tu                na-macay        a             saladj  aya yu
    言談標記 主格 歐巴桑 人名  否定 <主焦>知道     補語連詞  完成貌-死亡  連繫詞  同伴     說   助詞
    但在被關時她完全不知"拉魯麼砍"已經自殺身亡喔

    64.
    0:03:11.060,0:03:12.860
    lja izua azua viden
    lja              izua   azua       viden
    言談標記 存在  主格.那  隔間
    因為那房子有用水泥隔間

    65.
    0:03:13.180,0:03:16.460
    viden viden aya tjen ta azua
    viden viden aya=tjen                      ta      azua
    間隔   間隔   說=我們.包含.主格 斜格  主格.那
    我們說那是中間隔

    66.
    0:03:17.040,0:03:20.080
    namaya ta aza tja umaq izuwa tjailauz a qaqelengan au
    namaya ta      aza          tja=umaq                   izua    tja-i-lauz               a            qa-qeleng-an    au
    就像      斜格  主格.那 我們.包含.屬格=家  存在  比較-處所-下面 連繫詞   重疊-躺-AN      言談標記
    如同我們的家.房間有分左右旁邊

    67.
    0:03:20.780,0:03:22.700
    naika kemeljang aya au
    na-ika              k<em>eljang      aya  au
    完成貌-否定  <主焦>知道         說  言談標記
    "砂島碗"不知發生了什麼事..然後

    68.
    0:03:23.800,0:03:24.640
    na
    na
    ==

    就

    69.
    0:03:25.320,0:03:26.480
    aza ti ubasan Uwan
    aza           ti      ubasan Uwan
    主格.那 主格  歐巴桑  人名
    那位"砂島碗"

    70.
    0:03:27.100,0:03:28.600
    natjalja lukadjuan lja tauta
    na-tja-lja-lu-kadju-an                lja                tauta
    完成貌-比較-LJA-LU-貪戀-AN 言談標記   也
    當時年輕貌美情感豐富

    71.
    0:03:29.000,0:03:30.180
    namakadju aya
    na-ma-kadju            aya
    完成貌-主焦-貪戀  說
    也很多情

    72.
    0:03:30.620,0:03:32.840
    tja lukaian pai ta pacengecen
    tja=lu-kai-an                            pai              ta      pa-cengeceng
    我們.包含.屬格=LU-話-AN   言談標記 斜格 使役-正確

    沒關係!細述要確實...真正的

    73.
    0:03:33.140,0:03:35.640
    ui namakadju saka aza na Dripung a ziday
    ui                 na-ma-kadju            saka  aza          na        Dripung  a              ziday
    言談標記  完成貌-主焦-如何  而且  主格.那  屬格    日本        連繫詞  時代.日語
    她很多情.而且在日本時代期間

    74.
    0:03:36.040,0:03:37.821
    naikaui ma aya itjen
    na-ika-ui               ma-aya=itjen
    屬格-否定-同意  主焦-說=我們.包含.主格
    他們嚴禁

    75.
    0:03:38.960,0:03:41.580
    a kisudju itjen kamaya tiamadju a ripun
    a              ki-sudju=itjen                          ka-maya=tiamatju      a              Dripung
    連繫詞  KI-朋友=我們.包含.主格       KA-不要= 他們.主格  連繫詞   日本

    嚴禁村裡頭談戀愛

    76.
    0:03:41.760,0:03:45.340
    naikaui a tja kisudjuan na aya aza ramaljemaljeng
    na-ika-ui                   a             tja=ki-sudju-an                               na-aya  aza         ra<malje>maljeng
    完成貌-否定-肯定 填補詞  我們.包含.屬格=得到-情人-AN  完成貌-說  主格.那 <重疊>前輩
    而且老人家說那些日本人也不允許村裡婦女喜歡他們

    77.
    0:03:46.160,0:03:47.760
    au namaitazua
    au               na-maitazua
    言談標記 完成貌-這樣
    就是這樣

    78.
    0:03:47.980,0:03:50.200
    saka na valeljevelj angta aza
    saka  na-valeljevelj angata  aza
    而且  完成貌-漂亮   確實   主格.那
    不過流傳那兩位小姐

    79.
    0:03:50.440,0:03:53.000
    ti Ljalumegan kati ubasan Uwan na aya
    ti       Ljalumegan kati ubasan  Uwan na      aya
    主格 人名              跟     歐巴桑   人名  屬格 說
    "拉魯麼砍"跟"砂島碗"真的很美

    80.
    0:03:53.500,0:03:56.160
    aza tia kaka i Luliku  kaka i Draruy
    aza         tia      kaka           i  Luliku  kaka           i Draruy
    主格.那 主格  兄弟姊妹  I  人名     兄弟姊妹  I  人名
    聽我已世的姐姐"魯哩谷"和"拉蕊"他們說

    81.
    0:03:57.060,0:03:59.792
    tia kaka anga i Tjuku a tjadruigi
    tia      kaka=anga               i  Tjuku  a             Tjadruigi
    主格  兄弟姊妹=完成貌 I  人名   連繫詞    家族名
    還有我的嫂嫂tjuku

    82.
    0:04:00.660,0:04:02.440
    lja nu maljavaljavale aza tiamatju
    lja                nu     ma-ljava-ljaval aza         tiamatju
    言談標記  如果 主焦-重疊-討論        主格.那  他們.主格
    因為每當他們在閒聊時

    83.
    0:04:02.880,0:04:04.200
    nakisacalinga
    na-ki-sa-calinga
    完成貌-KI-去-耳朵
    我都會在旁邊豎耳傾聽

    84.
    0:04:04.480,0:04:05.880
    lja aicu a 'u calinga
    lja                aicu    a             'u=calinga
    言談標記 這個   連繫詞  我.屬格=耳朵
    因為我這耳朵

    85.
    0:04:06.140,0:04:09.040
    kemasi cuway angata ika a 'en a madrawdraw ta anema
    k<em>asi cuay  angata ika=a'en             a              ma-draudraw   ta      anema
    <主焦>從  久      確實   否定=我.主格   連繫詞   主焦-忘記          斜格  什麼
    從以前記性就很好不曾輕易忘記甚麼

    86.
    0:04:09.580,0:04:12.040
    ljakua meramaljeng anga  a'en
    ljakua me-ramaljeng=anga  a'en
    但是    主焦-老人=完成貌     我.主格

    但因為我變老了

    87.
    0:04:12.400,0:04:15.480
    izua tu 'u pinaqenetj izua tu ika 'u pinaqenetj tucu anga
    izua  tu                 'u=p<in>a-qenetj                                 izua   tu                ika    'u=p<in>a-qenetj
    存在 補語連詞  我.屬格=<受焦.完成貌>使役-記得 存在 補語連詞  否定 我.屬格=<完成貌>使役-記得
    tucu=anga
    現在=完成貌
    有時候經常會忘東忘西

    88.
    0:04:15.820,0:04:18.080
    au gemalal dri mama aza izua
    au               g<em>alal      dri          mama  aza          izua
    言談標記  <主焦>鬧鬼   語助詞   媽媽    主格.那  存在
    那裏會鬧鬼?

    89.
    0:04:18.420,0:04:19.380
    ilu keljang lja
    ilu          keljang   lja
    怎麼會  知道      言談標記
    我怎麼知道

    90.
    0:04:19.640,0:04:21.520
    ini a su kinilandandan izua
    ini     a              su=k<in>i-landand-an               izua
    否定 填補詞  你.屬格=<完成貌>KI-聽-AN   存在
    我意思是說:你有聽說過?

    91.
    0:04:21.860,0:04:22.700
    a gemalalj
    a             g<em>alalj
    連繫詞  <主焦>鬧鬼
    鬧鬼?

    92.
    0:04:24.340,0:04:28.220
    ilu ka gemalalj na lusiaqan aza ti sa Ljaljumegan aya
    ilu          ka   g<em>alalj   na-lu-siaq-an                         aza           ti     sa-Ljaljumegan aya
    怎麼會  KA <主焦>鬧鬼  完成貌-習慣貌-害羞-AN  主格.那  主格  已故-人名          說
    怎麼會鬧鬼.聽說"拉魯麼砍"本身是很內向溫婉

    93.
    0:04:28.540,0:04:29.060
    ui
    ui
    言談標記
    是喔!

    94.
    0:04:29.620,0:04:31.600
    nalusiyaqan saka navaleljevelj
    na-lu-siaq-an          saka   na-valeljevelj
    完成貌-習慣貌-害羞-AN  而且  完成貌-漂亮
    溫柔而且非常漂亮

    95.
    0:04:31.840,0:04:34.020
    qetji aza tia ina i Djasa a ngeruq
    qetji   aza         tia      ina     i Djasa   a             ngeruq
    你看  主格.那  主格  媽媽 I  人名   連繫詞   手足
    你看那些她的親戚們

    96.
    0:04:34.380,0:04:35.740
    ngeruq
    ngeruq
    手足
    親戚?

    97.
    0:04:37.160,0:04:40.080
    tima cinuljev ni ta  vuvuvuvu ni
    tima  cinuljev  ni               ta        vuvu-vuvu   ni
    誰      遺傳       言談標記  斜格  重疊-祖孫    助詞
    她的親戚不曉得誰比較像她?

    98.
    0:04:40.660,0:04:42.340
    kitima tja lja vulungan lja
    ki-tima tja-lja-vulung-an     lja
    KI-誰     比較-LJA-老人-AN  言談標記
    我忘了她的手足中誰最大

    99.
    0:04:44.120,0:04:47.560
    pai aza na ti Sakinu avan anga tja aya
    pai              aza          na          ti       Sakinu avan=anga      tja=aya
    言談標記  主格.那 屬格      主格 人名     就是=完成貌  我們.包含.屬格=說
    那個叫"沙基奴"就是她的親戚

    100.
    0:04:48.300,0:04:50.080
    malekaka tiamadju
    malekaka tiamadju
    姊妹           他們.主格

    拉魯麼砍跟砂島碗是姊妹?

    101.
    0:04:50.500,0:04:51.000
    malekaka
    malekaka
    姊妹
    姊妹

    102.
    0:04:51.720,0:04:54.200
    uh ti sa Tauwan a tjavulung a kaka avavayan
    uh                 ti         sa-Tauwan  a            tja-vulung   a              kaka           vavayan
    言談標記   主格   已故-人名  連繫詞 比較-老人   連繫詞   兄弟姊妹  女生
    喔 !而"砂島碗"是姊姊

    103.
    0:04:54.440,0:04:54.940
    tima
    tima
    誰
    誰?

    104.
    0:04:55.120,0:04:55.620
    aza
    aza
    主格.那

    那個

    105.
    0:04:55.900,0:04:57.140
    qaliqali nana
    qali-qali     nana
    重疊-外人  XX

    她們是不同家族

    106.
    0:04:57.820,0:05:00.040
    aya tua uli kisan kanguhu aya
    aya tua     uli            ki-san    kanguhu     aya
    說   斜格   非實現   KI-做     護士.日語   說
    "砂島碗"在構想要做護士

    107.
    0:05:00.240,0:05:02.100
    au aza tima za tiima azua a naki
    au                 aza         tima za   tiima   azua        a             na-ki
    言談標記   主格.那  誰     那   誰       主格.那  連繫詞    XX
    然後那位那位自殺的人

    108.
    0:05:02.280,0:05:03.020
    ti Ljaljumegan
    ti         Ljaljumegan
    主格  人名
    拉魯麼砍?

    109.
    0:05:03.240,0:05:05.040
    aza na macay ti Ljaljumegan
    aza          na-macay    ti        Ljaljumegan
    主格.那  完成貌-死  主格  人名
    自殺的叫拉魯麼砍?

    110.
    0:05:05.120,0:05:05.620
    ui
    ui
    言談標記
    是

    111.
    0:05:05.740,0:05:06.640
    ika kaka ni aya
    ika      kaka           ni       aya
    否定   兄弟姊妹  屬格  說
    不是"砂島碗"的姐姐喔

    112.
    0:05:06.780,0:05:07.580
    kinaka nu kanki
    ki-naka   nu       kanki
    KI-否定  如果   關係.日語
    沒有關係

    113.
    0:05:08.480,0:05:09.960
    nia nia ima  azua
    nia    nia    ima  azua
    屬格 屬格  誰   主格.那

    那她是屬於哪個家族?

    114.
    0:05:10.520,0:05:13.000
    aza nia qipu a ubasan
    aza          nia=Qipu                  a              ubasan
    主格.那   我們.屬格=人名   連繫詞    歐巴桑.日語

    就施家的阿姨啊

    115.
    0:05:14.480,0:05:16.120
    ui aza ti ina anga i Djasa
    ui                 aza            ti         ina=anga         i Djasa
    言談標記   主格.那   主格   母親=完成貌  I  人名
    是 那個ina"價沙"

    116.
    0:05:16.600,0:05:18.240
    tiamadju a malekaka
    tiamadju   a             male-kaka
    他們.主格 連繫詞  MALE-兄弟姊妹

    是她們的姊妹

    117.
    0:05:18.420,0:05:19.640
    aza ti Sakinu ti
    aza            ti        Sakinu  ti
    主格.那    主格   人名    XX

    那個"沙基奴"

    118.
    0:05:20.680,0:05:22.380
    ti Sakinu a zua a  aya
    ti          Sakinu  azua        a              aya
    主格   人名     主格.那  連繫詞   說
    沙基奴是

    119.
    0:05:22.700,0:05:24.480
    na puvaljaw tjai Masayu
    na-pu-valjaw        tjai     Masayu
    完成貌-有-配偶   斜格  人名

    就娶朱家小姐叫"嗎沙優"的

    120.
    0:05:26.680,0:05:29.300
    tima anga aza 朱..朱 朱家的
    tima=anga   aza         朱 朱 朱家的
    誰=完成貌  主格.那  朱 朱 朱家的
    朱家的誰了

    121.
    0:05:30.000,0:05:31.360
    uh tiamadju a taqumaqan
    uh               tiamadju  a               taqumaqan
    言談標記  他.斜格     連繫詞  一家人
    喔 他們那一家的

    122.
    0:05:31.580,0:05:32.780
    'u pinaka melekaka aza
    'u=p<in>aka                   mele-kaka                       aza
    我.屬格=<受焦>經由  MALE-兄弟姊妹           主格.那
    我以為"拉魯麼砍"跟"沙島碗"是姊妹

    123.
    0:05:33.000,0:05:34.660
    tia Sauren avav anga aza tia Pinsiang
    tia    Sauren avan=anga         aza             tia       Pinsiang
    主格 人名     就是=完成貌   主格.那     主格   家屋名
    "拉魯麼砍"的親戚還有田家家族

    124.
    0:05:36.860,0:05:37.440
    'u pinaka
    'u=p<in>aka
    我.屬格=<受焦>覺得

    我以為

    125.
    0:05:37.540,0:05:39.974
    ti Sadengiyap a kama ni aya
    ti         Sadengiyap   a               kama  ni        aya
    主格  人名                連繫詞    父親   屬格   說
    "沙的哩牙蔔"是爸爸

    126.
    0:05:39.974,0:05:41.974
    ni Sauren kati Sakinu
    ni      Sauren  kati  Sakinu
    屬格 人名       跟    人名
    "Sauren 跟Sakinu的爸爸

    127.
    0:05:42.400,0:05:44.320
    G: 'u pinaka melekaka tiamadju
    G: 'u=p<in>aka                 mele-kaka           tiamadju
    G: 我.屬格=<受焦>覺得  互相-兄弟姊妹  他們.主格

    我以為她們是姊妹

    128.
    0:05:44.740,0:05:46.560
    au ti Ljaljumegan
    au               ti        Ljaljumegan
    言談標記  主格  人名
    然後拉魯麼砍

    129.
    0:05:47.740,0:05:49.540
    ti Ljaljumegan ti Sadjasa
    ti        Ljaljumegan   ti        Sadjasa
    主格  人名                主格  人名
    "拉魯麼砍" "沙家沙"

    130.
    0:05:50.860,0:05:51.480
    matu
    matu
    好像
    好像

    131.
    0:05:52.573,0:05:53.128
    tjalja
    tja-lja
    比較-LJA
    最

    132.
    0:05:53.350,0:05:54.829
    tjalja sipu
    tja-lja          sipu
    比較-LJA    XX

    133.
    0:05:55.460,0:05:58.600
    tjaljavulungan a ni Sauren a kama ti Sadengiyap
    tja-lja-vulung-an  a             ni      Sauren  a            kama   ti        Sadengiyap
    比較-LJA-老-AN  連繫詞  屬格  人名     連繫詞  父親    主格   人名
    他們是三兄妹.最大是田家的爸爸

    134.
    0:05:59.380,0:06:01.420
    tja silukai-an anan numaya aza kuvekuv
    tja=si-lu-kai-an=anan                              numaya    aza       kuvekuv
    我們.包含.屬格=參焦-LU-話-AN=還    不然        主格.那   監獄
    不然我們先回到那個監獄的故事

    135.
    0:06:01.620,0:06:03.380
    au kamacay
    au                 ka-macay
    言談標記    當-死
    後來她死了

    136.
    0:06:04.960,0:06:07.720
    G: akumay kemeljang tu na kipacay aya anga
    G: akumay k<em>eljang  tu                na-ki-pacay          aya=anga
    G: 為何       <主焦>知道    補語連詞  完成貌-自己-死   說=完成貌
    G: 為什麼日本人知道他死掉了?

    137.
    0:06:08.520,0:06:09.900
    G: aza ti Ljaljumegan
    G: aza           ti        Ljaljumegan
    G: 主格.那  主格   人名
    G: 那位拉魯麼砍?

    138.
    0:06:10.320,0:06:12.400
    saka suqeljevan nua kisace
    sa-ka        su-qeljev-an          nua   kisace
    然後-KA  SU-開.關門-AN     屬格  警察

    警察會開門查看啊!

    139.
    0:06:12.660,0:06:13.740
    masa na uli
    masa na-uli
    也許  完成貌-非實現
    也許可能

    140.
    0:06:14.520,0:06:17.020
    pinasasasaw ki na uli ka pinakakanan
    p<in>a-sa-sasaw                   ki-na            uli            ka-p<in>a-ka-kan-an
    <完成貌>使役-重疊-外面   KI-完成貌  非實現   KA-<受焦>使役-重疊-吃-AN

    要放他出去或者要拿飯給他吃

    141.
    0:06:17.140,0:06:19.900
    lja nu i huin itjen pakanan nitjen dalu
    lja     nu       i      huin=itjen                               pa-kan-an      nitjen                    dalu
    因為 如果  在  法院.日語=我們.包含.主格  使役-吃-AN   我們.包含.屬格  DALU
    因為我們被關在監獄會給我們吃飯吧!

    142.
    0:06:21.240,0:06:22.960
    au neka anga aya
    au               neka=anga          aya
    言談標記  否定=完成貌     說
    結果沒有氣了這樣

    143.
    0:06:22.960,0:06:23.888
    uh
    uh
    言談標記
    喔

    144.
    0:06:24.640,0:06:26.320
    au pida qadaw a qineljevan
    au                pida   qadaw  a            q<in>eljev-an
    言談標記   多少   日子    連繫詞  <受焦>關-AN
    然後關幾天?

    145.
    0:06:26.660,0:06:28.840
    ilu 'u keljang ljakua na maitazua
    ilu          'u=keljang        ljakua  na-maitazua
    怎麼會  我.屬格=知道  但是   完成貌-這樣
    我不清楚.但事情就這樣

    146.
    0:06:29.380,0:06:30.780
    a na tjaucikel
    a             na-tjaucikel
    連繫詞  完成貌-告訴
    傳述的

    147.
    0:06:31.620,0:06:33.080
    naikaui i aya ma
    na-ika-ui               i aya   ma
    完成貌-不-肯定  I  說   言談標記

    過去就是不行

    148.
    0:06:33.340,0:06:34.440
    nai kaui  aya
    na-ika-ui               aya
    完成貌-不-肯定   說
    不准

    149.
    0:06:35.760,0:06:38.360
    Dripung tjanuitjen puvaljaw ta pailang tua
    Dripung  tjanuitjen            pu-valjaw   ta      pailang  tua
    日本        我們.包含.斜格  有-配偶      斜格  平地人  斜格

    日本人不准我們原住民嫁平地人

    150.
    0:06:38.360,0:06:38.860
    tua tjayamadju
    tua    tjayamadju
    斜格  他們.斜格
    或他們

    151.
    0:06:38.960,0:06:41.440
    na sa puvaljaw ta
    na-sa-pu-valjaw          ta
    屬格-然後-有-配偶   斜格
    可能想娶

    152.
    0:06:41.640,0:06:44.200
    aya dalu na tjengelay a Dripung ta aza tiamadju
    aya dalu    na-tjengelay   a             Dripung   ta      aza          tiamadju
    說   DALU  完成貌-喜歡  連繫詞  日本        斜格  主格.那   他們.主格

    153.
    0:06:44.560,0:06:45.960
    saka na valeljevelj aya
    saka  na-valeljevelj aya
    而且  完成貌-漂亮   說
    就是太漂亮了啦!

    154.
    0:06:46.560,0:06:47.500
    sa aya tjamadju
    sa      aya=tjaimadju
    想要 說=他們.主格
    想要給他

    155.
    0:06:47.500,0:06:48.480
    ui
    ui
    言談標記
    是

    156.
    0:06:48.480,0:06:52.580
    qetji aza na ti vuvu anga i Sakenge a kina ni Muljasan.
    qetji  aza          na      ti       vuvu=anga      i   Sakenge  a            kina    ni      Muljasan
    你看  主格.那 屬格  主格 奶奶=完成貌  I  人名         連繫詞  媽媽  屬格 人名
    你看那土坂有錢家族"Mliasan"的奶奶"Skenge

    157.
    0:06:52.700,0:06:54.700
    na puvaljaw ta ripun
    na-pu-valjaw       ta      dripung
    完成貌-有-配偶  斜格    日本
    有嫁給日本人

    158.
    0:06:55.300,0:06:56.440
    tia Muljasan ni
    tia   Muljasan ni
    XX  人名          言談標記

    目拉上(望族)

    159.
    0:06:56.600,0:06:59.201
    ljakua na anema na Dripung aza kama ni
    ljakua na=anema         na       Dripung  aza          kama  ni
    但是    完成貌=什麼   屬格   日本         主格.那  父親  屬格
    但是他爸爸好像是在當時的日本

    160.
    0:06:59.758,0:07:01.461
    kama ni Muljiasan kiaya
    kama   ni      Muljiasan ki-aya
    父親   屬格  人名          KI-說
    Muljasan當某個官差

    161.
    0:07:01.860,0:07:03.220
    na izua zua i
    na       i<zua>zua                i
    屬格  處所.那<重疊>      xx
    他們住在那裡..

    162.
    0:07:04.120,0:07:07.260
    qadjaw ki na uli kaizuanan a kisace tazua
    qadjaw ki-na-uli               kaizuanan   a                  kisace  tazua
    可能      KI-屬格-非實現  居住地       主格標記    警察      那時
    不知那時還有沒有日本警察

    163.
    0:07:07.640,0:07:09.880
    lja kinungida tazua ma
    lja      kinungida tazua  ma
    因為 何時           那時     言談標記
    因為不知什麼時候的那個嘛!.....

    164.
    0:07:10.400,0:07:12.260
    ki tjaisangas a ziday  ki anemam
    ki-tja-isangas   a             ziday  ki-anema
    KI-比較-先前  連繫詞  時代    KI-什麼
    不知是民前或者是什麼

    165.
    0:07:13.180,0:07:15.620
    "民前" a tjai sangas ta Dripung dalu
    民前   a             tjai     sangas  ta       Dripung dalu
    民前  連繫詞  斜格   之前    斜格   日本       DALU
    民前比日本還前面?

    166.
    0:07:16.000,0:07:16.720
    ljki Dripung
    ljki    Dripung
    還是 日本
    還是日本

    167.
    0:07:18.660,0:07:21.040
    日本喔 a 昭和...昭和吧
    日本喔   a 昭和 昭和吧
    日本喔   連繫詞  昭和 昭和吧
    日本喔  昭和 昭和吧

    168.
    0:07:22.360,0:07:23.380
    昭和
    昭和
    昭和
    昭和

    169.
    0:07:23.560,0:07:26.180
    昭和 a tjaisangas ta 日本
    昭和   a             tja-isangas  ta      日本
    昭和 連繫詞   比較-之前   斜格 日本
    比日本昭和之前

    170.
    0:07:29.380,0:07:30.660
    ljavililj anga 昭和 qetji azua sinan
    lja-vililj=anga 昭和             qetji  azua      s<in>an
    比較-後面=完成貌  昭和  看     主格.那 <受焦>做
    昭和很後面了!你看那座的

    171.
    0:07:30.940,0:07:32.280
    qetji aza sinan tjakuran
    qetji  aza          s<in>an      tjakuran
    看     主格.那   <主焦>做  吊橋
    你看他們做的吊橋

    172.
    0:07:32.440,0:07:34.200
    哪民國14..13年
    哪民國14 13年
    哪民國14 13年
    哪民國14..13年

    173.
    0:07:34.960,0:07:38.060
    avan ka uli maqaqeci anga tjen vaik anga
    avan ka-uli           ma-qa-qeci=anga=tjen                                vaik=anga
    就是 當-非實現   主焦-重疊-殺=完成貌=我們.包含.這個   去=完成貌
    是我們快要戰爭時日本人才離開

    174.
    0:07:39.220,0:07:40.860
    navan tazua
    navan tazua
    就是   那時
    就那時候

    175.
    0:07:40.860,0:07:41.505
    uh
    uh
    言談標記
    喔

    176.
    0:07:42.080,0:07:45.360
    ljakua  aza ti ubasan Uwan na ika mahuing
    ljakua  aza           ti       ubasan Uwan  na            ika   ma-huing
    但是    主格.那   主格  歐巴桑  人名  完成貌  否定 主焦-監獄
    但砂島婉並沒因此入獄

    177.
    0:07:45.920,0:07:48.440
    pai na kiniljingaljinga na  Dripung
    pai                na-k<in>i-ljinga-ljinga             na     Dripung
    言談標記    完成貌-<受焦>KI-重疊-罵    屬格  日本
    那時被日本罵得很慘

    178.
    0:07:48.900,0:07:51.340
    kamakadju ta aza kama ni Asaku
    ka-ma-kadju     ta      aza           kama  ni       Asaku
    KA-主焦-貪戀  斜格 主格.那  父親    屬格  人名
    她在喜歡包頭目的爸爸

    179.
    0:07:51.920,0:07:52.460
    Dripung
    Dripung
    日本
    日本

    180.
    0:07:52.794,0:07:53.400
    ui
    ui
    言談標記
    是

    181.
    0:07:53.400,0:07:55.220
    a ui  Dripung aza kama ni Asaku
    a             ui                Dripung   aza         kama  ni     Asaku
    填補詞 言談標記  日本        主格.那  父親    屬格 人名

    啊對! 包頭目"阿莎古"的爸爸

    182.
    0:07:56.080,0:07:58.760
    au sivaivaik anga  aza kama sema
    au                si-vai-vaik=anga             aza         kama  s<em>a
    言談標記  參焦-重疊-去=完成貌  主格.那 父親   <主焦>去
    他父親就丟下她們

    183.
    0:07:58.760,0:08:00.616
    aya kama aya
    aya ka-ma-aya
    說   KA-主焦-說
    跟中日

    184.
    0:08:01.140,0:08:02.494
    kapuamin namaqaqeci
    ka-pu-amin  na-ma-qa-qeci
    KA-有-結束  完成貌-主焦-重疊-殺
    當戰爭結束

    185.
    0:08:02.494,0:08:03.223
    ui
    ui
    言談標記
    是

    186.
    0:08:03.520,0:08:07.320
    au tima au ika kinacu ti..ti ina i Asaku
    au               tima  au                ika    k<in>acu  ti        ti        ina      i  Asaku
    言談標記  誰     言談標記   否定 <受焦>帶 XX    主格   母親    I  人名
    然後那位..然後沒將"阿莎古"帶回日本?

    187.
    0:08:07.640,0:08:08.440
    ita ni
    ita      ni
    一個   助詞

    一個后

    188.
    0:08:08.520,0:08:09.020
    na ita
    na      ita
    屬格  一個
    嗯 只有一個

    189.
    0:08:10.060,0:08:13.200
    au napatigamigamiyanan aya yu
    au               na-pa-ti<gami>gami=anan  aya  yu
    言談標記  完成貌-使役-<重疊>信=還  說   助詞
    聽說那日本人曾來信多次

    190.
    0:08:13.300,0:08:15.515
    aza na kama ni Asaku a Dripung
    aza         na      kama   ni     Asaku  a           Dripung
    主格.那 屬格  父親   屬格 人名   連繫詞  日本
    那"阿莎古"的日本爸

    191.
    0:08:15.680,0:08:17.040
    ti ubasan Uwan
    ti       ubasan  Uwan
    主格 歐巴桑  人名
    及" 砂島婉"

    192.
    0:08:17.540,0:08:19.900
    tazua na makadjukadju anga tjai Sadjanau
    tazua na-ma-kadju-kadju=anga                tjai    Sadjanau
    那時  完成貌-主焦-重疊-戀愛=完成貌   斜格 人名
    那時候"砂島婉"正在跟"砂家腦"戀愛

    193.
    0:08:19.960,0:08:21.740
    kama ni Dasan
    kama ni      Dasan
    父親  斜格  人名
    包賜晶的爸爸

    194.
    0:08:22.200,0:08:24.120
    aza ti ubasan Uwan aya au
    aza         ti        ubasan Uwan aya au
    主格.那 主格  歐巴桑  人名   說  言談標記
    那"砂島婉"這樣然後

    195.
    0:08:24.460,0:08:26.720
    naika sinitjumatjumalj a tigami aya
    na=ika             s<in>i-tjuma-tjumalj             a             tigami aya
    完成貌=否定 <完成貌>參焦-重疊-告訴   連繫詞  信         說

    關於日本人寫信這件事情.

    196.
    0:08:26.720,0:08:29.960
    taza ti aya ti Sadjanau
    taza         ti        aya  ti       Sadjanau
    斜格.那  主格  說   主格 人名
    她瞞著王天量她先生

    197.
    0:08:30.480,0:08:32.180
    kama ni aya Dasan
    kama ni      aya Dasan
    父親  屬格 說   人名
    就"達上"的爸爸

    198.
    0:08:32.540,0:08:35.420
    ika vaiken a kimen, qadjaw ka izuanan
    ika    vaik-en   a            kimen  qadjaw  ka   izua=anan
    否定 去-受焦 連繫詞   找         不知道  KA  存在句=還
    怎麼不去日本找， 也許還找的到

    199.
    0:08:35.600,0:08:37.860
    saka uli navinainaik a kemin a ma Dripung
    saka uli           na-v<in>ai-vaik     a kemin  a            ma-Dripung
    而且 非實現 <完成貌>重疊-去 連繫詞   連繫詞  主焦-國名

    而且本來有說要去日本找

    200.
    0:08:38.020,0:08:40.280
    ljakua neka anga matu na aya aya
    ljakua neka=anga       matu na-aya         aya
    但是     否定=完成貌 好像 完成貌-說   說
    但聽說過世了這樣

    201.
    0:08:40.440,0:08:41.380
    a pasemalaw
    a              pasemalaw
    連繫詞   告訴
    告知的

    202.
    0:08:41.440,0:08:43.480
    uli kaizua malekakakaka
    uli           ka-izua         male-kaka-kaka
    非實現  KA-存在句   互相-重疊-兄弟姊妹
    也許日本還有他的親戚們

    203.
    0:08:44.640,0:08:45.640
    tjala izuwa lja
    tjala izua   lja
    應該 存在 言談標記
    可能有吧!

    204.
    0:08:51.580,0:08:52.600
    inu ca
    inu     ca
    那裡  這
    在那兒?

    205.
    0:08:53.820,0:08:54.600
    uduli
    uduli
    跳舞.日語
    跳舞

    206.
    0:08:55.400,0:08:57.160
    mama inu aza vuvuwa na
    mama inu    aza         vuvuwa  na
    媽媽    哪裡 主格.那  山上      屬格
    媽媽那山上在哪裡

    207.
    0:08:57.380,0:08:59.840
    na kase Tjuabalan a aya
    na     ka-se-Tjuabal-an     a           aya
    屬格 KA-屬-地名-AN      連繫詞  說
    真正土板在地的舊部落

    208.
    0:09:00.000,0:09:03.500
    azua pasu lizuk aza itua namatucu a gadu
    azua       pa-su-lizuk       aza          itua namaitucu      a              gadu
    主格.那  使役-SU-平原 主格.那  在    這樣                 連繫詞   山
    就那座比較平原的山脈

    209.
    0:09:03.500,0:09:04.000
    ainu
    ainu
    哪裡
    哪裡

    210.
    0:09:04.100,0:09:07.120
    azua zuazua anan a gadu namaitucu
    azua        zua-zua=anan       a              gadu   namaitucu
    主格.那   重疊-主格.那=還 連繫詞   山       這樣
    就後面那座這樣的山

    211.
    0:09:07.500,0:09:08.000
    avan azua
    avan azua
    就是 主格.那
    就那個...

    212.
    0:09:09.940,0:09:12.160
    qadjaw kipaljecaza su sasinki
    qadjaw  ki-pa-lje-caza     su           sasinki
    不知道   KI-使役-LJE-遠 你.屬格  相機.日語
    你的照相機可以照那麼遠?

    213.
    0:09:12.340,0:09:13.420
    dikilu ljakua keri
    dikilu          ljakua   keri
    可以.日語   但是    小
    可以但影目很小

    214.
    0:09:13.420,0:09:15.500
    aza aicu i caceveljan i pavavaw
    aza         aicu   i       ca-cevelj-an    i pa-vavaw
    主格.那  這   處所  重疊-埋-AN    I  使役-上面
    在這個墳墓的上面喔

    215.
    0:09:15.780,0:09:18.440
    ui aicu a sevesevec a paljezua i zaya
    ui                aicu a              seve-sevec a              pa-lje-zua                 i          zaya
    言談標記  這    連繫詞  重疊-直       連繫詞  使役-LJE-主格.那   處所  上方
    是,這直直的往上面

    216.
    0:09:18.640,0:09:20.440
    taza namaitucu a gadu lja
    taza         namaitucu  a              gadu  lja
    斜格.那  這樣             連繫詞   山       言談標記
    像這樣的山脈啦

    217.
    0:09:20.440,0:09:21.374
    tucu
    tucu
    這樣
    這樣

    218.
    0:09:21.374,0:09:22.224
    uh
    uh
    言談標記
    喔

    219.
    0:09:23.892,0:09:25.829
    aicu a quma nia Iki
    aicu  a            quma nia=Iki
    這    連繫詞  山上    我們.屬格=人名
    這Iki的山上

    220.
    0:09:26.220,0:09:27.960
    tinalem ta zulin
    t<in>alem     ta      zulin
    <受焦>種植  斜格 造林

    有種造林
    """
