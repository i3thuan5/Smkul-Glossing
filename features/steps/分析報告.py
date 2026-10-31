"""分析報告的 behave step:檢查程式有沒有照 features/分析報告.feature 跑。

這份 feature 是嚴重度規則的正本。step 對照的程式:
entry.py 的 SEVERITY 與 Entry.is_clean()(翻譯訓練YAML 匯不匯出)、
proofreading.py 的 PROOFREAD_SEVERITIES(要不要請老師校對)、
report.py 與 validate_glossing.py(報告的總覽、第 7 章、章節)。
"""

import os
import re
import shutil
import tempfile

from behave import then, when

from tests import DATA

from scripts import validate_glossing
from scripts.smkul import proofreading, report
from scripts.smkul.entry import SEVERITY, Entry, Issue, IssueKind, Severity
from scripts.smkul.parser import MISMATCH_WHY

MISMATCH_PREFIX = IssueKind.SOURCE_SEGMENT_MISMATCH.value + "-"


def _severity_of(value):
    for severity in Severity:
        if severity.value == value:
            return severity
    raise AssertionError("feature 寫了程式沒有的嚴重度:" + value)


def _kind_with(severity):
    """這個嚴重度的第一種問題,當代表。"""
    for kind, found in SEVERITY.items():
        if found is severity:
            return kind
    raise AssertionError("程式裡沒有嚴重度是「" + severity.value + "」的問題")


def _issue_for(kind, number="1"):
    detail = ""
    if kind is IssueKind.SOURCE_SEGMENT_MISMATCH:
        detail = next(iter(MISMATCH_WHY)) + ":差異"
    return Issue(kind, "阿美族/秀姑巒/a.docx", number, detail)


def _program_labels():
    """程式裡的問題名稱與嚴重度,照 SEVERITY 的順序;不符的大類展開成小類。"""
    out = []
    for kind, severity in SEVERITY.items():
        if kind is IssueKind.SOURCE_SEGMENT_MISMATCH:
            for sub in MISMATCH_WHY:
                out.append((MISMATCH_PREFIX + sub, severity.value))
        else:
            out.append((kind.value, severity.value))
    return out


def _issue_for_label(label, number):
    if label.startswith(MISMATCH_PREFIX):
        return Issue(IssueKind.SOURCE_SEGMENT_MISMATCH,
                     "阿美族/秀姑巒/a.docx", number,
                     label[len(MISMATCH_PREFIX):] + ":差異")
    for kind in IssueKind:
        if kind.value == label:
            return Issue(kind, "阿美族/秀姑巒/a.docx", number, "原因")
    raise AssertionError("程式裡沒有這種問題:" + label)


def _subheadings(text):
    """第 7 章(問題類型說明與例子)裡 ### 小節的名稱,去掉後面的筆數。"""
    out = []
    for line in text.splitlines():
        if line.startswith("### "):
            out.append(re.sub(r"\(\d+ 筆\)$", "", line[4:]))
    return out


@when("一段語料只有一筆某個嚴重度的問題")
def step_一筆問題(context):
    context.entries = {}
    for severity in Severity:
        entry = Entry("1", "0", "1", path="阿美族/秀姑巒/a.docx")
        entry.issues.append(_issue_for(_kind_with(severity)))
        context.entries[severity] = entry


@then("各嚴重度的產出是：")
def step_各嚴重度的產出(context):
    context.mapping = context.table
    for row in context.table:
        severity = _severity_of(row["嚴重度"])
        entry = context.entries[severity]
        exported = entry.is_clean()
        assert exported == (row["翻譯訓練YAML"] == "匯出"), (
            severity.value + " 的翻譯訓練YAML 應該是" + row["翻譯訓練YAML"])
        section = validate_glossing.kinds_section(entry.issues)
        label = report.issue_label(entry.issues[0])
        shown = label in section
        assert shown == (row["報告舉例"] == "舉例"), (
            severity.value + " 的報告舉例應該是" + row["報告舉例"])
        asked = severity in proofreading.PROOFREAD_SEVERITIES
        assert asked == (row["請老師校對"] == "要"), (
            severity.value + " 的請老師校對應該是" + row["請老師校對"])


@then("報告總覽有同一張對應表")
def step_總覽對應表(context):
    got = validate_glossing.overview([], [], 0, 0)
    headings = context.mapping.headings
    expected = "| " + " | ".join(headings) + " |"
    assert expected in got, "總覽沒有對應表的標題列:" + expected
    for row in context.mapping:
        cells = []
        for heading in headings:
            cells.append(row[heading])
        line = "| " + " | ".join(cells) + " |"
        assert line in got, "總覽的對應表少了:" + line


@then("每一種問題的嚴重度是：")
def step_每一種問題的嚴重度(context):
    expected = []
    for row in context.table:
        expected.append((row["問題"], row["嚴重度"]))
    context.labels = expected
    got = _program_labels()
    assert got == expected, (
        "\n程式的嚴重度與順序跟 feature 不一樣"
        "\nfeature:" + str(expected) + "\n程式:" + str(got))
    issues = []
    for index, (label, severity) in enumerate(expected):
        issues.append(_issue_for_label(label, str(index + 1)))
    order = []
    for label, severity in expected:
        order.append(label)
    assert report.ordered_labels(issues) == order, "問題表的順序跟 feature 不一樣"
    table = report.kind_table(issues)
    rows = []
    for line in table.splitlines():
        cells = line.strip("|").split("|")
        if len(cells) == 4 and cells[0].strip().isdigit():
            rows.append((cells[0].strip(), cells[1].strip(), cells[2].strip()))
    want = []
    for index, (label, severity) in enumerate(expected):
        want.append((str(index + 1), label, severity))
    assert rows == want, "\n問題表:" + str(rows) + "\n預期:" + str(want)
    section = validate_glossing.kinds_section(issues)
    assert _subheadings(section) == order, (
        "第 7 章的小節順序跟問題表不一樣:" + str(_subheadings(section)))


@then("程式裡沒有這張表以外的問題種類")
def step_沒有表外的問題(context):
    labels = set()
    for label, severity in context.labels:
        labels.add(label)
    for kind in IssueKind:
        if kind is IssueKind.SOURCE_SEGMENT_MISMATCH:
            for sub in MISMATCH_WHY:
                assert MISMATCH_PREFIX + sub in labels, (
                    "feature 少了:" + MISMATCH_PREFIX + sub)
            continue
        assert kind.value in labels, "程式有 feature 沒寫的問題:" + kind.value


@when("產生報告")
def step_產生報告(context):
    work = tempfile.mkdtemp()
    context.add_cleanup(shutil.rmtree, work)
    base = os.path.join(work, "giliau")
    folder = os.path.join(base, "阿美族", "秀姑巒")
    os.makedirs(folder)
    shutil.copy(os.path.join(DATA, "最小範例.docx"), folder)
    context.out_dir = os.path.join(work, "out")
    validate_glossing.run(
        base, proof_dir=os.path.join(work, "校對"), out_dir=context.out_dir)
    context.report = ""
    path = os.path.join(context.out_dir, validate_glossing.REPORT_NAME)
    if os.path.exists(path):
        with open(path, encoding="utf-8") as handle:
            context.report = handle.read()


@then("報告的章節依序是：")
def step_章節(context):
    got = []
    for line in context.report.splitlines():
        found = re.match(r"## \d+\. (.+)$", line)
        if found:
            got.append(found.group(1))
    expected = []
    for row in context.table:
        expected.append(row["章節"])
    assert got == expected, "\n報告:" + str(got) + "\n預期:" + str(expected)


@then('報告的檔名是 "{name}"')
def step_報告檔名(context, name):
    names = sorted(os.listdir(context.out_dir))
    assert name in names, "輸出資料夾裡沒有 " + name + ":" + str(names)
    assert "glossing_report.md" not in names, "還產生了舊檔名 glossing_report.md"


@then("不會產生 docx／txt 一致性報告")
def step_沒有_docx_txt_報告(context):
    assert not os.path.exists(
        os.path.join(context.out_dir, "docx_txt_report.md"))
    scripts = os.path.dirname(os.path.abspath(validate_glossing.__file__))
    assert not os.path.exists(os.path.join(scripts, "check_docx_txt.py")), (
        "scripts/check_docx_txt.py 還在")
