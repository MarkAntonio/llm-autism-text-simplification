import os
from csv import DictWriter
from pathlib import Path

import bert_score
from dotenv import load_dotenv
from langchain_text_splitters import SentenceTransformersTokenTextSplitter


MIN_ALIGNMENT_SCORE = 0.5
BERTSCORE_BATCH_SIZE = 16


def read_text(path: Path) -> str:
    with path.open("r", encoding="utf-8") as file:
        return file.read()


def document_key(path: Path) -> str:
    return path.name.split(".", maxsplit=1)[0]


def get_original_files(original_dir: Path) -> dict[str, Path]:
    files: dict[str, Path] = {}

    for path in original_dir.glob("*_stripped.md"):
        files[document_key(path)] = path

    for path in original_dir.glob("*.md"):
        if not path.name.endswith("_stripped.md"):
            files.setdefault(document_key(path), path)

    return files


def get_generated_files(generated_dir: Path) -> list[tuple[str, Path]]:
    return sorted(
        (path.parent.name, path)
        for path in generated_dir.glob("*/*_stripped.md")
    )


def align_chunks(
    f1_scores: list[list[float]],
    min_alignment_score: float = MIN_ALIGNMENT_SCORE,
) -> list[tuple[int, int]]:
    generated_count = len(f1_scores)
    original_count = len(f1_scores[0]) if generated_count else 0
    best_score = [
        [0.0] * (original_count + 1)
        for _ in range(generated_count + 1)
    ]
    previous_step = [
        [""] * (original_count + 1)
        for _ in range(generated_count + 1)
    ]

    for generated_index in range(1, generated_count + 1):
        for original_index in range(1, original_count + 1):
            best_score[generated_index][original_index] = best_score[
                generated_index - 1
            ][original_index]
            previous_step[generated_index][original_index] = "generated"

            if best_score[generated_index][original_index - 1] > best_score[
                generated_index
            ][original_index]:
                best_score[generated_index][original_index] = best_score[
                    generated_index
                ][original_index - 1]
                previous_step[generated_index][original_index] = "original"

            pair_score = f1_scores[generated_index - 1][original_index - 1]
            if pair_score > min_alignment_score:
                match_score = best_score[generated_index - 1][
                    original_index - 1
                ] + pair_score - min_alignment_score
                if match_score > best_score[generated_index][original_index]:
                    best_score[generated_index][original_index] = match_score
                    previous_step[generated_index][original_index] = "match"

    matches = []
    generated_index = generated_count
    original_index = original_count
    while generated_index > 0 and original_index > 0:
        step = previous_step[generated_index][original_index]
        if step == "match":
            matches.append((generated_index - 1, original_index - 1))
            generated_index -= 1
            original_index -= 1
        elif step == "generated":
            generated_index -= 1
        elif step == "original":
            original_index -= 1
        else:
            break

    return list(reversed(matches))


def calc_aligned_bert_score(
    generated_chunks: list[str],
    original_chunks: list[str],
    min_alignment_score: float = MIN_ALIGNMENT_SCORE,
) -> dict[str, float | int]:
    if not generated_chunks or not original_chunks:
        raise ValueError("Os textos gerado e original precisam ter ao menos um chunk.")

    generated_pairs = [
        generated_chunk
        for generated_chunk in generated_chunks
        for _ in original_chunks
    ]
    original_pairs = original_chunks * len(generated_chunks)
    precision_scores, recall_scores, f1_scores = bert_score.score(
        generated_pairs,
        original_pairs,
        lang="pt",
        batch_size=BERTSCORE_BATCH_SIZE,
    )

    original_count = len(original_chunks)
    precision_matrix = [
        precision_scores[index : index + original_count].tolist()
        for index in range(0, len(generated_pairs), original_count)
    ]
    recall_matrix = [
        recall_scores[index : index + original_count].tolist()
        for index in range(0, len(generated_pairs), original_count)
    ]
    f1_matrix = [
        f1_scores[index : index + original_count].tolist()
        for index in range(0, len(generated_pairs), original_count)
    ]
    matches = align_chunks(f1_matrix, min_alignment_score)

    precision = sum(precision_matrix[generated][original] for generated, original in matches)
    precision /= len(generated_chunks)
    recall = sum(recall_matrix[generated][original] for generated, original in matches)
    recall /= len(original_chunks)
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0

    return {
        "precision": precision,
        "recall": recall,
        "bert_score": f1,
        "matched_chunks": len(matches),
        "generated_chunks": len(generated_chunks),
        "original_chunks": len(original_chunks),
    }


def main() -> None:
    load_dotenv()
    data_dir = Path(os.getenv("DATA_BASE_DIR", "data"))
    original_dir = data_dir / "full_original_docs"
    generated_dir = data_dir / "full_simplified_docs"

    if not original_dir.is_dir():
        raise FileNotFoundError(f"Diretório de originais não encontrado: {original_dir}")
    if not generated_dir.is_dir():
        raise FileNotFoundError(
            f"Diretório de simplificados não encontrado: {generated_dir}"
        )

    splitter = SentenceTransformersTokenTextSplitter(
        chunk_overlap=0,
        model_name="google-bert/bert-base-multilingual-cased",
        tokens_per_chunk=510,
    )
    original_files = get_original_files(original_dir)
    generated_files = get_generated_files(generated_dir)
    output_path = Path("bertscore_aligned.csv")

    with output_path.open("w", newline="", encoding="utf-8") as csv_file:
        fieldnames = [
            "name",
            "model",
            "precision",
            "recall",
            "bert_score",
            "matched_chunks",
            "generated_chunks",
            "original_chunks",
        ]
        writer = DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()

        for model, generated_path in generated_files:
            original_path = original_files.get(document_key(generated_path))
            if original_path is None:
                print(
                    f"Ignorando {generated_path.name}: "
                    "não há original correspondente"
                )
                continue

            original_chunks = splitter.split_text(read_text(original_path))
            generated_chunks = splitter.split_text(read_text(generated_path))
            scores = calc_aligned_bert_score(generated_chunks, original_chunks)

            writer.writerow(
                {
                    "name": generated_path.name,
                    "model": model,
                    **scores,
                }
            )
            print(
                f"{generated_path.name} ({model}): "
                f"{scores['matched_chunks']}/{scores['generated_chunks']} chunks "
                f"gerados alinhados; "
                f"{scores['matched_chunks']}/{scores['original_chunks']} originais"
            )

    print(f"Resultado salvo em: {output_path.resolve()}")


if __name__ == "__main__":
    main()
