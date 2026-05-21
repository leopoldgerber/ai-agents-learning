import re
import hashlib
from typing import List
from langchain_core.documents import Document


def is_table_row(text: str) -> bool:
    return bool(re.search(r'\|.*\|', text)) or \
           bool(re.search(r'\t{2,}', text)) or \
           bool(re.search(r'^\s*[\w\s]+\s{2,}[\w\s]+', text))


def filter_and_dedup(
        docs: List[Document],
        min_length: int = 30
) -> List[Document]:
    unique_hashes = set()
    filtered = []
    stats = {'duplicates': 0, 'too_short': 0, 'empty': 0}
    for doc in docs:
        text = doc.page_content.strip()
        if not text:
            stats['empty'] += 1
            continue
        if len(text) < min_length and not is_table_row(text):
            stats['too_short'] += 1
            continue
        h = hashlib.md5(text.encode('utf-8')).hexdigest()
        if h in unique_hashes:
            stats['duplicates'] += 1
            continue
        unique_hashes.add(h)
        filtered.append(doc)
    print(f"Первоначально: {len(docs)} чанков")
    print(
        f"Удалено дубликатов: {stats['duplicates']}, "
        f"слишком коротких: {stats['too_short']},"
        f"пустых: {stats['empty']}"
    )
    print(f"Осталось: {len(filtered)} чанков")
    return filtered


def main() -> None:
    docs = [
        Document(
            page_content="Это достаточно длинный текстовый чанк для проверки."
        ),
        Document(
            page_content="Это достаточно длинный текстовый чанк для проверки."
        ),
        Document(page_content="Короткий"),
        Document(page_content=""),
        Document(page_content="Колонка 1 | Колонка 2 | Колонка 3"),
    ]

    filtered_docs = filter_and_dedup(docs)

    print("\nОтфильтрованные документы:")
    for i, doc in enumerate(filtered_docs, start=1):
        print(f"{i}. {doc.page_content}")


if __name__ == "__main__":
    main()
