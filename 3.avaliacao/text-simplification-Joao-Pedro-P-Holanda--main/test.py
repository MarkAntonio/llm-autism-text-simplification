import os
import zipfile
import glob
from sentence_transformers import SentenceTransformer
import buscador


def unzip_if_needed(zip_path: str, target_dir: str):
    """Extrai um zip para target_dir se ele existir e ainda não foi extraído."""
    if not os.path.isfile(zip_path):
        return

    os.makedirs(target_dir, exist_ok=True)

    # Se o diretório final já existe, não reextrai
    base_name = os.path.splitext(os.path.basename(zip_path))[0]
    final_dir = os.path.join(target_dir, base_name)
    if os.path.isdir(final_dir):
        print(f"Diretório já existe: {final_dir}")
        return

    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(target_dir)

    print(f"Arquivo extraído: {zip_path} -> {target_dir}")


def find_local_model_dir(base_dir: str, expected_name: str):
    """
    Procura a pasta real do modelo depois da extração.
    Tenta:
    - ./cache/models/<expected_name>
    - ou uma subpasta em ./cache/models que contenha config_sentence_transformers.json
    """
    exact = os.path.join(base_dir, expected_name)
    if os.path.isdir(exact):
        return exact

    candidates = []
    for root, dirs, files in os.walk(base_dir):
        files_set = set(files)
        if (
            "config_sentence_transformers.json" in files_set
            or "modules.json" in files_set
            or "config.json" in files_set
        ):
            candidates.append(root)

    if candidates:
        # Prioriza a que tem "sentence-transformers" na estrutura
        for c in sorted(candidates):
            if expected_name in c.lower():
                return c
        return candidates[0]

    return exact


# ---------------------------
# 1) Download do modelo
# ---------------------------
model_name = "legal_sroberta_v1"
output_dir = "./cache/models"

os.makedirs(output_dir, exist_ok=True)

print(f"Baixando {model_name} via Ulysses Fetcher...")
ok = buscador.download_resource(
    task_name="sentence_similarity",
    resource_name=model_name,
    output_dir=output_dir,
    show_progress_bar=True,
    check_cached=True,
    clean_compressed_files=False,  # deixa o zip para a extração manual
    check_resource_hash=True,
    timeout_limit_seconds=60,
)
print("Download concluído:", ok)

# ---------------------------
# 2) Extrair zip, se existir
# ---------------------------
zip_path = os.path.join(output_dir, f"{model_name}.zip")
if os.path.isfile(zip_path):
    unzip_if_needed(zip_path, output_dir)
else:
    print(f"Arquivo .zip não encontrado em: {zip_path}")

# ---------------------------
# 3) Localizar a pasta real do modelo
# ---------------------------
model_dir = find_local_model_dir(output_dir, model_name)
print("Diretório real do modelo:", model_dir)

# ---------------------------
# 4) Verificar se existe localmente
# ---------------------------
if not os.path.isdir(model_dir):
    raise FileNotFoundError(
        f"Modelo não foi encontrado localmente em {model_dir}. "
        "Confirme se o zip foi extraído corretamente."
    )

# Verificação rápida de arquivos esperados
expected_files = [
    "config_sentence_transformers.json",
    "modules.json",
    "config.json",
    "pytorch_model.bin",
]
present = [f for f in expected_files if os.path.isfile(os.path.join(model_dir, f))]
print("Arquivos presentes no diretório do modelo:", present)

# ---------------------------
# 5) Carregar via SentenceTransformer
# ---------------------------
print("Tentando carregar com SentenceTransformer...")
model = SentenceTransformer(model_dir)
print("Modelo carregado com sucesso:", model)

# ---------------------------
# 6) Teste rápido
# ---------------------------
sentences = [
    "A legislação define regras para a contratação pública.",
    "A lei estabelece critérios para contratos administrativos.",
]

emb = model.encode(sentences, convert_to_numpy=True, normalize_embeddings=True)
print("Shape do embedding:", emb.shape)
print("Embeddings:", emb)