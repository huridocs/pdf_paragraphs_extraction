from huggingface_hub import hf_hub_download

import config

hf_hub_download(
    repo_id="HURIDOCS/pdf-segmetation",
    filename="segmentator_model_config.txt",
    revision="52c44568f40ba3c19bd22e5ebc363425b7130a6b",
    cache_dir=config.HUGGINGFACE_PATH,
)

hf_hub_download(
    repo_id="HURIDOCS/pdf-segmetation",
    filename="segmentator_model.txt",
    revision="ab83ee7d75e7e1cfe7f0a740d1bf6a3b74a1fdf3",
    cache_dir=config.HUGGINGFACE_PATH,
)

hf_hub_download(
    repo_id="HURIDOCS/pdf-segmetation",
    filename="tag_type_finding_model_config.txt",
    revision="7d98776dd34acb2fe3a06495c82e64b9c84bdc16",
    cache_dir=config.HUGGINGFACE_PATH,
)

hf_hub_download(
    repo_id="HURIDOCS/pdf-segmetation",
    filename="tag_type_finding_model.txt",
    revision="c9e886597823a7995a1454f2de43b821bc930368",
    cache_dir=config.HUGGINGFACE_PATH,
)

hf_hub_download(
    repo_id="HURIDOCS/pdf-segmetation",
    filename="letter_corpus.txt",
    revision="da00a69c8d6a84493712e819580c0148757f466c",
    cache_dir=config.HUGGINGFACE_PATH,
)
