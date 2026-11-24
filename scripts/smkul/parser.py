"""語料的 parser：把 docx 切成一段一段的標註。

規格寫在 features/字元正規化.feature、features/排版分析.feature、
features/時間碼.feature、features/族語原句詞素切割比對.feature。
"""

import dataclasses
import difflib
import re
from collections import OrderedDict

from scripts.smkul.docx2text import docx_text
from scripts.smkul.entry import (
    MISMATCH_PREFIX,
    CorpusFile,
    code,
    Entry,
    is_mismatch,
    Issue,
    IssueKind,
    NO_TIME,
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

# 分隔符 → 格式名。規格見 features/時間碼.feature。
SEPARATOR_NAME = {
    "-->": "SRT 式",
    ",": "逗號式",
    "–": "en-dash 式",
    "—": "en-dash 式",
    "-": "連字號式",
}
# 用 --> 分開、毫秒卻用小數點的(南排灣 3),跟 SRT 式分開算檔數。
ARROW_DOT_FORMAT = "--> 配小數點"
# 連字號式沒有毫秒,照 分:秒:影格 換算;30fps 是推斷的,要跟對方確認。
UNCLEAR_UNIT_FORMAT = "連字號式"
FRAMES_PER_SECOND = 30
# 有「數字:數字」的樣子。編號行的下一行有這個樣子、卻解析不了,
# 就是時間碼行打錯。
TIMECODE_LIKE = re.compile(r'\d\s*[:;]\s*\d')

# GLOTTAL:喉塞音一律用 U+02BC;語料裡的 U+0027、U+2018、U+2019 也算喉塞音。

BOM = "\ufeff"
GLOTTAL = "\u02bc"
QUOTES = "'\u2018\u2019" + GLOTTAL


def timecode_milliseconds(stamp, fmt):
    """時間碼原字串換成總毫秒數;毫秒不是三位數就回傳 None。

    連字號式是 分:秒:影格(30fps),影格用整數四捨五入成毫秒
    (不用 round,round 遇到 .5 會捨入成偶數)。其他格式是 時:分:秒 加毫秒。
    """
    parts = re.split(r'[:.,]', stamp)
    if fmt == UNCLEAR_UNIT_FORMAT and len(parts) == 3:
        minutes, seconds, frames = int(parts[0]), int(parts[1]), int(parts[2])
        half = FRAMES_PER_SECOND // 2
        frame_ms = (frames * 1000 + half) // FRAMES_PER_SECOND
        return minutes * 60000 + seconds * 1000 + frame_ms
    if len(parts) != 4 or len(parts[3]) != 3:
        return None
    hours, minutes, seconds = int(parts[0]), int(parts[1]), int(parts[2])
    return (hours * 3600 + minutes * 60 + seconds) * 1000 + int(parts[3])


def srt_string(milliseconds):
    """總毫秒數換成 SRT 字串 HH:MM:SS,mmm。"""
    hours, rest = divmod(milliseconds, 3600000)
    minutes, rest = divmod(rest, 60000)
    seconds, rest = divmod(rest, 1000)
    return "%02d:%02d:%02d,%03d" % (hours, minutes, seconds, rest)


def convert_timecode(start, end, fmt):
    """開始、結束的原字串轉成 SRT 字串。回傳 (開始, 結束, 問題種類)。

    時間不能用的,開始、結束都是 NO_TIME,問題種類是毫秒位數不對或
    結束時間早於開始;沒問題的問題種類是 None。
    毫秒位數不對就不比先後:毫秒讀不準,先後也比不準。
    """
    begin = timecode_milliseconds(start, fmt)
    finish = timecode_milliseconds(end, fmt)
    if begin is None or finish is None:
        return NO_TIME, NO_TIME, IssueKind.TIMECODE_MS_DIGITS
    if finish < begin:
        return NO_TIME, NO_TIME, IssueKind.REVERSED_TIMECODE
    return srt_string(begin), srt_string(finish), None


def _char_at(line, index):
    """line 的第 index 個字;超出範圍當成空白(行頭、行尾)。"""
    if 0 <= index < len(line):
        return line[index]
    return " "


def is_quotation(line, index):
    """line 第 index 個字的引號是引用符號(不是喉塞音)嗎?

    規格見 features/字元正規化.feature「當引用符號用的引號不轉」:
    一、兩個 ‘ 連在一起;二、兩個引號連在一起,接在字母後面、後面不是
    字母(雙引號的結尾);三、緊接在 ! ? 後面;四、單獨一個,前後都是空白。
    """
    char = line[index]
    before = _char_at(line, index - 1)
    after = _char_at(line, index + 1)
    if char == "‘" and (before == char or after == char):
        return True
    if after in QUOTES and before.isalpha() and \
            not _char_at(line, index + 2).isalpha():
        return True
    if before in QUOTES and _char_at(line, index - 2).isalpha() and \
            not after.isalpha():
        return True
    if before in "!?":
        return True
    return before.isspace() and after.isspace()


def unify_quotes(line):
    """引號 U+0027、U+2018、U+2019 統一成 U+02BC,引用符號不轉。"""
    out = []
    for index, char in enumerate(line):
        if char in QUOTES and char != GLOTTAL and \
                not is_quotation(line, index):
            out.append(GLOTTAL)
        else:
            out.append(char)
    return "".join(out)


def _fix_chars(line, log=None, path="", number=""):
    """全形＝換半形、引號統一成 U+02BC。"""
    fixed = line
    if "＝" in fixed:
        changed = fixed.replace("＝", "=")
        if log is not None:
            log.note(
                NormKind.FULLWIDTH_EQUALS, fixed.strip(),
                changed.strip(), path, number,
            )
        fixed = changed
    changed = unify_quotes(fixed)
    if changed != fixed:
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
    時間碼行不可以走這裡——en-dash 是時間碼的合法分隔符號。切段
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
    """檔案層的正規化:BOM、全形＝、引號。逐行做，才留得下真正的例子。

    這一層不換 en-dash、不摺疊空白——切段要先認出時間碼行，
    而排版分析要看得到原本的行。那兩項在 normalize_line。
    """
    out = []
    for line in text.split("\n"):
        # BOM 不一定在全文最前面:docx 第一段時間碼行的最前面也有
        # (檔頭與編號行在它前面)。BOM 擋住時間碼,第一段就會被當成檔頭。
        if line.startswith(BOM):
            line = line[len(BOM):]
            if log is not None:
                log.note(NormKind.BOM, BOM + line.strip(), line.strip(), path)
        out.append(_fix_chars(line, log, path))
    return "\n".join(out)


def normalize_en_dash(line, log=None, path="", number=""):
    """詞素切割行、詞素翻譯行的 en-dash 換成半形。時間碼行不能用這個。"""
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
    fmt = SEPARATOR_NAME[matched.group(3)]
    if matched.group(3) == "-->" and "." in matched.group(2):
        fmt = ARROW_DOT_FORMAT
    return (
        number,
        matched.group(2),
        matched.group(4),
        fmt,
    )


def _entry_starts(lines):
    """找出每一段的起頭。回傳 [(起始 index, 時間碼 index, 解析結果)]。

    編號行的下一行有「數字:數字」的樣子、卻解析不了,是時間碼行打錯:
    照樣當成段的起頭,解析結果是 (編號, 原字串, "", None),格式是 None。
    規格見 features/時間碼.feature「編號行的下一行看起來是時間碼…」。
    """
    out = []
    for index, line in enumerate(lines):
        parsed = parse_timecode(line)
        if parsed is None and not TIMECODE_LIKE.search(line):
            continue
        back = index - 1
        while back >= 0 and not lines[back].strip():
            back -= 1
        number_match = None
        if back >= 0:
            number_match = NUM_ONLY.match(lines[back])
        if parsed is None:
            if number_match is not None:
                typo = (number_match.group(1), line.strip(), "", None)
                out.append((back, index, typo))
            continue
        if number_match is not None and not parsed[0]:
            parsed = (number_match.group(1),) + parsed[1:]
            out.append((back, index, parsed))
        else:
            out.append((index, index, parsed))
    return out


# 說話者標記:1 到 3 個字母加冒號,例如 Y:、Lj:、Yu:。
# 規格見 features/排版分析.feature 的「對話段」與「同一組，有2個發音人」。
SPEAKER_START = re.compile(r"^\s*([A-Za-z]{1,3})[:：]")
SPEAKER_INLINE = re.compile(r"(?:^|(?<=\s))([A-Za-z]{1,3})[:：]")
# 一套標註的行數:族語原句、詞素切割、詞素翻譯、華語翻譯。
LINES_PER_SET = 4
OPENING = "(（"
CLOSING = ")）"


def _speaker_of(line):
    """行頭的說話者標記(小寫);沒有就是空字串。"""
    found = SPEAKER_START.match(line)
    if found is None:
        return ""
    return found.group(1).lower()


def _dialogue_bodies(body):
    """對話段:每一行都有說話者標記,一位說話者一套四行,切成好幾套。"""
    if len(body) < 2 * LINES_PER_SET or len(body) % LINES_PER_SET:
        return None
    sets = []
    for begin in range(0, len(body), LINES_PER_SET):
        names = set()
        for line in body[begin:begin + LINES_PER_SET]:
            names.add(_speaker_of(line))
        if len(names) != 1 or "" in names:
            return None
        sets.append(body[begin:begin + LINES_PER_SET])
    for index in range(1, len(sets)):
        if _speaker_of(sets[index][0]) == _speaker_of(sets[index - 1][0]):
            return None
    return sets


def _speaker_groups(middle):
    """詞素切割、詞素翻譯照說話者分組:[(說話者, [行])]。

    每一對(詞素切割、詞素翻譯)都要有同一個說話者標記;同一位說話者
    連著的幾對是長句換行,算同一組。不到兩組就不是兩位發音人。
    """
    if len(middle) < 4 or len(middle) % 2:
        return None
    groups = []
    for index in range(0, len(middle), 2):
        name = _speaker_of(middle[index])
        if not name or _speaker_of(middle[index + 1]) != name:
            return None
        if groups and groups[-1][0] == name:
            groups[-1][1].append(middle[index])
            groups[-1][1].append(middle[index + 1])
        else:
            groups.append((name, [middle[index], middle[index + 1]]))
    if len(groups) < 2:
        return None
    return groups


def _split_by_marks(line, names):
    """照行內的說話者標記切開,標記留著。標記的順序要跟分組一樣。"""
    found = []
    marks = []
    for match in SPEAKER_INLINE.finditer(line):
        found.append(match)
        marks.append(match.group(1).lower())
    if marks != names or line[:found[0].start()].strip():
        return None
    parts = []
    for index, match in enumerate(found):
        stop = len(line)
        if index + 1 < len(found):
            stop = found[index + 1].start()
        part = line[match.start():stop].strip()
        if not part[len(match.group(0)):].strip():
            return None
        parts.append(part)
    return parts


def _split_by_brackets(line):
    """沒有說話者標記的行:括號裡的一截、括號外的一截,照順序切開。"""
    parts = []
    current = ""
    depth = 0
    for char in line:
        if char in OPENING and depth == 0:
            if current.strip():
                parts.append(current.strip())
            current = char
            depth = 1
        elif char in OPENING:
            current += char
            depth += 1
        elif char in CLOSING and depth > 0:
            current += char
            depth -= 1
            if depth == 0:
                parts.append(current.strip())
                current = ""
        else:
            current += char
    if current.strip():
        parts.append(current.strip())
    return parts


def _split_line(line, names):
    """族語原句或華語翻譯切成跟分組一樣多份;切不成就是 None。"""
    if SPEAKER_INLINE.search(line):
        return _split_by_marks(line, names)
    parts = _split_by_brackets(line)
    if len(parts) != len(names):
        return None
    return parts


def _speaker_bodies(body):
    """兩位說話者的段切成好幾段的內文;不是這種排法或切不成就是 None。

    對話段:一位說話者一套四行。兩位發音人一組:族語原句、華語翻譯各一行,
    詞素切割與詞素翻譯照說話者分組;族語原句、華語翻譯有說話者標記就照
    標記切,沒有的照括號切(括號裡是前一位說話者的話)。份數對不起來的
    整段不切,留給 classify_entry 判成「行黏在一起」。
    """
    sets = _dialogue_bodies(body)
    if sets is not None:
        return sets
    if len(body) < 6:
        return None
    groups = _speaker_groups(body[1:-1])
    if groups is None:
        return None
    names = []
    for name, lines in groups:
        names.append(name)
    sources = _split_line(body[0], names)
    translations = _split_line(body[-1], names)
    if sources is None or translations is None:
        return None
    out = []
    for index, (name, lines) in enumerate(groups):
        part = [sources[index]]
        for line in lines:
            part.append(line)
        part.append(translations[index])
        out.append(part)
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
        number, raw_start, raw_end, fmt = parsed
        raw_line = lines[time_index].strip()
        if fmt is None:
            start, end, problem = NO_TIME, NO_TIME, IssueKind.TIMECODE_TYPO
        else:
            if fmt not in formats:
                formats[fmt] = raw_line
            start, end, problem = convert_timecode(raw_start, raw_end, fmt)
        if order + 1 < len(starts):
            stop = starts[order + 1][0]
        else:
            stop = len(lines)
        body = []
        for line in lines[time_index + 1:stop]:
            if line.strip():
                body.append(line)
        # 兩位說話者的段照說話者切成好幾段,段號加 -1、-2。
        parts = None
        if number:
            parts = _speaker_bodies(body)
        if parts is None:
            parts = [body]
        part_entries = []
        for part_index, part in enumerate(parts):
            part_number = number
            if len(parts) > 1:
                part_number = number + "-" + str(part_index + 1)
            part_entries.append(Entry(
                number=part_number, start=start, end=end, path=path,
                body=part,
            ))
        # 時間碼的問題記在第一段,不要每一段各記一次。
        entry = part_entries[0]
        number = entry.number
        if log is not None:
            log.note(
                NormKind.TIMECODE_SPLIT, raw_line,
                "開始 " + str(start) + " / 結束 " + str(end), path, number,
            )
        if not number:
            entry.issues.append(
                Issue(
                    IssueKind.ORPHAN_TIMECODE, path, "",
                    "時間碼 " + code(raw_line) + " 沒有編號也沒有內文",
                )
            )
        if problem is IssueKind.REVERSED_TIMECODE:
            entry.issues.append(
                Issue(
                    problem, path, number, "結束時間比開始還早",
                    [("開始", raw_start), ("結束", raw_end)],
                )
            )
        elif problem is IssueKind.TIMECODE_MS_DIGITS:
            entry.issues.append(
                Issue(
                    problem, path, number,
                    "時間碼 " + code(raw_line) + " 的毫秒只有一位或兩位數",
                )
            )
        elif problem is IssueKind.TIMECODE_TYPO:
            entry.issues.append(
                Issue(
                    problem, path, number,
                    "時間碼行 " + code(raw_line) + " 解析不了",
                )
            )
        if order + 1 < len(starts) and stop - 1 >= 0:
            if lines[stop - 1].strip() and log is not None:
                log.note(
                    NormKind.MISSING_BLANK_LINE,
                    lines[stop - 1].strip() + " ⏎ " +
                    lines[stop].strip(),
                    "視為兩段，不依賴空行", path, number,
                )
        for part_entry in part_entries:
            entries.append(part_entry)

    if UNCLEAR_UNIT_FORMAT in formats:
        issues.append(
            Issue(
                IssueKind.UNKNOWN_TIMECODE_UNIT, path, "",
                "連字號式時間碼照 分:秒:影格(30fps)換算，請對方確認"
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
    """一行是「拉丁」(族語原句、詞素切割)還是「漢字」(詞素翻譯、華語翻譯)。

    比較的是小寫拉丁字母和漢字的數量,大寫不算——看 _count_kinds。
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


def bare_form(text, long_vowel=False):
    """保留字母、漢字、數字、單引號;空白、標點、切割符號都去掉。

    單引號(喉塞音)是音位，不能去掉——排灣語 ODS 1-3 規定詞素切割要
    跟著族語原句的寫法。各種引號都當成 '。大小寫不計(詞素切割常把
    專有名詞寫成大寫)。阿美語的 ^ 是書寫系統的喉塞音字母，跟單引號一樣
    保留;泰雅語的 _ 是符號，不是字母，跟切割符號一樣去掉。
    long_vowel 為真(阿美語)時，詞中間的長音 : 也保留。
    """
    return bare_form_positions(text, long_vowel)[0]


def _is_long_vowel(text, index):
    """text 第 index 個字的 : 是詞中間的長音嗎?前面是字母,後面是字母或切割符號。"""
    after = _char_at(text, index + 1)
    return _char_at(text, index - 1).isalpha() and \
        (after.isalpha() or after in "-=<>~")


def bare_form_positions(text, long_vowel=False):
    """跟 bare_form 一樣,另外回傳每個留下來的字在原字串的位置。

    校對表標出「族語原句與詞素切割不符」不一樣的字母時要用。
    """
    out = []
    positions = []
    for index, char in enumerate(text):
        lower = char.lower()[:1]
        if "a" <= lower <= "z" or lower == "^":
            out.append(lower)
        elif "一" <= lower <= "鿿" or lower.isdigit():
            out.append(lower)
        elif lower in QUOTES:
            out.append("'")
        elif long_vowel and lower == ":" and _is_long_vowel(text, index):
            out.append(":")
        else:
            continue
        positions.append(index)
    return "".join(out), positions


# 族語原句與詞素切割不符的小類。差一個字母與差一整串,要處理的方式不一樣。
# 小類名稱跟 features/族語原句詞素切割比對.feature 的分類一樣,
# 每個小類各是一種問題(IssueKind),說明與嚴重度在 entry.py。
MISMATCH_KIND = OrderedDict()
for 種類 in IssueKind:
    if is_mismatch(種類):
        MISMATCH_KIND[種類.value[len(MISMATCH_PREFIX):]] = 種類
MISMATCH_WORDS = "詞數不同"
MISMATCH_APOSTROPHE = "只差單引號"
MISMATCH_ONE = "只差一個字母"
MISMATCH_FEW = "差 2-3 個字母"
MISMATCH_MANY = "多處不同"
MISMATCH_LENGTH = "長度差很多"
MISMATCH_LANGUAGE = "族語和華語不一致"
MISMATCH_LENGTHENING = "詞素切割有拉長音"
MISMATCH_LONG_VOWEL = "只差長音符號"

# 差幾個字母算「一點點」,超過就算多處不同。
FEW_LIMIT = 3
# 長度差這個比例以上,就當做少了一整串。
LENGTH_RATIO = 0.25
# 詞素切割可以把族語原句的詞併起來的符號:依附詞 = 與詞組 .;
# 泰雅語另外可以用 +。- 不行。
JOINERS = "=."
PLUS_JOINER_ETHNIC = "泰雅"
# 阿美語的長音 : 要兩行一致(《原住民族語言書寫系統》)。
LONG_VOWEL_ETHNIC = "阿美"
# 拉長音。只該寫在族語原句,詞素切割不用標。
LENGTHENING = "=="
# 泰雅語群的詞素切割常寫完整形(lga → la+ga),差幾個字母算通過。
ATAYALIC = ("泰雅", "太魯閣", "賽德克")
ATAYALIC_PASSES = (MISMATCH_ONE, MISMATCH_FEW, MISMATCH_LENGTH)


def _diff_ops(one, other):
    ops = []
    for op in difflib.SequenceMatcher(None, one, other).get_opcodes():
        if op[0] != "equal":
            ops.append(op)
    return ops


def _mismatch_detail(source, segmentation, long_vowel=False):
    """族語原句與詞素切割差在哪裡，寫成短短一句，例如 `pai` → `pay`。"""
    one = bare_form(source, long_vowel)
    other = bare_form(segmentation, long_vowel)
    parts = []
    for tag, i1, i2, j1, j2 in _diff_ops(one, other)[:3]:
        left = one[i1:i2]
        right = other[j1:j2]
        if not left:
            parts.append("詞素切割多了「" + right + "」")
        elif not right:
            parts.append("詞素切割少了「" + left + "」")
        else:
            parts.append("「" + left + "」→「" + right + "」")
    return "、".join(parts)


def _word_counts_fit(source, segmentation, ethnic=""):
    """族語原句的詞數和詞素切割的詞數對不對得起來。

    一個詞素切割 token 裡的 =(依附詞)、.(詞組)會把族語原句的幾個詞
    併成一個(awa to → awa=to、kiya ni → kiya.ni),泰雅語的 + 也可以
    (la ga → la+ga)。所以一個 token 最多吃(1 + 這些符號的個數)個
    族語原句的詞。- 不算:族語原句寫成兩個詞、詞素切割用 - 接起來,
    算詞數不同。
    """
    joiners = JOINERS
    if ethnic == PLUS_JOINER_ETHNIC:
        joiners = joiners + "+"
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
        most += 1
        for char in token:
            if char in joiners:
                most += 1
    if least == 0:
        return True
    return least <= source_words <= most


def _lengthened_word(segmentation):
    """詞素切割裡第一個寫了拉長音 == 的詞;沒有就是空字串。"""
    for word in segmentation.split():
        if LENGTHENING in word:
            return word
    return ""


def _script_of(word):
    """一個詞是族語(拉丁字母)還是華語(漢字);兩種都有或都沒有是空字串。"""
    letters = bare_form(word)
    latin = False
    han = False
    for char in letters:
        if "a" <= char <= "z":
            latin = True
        elif "一" <= char <= "鿿":
            han = True
    if latin and not han:
        return "族語"
    if han and not latin:
        return "華語"
    return ""


def _language_mismatch(source, segmentation):
    """同一個位置的詞一邊是族語、一邊是華語,回傳 [(族語原句的詞, 詞素切割的詞)]。

    兩行的詞數一樣才逐詞對位;詞數不一樣就沒辦法對,回傳空清單。
    """
    left = []
    for word in source.split():
        if bare_form(word):
            left.append(word)
    right = []
    for word in segmentation.split():
        if bare_form(word):
            right.append(word)
    if len(left) != len(right):
        return []
    out = []
    for index, word in enumerate(left):
        here = _script_of(word)
        there = _script_of(right[index])
        if here and there and here != there:
            out.append((word, right[index]))
    return out


def _mismatch_kind(source, segmentation):
    """把「族語原句與詞素切割不符」再分類，才知道要怎麼處理。"""
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


@dataclasses.dataclass
class SourceCheck:
    """族語原句與詞素切割逐字比對的結果。

    規格寫在 features/族語原句詞素切割比對.feature：
    passed 是通過與否，kind 是不通過的分類（通過時是 None），
    detail 是差在哪裡的一句話。族語原句的標點不比，
    詞素切割行的標點另外由 check_segment_punctuation 檢查。
    """

    passed: bool
    kind: object = None
    detail: str = ""


def compare_source(source, segmentation, ethnic=""):
    """族語原句與詞素切割逐字比對，回傳 SourceCheck。

    這是 features/族語原句詞素切割比對.feature 的入口，assemble_entry 也用
    同一支產生「族語原句與詞素切割不符」。ethnic 是族別(阿美、泰雅……),
    沒給的話只限某些語言的規則都不套用。

    不符時一段只歸一個小類,前面的先算:詞素切割有拉長音 → 族語和華語
    不一致 → 只差長音符號(阿美語) → 原本的 6 類。泰雅語群的只差一個
    字母、差 2-3 個字母、長度差很多算通過。
    """
    lengthened = _lengthened_word(segmentation)
    if lengthened:
        return SourceCheck(
            False, MISMATCH_LENGTHENING,
            "詞素切割的「" + lengthened + "」有拉長音「" + LENGTHENING + "」")
    long_vowel = ethnic == LONG_VOWEL_ETHNIC
    same = bare_form(source) == bare_form(segmentation)
    fits = _word_counts_fit(source, segmentation, ethnic)
    if same and fits and bare_form(source, long_vowel) == \
            bare_form(segmentation, long_vowel):
        return SourceCheck(True, None, "")
    mixed = _language_mismatch(source, segmentation)
    if mixed:
        parts = []
        for word, other in mixed[:3]:
            parts.append(
                "「" + bare_form(word) + "」→「" + bare_form(other) + "」")
        return SourceCheck(False, MISMATCH_LANGUAGE, "、".join(parts))
    if same and fits:
        return SourceCheck(
            False, MISMATCH_LONG_VOWEL,
            _mismatch_detail(source, segmentation, long_vowel))
    分類 = _mismatch_kind(source, segmentation)
    if ethnic in ATAYALIC and 分類 in ATAYALIC_PASSES:
        return SourceCheck(True, None, "")
    return SourceCheck(
        passed=False,
        kind=分類,
        detail=_mismatch_detail(source, segmentation),
    )


# 詞素切割行一定可以有的符號:切割符號、單引號(各種寫法)、笑聲的＠。
SEGMENT_SYMBOLS = "-=<>~" + QUOTES + "＠"
# 《原住民族語言書寫系統》(113 年修正)各語言明定的符號,依族別查。
# 泰雅語的 + 標示詞組。
WRITING_SYMBOLS = {
    "阿美": "^:",
    "泰雅": "_+",
    "賽夏": ":",
    "邵": ".",
}
# 程式推不出正確寫法的符號:括號裡可能是省略的音,也可能是補充說明。
UNSURE_SYMBOLS = "()（）"
# 獨立的說話者標記:整個詞是 1 到 3 個字母加冒號,例如 G:、Lj:。
SPEAKER = re.compile(r"[A-Za-z]{1,3}[:：]")
COLONS = ":："
# 第一個詞的冒號可能是說話者標記沒空白,目前只在泰雅語看到。
SPEAKER_COLON_ETHNIC = "泰雅"
# 只有泰雅語可以用 + 標示詞組,其他語言的詞組要用 .。
PLUS_ETHNIC = "泰雅"


@dataclasses.dataclass
class PunctuationFinding:
    """一種標點問題:提示的句子與有問題的詞是第幾個(從 0 數起)。"""

    sentences: list = dataclasses.field(default_factory=list)
    positions: list = dataclasses.field(default_factory=list)

    @property
    def hint(self):
        return "；".join(self.sentences)


@dataclasses.dataclass
class SegmentPunctuation:
    """詞素切割行標點檢查的結果。

    規格寫在 features/詞素切割標點.feature：findings 是 {IssueKind:
    PunctuationFinding},一種問題一筆;hint 是全部的提示照詞的位置接起來
    (沒有標點時是空字串)。
    """

    findings: dict = dataclasses.field(default_factory=OrderedDict)
    ordered: list = dataclasses.field(default_factory=list)

    @property
    def hint(self):
        return "；".join(self.ordered)


def _inside_word(word, index):
    """這個位置的前後都緊接字母或數字,才算詞中間。"""
    if index == 0 or index == len(word) - 1:
        return False
    return word[index - 1].isalnum() and word[index + 1].isalnum()


def _unique(chars):
    """照出現順序去掉重複的字元。"""
    out = []
    for char in chars:
        if char not in out:
            out.append(char)
    return out


def _quoted(chars):
    """每個字元各用反引號包起來,用「、」隔開,例如 `?`、`!`。

    被引用的字元是語料,跟報告裡其他語料一樣放在反引號裡,
    報告內文的全形逗號規則才不會碰到它。反引號本身換成單引號。
    """
    out = []
    for char in _unique(chars):
        out.append("`" + char.replace("`", "'") + "`")
    return "、".join(out)


def _word_problem(word, allowed):
    """一個詞裡面算標點的字元。詞中間的 . 是詞組，不算。"""
    marks = []
    for index, char in enumerate(word):
        if char.isalnum() or char in SEGMENT_SYMBOLS or char in allowed:
            continue
        if char == "." and _inside_word(word, index):
            continue
        marks.append(char)
    return marks


def _has_letter(word):
    for char in word:
        if char.isalnum():
            return True
    return False


def _without(words, position):
    """整行拿掉第 position 個詞(從 0 數起)。"""
    kept = []
    for index, word in enumerate(words):
        if index != position:
            kept.append(word)
    return " ".join(kept)


def _sentence(words, position, marks):
    """一個有問題的詞寫一句提示。"""
    word = words[position]
    where = "詞素切割第 " + str(position + 1) + " 個詞的 `" + word + "` 有"
    unsure = []
    for char in marks:
        if char in UNSURE_SYMBOLS:
            unsure.append(char)
    if unsure:
        return (where + "括號 `" + "".join(_unique(unsure)) + "`，"
                "程式無法判斷，請標注者確認")
    if not _has_letter(word):
        return (where + "符號 " + _quoted(marks) + "，程式判斷要整個詞刪掉，"
                "因為詞素切割不能有標點，應該寫是 `" +
                _without(words, position) + "`")
    fixed = []
    for char in word:
        if char not in marks:
            fixed.append(char)
    return (where + "標點 " + _quoted(marks) + "，程式判斷要刪掉，"
            "因為詞素切割不能有標點，應該寫是 `" + "".join(fixed) + "`")


def _plus_sentence(words, position):
    """泰雅語以外用了 +:建議改成 .。"""
    word = words[position]
    return ("詞素切割第 " + str(position + 1) + " 個詞的 `" + word +
            "` 有標點 `+`，程式判斷要改成 `.`，因為只有泰雅語可以用 + "
            "標示詞組，應該寫是 `" + word.replace("+", ".") + "`")


def _split_marks(marks, position, ethnic):
    """一個詞的標點分到三種問題:{IssueKind: [字元]}。"""
    out = OrderedDict()
    for char in marks:
        kind = IssueKind.SEGMENT_PUNCTUATION
        if char in COLONS and position == 0 and \
                ethnic == SPEAKER_COLON_ETHNIC:
            kind = IssueKind.SEGMENT_SPEAKER_COLON
        elif char == "+":
            kind = IssueKind.SEGMENT_PLUS
        out.setdefault(kind, []).append(char)
    return out


def check_segment_punctuation(segmentation, ethnic=""):
    """檢查詞素切割行有沒有標點,回傳 SegmentPunctuation。

    這是 features/詞素切割標點.feature 的入口,build_entry 也用同一支
    產生標點的三種問題。ethnic 用來查書寫系統的符號:泰雅語第一個詞的
    冒號是「詞素切割第一個詞有冒號」,泰雅語以外的 + 是「非泰雅語的
    詞素切割不應該用 + 符號」,其他都是「詞素切割有標點」。
    """
    allowed = WRITING_SYMBOLS.get(ethnic, "")
    words = segmentation.split()
    result = SegmentPunctuation()
    for position, word in enumerate(words):
        if SPEAKER.fullmatch(word):
            continue
        marks = _word_problem(word, allowed)
        for kind, chars in _split_marks(marks, position, ethnic).items():
            if kind is IssueKind.SEGMENT_PLUS:
                sentence = _plus_sentence(words, position)
            else:
                sentence = _sentence(words, position, chars)
            finding = result.findings.setdefault(kind, PunctuationFinding())
            finding.sentences.append(sentence)
            finding.positions.append(position)
            result.ordered.append(sentence)
    return result


# 詞素切割的字數比族語原句多這麼多,就不是換行,而是同一句標了兩版。
DUPLICATE_RATIO = 1.5


def _is_duplicate(source_line, joined_segments):
    """比對族語原句與重組後的詞素切割，判斷是換行還是重複標註。"""
    source = bare_form(source_line)
    if not source:
        return False
    return len(bare_form(joined_segments)) / len(source) >= DUPLICATE_RATIO


def assemble_entry(entry, log=None, ethnic=""):
    """把 body 組成四行。組得起來回傳 True，組不起來回傳 False。

    標準排法是:族語原句 +(詞素切割， 詞素翻譯)× n + 華語翻譯。
    四行段是 n=1,長句換行是 n>1。中間的行要「拉丁、漢字」相間才組得起來。
    ethnic 是族別,族語原句與詞素切割比對要用。
    """
    body = entry.body
    if len(body) < 3:
        return False
    middle = body[1:-1]
    if len(middle) % 2 != 0:
        return False
    # 排版分析這一步只管切段和四行對位,不管內容是族語還是華語。
    # 整段都是華語時找不到拉丁行,照位置排就好,不能因為這樣
    # 就說它組不起來——「整段華語就不做詞素切割分析」是下一步的事。
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
                "族語原句只有一句，詞素切割卻有 " + str(len(segments)) + " 版",
                [
                    ("族語原句", collapse_spaces(body[0])),
                    ("詞素切割", " ⏎ ".join(segments)),
                ],
            )
        )
        return False

    entry.source = collapse_spaces(body[0])
    entry.segmentation = joined
    entry.gloss = " ".join(glosses)
    entry.translation = collapse_spaces(body[-1])
    比對 = compare_source(entry.source, entry.segmentation, ethnic)
    if not 比對.passed:
        entry.issues.append(
            Issue(
                MISMATCH_KIND[比對.kind], entry.path, entry.number,
                比對.detail,
                [("族語原句", entry.source), ("詞素切割", entry.segmentation)],
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


# 只有數字、標點這種,不是語料也不是註記的行(例如 0000、136.6)。
NOISE = re.compile(r'^[\d.\-–—:,()（）\s]+$')

# 詞素翻譯行尾如果有句讀,很可能是華語翻譯黏在後面。
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
    """詞素翻譯行尾是否黏著華語翻譯:看有沒有句讀。"""
    for mark in SENTENCE_MARKS:
        if mark in line:
            return True
    return False


def classify_entry(entry):
    """組不起來的段，判斷是哪一種結構異常。回傳 IssueKind 或 None。"""
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
        return IssueKind.MISSING_GLOSS_LINE
    return IssueKind.GLUED_LINE


DETAIL = {
    IssueKind.EMPTY_ENTRY: "只有編號與時間碼，沒有內文",
    IssueKind.STRAY_LINE: "段內有無法歸類的雜訊行",
    IssueKind.CHINESE_ONLY: "整段都是華語，沒有族語標註",
    IssueKind.MISSING_TRANSLATION: "沒有第四行華語翻譯",
    IssueKind.GLUED_LINE: "有兩行黏在一起",
    IssueKind.MISSING_GLOSS_LINE: "有一截詞素切割沒有對應的詞素翻譯",
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


def build_entry(entry, log=None, ethnic=""):
    """組四行;組不起來就分類異常。回傳組不組得起來。

    ethnic 是族別,檢查詞素切割行標點時查書寫系統的符號用。
    """
    if assemble_entry(entry, log, ethnic):
        # 排版分析(組四行)和內容判斷是兩步。整段都是華語的也組得
        # 起來,但不能匯出,所以組好之後再記一筆「純華語句」。
        if _all_han(_kinds_of(entry.body)):
            entry.issues.append(
                Issue(
                    IssueKind.CHINESE_ONLY, entry.path, entry.number,
                    DETAIL.get(IssueKind.CHINESE_ONLY, ""),
                    [("內文", " ⏎ ".join(entry.body))],
                )
            )
        else:
            _note_segment_punctuation(entry, ethnic)
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


def _note_segment_punctuation(entry, ethnic):
    """詞素切割行的標點問題,一種記一筆。純華語句不檢查。"""
    結果 = check_segment_punctuation(entry.segmentation, ethnic)
    for kind, finding in 結果.findings.items():
        entry.issues.append(
            Issue(
                kind, entry.path, entry.number, finding.hint,
                [("詞素切割", entry.segmentation)],
            )
        )


def parse_corpus_file(path, rel_path, ethnic="", variant="", log=None):
    """讀一個 docx，轉成 CorpusFile(已經組四行、已經分類)。

    語料的來源是 docx。審閱註解在 word/comments.xml,抽內文時
    本來就不會混進來,所以沒有註解殘留要清——看
    openspec/specs/corpus-parsing 的「語料來源為 docx」。
    """
    corpus = parse_text(
        docx_text(path), path=rel_path, ethnic=ethnic,
        variant=variant, log=log,
    )
    for entry in corpus.entries:
        build_entry(entry, log, ethnic)
    return corpus
