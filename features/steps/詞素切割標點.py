"""詞素切割行標點檢查的 behave step。

每個 scenario 自己帶著族別與詞素切割行，所以不需要語料就能跑。
規格寫在 features/詞素切割標點.feature。
"""

from behave import then, when

from scripts.smkul.parser import check_segment_punctuation


@when('族別是 "{ethnic}"，詞素切割是 "{segmentation}"')
def step_詞素切割(context, ethnic, segmentation):
    context.segmentation = segmentation
    context.result = check_segment_punctuation(segmentation, ethnic)


@then("沒有標點問題")
def step_沒有標點問題(context):
    assert not context.result.hint, (
        "\n詞素切割:" + context.segmentation +
        "\n提示:" + context.result.hint)


@then('提示是 "{hint}"')
def step_提示(context, hint):
    assert context.result.hint == hint, (
        "\n預期:" + hint + "\n實際:" + context.result.hint)


@then('列入待討論 "{label}"')
def step_待討論(context, label):
    assert label in context.result.discuss, (
        "預期列入待討論 " + label + "，實際 " +
        str(sorted(context.result.discuss)))
