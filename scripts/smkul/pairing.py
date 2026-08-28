"""docx 與 txt 的配對、逐組比對。"""

import difflib
import os
import re
import unicodedata

from scripts.smkul.docx2text import docx_comments, docx_text
from scripts.smkul.entry import Issue, IssueKind
from scripts.smkul.parser import (
    build_entry,
    collapse_spaces,
    normalize_text,
    parse_text,
)

# docx 匯出做 txt ê時,審閱註解會tī內文留兩个 [a] 這款錨點,
# 註解本文嘛會予寫做一般ê文字行(像「[a]待討論」)。
# 語料本身已經改用 docx 做來源,遮ê攏無關係矣;毋過 docx↔txt
# 這份歷史核對若無先共這款殘留掰掉,差異會予淹掉(253 筆 vs 17 筆),
# 看袂出真正ê內容無仝。
ANCHOR = re.compile(r'\[([a-z]{1,2})\]')


def read_txt(path):
    """讀 txt 檔,原封回傳全文(BOM 交予 normalize_text 處理)。"""
    with open(path, encoding="utf-8") as handle:
        return handle.read()


def strip_comment_residue(text, comments):
    """共 txt ê註解殘留掰掉。comments 是 docx ê {字母: 內容}。"""
    if not comments:
        return text
    out = []
    for line in text.split("\n"):
        stripped = line.strip()
        found = ANCHOR.match(stripped)
        if found and found.group(1) in comments:
            # 規逝就是註解本文,規逝掰掉。
            continue
        kept = []
        last = 0
        for anchor in ANCHOR.finditer(line):
            if anchor.group(1) not in comments:
                continue
            kept.append(line[last:anchor.start()])
            last = anchor.end()
        kept.append(line[last:])
        out.append("".join(kept))
    return "\n".join(out)

# 目錄名 → (族別, 語別)。語別是路徑的第二層,沒有時用族別。


def split_kind(rel_path):
    """從相對路徑取出族別與語別。"""
    parts = rel_path.split(os.sep)
    if len(parts) < 2:
        parts = rel_path.split("/")
    ethnic = parts[0].replace("族", "")
    if len(parts) >= 3:
        variant = parts[1]
    else:
        variant = ethnic
    return ethnic, variant


def _key(stem):
    """檔名的比對 key:Unicode 正規化，去掉空白與底線。"""
    text = unicodedata.normalize("NFC", stem)
    out = []
    for char in text:
        if char.isspace() or char == "_":
            continue
        out.append(char)
    return "".join(out)


def collect(base):
    """走過語料目錄，回傳 {相對路徑(無副檔名): {"txt": 路徑， "docx": 路徑}}。"""
    found = {}
    for root, dirs, names in os.walk(base):
        for name in sorted(names):
            stem, ext = os.path.splitext(name)
            if ext not in (".txt", ".docx"):
                continue
            rel_dir = os.path.relpath(root, base)
            if rel_dir == ".":
                rel_dir = ""
            slot = found.setdefault((rel_dir, _key(stem)), {})
            slot[ext[1:]] = os.path.join(root, name)
            slot.setdefault("stems", {})[ext[1:]] = stem
    return found


# 檔名像到這種程度,就是同一篇,只是名字寫法不同(例如 鳯/鳳)。
SIMILAR_ENOUGH = 0.6


def _similar(left, right):
    return difflib.SequenceMatcher(None, left, right).ratio()


def _show(rel_dir, stem):
    if rel_dir:
        return rel_dir + "/" + stem
    return stem


def pair_files(base):
    """配對。回傳 (成對的清單， 問題清單)。

    檔名完全相同才算成對。名字很像但不完全相同的(例如魯凱霧台 3 的
    鳯/鳳)，依 spec 算「檔名不一致」錯誤，不自動視為成對。
    """
    pairs = []
    issues = []
    lonely = {}
    found = collect(base)
    for (rel_dir, _), slot in sorted(found.items()):
        stems = slot.get("stems", {})
        txt = slot.get("txt")
        docx = slot.get("docx")
        if txt is not None and docx is not None:
            pairs.append((rel_dir, stems["txt"], txt, docx))
            continue
        if txt is None:
            lonely.setdefault(rel_dir, {}).setdefault("docx", []).append(
                stems["docx"])
        else:
            lonely.setdefault(rel_dir, {}).setdefault("txt", []).append(
                stems["txt"])

    for rel_dir in sorted(lonely):
        only_txt = lonely[rel_dir].get("txt", [])
        only_docx = lonely[rel_dir].get("docx", [])
        used = set()
        for txt_stem in only_txt:
            best = ""
            score = 0.0
            for docx_stem in only_docx:
                if docx_stem in used:
                    continue
                ratio = _similar(txt_stem, docx_stem)
                if ratio > score:
                    score = ratio
                    best = docx_stem
            if score >= SIMILAR_ENOUGH:
                used.add(best)
                issues.append(
                    Issue(
                        IssueKind.FILENAME_MISMATCH,
                        _show(rel_dir, txt_stem), "",
                        "檔名不同，無法自動配對",
                        [("txt", txt_stem), ("docx", best)],
                    )
                )
            else:
                issues.append(
                    Issue(
                        IssueKind.MISSING_FILE, _show(rel_dir, txt_stem),
                        "", "只有 txt，沒有 docx"
                    )
                )
        for docx_stem in only_docx:
            if docx_stem in used:
                continue
            issues.append(
                Issue(
                    IssueKind.MISSING_FILE, _show(rel_dir, docx_stem),
                    "", "只有 docx，沒有 txt"
                )
            )
    return pairs, issues


def comment_map(docx_path):
    """docx 的註解 → {字母: 內容}。txt 的註解殘留靠這個判斷。"""
    out = {}
    for item in docx_comments(docx_path):
        out[item["字母"]] = item["內容"]
    return out


def _entry_map(entries):
    out = {}
    for entry in entries:
        if entry.number:
            out[entry.number] = entry
    return out


TIMES = (("開始時間", "start"), ("結束時間", "end"))


def compare_entries(rel_path, txt_corpus, docx_corpus):
    """逐組比對。空白差異已經由 parser 合併掉了。"""
    issues = []
    txt_map = _entry_map(txt_corpus.entries)
    docx_map = _entry_map(docx_corpus.entries)
    if len(txt_corpus.entries) != len(docx_corpus.entries):
        issues.append(
            Issue(
                IssueKind.ENTRY_COUNT_MISMATCH, rel_path, "",
                "txt " + str(len(txt_corpus.entries)) + " 組，docx " +
                str(len(docx_corpus.entries)) + " 組",
            )
        )
    numbers = set(txt_map) | set(docx_map)
    for number in sorted(numbers, key=_sort_key):
        in_txt = txt_map.get(number)
        in_docx = docx_map.get(number)
        if in_txt is None:
            issues.append(
                Issue(IssueKind.CONTENT_DIFF, rel_path, number,
                      "txt 裡找不到這一組")
            )
            continue
        if in_docx is None:
            issues.append(
                Issue(IssueKind.CONTENT_DIFF, rel_path, number,
                      "docx 裡找不到這一組")
            )
            continue
        for label, field in TIMES:
            left = getattr(in_txt, field)
            right = getattr(in_docx, field)
            if left != right:
                issues.append(
                    Issue(
                        IssueKind.CONTENT_DIFF, rel_path, number,
                        label + "不同",
                        [("txt", left), ("docx", right)],
                    )
                )
        for issue in _compare_body(rel_path, number, in_txt, in_docx):
            issues.append(issue)
    return issues


def _lines_of(entry):
    """每一行內文，空白已合併。比對要用這個，不能用組裝後的欄位——
    組不起來時欄位是空的，會報出不存在的差異。"""
    out = []
    for line in entry.body:
        out.append(collapse_spaces(line))
    return out


def _compare_body(rel_path, number, in_txt, in_docx):
    """逐行比對內文。註解錨點與註解本文已經由 parser 清掉了。"""
    issues = []
    left = _lines_of(in_txt)
    right = _lines_of(in_docx)
    if len(left) != len(right):
        issues.append(
            Issue(
                IssueKind.CONTENT_DIFF, rel_path, number,
                "內文行數不同:txt " + str(len(left)) + " 行，docx " +
                str(len(right)) + " 行",
            )
        )
    for index in range(max(len(left), len(right))):
        if index < len(left):
            one = left[index]
        else:
            one = ""
        if index < len(right):
            other = right[index]
        else:
            other = ""
        if one != other:
            issues.append(
                Issue(
                    IssueKind.CONTENT_DIFF, rel_path, number,
                    "第 " + str(index + 1) + " 行不同",
                    [("txt", one), ("docx", other)],
                )
            )
    return issues


def _sort_key(number):
    try:
        return (0, int(number), "")
    except ValueError:
        return (1, 0, number)


def check_pair(rel_dir, stem, txt_path, docx_path, log=None):
    """比對一對檔案。回傳 (相對路徑， 問題清單)。"""
    if rel_dir:
        rel_path = rel_dir + "/" + stem + ".txt"
    else:
        rel_path = stem + ".txt"
    comments = comment_map(docx_path)
    raw = normalize_text(read_txt(txt_path), None, rel_path)
    txt_corpus = parse_text(
        strip_comment_residue(raw, comments), path=rel_path, log=log)
    docx_corpus = parse_text(docx_text(docx_path), path=rel_path)
    for entry in txt_corpus.entries:
        build_entry(entry, log)
    for entry in docx_corpus.entries:
        build_entry(entry)
    return rel_path, compare_entries(rel_path, txt_corpus, docx_corpus)
