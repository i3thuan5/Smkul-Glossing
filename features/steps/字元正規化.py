"""字元正規化的 behave step。

每個 scenario 自己帶著要處理的那一行，所以不需要語料就能跑。
規格寫在 features/字元正規化.feature。
"""

from behave import then, when

from scripts.smkul.parser import normalize_line


@when('原本的一行是 "{line}"')
def step_一行(context, line):
    context.result = normalize_line(line)


@then('處理後是 "{expect}"')
def step_處理後(context, expect):
    assert context.result == expect, (
        "\n預期:" + expect + "\n實際:" + context.result)
