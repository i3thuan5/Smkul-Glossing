# Tasks: docx-first-yaml

順序固定：feature → steps → 程式 → behave。apply 時若某條 feature 覺得不合理，記在最後一節「apply 時跳過」、先跳過、繼續做，全部做完一次回報，不中途停。

## 1. Feature

- [x] 1.1 刪 `features/註解殘留.feature`；`ls features/` 確認不存在
- [x] 1.2 `features/構詞判定.feature`：「判斷方法」第 3 點補「分不出詞根的，構詞記『無法判斷』，可以進 YAML」；尾端加 A（`tja=黑板`，`@規格要討論`，Then 寫程式現在的輸出、註解寫應該要是）、B（`'i-vaqu` 採-小米，Then 無法判斷）、C（`PA'A`，Then 無法判斷）三條 scenario，例子照語言優先序、各附出處；`npx gherkin-lint features/構詞判定.feature` 無錯
- [x] 1.3 全部 feature 更新日期改成當天；`npx gherkin-lint` 掃整個 `features/` 無錯

## 2. Steps

- [x] 2.1 `features/steps/自動處理.py`：拔 `strip_comments` import 與「docx 的審閱註解是」「讀入這幾行有註解殘留」「清掉註解後是」三個 step；`python -m behave --dry-run` 沒有 undefined step
- [x] 2.2 `features/steps/構詞判定.py`：「判定結果是」把表格的「（無法判斷）」對到 `無法判斷`；`python -m behave features/構詞判定.feature` 裡 A/B/C 三條此時應該**失敗**（程式還沒改），其餘照舊

## 3. 程式：語料來源改 docx（程式未 review，可重寫，見 design D0）

- [x] 3.1 parser 只吃行序列，沒有任何 txt 或註解相關的程式；`grep -rn 'comment\|\.txt' scripts/smkul/parser.py` 零筆
- [x] 3.2 `validate_glossing` 語料走訪只認 `.docx`；`check_docx_txt` 的缺檔/檔名不一致降成提醒；`python -m scripts.validate_glossing` 跑完，總覽檔數為 31
- [x] 3.3 `NormKind` 刪註解錨點、註解本文兩項；`tests/` 的 fixture 改讀 `tests/data/*.docx`，刪註解殘留相關測試；`python -m unittest` 綠燈

## 4. 程式：標記不在清單 → 無法判斷

- [x] 4.1 `scripts/smkul/entry.py`：`Attachment` 加 `UNDECIDED = "無法判斷"`；刪 `IssueKind.MARKER_NOT_IN_LIST` 與其 severity、KIND_WHY；`grep -rn MARKER_NOT_IN_LIST scripts tests features` 零筆
- [x] 4.2 構詞判定查不到清單時把詞素構詞設 `無法判斷`，並回傳 `(gloss, 語言, 類別 A/B/C)` 給報告統計；`python -m behave features/構詞判定.feature` 全綠（含 A/B/C）
- [x] 4.3 `scripts/smkul/yamlout.py` / `entry.py`：確認 `無法判斷` 會寫進 YAML 的「構詞」欄；跑全語料後 `grep -c '構詞: 無法判斷' kithann/out/corpus.yaml` 大於 0，且 YAML 句數比現在的 3786 多

## 5. 報告

- [x] 5.1 `scripts/validate_glossing.py` / `report.py`：第 3 章改寫成「由 docx 產生」；第 4、5 章合併成「自動處理與比對政策」，每項摘要＋筆數＋對應 feature 檔名與 Scenario 名，例子不附；刪 5.10/5.11；產出的 `glossing_report.md` 該章每項都有 `features/` 字樣
- [x] 5.2 新章「構詞判斷困難」：開頭說明（YAML 記無法判斷、照樣匯出、不算錯誤）、A/B/C 三節摘要＋筆數＋指向 `features/構詞判定.feature`、「詞素 × 語言 × 次數 × 檔案數」統計表、尾句「建議補充到《常用構詞標記清單》」；原 6.2、第 8 章、10.2 刪除；總覽加「構詞無法判斷：N 個詞素，見第 N 章」
- [x] 5.3 第 9 章「不確定」標記統計尾句加「建議補充到《常用構詞標記清單》」；第 10 章討論加一條指回「構詞判斷困難」
- [x] 5.4 `scripts/check_docx_txt.py`：todo 章的「請重新匯出乾淨的 txt」拿掉，註解章開頭改成「語料由 docx 產生，沒有殘留問題」；`python -m scripts.check_docx_txt` 跑完
- [x] 5.5 `openspec/specs/corpus-export/spec.md` 的報告需求提到的章節與產出對得上：人工對照 `kithann/out/glossing_report.md` 的標題列表與 design D3

## 6. 驗收

- [x] 6.1 `python -m behave --no-skipped` 全綠
- [x] 6.2 `tox -e flake8,test,yamllint` 綠燈；`npx gherkin-lint` 無錯；`pymarkdown` 對 `openspec/` 與 `docs/` 無錯
- [x] 6.3 人工抽查：東排灣 2 在 YAML 裡沒有 `[a]`～`[z]` 字樣（`grep -c '\[[a-z]\]' kithann/out/corpus.yaml` 為 0）；太魯閣 2 出現在報告與 YAML
- [x] 6.4 更新 `docs/glossing-rules.md` 開頭的語料來源說明（31 docx）與第四節第 5 點（清單外改記無法判斷）

## 8. 補既有紅燈（apply 時擴充的範圍，使用者確認「全部補到綠」）

apply 前 behave 就已經 28 failed / 7 error，與本 change 無關。使用者選擇一併補到綠，因此多做下面這些：

- [x] 8.1 `features/steps/切分與glossing對應.py`：這個 feature **完全沒有 steps 檔**（7 scenario 全 error、17 個 undefined step）。新增 steps，並在 `rules.py` 加 `check_correspondence()` 做五種分類；`python -m behave features/切分與glossing對應.feature` 全綠
- [x] 8.2 構詞判定的詞彙細分（前綴/後綴/環綴/依附詞）：feature 的判斷方法 2a–2d 要求這個粒度，程式只有「詞綴/附著」，整份 feature 因此全紅。`Attachment` 改成 8 個值、`markers.py` 加 `circumfixes_of()` 讀 ODS 環綴；`features/構詞判定.feature` 28/28 全綠
- [x] 8.3 `_count_kinds()` 把大寫拉丁字母也算成拉丁，與 `features/排版分析.feature`「認拉丁行只算小寫字母」相反。改成只算小寫
- [x] 8.4 全華語句組不起來四行：`assemble_entry()` 要求中間行「拉丁、漢字」相間，全華語組因此組不起來。改成整組都是華語時照位置排；組好後仍記一筆「純華語句」NOTICE，所以照舊不匯出
- [x] 8.5 `==`（拉長音，ODS 1-4）被當成兩個 `=` 切壞：`split_morphemes()` 與 `symbol_shape()` 都先把 `==` 閃開
- [x] 8.6 「只差空白」規格（`features/原文切分比對.feature`）程式沒跟上：新增 `word_counts_fit()` 與 `matches()`，字母序列一樣但詞數對不起來就算「詞數不同」（依附詞 `=` 併詞的情形例外）

## 7. apply 時跳過（做的時候填）

- `features/構詞判定.feature` 的「~ 當歌謠的音節分隔」與「拉長音的 == 撞到依附詞的 =」：**兩條的 When 一模一樣，Then 卻互相矛盾**，不可能同時通過。前者要求 `==` 整串算一段詞根（合 ODS 1-4「拉長音用 ==」），後者記的是程式把 `==` 當兩個 `=` 切壞的舊輸出。已依 ODS 實作成「`==` 不當切分符號」，並把後者的 Then 改成新輸出——**兩條現在完全重複，建議合併成一條**，留給您決定。
- `features/構詞判定.feature`「3c 每一段都被標成詞綴：阿美語 tayni-ay」：註解寫「「來」與「實現」都在清單裡」，但 Given 只列了「來」那一列，少了「實現」。已補上 ODS 阿美語 9-18 那一列，Given 才與註解一致。
- **規格待補（請您決定）**：`features/構詞判定.feature` 判斷方法第 1 步只看 gloss 查不查得到清單，所以「實詞的意思剛好等於某個詞綴的 gloss」時（`vaik-i` 去／主焦.祈使、`s-rngaw` 周邊焦／說、`tayni-ay` 來／實現、`na-ni` 過去／NI），每一段都算詞綴，照 3c 判不出詞根——雖然人一看就知道答案。缺的那條規則是：《常用構詞標記清單》登記的是詞綴的**形**（`ma-`、`s-`、`-un`、`-i`、`na-`），不是只有 gloss；「去」在清單裡只代表前綴 `ma-` 的意思是「去」，不代表 `vaik` 這一段是詞綴。若第 1 步加上「形也要對得上登記的詞綴，才算詞綴」，上面四條都判得出來，全語料 350 個「每一段都被標成詞綴」的詞多數也會有解。使用者確認後已把這條寫進判斷方法 1f 並實作：`markers.affix_forms_of()` 從清單抽出每個標記登記的詞綴形，`rules._form_fits()` 查表時形也要對得上。三條原本判不出來的（`vaik-i`、`s-rngaw`、`tayni-ay`）現在都判出正確答案；`Tala-likor-ay=to` 反過來變成（無法判斷），因為清單沒登記 `tala-`、「以後」只登記成詞 `anoayaw`；該 scenario 後來確認行為都被別條涵蓋（形對不上→`vaik-i`、登記成詞→`s-rngaw`、3b 兩個候選與「算起來一致就判得出」→`z<em>e-liu-liulj=amen`），已刪掉，清單缺漏由報告「構詞判斷困難」的統計表呈現。另外補了規則 3 的一條：詞根分不出來的時候，只有分不出來的那幾段記「無法判斷」——中綴／環綴／重疊照留，其餘詞綴若不管詞根是哪一段都判成一樣（像 `Tala-likor-ay=to` 的 `-ay` 與 `=to`，不管詞根是 Tala 還是 likor 都在右邊），那一段照樣判得出來。全語料的「無法判斷」最後是 9.5%，跟加 1f 之前的 9.3% 差不多，但判對的比例高很多。
- `features/構詞判定.feature` 的「已知會判錯：vaik-i」與「難判斷：na-ni」：Then 原本寫的是舊程式的輸出（前綴/詞根、詞根/後綴）。新演算法判成「無法判斷」——比舊的錯答案誠實。已依 CLAUDE.md「程式修好了後才轉來改表格」更新 Then。後來確認：`無法判斷` 本來就是判斷方法 3c 的答案，不是在配合程式。真正要改的是註解——它還在用「程式比 gloss 長短」「先排除全大寫」這種已經刪掉的做法當理由。註解已全部改寫成照規格說明，並把「人看的答案」與缺的那條規則寫清楚。
