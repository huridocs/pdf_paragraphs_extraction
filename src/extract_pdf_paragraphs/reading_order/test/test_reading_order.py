from os.path import join
from pathlib import Path
from unittest import TestCase

from extract_pdf_paragraphs.pdf_features.PdfFeatures import PdfFeatures
from extract_pdf_paragraphs.reading_order.ReadingOrderFinder import ReadingOrderFinder
from extract_pdf_paragraphs.segmentator.predict import predict


class TestReadingOrder(TestCase):
    def test_reading_order(self):
        print("start")
        pdf_features = PdfFeatures.from_pdfalto(join(Path(__file__).parent, "two_column.xml"))
        ReadingOrderFinder().get_reading_order_from_pdf_features(pdf_features)
        pdf_segments = predict(pdf_features)
        self.assertEqual("© 2021 Copyright held by the owner/author(s).", pdf_segments[-1].text_content)
