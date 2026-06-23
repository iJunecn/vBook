<script setup lang="ts">
import { ref } from 'vue';

const props = defineProps<{ bookId: string; status: string }>();

const current = ref(props.status);
const loading = ref(false);
const error = ref<string | null>(null);

async function setStatus(status: 'sold' | 'available') {
  error.value = null;
  loading.value = true;
  try {
    const res = await fetch(`/api/books/${props.bookId}/status`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status }),
    });
    if (!res.ok) {
      const data = await res.json().catch(() => ({}));
      throw new Error(data.error || '操作失败');
    }
    current.value = status;
  } catch (e) {
    error.value = e instanceof Error ? e.message : '操作失败';
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <div class="flex items-center gap-2">
    <span
      :class="[
        'rounded-full px-2.5 py-0.5 text-xs font-medium',
        current === 'available'
          ? 'bg-emerald-50 text-emerald-700'
          : current === 'sold'
            ? 'bg-slate-200 text-slate-600'
            : 'bg-rose-50 text-rose-600',
      ]"
    >
      {{ current === 'available' ? '在售' : current === 'sold' ? '已售' : '已下架' }}
    </span>

    <button
      v-if="current === 'available'"
      type="button"
      :disabled="loading"
      @click="setStatus('sold')"
      class="rounded-lg border border-slate-300 px-3 py-1 text-xs font-medium text-slate-600 hover:border-brand-300 disabled:opacity-50"
    >
      标记为已售
    </button>
    <button
      v-else-if="current === 'sold'"
      type="button"
      :disabled="loading"
      @click="setStatus('available')"
      class="rounded-lg border border-brand-300 px-3 py-1 text-xs font-medium text-brand-700 hover:bg-brand-50 disabled:opacity-50"
    >
      重新上架
    </button>

    <span v-if="error" class="text-xs text-rose-600">{{ error }}</span>
  </div>
</template>
