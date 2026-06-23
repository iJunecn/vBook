import type { APIRoute } from 'astro';
import { eq } from 'drizzle-orm';
import { db } from '../../lib/db';
import { books, orders } from '../../lib/schema';

export const prerender = false;

function json(data: unknown, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { 'Content-Type': 'application/json' },
  });
}

export const POST: APIRoute = async ({ request, locals }) => {
  if (!locals.user) return json({ error: '请先登录' }, 401);

  let body: { bookId?: unknown };
  try {
    body = await request.json();
  } catch {
    return json({ error: '请求格式错误' }, 400);
  }

  const bookId = body.bookId;
  if (typeof bookId !== 'string' || !bookId) return json({ error: '缺少 bookId' }, 400);

  try {
    const result = await db.transaction(async (tx) => {
      const [book] = await tx.select().from(books).where(eq(books.id, bookId)).for('update');
      if (!book) return { error: '书籍不存在', status: 404 } as const;
      if (book.status !== 'available') return { error: '该书籍已售出', status: 409 } as const;

      const [order] = await tx
        .insert(orders)
        .values({ bookId, buyerId: locals.user!.id })
        .returning({ id: orders.id });

      await tx.update(books).set({ status: 'sold' }).where(eq(books.id, bookId));
      return { orderId: order.id } as const;
    });

    if ('error' in result) return json({ error: result.error }, result.status);
    return json({ orderId: result.orderId });
  } catch (e) {
    console.error('create order failed:', e);
    return json({ error: '下单失败' }, 500);
  }
};
