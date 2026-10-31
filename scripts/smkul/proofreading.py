"""校對表:問題 ID、讀回老師的判斷、產生校對表。

規格見 openspec 的 proofreading spec。老師在 xlsx 校對表的「判斷」欄
選三個選項之一,程式重跑時讀回來:「docx 正確，程式判斷錯」的問題就
不再算問題,移到報告最後一章。xlsx 的讀寫在 xlsx.py。
"""

import difflib
import hashlib
import os
import re
from collections import OrderedDict, namedtuple

from scripts.smkul import report, xlsx
from scripts.smkul.entry import IssueKind
from scripts.smkul.pairing import split_kind
from scripts.smkul.parser import bare_form_positions, check_segment_punctuation

ID_PREFIX = "ISSUE-"
# ID 取 sha256 的前幾碼。
ID_LENGTH = 8


def id_source(issue, body):
    """算 ID 用的內容:檔案、段編號、問題種類、段的全部內文行。

    沒有段編號的問題(檔案層的問題、孤兒時間碼)用原因與對照代替內文。
    """
    parts = [issue.path, issue.number, issue.kind.value]
    if issue.number and body:
        for line in body:
            parts.append(line)
    else:
        parts.append(issue.detail)
        for label, value in issue.compare:
            parts.append(label + ":" + value)
    return "\n".join(parts)


def issue_id(source):
    digest = hashlib.sha256(source.encode("utf-8")).hexdigest()
    return ID_PREFIX + digest[:ID_LENGTH]


class IdBook:
    """一次執行裡發過的 ID。

    一模一樣的問題出現第二次,內容後面加「#2」再算,ID 才不會重複。
    不同的內容算出同一個 ID(撞號)是程式要處理的問題,直接報錯。
    """

    def __init__(self):
        self.sources = {}
        self.used = set()

    def assign(self, issue, body):
        source = id_source(issue, body)
        candidate = source
        count = 1
        while candidate in self.used:
            count += 1
            candidate = source + "\n#" + str(count)
        found = issue_id(candidate)
        if found in self.sources and self.sources[found] != candidate:
            raise ValueError("問題 ID 撞號:" + found)
        self.sources[found] = candidate
        self.used.add(candidate)
        issue.id = found
        return found


# 「判斷」欄的三個選項。
FIX_DOCX = "程式對，docx 要修改"
PROGRAM_WRONG = "docx 正確，程式判斷錯"
DISCUSS = "要討論"
CHOICES = [FIX_DOCX, PROGRAM_WRONG, DISCUSS]

# 校對表的欄位,照順序。
HEADERS = [
    "ID", "檔案", "段", "問題", "提示", "族語原句", "詞素切割", "詞素翻譯",
    "華語翻譯", "判斷", "備註",
]

# 老師填的一列。values 是 {欄名: 值},整列原樣留著,「已不存在的紀錄」用。
Judgement = namedtuple(
    "Judgement",
    ["id", "judgement", "note", "values", "source", "row", "mtime"],
)
# 讀回來的結果:{ID: Judgement},以及要在報告提醒的讀取問題。
ReadBack = namedtuple("ReadBack", ["judgements", "problems"])


def _sheet_judgements(name, sheet, rows, mtime, problems):
    """一個分頁裡老師填過的列。沒有 ID 或「判斷」欄的分頁略過。"""
    out = []
    if not rows or "ID" not in rows[0] or "判斷" not in rows[0]:
        return out
    header = rows[0]
    for index, row in enumerate(rows[1:]):
        values = {}
        for column, title in enumerate(header):
            if column < len(row):
                values[title] = row[column].strip()
            else:
                values[title] = ""
        issue_id = values.get("ID", "")
        if not issue_id:
            continue
        number = index + 2
        judgement = values.get("判斷", "")
        if judgement and judgement not in CHOICES:
            problems.append(
                name + " 「" + sheet + "」分頁第 " + str(number) +
                " 列的判斷「" + judgement + "」不是三個選項之一，"
                "當作沒有判斷")
            judgement = ""
        note = values.get("備註", "")
        if not judgement and not note:
            continue
        out.append(Judgement(
            issue_id, judgement, note, values, name, number, mtime))
    return out


def read_judgements(folder):
    """讀資料夾裡所有老師交回的 xlsx,回傳 ReadBack。

    資料夾不存在就當作沒有任何判斷。同一個 ID 出現在好幾個檔、判斷又不
    一樣時,以檔案修改時間較新的為準,並記一筆讀取問題。
    """
    judgements = {}
    problems = []
    if not os.path.isdir(folder):
        return ReadBack(judgements, problems)
    for name in sorted(os.listdir(folder)):
        # ~$ 開頭的是 Excel 開著檔案時留下的暫存檔。
        if not name.endswith(".xlsx") or name.startswith("~$"):
            continue
        path = os.path.join(folder, name)
        mtime = os.path.getmtime(path)
        for sheet, rows in xlsx.read(path).items():
            found = _sheet_judgements(name, sheet, rows, mtime, problems)
            for item in found:
                _keep_newer(judgements, item, problems)
    return ReadBack(judgements, problems)


def _keep_newer(judgements, item, problems):
    old = judgements.get(item.id)
    if old is None:
        judgements[item.id] = item
        return
    newer = item
    if old.mtime > item.mtime:
        newer = old
    if old.judgement != item.judgement:
        problems.append(
            item.id + " 在 " + old.source + " 與 " + item.source +
            " 的判斷不一樣（「" + old.judgement + "」／「" + item.judgement +
            "」），以修改時間較新的 " + newer.source + " 為準")
    judgements[item.id] = newer


def apply_judgements(issues, judgements):
    """把老師的判斷套到一串問題上。

    「docx 正確，程式判斷錯」的問題從 issues 移走(段就可能變乾淨、照常
    匯出);「要討論」的照常留著,另外收起來給報告的「老師標要討論的
    項目」。回傳 (確認過的, 要討論的),每一筆是 (Issue, Judgement)。
    """
    confirmed = []
    discussed = []
    kept = []
    for issue in issues:
        found = judgements.get(issue.id)
        if found is not None and found.judgement == PROGRAM_WRONG:
            confirmed.append((issue, found))
            continue
        if found is not None and found.judgement == DISCUSS:
            discussed.append((issue, found))
        kept.append(issue)
    issues[:] = kept
    return confirmed, discussed


# 校對表的一列:族別、語言別、問題,以及問題所在的段(檔案層的問題是 None)。
SheetRow = namedtuple("SheetRow", ["ethnic", "variant", "issue", "entry"])
MAIN_SHEET = "校對"
GONE_SHEET = "已不存在的紀錄"
# 每一欄的寬度(字元數),照 HEADERS 的順序。
WIDTHS = [17, 30, 6, 24, 40, 30, 30, 30, 24, 24, 24]


def _segments(text, marked):
    """把一格文字切成 [(文字, 要不要標紅)],marked 是要標紅的位置。"""
    out = []
    for index, char in enumerate(text):
        flag = index in marked
        if out and out[-1][1] == flag:
            out[-1] = (out[-1][0] + char, flag)
        else:
            out.append((char, flag))
    return out


def _word_spans(text):
    spans = []
    for found in re.finditer(r"\S+", text):
        spans.append((found.start(), found.end()))
    return spans


def marked_cells(issue, entry, ethnic):
    """要標紅的語料格:{欄名: [(文字, 要不要標紅)]}。

    「詞素切割有標點」標有問題的詞;「族語原句與詞素切割不符」標兩邊
    不一樣的字母;其他種類不標。
    """
    if entry is None:
        return {}
    if issue.kind is IssueKind.SEGMENT_PUNCTUATION:
        result = check_segment_punctuation(entry.segmentation, ethnic)
        spans = _word_spans(entry.segmentation)
        marked = set()
        for position in result.positions:
            start, end = spans[position]
            for index in range(start, end):
                marked.add(index)
        if not marked:
            return {}
        return {"詞素切割": _segments(entry.segmentation, marked)}
    if issue.kind is IssueKind.SOURCE_SEGMENT_MISMATCH:
        one, one_at = bare_form_positions(entry.source)
        other, other_at = bare_form_positions(entry.segmentation)
        left = set()
        right = set()
        matcher = difflib.SequenceMatcher(None, one, other)
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == "equal":
                continue
            for index in one_at[i1:i2]:
                left.add(index)
            for index in other_at[j1:j2]:
                right.add(index)
        out = {}
        if left:
            out["族語原句"] = _segments(entry.source, left)
        if right:
            out["詞素切割"] = _segments(entry.segmentation, right)
        return out
    return {}


def _number_key(number):
    """段編號照數字排,9 在 10 前面。"""
    found = re.match(r"\d+", number)
    if found:
        return (0, int(found.group(0)), number)
    return (1, 0, number)


def _issue_row(row, judgements):
    entry = row.entry
    lines = {"族語原句": "", "詞素切割": "", "詞素翻譯": "", "華語翻譯": ""}
    if entry is not None:
        lines["族語原句"] = entry.source
        lines["詞素切割"] = entry.segmentation
        lines["詞素翻譯"] = entry.gloss
        lines["華語翻譯"] = entry.translation
    for column, segments in marked_cells(
            row.issue, entry, row.ethnic).items():
        lines[column] = segments
    found = judgements.get(row.issue.id)
    judgement = ""
    note = ""
    if found is not None:
        judgement = found.judgement
        note = found.note
    return [
        row.issue.id, row.issue.path, row.issue.number,
        report.issue_label(row.issue), report.shown_detail(row.issue),
        lines["族語原句"], lines["詞素切割"], lines["詞素翻譯"],
        lines["華語翻譯"], judgement, note,
    ]


def _gone_row(found):
    out = []
    for header in HEADERS:
        out.append(found.values.get(header, ""))
    return out


def _clear(folder):
    for name in os.listdir(folder):
        if name.endswith(".xlsx"):
            os.remove(os.path.join(folder, name))


def write_sheets(folder, rows, judgements):
    """產生校對表,一個語言別一個 xlsx,回傳寫出去的路徑。

    rows 要包含所有問題,也包含老師確認過是程式判斷錯的問題(判斷欄
    保留老師填的,老師才看得到)。讀回來的判斷對不到這次任何問題的,
    寫進同一個語言別的「已不存在的紀錄」分頁。
    """
    os.makedirs(folder, exist_ok=True)
    _clear(folder)
    groups = OrderedDict()
    current = set()
    for row in rows:
        groups.setdefault((row.ethnic, row.variant), []).append(row)
        current.add(row.issue.id)
    gone = OrderedDict()
    for found in judgements.values():
        if found.id in current:
            continue
        key = split_kind(found.values.get("檔案", ""))
        gone.setdefault(key, []).append(found)
    choices = {HEADERS.index("判斷"): CHOICES}
    paths = []
    for key in sorted(set(groups) | set(gone)):
        found_rows = groups.get(key, [])
        ordered = sorted(found_rows, key=_row_key)
        table = [list(HEADERS)]
        for row in ordered:
            table.append(_issue_row(row, judgements))
        sheets = [xlsx.Sheet(MAIN_SHEET, table, choices, WIDTHS)]
        if key in gone:
            old = [list(HEADERS)]
            for found in gone[key]:
                old.append(_gone_row(found))
            sheets.append(xlsx.Sheet(GONE_SHEET, old, choices, WIDTHS))
        path = os.path.join(
            folder, "校對表_" + key[0] + "_" + key[1] + ".xlsx")
        xlsx.write(path, sheets)
        paths.append(path)
    return paths


def _row_key(row):
    return (row.issue.path, _number_key(row.issue.number))
