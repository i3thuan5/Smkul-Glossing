"""原文與切分逐字比對的 behave step。

每個 scenario 自己帶著要比對的兩行，所以不需要語料就能跑。
分類的名稱與 features/原文切分比對.feature 的 Scenario 一致。
"""

from behave import then, when

from scripts.smkul.parser import compare_source


@when('原文是 "{source}"，切分是 "{segmentation}"')
def step_原文切分(context, source, segmentation):
    context.source = source
    context.segmentation = segmentation
    context.check = compare_source(source, segmentation)


@then("逐字比對通過")
def step_比對通過(context):
    assert context.check.passed, (
        "\n原文:" + context.source +
        "\n切分:" + context.segmentation +
        "\n分類:" + str(context.check.kind) +
        "\n差異:" + context.check.detail)


@then('逐字比對不符，分類是 "{kind}"')
def step_比對不符(context, kind):
    assert not context.check.passed, (
        "這組其實比對通過:" + context.segmentation)
    assert context.check.kind == kind, (
        "預期分類 " + kind + "，實際 " + str(context.check.kind))


@then('差異是 "{detail}"')
def step_差異(context, detail):
    assert context.check.detail == detail, (
        "\n預期:" + detail + "\n實際:" + context.check.detail)


@then("另外記一筆標點不同")
def step_標點不同(context):
    assert context.check.punctuation_differs, "這組的標點其實一樣"
