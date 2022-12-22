from abc import ABC, abstractmethod
from os.path import join, dirname, realpath
from typing import List

from src.toc.PdfFeatures.TocPdfFeatures import TocPdfFeatures


class Method(ABC):
    def __init__(self):
        self.root_path = dirname(realpath(__file__))
        print("running method", self.get_name())
        self.model_path = join(self.root_path, "models", self.get_name())

    @abstractmethod
    def train(self, pdfs_features: List[TocPdfFeatures]):
        pass

    @abstractmethod
    def predict(self, pdfs_features: List[TocPdfFeatures]) -> List[TocPdfFeatures]:
        pass

    def get_name(self):
        return self.__class__.__name__
