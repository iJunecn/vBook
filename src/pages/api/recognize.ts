import type { APIRoute } from 'astro';
import { recognizeBookSpine } from '../../lib/ai';

export const prerender = false;

const MAX_SIZE = 10 * 1024 * 1024;

function json(data: unknown, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { 'Content-Type': 'application/json' },
  });
}

export const POST: APIRoute = async ({ request, locals }) => {
  if (!locals.user) return json({ error: '请先登录' }, 401);

  let formData: FormData;
  try {
    formData = await request.formData();
  } catch {
    return json({ error: '请求格式错误' }, 400);
  }

  const file = formData.get('image');
  if (!(file instanceof File)) return json({ error: '缺少图片' }, 400);
  if (!file.type.startsWith('image/')) return json({ error: '文件类型必须为图片' }, 400);
  if (file.size > MAX_SIZE) return json({ error: '图片不能超过 10MB' }, 400);

  try {
    const buffer = Buffer.from(await file.arrayBuffer());
    const base64 = buffer.toString('base64');
    const books = await recognizeBookSpine(base64, file.type);
    return json({ books });
  } catch (e) {
    console.error('recognize failed:', e);
    return json({ error: 'AI 识别失败，请稍后重试' }, 500);
  }
};
