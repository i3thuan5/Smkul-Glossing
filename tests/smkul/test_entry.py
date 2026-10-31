"""測試 entry.py 的資料型別。"""

import os
import unittest

from scripts.smkul.entry import (
    NORM_FEATURE,
    SEVERITY,
    CorpusFile,
    Entry,
    Issue,
    IssueKind,
    NormKind,
    NormLog,
    Severity,
)

FEATURES = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__)))),
    "features",
)


def read_feature(name):
    path = os.path.join(FEATURES, name + ".feature")
    with open(path, encoding="utf-8") as handle:
        return handle.read()


class TestIssue(unittest.TestCase):

    def test_每個_kind_都有_severity(self):
        for kind in IssueKind:
            self.assertIn(kind, SEVERITY)

    def test_error_與_warning(self):
        error = Issue(IssueKind.GLUED_LINE, "a.txt", "5")
        warning = Issue(IssueKind.MIXED_TIMECODE_FORMAT, "a.txt")
        self.assertTrue(error.is_error())
        self.assertFalse(warning.is_error())

    def test_純華語句_是現象_不是錯誤(self):
        issue = Issue(IssueKind.CHINESE_ONLY, "a.txt", "112")
        self.assertIs(issue.severity, Severity.NOTICE)
        self.assertFalse(issue.is_error())

    def test_空段與孤兒時間碼_是現象(self):
        # 規格見 features/分析報告.feature「每一種問題的嚴重度」。
        for kind in (IssueKind.EMPTY_ENTRY, IssueKind.ORPHAN_TIMECODE):
            issue = Issue(kind, "a.txt", "1")
            self.assertIs(issue.severity, Severity.NOTICE, kind.value)
            self.assertFalse(issue.is_error())

    def test_詞素切割有標點_是錯誤照常匯出(self):
        issue = Issue(IssueKind.SEGMENT_PUNCTUATION, "a.txt", "12")
        self.assertIs(issue.severity, Severity.EXPORTED_ERROR)
        self.assertFalse(issue.is_error())

    def test_四級嚴重度的名稱(self):
        self.assertEqual(Severity.ERROR.value, "錯誤")
        self.assertEqual(Severity.EXPORTED_ERROR.value, "錯誤（照常匯出）")
        self.assertEqual(Severity.WARNING.value, "警告（照常匯出）")
        self.assertEqual(Severity.NOTICE.value, "現象")

    def test_沒有標點不同這一類(self):
        names = []
        for kind in IssueKind:
            names.append(kind.value)
        self.assertNotIn("標點不同", names)


class TestKindNames(unittest.TestCase):
    """分類名照 meeting-terms-yaml design 決策 1;三類改名照 report-trim design 決策 8。"""

    def test_對應的五類與_feature_的_scenario_一字不差(self):
        text = read_feature("詞素切割與詞素翻譯對應")
        expect = {
            IssueKind.GLOSS_FEWER: "詞素切割的詞比詞素翻譯多",
            IssueKind.GLOSS_MORE: "詞素切割的詞比詞素翻譯少",
            IssueKind.GLOSS_CUT_MORE: "詞素切割沒有切，詞素翻譯有切",
            IssueKind.GLOSS_CUT_FEWER: "詞素切割有切，詞素翻譯沒有切",
            IssueKind.SYMBOL_KIND_DIFF: "詞素切割和詞素翻譯的符號不一樣",
        }
        for kind, name in expect.items():
            self.assertEqual(kind.value, name)
            self.assertIn("Scenario: 不對應——" + name + "\n", text)

    def test_結構異常與比對的分類名(self):
        self.assertEqual(IssueKind.MISSING_GLOSS_LINE.value, "缺詞素翻譯行")
        self.assertEqual(IssueKind.MISSING_TRANSLATION.value, "缺華語翻譯行")
        self.assertEqual(IssueKind.EMPTY_ENTRY.value, "空段")
        self.assertEqual(
            IssueKind.SOURCE_SEGMENT_MISMATCH.value, "族語原句與詞素切割不符")
        # 「段數不同」是 docx／txt 比對的分類，隨 docx-txt-consistency 刪掉。
        names = []
        for kind in IssueKind:
            names.append(kind.value)
        self.assertNotIn("段數不同", names)

    def test_自動處理指向的_scenario_都找得到(self):
        for kind, (feature, scenario) in NORM_FEATURE.items():
            text = read_feature(feature)
            self.assertTrue(
                "Scenario: " + scenario + "\n" in text,
                str(kind) + " 指向 " + feature + ".feature 的「" +
                scenario + "」，找不到")


class TestYaml(unittest.TestCase):
    """對照 corpus-export spec「YAML 匯出結構」的秀姑巒第 26 段範例。"""

    def build_entry(self):
        return Entry(
            number="26",
            start="00:02:09,410",
            end="00:02:12,547",
            source="pisanoAmis a caciyaw awa to matini",
            segmentation="pi-sano-Amis a caciyaw awa=to matini",
            gloss="PI-像-族名 連繫詞 說話 沒有=完成貌 現在",
            translation="使用族語的情況已經少見了",
        )

    def test_段_yaml_的_key(self):
        data = self.build_entry().to_yaml()
        self.assertEqual(
            list(data),
            ["編號", "開始", "結束", "族語原句", "詞素切割", "詞素翻譯",
             "華語翻譯"],
        )
        self.assertEqual(data["編號"], "26")
        self.assertEqual(data["開始"], "00:02:09,410")
        self.assertEqual(data["結束"], "00:02:12,547")
        self.assertEqual(
            data["族語原句"], "pisanoAmis a caciyaw awa to matini")
        self.assertEqual(
            data["詞素切割"], "pi-sano-Amis a caciyaw awa=to matini")
        self.assertEqual(
            data["詞素翻譯"], "PI-像-族名 連繫詞 說話 沒有=完成貌 現在")
        self.assertEqual(data["華語翻譯"], "使用族語的情況已經少見了")

    def test_段_yaml_沒有構詞資訊(self):
        data = self.build_entry().to_yaml()
        for key in ("詞", "詞素", "構詞"):
            self.assertNotIn(key, data)

    def test_檔案_yaml_只收乾淨的段(self):
        good = self.build_entry()
        bad = Entry("27", "0", "1")
        bad.issues.append(Issue(IssueKind.GLUED_LINE, "a.txt", "27"))
        corpus = CorpusFile(
            path="阿美族/秀姑巒/a.txt",
            ethnic="阿美",
            variant="秀姑巒",
            entries=[good, bad],
        )
        data = corpus.to_yaml()
        self.assertEqual(len(data["段"]), 1)
        self.assertEqual(data["段"][0]["編號"], "26")
        self.assertEqual(data["族別"], "阿美")
        self.assertEqual(data["語言別"], "秀姑巒")
        self.assertEqual(data["語言別代號"], "ami-x-skl")

    def test_warning_不擋匯出(self):
        entry = self.build_entry()
        entry.issues.append(
            Issue(IssueKind.MIXED_TIMECODE_FORMAT, "a.txt", "26")
        )
        self.assertTrue(entry.is_clean())

    def test_錯誤照常匯出_不擋匯出(self):
        entry = self.build_entry()
        entry.issues.append(
            Issue(IssueKind.SEGMENT_PUNCTUATION, "a.txt", "26")
        )
        self.assertTrue(entry.is_clean())

    def test_現象_仍不匯出(self):
        entry = self.build_entry()
        entry.issues.append(Issue(IssueKind.CHINESE_ONLY, "a.txt", "26"))
        self.assertFalse(entry.is_clean())


class TestNormLog(unittest.TestCase):

    def test_沒發生的項目也要列出來(self):
        log = NormLog()
        records = log.ordered()
        self.assertEqual(len(records), len(list(NormKind)))
        for record in records:
            self.assertEqual(record.count, 0)

    def test_最多留三組例(self):
        log = NormLog()
        for index in range(5):
            log.note(
                NormKind.EN_DASH, "PI–書" + str(index),
                "PI-書" + str(index), "a.txt", str(index),
            )
        record = log.records[NormKind.EN_DASH]
        self.assertEqual(record.count, 5)
        self.assertEqual(len(record.examples), 3)
        self.assertEqual(record.examples[0]["原句子"], "PI–書0")
        self.assertEqual(record.examples[0]["處理後"], "PI-書0")
        self.assertEqual(record.examples[0]["編號"], "0")
        self.assertIn("en-dash", record.kind.value)
        self.assertTrue(record.why)


if __name__ == "__main__":
    unittest.main()
