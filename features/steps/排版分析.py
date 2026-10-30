"""排版分析（切段、長句換行重組）的 behave step。

每個 scenario 自己帶著要讀的那幾行，所以不需要語料就能跑。
"""

from behave import then, when

from scripts.smkul.parser import build_entry, parse_text


@when("讀入這幾行")
def step_讀入(context):
    context.corpus = parse_text(context.text, path="feature")
    for entry in context.corpus.entries:
        build_entry(entry)


@then('第 {order:d} 段重組後的詞素切割是 "{expect}"')
def step_第幾段詞素切割(context, order, expect):
    entry = context.corpus.entries[order - 1]
    assert entry.segmentation == expect, (
        "\n預期:" + expect + "\n實際:" + entry.segmentation)


@then('第 {order:d} 段重組後的詞素翻譯是 "{expect}"')
def step_第幾段詞素翻譯(context, order, expect):
    entry = context.corpus.entries[order - 1]
    assert entry.gloss == expect, (
        "\n預期:" + expect + "\n實際:" + entry.gloss)


@then("切出 {count:d} 段")
def step_段數(context, count):
    got = len(context.corpus.entries)
    assert got == count, "預期 " + str(count) + " 段，實際 " + str(got) + " 段"


@then("檔頭註記是")
def step_檔頭註記(context):
    expect = []
    for row in context.table:
        expect.append(row["註記"])
    got = context.corpus.header_notes
    assert got == expect, "\n預期:" + str(expect) + "\n實際:" + str(got)


@then("第 {order:d} 段被判成「{label}」")
def step_判成(context, order, label):
    entry = context.corpus.entries[order - 1]
    kinds = []
    for issue in entry.issues:
        kinds.append(issue.kind.value)
    assert label in kinds, (
        "\n預期:" + label + "\n實際:" + str(kinds))
