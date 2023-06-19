from extract_pdf_paragraphs.pdf_features.PdfTag import PdfTag


def get_next_tag_features(previous_tag: PdfTag = None, possible_next_tag: PdfTag = None):
    return [
        previous_tag.bounding_box.top,
        previous_tag.bounding_box.left,
        previous_tag.bounding_box.right,
        previous_tag.bounding_box.bottom,
        possible_next_tag.bounding_box.top,
        possible_next_tag.bounding_box.left,
        possible_next_tag.bounding_box.right,
        possible_next_tag.bounding_box.bottom,
        previous_tag.bounding_box.bottom - possible_next_tag.bounding_box.top,
    ]
