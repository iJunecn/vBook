import type { APIRoute } from 'astro';
import { lucia } from '../../../lib/auth';

export const prerender = false;

export const POST: APIRoute = async ({ locals, cookies }) => {
  if (locals.session) {
    await lucia.invalidateSession(locals.session.id);
  }
  const cookie = lucia.createBlankSessionCookie();
  cookies.set(cookie.name, cookie.value, cookie.attributes);

  return new Response(null, { status: 302, headers: { Location: '/auth/login' } });
};
