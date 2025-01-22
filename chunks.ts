// This code does two things:
// 1. It splits a long piece of text into smaller chunks, making it easier to read or process.
// 2. It finds useful details about the text, like the title (first line), word count, and estimated reading time.

export const chunkText = (text: string, maxChunkSize: number = 1000): string[] => {
  // Split into sentences (basic implementation)
  const sentences = text.match(/[^.!?]+[.!?]+/g) || [text];
  const chunks: string[] = [];
  let currentChunk = '';

  for (const sentence of sentences) {
    // If adding this sentence would exceed maxChunkSize, start a new chunk
    if (currentChunk.length + sentence.length > maxChunkSize && currentChunk.length > 0) {
      chunks.push(currentChunk.trim());
      currentChunk = '';
    }
    currentChunk += sentence + ' ';
  }

  // Add the last chunk if it's not empty
  if (currentChunk.trim().length > 0) {
    chunks.push(currentChunk.trim());
  }

  return chunks;
};

export const extractMetadata = (text: string) => {
  // Basic metadata extraction
  const firstLine = text.split('\n')[0];
  const wordCount = text.split(/\s+/).length;
  const estimatedReadingTime = Math.ceil(wordCount / 200); // Assuming 200 words per minute

  return {
    title: firstLine,
    wordCount,
    estimatedReadingTime,
    processedAt: new Date().toISOString(),
  };
};
