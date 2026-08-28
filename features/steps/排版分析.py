"""排版分析（切組、長句分段重組）的 behave step。

每個 scenario 自己帶著要讀的那幾行，所以不需要語料就能跑。
"""

from behave import then, when

from scripts.smkul.parser import build_entry, parse_text


@when("讀入這幾行")
def step_讀入(context):
    context.corpus = parse_text(context.text, path="feature")
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


@then("第 {order:d} 組被判成「{label}」")
def step_判成(context, order, label):
    entry = context.corpus.entries[order - 1]
    kinds = []
    for issue in entry.issues:
        kinds.append(issue.kind.value)
    assert label in kinds, (
        "\n預期:" + label + "\n實際:" + str(kinds))
