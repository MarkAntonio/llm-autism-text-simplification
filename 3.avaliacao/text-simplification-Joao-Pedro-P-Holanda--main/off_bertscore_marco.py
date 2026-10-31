import os
from csv import DictWriter
from pathlib import Path
from glob import glob
import bert_score
import json
from pipelines import transform_document_to_metric_operations
from berts_score_util import (
    remove_markdown_tables,
    strip_special_characters,
    remove_duplicate_captions,
    remove_image_references,
    remove_extra_whitespaces,
    change_links_to_alt_texts,
    remove_html_tags,
    remove_enumerations,
    strip_document_markdown_formatting
)
from langchain_text_splitters import SentenceTransformersTokenTextSplitter


def open_json_chunks(file_path: str) -> dict["int", str]:
  with open(file_path, 'r', encoding="UTF-8") as file:
    loaded_json_chunks = json.load(file)

  return loaded_json_chunks


if __name__ == "__main__":
    json_files = glob("/home/marco-santos/Documents/1.Pré-pcc/3.Execução/2.code/2.simplificacao/paired_original_simplified_chunked_docs/*.json")

    all_average_bertscore = {}

    splitter = SentenceTransformersTokenTextSplitter(
        chunk_overlap=0,
        model_name="google-bert/bert-base-multilingual-cased",
        tokens_per_chunk=510,
    )


    for file_path in json_files:
        file_name = Path(file_path).name
        print(f"Opening {file_name}...")
        print(file_path)
        current_json_chunks = open_json_chunks(file_path)

        current_average_bertscore = {}

        for number_of_chunk in current_json_chunks:
            if number_of_chunk != "inference_time_for_all_chunks":

                original_text = current_json_chunks[number_of_chunk]["original_chunk"]
            
                for model, generated_dict in current_json_chunks[number_of_chunk]["simplified_chunks_by_model"].items():
                    
                    generated_text = generated_dict["simplified_chunk"]
                    
                    print(f"MODEL: {model}")

                    print(f"Original text: {original_text}")
                    print(f"Length in Chars of original text: {len(original_text)}")
                    print(f"Length in Words of original text: {len(original_text.split())}")

                    print(f"Generated text: {generated_text}")
                    print(f"Length in Chars of generated text: {len(generated_text)}")
                    print(f"Length in Words of generated text: {len(generated_text.split())}")

                    # original_chunks = splitter.split_text(original_text)
                    # generated_chunks = splitter.split_text(generated_text)



                    # print(f"ORIGINAL CHUNK ({len(original_chunks)})" + "="*20)

                    # print(f"GENERATED CHUNK ({len(generated_chunks)})" + "="*20)

                    # matched_chunk_count = min(len(original_chunks), len(generated_chunks))

        #             scores = bert_score.score(
        #                 generated_chunks[:matched_chunk_count],
        #                 original_chunks[:matched_chunk_count],
        #                 lang="pt",
        #             )

        #             current_average_bertscore[model] = {
        #                 "precision": scores[0].mean().item(),
        #                 "recall": scores[1].mean().item(),
        #                 "bert_score": scores[2].mean().item(),
        #             }

        
               
        # all_average_bertscore[file_name] = current_average_bertscore
        # current_average_bertscore.clear()

        # print(all_average_bertscore)
        # print(current_average_bertscore)
        break


 

            

