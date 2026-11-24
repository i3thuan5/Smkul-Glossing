"""語料的資料型別:檔案 → 段，還有問題分類。"""

import enum
from dataclasses import dataclass, field

from scripts.smkul import languages


class Severity(enum.Enum):
    """問題的嚴重度。ERROR 會影響 exit code，其他不會。

    ERROR、UNSURE、NOTICE 不匯出；EXPORTED_ERROR 與 WARNING 照常匯出。
    宣告的順序就是報告總覽列筆數的順序。
    """

    ERROR = "錯誤"
    EXPORTED_ERROR = "錯誤（照常匯出）"
    WARNING = "警告（照常匯出）"
    UNSURE = "不確定，待檢查"
    NOTICE = "現象"


# 「族語原句與詞素切割不符」的大類名稱。9 個小類各是一種問題,
# 名稱是「大類-小類」。
MISMATCH = "族語原句與詞素切割不符"
MISMATCH_PREFIX = MISMATCH + "-"


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
    # 族語原句與詞素切割不符的 9 個小類。
    # 規格見 features/族語原句詞素切割比對.feature。
    MISMATCH_APOSTROPHE = MISMATCH_PREFIX + "只差單引號"
    MISMATCH_WORDS = MISMATCH_PREFIX + "詞數不同"
    MISMATCH_LENGTH = MISMATCH_PREFIX + "長度差很多"
    MISMATCH_MANY = MISMATCH_PREFIX + "多處不同"
    MISMATCH_LANGUAGE = MISMATCH_PREFIX + "族語和華語不一致"
    MISMATCH_LENGTHENING = MISMATCH_PREFIX + "詞素切割有拉長音"
    MISMATCH_LONG_VOWEL = MISMATCH_PREFIX + "只差長音符號"
    MISMATCH_ONE = MISMATCH_PREFIX + "只差一個字母"
    MISMATCH_FEW = MISMATCH_PREFIX + "差 2-3 個字母"
    # 詞素切割行的標點。規格見 features/詞素切割標點.feature。
    SEGMENT_PUNCTUATION = "詞素切割有標點"
    SEGMENT_SPEAKER_COLON = "詞素切割第一個詞有冒號，可能是語者標記沒空白"
    SEGMENT_PLUS = "非泰雅語的詞素切割不應該用 + 符號"
    # 詞素切割行與詞素翻譯行的對應。這些值與
    # features/詞素切割與詞素翻譯對應.feature 的 Scenario 名一樣。
    GLOSS_FEWER = "詞素切割的詞比詞素翻譯多"
    GLOSS_MORE = "詞素切割的詞比詞素翻譯少"
    GLOSS_CUT_MORE = "詞素切割沒有切，詞素翻譯有切"
    GLOSS_CUT_FEWER = "詞素切割有切，詞素翻譯沒有切"
    SYMBOL_KIND_DIFF = "詞素切割和詞素翻譯的符號不一樣"
    ROOT_BEFORE_INFIX = "詞根放在中綴前面"
    AFFIX_BEFORE_INFIX = "詞綴黏在中綴前面，切割符號在中綴後面"
    # 時間碼。規格見 features/時間碼.feature。
    TIMECODE_MS_DIGITS = "時間碼毫秒位數不對"
    TIMECODE_TYPO = "時間碼行打錯"
    UNKNOWN_TIMECODE_UNIT = "時間碼單位不明"


# 每一種問題的嚴重度。順序就是報告總覽問題表與第 7 章的順序,
# 跟 features/分析報告.feature「每一種問題的嚴重度」那張表一樣(step 會檢查)。
SEVERITY = {
    IssueKind.GLUED_LINE: Severity.ERROR,
    IssueKind.MISSING_GLOSS_LINE: Severity.ERROR,
    IssueKind.MISSING_TRANSLATION: Severity.ERROR,
    IssueKind.STRAY_LINE: Severity.ERROR,
    IssueKind.DUPLICATE_ANNOTATION: Severity.ERROR,
    IssueKind.GLOSS_CUT_MORE: Severity.ERROR,
    IssueKind.GLOSS_CUT_FEWER: Severity.ERROR,
    IssueKind.SYMBOL_KIND_DIFF: Severity.ERROR,
    IssueKind.ROOT_BEFORE_INFIX: Severity.ERROR,
    IssueKind.AFFIX_BEFORE_INFIX: Severity.ERROR,
    IssueKind.GLOSS_FEWER: Severity.ERROR,
    IssueKind.GLOSS_MORE: Severity.ERROR,
    IssueKind.MISMATCH_APOSTROPHE: Severity.ERROR,
    IssueKind.MISMATCH_WORDS: Severity.ERROR,
    IssueKind.MISMATCH_LENGTH: Severity.ERROR,
    IssueKind.MISMATCH_MANY: Severity.ERROR,
    IssueKind.MISMATCH_LANGUAGE: Severity.ERROR,
    IssueKind.MISMATCH_LENGTHENING: Severity.ERROR,
    IssueKind.SEGMENT_PLUS: Severity.ERROR,
    IssueKind.MISMATCH_LONG_VOWEL: Severity.EXPORTED_ERROR,
    IssueKind.SEGMENT_PUNCTUATION: Severity.EXPORTED_ERROR,
    # 時間碼的問題是資料錯,但標注本身沒有問題,所以照常匯出。
    IssueKind.REVERSED_TIMECODE: Severity.WARNING,
    IssueKind.TIMECODE_MS_DIGITS: Severity.WARNING,
    IssueKind.TIMECODE_TYPO: Severity.WARNING,
    IssueKind.UNKNOWN_TIMECODE_UNIT: Severity.WARNING,
    IssueKind.MISMATCH_ONE: Severity.UNSURE,
    IssueKind.MISMATCH_FEW: Severity.UNSURE,
    IssueKind.SEGMENT_SPEAKER_COLON: Severity.UNSURE,
    IssueKind.EMPTY_ENTRY: Severity.NOTICE,
    IssueKind.ORPHAN_TIMECODE: Severity.NOTICE,
    IssueKind.CHINESE_ONLY: Severity.NOTICE,
}


# 不匯出翻譯訓練YAML 的嚴重度。
NOT_EXPORTED = (Severity.ERROR, Severity.UNSURE, Severity.NOTICE)

# 時間不能用的段，開始、結束記成這個數字(不是字串)。
NO_TIME = -1.0


def is_mismatch(kind):
    """是不是「族語原句與詞素切割不符」的小類。"""
    return kind.value.startswith(MISMATCH_PREFIX)


def id_group(kind):
    """算問題 ID 用的大類名稱。

    小類是 2026.11 才拆出來的。ID 用拆開以前的名稱,老師在校對表填過的
    判斷才對得回去;小類改判(例如多處不同改成族語和華語不一致)ID 也不變。
    """
    if is_mismatch(kind):
        return MISMATCH
    if kind in (IssueKind.SEGMENT_SPEAKER_COLON, IssueKind.SEGMENT_PLUS):
        return IssueKind.SEGMENT_PUNCTUATION.value
    return kind.value


def code(text):
    """語料內容要用反引號包起來，markdown 才不會把 <in> 當成 HTML。"""
    return "`" + str(text).replace("`", "'") + "`"


@dataclass
class Issue:
    """一筆問題。path 是相對於語料目錄的路徑。"""

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
        "txt 與 docx 一模一樣，所以是原始 docx 裡就打錯了。"
        "時間不能用，翻譯訓練YAML 的開始、結束記成 -1.0。",
    IssueKind.TIMECODE_MS_DIGITS:
        "毫秒只有一位或兩位數，例如 `00:01:27,53`。53 可以讀成 0.53 秒，"
        "也可以讀成省略前面 0 的 53 毫秒，程式不猜，"
        "翻譯訓練YAML 的開始、結束記成 -1.0。請照錄音補成三位數。",
    IssueKind.TIMECODE_TYPO:
        "編號行的下一行看起來是時間碼，可是解析不了，例如時間碼後面"
        "黏了字、時間打錯。段照常切，翻譯訓練YAML 的開始、結束記成 -1.0。",
    IssueKind.STRAY_LINE:
        "段內有無法歸類的行，例如只有數字的 `0000`、`136.6`。",
    IssueKind.CHINESE_ONLY:
        "整段都是華語，沒有族語標註。而且有三種表法:只有 1 行、"
        "族語原句+華語翻譯 2 行、4 行全是同一句華語。這類一律不匯出。",
    IssueKind.DUPLICATE_ANNOTATION:
        "同一句留了兩版詞素切割與詞素翻譯(修訂沒清乾淨)，不是長句換行。"
        "用族語原句與詞素切割的長度比判斷出來的。",
    IssueKind.MISMATCH_APOSTROPHE:
        "只有喉塞音單引號的有無或位置不同。排灣語 ODS 1-3 規定詞素切割的 "
        "[k] / ['] 要跟著族語原句的寫法，所以這一類多半是要決定哪一邊才對。",
    IssueKind.MISMATCH_WORDS:
        "字母序列一樣，可是詞的個數不一樣——族語原句黏成一個詞、詞素切割拆開"
        "（或相反）。依照「詞數要一個對一個、只有依附詞與詞組例外」，"
        "這種算不符。",
    IssueKind.MISMATCH_LENGTH:
        "長度差四分之一以上，通常是詞素切割比族語原句少了一整串（或多了一整串），"
        "內容可能遺失。",
    IssueKind.MISMATCH_MANY:
        "差很多個字母，可能是換了詞、或族語原句與詞素切割不是同一句。",
    IssueKind.MISMATCH_LANGUAGE:
        "同一個位置的詞，一邊寫族語、一邊寫華語（例如族語原句寫 `moyi`、"
        "詞素切割寫 `母語`）。族語原句和詞素切割要都是族語或都是華語。",
    IssueKind.MISMATCH_LENGTHENING:
        "詞素切割寫了拉長音的 `==`。《常用構詞標記清單》的拉長音「不用標」，"
        "`==` 只該出現在族語原句，詞素切割、詞素翻譯不用標。",
    IssueKind.MISMATCH_LONG_VOWEL:
        "阿美語的長音符號 `:` 兩行不一致，詞素切割要跟族語原句一樣保留。"
        "這是錯誤，但照常匯出。",
    IssueKind.MISMATCH_ONE:
        "只差一個字母，多半是詞素切割時多打或漏打一個音，或是照發音改寫了拼法。"
        "不一定是錯，列為待檢查，請老師看。泰雅、太魯閣、賽德克算通過。",
    IssueKind.MISMATCH_FEW:
        "差 2-3 個字母，通常是拼法慣例不同。不一定是錯，列為待檢查，"
        "請老師看。泰雅、太魯閣、賽德克算通過。",
    IssueKind.SEGMENT_PUNCTUATION:
        "2026.09 會議案由五決議：詞素切割行不能有標點。字母、漢字、數字、"
        "切割符號、詞中間的 `.`、單引號、空白、`＠`，以及書寫系統明定的符號"
        "（阿美語的 `^`、`:`，泰雅語的 `_`、`+` 等）以外的字元都算；"
        "說話者標記（`G:`）不算。這是錯誤，但照常匯出；"
        "每段的提示寫出第幾個詞、應該怎麼改。",
    IssueKind.SEGMENT_SPEAKER_COLON:
        "泰雅語詞素切割的第一個詞裡面有冒號（`Yu:m-uwah`），可能是說話者"
        "標記後面沒有空白，也可能是一般的族語詞。程式建議刪掉冒號，"
        "不一定對，請老師判斷。",
    IssueKind.SEGMENT_PLUS:
        "只有泰雅語可以用 `+` 標示詞組，其他語言的詞組要用 `.`。",
    IssueKind.ROOT_BEFORE_INFIX:
        "有中綴的詞，詞素翻譯把詞根寫在中綴前面（`說<主焦>`），"
        "應該寫在中綴後面（`<主焦>說`）。",
    IssueKind.AFFIX_BEFORE_INFIX:
        "有中綴的詞，詞素翻譯寫成「詞綴<中綴>-詞根」（`使役<主焦>-告訴`），"
        "切割符號跑到中綴後面；應該寫「詞綴-<中綴>詞根」（`使役-<主焦>告訴`）。",
    IssueKind.GLOSS_FEWER:
        "詞素切割行的詞比詞素翻譯行多，兩行沒辦法一個詞對一個詞。",
    IssueKind.GLOSS_MORE:
        "詞素切割行的詞比詞素翻譯行少，兩行沒辦法一個詞對一個詞。",
    IssueKind.GLOSS_CUT_MORE:
        "某一個詞在詞素切割行沒有切，詞素翻譯行卻切了。詞素切割行少了 "
        "`-`、`=`、`<>`、`~` 其中一個。",
    IssueKind.GLOSS_CUT_FEWER:
        "某一個詞在詞素切割行切了，詞素翻譯行卻沒有切。詞素翻譯行少了 "
        "`-`、`=`、`<>`、`~` 其中一個。",
    IssueKind.SYMBOL_KIND_DIFF:
        "某一個詞兩邊的切割符號個數一樣，種類或順序不一樣，"
        "例如詞素切割寫 `-=`、詞素翻譯寫 `==`。",
    IssueKind.UNKNOWN_TIMECODE_UNIT:
        "連字號式時間碼沒有毫秒，程式照 分:秒:影格(30fps)換算成 SRT 字串。"
        "30fps 是從資料推斷的，請對方確認。",
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
    """一段語料:編號、時間碼，還有四行標註。

    start、end 是轉好的 SRT 字串(00:00:27,880);時間不能用的是 NO_TIME。
    規格見 features/時間碼.feature。
    """

    number: str
    start: object
    end: object
    path: str = ""
    body: list = field(default_factory=list)
    source: str = ""
    segmentation: str = ""
    gloss: str = ""
    translation: str = ""
    words: list = field(default_factory=list)
    issues: list = field(default_factory=list)

    def is_clean(self):
        """沒有 ERROR、UNSURE、NOTICE 才可以匯出。"""
        for issue in self.issues:
            if issue.severity in NOT_EXPORTED:
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
    APOSTROPHE = "引號統一為 U+02BC"
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
        "語料混用 U+0027、U+2018、U+2019、U+02BC，同一個詞會變成好幾種寫法，"
        "所以統一成 U+02BC。當引用符號用的引號（`wah!'`、`‘‘…’’`）不轉。",
    NormKind.EN_DASH:
        "詞素翻譯行有時用 en-dash 代替連字號，會與詞素切割行不呼應。",
    NormKind.WHITESPACE:
        "語料用寬空白排列欄位，切 token 時要視為單一分隔。",
    NormKind.LONG_ENTRY_REJOIN:
        "長句的詞素切割行與詞素翻譯行是刻意換行排版的，不是錯誤。",
    NormKind.MISSING_BLANK_LINE:
        "段界以編號行與時間碼行判斷，不依賴段間空行。",
    NormKind.TIMECODE_SPLIT:
        "五種時間碼寫法拆成開始、結束，轉成 SRT 字串；"
        "時間不能用的記成 -1.0。",
    NormKind.HEADER_NOTE:
        "審閱進度、採集標題這類註記不是語料，但也不能丟棄。",
}


# 逐項自動處理對應的 feature 與 Scenario。報告只寫摘要與筆數，
# 例子統一放在 feature，兩邊才不會各寫一份、日久走精。
NORM_FEATURE = {
    NormKind.BOM: ("字元正規化", "移除 BOM（U+FEFF）"),
    NormKind.FULLWIDTH_EQUALS: ("字元正規化", "全形 ＝ 換成半形 ="),
    NormKind.APOSTROPHE: (
        "字元正規化",
        "資料寫 U+0027、U+2018、U+2019、U+02BC 都接受。"
        "之後使用時引號再統一轉成 U+02BC"),
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
