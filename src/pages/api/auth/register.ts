import type { APIRoute } from 'astro';
import bcrypt from 'bcryptjs';
import { eq, or } from 'drizzle-orm';
import { db } from '../../../lib/db';
import { users } from '../../../lib/schema';
import { lucia } from '../../../lib/auth';

export const prerender = false;

function fail(message: string) {
  return new Response(null, {
    status: 302,
    headers: { Location: `/auth/register?error=${encodeURIComponent(message)}` },
  });
}

export const POST: APIRoute = async ({ request, cookies }) => {
  const form = await request.formData();
  const email = String(form.get('email') ?? '')
    .trim()
    .toLowerCase();
  const username = String(form.get('username') ?? '').trim();
  const password = String(form.get('password') ?? '');

  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) return fail('邮箱格式不正确');
  if (username.length < 3 || username.length > 32) return fail('用户名需 3-32 个字符');
  if (password.length < 6) return fail('密码至少 6 位');

  const existing = await db
    .select({ id: users.id, email: users.email })
    .from(users)
    .where(or(eq(users.email, email), eq(users.username, username)));

  if (existing.length) {
    return fail(existing[0].email === email ? '该邮箱已被注册' : '该用户名已被占用');
  }

  const passwordHash = await bcrypt.hash(password, 10);

  const [user] = await db
    .insert(users)
    .values({ email, username, passwordHash })
    .returning({ id: users.id });

  const session = await lucia.createSession(user.id, {});
  const cookie = lucia.createSessionCookie(session.id);
  cookies.set(cookie.name, cookie.value, cookie.attributes);

  return new Response(null, { status: 302, headers: { Location: '/' } });
};
