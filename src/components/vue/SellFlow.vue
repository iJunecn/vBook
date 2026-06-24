<script setup lang="ts">
import { ref } from 'vue';
import type { RecognizedBook } from '../../lib/ai';
import ImageUploader from './ImageUploader.vue';
import RecognitionTable from './RecognitionTable.vue';

const loading = ref(false);
const error = ref<string | null>(null);
const recognized = ref<RecognizedBook[]>([]);
const hasRecognized = ref(false);

async function onRecognize(file: File) {
  error.value = null;
  loading.value = true;
  try {
    const form = new FormData();
    form.append('image', file);
    const res = await fetch('/api/recognize', { method: 'POST', body: form });
    if (!res.ok) {
      const data = await res.json().catch(() => ({}));
      throw new Error(data.error || '识别失败，请重试');
    }
    const data = (await res.json()) as { books: RecognizedBook[] };
    recognized.value = data.books ?? [];
    hasRecognized.value = true;
  } catch (e) {
    error.value = e instanceof Error ? e.message : '识别失败';
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <div class="space-y-8">
    <section class="max-w-2xl">
      <h2 class="mb-3 text-sm font-semibold text-slate-500">1 · 上传书脊照片</h2>
      <ImageUploader :loading="loading" @recognize="onRecognize" />
      <p v-if="error" class="mt-3 text-sm text-rose-600">{{ error }}</p>
    </section>

    <section>
      <div class="mb-3 flex items-center justify-between">
        <h2 class="text-sm font-semibold text-slate-500">2 · 确认并编辑书目</h2>
        <span v-if="hasRecognized" class="text-xs text-slate-400">
          AI 识别到 {{ recognized.length }} 本，可自由修改
        </span>
      </div>
      <RecognitionTable :initial-books="recognized" />
    </section>
  </div>
</template>
