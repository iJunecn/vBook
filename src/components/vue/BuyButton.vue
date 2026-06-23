<script setup lang="ts">
import { ref } from 'vue';

const props = defineProps<{
  bookId: string;
  loggedIn: boolean;
  sold: boolean;
  isOwn: boolean;
}>();

const loading = ref(false);
const error = ref<string | null>(null);

async function buy() {
  error.value = null;
  if (!props.loggedIn) {
    window.location.href = '/auth/login';
    return;
  }
  loading.value = true;
  try {
    const res = await fetch('/api/orders', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ bookId: props.bookId }),
    });
    if (res.status === 409) throw new Error('这本书刚刚被买走了');
    if (!res.ok) {
      const data = await res.json().catch(() => ({}));
      throw new Error(data.error || '下单失败');
    }
    window.location.href = '/profile/orders';
  } catch (e) {
    error.value = e instanceof Error ? e.message : '下单失败';
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <div class="space-y-2">
    <button
      v-if="!sold && !isOwn"
      type="button"
      :disabled="loading"
      @click="buy"
      class="w-full rounded-xl bg-rose-600 py-3 text-base font-semibold text-white transition hover:bg-rose-700 disabled:opacity-50"
    >
      {{ loading ? '处理中…' : '立即购买' }}
    </button>

    <div v-else-if="isOwn" class="rounded-xl bg-slate-100 py-3 text-center text-sm text-slate-500">
      这是你发布的书籍
    </div>
    <div v-else class="rounded-xl bg-slate-200 py-3 text-center text-sm font-medium text-slate-500">
      已售出
    </div>

    <p v-if="error" class="text-sm text-rose-600">{{ error }}</p>
  </div>
</template>
