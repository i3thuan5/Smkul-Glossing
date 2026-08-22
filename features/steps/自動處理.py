"""自動處理（字元正規化、排版分析、註解殘留、時間碼）的 behave step。

每個 scenario 自己帶著需要的資料，所以不需要語料就能跑。
"""

from behave import given, then, when

from scripts.smkul.parser import (
    collapse_spaces,
    normalize_en_dash,
    normalize_text,
    parse_text,
    parse_timecode,
    strip_comments,
)
from scripts.smkul.parser import build_entry


@when('原本的一行是 "{line}"')
def step_一行(context, line):
    """字元正規化：BOM、全形＝、引號、en-dash、多餘空白。"""
    text = normalize_text(line)
    text = normalize_en_dash(text)
    context.result = collapse_spaces(text)


@then('處理後是 "{expect}"')
def step_處理後(context, expect):
    assert context.result == expect, (
        "\n預期:" + expect + "\n實際:" + context.result)


@when("讀入這幾行")
def step_讀入(context):
    context.raw = context.text
    context.corpus = parse_text(normalize_text(context.text), path="feature")
    for entry in context.corpus.entries:
        build_entry(entry)


@then('第 {order:d} 組重組後的切分是 "{expect}"')
def step_第幾組切分(context, order, expect):
    entry = context.corpus.entries[order - 1]
    assert entry.segmentation == expect, (
        "\n預期:" + expect + "\n實際:" + entry.segmentation)


@then('第 {order:d} 組重組後的 gloss 是 "{expect}"')
def step_第幾組gloss(context, order, expect):
    entry = context.corpus.entries[order - 1]
    assert entry.gloss == expect, (
        "\n預期:" + expect + "\n實際:" + entry.gloss)


@then("切出 {count:d} 組")
def step_組數(context, count):
    got = len(context.corpus.entries)
    assert got == count, "預期 " + str(count) + " 組，實際 " + str(got) + " 組"


@then("檔頭註記是")
def step_檔頭註記(context):
    expect = []
    for row in context.table:
        expect.append(row["註記"])
    got = context.corpus.header_notes
    assert got == expect, "\n預期:" + str(expect) + "\n實際:" + str(got)


@given("docx 的審閱註解是")
def step_註解(context):
    comments = {}
    for row in context.table:
        comments[row["字母"].strip()] = row["內容"].strip()
    context.comments = comments


@when("讀入這幾行有註解殘留")
def step_讀入註解(context):
    context.result = strip_comments(
        context.text, None, "feature", getattr(context, "comments", None))


def _tidy(text):
    """比對的時候，尾端的空行與行尾空白不算差異。"""
    lines = []
    for line in text.split("\n"):
        lines.append(line.rstrip())
    while lines and not lines[-1]:
        lines.pop()
    return "\n".join(lines)


@then("清掉註解後是")
def step_清掉(context):
    got = _tidy(context.result)
    expect = _tidy(context.text)
    assert got == expect, "\n預期:\n" + expect + "\n實際:\n" + got


@when('時間碼行是 "{line}"')
def step_時間碼(context, line):
    context.timecode = parse_timecode(line)
    assert context.timecode is not None, "解析袂出來:" + line


@then('開始是 "{expect}"')
def step_開始(context, expect):
    assert context.timecode[1] == expect, (
        "預期 " + expect + "，實際 " + context.timecode[1])


@then('結束是 "{expect}"')
def step_結束(context, expect):
    assert context.timecode[2] == expect, (
        "預期 " + expect + "，實際 " + context.timecode[2])


@then("第 {order:d} 組被判成「{label}」")
def step_判成(context, order, label):
    entry = context.corpus.entries[order - 1]
    kinds = []
    for issue in entry.issues:
        kinds.append(issue.kind.value)
    assert label in kinds, (
        "\n預期:" + label + "\n實際:" + str(kinds))


@then("這一組記成結束時間早於開始")
def step_時間顛倒(context):
    from scripts.smkul.entry import IssueKind
    from scripts.smkul.parser import timecode_parts
    start = timecode_parts(context.timecode[1])
    end = timecode_parts(context.timecode[2])
    assert end < start, "這組ê結束並無比開始較早"
    assert IssueKind.REVERSED_TIMECODE.value == "結束時間早於開始"


@when('原文是 "{source}"，切分是 "{segmentation}"')
def step_原文切分(context, source, segmentation):
    from scripts.smkul.parser import (bare_form, mismatch_detail,
                                      mismatch_kind, punctuation_of)
    context.source = source
    context.segmentation = segmentation
    context.same = bare_form(source) == bare_form(segmentation)
    context.mismatch_kind = mismatch_kind(source, segmentation)
    context.mismatch_detail = mismatch_detail(source, segmentation)
    context.punctuation_diff = (
        punctuation_of(source) != punctuation_of(segmentation))


@then("逐字比對通過")
def step_比對通過(context):
    assert context.same, (
        "\n原文:" + context.source +
        "\n切分:" + context.segmentation +
        "\n差異:" + context.mismatch_detail)


@then('逐字比對不符，分類是 "{kind}"')
def step_比對不符(context, kind):
    assert not context.same, "這組其實比對通過:" + context.segmentation
    assert context.mismatch_kind == kind, (
        "預期分類 " + kind + "，實際 " + context.mismatch_kind)


@then('差異是 "{detail}"')
def step_差異(context, detail):
    assert context.mismatch_detail == detail, (
        "\n預期:" + detail + "\n實際:" + context.mismatch_detail)


@then("另外記一筆標點不同")
def step_標點不同(context):
    assert context.punctuation_diff, "這組ê標點其實仝款"
