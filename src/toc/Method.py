from abc import ABC, abstractmethod
from os.path import join, dirname, realpath

from toc.PdfSegmentation import PdfSegmentation


class Method(ABC):
    def __init__(self):
        self.root_path = dirname(realpath(__file__))
        print("running method", self.get_name())
        self.model_path = join(self.root_path, "models", self.get_name())

    @abstractmethod
    def train(self, pdfs_segmentations: list[PdfSegmentation]):
        pass

    @abstractmethod
    def predict(self, pdfs_segmentations: list[PdfSegmentation]) -> list[PdfSegmentation]:
        pass

    def get_name(self):
        return self.__class__.__name__
