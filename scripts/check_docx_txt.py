"""核對 docx 與 txt 是否一致，產生報告。

語料已經改成直接由 docx 產生(見 scripts/validate_glossing.py)，
所以這支程式是**歷史核對**用的:確認對方交付的 txt 副本與 docx
內容一致。缺檔與檔名不一致只是提醒，不影響語料。

用法(在專案根目錄):

    python -m scripts.check_docx_txt [語料目錄]

有錯誤時 exit code 非 0,CI 可以擋下來。
"""

import argparse
import os
import sys

from scripts.smkul import report
from scripts.smkul.docx2text import docx_comments
from scripts.smkul.entry import IssueKind, NormLog, code
from scripts.smkul.pairing import check_pair, pair_files, split_kind

BASE = os.path.join("kithann", "giliau")
RED_TEXT_NOTE = (
    "docx 內含文字顏色/標亮這一層標記(例如太魯閣 1 有 35 處紅字，"
    "中排灣 1 檔頭寫「橘色 Megan」)，txt 沒有這些資訊。"
)


def collect_comments(pairs):
    """每個 docx 的審閱註解。"""
    out = []
    for rel_dir, stem, txt_path, docx_path in pairs:
        found = docx_comments(docx_path)
        if found:
            if rel_dir:
                shown = rel_dir + "/" + stem
            else:
                shown = stem
            out.append((shown, found))
    return out


def overview(pairs, issues, comments):
    errors, warnings, notices = report.severity_split(issues)
    lines = [report.heading("總覽")]
    lines.append("")
    lines.append("- 成對的檔案:" + str(len(pairs)) + " 對")
    lines.append("- 問題總數:" + str(len(issues)) + " 筆(錯誤 " +
                 str(len(errors)) + ")")
    comment_total = 0
    for _, found in comments:
        comment_total += len(found)
    lines.append(
        "- docx 審閱註解:" + str(comment_total) + " 條，分布在 " +
        str(len(comments)) + " 個檔案")
    lines.append("")
    lines.append(report.kind_table(issues))
    return "\n".join(lines)


VARIANT_NOTE = (
    "「有差異的組數」是有問題的句子數;「差異筆數」是問題的筆數。"
    "一組可以有好幾筆——例如某一組的內文行數不同、而且第 3 行與第 4 行"
    "各自不同，那就是 1 組、3 筆。"
)


def variant_table(per_file):
    """依語別統計。檔數與差異數都由 per_file 計算，才不會重複計。"""
    rows = {}
    for rel_path, found in per_file:
        key = split_kind(rel_path)
        slot = rows.setdefault(key, [0, 0, set()])
        slot[0] += 1
        slot[1] += len(found)
        for issue in found:
            slot[2].add((rel_path, issue.number))
    out = []
    for (ethnic, variant), (files, count, groups) in sorted(rows.items()):
        out.append((ethnic, variant, files, len(groups), count))
    return report.table(
        ["族別", "語別", "檔數", "有差異的組數", "差異筆數"], out)


def comment_section(comments):
    lines = [report.heading("docx 審閱註解(請對方處理)"), ""]
    if not comments:
        lines.append("(無)")
        return "\n".join(lines)
    lines.append(
        "這些是 docx 內的審閱註解，是對方自己標注的修改指示。"
        "語料已經改成**直接由 docx 產生**，註解本文放在 "
        "`word/comments.xml`，抽內文時不會混進來，所以"
        "**沒有註解殘留的問題**，也不用列入討論。"
        "這一章列的是註解的內容本身，會議上可逐條處理。"
    )
    for path, found in comments:
        lines.append("")
        lines.append(
            report.heading(path + "(" + str(len(found)) + " 條)", 3))
        lines.append("")
        rows = []
        for item in found:
            rows.append((
                code("[" + item["字母"] + "]"), item["作者"],
                item["日期"], code(item["內容"]),
            ))
        lines.append(report.table(["錨點", "作者", "日期", "內容"], rows))
    return "\n".join(lines)


def todo_section(issues, comments):
    """討論事項。逐項先寫「說明」(事實)，才寫「討論」(欲問對方ê)。"""
    lines = [report.heading("討論"), ""]
    groups = report.group_by_path(issues)
    missing = []
    for path, found in groups.items():
        for issue in found:
            if issue.kind in (IssueKind.MISSING_FILE,
                              IssueKind.FILENAME_MISMATCH):
                missing.append((path, issue.detail))

    lines.append(report.heading("docx 和 txt 的關係是?", 3))
    lines.append("")
    lines.append("說明:")
    lines.append("")
    lines.append("1. 需要重新產生的檔案:")
    lines.append("")
    if missing:
        lines.append(report.table(["檔案", "情形"], missing))
    else:
        lines.append("(無)")
    lines.append("")
    lines.append(
        "2. 「差異明細」那一節也說明，docx 和 txt 的內容也有差異，"
        "感覺 docx 的內容比較新。"
    )
    lines.append("")
    lines.append("討論:")
    lines.append("")
    lines.append("是否以 docx 資料為主，txt 當做參考?")

    lines.append("")
    lines.append(report.heading("docx 的顏色標記層", 3))
    lines.append("")
    lines.append("說明:")
    lines.append("")
    lines.append(RED_TEXT_NOTE)
    lines.append("")
    lines.append("討論:")
    lines.append("")
    lines.append("紅字代表什麼意思?需要保留嗎?")

    total = 0
    for _, found in comments:
        total += len(found)
    lines.append("")
    lines.append(report.heading("docx 審閱註解", 3))
    lines.append("")
    lines.append("說明:")
    lines.append("")
    lines.append(
        "共 " + str(total) + " 條，詳細內容請看「docx 審閱註解」那一章。"
        "txt 內留下的錨點與註解本文，程式已經對照 docx 自動刪掉了，"
        "不需要討論。"
    )
    lines.append("")
    lines.append("討論:")
    lines.append("")
    lines.append("這些註解日後會處理嗎?還是處理的時候全部忽略?")
    return "\n".join(lines)


def run(base):
    log = NormLog()
    pairs, issues = pair_files(base)
    per_file = []
    for rel_dir, stem, txt_path, docx_path in pairs:
        rel_path, found = check_pair(rel_dir, stem, txt_path, docx_path, log)
        per_file.append((rel_path, found))
        for issue in found:
            issues.append(issue)
    comments = collect_comments(pairs)

    sections = [
        "# docx / txt 一致性檢查報告",
        "更新日期:" + report.today(),
        overview(pairs, issues, comments),
        report.heading("依語別統計") + "\n\n" + VARIANT_NOTE +
        "\n\n" + variant_table(per_file),
        report.heading("YAML 的來源") + "\n\n" + report.YAML_SOURCE_WHY,
        # 自動處理那一章只放在 glossing 報告,這份報告談的是
        # docx 與 txt 一不一致,不需要重複。
        detail(per_file, issues),
        comment_section(comments),
        todo_section(issues, comments),
    ]
    path = report.write("docx_txt_report.md", sections)
    errors, warnings, notices = report.severity_split(issues)
    return path, len(errors)


def detail(per_file, issues):
    flat = []
    for issue in issues:
        flat.append(issue)
    return report.detail_section("差異明細", flat)


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="核對 docx 與 txt 是否一致(歷史核對用)")
    parser.add_argument("base", nargs="?", default=BASE, help="語料目錄")
    args = parser.parse_args(argv)
    path, errors = run(args.base)
    print("報告:" + path)
    print("錯誤:" + str(errors) + " 筆")
    if errors:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
