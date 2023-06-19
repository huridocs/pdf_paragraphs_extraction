from abc import ABC, abstractmethod
from os.path import join, dirname, realpath

from src.toc.pdf_features.TocPdfFeatures import TocPdfFeatures


class Method(ABC):
    def __init__(self):
        self.root_path = dirname(realpath(__file__))
        print("running method", self.get_name())
        self.model_path = join(self.root_path, "models", self.get_name())

    @abstractmethod
    def train(self, pdfs_features: list[TocPdfFeatures]):
        pass

    @abstractmethod
    def predict(self, pdfs_features: list[TocPdfFeatures]) -> list[TocPdfFeatures]:
        pass

    def get_name(self):
        return self.__class__.__name__
