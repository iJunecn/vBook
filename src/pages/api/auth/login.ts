import type { APIRoute } from 'astro';
import bcrypt from 'bcryptjs';
import { eq } from 'drizzle-orm';
import { db } from '../../../lib/db';
import { users } from '../../../lib/schema';
import { lucia } from '../../../lib/auth';

export const prerender = false;

function fail(message: string) {
  return new Response(null, {
    status: 302,
    headers: { Location: `/auth/login?error=${encodeURIComponent(message)}` },
  });
}

export const POST: APIRoute = async ({ request, cookies }) => {
  const form = await request.formData();
  const email = String(form.get('email') ?? '')
    .trim()
    .toLowerCase();
  const password = String(form.get('password') ?? '');

  if (!email || !password) return fail('请输入邮箱和密码');

  const [user] = await db.select().from(users).where(eq(users.email, email));
  if (!user) return fail('邮箱或密码错误');

  const valid = await bcrypt.compare(password, user.passwordHash);
  if (!valid) return fail('邮箱或密码错误');

  const session = await lucia.createSession(user.id, {});
  const cookie = lucia.createSessionCookie(session.id);
  cookies.set(cookie.name, cookie.value, cookie.attributes);

  return new Response(null, { status: 302, headers: { Location: '/' } });
};
