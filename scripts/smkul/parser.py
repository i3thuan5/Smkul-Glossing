"""語料的 parser：把 docx 切成一組一組的標註。

規格寫在 features/字元正規化.feature、features/排版分析.feature、
features/時間碼.feature、features/原文切分比對.feature。
"""

import dataclasses
import difflib
import re
from collections import OrderedDict

from scripts.smkul.docx2text import docx_text
from scripts.smkul.entry import (
    CorpusFile,
    code,
    Entry,
    Issue,
    IssueKind,
    NormKind,
)

# 時間碼:時:分:秒,毫秒用 . 或 , 分隔,也有沒有毫秒的。
_STAMP = r'\d{1,2}:\d\d:\d\d(?:[.,]\d+)?'
NUM_TIME = re.compile(
    r'^\s*(?:(\d+)[.]?\s+)?'
    r'(' + _STAMP + r')'
    r'\s*(-->|[–—,-])\s*'
    r'(' + _STAMP + r')\s*$'
)
NUM_ONLY = re.compile(r'^\s*(\d+)[.]?\s*$')

# 分隔符 → 格式名。光看分隔符就能分出四種格式。
SEPARATOR_NAME = {
    "-->": "SRT 式",
    ",": "逗號式",
    "–": "en-dash 式",
    "—": "en-dash 式",
    "-": "連字號式",
}
# 連字號式沒有毫秒,單位問題要跟對方確認。
UNCLEAR_UNIT_FORMAT = "連字號式"

BOM = "\ufeff"


def timecode_parts(value):
    """時間碼拆做數字,通好比較先後。同一逝的開始佮結束一定同款格式,
    所以照欄位比就會準,免管單位是啥物。"""
    out = []
    for chunk in re.split(r'[:.,]', value):
        if chunk.isdigit():
            out.append(int(chunk))
    return tuple(out)


def _fix_chars(line, log=None, path="", number=""):
    """全形＝換半形、彎引號統一成 U+0027。"""
    fixed = line
    if "＝" in fixed:
        changed = fixed.replace("＝", "=")
        if log is not None:
            log.note(
                NormKind.FULLWIDTH_EQUALS, fixed.strip(),
                changed.strip(), path, number,
            )
        fixed = changed
    if "\u2019" in fixed or "\u2018" in fixed:
        changed = fixed.replace("\u2019", "'").replace("\u2018", "'")
        if log is not None:
            log.note(
                NormKind.APOSTROPHE, fixed.strip(), changed.strip(),
                path, number,
            )
        fixed = changed
    return fixed


def normalize_line(line, log=None, path="", number=""):
    """單行的字元正規化：BOM、全形＝、引號、en-dash、多餘空白。

    這是 features/字元正規化.feature 的入口，也是四行內容用的同一支。
    時間碼行不可以走這裡——en-dash 是時間碼的合法分隔符號。切組
    （parse_timecode）先做，四行的內容才正規化，見 assemble_entry。
    """
    fixed = line
    if fixed.startswith(BOM):
        fixed = fixed[len(BOM):]
        if log is not None:
            log.note(NormKind.BOM, line.strip(), fixed.strip(), path, number)
    fixed = _fix_chars(fixed, log, path, number)
    fixed = normalize_en_dash(fixed, log, path, number)
    return collapse_spaces(fixed)


def normalize_text(text, log=None, path=""):
    """檔案層的正規化:BOM、全形＝、引號。逐行做，才留會著真正的例。

    這一層不換 en-dash、不摺疊空白——切組要先認出時間碼行，
    而排版分析要看得到原本的行。那兩項在 normalize_line。
    """
    if text.startswith(BOM):
        text = text[len(BOM):]
        if log is not None:
            first = text.split("\n", 1)[0].strip()
            log.note(NormKind.BOM, BOM + first, first, path)
    out = []
    for line in text.split("\n"):
        out.append(_fix_chars(line, log, path))
    return "\n".join(out)


def normalize_en_dash(line, log=None, path="", number=""):
    """切分行、gloss 行的 en-dash 換成半形。時間碼行不能用這個。"""
    if "–" not in line and "—" not in line:
        return line
    fixed = line.replace("–", "-").replace("—", "-")
    if log is not None:
        log.note(NormKind.EN_DASH, line.strip(), fixed.strip(), path, number)
    return fixed


def parse_timecode(line):
    """解析時間碼行，回傳 (編號， 開始， 結束， 格式名);不是時間碼回傳 None。"""
    matched = NUM_TIME.match(line)
    if matched is None:
        return None
    number = matched.group(1) or ""
    return (
        number,
        matched.group(2),
        matched.group(4),
        SEPARATOR_NAME[matched.group(3)],
    )


def _entry_starts(lines):
    """找出每一組的起頭。回傳 [(起始 index, 時間碼 index, 解析結果)]。"""
    out = []
    for index, line in enumerate(lines):
        parsed = parse_timecode(line)
        if parsed is None:
            continue
        back = index - 1
        while back >= 0 and not lines[back].strip():
            back -= 1
        number_match = None
        if back >= 0:
            number_match = NUM_ONLY.match(lines[back])
        if number_match is not None and not parsed[0]:
            parsed = (number_match.group(1),) + parsed[1:]
            out.append((back, index, parsed))
        else:
            out.append((index, index, parsed))
    return out


def split_entries(text, path="", log=None):
    """把正規化過的全文切成:(檔頭註記， [Entry], 檔案層問題)。"""
    lines = text.splitlines()
    starts = _entry_starts(lines)
    header = []
    if starts:
        limit = starts[0][0]
    else:
        limit = len(lines)
    for line in lines[:limit]:
        if line.strip():
            header.append(line.strip())
            if log is not None:
                log.note(
                    NormKind.HEADER_NOTE, line.strip(),
                    "收進檔頭註記 metadata", path,
                )

    entries = []
    issues = []
    formats = OrderedDict()
    for order, (begin, time_index, parsed) in enumerate(starts):
        number, start, end, fmt = parsed
        if fmt not in formats:
            formats[fmt] = lines[time_index].strip()
        if order + 1 < len(starts):
            stop = starts[order + 1][0]
        else:
            stop = len(lines)
        body = []
        for line in lines[time_index + 1:stop]:
            if line.strip():
                body.append(line)
        entry = Entry(
            number=number, start=start, end=end, path=path, body=body,
        )
        if log is not None:
            log.note(
                NormKind.TIMECODE_SPLIT, lines[time_index].strip(),
                "開始 " + start + " / 結束 " + end, path, number,
            )
        if not number:
            entry.issues.append(
                Issue(
                    IssueKind.ORPHAN_TIMECODE, path, "",
                    "時間碼 " + code(lines[time_index].strip()) +
                    " 沒有編號也沒有內文",
                )
            )
        if timecode_parts(end) < timecode_parts(start):
            entry.issues.append(
                Issue(
                    IssueKind.REVERSED_TIMECODE, path, number,
                    "結束時間比開始還早",
                    [("開始", start), ("結束", end)],
                )
            )
        if order + 1 < len(starts) and stop - 1 >= 0:
            if lines[stop - 1].strip() and log is not None:
                log.note(
                    NormKind.MISSING_BLANK_LINE,
                    lines[stop - 1].strip() + " ⏎ " +
                    lines[stop].strip(),
                    "視為兩組，不依賴空行", path, number,
                )
        entries.append(entry)

    if len(formats) > 1:
        issues.append(
            Issue(
                IssueKind.MIXED_TIMECODE_FORMAT, path, "",
                "同一個檔案用了 " + "、".join(sorted(formats)),
            )
        )
    if UNCLEAR_UNIT_FORMAT in formats:
        issues.append(
            Issue(
                IssueKind.UNKNOWN_TIMECODE_UNIT, path, "",
                "連字號式時間碼沒有毫秒，單位不明，需要跟對方確認"
            )
        )
    return header, entries, issues, formats


def parse_text(text, path="", ethnic="", variant="", log=None):
    """由原始全文建立一個 CorpusFile。"""
    text = normalize_text(text, log, path)
    header, entries, issues, formats = split_entries(text, path, log)
    return CorpusFile(
        path=path,
        ethnic=ethnic,
        variant=variant,
        header_notes=header,
        entries=entries,
        issues=issues,
        timecode_formats=formats,
    )


def _count_kinds(line):
    """計算一行裡面有多少拉丁字母與漢字。"""
    latin = 0
    han = 0
    for char in line:
        if "a" <= char <= "z":
            latin += 1
        elif "一" <= char <= "鿿":
            han += 1
    return latin, han


def line_kind(line):
    """一行是「拉丁」(原文、切分)抑是「漢字」(gloss、翻譯)。

    比較ê是小寫拉丁字母佮漢字ê數量,大寫無算——看 _count_kinds。
    """
    latin, han = _count_kinds(line)
    if latin == 0 and han == 0:
        return "空"
    if latin >= han:
        return "拉丁"
    return "漢字"


def collapse_spaces(line):
    """語料用寬空白排列欄位，切 token 時視為單一分隔。"""
    return " ".join(line.split())


def bare_form(text):
    """保留字母、漢字、數字、單引號;空白、標點、切分符號都去掉。

    單引號(喉塞音)是音位，不能去掉——排灣語 ODS 1-3 規定切分要跟著
    原文的寫法。大小寫不計(切分常把專有名詞寫成大寫)。
    """
    out = []
    for char in text.lower():
        if "a" <= char <= "z":
            out.append(char)
        elif "一" <= char <= "鿿" or char.isdigit():
            out.append(char)
        elif char in "'\u2019\u2018":
            out.append("'")
    return "".join(out)


# 原文與切分不符的細分。差一個字母與差一整段,要處理的方式不一樣。
MISMATCH_WORDS = "詞數不同"
MISMATCH_APOSTROPHE = "只差單引號"
MISMATCH_ONE = "只差一個字母"
MISMATCH_FEW = "差 2-3 個字母"
MISMATCH_MANY = "多處不同"
MISMATCH_LENGTH = "長度差很多"

MISMATCH_WHY = OrderedDict()
MISMATCH_WHY[MISMATCH_WORDS] = (
    "字母序列一樣，可是詞的個數不一樣——原文黏成一個詞、切分拆開"
    "(或相反)。依照「詞數要一個對一個、只有依附詞例外」，這種算不符。"
)
MISMATCH_WHY[MISMATCH_APOSTROPHE] = (
    "只有喉塞音單引號的有無或位置不同。排灣語 ODS 1-3 規定切分的 "
    "[k] / ['] 要跟著原文的寫法，所以這一類多半是要決定哪一邊才對。"
)
MISMATCH_WHY[MISMATCH_ONE] = (
    "只差一個字母，多半是切分時多打或漏打一個音，或是照發音改寫了拼法。"
)
MISMATCH_WHY[MISMATCH_FEW] = "差 2-3 個字母，通常是拼法慣例不同。"
MISMATCH_WHY[MISMATCH_MANY] = (
    "差很多個字母，可能是換了詞、或原文與切分不是同一句。"
)
MISMATCH_WHY[MISMATCH_LENGTH] = (
    "長度差四分之一以上，通常是切分比原文少了一整段(或多了一整段)，"
    "內容可能遺失。"
)

# 差幾個字母算「少少仔」,超過就算多處不同。
FEW_LIMIT = 3
# 長度差這个比例以上,就當做少了一整段。
LENGTH_RATIO = 0.25


def _diff_ops(one, other):
    ops = []
    for op in difflib.SequenceMatcher(None, one, other).get_opcodes():
        if op[0] != "equal":
            ops.append(op)
    return ops


def _mismatch_detail(source, segmentation):
    """原文與切分差在哪裡，寫成短短一句，例如 `pai` → `pay`。"""
    one = bare_form(source)
    other = bare_form(segmentation)
    parts = []
    for tag, i1, i2, j1, j2 in _diff_ops(one, other)[:3]:
        left = one[i1:i2]
        right = other[j1:j2]
        if not left:
            parts.append("切分多了「" + right + "」")
        elif not right:
            parts.append("切分少了「" + left + "」")
        else:
            parts.append("「" + left + "」→「" + right + "」")
    return "、".join(parts)


def _word_counts_fit(source, segmentation):
    """原文ê詞數佮切分ê詞數敢對會起來。

    一个切分 token 內底ê = 會共原文ê幾若个詞併做一个(awa to →
    awa=to),所以一个 token 上濟食(1 + = ê個數)个原文詞。
    """
    source_words = 0
    for token in source.split():
        if bare_form(token):
            source_words += 1
    least = 0
    most = 0
    for token in segmentation.split():
        if not bare_form(token):
            continue
        least += 1
        most += 1 + token.count("=")
    if least == 0:
        return True
    return least <= source_words <= most


def _matches(source, segmentation):
    """原文佮切分敢對會起來:逐字仝款,而且詞數嘛對會起來。"""
    if bare_form(source) != bare_form(segmentation):
        return False
    return _word_counts_fit(source, segmentation)


def _mismatch_kind(source, segmentation):
    """把「原文與切分不符」再分類，才知道要怎麼處理。"""
    one = bare_form(source)
    other = bare_form(segmentation)
    if one == other:
        return MISMATCH_WORDS
    ops = _diff_ops(one, other)
    changed = 0
    only_apostrophe = True
    for tag, i1, i2, j1, j2 in ops:
        changed += max(i2 - i1, j2 - j1)
        if set(one[i1:i2]) - {"'"} or set(other[j1:j2]) - {"'"}:
            only_apostrophe = False
    if only_apostrophe:
        return MISMATCH_APOSTROPHE
    longest = max(len(one), len(other))
    if abs(len(one) - len(other)) >= longest * LENGTH_RATIO:
        return MISMATCH_LENGTH
    if changed == 1:
        return MISMATCH_ONE
    if changed <= FEW_LIMIT:
        return MISMATCH_FEW
    return MISMATCH_MANY


# 句讀。原文保留、切分照慣例不留,這種差異不算錯,但要提出來討論。
PUNCTUATION = ",.?!;:，。、？！；：「」\"“”()（）…"


def _punctuation_of(text):
    """把一行裡面的句讀照順序抽出來。"""
    out = []
    for char in text:
        if char in PUNCTUATION:
            out.append(char)
    return "".join(out)


@dataclasses.dataclass
class SourceCheck:
    """原文與切分逐字比對的結果。

    規格寫在 features/原文切分比對.feature：
    passed 是通過與否，kind 是不通過的分類（通過時是 None），
    detail 是差在哪裡的一句話，punctuation_differs 是標點有沒有差。
    標點差異不影響 passed——那是另外記一筆的 warning。
    """

    passed: bool
    kind: object = None
    detail: str = ""
    punctuation_differs: bool = False


def compare_source(source, segmentation):
    """原文與切分逐字比對，回傳 SourceCheck。

    這是 features/原文切分比對.feature 的入口，assemble_entry 也用
    同一支產生「原文與切分不符」與「標點不同」兩種問題。
    """
    通過 = _matches(source, segmentation)
    分類 = None
    if not 通過:
        分類 = _mismatch_kind(source, segmentation)
    return SourceCheck(
        passed=通過,
        kind=分類,
        detail=_mismatch_detail(source, segmentation),
        punctuation_differs=(
            _punctuation_of(source) != _punctuation_of(segmentation)),
    )


# 切分的字數比原文多這麼多,就不是換行,而是同一句標了兩版。
DUPLICATE_RATIO = 1.5


def _is_duplicate(source_line, joined_segments):
    """比對原文與重組後的切分，判斷是換行還是重複標註。"""
    source = bare_form(source_line)
    if not source:
        return False
    return len(bare_form(joined_segments)) / len(source) >= DUPLICATE_RATIO


def assemble_entry(entry, log=None):
    """把 body 組成四行。組得起來回傳 True，組不起來回傳 False。

    標準排法是:原文 +(切分， gloss)× n + 翻譯。四行組是 n=1,
    長句分段是 n>1。中間的行要「拉丁、漢字」相間才組得起來。
    """
    body = entry.body
    if len(body) < 3:
        return False
    middle = body[1:-1]
    if len(middle) % 2 != 0:
        return False
    # 排版分析這一步只管切組佮四行對位,無管內容是族語抑是華語。
    # 規組攏是華語ê時陣揣無拉丁行,照位置排就好,袂當因為按呢
    # 就講伊組袂起來——「整組華語就毋做切分分析」是後一步ê代誌。
    kinds = []
    for line in body:
        kinds.append(line_kind(line))
    if not _all_han(kinds):
        for index, line in enumerate(middle):
            kind = line_kind(line)
            if index % 2 == 0:
                if kind != "拉丁":
                    return False
            elif kind != "漢字":
                return False

    segments = []
    glosses = []
    for index, line in enumerate(middle):
        fixed = normalize_line(line, log, entry.path, entry.number)
        if index % 2 == 0:
            segments.append(fixed)
        else:
            glosses.append(fixed)

    joined = " ".join(segments)
    if len(segments) > 1 and _is_duplicate(body[0], joined):
        entry.issues.append(
            Issue(
                IssueKind.DUPLICATE_ANNOTATION, entry.path, entry.number,
                "原文只有一句，切分卻有 " + str(len(segments)) + " 版",
                [
                    ("原文", collapse_spaces(body[0])),
                    ("切分", " ⏎ ".join(segments)),
                ],
            )
        )
        return False

    entry.source = collapse_spaces(body[0])
    entry.segmentation = joined
    entry.gloss = " ".join(glosses)
    entry.translation = collapse_spaces(body[-1])
    比對 = compare_source(entry.source, entry.segmentation)
    if 比對.punctuation_differs:
        entry.issues.append(
            Issue(
                IssueKind.PUNCTUATION_DIFF, entry.path, entry.number,
                "原文與切分的標點不同(不擋匯出)",
                [("原文", entry.source), ("切分", entry.segmentation)],
            )
        )
    if not 比對.passed:
        entry.issues.append(
            Issue(
                IssueKind.SOURCE_SEGMENT_MISMATCH, entry.path,
                entry.number,
                比對.kind + ":" + 比對.detail,
                [("原文", entry.source), ("切分", entry.segmentation)],
            )
        )
    if log is not None:
        if len(middle) > 2:
            log.note(
                NormKind.LONG_ENTRY_REJOIN,
                " ⏎ ".join(segments),
                entry.segmentation,
                entry.path, entry.number,
            )
        if _has_wide_space(body):
            log.note(
                NormKind.WHITESPACE, _wide_line(body).strip(),
                collapse_spaces(_wide_line(body)),
                entry.path, entry.number,
            )
    return True


# 干焦數字、標點這款,毋是語料嘛毋是註記ê行(例如 0000、136.6)。
NOISE = re.compile(r'^[\d.\-–—:,()（）\s]+$')

# gloss 行尾若有句讀,誠有可能是華語翻譯黏tī後壁。
SENTENCE_MARKS = "，。、？！；：,.?!;"


def _kinds_of(body):
    out = []
    for line in body:
        out.append(line_kind(line))
    return out


def _has_noise(body):
    for line in body:
        if NOISE.match(line.strip()):
            return line.strip()
    return ""


def _all_han(kinds):
    for kind in kinds:
        if kind != "漢字":
            return False
    return len(kinds) > 0


def _alternation_broken(middle):
    """中間的行是否沒有照「拉丁、漢字」相間。"""
    for index, line in enumerate(middle):
        kind = line_kind(line)
        if index % 2 == 0:
            if kind != "拉丁":
                return True
        elif kind != "漢字":
            return True
    return False


def _looks_glued(line):
    """gloss 行尾是否黏著華語翻譯:看有沒有句讀。"""
    for mark in SENTENCE_MARKS:
        if mark in line:
            return True
    return False


def classify_entry(entry):
    """組不起來的組，判斷是哪一種結構異常。回傳 IssueKind 或 None。"""
    body = entry.body
    if not body:
        # 沒有編號的,split_entries 已經記為孤兒時間碼了。
        if entry.number:
            return IssueKind.EMPTY_ENTRY
        return None
    noise = _has_noise(body)
    if noise:
        return IssueKind.STRAY_LINE
    kinds = _kinds_of(body)
    if _all_han(kinds):
        return IssueKind.CHINESE_ONLY
    if len(body) == 3 and kinds == ["拉丁", "拉丁", "漢字"]:
        if _looks_glued(body[2]):
            return IssueKind.GLUED_LINE
        return IssueKind.MISSING_TRANSLATION
    middle = body[1:-1]
    if _alternation_broken(middle):
        return IssueKind.GLUED_LINE
    if len(middle) % 2 != 0:
        return IssueKind.MISSING_GLOSS_SEGMENT
    return IssueKind.GLUED_LINE


DETAIL = {
    IssueKind.EMPTY_ENTRY: "只有編號與時間碼，沒有內文",
    IssueKind.STRAY_LINE: "組內有無法歸類的雜訊行",
    IssueKind.CHINESE_ONLY: "整組都是華語，沒有族語標註",
    IssueKind.MISSING_TRANSLATION: "沒有第四行華語翻譯",
    IssueKind.GLUED_LINE: "有兩行黏在一起",
    IssueKind.MISSING_GLOSS_SEGMENT: "有一段切分沒有對應的 gloss",
}


def _has_wide_space(body):
    for line in body:
        if "  " in line or "\t" in line:
            return True
    return False


def _wide_line(body):
    for line in body:
        if "  " in line or "\t" in line:
            return line
    return body[0]


def build_entry(entry, log=None):
    """組四行;組袂起來就分類異常。回傳敢組會起來。"""
    if assemble_entry(entry, log):
        # 排版分析(組四行)佮內容判斷是兩步。規組攏是華語ê嘛組會
        # 起來,毋過袂使匯出,所以組好了後閣記一筆「純華語句」。
        if _all_han(_kinds_of(entry.body)):
            entry.issues.append(
                Issue(
                    IssueKind.CHINESE_ONLY, entry.path, entry.number,
                    DETAIL.get(IssueKind.CHINESE_ONLY, ""),
                    [("內文", " ⏎ ".join(entry.body))],
                )
            )
        return True
    for issue in entry.issues:
        if issue.kind is IssueKind.DUPLICATE_ANNOTATION:
            return False
    kind = classify_entry(entry)
    if kind is not None:
        detail = DETAIL.get(kind, "")
        if kind is IssueKind.STRAY_LINE:
            detail = detail + ":" + code(_has_noise(entry.body))
        entry.issues.append(
            Issue(
                kind, entry.path, entry.number, detail,
                [("內文", " ⏎ ".join(entry.body))],
            )
        )
    return False


def parse_corpus_file(path, rel_path, ethnic="", variant="", log=None):
    """讀一个 docx，轉做 CorpusFile(已經組四行、已經分類)。

    語料ê來源是 docx。審閱註解tī word/comments.xml,抽內文ê時
    本底就袂濫入來,所以無註解殘留通清——看
    openspec/specs/corpus-parsing 的「語料來源為 docx」。
    """
    corpus = parse_text(
        docx_text(path), path=rel_path, ethnic=ethnic,
        variant=variant, log=log,
    )
    for entry in corpus.entries:
        build_entry(entry, log)
    return corpus
