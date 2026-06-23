import type { APIRoute } from 'astro';
import { eq } from 'drizzle-orm';
import { db } from '../../lib/db';
import { users, campusEnum } from '../../lib/schema';
import type { Campus } from '../../lib/schema';

export const prerender = false;

const validCampus = new Set<string>(campusEnum.enumValues);

export const POST: APIRoute = async ({ request, locals }) => {
  if (!locals.user) {
    return new Response(null, { status: 302, headers: { Location: '/auth/login' } });
  }

  const form = await request.formData();
  const nickname = String(form.get('nickname') ?? '').trim();
  const campusRaw = String(form.get('campus') ?? '').trim();
  const avatarUrl = String(form.get('avatarUrl') ?? '').trim();

  const campus: Campus | null = validCampus.has(campusRaw) ? (campusRaw as Campus) : null;

  await db
    .update(users)
    .set({
      nickname: nickname || null,
      campus,
      avatarUrl: avatarUrl || null,
    })
    .where(eq(users.id, locals.user.id));

  return new Response(null, {
    status: 302,
    headers: { Location: '/profile?saved=1' },
  });
};
