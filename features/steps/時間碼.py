"""時間碼拆開始、結束的 behave step。

每個 scenario 自己帶著時間碼那一行，所以不需要語料就能跑。
規格寫在 features/時間碼.feature。
"""

from behave import then, when

from scripts.smkul.entry import IssueKind
from scripts.smkul.parser import parse_text, parse_timecode


@when('時間碼行是 "{line}"')
def step_時間碼(context, line):
    context.timecode_line = line
    context.timecode = parse_timecode(line)
    assert context.timecode is not None, "解析不出來:" + line


@then('開始是 "{expect}"')
def step_開始(context, expect):
    assert context.timecode[1] == expect, (
        "預期 " + expect + "，實際 " + context.timecode[1])


@then('結束是 "{expect}"')
def step_結束(context, expect):
    assert context.timecode[2] == expect, (
        "預期 " + expect + "，實際 " + context.timecode[2])


@then("這一組記成結束時間早於開始")
def step_時間顛倒(context):
    """時間顛倒是組層級的問題，所以要讓程式真的去解析一組。

    這一條只看時間碼，本文是什麼不影響判斷，
    所以只餵編號行加時間碼行。
    """
    text = "1\n" + context.timecode_line + "\n"
    corpus = parse_text(text, path="feature")
    assert corpus.entries, "切不出組:" + context.timecode_line
    kinds = []
    for issue in corpus.entries[0].issues:
        kinds.append(issue.kind)
    assert IssueKind.REVERSED_TIMECODE in kinds, (
        "\n時間碼:" + context.timecode_line +
        "\n程式記的問題:" + str(kinds))
