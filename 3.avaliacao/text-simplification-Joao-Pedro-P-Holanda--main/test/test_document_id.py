import unittest

from schema import Document


class DocumentIdTest(unittest.TestCase):
    def test_reads_numeric_prefix_before_dot(self) -> None:
        document = Document(path="data/qwen2_5_7b/10.chunked_pneei_qwen2.5_7b.md", text="")

        self.assertEqual(document.id, 10)

    def test_preserves_numeric_suffix_fallback(self) -> None:
        document = Document(path="data/reference/2025_document_7.md", text="")

        self.assertEqual(document.id, 7)

    def test_returns_none_when_filename_has_no_numeric_id(self) -> None:
        document = Document(path="data/reference/document.md", text="")

        self.assertIsNone(document.id)
