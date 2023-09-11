from paragraph_extraction_trainer.PdfSegment import PdfSegment
from pdf_features.PdfFeatures import PdfFeatures


class PdfSegmentation:
    def __init__(self, pdf_features: PdfFeatures, pdf_segments: list[PdfSegment]):
        self.pdf_features: PdfFeatures = pdf_features
        self.pdf_segments: list[PdfSegment] = pdf_segments
        self.title_predictions: list[float] = [0] * len(pdf_segments)

    def loop_predictions(self):
        for pdf_segment, title_prediction in zip(self.pdf_segments, self.title_predictions):
            yield pdf_segment, title_prediction
