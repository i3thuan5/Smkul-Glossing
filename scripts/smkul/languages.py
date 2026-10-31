"""語言別代號查表。

對照 `data/族語及語言別名稱 - 語言別名稱.csv`(複製自 `kithann/規範/`,
因為 `kithann/` 不進版控)。CSV 的「語言別」欄是族語標準全名(例如
「秀姑巒阿美語」),語料目錄的語言別通常只是地區前綴(例如「秀姑巒」);
兩種目錄命名都有——排灣語系的子目錄本身就含族名(「中排灣」),
阿美語系只有地區前綴(「秀姑巒」)——所以查表時兩種組法都試。
「台/臺」這種異體字也一併試,因為目錄名(霧台)跟 CSV(霧臺)寫法不同。
"""

import csv
import os

CSV_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "data", "族語及語言別名稱 - 語言別名稱.csv",
)


def _load_table(path):
    """讀 CSV,回傳 {語言別: 代號}。"""
    table = {}
    with open(path, encoding="utf-8-sig", newline="") as handle:
        reader = csv.reader(handle)
        next(reader, None)
        for row in reader:
            if len(row) < 4:
                continue
            variant = row[2].strip()
            code = row[3].strip()
            if variant and code:
                table[variant] = code
    return table


def _candidates(ethnic, variant):
    """從族別、語言別猜 CSV 裡的語言別全名,寬版本在前。"""
    if variant == ethnic:
        names = [ethnic + "語"]
    else:
        names = [variant + ethnic + "語", variant + "語"]
    out = []
    for name in names:
        out.append(name)
        out.append(name.replace("台", "臺"))
    return out


def code(ethnic, variant):
    """查語言別代號。查不到回傳空字串,不擋匯出。"""
    table = _load_table(CSV_PATH)
    for name in _candidates(ethnic, variant):
        if name in table:
            return table[name]
    return ""


def split_kind(rel_path):
    """從語料的相對路徑取出族別與語言別。

    `阿美族/秀姑巒/a.docx` → (阿美, 秀姑巒);沒有語言別目錄的
    `太魯閣族/a.docx` → (太魯閣, 太魯閣)。
    """
    parts = rel_path.split(os.sep)
    if len(parts) < 2:
        parts = rel_path.split("/")
    ethnic = parts[0].replace("族", "")
    if len(parts) >= 3:
        variant = parts[1]
    else:
        variant = ethnic
    return ethnic, variant
