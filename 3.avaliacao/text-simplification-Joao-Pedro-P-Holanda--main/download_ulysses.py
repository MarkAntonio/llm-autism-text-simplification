import os
import zipfile
import shutil

import buscador
import segmentador


def unzip_if_needed(zip_path: str, target_dir: str):
    """Extrai um zip para target_dir se ele existir e ainda não foi extraído."""
    if not os.path.isfile(zip_path):
        return

    os.makedirs(target_dir, exist_ok=True)

    # Se já foi extraído, não faz nada
    if os.path.isdir(os.path.splitext(zip_path)[0]):
        return

    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(target_dir)

    print(f"Arquivo extraído: {zip_path} -> {target_dir}")


def find_model_dir(base_dir: str, model_name: str):
    """
    Procura o diretório real do modelo depois da extração.
    Pega:
    - ./cache/models/<model_name>
    - ou ./cache/models (se os arquivos saíram na raiz)
    """
    candidate1 = os.path.join(base_dir, model_name)
    if os.path.isdir(candidate1):
        return candidate1

    # Caso o zip tenha extraído na própria pasta base
    if os.path.isdir(base_dir):
        files = os.listdir(base_dir)
        for name in files:
            full = os.path.join(base_dir, name)
            if os.path.isdir(full):
                # tenta encontrar config.json no diretório
                if os.path.isfile(os.path.join(full, "config.json")):
                    return full

    return candidate1


def find_tokenizer_dir(base_dir: str, tokenizer_name: str):
    candidate = os.path.join(base_dir, tokenizer_name)
    if os.path.isdir(candidate):
        return candidate

    if os.path.isdir(base_dir):
        for name in os.listdir(base_dir):
            full = os.path.join(base_dir, name)
            if os.path.isdir(full):
                # tokenizers tem arquivo tokenizer_config.json ou vocab.txt
                if (
                    os.path.isfile(os.path.join(full, "tokenizer_config.json"))
                    or os.path.isfile(os.path.join(full, "tokenizer.json"))
                    or os.path.isfile(os.path.join(full, "vocab.txt"))
                ):
                    return full

    return candidate


# -----------------------------
# 1) Defina os caminhos
# -----------------------------
model_name = "4_layer_6000_vocab_size_bert_v3"
tokenizer_name = "6000_subword_tokenizer"

model_output_dir = "./cache/models"
tokenizer_output_dir = "./cache/tokenizers"

os.makedirs(model_output_dir, exist_ok=True)
os.makedirs(tokenizer_output_dir, exist_ok=True)

# -----------------------------
# 2) Download do modelo
# -----------------------------
print("Baixando modelo...")
ok_model = buscador.download_resource(
    task_name="legal_text_segmentation",
    resource_name=model_name,
    output_dir=model_output_dir,
    show_progress_bar=True,
    check_cached=True,
    clean_compressed_files=False,  # deixa o zip para a extração manual
    check_resource_hash=True,
    timeout_limit_seconds=30,
)

print("Modelo baixado:", ok_model)

# -----------------------------
# 3) Download do tokenizer
# -----------------------------
print("Baixando tokenizer...")
try:
    ok_tokenizer = buscador.download_resource(
        task_name="legal_text_segmentation",
        resource_name=tokenizer_name,
        output_dir=tokenizer_output_dir,
        show_progress_bar=True,
        check_cached=True,
        clean_compressed_files=False,
        check_resource_hash=True,
        timeout_limit_seconds=30,
    )
    print("Tokenizer baixado:", ok_tokenizer)
except Exception as e:
    print(f"Tokenizer não foi baixado ou não existe para esse recurso: {e}")
    ok_tokenizer = False

# -----------------------------
# 4) Extração do zip
# -----------------------------
zip_model_path = os.path.join(model_output_dir, f"{model_name}.zip")
if os.path.isfile(zip_model_path):
    unzip_if_needed(zip_model_path, model_output_dir)

zip_tokenizer_path = os.path.join(tokenizer_output_dir, f"{tokenizer_name}.zip")
if os.path.isfile(zip_tokenizer_path):
    unzip_if_needed(zip_tokenizer_path, tokenizer_output_dir)

# -----------------------------
# 5) Descobre caminhos reais
# -----------------------------
model_dir = find_model_dir(model_output_dir, model_name)
tokenizer_dir = find_tokenizer_dir(tokenizer_output_dir, tokenizer_name)

print("Modelo encontrado em:", model_dir)
print("Tokenizer encontrado em:", tokenizer_dir)

# -----------------------------
# 6) Carrega o segmentador
# -----------------------------
uri_model = model_dir if os.path.isdir(model_dir) else model_output_dir
uri_tokenizer = tokenizer_dir if os.path.isdir(tokenizer_dir) else None

print("uri_model =", uri_model)
print("uri_tokenizer =", uri_tokenizer)

segmenter = segmentador.BERTSegmenter(
    uri_model=uri_model,
    uri_tokenizer=uri_tokenizer,
    local_files_only=True,
    device="cpu",
)

# -----------------------------
# 7) Teste rápido
# -----------------------------
text = """
PROJETO DE LEI N. 0123 (Da Sra. Alguém)
Dispõe de algo. O Congresso Nacional decreta:
Artigo 1. Este projeto de lei não tem efeito.
"""

out = segmenter(text)
print(out)