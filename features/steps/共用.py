"""好幾個 feature 共用的 behave step。

behave 的 step 是全域的，同一句只能定義一次，所以放在這裡。
族語原句詞素切割比對、詞素切割標點、詞素切割與詞素翻譯對應三個 feature
的 When 都把這次檢查出來的問題清單放進 context.issues。
"""

from behave import then


@then('嚴重度是 "{severity}"')
def step_嚴重度(context, severity):
    assert context.issues, "這次檢查沒有任何問題，沒有嚴重度可以比"
    got = context.issues[-1].severity.value
    assert got == severity, (
        "\n問題:" + context.issues[-1].kind.value +
        "\n預期嚴重度:" + severity + "\n實際嚴重度:" + got)
