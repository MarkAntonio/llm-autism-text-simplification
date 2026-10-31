import json
import os
import re
from collections import defaultdict
from csv import DictWriter
from pathlib import Path
from typing import Any

from bert_score import BERTScorer
from dotenv import load_dotenv
from utils import strip_document_markdown_formatting



BERTSCORE_BATCH_SIZE = 16
MIN_ALIGNMENT_SCORE = 0.5


def read_json_file(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as file:
        content = json.load(file)

    if not isinstance(content, dict):
        raise ValueError(f"O JSON precisa conter um objeto na raiz: {path}")

    return content


def get_token_ids(text: str, tokenizer) -> list[int]:
    tokens = tokenizer.tokenize(text, verbose=False)
    return tokenizer.convert_tokens_to_ids(tokens)


def split_text_by_model_tokens(
    text: str, tokenizer, max_tokens: int
) -> list[tuple[str, int]]:
    token_ids = get_token_ids(text, tokenizer)
    if not token_ids:
        return []

    return [
        (
            tokenizer.decode(
                token_ids[index : index + max_tokens],
                skip_special_tokens=True,
                clean_up_tokenization_spaces=False,
            ),
            len(token_ids[index : index + max_tokens]),
        )
        for index in range(0, len(token_ids), max_tokens)
    ]


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


def calculate_paired_chunk_scores(
    original_text: str,
    generated_text: str,
    scorer: BERTScorer,
    max_tokens: int,
) -> dict[str, float | int]:
    original_tokens = get_token_ids(original_text, scorer._tokenizer)
    generated_tokens = get_token_ids(generated_text, scorer._tokenizer)
    original_parts_with_sizes = split_text_by_model_tokens(
        original_text, scorer._tokenizer, max_tokens
    )
    generated_parts_with_sizes = split_text_by_model_tokens(
        generated_text, scorer._tokenizer, max_tokens
    )
    original_parts = [part for part, _ in original_parts_with_sizes]
    generated_parts = [part for part, _ in generated_parts_with_sizes]

    if not original_parts or not generated_parts:
        raise ValueError("O chunk original e o simplificado não podem estar vazios.")

    generated_pairs = [
        generated_part
        for generated_part in generated_parts
        for _ in original_parts
    ]
    original_pairs = original_parts * len(generated_parts)
    precision_scores, recall_scores, f1_scores = scorer.score(
        generated_pairs,
        original_pairs,
        batch_size=BERTSCORE_BATCH_SIZE,
    )

    original_count = len(original_parts)
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
    matches = align_chunks(f1_matrix)

    generated_part_sizes = [size for _, size in generated_parts_with_sizes]
    original_part_sizes = [size for _, size in original_parts_with_sizes]
    precision_total = sum(
        precision_matrix[generated][original] * generated_part_sizes[generated]
        for generated, original in matches
    )
    recall_total = sum(
        recall_matrix[generated][original] * original_part_sizes[original]
        for generated, original in matches
    )
    precision = precision_total / len(generated_tokens)
    recall = recall_total / len(original_tokens)
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0

    return {
        "precision": precision,
        "recall": recall,
        "bert_score": f1,
        "matched_parts": len(matches),
        "generated_parts": len(generated_parts),
        "original_parts": len(original_parts),
        "generated_tokens": len(generated_tokens),
        "original_tokens": len(original_tokens),
    }


def get_json_chunks(content: dict[str, Any]) -> list[tuple[str, dict[str, Any]]]:
    chunks = [
        (key, value)
        for key, value in content.items()
        if key.isdigit() and isinstance(value, dict)
    ]
    return sorted(chunks, key=lambda item: int(item[0]))


def main() -> None:
    load_dotenv()
    json_dir = Path(
        os.getenv("PAIRED_JSON_DIR", "/home/marco-santos/Documents/1.Pré-pcc/3.Execução/2.code/2.simplificacao/paired_original_simplified_chunked_docs")
    )
    output_dir = Path(os.getenv("BERTSCORE_OUTPUT_DIR", "."))

    if not json_dir.is_dir():
        raise FileNotFoundError(
            f"Diretório de JSONs pareados não encontrado: {json_dir}. "
            "Configure PAIRED_JSON_DIR."
        )

    json_files = sorted(json_dir.glob("*.json"))
    if not json_files:
        raise FileNotFoundError(f"Nenhum arquivo JSON encontrado em: {json_dir}")

    output_dir.mkdir(parents=True, exist_ok=True)
    summary_path = output_dir / "bertscore_json_resumo.csv"
    chunks_path = output_dir / "bertscore_json_chunks.csv"

    scorer = BERTScorer(
        lang="pt",
        batch_size=BERTSCORE_BATCH_SIZE,
    )
    max_tokens = scorer._model.config.max_position_embeddings - 2
    totals: dict[tuple[str, str], dict[str, float | int]] = defaultdict(
        lambda: {
            "precision_total": 0.0,
            "generated_tokens": 0,
            "recall_total": 0.0,
            "original_tokens": 0,
            "chunks": 0,
            "matched_parts": 0,
            "generated_parts": 0,
            "original_parts": 0,
        }
    )

    with chunks_path.open("w", newline="", encoding="utf-8") as chunks_file:
        chunk_writer = DictWriter(
            chunks_file,
            fieldnames=[
                "document",
                "chunk",
                "model",
                "precision",
                "recall",
                "bert_score",
                "matched_parts",
                "generated_parts",
                "original_parts",
                "generated_tokens",
                "original_tokens",
            ],
        )
        chunk_writer.writeheader()

        for json_path in json_files:
            print(f"Lendo {json_path.name}...")
            content = read_json_file(json_path)

            for chunk_number, chunk_data in get_json_chunks(content):
                original_text = strip_document_markdown_formatting(chunk_data["original_chunk"])
                simplified_by_model = chunk_data["simplified_chunks_by_model"]

                for model, model_data in simplified_by_model.items():
                    generated_text = strip_document_markdown_formatting(model_data["simplified_chunk"])
                    scores = calculate_paired_chunk_scores(
                        original_text,
                        generated_text,
                        scorer,
                        max_tokens,
                    )

                    chunk_writer.writerow(
                        {
                            "document": json_path.name,
                            "chunk": chunk_number,
                            "model": model,
                            **scores,
                        }
                    )

                    key = (json_path.name, model)
                    total = totals[key]
                    total["precision_total"] += (
                        scores["precision"] * scores["generated_tokens"]
                    )
                    total["generated_tokens"] += scores["generated_tokens"]
                    total["recall_total"] += (
                        scores["recall"] * scores["original_tokens"]
                    )
                    total["original_tokens"] += scores["original_tokens"]
                    total["chunks"] += 1
                    total["matched_parts"] += scores["matched_parts"]
                    total["generated_parts"] += scores["generated_parts"]
                    total["original_parts"] += scores["original_parts"]

    with summary_path.open("w", newline="", encoding="utf-8") as summary_file:
        summary_writer = DictWriter(
            summary_file,
            fieldnames=[
                "document",
                "model",
                "precision",
                "recall",
                "bert_score",
                "chunks",
                "matched_parts",
                "generated_parts",
                "original_parts",
            ],
        )
        summary_writer.writeheader()

        for (document, model), total in sorted(totals.items()):
            precision = total["precision_total"] / total["generated_tokens"]
            recall = total["recall_total"] / total["original_tokens"]
            f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0

            summary_writer.writerow(
                {
                    "document": document,
                    "model": model,
                    "precision": precision,
                    "recall": recall,
                    "bert_score": f1,
                    "chunks": total["chunks"],
                    "matched_parts": total["matched_parts"],
                    "generated_parts": total["generated_parts"],
                    "original_parts": total["original_parts"],
                }
            )
            print(
                f"{document} | {model}: "
                f"precision={precision:.4f}, recall={recall:.4f}, F1={f1:.4f}"
            )

    print(f"Resultados por chunk salvos em: {chunks_path.resolve()}")
    print(f"Resultados agregados salvos em: {summary_path.resolve()}")


if __name__ == "__main__":
    main()
