"""語料的資料型別:檔案 → 段，還有問題分類。"""

import enum
from dataclasses import dataclass, field

from scripts.smkul import languages


class Severity(enum.Enum):
    """問題的嚴重度。ERROR 會影響 exit code，其他不會。

    ERROR 與 NOTICE 不匯出；EXPORTED_ERROR 與 WARNING 照常匯出。
    """

    ERROR = "錯誤"
    EXPORTED_ERROR = "錯誤（照常匯出）"
    WARNING = "警告（照常匯出）"
    NOTICE = "現象"


class IssueKind(enum.Enum):
    """所有問題的分類。值就是報告裡顯示的名稱。"""

    # 解析結構異常
    GLUED_LINE = "行黏在一起"
    MISSING_GLOSS_LINE = "缺詞素翻譯行"
    MISSING_TRANSLATION = "缺華語翻譯行"
    EMPTY_ENTRY = "空段"
    ORPHAN_TIMECODE = "孤兒時間碼"
    REVERSED_TIMECODE = "結束時間早於開始"
    STRAY_LINE = "孤立雜訊行"
    CHINESE_ONLY = "純華語句"
    DUPLICATE_ANNOTATION = "重複標註"
    SOURCE_SEGMENT_MISMATCH = "族語原句與詞素切割不符"
    SEGMENT_PUNCTUATION = "詞素切割有標點"
    # 詞素切割行與詞素翻譯行的對應。這五類的值與
    # features/詞素切割與詞素翻譯對應.feature 的 Scenario 名一樣。
    GLOSS_FEWER = "詞素翻譯的詞比詞素切割少"
    GLOSS_MORE = "詞素翻譯的詞比詞素切割多"
    GLOSS_CUT_MORE = "詞素切割沒有切，詞素翻譯有切"
    GLOSS_CUT_FEWER = "詞素切割有切，詞素翻譯沒有切"
    SYMBOL_KIND_DIFF = "符號的種類不一樣"
    # docx / txt 一致性
    MISSING_FILE = "缺檔"
    FILENAME_MISMATCH = "檔名不一致"
    ENTRY_COUNT_MISMATCH = "段數不同"
    CONTENT_DIFF = "內容差異"
    # warning
    MIXED_TIMECODE_FORMAT = "時間碼格式混用"
    UNKNOWN_TIMECODE_UNIT = "時間碼單位不明"


SEVERITY = {
    IssueKind.GLUED_LINE: Severity.ERROR,
    IssueKind.MISSING_GLOSS_LINE: Severity.ERROR,
    IssueKind.MISSING_TRANSLATION: Severity.ERROR,
    IssueKind.EMPTY_ENTRY: Severity.ERROR,
    IssueKind.ORPHAN_TIMECODE: Severity.ERROR,
    # 時間碼顛倒是資料錯,但標注本身沒有問題,所以照常匯出。
    IssueKind.REVERSED_TIMECODE: Severity.WARNING,
    IssueKind.STRAY_LINE: Severity.ERROR,
    IssueKind.CHINESE_ONLY: Severity.NOTICE,
    IssueKind.DUPLICATE_ANNOTATION: Severity.ERROR,
    IssueKind.SOURCE_SEGMENT_MISMATCH: Severity.ERROR,
    IssueKind.GLOSS_FEWER: Severity.ERROR,
    IssueKind.GLOSS_MORE: Severity.ERROR,
    IssueKind.GLOSS_CUT_MORE: Severity.ERROR,
    IssueKind.GLOSS_CUT_FEWER: Severity.ERROR,
    IssueKind.SYMBOL_KIND_DIFF: Severity.ERROR,
    IssueKind.MISSING_FILE: Severity.ERROR,
    IssueKind.FILENAME_MISMATCH: Severity.ERROR,
    IssueKind.ENTRY_COUNT_MISMATCH: Severity.ERROR,
    IssueKind.CONTENT_DIFF: Severity.ERROR,
    IssueKind.SEGMENT_PUNCTUATION: Severity.EXPORTED_ERROR,
    IssueKind.MIXED_TIMECODE_FORMAT: Severity.WARNING,
    IssueKind.UNKNOWN_TIMECODE_UNIT: Severity.WARNING,
}


def code(text):
    """語料內容要用反引號包起來，markdown 才不會把 <in> 當成 HTML。"""
    return "`" + str(text).replace("`", "'") + "`"


@dataclass
class Issue:
    """一筆問題。path 是相對於 kithann/giliau/ 的路徑。"""

    kind: IssueKind
    path: str
    number: str = ""
    detail: str = ""
    compare: list = field(default_factory=list)
    # 問題 ID,對得到校對表。由 proofreading.IdBook 算。
    id: str = ""

    @property
    def severity(self):
        return SEVERITY[self.kind]

    def is_error(self):
        return self.severity is Severity.ERROR


# 逐種問題的說明。報告的「問題類型說明」那一章會用到。
KIND_WHY = {
    IssueKind.GLUED_LINE:
        "兩行黏成一行，多半是華語翻譯黏在詞素翻譯行尾，或是下一截的"
        "詞素切割黏在詞素翻譯行尾。這種段沒辦法自動拆開，要請對方分行。",
    IssueKind.MISSING_GLOSS_LINE:
        "長句換行排版時，某一截有詞素切割卻沒有對應的詞素翻譯行。",
    IssueKind.MISSING_TRANSLATION:
        "只有族語原句、詞素切割、詞素翻譯三行，沒有第四行華語翻譯。",
    IssueKind.EMPTY_ENTRY:
        "只有編號與時間碼，沒有任何內文。可能是還沒標，也可能是"
        "這一段本來就沒有話。",
    IssueKind.ORPHAN_TIMECODE:
        "時間碼沒有編號也沒有內文。那一段講的話沒有留下來，"
        "內容可能已經遺失。",
    IssueKind.REVERSED_TIMECODE:
        "同一段的結束時間比開始還早。魯凱霧台 2 有 3 段是這樣，"
        "txt 與 docx 一模一樣，所以是原始 docx 裡就打錯了。",
    IssueKind.STRAY_LINE:
        "段內有無法歸類的行，例如只有數字的 `0000`、`136.6`。",
    IssueKind.CHINESE_ONLY:
        "整段都是華語，沒有族語標註。而且有三種表法:只有 1 行、"
        "族語原句+華語翻譯 2 行、4 行全是同一句華語。這類一律不匯出。",
    IssueKind.DUPLICATE_ANNOTATION:
        "同一句留了兩版詞素切割與詞素翻譯(修訂沒清乾淨)，不是長句換行。"
        "用族語原句與詞素切割的長度比判斷出來的。",
    IssueKind.SOURCE_SEGMENT_MISMATCH:
        "詞素切割行去掉切割符號後，與族語原句逐字比對不符。詳細分類見下面。",
    IssueKind.SEGMENT_PUNCTUATION:
        "2026.09 會議案由五決議：詞素切割行不能有標點。字母、漢字、數字、"
        "切割符號、單引號、空白，以及書寫系統明定的符號（阿美語的 `^`、"
        "`:`，泰雅語的 `_` 等）以外的字元都算。這是錯誤，但照常匯出；"
        "每段的提示寫出第幾個詞、應該怎麼改。",
    IssueKind.GLOSS_FEWER:
        "詞素翻譯行的詞比詞素切割行少，兩行沒辦法一個詞對一個詞。",
    IssueKind.GLOSS_MORE:
        "詞素翻譯行的詞比詞素切割行多，兩行沒辦法一個詞對一個詞。",
    IssueKind.GLOSS_CUT_MORE:
        "某一個詞在詞素切割行沒有切，詞素翻譯行卻切了。詞素切割行少了 "
        "`-`、`=`、`<>`、`~` 其中一個。",
    IssueKind.GLOSS_CUT_FEWER:
        "某一個詞在詞素切割行切了，詞素翻譯行卻沒有切。詞素翻譯行少了 "
        "`-`、`=`、`<>`、`~` 其中一個。",
    IssueKind.SYMBOL_KIND_DIFF:
        "某一個詞兩邊的切割符號個數一樣，種類或順序不一樣，"
        "例如詞素切割寫 `-=`、詞素翻譯寫 `==`。",
    IssueKind.MISSING_FILE: "docx 與 txt 只有一邊存在。",
    IssueKind.FILENAME_MISMATCH:
        "docx 與 txt 的檔名不完全相同，沒辦法自動配對。",
    IssueKind.ENTRY_COUNT_MISMATCH: "docx 與 txt 的段數不一樣。",
    IssueKind.CONTENT_DIFF: "docx 與 txt 同一段的內容不一樣。",
    IssueKind.MIXED_TIMECODE_FORMAT:
        "同一個檔案裡用了兩種以上的時間碼格式。程式照樣解析，"
        "不算錯誤。",
    IssueKind.UNKNOWN_TIMECODE_UNIT:
        "時間碼沒有毫秒，單位不明(可能是 時:分:秒，也可能是"
        " 分:秒:frame)。程式一律保留原字串不換算。",
}


class Attachment(enum.Enum):
    """詞素的構詞。只給 features/構詞判定.feature 的草稿用。

    分類與判定流程寫在 features/構詞判定.feature 的「判斷方法」。
    構詞判定已經暫停,報告與 YAML 都不用這個分類。
    UNDECIDED 是詞根分不出來的時候用的(3b、3c),不算錯誤。
    """

    ROOT = "詞根"
    PREFIX = "前綴"
    SUFFIX = "後綴"
    CIRCUMFIX = "環綴"
    INFIX = "中綴"
    CLITIC = "依附詞"
    REDUPLICATION = "重疊"
    UNDECIDED = "無法判斷"


@dataclass
class Morpheme:
    """一個詞素:形、義、構詞。"""

    form: str
    gloss: str
    attachment: Attachment


@dataclass
class Word:
    """一個詞:原詞、詞素切割，還有切出來的詞素。"""

    raw: str
    segmentation: str
    morphemes: list = field(default_factory=list)


@dataclass
class Entry:
    """一段語料:編號、時間碼，還有四行標註。"""

    number: str
    start: str
    end: str
    path: str = ""
    body: list = field(default_factory=list)
    source: str = ""
    segmentation: str = ""
    gloss: str = ""
    translation: str = ""
    words: list = field(default_factory=list)
    issues: list = field(default_factory=list)
    # 詞素切割行裡待討論的符號，{名稱: 處數}，報告的待討論章用。
    discuss: dict = field(default_factory=dict)

    def is_clean(self):
        """沒有 ERROR 也沒有 NOTICE 才可以匯出。"""
        for issue in self.issues:
            if issue.severity in (Severity.ERROR, Severity.NOTICE):
                return False
        return True

    def to_yaml(self):
        return {
            "編號": self.number,
            "開始": self.start,
            "結束": self.end,
            "族語原句": self.source,
            "詞素切割": self.segmentation,
            "詞素翻譯": self.gloss,
            "華語翻譯": self.translation,
        }


@dataclass
class CorpusFile:
    """一個語料檔:路徑、族別、語言別、檔頭註記，還有全部的段。"""

    path: str
    ethnic: str = ""
    variant: str = ""
    header_notes: list = field(default_factory=list)
    entries: list = field(default_factory=list)
    issues: list = field(default_factory=list)
    # {時間碼格式名: 這個檔案裡的一個原字串}。報告的
    # 「語料格式說明」章拿它算各格式的檔數與例子。
    timecode_formats: dict = field(default_factory=dict)

    def all_issues(self):
        out = []
        for issue in self.issues:
            out.append(issue)
        for entry in self.entries:
            for issue in entry.issues:
                out.append(issue)
        return out

    def clean_entries(self):
        out = []
        for entry in self.entries:
            if entry.is_clean():
                out.append(entry)
        return out

    def to_yaml(self):
        out = []
        for entry in self.clean_entries():
            out.append(entry.to_yaml())
        return {
            "路徑": self.path,
            "族別": self.ethnic,
            "語言別": self.variant,
            "語言別代號": languages.code(self.ethnic, self.variant),
            "檔頭註記": self.header_notes,
            "段": out,
        }


class NormKind(enum.Enum):
    """程式自動處理的項目，報告「我們做了哪些自動處理」用的。"""

    BOM = "移除 BOM(U+FEFF)"
    FULLWIDTH_EQUALS = "全形 ＝ → 半形 ="
    APOSTROPHE = "引號統一為 U+0027"
    EN_DASH = "詞素切割行與詞素翻譯行的 en-dash – → 半形 -"
    WHITESPACE = "多餘空白合併"
    LONG_ENTRY_REJOIN = "長句換行重組"
    MISSING_BLANK_LINE = "段間缺空行照常切段"
    TIMECODE_SPLIT = "時間碼拆開始/結束"
    HEADER_NOTE = "檔頭註記、段內元註記收進 metadata"


NORM_WHY = {
    NormKind.BOM:
        "BOM 會影響第一段的解析。docx 來源通常沒有，規則保留。",
    NormKind.FULLWIDTH_EQUALS:
        "全形＝與半形=同樣是附著詞符號，必須統一才能比對。",
    NormKind.APOSTROPHE:
        "語料混用 U+0027 與 U+2019，同一個詞會變成兩種寫法。",
    NormKind.EN_DASH:
        "詞素翻譯行有時用 en-dash 代替連字號，會與詞素切割行不呼應。",
    NormKind.WHITESPACE:
        "語料用寬空白排列欄位，切 token 時要視為單一分隔。",
    NormKind.LONG_ENTRY_REJOIN:
        "長句的詞素切割行與詞素翻譯行是刻意換行排版的，不是錯誤。",
    NormKind.MISSING_BLANK_LINE:
        "段界以編號行與時間碼行判斷，不依賴段間空行。",
    NormKind.TIMECODE_SPLIT:
        "四種時間碼格式統一拆成開始/結束，原字串保留不換算。",
    NormKind.HEADER_NOTE:
        "審閱進度、採集標題這類註記不是語料，但也不能丟棄。",
}


# 逐項自動處理對應的 feature 與 Scenario。報告只寫摘要與筆數，
# 例子統一放在 feature，兩邊才不會各寫一份、日久走精。
NORM_FEATURE = {
    NormKind.BOM: ("字元正規化", "移除 BOM（U+FEFF）"),
    NormKind.FULLWIDTH_EQUALS: ("字元正規化", "全形 ＝ 換成半形 ="),
    NormKind.APOSTROPHE: ("字元正規化", "引號統一成 U+0027"),
    NormKind.EN_DASH:
        ("字元正規化", "詞素切割行與詞素翻譯行的 en-dash – 換成半形 -"),
    NormKind.WHITESPACE: ("字元正規化", "多餘的空白合併成一個"),
    NormKind.LONG_ENTRY_REJOIN: ("排版分析", "長句換行重組——兩截"),
    NormKind.MISSING_BLANK_LINE: ("排版分析", "段間缺空行照常切段"),
    NormKind.TIMECODE_SPLIT: ("時間碼", "逗號式"),
    NormKind.HEADER_NOTE: ("排版分析", "檔頭註記收進 metadata"),
}


# 每項自動處理最多留幾組例。
EXAMPLE_LIMIT = 3


@dataclass
class NormRecord:
    """一項自動處理的統計:幾筆，還有前幾組例。"""

    kind: NormKind
    count: int = 0
    examples: list = field(default_factory=list)

    def note(self, before="", after="", path="", number=""):
        """記一筆。前 3 組留原句子與處理後的句子。"""
        self.count += 1
        if not before and not after:
            return
        if len(self.examples) >= EXAMPLE_LIMIT:
            return
        self.examples.append({
            "原句子": before,
            "處理後": after,
            "檔案": path,
            "編號": number,
        })

    @property
    def why(self):
        return NORM_WHY[self.kind]


class NormLog:
    """整次執行的自動處理統計。"""

    def __init__(self):
        self.records = {}
        for kind in NormKind:
            self.records[kind] = NormRecord(kind)

    def note(self, kind, before="", after="", path="", number=""):
        self.records[kind].note(before, after, path, number)

    def ordered(self):
        """照 NormKind 的宣告順序，沒發生的項目也要列。"""
        out = []
        for kind in NormKind:
            out.append(self.records[kind])
        return out
