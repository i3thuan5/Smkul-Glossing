"""詞根與詞綴判定的 behave step。

每個 scenario 自己帶著《常用構詞標記清單》的原始資料，所以不需要
語料與 ODS 就能跑。Given 的表格欄位與內容都照 ODS，step 再用與正式
程式同一支 MarkerList.from_rows() 讀成清單。
規格寫在 features/構詞判定.feature。
"""

from behave import given, then, when

from scripts.smkul.markers import MarkerList
from scripts.smkul.rules import analyse_word


@given("在{language}常用構詞標記清單中")
def step_標記清單(context, language):
    rows = []
    for row in context.table:
        values = []
        for heading in context.table.headings:
            values.append(row[heading].strip())
        rows.append(values)
    context.markers = MarkerList.from_rows(rows)


@when('切分是 "{segmentation}"，glossing 是 "{gloss}"')
def step_判定(context, segmentation, gloss):
    context.segmentation = segmentation
    context.gloss = gloss
    # 沒有 Given 的 scenario 表示判定不查表，清單當做空的。
    markers = getattr(context, "markers", None)
    if markers is None:
        markers = MarkerList.empty()
    context.morphemes = analyse_word(segmentation, gloss, markers)


@then("判定結果是")
def step_結果(context):
    got = []
    for morpheme in context.morphemes:
        got.append((morpheme.form, morpheme.gloss,
                    morpheme.attachment.value))
    expect = []
    for row in context.table:
        # 表格裡寫做（無法判斷），程式的值是「無法判斷」。
        expect.append((row["形"], row["義"], row["構詞"].strip("（）")))
    assert got == expect, (
        "\n切分:" + context.segmentation +
        "\nglossing:" + context.gloss +
        "\n預期:" + str(expect) +
        "\n實際:" + str(got)
    )
