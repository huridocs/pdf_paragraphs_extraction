from pdf_features.PdfToken import PdfToken


class Paragraph:
    def __init__(self, tokens: list[PdfToken]):
        self.tokens = tokens

    def add_token(self, token: PdfToken):
        self.tokens.append(token)
