from glob import glob
from gloe.collection import Map
from file_processing_steps import read_markdown_file, store_results_as_csv
from metrics_steps import (
    extract_document_statistics_port_parser,
    list_complex_words,
    transform_document_to_metric_operations,
)
from pipelines import (
    extract_metrics_from_generated_texts_port_tokenizer as extract_readability_metrics_simplified,
    extract_metrics_from_complete_texts_port_tokenizer as extract_readability_metrics_original,
    extract_udpipe_nilc_metrix_from_generated_simplified_texts as extract_morphosyntactic_metrics_simplified,
    extract_udpipe_nilc_metrix_from_original_complete_texts as extract_morphosyntactic_metrics_original
)


simplified_md_files = glob("./data/full_simplified_docs/**/*.md", recursive=True)

if not simplified_md_files:
    raise FileNotFoundError("Nenhum arquivo .md encontrado em ./data")


original_md_files = glob("./data/full_original_docs/*.conllu")

if not original_md_files:
    raise FileNotFoundError("Nenhum arquivo .md encontrado em ./data")

print(simplified_md_files)


# extract_morphosyntactic_metrics_simplified(simplified_md_files)
# extract_morphosyntactic_metrics_original(original_md_files)


# extract_readability_metrics_simplified(simplified_md_files)
extract_readability_metrics_original(original_md_files)

