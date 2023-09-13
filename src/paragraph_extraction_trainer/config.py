from os.path import join
from pathlib import Path

ROOT_PATH = Path(__file__).parent.parent.parent.absolute()

PDF_LABELED_DATA_ROOT_PATH = Path(join(ROOT_PATH.parent, "pdf-labeled-data"))
PARAGRAPH_EXTRACTION_RELATIVE_PATH = join("labeled_data", "paragraph_extraction")
