"""時間碼拆開始、結束並轉成 SRT 字串的 behave step。

每個 scenario 自己帶著時間碼那一行，所以不需要語料就能跑。
規格寫在 features/時間碼.feature。
"""

from behave import then, when

from scripts.smkul.entry import NO_TIME
from scripts.smkul.parser import parse_text, parse_timecode


def _一段(text):
    """餵給 parser，回傳 CorpusFile。"""
    return parse_text(text, path="feature")


def _找問題(issues, kind, where):
    """在 issues 裡找名稱是 kind 的問題;找不到就讓 step 失敗。"""
    names = []
    for issue in issues:
        names.append(issue.kind.value)
        if issue.kind.value == kind:
            return issue
    raise AssertionError(
        where + "沒有記「" + kind + "」，程式記的問題:" + str(names))


@when('時間碼行是 "{line}"')
def step_時間碼(context, line):
    """時間碼要放在段裡才會換算、記問題，所以前面補一行編號。"""
    context.timecode_line = line
    assert parse_timecode(line) is not None, "解析不出來:" + line
    context.corpus = _一段("1\n" + line + "\n")
    assert context.corpus.entries, "切不出段:" + line
    context.entry = context.corpus.entries[0]


@then('開始是 "{expect}"')
def step_開始(context, expect):
    got = context.entry.start
    assert got == expect, "預期 " + expect + "，實際 " + str(got)


@then('結束是 "{expect}"')
def step_結束(context, expect):
    got = context.entry.end
    assert got == expect, "預期 " + expect + "，實際 " + str(got)


def _時間不能用(entry):
    assert entry.start == NO_TIME and entry.end == NO_TIME, (
        "預期開始、結束都是 -1.0，實際 " + repr(entry.start) + "、" +
        repr(entry.end))
    assert isinstance(entry.start, float), "-1.0 要是數字，不是字串"


@then("開始與結束都是 -1.0")
def step_時間不能用(context):
    _時間不能用(context.entry)


@then("記一筆「{kind}」")
def step_記一筆(context, kind):
    issue = _找問題(context.entry.issues, kind, "這一段")
    context.issues = [issue]


@then("這個檔案記一筆「{kind}」")
def step_檔案記一筆(context, kind):
    issue = _找問題(context.corpus.issues, kind, "這個檔案")
    context.issues = [issue]


@then("這一段記成結束時間早於開始")
def step_時間顛倒(context):
    issue = _找問題(context.entry.issues, "結束時間早於開始", "這一段")
    context.issues = [issue]


@then("第 {order:d} 段的開始與結束都是 -1.0")
def step_第幾段時間不能用(context, order):
    _時間不能用(context.corpus.entries[order - 1])


@then("第 {order:d} 段記一筆「{kind}」")
def step_第幾段記一筆(context, order, kind):
    entry = context.corpus.entries[order - 1]
    issue = _找問題(entry.issues, kind, "第 " + str(order) + " 段")
    context.issues = [issue]
