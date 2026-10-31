from sentence_transformers import SentenceTransformer, util

# 1. Carrega o modelo com janela de contexto de 8.192 tokens
# Este modelo é otimizado para o português brasileiro

# Usar primeiro o embeddinggemma, depois o BAAI, para garantir que vai existir uma neutralidade tanto por serem modelos difeirentes onde o primeiro é mais focado em pt-br, mas  também para garantir que ele não pontue melhor para o gemma, pois ele tem um modelo gemma por base, por mais que segundo o Gemini isso não beneficia por se tratar de dois contextos diferentes (embedding e LLM). Mas também o primeiro é modelo LLM e o segundo é model Enconder. isso pode diferentciar

embedding_model_name = "tardellirs/embeddinggemma-pt-br"
embedding_model = SentenceTransformer(embedding_model_name)

import os
from csv import DictWriter
from pathlib import Path

from dotenv import load_dotenv
from glob import glob
from langchain_text_splitters import SentenceTransformersTokenTextSplitter


import nltk

# # Define a pasta nltk_data para dentro do seu projeto/venv atual
# nltk_data_dir = os.path.join(os.getcwd(), ".venv", "nltk_data")
# os.makedirs(nltk_data_dir, exist_ok=True)
# nltk.data.path.append(nltk_data_dir)

# # Baixe os pacotes necessários
# nltk.download("punkt", download_dir=nltk_data_dir)
# nltk.download("punkt_tab", download_dir=nltk_data_dir)  

# from nltk.tokenize import sent_tokenize

import segmentador

# 1. Primeiro, segmenta o texto usando a inteligência jurídica do Ulysses
ulysses_splliter = segmentador.BERTSegmenter()


def read_stripped_markdown_file(path: Path) -> str:
    with open(path, "r", encoding="utf-8") as file:
        text = "".join(file.readlines())

    return text


if __name__ == "__main__":
    load_dotenv()
    data_dir = Path(os.getenv("DATA_BASE_DIR", "data"))
    ORIGINAL_DATA_DIR = data_dir / "full_original_docs"
    RESULT_DIR = data_dir / "full_simplified_docs"

    original_files = {
            Path(x).name.replace("_stripped",""): Path(x)
            for x in glob(f"./{ORIGINAL_DATA_DIR}/*_stripped.md",recursive=True)
        }

    generated_files_with_model_name = [(Path(x).parent.name, Path(x)) for x in glob(f"./{RESULT_DIR}/**/*_stripped.md",recursive=True)]

    splitter = SentenceTransformersTokenTextSplitter(
        chunk_overlap=0,
        # Modelo 
        model_name=embedding_model_name,
        tokens_per_chunk=200,  # descontando 2 de 2048 para os tokens especiais CLS e SEP
    )

    with open("embeddings.csv", "w", newline="") as csvfile:
        fieldnames = ["name", "llm_model", "embedding_model", "SentenceBERT"]
        writer = DictWriter(csvfile, fieldnames=fieldnames)
        # checando se o arquivo não é vazio, não funciona em arquivos xlsx
        if os.stat("embeddings.csv").st_size == 0:
            writer.writeheader()

        for model,file in generated_files_with_model_name:
            matching_original = original_files.get(file.name.replace("_stripped",""))

            if not matching_original:
                print(f"File {file.name} don't have a corresponding simplification, skipping")
                continue
            file = "data/full_simplified_docs/gemma-4-E2B-it-qat-q4.0-gguf/3.lei_13977_stripped.md"
            # Quebrando os dois textos utilizando o Tokenizer
            original_simplification = read_stripped_markdown_file(matching_original)
            print("CURRENT SIMPLIFICATION PATH: ", matching_original)
            print("CURRENT GENERATED PATH: ", file)

            generated_simplification = read_stripped_markdown_file(file)
            

            original_chunks = splitter.split_text(original_simplification)

            with open("original_chunks.txt", "w") as file:
                file.write("\n{CHUNK}\n".join(original_chunks))
          
            # frases = sent_tokenize(original_simplification, language="portuguese")
            # print(frases)

            # with open("original_nltk.txt", "w") as file:
            #     file.write("\n{CHUNK}\n".join(frases))

            # lei = ulysses_splliter(original_chunks)

            # with open("original_ulysses.txt", "w") as file:
            #     file.write("\n{CHUNK}\n".join(frases))

            # break
        
            generated_chunks = splitter.split_text(generated_simplification)

            smaller_chunk_size = min(
                len(original_chunks), len(generated_chunks)
            )

            print(f"Calculando Sentence BERT para documento {file.name} com a versão do modelo {model}")

            embedding_a = embedding_model.encode(original_chunks[:smaller_chunk_size], convert_to_tensor=True, normalize_embeddings=True)
            embedding_b = embedding_model.encode(generated_chunks[:smaller_chunk_size], convert_to_tensor=True, normalize_embeddings=True)

            # # 5. Calcular a similaridade de cosseno
            average_similarity = []
            count = 0
            print("smaller_chunk_size: ", smaller_chunk_size)
            for i in range(smaller_chunk_size):
                
                print(f"CHUNK {i}")
                print(f"Original: {original_chunks[i][:200]}")
                print(f"Generated: {generated_chunks[i][:200]}")
                
                count += 1


               
                similarity = util.cos_sim(embedding_a[i], embedding_b[i])
                average_similarity.append(similarity.item())

            average_similarity = sum(average_similarity) / len(average_similarity)

            writer.writerow(
                {
                    "name": file.name,
                    "llm_model": model,
                    "embedding_model": embedding_model_name,
                    "SentenceBERT": average_similarity
                }
            )

            break