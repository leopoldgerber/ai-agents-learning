from langchain_text_splitters import RecursiveCharacterTextSplitter


def build_splitter(
    chunk_size: int,
    chunk_overlap: int,
) -> RecursiveCharacterTextSplitter:
    """Build character-based text splitter.
    Args:
        chunk_size (int): Maximum size of one chunk in characters.
        chunk_overlap (int): Number of overlapping characters."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
    return splitter


def split_text(
    text: str,
    chunk_size: int,
    chunk_overlap: int,
) -> list[str]:
    """Split text into character-based chunks.
    Args:
        text (str): Input text for splitting.
        chunk_size (int): Maximum size of one chunk in characters.
        chunk_overlap (int): Number of overlapping characters."""
    splitter = build_splitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
    chunks_list = splitter.split_text(text)
    return chunks_list


def print_chunks(chunks_list: list[str]) -> list[str]:
    """Print chunks with their indexes.
    Args:
        chunks_list (list[str]): List of text chunks."""
    for index, chunk_text in enumerate(chunks_list, start=1):
        print(f'Chunk {index}:')
        print(chunk_text)
        print('-' * 40)
    return chunks_list


if __name__ == '__main__':
    raw_text = (
        'Chunking is a key step in RAG systems. '
        'A long document cannot always be processed as one unit. '
        'That is why the text is divided into smaller fragments. '
        'Character-based splitting is often the first practical '
        'strategy because it is simple and predictable. '
        'Overlap helps preserve context near chunk boundaries.'
    )

    chunks_list = split_text(
        text=raw_text,
        chunk_size=120,
        chunk_overlap=20,
    )
    printed_chunks = print_chunks(chunks_list=chunks_list)
