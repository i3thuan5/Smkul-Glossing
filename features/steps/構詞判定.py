"""詞根與詞綴判定的 behave step。

每個 scenario 自己帶著原語會標記清單的原始資料,所以不需要語料與
ODS 就能跑。Given 的表格欄位與內容都照 ODS,step 再用與正式程式
同一支 markers_of() 抽出合法標記。
"""

from behave import given, then, when

from scripts.smkul.entry import Entry
from scripts.smkul.markers import markers_of
from scripts.smkul.rules import build_words


@given("在{language}常用構詞標記清單中")
def step_標記清單(context, language):
    rows = []
    for row in context.table:
        values = []
        for heading in context.table.headings:
            values.append(row[heading].strip())
        rows.append(values)
    context.language = language
    context.allowed = markers_of(rows)


@when('切分是 "{segmentation}"，glossing 是 "{gloss}"')
def step_判定(context, segmentation, gloss):
    entry = Entry(
        number="1", start="0", end="1", path="feature",
        segmentation=segmentation, gloss=gloss,
    )
    context.segmentation = segmentation
    context.gloss = gloss
    # 沒有 Given 的 scenario 表示判定不查表,清單當做空的。
    context.words = build_words(entry, getattr(context, "allowed", set()))


@then("判定結果是")
def step_結果(context):
    assert len(context.words) == 1, "應該只有一個詞:" + context.segmentation
    got = []
    for morpheme in context.words[0].morphemes:
        got.append((morpheme.form, morpheme.gloss,
                    morpheme.attachment.value))
    expect = []
    for row in context.table:
        expect.append((row["形"], row["義"], row["構詞"]))
    assert got == expect, (
        "\n切分:" + context.segmentation +
        "\nglossing:" + context.gloss +
        "\n預期:" + str(expect) +
        "\n實際:" + str(got)
    )
