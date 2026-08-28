"""測試 markers.py:從 ODS 建立各語言的合法標記集合。"""

import unittest

from tests import ODS

from scripts.smkul.markers import (
    SHEET_OF,
    affix_position,
    load_marker_lists,
    marker_from_gloss,
    read_sheets,
    sheet_for,
    split_gloss,
)


class TestSheetMapping(unittest.TestCase):

    def test_六種語言都對得上(self):
        self.assertEqual(len(SHEET_OF), 6)
        self.assertEqual(sheet_for("阿美族/秀姑巒/a.txt"), "阿美語")
        self.assertEqual(sheet_for("魯凱族/霧台/a.txt"), "霧台魯凱語")
        self.assertEqual(sheet_for("太魯閣族/a.txt"), "太魯閣語")

    def test_還沒交付的語言對不到(self):
        self.assertEqual(sheet_for("鄒族/a.txt"), "")


class TestSplit(unittest.TestCase):

    def test_照切分符號拆(self):
        self.assertEqual(split_gloss("主焦-學習"), ["主焦", "學習"])
        self.assertEqual(
            split_gloss("主焦-知道=完成貌"), ["主焦", "知道", "完成貌"])

    def test_有空白的不算單一標記(self):
        self.assertEqual(split_gloss("如果 沒有 言談標記"), [])


class TestAffixPosition(unittest.TestCase):

    def test_前綴看第一段(self):
        self.assertEqual(affix_position("mi-"), "頭")
        self.assertEqual(marker_from_gloss("主焦-學習", "頭"), "主焦")

    def test_後綴看最後一段(self):
        self.assertEqual(affix_position("-an"), "尾")
        self.assertEqual(marker_from_gloss("告訴-處焦", "尾"), "處焦")

    def test_附著看最後一段(self):
        self.assertEqual(affix_position("=to"), "尾")
        self.assertEqual(
            marker_from_gloss("主焦-知道=完成貌", "尾"), "完成貌")

    def test_中綴(self):
        self.assertEqual(affix_position("<om>"), "中綴")
        self.assertEqual(marker_from_gloss("<主焦>吃", "中綴"), "主焦")

    def test_獨立詞不取(self):
        self.assertEqual(affix_position("ano"), "")


class TestMarkers(unittest.TestCase):

    def setUp(self):
        self.markers = load_marker_lists(ODS)

    def test_讀得到每個_sheet(self):
        self.assertEqual(set(self.markers), {"阿美語", "布農語"})

    def test_收得到語法標記(self):
        amis = self.markers["阿美語"].allowed
        for label in ("主焦", "受焦", "處焦", "完成貌"):
            self.assertIn(label, amis, label)

    def test_詞根的意譯不會被收進去(self):
        """這是關鍵:書、學習、吃、族名是詞根的意譯,不是語法標記。"""
        amis = self.markers["阿美語"].allowed
        for label in ("學習", "吃", "族名", "給", "告訴", "知道"):
            self.assertNotIn(label, amis, label)

    def test_中綴寫在詞素翻譯裡也收得到(self):
        """布農語 3-7 的詞綴欄只寫 s-,經驗貌藏在 gloss 的 <> 裡。"""
        self.assertIn("經驗貌", self.markers["布農語"].allowed)

    def test_用點串接的子標記也算數(self):
        bunun = self.markers["布農語"].allowed
        self.assertIn("主焦.祈使", bunun)
        self.assertIn("祈使", bunun)

    def test_欄位重複會展開(self):
        rows = read_sheets(ODS)["阿美語"]
        self.assertTrue(rows)
        for values in rows:
            self.assertLess(len(values), 20)


if __name__ == "__main__":
    unittest.main()
