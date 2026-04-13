from typing import Protocol


class TextSplitterProtocol(Protocol):
    """Describe splitter interface.
    Args:
        None: No arguments."""

    def split_text(self, text: str) -> list[str]:
        """Split text into chunks.
        Args:
            text (str): Input text."""


class SimpleTokenSplitter:
    """Provide fallback token-like splitting by words.
    Args:
        chunk_size (int): Maximum number of words per chunk.
        chunk_overlap (int): Number of overlapping words."""

    def __init__(self, chunk_size: int, chunk_overlap: int) -> None:
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def split_text(self, text: str) -> list[str]:
        """Split text with simple word-based fallback.
        Args:
            text (str): Input text for splitting."""
        words_list = text.split()

        if not words_list:
            return []

        if self.chunk_size <= 0:
            return [' '.join(words_list)]

        step_size = self.chunk_size - self.chunk_overlap
        if step_size <= 0:
            step_size = 1

        chunks_list: list[str] = []

        for index in range(0, len(words_list), step_size):
            chunk_words = words_list[index:index + self.chunk_size]
            if not chunk_words:
                continue
            chunks_list.append(' '.join(chunk_words))

            if index + self.chunk_size >= len(words_list):
                break

        return chunks_list


def build_splitter(
    chunk_size: int,
    chunk_overlap: int,
    encoding_name: str,
) -> TextSplitterProtocol:
    """Build token-based text splitter.
    Args:
        chunk_size (int): Maximum number of tokens per chunk.
        chunk_overlap (int): Number of overlapping tokens.
        encoding_name (str): Tokenizer encoding name."""
    try:
        from langchain_text_splitters import TokenTextSplitter

        splitter = TokenTextSplitter(
            encoding_name=encoding_name,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )
        return splitter
    except ImportError:
        splitter = SimpleTokenSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )
        return splitter


def split_text(
    text: str,
    chunk_size: int,
    chunk_overlap: int,
    encoding_name: str,
) -> list[str]:
    """Split text into token-based chunks.
    Args:
        text (str): Input text for splitting.
        chunk_size (int): Maximum number of tokens per chunk.
        chunk_overlap (int): Number of overlapping tokens.
        encoding_name (str): Tokenizer encoding name."""
    splitter = build_splitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        encoding_name=encoding_name,
    )
    chunks_list = splitter.split_text(text)
    return chunks_list


def print_chunks(chunks_list: list[str]) -> list[str]:
    """Print token-based chunks with indexes.
    Args:
        chunks_list (list[str]): List of split text chunks."""
    for index, chunk_text in enumerate(chunks_list, start=1):
        print(f'Chunk {index}:')
        print(chunk_text)
        print('-' * 40)
    return chunks_list


if __name__ == '__main__':
    raw_text = (
        'Token-based chunking is useful when a model provider works '
        'with token limits. This approach makes chunk sizes closer to '
        'the actual model constraints and gives more control over the '
        'context window. Overlap helps preserve transitions between '
        'neighboring chunks in retrieval pipelines.'
    )

    chunks_list = split_text(
        text=raw_text,
        chunk_size=30,
        chunk_overlap=5,
        encoding_name='cl100k_base',
    )
    printed_chunks = print_chunks(chunks_list=chunks_list)
