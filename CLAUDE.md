# CLAUDE 規定

## Git 操作規定

Claude Code **毋准**執行下底ê git 指令（會影響 staged 檔案、commit 紀錄、分支、抑是遠端）：

- `git commit`
- `git add`
- `git checkout`
- `git switch`
- `git restore --staged`
- `git reset`（任何形式，含 --soft、--hard、--mixed）
- `git branch -d` / `git branch -D`
- `git push`
- `git pull`
- `git fetch`

**准**執行下底ê git 指令（查看抑是暫存，毋影響紀錄）：

- `git stash`、`git stash pop`、`git stash apply`、`git stash list`
- `git log`、`git show`、`git diff`、`git status`
- `git branch`（列出，毋是建立抑是hìnn-sak）
- `git restore <file>`（working tree only，無 `--staged`）

程式碼修改（Edit、Write、等工具）會用得用。

## Python sir-tái-luh

- `for` khǹg 頭前（`for x in ...:`），毋准用 list comprehension 抑是 generator expression kā `for` khǹg tī 後壁（`[... for x in ...]`）。若欲，ài 有特殊理由，而且經過使用者同意。

## 報告語言

程式產生ê報告(`kithann/out/*.md`)一律用**華語**寫,毋通用台語。報告是欲予對方(語料提供方)看--ê，對方讀華語。

程式碼內底ê註解、docstring、變數名、測試名嘛仝款愛用**華語**——對方會看程式碼。

## 報告ê更新日期

報告(`kithann/out/*.md`)ê頭前愛寫**更新日期**,格式親像 `更新日期:2026-08-21`。日期是產生報告彼工ê日子,`report.py` ê `today()` 自動掠,免家己寫。開會ê時陣才知影手頭這份是新--ê抑是舊--ê。

## 報告ê標點

報告(`kithann/out/*.md`)ê**內文**,逗號愛用全形「，」,毋通用半形「,」。

毋過**引用語料ê所在袂使改**——語料原本是半形就留半形。語料攏是用反引號包起來ê(`report.py` ê `code()`),所以規則是:反引號內底莫振動,反引號外口ê內文才換全形。

## 報告ê章節編號

報告(`kithann/out/*.md`)ê章節愛加編號:`## 1. 總覽`、`### 4.2 全形＝→半形=`。開會ê時陣通好直接講「第 5.3 節」,免koh揣。編號是 `scripts/smkul/report.py` ê `number_headings()` 自動加ê,寫章節ê時免家己編。

## 報告ê例

報告內底ê「自動處理」佮「構詞判斷困難」這兩章,逐項干焦寫**摘要佮筆數**,例莫複製入去報告,直接註明「詳見 `features/xxx.feature`」。**3 組例**攏寫tī feature ê Scenario 註解(逐組愛有「原句子」佮「處理後ê句子」,koh愛註明是佗一个檔案、第幾組),規則佮例干焦一份,袂走精。

## 統計欄位ê定義

報告內底ê統計表,若是「組數」佮「筆數」無仝ê,兩欄攏愛列,koh愛tī表頂懸寫清楚定義。一組會使有幾若筆問題(親像行數無仝算一筆、逐逝無仝koh各算一筆),干焦列一欄會hōo人看毋著。

## Gherkin feature

**討論 feature ê時,feature 是規格,程式後壁才綴。** 咱討論規格ê時陣,`features/*.feature` 直接寫**確定ê規格**,Step ê內文寫**正確ê行為**(毋是程式這馬ê行為)。`features/steps/` 佮 `scripts/` 這時陣**莫振動**,測試紅ê無要緊——彼是teh講「規格已經定矣,程式猶未做」。等規格定案,使用者開喙講欲做,才轉來改 step 佮程式。

逐个 `features/*.feature` ê Feature 名後壁愛寫**更新日期**,格式親像 `更新日期：2026.8.22`,khǹg tī 第 3 逝(Feature 名下底空一逝)。開會ê時陣才知影手頭這份是新--ê抑是舊--ê。

`features/*.feature` ê Scenario 名佮 Step 內文,咱家己寫ê彼部份,逗號愛用**全形**(`，`)。引用ê語料原文、ODS 原始資料一律**照原樣**——語料本底是半形就留半形,袂使去改伊。

Feature ê例愛照語言優先序揀:**例 1 阿美(秀姑巒→海岸→南勢)、例 2 太魯閣、例 3 魯凱**,無夠才用排灣,koh再無夠才用布農、泰雅。三組例盡量三種無仝ê語言。Given、When、Then 用ê彼組嘛照這个順序揀(就是例 1)。

**難判斷佮已知判毋著ê案例,愛排tī feature ê上尾**,逐个各做一條 scenario,標 `@規格要討論`,而且tī註解寫清楚:出處、為啥物歹判斷、程式這馬判按怎、應該愛是按怎。Then 寫ê是程式這馬ê輸出(毋是正確答案),予人通好逐條確認;程式修好了後才轉來改表格佮標籤。

`features/*.feature` 愛過 `npx gherkin-lint`(設定 tī `.gherkin-lintrc`,CI 有走,看 `.travis.yml` ê「Check Gherkin format」)。注意伊ê縮排慣例佮一般無仝:Scenario 0 格、Step 2 格、表格 4 格。

## OpenSpec change 文件ê標點

`openspec/changes/**/*.md`(proposal、design、specs、tasks)ê**內文**,標點愛用全形:逗號「，」、冒號「：」、分號「；」、括號「（）」。毋通用半形。

仝款,反引號內底(程式碼、語料、路徑、YAML)莫振動;另外 openspec 家己ê結構標頭(`### Requirement:`、`#### Scenario:`、`**WHEN**`、`**Reason**:`、`**Migration**:`)ài留半形,伊ê parser 才認得。
