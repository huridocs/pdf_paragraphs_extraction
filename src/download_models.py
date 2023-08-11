from huggingface_hub import hf_hub_download

import config

paragraph_extraction_model_path = hf_hub_download(
    repo_id="HURIDOCS/pdf-segmetation",
    filename="paragraph_extraction_model.model",
    revision="42bfe646276eddd4de9c08420ed2caf078cdc25f",
    cache_dir=config.HUGGINGFACE_PATH,
)

letter_corpus_path = hf_hub_download(
    repo_id="HURIDOCS/pdf-segmetation",
    filename="letter_corpus.txt",
    revision="da00a69c8d6a84493712e819580c0148757f466c",
    cache_dir=config.HUGGINGFACE_PATH,
)

toc_model_path = hf_hub_download(
    repo_id="HURIDOCS/pdf-segmetation",
    filename="TwoModelsV3SegmentsContext2Len.model",
    revision="d66b49062439d6283464edadd9428a186c553f64",
    cache_dir=config.HUGGINGFACE_PATH,
)
