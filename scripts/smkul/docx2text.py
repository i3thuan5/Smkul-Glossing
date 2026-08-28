"""docx → 段落文字。使用 stdlib 的 zipfile + ElementTree,不依賴第三方套件。

docx 是 zip,內文在 word/document.xml。一個 <w:p> 就是一行,
裡面的 <w:t> 是實際的文字。文字顏色、標亮這類格式層這裡不處理
(報告會請對方說明紅字的意思)。
"""

import zipfile
from xml.etree import ElementTree

WORD_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
DOCUMENT = "word/document.xml"
PARAGRAPH = "{" + WORD_NS + "}p"
TEXT = "{" + WORD_NS + "}t"
TAB = "{" + WORD_NS + "}tab"
BREAK = "{" + WORD_NS + "}br"


def paragraph_text(node):
    """一個 <w:p> 裡面的文字。<w:tab> 換成空白,<w:br> 換成換行。"""
    parts = []
    for child in node.iter():
        if child.tag == TEXT:
            if child.text:
                parts.append(child.text)
        elif child.tag == TAB:
            parts.append(" ")
        elif child.tag == BREAK:
            # <w:br> 是段落內的換行,不能變成空白,否則兩行會黏在一起。
            parts.append("\n")
    return "".join(parts)


def docx_paragraphs(path):
    """讀 docx,回傳每一段的文字(照順序,空段也保留)。"""
    out = []
    with zipfile.ZipFile(path) as archive:
        data = archive.read(DOCUMENT)
    root = ElementTree.fromstring(data)
    for node in root.iter(PARAGRAPH):
        out.append(paragraph_text(node))
    return out


def docx_text(path):
    """讀 docx,回傳一行一行的全文,可以直接交給 parser。"""
    return "\n".join(docx_paragraphs(path))


COMMENTS = "word/comments.xml"
COMMENT = "{" + WORD_NS + "}comment"
RANGE_START = "{" + WORD_NS + "}commentRangeStart"
ID = "{" + WORD_NS + "}id"
AUTHOR = "{" + WORD_NS + "}author"
DATE = "{" + WORD_NS + "}date"


def _letter(index):
    """0 → a、1 → b……。匯出 txt 時錨點用的就是這種字母。"""
    if index < 26:
        return chr(ord("a") + index)
    first = chr(ord("a") + index // 26 - 1)
    return first + chr(ord("a") + index % 26)


def docx_comments(path):
    """讀 docx 的審閱註解,照文件順序排列。

    回傳 [{"字母", "id", "作者", "日期", "內容"}]。txt 匯出時,
    每條註解會在內文留下兩個 [字母] 錨點,所以字母可以對應到註解。
    """
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        if COMMENTS not in names:
            return []
        body = archive.read(COMMENTS)
        document = archive.read(DOCUMENT)

    texts = {}
    root = ElementTree.fromstring(body)
    for node in root.iter(COMMENT):
        parts = []
        for text_node in node.iter(TEXT):
            if text_node.text:
                parts.append(text_node.text)
        texts[node.get(ID)] = {
            "作者": node.get(AUTHOR, ""),
            "日期": (node.get(DATE, "") or "")[:10],
            "內容": "".join(parts).strip(),
        }

    out = []
    doc_root = ElementTree.fromstring(document)
    index = 0
    for node in doc_root.iter(RANGE_START):
        comment_id = node.get(ID)
        found = texts.get(comment_id)
        if found is None:
            continue
        item = {"字母": _letter(index), "id": comment_id}
        item.update(found)
        out.append(item)
        index += 1
    return out
