"""切分行與 gloss 行對應檢查的 behave step。

每個 scenario 自己帶著要比對的兩行，所以不需要語料就能跑。
分類的名稱與 rules.check_correspondence 回傳的一樣。
"""

from behave import then, when

from scripts.smkul.rules import check_correspondence


@when('切分行是 "{segmentation}"，gloss 行是 "{gloss}"')
def step_對應(context, segmentation, gloss):
    context.segmentation = segmentation
    context.gloss = gloss
    found = check_correspondence(segmentation, gloss)
    context.kind, context.left, context.right = found


@then("對應通過")
def step_通過(context):
    assert context.kind is None, (
        "\n切分:" + context.segmentation +
        "\ngloss:" + context.gloss +
        "\n預期:對應通過"
        "\n實際:" + str(context.kind))


@then('對應不符，分類是 "{kind}"')
def step_不符(context, kind):
    assert context.kind == kind, (
        "\n切分:" + context.segmentation +
        "\ngloss:" + context.gloss +
        "\n預期:" + kind +
        "\n實際:" + str(context.kind))


@then('對不起來的是切分 "{left}" 對 gloss "{right}"')
def step_對袂起來(context, left, right):
    assert context.left == left, (
        "\n預期切分:" + left + "\n實際切分:" + context.left)
    assert context.right == right, (
        "\n預期 gloss:" + right + "\n實際 gloss:" + context.right)
