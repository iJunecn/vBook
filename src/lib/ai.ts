import OpenAI from 'openai';

const client = new OpenAI({
  apiKey: import.meta.env.AGNES_API_KEY,
  baseURL: import.meta.env.AGNES_BASE_URL,
});

export interface RecognizedBook {
  title: string | null;
  author: string | null;
  publisher: string | null;
  isbn: string | null;
  edition: string | null;
}

export async function recognizeBookSpine(
  imageBase64: string,
  mimeType: string
): Promise<RecognizedBook[]> {
  const response = await client.chat.completions.create({
    model: 'agnes-2.0-flash',
    messages: [
      {
        role: 'user',
        content: [
          {
            type: 'image_url',
            image_url: {
              url: `data:${mimeType};base64,${imageBase64}`,
            },
          },
          {
            type: 'text',
            text: `This is a photo of book spines on a bookshelf.
Identify every book visible and return a JSON array only — no markdown, no explanation, no code fences.
Each element must have exactly these fields: title, author, publisher, isbn, edition.
Set any field to null if not visible on the spine.`,
          },
        ],
      },
    ],
    max_tokens: 1000,
  });

  const content = response.choices[0]?.message?.content ?? '[]';
  try {
    return JSON.parse(content) as RecognizedBook[];
  } catch {
    // Try to extract a JSON array if the model adds extra text/fences.
    const match = content.match(/\[[\s\S]*\]/);
    if (match) {
      try {
        return JSON.parse(match[0]) as RecognizedBook[];
      } catch {
        return [];
      }
    }
    return [];
  }
}
