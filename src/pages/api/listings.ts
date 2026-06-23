import type { APIRoute } from 'astro';
import { db } from '../../lib/db';
import { listings, books } from '../../lib/schema';

export const prerender = false;

function json(data: unknown, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { 'Content-Type': 'application/json' },
  });
}

interface IncomingBook {
  title?: unknown;
  author?: unknown;
  publisher?: unknown;
  isbn?: unknown;
  edition?: unknown;
  price?: unknown;
}

const str = (v: unknown): string | null => {
  if (typeof v !== 'string') return null;
  const t = v.trim();
  return t.length ? t : null;
};

export const POST: APIRoute = async ({ request, locals }) => {
  if (!locals.user) return json({ error: '请先登录' }, 401);

  let body: { books?: IncomingBook[] };
  try {
    body = await request.json();
  } catch {
    return json({ error: '请求格式错误' }, 400);
  }

  const incoming = body.books;
  if (!Array.isArray(incoming) || incoming.length === 0) {
    return json({ error: '请至少提供一本书' }, 400);
  }

  const rows: Array<{
    title: string;
    author: string | null;
    publisher: string | null;
    isbn: string | null;
    edition: string | null;
    price: string;
  }> = [];

  for (const b of incoming) {
    const title = str(b.title);
    const price = Number(b.price);
    if (!title) return json({ error: '每本书都需要书名' }, 400);
    if (Number.isNaN(price) || price < 0) return json({ error: '价格无效' }, 400);
    rows.push({
      title,
      author: str(b.author),
      publisher: str(b.publisher),
      isbn: str(b.isbn),
      edition: str(b.edition),
      price: price.toFixed(2),
    });
  }

  try {
    const listingId = await db.transaction(async (tx) => {
      const [listing] = await tx
        .insert(listings)
        .values({ sellerId: locals.user!.id })
        .returning({ id: listings.id });

      await tx.insert(books).values(rows.map((r) => ({ ...r, listingId: listing.id })));
      return listing.id;
    });

    return json({ listingId });
  } catch (e) {
    console.error('create listing failed:', e);
    return json({ error: '上架失败' }, 500);
  }
};
