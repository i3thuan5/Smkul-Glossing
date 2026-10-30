"""標注規則驗證：詞素切割與詞素翻譯的對應、構詞判定。

規則本身寫在 features/詞素切割與詞素翻譯對應.feature 與
features/構詞判定.feature，這裡是對應的實作。構詞判定已經暫停，
只給 features/構詞判定.feature 的草稿用，驗證流程不呼叫。
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
from scripts.smkul.markers import MarkerList, REDUPLICATION_GLOSS

# 切割符號。位置要與詞素翻譯呼應。
AFFIX = "-"
CLITIC = "="
REDUPLICATION = "~"
INFIX_OPEN = "<"
INFIX_CLOSE = ">"
SYMBOLS = AFFIX + CLITIC + REDUPLICATION + INFIX_OPEN + INFIX_CLOSE

# ODS 備註欄認可的特殊符號與言談現象。值是
# (標在第幾行, 說明, 在詞素翻譯裡也算合法符號)。
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
# 詞素翻譯裡出現也不算錯誤的那幾個。
SPECIAL = tuple(_合法)


# 切割符號的意思。報告的「語料格式說明」章直接用這一份。
SYMBOL_MEANING = OrderedDict()
SYMBOL_MEANING[AFFIX] = ("詞綴（前綴、後綴）", "`pi-codad-an` / `PI-書-處焦`")
SYMBOL_MEANING[CLITIC] = ("依附詞（clitic）", "`awa=to` / `沒有=完成貌`")
SYMBOL_MEANING["<>"] = ("中綴", "`s<m>iling` / `<主焦>問`")
SYMBOL_MEANING[REDUPLICATION] = ("重疊", "`m~meenu` / `即將~什麼樣`")


def tokens(line):
    return line.split()


def symbol_shape(token):
    """一個 token 的切割符號長相,照順序。用來比兩邊有沒有呼應。

    拉長音的 ==(ODS 1-4)不是切割符號,要先避開;不然
    `lja==` 和它的詞素翻譯 `XX` 就會被比成不一樣。
    """
    out = []
    for char in token.replace(LONG_VOWEL, ""):
        if char in SYMBOLS:
            out.append(char)
    return "".join(out)


# 詞素切割行與詞素翻譯行對不起來的分類,名稱與
# features/詞素切割與詞素翻譯對應.feature 的 Scenario 一樣。
# 直接用 IssueKind 的值,兩邊才不會各寫一份。
GLOSS_FEWER = IssueKind.GLOSS_FEWER.value
GLOSS_MORE = IssueKind.GLOSS_MORE.value
GLOSS_CUT_MORE = IssueKind.GLOSS_CUT_MORE.value
GLOSS_CUT_FEWER = IssueKind.GLOSS_CUT_FEWER.value
SYMBOL_KIND_DIFF = IssueKind.SYMBOL_KIND_DIFF.value


def check_correspondence(segmentation, gloss):
    """比詞素切割行與詞素翻譯行對不對得起來。

    回傳 (分類, 詞素切割 token, 詞素翻譯 token)。對得起來時分類是
    None。詞數不同就整行比;詞數相同才逐個 token 比符號,
    取第一個對不起來的。
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
    """一段的詞素切割行與詞素翻譯行對不對得起來，回傳問題清單。

    分類與說明都照 features/詞素切割與詞素翻譯對應.feature。詞數不同的
    兩類對照整行，逐個詞比出來的三類對照那一對詞。
    """
    kind, left, right = check_correspondence(
        entry.segmentation, entry.gloss)
    if kind is None:
        return []
    if left or right:
        detail = "這個詞的切割符號對不起來"
        pairs = [("詞素切割", left), ("詞素翻譯", right)]
    else:
        detail = (
            "詞素切割 " + str(len(tokens(entry.segmentation))) + " 個詞，"
            "詞素翻譯 " + str(len(tokens(entry.gloss))) + " 個詞"
        )
        pairs = [
            ("詞素切割", entry.segmentation), ("詞素翻譯", entry.gloss)]
    return [
        Issue(
            CORRESPONDENCE_KIND[kind], entry.path, entry.number,
            detail, pairs,
        )
    ]


INFIX_PATTERN = re.compile(r'<([^>]*)>')

# 中綴用這個記號,跟 -、=、~ 這種真正的分界符號分開。
INFIX_MARK = "<>"

# 拉長音的 ==(ODS 1-4)不是切割符號。掃的時候先換成替身,
# 才不會被 = 切成兩刀(霧台魯凱 ai==au==i)。
LONG_VOWEL = "=="
PLACEHOLDER = "\x00"


def split_morphemes(token):
    """把一個 token 拆成 [(形, 分界符號)]。

    中綴先抽出來排在前面,剩下的詞幹才照 -、=、~ 拆。分界符號記的是
    這個詞素「前面那個符號」,第一個詞素是空字串。詞素切割行和詞素
    翻譯行用同一套規則,兩邊才對得起來:
    `q<m><n>ita=su` → [(m, <>), (n, <>), (qita, ), (su, =)]
    `看<主焦><完成貌>=你.屬格` → [(主焦, <>), (完成貌, <>), (看, ),
                                  (你.屬格, =)]

    拉長音的 ==(ODS 1-4)不是切割符號,不能被 = 切成兩刀,
    所以先避開再掃。
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
    """詞素翻譯直接寫「重疊」的（判斷方法 1e）。"""
    return gloss.strip() == REDUPLICATION_GLOSS


def classify(forms, glosses, markers):
    """判每個詞素的構詞。流程照 features/構詞判定.feature 的「判斷方法」。

    第 1 步先標詞綴(中綴、環綴、重疊、未分類詞綴),第 2 步看剩下
    幾個詞素沒標:只有一個就是詞根,其他的照和詞根之間跨過什麼符號
    分成依附詞/重疊/前綴/後綴。第 3 步分不出詞根的(3b、3c),中綴以外
    每個詞素都記「無法判斷」。
    """
    fixed = []
    tentative = []
    for index in range(len(forms)):
        fixed.append(None)
        tentative.append(False)

    # 1a 中綴:<> 裡面的。
    for index, (form, mark) in enumerate(forms):
        if mark == INFIX_MARK:
            fixed[index] = Attachment.INFIX

    # 1c 環綴:清單有登記的,頭尾兩個詞素各自標。
    if markers.circumfix_pair(glosses):
        if fixed[0] is None:
            fixed[0] = Attachment.CIRCUMFIX
        if fixed[-1] is None:
            fixed[-1] = Attachment.CIRCUMFIX

    # 1b、1d 未分類詞綴:查得到清單的,或是大寫的不確定標記。
    for index in range(len(forms)):
        if fixed[index] is not None:
            continue
        if index < len(glosses):
            gloss = glosses[index][0]
        else:
            gloss = ""
        tentative[index] = markers.is_marker(forms[index][0], gloss)

    # 1e 重疊:詞素翻譯直接寫「重疊」的。排在 1d 後面,因為清單的
    # 類別欄也有「重疊」,不能讓 1d 先標成未分類詞綴。
    for index in range(len(forms)):
        if fixed[index] is not None:
            continue
        if index < len(glosses) and _is_reduplication(glosses[index][0]):
            fixed[index] = Attachment.REDUPLICATION
            tentative[index] = False

    # 3a 的特例:整個詞只有一個詞素(沒有切割符號),那個詞素就是詞根。
    # 詞綴要有東西可黏才成立,沒有黏的時候查得到清單也不能算詞綴——
    # 不然 `a`/連繫詞、`ta`/斜格 這種單詞都會被判成「無法判斷」。
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

    # 3b、3c:只有一個詞素沒標,才判得出詞根。
    if len(roots) != 1:
        return _assign_without_root(forms, fixed, roots)

    return _assign(forms, fixed, roots[0])


def _stem_of(forms):
    """詞幹每個詞素的位置和它前面那個分界符號(中綴不算在內)。"""
    stem = []
    separators = []
    for index, (form, mark) in enumerate(forms):
        if mark == INFIX_MARK:
            continue
        stem.append(index)
        separators.append(mark)
    return stem, separators


def _assign_without_root(forms, fixed, roots):
    """詞根分不出來的時候(3b、3c)每個詞素要怎麼記。

    第 1 步就認出來的(中綴、環綴、重疊)不受詞根影響,照留。
    剩下的詞綴,如果對每一個可能的詞根位置都判成一樣,那個詞素仍然
    判得出來——像 Tala-likor-ay=to 的 -ay 和 =to,不論詞根是 Tala 還是
    likor,都在詞根的右邊,所以是後綴和依附詞。判成不一樣的,才
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
    """第 2 步:照詞根的位置決定其餘每個詞素是什麼構詞。"""
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
    """index 和 root 之間跨過的符號,決定構詞(判斷方法 2a-2d)。"""
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
    也呼叫這一支。詞素切割與詞素翻譯切出來的詞素數不一樣的時候（像
    拉長音的 `ung~`），分不出詞素，整個 token 算一個「無法判斷」。
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
    """把一段拆成詞與詞素。前提是 token 數與符號都對得起來。"""
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


def validate(entry):
    """驗證一段，回傳問題清單。

    只檢查詞素切割行與詞素翻譯行對不對得起來。構詞判定已經暫停
    （2026.09 會議決議不需要構詞資訊），所以這裡不判構詞；判定的
    函式留給 features/構詞判定.feature 的草稿用。
    """
    return check_entry_correspondence(entry)
