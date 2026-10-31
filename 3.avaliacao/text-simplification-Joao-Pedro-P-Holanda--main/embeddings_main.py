import os
from csv import DictWriter
from pathlib import Path

import bert_score
from dotenv import load_dotenv
from langchain_text_splitters import SentenceTransformersTokenTextSplitter


DATA_DIR = Path(os.getenv("DATA_BASE_DIR", "data"))
ORIGINAL_DIR = DATA_DIR / "full_original_docs"
GENERATED_DIR = DATA_DIR / "full_simplified_docs"
OUTPUT_PATH = Path("embeddings.csv")


def read_text(path: Path) -> str:
    with path.open("r", encoding="utf-8") as file:
        return "".join(file.readlines())


def document_key(path: Path) -> str:
    return path.name.split(".", maxsplit=1)[0]


def get_original_files() -> dict[str, Path]:
    files: dict[str, Path] = {}

    for path in ORIGINAL_DIR.glob("*_stripped.md"):
        files[document_key(path)] = path

    for path in ORIGINAL_DIR.glob("*.md"):
        if path.name.endswith("_stripped.md"):
            continue
        files.setdefault(document_key(path), path)

    return files


def get_generated_files() -> list[tuple[str, Path]]:
    return [
        (path.parent.name, path)
        for path in GENERATED_DIR.glob("*/*_stripped.md")
    ]


def calc_bert_score(original_text: str, generated_text: str, splitter):
    original_chunks = splitter.split_text(original_text)
    generated_chunks = splitter.split_text(generated_text)

    n = min(len(original_chunks), len(generated_chunks))
    if len(original_chunks) != len(generated_chunks):
        print(
            f"Aviso: original tem {len(original_chunks)} chunks e gerado tem {len(generated_chunks)}; "
            f"usando os primeiros {n}"
        )

    precision, recall, f1 = bert_score.score(
        generated_chunks[:n],
        original_chunks[:n],
        lang="pt",
    )

    return {
        "precision": precision.mean().item(),
        "recall": recall.mean().item(),
        "bert_score": f1.mean().item(),
    }


def main():
    load_dotenv()

    if not ORIGINAL_DIR.is_dir():
        raise FileNotFoundError(f"Diretório de originais não encontrado: {ORIGINAL_DIR}")
    if not GENERATED_DIR.is_dir():
        raise FileNotFoundError(f"Diretório de simplificados não encontrado: {GENERATED_DIR}")

    splitter = SentenceTransformersTokenTextSplitter(
        chunk_overlap=0,
        model_name="google-bert/bert-base-multilingual-cased",
        tokens_per_chunk=510,
    )

    original_files = get_original_files()
    generated_files = sorted(get_generated_files())

    with OUTPUT_PATH.open("w", newline="", encoding="utf-8") as csv_file:
        writer = DictWriter(
            csv_file,
            fieldnames=["name", "model", "precision", "recall", "bert_score"],
        )
        writer.writeheader()

        for model, generated_path in generated_files:
            original_path = original_files.get(document_key(generated_path))
            if original_path is None:
                print(f"Ignorando {generated_path.name}: não há original correspondente")
                continue

            scores = calc_bert_score(
                read_text(original_path),
                read_text(generated_path),
                splitter,
            )

            writer.writerow(
                {
                    "name": generated_path.name,
                    "model": model,
                    **scores,
                }
            )

    print(f"Resultado salvo em: {OUTPUT_PATH.resolve()}")


if __name__ == "__main__":
    main()
