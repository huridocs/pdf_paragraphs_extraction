from huggingface_hub import hf_hub_download

import config

segmentation_model_config_path = hf_hub_download(
    repo_id="HURIDOCS/pdf-segmetation",
    filename="segmentator_model_config.txt",
    revision="52c44568f40ba3c19bd22e5ebc363425b7130a6b",
    cache_dir=config.HUGGINGFACE_PATH,
)

segmentation_model_path = hf_hub_download(
    repo_id="HURIDOCS/pdf-segmetation",
    filename="segmentator_model.txt",
    revision="ab83ee7d75e7e1cfe7f0a740d1bf6a3b74a1fdf3",
    cache_dir=config.HUGGINGFACE_PATH,
)

tag_type_finding_config_path = hf_hub_download(
    repo_id="HURIDOCS/pdf-segmetation",
    filename="tag_type_finding_model_config.txt",
    revision="7d98776dd34acb2fe3a06495c82e64b9c84bdc16",
    cache_dir=config.HUGGINGFACE_PATH,
)

pdf_tag_type_model_path = hf_hub_download(
    repo_id="HURIDOCS/pdf-segmetation",
    filename="tag_type_finding_model.txt",
    revision="c9e886597823a7995a1454f2de43b821bc930368",
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

next_tag_model_path = hf_hub_download(
    repo_id="HURIDOCS/pdf-segmetation",
    filename="next_tags.model",
    revision="52a165ef899ccb6024361393ddae297d55b3f5cb",
    cache_dir=config.HUGGINGFACE_PATH,
)

reading_order_model_path = hf_hub_download(
    repo_id="HURIDOCS/pdf-segmetation",
    filename="reading_order.model",
    revision="5f0590ae32f3eb69296fb596013bbd2dd84a3d02",
    cache_dir=config.HUGGINGFACE_PATH,
)
