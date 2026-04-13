from typing import Any


def truncate_context(text: str, max_chars: int = 4000) -> str:
    return text[:max_chars]


def build_context_from_chunks(chunks: list[dict[str, Any]], max_chars: int) -> dict[str, Any]:
    sections: list[str] = []
    references: list[dict[str, Any]] = []
    total_chars = 0
    truncated = False

    for index, chunk in enumerate(chunks, start=1):
        document_name = chunk.get("document_name") or chunk.get("document_id") or "unknown"
        positions = chunk.get("positions") or []
        position_text = str(positions) if positions else "[]"
        content = (chunk.get("content") or "").strip()
        section = (
            f"[{index}] Source: {document_name}\n"
            f"Dataset ID: {chunk.get('dataset_id') or ''}\n"
            f"Document ID: {chunk.get('document_id') or ''}\n"
            f"Positions: {position_text}\n"
            f"Content:\n{content}\n"
        )

        if sections and total_chars + len(section) > max_chars:
            truncated = True
            break

        if not sections and len(section) > max_chars:
            section = truncate_context(section, max_chars)
            truncated = True

        sections.append(section)
        total_chars += len(section)
        references.append(
            {
                "index": index,
                "chunk_id": chunk.get("chunk_id", ""),
                "dataset_id": chunk.get("dataset_id"),
                "document_id": chunk.get("document_id"),
                "document_name": chunk.get("document_name", "") or "",
                "positions": positions,
                "similarity": float(chunk.get("similarity", 0) or 0),
                "vector_similarity": float(chunk.get("vector_similarity", 0) or 0),
                "term_similarity": float(chunk.get("term_similarity", 0) or 0),
                "content_preview": truncate_context(content.replace("\n", " ").strip(), 240),
            }
        )

    return {
        "context": "\n\n".join(sections).strip(),
        "references": references,
        "truncated": truncated,
    }
