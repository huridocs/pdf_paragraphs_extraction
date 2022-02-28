from unittest import TestCase

from extract_pdf_paragraphs.PdfFeatures.Rectangle import Rectangle


class TestRectangle(TestCase):
    def test_rectangle(self):
        rectangle = Rectangle.from_tag({"HPOS": 1, "VPOS": 2, "HEIGHT": 3, "WIDTH": 5})
        self.assertEqual(2, rectangle.top)
        self.assertEqual(5, rectangle.bottom)
        self.assertEqual(6, rectangle.right)
        self.assertEqual(1, rectangle.left)

    def test_rectangle_nan_value(self):
        rectangle = Rectangle.from_tag({"HPOS": 1, "VPOS": 2, "HEIGHT": "-nan", "WIDTH": 5})
        self.assertEqual(2, rectangle.top)
        self.assertEqual(2, rectangle.bottom)
        self.assertEqual(6, rectangle.right)
        self.assertEqual(1, rectangle.left)

    def test_rectangle_nan_values(self):
        rectangle = Rectangle.from_tag({"HPOS": "-nan", "VPOS": "nan", "HEIGHT": "-nan", "WIDTH": "nan"})
        self.assertEqual(0, rectangle.top)
        self.assertEqual(0, rectangle.bottom)
        self.assertEqual(0, rectangle.right)
        self.assertEqual(0, rectangle.left)
