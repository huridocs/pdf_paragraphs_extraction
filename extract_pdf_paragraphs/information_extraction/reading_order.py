from typing import List, Tuple

from bs4 import Tag


def get_tuples_pdfalto_reading_order_next(tags: List[Tag]) -> List[Tuple[Tag, Tag]]:
    tuples_to_check: List[Tuple[Tag, Tag]] = list()
    for index, tag in enumerate(tags):
        if index + 1 < len(tags):
            tuples_to_check.append((tags[index], tags[index + 1]))

    return tuples_to_check
