import os
from csv import DictWriter
from pathlib import Path

import bert_score
from dotenv import load_dotenv
from langchain_text_splitters import SentenceTransformersTokenTextSplitter


def read_stripped_markdown_file(path: Path) -> str:
    with open(path, "r", encoding="utf-8") as file:
        text = "".join(file.readlines())

    return text


def document_id(path: Path) -> str:
    """Return the numeric prefix shared by original and simplified filenames."""
    return path.name.split(".", maxsplit=1)[0]


if __name__ == "__main__":
    load_dotenv()
    data_dir = Path(os.getenv("DATA_BASE_DIR", "data"))
    original_dir = data_dir / "full_original_docs"
    simplified_dir = data_dir / "full_simplified_docs"

    if not original_dir.is_dir():
        raise FileNotFoundError(f"Original documents directory not found: {original_dir}")
    if not simplified_dir.is_dir():
        raise FileNotFoundError(
            f"Generated simplified documents directory not found: {simplified_dir}"
        )

    original_files: dict[str, Path] = {}
    for path in original_dir.glob("*_stripped.md"):
        key = document_id(path)
        if key in original_files:
            raise ValueError(f"Duplicate original document ID {key!r}: {path}")
        original_files[key] = path

    # If a source has not been stripped, use its Markdown version as a fallback.
    for path in original_dir.glob("*.md"):
        if path.name.endswith("_stripped.md"):
            continue
        original_files.setdefault(document_id(path), path)

    generated_files_with_model_name = [
        (path.parent.name, path)
        for path in simplified_dir.glob("*/*_stripped.md")
    ]

    if not generated_files_with_model_name:
        raise FileNotFoundError(
            f"No generated *_stripped.md files found under {simplified_dir}"
        )

    splitter = SentenceTransformersTokenTextSplitter(
        chunk_overlap=0,
        model_name="google-bert/bert-base-multilingual-cased",
        tokens_per_chunk=510,
    )

    output_path = Path("embeddings.csv")
    with output_path.open("w", newline="", encoding="utf-8") as csvfile:
        fieldnames = ["name", "model", "precision", "recall", "bert_score"]
        writer = DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for model, file in sorted(generated_files_with_model_name):
            matching_original = original_files.get(document_id(file))

            if not matching_original:
                print(
                    f"No original document with ID {document_id(file)!r} "
                    f"matches {file}; skipping"
                )
                continue

            original_text = read_stripped_markdown_file(matching_original)
            generated_text = read_stripped_markdown_file(file)

            original_chunks = splitter.split_text(original_text)
            generated_chunks = splitter.split_text(generated_text)

            print(f"ORIGINAL CHUNK ({matching_original})" + "="*20)
            print(original_chunks[1])

            print(f"GENERATED CHUNK ({file})" + "="*20)
            print(generated_chunks[1])

            matched_chunk_count = min(len(original_chunks), len(generated_chunks))
            
            print(len(original_chunks))
            print(len(generated_chunks))

            if len(original_chunks) != len(generated_chunks):
                print(
                    f"Warning: {file.name} has {len(generated_chunks)} generated "
                    f"chunks and {len(original_chunks)} original chunks; "
                    f"only the first {matched_chunk_count} pairs will be scored"
                )

            print(
                f"Calculating BERTScore for {file.name} against "
                f"{matching_original.name} (model folder: {model})"
            )



            break
            # bert_score.score expects candidates first and references second.
            scores = bert_score.score(
                generated_chunks[:matched_chunk_count],
                original_chunks[:matched_chunk_count],
                lang="pt",
            )

            writer.writerow(
                {
                    "name": file.name,
                    "model": model,
                    "precision": scores[0].mean().item(),
                    "recall": scores[1].mean().item(),
                    "bert_score": scores[2].mean().item(),
                }
            )

    print(f"Results written to {output_path.resolve()}")