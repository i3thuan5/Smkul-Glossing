"""詞素切割行標點檢查的 behave step。

每個 scenario 自己帶著族別與詞素切割行，所以不需要語料就能跑。
規格寫在 features/詞素切割標點.feature。
"""

from behave import then, use_step_matcher, when

from scripts.smkul.entry import Issue
from scripts.smkul.parser import check_segment_punctuation

# 族別裡面不會有引號；用 regex 限定，才不會搶走族語原句詞素切割比對的
# 「族別是 …，族語原句是 …，對應詞素切割是 …」。
use_step_matcher("re")


@when('族別是 "(?P<ethnic>[^"]+)"，詞素切割是 "(?P<segmentation>.*)"')
def step_詞素切割(context, ethnic, segmentation):
    context.segmentation = segmentation
    context.result = check_segment_punctuation(segmentation, ethnic)
    context.issues = []
    for kind, finding in context.result.findings.items():
        context.issues.append(Issue(kind, "feature", "1", finding.hint))


use_step_matcher("parse")


@then("沒有標點問題")
def step_沒有標點問題(context):
    assert not context.result.hint, (
        "\n詞素切割:" + context.segmentation +
        "\n提示:" + context.result.hint)


@then('提示是 "{hint}"')
def step_提示(context, hint):
    assert context.result.hint == hint, (
        "\n預期:" + hint + "\n實際:" + context.result.hint)


@then("不用列入待討論")
def step_不用列入待討論(context):
    # 2026.11 刪掉待討論章:說話者標記、泰雅語的 +、詞中間的 . 都是
    # 合法寫法，檢查結果裡不再收集待討論的符號。
    assert not hasattr(context.result, "discuss"), (
        "檢查結果不應該再收集待討論的符號")
