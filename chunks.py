# This code does two things:
# 1. It splits a long piece of text into smaller chunks, making it easier to read or process.
# 2. It finds useful details about the text, like the title (first line), word count, and estimated reading time.

def chunk_text(text: str, max_chunk_size: int = 1000) -> list[str]:
    """
    Splits the input text into smaller chunks based on sentence boundaries.

    :param text: The input text to chunk.
    :param max_chunk_size: Maximum size of each chunk.
    :return: A list of text chunks.
    """
    import re

    # Split text into sentences
    sentences = re.findall(r'[^.!?]+[.!?]+', text) or [text]
    chunks = []
    current_chunk = ''

    for sentence in sentences:
        # If adding this sentence exceeds max_chunk_size, start a new chunk
        if len(current_chunk) + len(sentence) > max_chunk_size and current_chunk:
            chunks.append(current_chunk.strip())
            current_chunk = ''
        current_chunk += sentence + ' '

    # Add the last chunk if not empty
    if current_chunk.strip():
        chunks.append(current_chunk.strip())

    return chunks

def extract_metadata(text: str) -> dict:
    """
    Extracts basic metadata from the text.

    :param text: The input text.
    :return: A dictionary containing metadata: title, word count, estimated reading time, and processing timestamp.
    """
    import math
    from datetime import datetime

    # Extract metadata
    first_line = text.split('\n')[0]
    word_count = len(text.split())
    estimated_reading_time = math.ceil(word_count / 200)  # Assuming 200 words per minute

    return {
        "title": first_line,
        "word_count": word_count,
        "estimated_reading_time": estimated_reading_time,
        "processed_at": datetime.utcnow().isoformat(),
    }
