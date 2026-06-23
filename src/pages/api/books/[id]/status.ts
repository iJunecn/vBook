import type { APIRoute } from 'astro';
import { eq } from 'drizzle-orm';
import { db } from '../../../../lib/db';
import { books, listings } from '../../../../lib/schema';

export const prerender = false;

function json(data: unknown, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { 'Content-Type': 'application/json' },
  });
}

export const PATCH: APIRoute = async ({ request, params, locals }) => {
  if (!locals.user) return json({ error: '请先登录' }, 401);

  const bookId = params.id;
  if (!bookId) return json({ error: '缺少书籍 ID' }, 400);

  let body: { status?: unknown };
  try {
    body = await request.json();
  } catch {
    return json({ error: '请求格式错误' }, 400);
  }

  const status = body.status;
  if (status !== 'sold' && status !== 'available') {
    return json({ error: 'status 必须为 sold 或 available' }, 400);
  }

  // Confirm the book exists and belongs to the current user (via its listing).
  const [row] = await db
    .select({ bookId: books.id, sellerId: listings.sellerId })
    .from(books)
    .innerJoin(listings, eq(books.listingId, listings.id))
    .where(eq(books.id, bookId));

  if (!row) return json({ error: '书籍不存在' }, 404);
  if (row.sellerId !== locals.user.id) return json({ error: '无权操作此书籍' }, 403);

  await db.update(books).set({ status }).where(eq(books.id, bookId));
  return json({ ok: true });
};
