"""測試 parser.py 裡 feature 沒有涵蓋的部份。

字元正規化、排版分析、時間碼、族語原句詞素切割比對的規則都寫在對應的
features/*.feature，由 behave 測。這裡只留 feature 測不到的:
自動處理的計數、feature 沒有例子的錯誤分類、病態段。
Fixture 都是從真語料抽出來的。
"""

import os
import unittest

from tests import DATA

from scripts.smkul.entry import IssueKind, NormKind, NormLog
from scripts.smkul.parser import (
    assemble_entry,
    bare_form,
    build_entry,
    check_segment_punctuation,
    normalize_en_dash,
    parse_text,
    parse_timecode,
    timecode_parts,
)


def load(name):
    path = os.path.join(DATA, name)
    with open(path, encoding="utf-8") as handle:
        return handle.read()


def parse(name, log=None):
    return parse_text(load(name), path=name, log=log)


class TestTimecode(unittest.TestCase):
    """四種格式都要拆成開始/結束,而且保留原字串。"""

    def test_編號與時間碼同行(self):
        got = parse_timecode("1. 0:00:00.000,0:00:01.480")
        self.assertEqual(got[0], "1")
        self.assertEqual(got[1], "0:00:00.000")

    def test_不是時間碼(self):
        self.assertIsNone(parse_timecode("Kiya ha, Tku ita mnswayi"))
        self.assertIsNone(parse_timecode("1."))


class TestNormalize(unittest.TestCase):

    def test_沒有_endash_就不計數(self):
        log = NormLog()
        got = normalize_en_dash("PI-書-處焦", log, "a.txt", "79")
        self.assertEqual(got, "PI-書-處焦")
        self.assertEqual(log.records[NormKind.EN_DASH].count, 0)


class TestSplitEntries(unittest.TestCase):

    def test_典型_連字號式_會記單位不明(self):
        corpus = parse("典型_連字號式.txt")
        kinds = []
        for issue in corpus.issues:
            kinds.append(issue.kind)
        self.assertIn(IssueKind.UNKNOWN_TIMECODE_UNIT, kinds)
        self.assertEqual(corpus.entries[0].end, "00:04:21")

    def test_編號同行(self):
        corpus = parse("編號同行.txt")
        self.assertEqual(len(corpus.entries), 2)
        self.assertEqual(corpus.entries[0].number, "1")
        self.assertEqual(corpus.entries[1].number, "2")

    def test_格式中途切換會記_warning(self):
        corpus = parse("格式中途切換.txt")
        kinds = []
        for issue in corpus.issues:
            kinds.append(issue.kind)
        self.assertIn(IssueKind.MIXED_TIMECODE_FORMAT, kinds)

    def test_孤兒時間碼(self):
        corpus = parse("病態_孤兒時間碼.txt")
        orphans = []
        for entry in corpus.entries:
            for issue in entry.issues:
                if issue.kind is IssueKind.ORPHAN_TIMECODE:
                    orphans.append(issue)
        self.assertEqual(len(orphans), 1)

    def test_全形等號_解析後沒有全形(self):
        log = NormLog()
        corpus = parse("正規化_全形等號.txt", log)
        for entry in corpus.entries:
            for line in entry.body:
                self.assertNotIn("＝", line)
        self.assertTrue(log.records[NormKind.FULLWIDTH_EQUALS].count >= 1)


class TestAssemble(unittest.TestCase):
    """組四行:標準段、長句換行重組、重複標註。"""

    def assemble_all(self, name, log=None):
        corpus = parse(name, log)
        out = []
        for entry in corpus.entries:
            out.append((entry, assemble_entry(entry, log)))
        return out

    def test_endash_詞素翻譯_重組後換半形(self):
        log = NormLog()
        entry, ok = self.assemble_all("正規化_endash_詞素翻譯.txt", log)[0]
        self.assertTrue(ok)
        self.assertNotIn("–", entry.gloss)
        self.assertIn("PI-書-處焦", entry.gloss)
        self.assertEqual(log.records[NormKind.EN_DASH].count, 1)

    def test_重複標註_不可以組起來(self):
        """南排灣 4 第 156、157 段是同一句留兩版,不是換行。"""
        results = self.assemble_all("病態_重複標註.txt")
        self.assertEqual(len(results), 2)
        for entry, ok in results:
            self.assertFalse(ok)
            kinds = []
            for issue in entry.issues:
                kinds.append(issue.kind)
            self.assertIn(IssueKind.DUPLICATE_ANNOTATION, kinds)
            self.assertFalse(entry.is_clean())

    def test_病態段都組不起來(self):
        names = [
            "病態_黏行.txt",
            "病態_缺詞素翻譯行.txt",
            "病態_缺華語翻譯行.txt",
            "病態_雜訊行.txt",
        ]
        for name in names:
            for entry, ok in self.assemble_all(name):
                self.assertFalse(ok, name + " 第" + entry.number + "段")


class TestSourceSegmentation(unittest.TestCase):
    """嚴格用族語原句檢查詞素切割:差一個字母或單引號就算錯誤。"""

    def check(self, name, index=0):
        corpus = parse(name)
        entry = corpus.entries[index]
        assemble_entry(entry)
        kinds = []
        for issue in entry.issues:
            kinds.append(issue.kind)
        return entry, kinds

    def test_bare_form_留單引號_去掉標點大小寫(self):
        self.assertEqual(bare_form("Kiya ha, Tku"), "kiyahatku")
        self.assertEqual(bare_form("’ana ne’a"), "'anane'a")
        self.assertEqual(
            bare_form("pi-sano-Amis a caciyaw awa=to"),
            "pisanoamisacaciyawawato",
        )

    def test_bare_form_留阿美語的_喉塞音字母(self):
        # 《原住民族語言書寫系統》的阿美語，^ 是喉塞音字母。
        self.assertEqual(bare_form("pa^tang"), "pa^tang")

    def test_bare_form_去掉書寫系統的符號(self):
        # 阿美語的長音 :、泰雅語的 _ 是符號，不是字母。
        self.assertEqual(bare_form("iti:raw"), "itiraw")
        self.assertEqual(bare_form("m_yan"), "myan")


class TestClassify(unittest.TestCase):
    """組不起來的段,要分得出是哪一種異常。"""

    def kinds_of(self, name):
        corpus = parse(name)
        out = []
        for entry in corpus.entries:
            build_entry(entry)
            labels = []
            for issue in entry.issues:
                labels.append(issue.kind)
            out.append((entry.number, labels))
        return out

    def test_空段(self):
        got = self.kinds_of("病態_空段.txt")
        self.assertIn(IssueKind.EMPTY_ENTRY, got[0][1])
        # 第 2 段是正常的段,但族語原句 `O na` 詞素切割寫成 `Ona`,
        # 詞數對不起來——照族語原句詞素切割比對.feature「只差空白，
        # 先算不通過」那條,這算「族語原句與詞素切割不符」。
        self.assertEqual(
            got[1][1], [IssueKind.SOURCE_SEGMENT_MISMATCH])

    def test_孤兒時間碼(self):
        got = self.kinds_of("病態_孤兒時間碼.txt")
        self.assertIn(IssueKind.ORPHAN_TIMECODE, got[2][1])

    def test_雜訊行(self):
        got = self.kinds_of("病態_雜訊行.txt")
        self.assertIn(IssueKind.STRAY_LINE, got[0][1])

    def test_布農的_0000_也是雜訊(self):
        got = self.kinds_of("布農雜訊.txt")
        self.assertIn(IssueKind.STRAY_LINE, got[0][1])

    def test_純華語句_三種表法(self):
        got = self.kinds_of("病態_純華語句.txt")
        for number, labels in got:
            self.assertIn(IssueKind.CHINESE_ONLY, labels, number)

    def test_缺華語翻譯行(self):
        got = self.kinds_of("病態_缺華語翻譯行.txt")
        for number, labels in got:
            self.assertIn(IssueKind.MISSING_TRANSLATION, labels, number)

    def test_行黏在一起(self):
        got = self.kinds_of("病態_黏行.txt")
        for number, labels in got:
            self.assertIn(IssueKind.GLUED_LINE, labels, number)

    def test_缺詞素翻譯行(self):
        got = self.kinds_of("病態_缺詞素翻譯行.txt")
        self.assertIn(IssueKind.MISSING_GLOSS_LINE, got[0][1])

    def test_重複標註不會再分成別種(self):
        got = self.kinds_of("病態_重複標註.txt")
        for number, labels in got:
            self.assertEqual(labels, [IssueKind.DUPLICATE_ANNOTATION])

    def test_正常的段沒問題(self):
        for name in ("典型_srt式.txt", "長句換行.txt"):
            corpus = parse(name)
            for entry in corpus.entries:
                build_entry(entry)
                for issue in entry.issues:
                    self.assertIsNot(issue.kind, IssueKind.GLUED_LINE)


class TestPunctuation(unittest.TestCase):
    """族語原句有標點、詞素切割沒有，算通過，不記任何問題。"""

    def test_族語原句有標點_詞素切割沒有_不記任何問題(self):
        corpus = parse("典型_逗號式.txt")
        entry = corpus.entries[0]
        build_entry(entry)
        self.assertIn(",", entry.source)
        self.assertNotIn(",", entry.segmentation)
        self.assertEqual(entry.issues, [])


def segment_entry(segmentation, source=None, ethnic=""):
    """用一段四行的語料組出 Entry，跑過 build_entry。"""
    if source is None:
        source = segmentation
    text = "1\n0:00:00.000,0:00:02.000\n" + source + "\n" + \
        segmentation + "\n詞\n華語\n"
    corpus = parse_text(text, path="t.txt", ethnic=ethnic)
    entry = corpus.entries[0]
    build_entry(entry, ethnic=ethnic)
    return entry


class TestSegmentPunctuation(unittest.TestCase):
    """詞素切割行不能有標點。規格見 features/詞素切割標點.feature。"""

    def hint(self, segmentation, ethnic):
        return check_segment_punctuation(segmentation, ethnic).hint

    def test_詞尾標點_刪掉(self):
        self.assertEqual(
            self.hint("iq kiya.", "太魯閣"),
            "詞素切割第 2 個詞的 `kiya.` 有標點「.」，程式判斷要刪掉，"
            "因為詞素切割不能有標點，應該寫是 `kiya`",
        )

    def test_一個詞好幾種標點_依出現順序列(self):
        self.assertEqual(
            self.hint("azua?!", "排灣"),
            "詞素切割第 1 個詞的 `azua?!` 有標點「?」「!」，程式判斷要刪掉，"
            "因為詞素切割不能有標點，應該寫是 `azua`",
        )

    def test_只有符號的詞_整個詞刪掉_寫整行(self):
        self.assertEqual(
            self.hint("pa-'a-pazangal ＠", "排灣"),
            "詞素切割第 2 個詞的 `＠` 有符號「＠」，程式判斷要整個詞刪掉，"
            "因為詞素切割不能有標點，應該寫是 `pa-'a-pazangal`",
        )

    def test_括號_程式無法判斷(self):
        self.assertEqual(
            self.hint("nu a(ne)ma.aya-a(ne)ma.aya='en", "排灣"),
            "詞素切割第 2 個詞的 `a(ne)ma.aya-a(ne)ma.aya='en` 有括號「()」，"
            "程式無法判斷，請標注者確認",
        )

    def test_好幾個詞_用分號接起來(self):
        self.assertEqual(
            self.hint("aji. uri. o brah", "太魯閣"),
            "詞素切割第 1 個詞的 `aji.` 有標點「.」，程式判斷要刪掉，"
            "因為詞素切割不能有標點，應該寫是 `aji`；"
            "詞素切割第 2 個詞的 `uri.` 有標點「.」，程式判斷要刪掉，"
            "因為詞素切割不能有標點，應該寫是 `uri`",
        )

    def test_阿美語的_喉塞音與長音不算標點(self):
        self.assertEqual(self.hint("Ma-so^so haw", "阿美"), "")
        self.assertEqual(self.hint("O no iti:ya-ay=ho sanay", "阿美"), "")

    def test_別的語言的_喉塞音符號算標點(self):
        self.assertIn("有標點「^」", self.hint("pa^tang", "排灣"))

    def test_泰雅語的底線不算標點(self):
        self.assertEqual(self.hint("k_yaqih hi=nya", "泰雅"), "")

    def test_別的語言的底線算標點(self):
        self.assertIn("有標點「_」", self.hint("k_yaqih", "排灣"))

    def test_邵語的點與賽夏語的冒號不算標點(self):
        self.assertEqual(self.hint("put.huum", "邵"), "")
        self.assertEqual(self.hint("lamo:", "賽夏"), "")

    def test_加號_不算標點_列入待討論(self):
        result = check_segment_punctuation("la+ga yan+ka", "泰雅")
        self.assertEqual(result.hint, "")
        self.assertEqual(result.discuss["+"], 2)

    def test_詞中間的點_列入待討論(self):
        result = check_segment_punctuation("kika kiya.ga", "太魯閣")
        self.assertEqual(result.hint, "")
        self.assertEqual(result.discuss["詞中間的 ."], 1)

    def test_詞頭的點仍算標點(self):
        result = check_segment_punctuation("nanu.yasa .qu", "泰雅")
        self.assertIn("`.qu` 有標點「.」", result.hint)
        self.assertEqual(result.discuss["詞中間的 ."], 1)

    def test_獨立的說話者標記_列入待討論(self):
        result = check_segment_punctuation(
            "K: anema ta azua? Lj: 電土", "排灣")
        self.assertEqual(result.discuss["說話者標記"], 2)
        self.assertEqual(
            result.hint,
            "詞素切割第 4 個詞的 `azua?` 有標點「?」，程式判斷要刪掉，"
            "因為詞素切割不能有標點，應該寫是 `azua`",
        )

    def test_黏著的說話者標記_當一般族語詞(self):
        result = check_segment_punctuation("Yu:m-uwah kekong", "泰雅")
        self.assertNotIn("說話者標記", result.discuss)
        self.assertEqual(
            result.hint,
            "詞素切割第 1 個詞的 `Yu:m-uwah` 有標點「:」，程式判斷要刪掉，"
            "因為詞素切割不能有標點，應該寫是 `Yum-uwah`",
        )

    def test_沒有標點(self):
        result = check_segment_punctuation("masa-maan i to", "阿美")
        self.assertEqual(result.hint, "")
        self.assertEqual(result.discuss, {})

    def test_一段只記一筆_照常匯出(self):
        entry = segment_entry("aji. uri. o brah", "Aji uri o brah", "太魯閣")
        found = []
        for issue in entry.issues:
            if issue.kind is IssueKind.SEGMENT_PUNCTUATION:
                found.append(issue)
        self.assertEqual(len(found), 1)
        self.assertIn("`aji.`", found[0].detail)
        self.assertIn("`uri.`", found[0].detail)
        self.assertTrue(entry.is_clean())

    def test_待討論的標記存在段上(self):
        entry = segment_entry("la+ga kiya.ga", ethnic="泰雅")
        self.assertEqual(entry.discuss, {"+": 1, "詞中間的 .": 1})

    def test_純華語句不檢查(self):
        entry = segment_entry("好，這個時候", ethnic="排灣")
        for issue in entry.issues:
            self.assertIsNot(issue.kind, IssueKind.SEGMENT_PUNCTUATION)


class TestReversedTimecode(unittest.TestCase):
    """結束時間比開始還早,是打錯的。"""

    def test_時間碼拆成數字(self):
        self.assertEqual(timecode_parts("0:00:27.880"), (0, 0, 27, 880))
        self.assertEqual(timecode_parts("00:04:21"), (0, 4, 21))

    def test_正常的時間碼沒問題(self):
        text = "1\n00:00:00-00:04:21\nkunaku\nkunaku\n我\n我\n"
        corpus = parse_text(text, path="t.txt")
        for issue in corpus.entries[0].issues:
            self.assertIsNot(issue.kind, IssueKind.REVERSED_TIMECODE)
