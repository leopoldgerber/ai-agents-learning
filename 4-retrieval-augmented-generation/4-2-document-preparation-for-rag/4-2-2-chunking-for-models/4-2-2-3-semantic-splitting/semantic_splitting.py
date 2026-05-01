from langchain_text_splitters import MarkdownHeaderTextSplitter


def build_splitter(
    headers_to_split_on: list[tuple[str, str]],
) -> MarkdownHeaderTextSplitter:
    """Build markdown header splitter.
    Args:
        headers_to_split_on (list[tuple[str, str]]): Header rules."""
    splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=headers_to_split_on,
    )
    return splitter


def split_text(
    text: str,
    headers_to_split_on: list[tuple[str, str]],
) -> list:
    """Split text by semantic markdown headers.
    Args:
        text (str): Input markdown text.
        headers_to_split_on (list[tuple[str, str]]): Header rules."""
    splitter = build_splitter(
        headers_to_split_on=headers_to_split_on,
    )
    chunks_list = splitter.split_text(text)
    return chunks_list


def print_chunks(chunks_list: list) -> list:
    """Print semantic chunks with metadata.
    Args:
        chunks_list (list): Split markdown chunks."""
    for index, chunk_item in enumerate(chunks_list, start=1):
        print(f'Chunk {index}:')
        print(chunk_item.page_content)
        print(chunk_item.metadata)
        print('-' * 40)
    return chunks_list


if __name__ == '__main__':
    markdown_text = (
        '# RAG System\n'
        'General overview of the system.\n\n'
        '## Retrieval Layer\n'
        'The retrieval layer finds relevant chunks.\n\n'
        '## Generation Layer\n'
        'The generation layer builds the final answer.\n\n'
        '### Output Control\n'
        'This block explains structured output.'
    )

    header_rules = [
        ('#', 'h1'),
        ('##', 'h2'),
        ('###', 'h3'),
    ]

    chunks_list = split_text(
        text=markdown_text,
        headers_to_split_on=header_rules,
    )
    printed_chunks = print_chunks(chunks_list=chunks_list)
