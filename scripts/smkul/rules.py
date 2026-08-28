"""glossing 規則驗證：切分與 gloss 的對應、構詞判定。

規則本身寫在 features/切分與glossing對應.feature 與
features/構詞判定.feature，這裡是對應的實作。
"""

import re
from collections import OrderedDict

from scripts.smkul.entry import (
    Attachment,
    Issue,
    IssueKind,
    Morpheme,
    Word,
)
from scripts.smkul.markers import (
    MarkerList,
    REDUPLICATION_GLOSS,
    is_uncertain,
)

# 切分符號。位置要與 gloss 呼應。
AFFIX = "-"
CLITIC = "="
REDUPLICATION = "~"
INFIX_OPEN = "<"
INFIX_CLOSE = ">"
SYMBOLS = AFFIX + CLITIC + REDUPLICATION + INFIX_OPEN + INFIX_CLOSE

# ODS 備註欄認可的特殊符號與言談現象。值是
# (標在第幾行, 說明, 在 gloss 裡也算合法符號)。
# 報告的「語料格式說明」章直接用這一份，不另外維護一份文件。
SPECIAL_MARKS = OrderedDict()
SPECIAL_MARKS["XX"] = (
    "第一、二、三行", "false start（口誤），前後空一格，不要切割", False)
SPECIAL_MARKS["=="] = ("第一行", "字尾、句尾拉長音，如 `wata==`", True)
SPECIAL_MARKS[":"] = (
    "第一、二行",
    "詞中拉長音，置於倒數第二音節之後，如 `iti:raw`；"
    "第三行的標記不含括弧部分", True)
SPECIAL_MARKS["..."] = ("第一行", "聽不清楚，前後空一格", True)
SPECIAL_MARKS["…"] = ("第一行", "聽不清楚（全形寫法）", True)
SPECIAL_MARKS["＠"] = ("第一行", "笑聲，前後空一格", True)
SPECIAL_MARKS["@"] = ("第一行", "笑聲（半形寫法）", True)
SPECIAL_MARKS["(咳嗽)"] = ("第一行", "咳嗽，前後空一格", False)
SPECIAL_MARKS["?"] = (
    "第三行", "不確定是什麼，與全大寫拉丁字母同義", True)
SPECIAL_MARKS["^"] = ("第一行", "ODS 備註欄列的其他標記", True)

_合法 = []
for _符號, _內容 in SPECIAL_MARKS.items():
    if _內容[2]:
        _合法.append(_符號)
# gloss 裡出現也不算錯誤的那幾個。
SPECIAL = tuple(_合法)


# 切分符號的意思。報告的「語料格式說明」章直接用這一份。
SYMBOL_MEANING = OrderedDict()
SYMBOL_MEANING[AFFIX] = ("詞綴（前綴、後綴）", "`pi-codad-an` / `PI-書-處焦`")
SYMBOL_MEANING[CLITIC] = ("依附詞（clitic）", "`awa=to` / `沒有=完成貌`")
SYMBOL_MEANING["<>"] = ("中綴", "`s<m>iling` / `<主焦>問`")
SYMBOL_MEANING[REDUPLICATION] = ("重疊", "`m~meenu` / `即將~什麼樣`")


def tokens(line):
    return line.split()


def symbol_shape(token):
    """一个 token ê切分符號長相,照順序。用來比兩爿呼應無。

    拉長音ê ==(ODS 1-4)毋是切分符號,愛先閃開;無ê話
    `lja==` 佮伊ê gloss `XX` 就會比做無仝款。
    """
    out = []
    for char in token.replace(LONG_VOWEL, ""):
        if char in SYMBOLS:
            out.append(char)
    return "".join(out)


# 切分行佮 gloss 行對袂起來ê分類,名稱佮
# features/切分與glossing對應.feature ê Scenario 仝款。
GLOSS_FEWER = "gloss 的詞比切分少"
GLOSS_MORE = "gloss 的詞比切分多"
GLOSS_CUT_MORE = "切分沒有切，gloss 有切"
GLOSS_CUT_FEWER = "切分有切，gloss 沒有切"
SYMBOL_KIND_DIFF = "符號的種類不一樣"


def check_correspondence(segmentation, gloss):
    """比切分行佮 gloss 行對會起來袂。

    回傳 (分類, 切分 token, gloss token)。對會起來ê時陣分類是
    None。詞數無仝就規逝比;詞數仝款才逐个 token 比符號,
    掠頭一个對袂起來ê。
    """
    left = tokens(segmentation)
    right = tokens(gloss)
    if len(right) < len(left):
        return GLOSS_FEWER, "", ""
    if len(right) > len(left):
        return GLOSS_MORE, "", ""
    for index, token in enumerate(left):
        here = symbol_shape(token)
        there = symbol_shape(right[index])
        if here == there:
            continue
        if len(here) < len(there):
            return GLOSS_CUT_MORE, token, right[index]
        if len(here) > len(there):
            return GLOSS_CUT_FEWER, token, right[index]
        return SYMBOL_KIND_DIFF, token, right[index]
    return None, "", ""


# 五種分類各對一個問題類別，值就是分類名。
CORRESPONDENCE_KIND = {
    GLOSS_FEWER: IssueKind.GLOSS_FEWER,
    GLOSS_MORE: IssueKind.GLOSS_MORE,
    GLOSS_CUT_MORE: IssueKind.GLOSS_CUT_MORE,
    GLOSS_CUT_FEWER: IssueKind.GLOSS_CUT_FEWER,
    SYMBOL_KIND_DIFF: IssueKind.SYMBOL_KIND_DIFF,
}


def check_entry_correspondence(entry):
    """一組的切分行與 gloss 行對不對得起來，回傳問題清單。

    分類與說明都照 features/切分與glossing對應.feature。詞數不同的
    兩類對照整行，逐個詞比出來的三類對照那一對詞。
    """
    kind, left, right = check_correspondence(
        entry.segmentation, entry.gloss)
    if kind is None:
        return []
    if left or right:
        detail = "這個詞的切分符號對不起來"
        pairs = [("切分", left), ("gloss", right)]
    else:
        detail = (
            "切分 " + str(len(tokens(entry.segmentation))) + " 個詞，"
            "gloss " + str(len(tokens(entry.gloss))) + " 個詞"
        )
        pairs = [("切分", entry.segmentation), ("gloss", entry.gloss)]
    return [
        Issue(
            CORRESPONDENCE_KIND[kind], entry.path, entry.number,
            detail, pairs,
        )
    ]


INFIX_PATTERN = re.compile(r'<([^>]*)>')

# 中綴用這个記號,佮 -、=、~ 這款真正ê分界符號分開。
INFIX_MARK = "<>"

# 拉長音ê ==(ODS 1-4)毋是切分符號。掃ê時先換做替身,
# 才袂去予 = 切做兩刀(霧台魯凱 ai==au==i)。
LONG_VOWEL = "=="
PLACEHOLDER = "\x00"


def split_morphemes(token):
    """把一個 token 拆成 [(形, 分界符號)]。

    中綴先抽出來排在前面,賰ê詞幹才照 -、=、~ 拆。分界符號記ê是
    這一段「頭前彼个符號」,第一段是空字串。切分行佮 gloss 行用
    仝一套規則,兩爿才對會起來:
    `q<m><n>ita=su` → [(m, <>), (n, <>), (qita, ), (su, =)]
    `看<主焦><完成貌>=你.屬格` → [(主焦, <>), (完成貌, <>), (看, ),
                                  (你.屬格, =)]

    拉長音ê ==(ODS 1-4)毋是切分符號,袂當去予 = 切做兩刀,
    所以先閃開才掃。
    """
    out = []
    for found in INFIX_PATTERN.findall(token):
        out.append((found, INFIX_MARK))
    rest = INFIX_PATTERN.sub("", token)
    rest = rest.replace(LONG_VOWEL, PLACEHOLDER)

    current = []
    separator = ""
    stem = []
    for char in rest:
        if char in (AFFIX, CLITIC, REDUPLICATION):
            stem.append(("".join(current), separator))
            current = []
            separator = char
            continue
        current.append(char)
    stem.append(("".join(current), separator))

    for form, mark in stem:
        out.append((form.replace(PLACEHOLDER, LONG_VOWEL), mark))
    return out


def _is_reduplication(gloss):
    """gloss 直接寫「重疊」的（判斷方法 1e）。"""
    return gloss.strip() == REDUPLICATION_GLOSS


def classify(forms, glosses, markers):
    """判逐段ê構詞。流程照 features/構詞判定.feature ê「判斷方法」。

    第 1 步先標詞綴(中綴、環綴、重疊、未分類詞綴),第 2 步看賰
    幾段無標:井一段就是詞根,其他ê照佮詞根之間跨過啥物符號分做
    依附詞/重疊/前綴/後綴。第 3 步分袂出詞根ê(3b、3c),中綴以外
    逐段攏記「無法判斷」。
    """
    fixed = []
    tentative = []
    for index in range(len(forms)):
        fixed.append(None)
        tentative.append(False)

    # 1a 中綴:<> 內底ê。
    for index, (form, mark) in enumerate(forms):
        if mark == INFIX_MARK:
            fixed[index] = Attachment.INFIX

    # 1c 環綴:清單有登記ê,頭尾兩段各家己標。
    if markers.circumfix_pair(glosses):
        if fixed[0] is None:
            fixed[0] = Attachment.CIRCUMFIX
        if fixed[-1] is None:
            fixed[-1] = Attachment.CIRCUMFIX

    # 1b、1d 未分類詞綴:查會著清單ê,抑是大寫ê不確定標記。
    for index in range(len(forms)):
        if fixed[index] is not None:
            continue
        if index < len(glosses):
            gloss = glosses[index][0]
        else:
            gloss = ""
        tentative[index] = markers.is_marker(forms[index][0], gloss)

    # 1e 重疊:gloss 直接寫「重疊」ê。排tī 1d 後壁,因為清單ê
    # 類別欄嘛有「重疊」,袂使去予 1d 先標做未分類詞綴。
    for index in range(len(forms)):
        if fixed[index] is not None:
            continue
        if index < len(glosses) and _is_reduplication(glosses[index][0]):
            fixed[index] = Attachment.REDUPLICATION
            tentative[index] = False

    # 3a ê特例:規个詞干焦一段(無切分符號),彼段就是詞根。
    # 詞綴愛有物件通黏才成立,無黏ê時陣查會著清單嘛袂使算詞綴——
    # 若無,`a`/連繫詞、`ta`/斜格 這款單詞就攏會予判做「無法判斷」。
    stem_count = 0
    only = -1
    for index, (form, mark) in enumerate(forms):
        if mark == INFIX_MARK:
            continue
        stem_count += 1
        only = index
    if stem_count == 1:
        return _assign(forms, fixed, only)

    roots = []
    for index in range(len(forms)):
        if fixed[index] is None and not tentative[index]:
            roots.append(index)

    # 3b、3c:井一段無標才判會出詞根。
    if len(roots) != 1:
        return _assign_without_root(forms, fixed, roots)

    return _assign(forms, fixed, roots[0])


def _stem_of(forms):
    """詞幹逐段ê位置佮伊頭前彼个分界符號(中綴無算tī內)。"""
    stem = []
    separators = []
    for index, (form, mark) in enumerate(forms):
        if mark == INFIX_MARK:
            continue
        stem.append(index)
        separators.append(mark)
    return stem, separators


def _assign_without_root(forms, fixed, roots):
    """詞根分袂出來ê時陣(3b、3c)逐段愛按怎記。

    第 1 步就認出來ê(中綴、環綴、重疊)袂受詞根影響,照留。
    賰ê詞綴,若對逐个可能ê詞根位置攏判做仝款,彼段猶原判會出來
    ——親像 Tala-likor-ay=to ê -ay 佮 =to,無論詞根是 Tala 抑是
    likor,攏tī詞根ê正爿,所以是後綴佮依附詞。判做無仝款ê,才
    記「無法判斷」。
    """
    stem, separators = _stem_of(forms)
    out = []
    for index in range(len(forms)):
        if fixed[index] is not None:
            out.append(fixed[index])
            continue
        if not roots or index in roots:
            out.append(Attachment.UNDECIDED)
            continue
        found = set()
        for root in roots:
            found.add(_between(stem, separators, index, root))
        if len(found) == 1:
            out.append(found.pop())
        else:
            out.append(Attachment.UNDECIDED)
    return out


def _assign(forms, fixed, root):
    """第 2 步:照詞根ê位置決定賰ê逐段是啥物構詞。"""
    stem, separators = _stem_of(forms)

    out = []
    for index in range(len(forms)):
        if index == root:
            out.append(Attachment.ROOT)
            continue
        if fixed[index] is not None:
            out.append(fixed[index])
            continue
        out.append(_between(stem, separators, index, root))
    return out


def _between(stem, separators, index, root):
    """index 佮 root 之間跨過ê符號,決定構詞(判斷方法 2a-2d)。"""
    if root not in stem or index not in stem:
        return Attachment.UNDECIDED
    here = stem.index(index)
    there = stem.index(root)
    if here > there:
        crossed = separators[there + 1:here + 1]
    else:
        crossed = separators[here + 1:there + 1]
    if CLITIC in crossed:
        return Attachment.CLITIC
    if REDUPLICATION in crossed:
        return Attachment.REDUPLICATION
    if here > there:
        return Attachment.SUFFIX
    return Attachment.PREFIX


def analyse_word(segmentation, gloss, markers):
    """判一個詞的構詞，回傳 [Morpheme]。

    這是 features/構詞判定.feature 的入口，build_words 逐個 token
    也呼叫這一支。切分與 gloss 切出來的段數不一樣的時候（像拉長音
    的 `ung~`），分不出詞素，整個 token 算一段「無法判斷」。
    """
    forms = split_morphemes(segmentation)
    glosses = split_morphemes(gloss)
    if len(forms) != len(glosses):
        return [Morpheme(segmentation, gloss, Attachment.UNDECIDED)]
    marks = classify(forms, glosses, markers)
    morphemes = []
    for order, (form, mark) in enumerate(forms):
        morphemes.append(Morpheme(form, glosses[order][0], marks[order]))
    return morphemes


def build_words(entry, markers=None):
    """把一組拆做詞與詞素。前提是 token 數與符號都對得起來。"""
    if markers is None:
        markers = MarkerList.empty()
    words = []
    source_tokens = tokens(entry.source)
    left = tokens(entry.segmentation)
    right = tokens(entry.gloss)
    if len(left) != len(right):
        return words
    for index, token in enumerate(left):
        raw = token
        for char in SYMBOLS:
            raw = raw.replace(char, "")
        if index < len(source_tokens) and source_tokens[index] == raw:
            raw = source_tokens[index]
        words.append(
            Word(raw, token, analyse_word(token, right[index], markers)))
    return words


def has_special(text):
    for mark in SPECIAL:
        if mark in text:
            return True
    return False


# 詞根判袂出來ê兩種情形,報告「構詞判斷困難」彼章用ê分類。
# 名稱佮 features/構詞判定.feature ê判斷方法第 3 點仝款。
CASE_MANY_ROOTS = "不只一段沒被標成詞綴"
CASE_NO_ROOT = "每一段都被標成詞綴"


def collect_undecided(entry, markers, sheet_name):
    """揀出構詞判做「無法判斷」ê詞素,予報告統計。

    這毋是錯誤,嘛袂擋匯出——只是詞根分袂出來,愛請對方確認。
    回傳 [(gloss, 語言, 情形, 切分)]。
    """
    out = []
    for word in entry.words:
        undecided = []
        for morpheme in word.morphemes:
            if morpheme.attachment is Attachment.UNDECIDED:
                undecided.append(morpheme)
        if not undecided:
            continue
        marked = 0
        for morpheme in word.morphemes:
            if morpheme.attachment is Attachment.INFIX:
                continue
            if markers.is_marker(morpheme.form, morpheme.gloss):
                marked += 1
        total = len(word.morphemes)
        if marked >= total:
            case = CASE_NO_ROOT
        else:
            case = CASE_MANY_ROOTS
        for morpheme in undecided:
            gloss = morpheme.gloss.strip()
            if not gloss:
                continue
            out.append((gloss, sheet_name, case, word.segmentation))
    return out


def collect_uncertain(entry, sheet_name):
    """全大寫ê「不確定」標記(ODS 1-2),合法,毋過愛統計。"""
    out = []
    for word in entry.words:
        for morpheme in word.morphemes:
            gloss = morpheme.gloss.strip()
            if not gloss or has_special(gloss):
                continue
            if morpheme.attachment is Attachment.ROOT:
                continue
            if is_uncertain(gloss):
                out.append((gloss, sheet_name))
    return out


def validate(entry, markers=None, sheet_name=""):
    """驗證一組。回傳 (問題清單, 不確定標記, 構詞判斷困難)。

    構詞查不到清單的,不是錯誤——那一段記做「無法判斷」照常匯出,
    另外統計給報告「構詞判斷困難」那一章用。
    """
    if markers is None:
        markers = MarkerList.empty()
    issues = check_entry_correspondence(entry)
    entry.words = build_words(entry, markers)
    uncertain = collect_uncertain(entry, sheet_name)
    undecided = collect_undecided(entry, markers, sheet_name)
    return issues, uncertain, undecided
