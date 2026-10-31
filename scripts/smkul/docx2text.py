"""docx → 段落文字。使用 stdlib 的 zipfile + ElementTree,不依賴第三方套件。

docx 是 zip,內文在 word/document.xml。一個 <w:p> 就是一行,
裡面的 <w:t> 是實際的文字。文字顏色、標亮這類格式層與審閱註解都不處理
(2026.09 會議案由二、三決議忽略)。
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
