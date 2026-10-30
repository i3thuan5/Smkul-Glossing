"""詞素切割行與詞素翻譯行對應檢查的 behave step。

每個 scenario 自己帶著要比對的兩行，所以不需要語料就能跑。
分類的名稱與 rules.check_correspondence 回傳的一樣。
"""

from behave import then, when

from scripts.smkul.rules import check_correspondence


@when('詞素切割行是 "{segmentation}"，詞素翻譯行是 "{gloss}"')
def step_對應(context, segmentation, gloss):
    context.segmentation = segmentation
    context.gloss = gloss
    found = check_correspondence(segmentation, gloss)
    context.kind, context.left, context.right = found


@then("對應通過")
def step_通過(context):
    assert context.kind is None, (
        "\n詞素切割:" + context.segmentation +
        "\n詞素翻譯:" + context.gloss +
        "\n預期:對應通過"
        "\n實際:" + str(context.kind))


@then('對應不符，分類是 "{kind}"')
def step_不符(context, kind):
    assert context.kind == kind, (
        "\n詞素切割:" + context.segmentation +
        "\n詞素翻譯:" + context.gloss +
        "\n預期:" + kind +
        "\n實際:" + str(context.kind))


@then('對不起來的是詞素切割 "{left}" 對詞素翻譯 "{right}"')
def step_對不起來(context, left, right):
    assert context.left == left, (
        "\n預期詞素切割:" + left + "\n實際詞素切割:" + context.left)
    assert context.right == right, (
        "\n預期詞素翻譯:" + right + "\n實際詞素翻譯:" + context.right)
