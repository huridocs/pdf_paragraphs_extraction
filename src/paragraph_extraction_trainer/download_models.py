from huggingface_hub import hf_hub_download

paragraph_extraction_model_path = hf_hub_download(
    repo_id="HURIDOCS/pdf-segmentation",
    filename="paragraph_extraction_model.model",
    revision="3dc98aa51e073066a78edde745d8882121c4891f",
)

toc_model_path = hf_hub_download(
    repo_id="HURIDOCS/pdf-segmentation",
    filename="TwoModelsV3SegmentsContext2Len.model",
    revision="d66b49062439d6283464edadd9428a186c553f64",
)
