"""讀原語會的《常用構詞標記清單》ODS,建立各語言的合法標記集合。

ODS 是 zip,內容在 content.xml。用 stdlib 的 zipfile + ElementTree,
不依賴第三方套件。要注意 table:number-columns-repeated 要正確展開,
否則欄位會對不上。
"""

import os
import re
import zipfile
from xml.etree import ElementTree

TABLE_NS = "urn:oasis:names:tc:opendocument:xmlns:table:1.0"
TEXT_NS = "urn:oasis:names:tc:opendocument:xmlns:text:1.0"
TABLE = "{" + TABLE_NS + "}table"
ROW = "{" + TABLE_NS + "}table-row"
CELL = "{" + TABLE_NS + "}table-cell"
NAME = "{" + TABLE_NS + "}name"
REPEAT = "{" + TABLE_NS + "}number-columns-repeated"
PARAGRAPH = "{" + TEXT_NS + "}p"

CONTENT = "content.xml"
ODS_PATH = os.path.join(
    "kithann", "giliau", "原語會提供-常用構詞標記清單_0713.ods")

# 一格如果重複這麼多次,那是排版用的空白格,不是真的資料。
MAX_REPEAT = 50

# 表頭是:大類 | 編號 | 類別 | 詞綴或詞 | 族語範例 | 詞素翻譯 | 備註。
# 不過只有每個大類的第一列才有「大類」那一格,其他列會少一欄,
# 所以要用「編號」欄(1-1、4-12 這種)當錨點來定位。
NUMBER = re.compile(r'^\d+-\d+$')
# 切分符號。詞素翻譯要照這些符號拆開,才拿得到單一標記。
SPLITTERS = "-=<>~"

OFFSET_CATEGORY = 1
OFFSET_AFFIX = 2
OFFSET_GLOSS = 4

# 語料目錄 → ODS 的 sheet 名。目前只有這六種語言交付語料。
SHEET_OF = {
    "阿美族": "阿美語",
    "排灣族": "排灣語",
    "泰雅族": "泰雅語",
    "布農族": "布農語",
    "太魯閣族": "太魯閣語",
    "魯凱族": "霧台魯凱語",
}


def sheet_for(rel_path):
    """語料相對路徑 → sheet 名。找不到回傳空字串。"""
    parts = rel_path.replace(os.sep, "/").split("/")
    if not parts:
        return ""
    return SHEET_OF.get(parts[0], "")


def cell_text(cell):
    parts = []
    for node in cell.iter(PARAGRAPH):
        for text in node.itertext():
            parts.append(text)
        parts.append(" ")
    return " ".join("".join(parts).split())


def row_values(row):
    """一列的每一格,重複的格子要展開。"""
    values = []
    for cell in row.findall(CELL):
        times = 1
        repeat = cell.get(REPEAT)
        if repeat is not None and repeat.isdigit():
            times = int(repeat)
            if times > MAX_REPEAT:
                times = 1
        text = cell_text(cell)
        for _ in range(times):
            values.append(text)
    while values and not values[-1]:
        values.pop()
    return values


def read_sheets(path=ODS_PATH):
    """讀 ODS,回傳 {sheet 名: [每一列的值]}。"""
    with zipfile.ZipFile(path) as archive:
        data = archive.read(CONTENT)
    root = ElementTree.fromstring(data)
    sheets = {}
    for table in root.iter(TABLE):
        rows = []
        for row in table.iter(ROW):
            values = row_values(row)
            if values:
                rows.append(values)
        sheets[table.get(NAME)] = rows
    return sheets


def split_gloss(text):
    """把詞素翻譯照切分符號拆開,回傳每一段。"""
    out = []
    current = []
    for char in text:
        if char in SPLITTERS:
            if current:
                out.append("".join(current).strip())
                current = []
        else:
            current.append(char)
    if current:
        out.append("".join(current).strip())
    clean = []
    for item in out:
        if item and " " not in item:
            clean.append(item)
    return clean


def affix_position(affix):
    """看「詞綴或詞」欄的寫法,判斷這個標記在 gloss 的哪個位置。

    `mi-` 前綴 → gloss 的第一段;`-un` 後綴、`=in` 附著 → 最後一段;
    `<om>` 中綴 → 中綴那一段;都不是(獨立詞)→ 不取。
    """
    affix = affix.strip()
    if not affix:
        return ""
    if affix.startswith("<") and affix.endswith(">"):
        return "中綴"
    if affix.endswith("-") or affix.endswith("="):
        return "頭"
    if affix.startswith("-") or affix.startswith("="):
        return "尾"
    return ""


def marker_from_gloss(gloss, position):
    """照位置從詞素翻譯取出標記那一段。"""
    if position == "中綴":
        found = re.findall(r'<([^>]*)>', gloss)
        if found:
            return found[0].strip()
        return ""
    parts = split_gloss(gloss)
    if not parts:
        return ""
    if position == "頭":
        return parts[0]
    return parts[-1]


def number_column(values):
    """找出「編號」欄的位置(1-1、4-12 這種)。找不到回傳 -1。"""
    for index, value in enumerate(values):
        if NUMBER.match(value):
            return index
    return -1


def markers_of(rows):
    """一個 sheet 的合法標記集合。

    兩個來源:
    1. 類別欄——本身就是標記名(主焦、受焦、完成貌……)。
    2. 詞綴或詞欄 + 詞素翻譯欄——照詞綴的位置(前綴/後綴/中綴)
       從詞素翻譯取出對應的那一段。這樣才不會把詞根的實詞意譯
       (書、學習、說話……)誤收成語法標記。
    """
    found = set()
    for values in rows:
        anchor = number_column(values)
        if anchor < 0:
            continue
        category = anchor + OFFSET_CATEGORY
        if len(values) > category:
            label = values[category]
            if label and " " not in label and len(label) <= 12:
                found.add(label)
        affix = anchor + OFFSET_AFFIX
        gloss = anchor + OFFSET_GLOSS
        if len(values) > gloss and len(values) > affix:
            position = affix_position(values[affix])
            if position:
                marker = marker_from_gloss(values[gloss], position)
                if marker and len(marker) <= 12:
                    found.add(marker)
        # 中綴的 gloss 有時寫在詞素翻譯裡(例如 參焦<經驗貌>說),
        # 詞綴欄卻只寫 s-,所以再撈一次 <...>。
        if len(values) > gloss:
            for infix in re.findall(r'<([^>]*)>', values[gloss]):
                infix = infix.strip()
                if infix and " " not in infix and len(infix) <= 12:
                    found.add(infix)
    found.discard("")
    return _with_parts(found)


def _with_parts(markers):
    """標記可以用 . 串幾個屬性(主焦.祈使)。子標記也要算數,
    語料常常只用其中一段。"""
    out = set()
    for marker in markers:
        out.add(marker)
        if "." in marker:
            for part in marker.split("."):
                part = part.strip()
                if part:
                    out.add(part)
    return out


# 環綴tī「詞綴或詞」欄ê寫法:pi-...-i、ki-...-an。
CIRCUMFIX = re.compile(r'^([^\s.]+)-\.\.\.-([^\s.]+)$')


def circumfixes_of(rows):
    """一个 sheet 有登記ê環綴,用頭尾兩段ê gloss 做鑰匙。

    ODS 4-29「祈使 | pi-...-i | pi-tengil-i | PI-聽-祈使」,
    掠出來就是 ("PI", "祈使")。判定ê時陣,一个詞ê頭尾兩段 gloss
    對著這組,兩爿就攏標做環綴(判斷方法 1c)。
    """
    found = set()
    for values in rows:
        anchor = number_column(values)
        if anchor < 0:
            continue
        affix = anchor + OFFSET_AFFIX
        gloss = anchor + OFFSET_GLOSS
        if len(values) <= gloss or len(values) <= affix:
            continue
        if not CIRCUMFIX.match(values[affix].strip()):
            continue
        parts = split_gloss(values[gloss])
        if len(parts) < 2:
            continue
        found.add((parts[0], parts[-1]))
    return found


# 詞綴或詞欄有幾若个形ê時,用 ; 抑是 , 分開(像 -u;-i);
# 一條環綴嘛會有幾若段(lri-ki-)。
FORM_SPLIT = re.compile(r'[;,\-=<>~\s]+')


def _concrete_forms(text):
    """共詞綴欄拆做一个一个ê形。

    漢字寫ê(「重疊-」)是位置ê講法,毋是實際ê形,袂收。
    """
    out = set()
    for piece in FORM_SPLIT.split(text.strip()):
        piece = piece.strip()
        if not piece:
            continue
        han = False
        for char in piece:
            if "一" <= char <= "鿿":
                han = True
                break
        if han:
            continue
        out.add(piece)
    return out


def _is_affix_row(affix_text, example):
    """這一列登記ê是詞綴抑是詞。

    詞綴欄本身有 -、=、<> ê就是詞綴;無ê時陣閣看族語範例——
    9-28「還｜ho」範例寫 `k<om>aen-ay=ho`,`=ho` 表示伊是依附詞。
    9-79「以後｜anoayaw」範例干焦 `anoayaw`,無黏tī別个詞頂懸,
    彼是詞,毋是詞綴。
    """
    if affix_position(affix_text):
        return True
    form = affix_text.strip()
    if not form or " " in form:
        return False
    for mark in ("-", "=", "<", ">"):
        if mark + form in example or form + mark in example:
            return True
    return False


def affix_forms_of(rows):
    """一个 sheet ê {標記: 這个標記登記ê詞綴形}。

    清單登記ê是某一个詞綴ê形佮意思(4-32「去｜ma-」講ê是「前綴
    ma- ê意思是去」),毋是「凡是 gloss 寫『去』ê攏算詞綴」。
    所以查表ê時陣形嘛愛對會著——看 features/構詞判定.feature
    判斷方法 1f。

    無tī這搭ê標記表示清單無共伊登記做詞綴(登記做詞,像 9-79
    「以後｜anoayaw」),彼款毋算詞綴。有tī這搭毋過集合是空ê,
    表示是詞綴毋過無實際ê形通對(像「重疊-」),按呢就干焦看 gloss。
    """
    out = {}
    for values in rows:
        anchor = number_column(values)
        if anchor < 0:
            continue
        affix = anchor + OFFSET_AFFIX
        gloss = anchor + OFFSET_GLOSS
        category = anchor + OFFSET_CATEGORY
        if len(values) <= affix:
            continue
        if len(values) > gloss:
            example = values[anchor + OFFSET_AFFIX + 1]
        else:
            example = ""
        if not _is_affix_row(values[affix], example):
            continue
        position = affix_position(values[affix])
        names = []
        if position and len(values) > gloss:
            found = marker_from_gloss(values[gloss], position)
            if found:
                names.append(found)
        if len(values) > category and values[category].strip():
            names.append(values[category].strip())
        forms = _concrete_forms(values[affix])
        for name in names:
            out.setdefault(name, set()).update(forms)
    return out


# 全大寫拉丁字母的 gloss 是 ODS 1-2 的「不確定」標記，合法但要統計。
UNCERTAIN = re.compile(r"^'?[A-Z]+$")

# 重疊的形是詞根自己的翻頭，沒辦法在清單登記成固定的形，所以
# 重疊免對形（判斷方法 1e、1f）。
REDUPLICATION_GLOSS = "重疊"


def head_of(gloss):
    """一個詞素可以用 . 串幾個屬性，查表時看第一個。"""
    if "." in gloss:
        return gloss.split(".")[0]
    return gloss


def is_uncertain(gloss):
    """ODS 1-2 的「不確定」標記：全大寫拉丁字母，或是 ?。

    排灣語有 'I、'A 這種帶喉塞音的寫法，也算。用 . 串接時
    （AN.主格）看第一段。
    """
    gloss = gloss.strip()
    if gloss == "?":
        return True
    if UNCERTAIN.match(gloss):
        return True
    return bool(UNCERTAIN.match(head_of(gloss)))


def _is_focus(gloss):
    """焦點標記（主焦、受焦、處焦、工具焦……）的 gloss 都是「焦」結尾。"""
    return gloss.endswith("焦")


class MarkerList:
    """一個語言的《常用構詞標記清單》。

    ODS 一個 sheet 就是一個語言。清單有三種用法，全部收在這裡：
    allowed 是合法的標記名，circumfixes 是登記過的環綴頭尾組合，
    affix_forms 是每個標記登記過的詞綴形。判定要查的是「這一段是
    不是詞綴」，所以對外只給 is_marker 與 circumfix_pair 兩支。
    查表的規則寫在 features/構詞判定.feature 的判斷方法 1b、1c、1d、1f。
    """

    def __init__(self, allowed=None, circumfixes=None, affix_forms=None):
        self.allowed = allowed or set()
        self.circumfixes = circumfixes or set()
        self.affix_forms = affix_forms or {}

    @classmethod
    def from_rows(cls, rows):
        """由 ODS 一個 sheet 的列建清單。"""
        return cls(
            allowed=markers_of(rows),
            circumfixes=circumfixes_of(rows),
            affix_forms=affix_forms_of(rows),
        )

    @classmethod
    def empty(cls):
        """空清單。判定不查表的時候用。"""
        return cls()

    def form_fits(self, form, gloss):
        """這一段的形對不對得上清單登記的詞綴形（判斷方法 1f）。

        清單登記的是某一個詞綴的形與意思，所以 gloss 對上了還不夠，
        形也要對得上。清單若沒有把這個 gloss 登記成詞綴（登記成詞，
        像 9-79「以後｜anoayaw」），就沒有形可以對，那一段不算詞綴；
        有登記成詞綴但沒有實際的形（像「重疊-」），就只看 gloss。
        """
        if head_of(gloss) == REDUPLICATION_GLOSS:
            return True
        if gloss not in self.affix_forms:
            return False
        registered = self.affix_forms[gloss]
        if not registered:
            return True
        return form.strip() in registered

    def is_marker(self, form, gloss):
        """這一段是不是語法標記（判斷方法 1b、1d、1f）。

        完全對上清單、形也對得上的才算標記；全大寫的不確定標記
        沒有形可以對，照算（1b）。用 . 串幾個屬性的時候看第一段，
        但是「焦點後面還有內容」（像「主焦.去」）照 1d 是詞根的候選。
        """
        gloss = gloss.strip()
        if not gloss:
            return False
        if is_uncertain(gloss):
            return True
        if gloss in self.allowed:
            return self.form_fits(form, gloss)
        head = head_of(gloss)
        if head == gloss:
            return False
        if _is_focus(head):
            return False
        if head in self.allowed:
            return self.form_fits(form, head)
        return False

    def circumfix_pair(self, glosses):
        """頭尾兩段是不是清單登記過的環綴（判斷方法 1c）。"""
        if len(glosses) < 2 or not self.circumfixes:
            return False
        pair = (glosses[0][0].strip(), glosses[-1][0].strip())
        return pair in self.circumfixes


def load_marker_lists(path=ODS_PATH):
    """回傳 {sheet 名: MarkerList}。"""
    out = {}
    for name, rows in read_sheets(path).items():
        out[name] = MarkerList.from_rows(rows)
    return out
