"""語料的資料型別:檔案 → 句 → 詞 → 詞素，還有問題分類。"""

import enum
from dataclasses import dataclass, field


class Severity(enum.Enum):
    """問題的嚴重度。ERROR 會影響 exit code，其他不會。"""

    ERROR = "錯誤"
    WARNING = "warning"
    NOTICE = "現象"


class IssueKind(enum.Enum):
    """所有問題的分類。值就是報告裡顯示的名稱。"""

    # 解析結構異常
    GLUED_LINE = "行黏在一起"
    MISSING_GLOSS_SEGMENT = "缺 gloss 段"
    MISSING_TRANSLATION = "缺翻譯行"
    EMPTY_ENTRY = "空組"
    ORPHAN_TIMECODE = "孤兒時間碼"
    REVERSED_TIMECODE = "結束時間早於開始"
    STRAY_LINE = "孤立雜訊行"
    CHINESE_ONLY = "純華語句"
    DUPLICATE_ANNOTATION = "重複標註"
    SOURCE_SEGMENT_MISMATCH = "原文與切分不符"
    PUNCTUATION_DIFF = "標點不同"
    # glossing 驗證。這五類的值與
    # features/切分與glossing對應.feature 的 Scenario 名一樣。
    GLOSS_FEWER = "gloss 的詞比切分少"
    GLOSS_MORE = "gloss 的詞比切分多"
    GLOSS_CUT_MORE = "切分沒有切，gloss 有切"
    GLOSS_CUT_FEWER = "切分有切，gloss 沒有切"
    SYMBOL_KIND_DIFF = "符號的種類不一樣"
    # docx / txt 一致性
    MISSING_FILE = "缺檔"
    FILENAME_MISMATCH = "檔名不一致"
    ENTRY_COUNT_MISMATCH = "組數不同"
    CONTENT_DIFF = "內容差異"
    # warning
    MIXED_TIMECODE_FORMAT = "時間碼格式混用"
    UNKNOWN_TIMECODE_UNIT = "時間碼單位不明"


SEVERITY = {
    IssueKind.GLUED_LINE: Severity.ERROR,
    IssueKind.MISSING_GLOSS_SEGMENT: Severity.ERROR,
    IssueKind.MISSING_TRANSLATION: Severity.ERROR,
    IssueKind.EMPTY_ENTRY: Severity.ERROR,
    IssueKind.ORPHAN_TIMECODE: Severity.ERROR,
    # 時間碼顛倒是資料錯,毋過標註本身無問題,所以照常匯出。
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
    IssueKind.PUNCTUATION_DIFF: Severity.WARNING,
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

    @property
    def severity(self):
        return SEVERITY[self.kind]

    def is_error(self):
        return self.severity is Severity.ERROR


# 逐種問題的說明。報告的「問題類型說明」那一章會用到。
KIND_WHY = {
    IssueKind.GLUED_LINE:
        "兩行黏成一行，多半是翻譯黏在 gloss 行尾，或是下一段的切分"
        "黏在 gloss 行尾。這種組沒辦法自動拆開，要請對方分行。",
    IssueKind.MISSING_GLOSS_SEGMENT:
        "長句分段排版時，某一段有切分卻沒有對應的 gloss 段。",
    IssueKind.MISSING_TRANSLATION:
        "只有原文、切分、gloss 三行，沒有第四行華語翻譯。",
    IssueKind.EMPTY_ENTRY:
        "只有編號與時間碼，沒有任何內文。可能是還沒標，也可能是"
        "這一段本來就沒有話。",
    IssueKind.ORPHAN_TIMECODE:
        "時間碼沒有編號也沒有內文。那一段講的話沒有留下來，"
        "內容可能已經遺失。",
    IssueKind.REVERSED_TIMECODE:
        "同一組的結束時間比開始還早。魯凱霧台 2 有 3 組是這樣，"
        "txt 與 docx 一模一樣，所以是原始 docx 裡就打錯了。",
    IssueKind.STRAY_LINE:
        "組內有無法歸類的行，例如只有數字的 `0000`、`136.6`。",
    IssueKind.CHINESE_ONLY:
        "整組都是華語，沒有族語標註。而且有三種表法:只有 1 行、"
        "原文+翻譯 2 行、4 行全是同一句華語。這類一律不匯出。",
    IssueKind.DUPLICATE_ANNOTATION:
        "同一句留了兩版切分與 gloss(修訂沒清乾淨)，不是長句分段。"
        "用原文與切分的長度比判斷出來的。",
    IssueKind.SOURCE_SEGMENT_MISMATCH:
        "切分行去掉構詞符號後，與原文逐字比對不符。詳細分類見下面。",
    IssueKind.PUNCTUATION_DIFF:
        "原文保留句讀、切分沒有。這不算錯誤、不擋匯出，列出來"
        "是要確認切分行不留句讀是不是預期的慣例。",
    IssueKind.GLOSS_FEWER:
        "gloss 行的詞比切分行少，兩行沒辦法一個詞對一個詞。",
    IssueKind.GLOSS_MORE:
        "gloss 行的詞比切分行多，兩行沒辦法一個詞對一個詞。",
    IssueKind.GLOSS_CUT_MORE:
        "某一個詞在切分行沒有切，gloss 行卻切了。切分行少了 `-`、"
        "`=`、`<>`、`~` 其中一個。",
    IssueKind.GLOSS_CUT_FEWER:
        "某一個詞在切分行切了，gloss 行卻沒有切。gloss 行少了 `-`、"
        "`=`、`<>`、`~` 其中一個。",
    IssueKind.SYMBOL_KIND_DIFF:
        "某一個詞兩邊的切分符號個數一樣，種類或順序不一樣，"
        "例如切分寫 `-=`、gloss 寫 `==`。",
    IssueKind.MISSING_FILE: "docx 與 txt 只有一邊存在。",
    IssueKind.FILENAME_MISMATCH:
        "docx 與 txt 的檔名不完全相同，沒辦法自動配對。",
    IssueKind.ENTRY_COUNT_MISMATCH: "docx 與 txt 的組數不一樣。",
    IssueKind.CONTENT_DIFF: "docx 與 txt 同一組的內容不一樣。",
    IssueKind.MIXED_TIMECODE_FORMAT:
        "同一個檔案裡用了兩種以上的時間碼格式。程式照樣解析，"
        "不算錯誤。",
    IssueKind.UNKNOWN_TIMECODE_UNIT:
        "時間碼沒有毫秒，單位不明(可能是 時:分:秒，也可能是"
        " 分:秒:frame)。程式一律保留原字串不換算。",
}


class Attachment(enum.Enum):
    """詞素的構詞。值直接寫入 YAML 的「構詞」欄。

    分類與判定流程寫在 features/構詞判定.feature 的「判斷方法」。
    UNDECIDED 是詞根分不出來的時候用的(3b、3c),不算錯誤,
    照樣匯出,讓後面的人知道這一段還沒有定論。
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

    def to_yaml(self):
        return {
            "形": self.form,
            "義": self.gloss,
            "構詞": self.attachment.value,
        }


@dataclass
class Word:
    """一個詞:原詞、切分，還有切出來的詞素。"""

    raw: str
    segmentation: str
    morphemes: list = field(default_factory=list)

    def to_yaml(self):
        out = []
        for morpheme in self.morphemes:
            out.append(morpheme.to_yaml())
        return {
            "原詞": self.raw,
            "切分": self.segmentation,
            "詞素": out,
        }


@dataclass
class Entry:
    """一組語料:編號、時間碼，還有四行標註。"""

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

    def is_clean(self):
        """沒有 ERROR 也沒有 NOTICE 才可以匯出。"""
        for issue in self.issues:
            if issue.severity is not Severity.WARNING:
                return False
        return True

    def to_yaml(self):
        out = []
        for word in self.words:
            out.append(word.to_yaml())
        return {
            "編號": self.number,
            "開始": self.start,
            "結束": self.end,
            "族語": self.source,
            "翻譯": self.translation,
            "詞": out,
        }


@dataclass
class CorpusFile:
    """一個語料檔:路徑、族別、語別、檔頭註記，還有全部的組。"""

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
            "語別": self.variant,
            "檔頭註記": self.header_notes,
            "句": out,
        }


class NormKind(enum.Enum):
    """程式自動處理的項目，報告「我們做了哪些自動處理」用的。"""

    BOM = "移除 BOM(U+FEFF)"
    FULLWIDTH_EQUALS = "全形 ＝ → 半形 ="
    APOSTROPHE = "引號統一為 U+0027"
    EN_DASH = "切分行與 gloss 行的 en-dash – → 半形 -"
    WHITESPACE = "多餘空白合併"
    LONG_ENTRY_REJOIN = "長句分段重組"
    MISSING_BLANK_LINE = "組間缺空行照常切組"
    TIMECODE_SPLIT = "時間碼拆開始/結束"
    HEADER_NOTE = "檔頭註記、組內元註記收進 metadata"


NORM_WHY = {
    NormKind.BOM:
        "BOM 會影響第一組的解析。docx 來源通常沒有，規則保留。",
    NormKind.FULLWIDTH_EQUALS:
        "全形＝與半形=同樣是附著詞符號，必須統一才能比對。",
    NormKind.APOSTROPHE:
        "語料混用 U+0027 與 U+2019，同一個詞會變成兩種寫法。",
    NormKind.EN_DASH:
        "gloss 行有時用 en-dash 代替連字號，會與切分行不呼應。",
    NormKind.WHITESPACE:
        "語料用寬空白排列欄位，切 token 時要視為單一分隔。",
    NormKind.LONG_ENTRY_REJOIN:
        "長句的切分行與 gloss 行是刻意分段排版的，不是錯誤。",
    NormKind.MISSING_BLANK_LINE:
        "組界以編號行與時間碼行判斷，不依賴組間空行。",
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
        ("字元正規化", "切分行與 gloss 行的 en-dash – 換成半形 -"),
    NormKind.WHITESPACE: ("字元正規化", "多餘的空白合併成一個"),
    NormKind.LONG_ENTRY_REJOIN: ("排版分析", "長句分段重組——兩段"),
    NormKind.MISSING_BLANK_LINE: ("排版分析", "組間缺空行照常切組"),
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
