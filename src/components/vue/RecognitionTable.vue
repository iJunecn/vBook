<script setup lang="ts">
import { ref, watch } from 'vue';
import { Trash2 } from 'lucide-vue-next';
import type { RecognizedBook } from '../../lib/ai';

interface EditableRow extends RecognizedBook {
  price: string;
}

const props = defineProps<{ initialBooks: RecognizedBook[] }>();

const rows = ref<EditableRow[]>([]);
const submitting = ref(false);
const error = ref<string | null>(null);
const bulkPrice = ref('');

function applyBulkPrice() {
  const price = Number(bulkPrice.value);
  if (bulkPrice.value === '' || Number.isNaN(price) || price < 0) return;
  rows.value.forEach((row) => {
    row.price = bulkPrice.value;
  });
}

function toRows(books: RecognizedBook[]): EditableRow[] {
  return books.map((b) => ({
    title: b.title ?? '',
    author: b.author ?? '',
    publisher: b.publisher ?? '',
    isbn: b.isbn ?? '',
    edition: b.edition ?? '',
    price: '',
  }));
}

watch(
  () => props.initialBooks,
  (books) => {
    rows.value = toRows(books);
  },
  { immediate: true }
);

function addRow() {
  rows.value.push({ title: '', author: '', publisher: '', isbn: '', edition: '', price: '' });
}

function removeRow(index: number) {
  rows.value.splice(index, 1);
}

async function submit() {
  error.value = null;

  if (rows.value.length === 0) {
    error.value = '请至少添加一本书';
    return;
  }
  for (const [i, row] of rows.value.entries()) {
    if (!row.title?.trim()) {
      error.value = `第 ${i + 1} 行缺少书名`;
      return;
    }
    const price = Number(row.price);
    if (!row.price || Number.isNaN(price) || price < 0) {
      error.value = `第 ${i + 1} 行价格无效`;
      return;
    }
  }

  submitting.value = true;
  try {
    const res = await fetch('/api/listings', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        books: rows.value.map((r) => ({
          title: r.title.trim(),
          author: r.author?.trim() || null,
          publisher: r.publisher?.trim() || null,
          isbn: r.isbn?.trim() || null,
          edition: r.edition?.trim() || null,
          price: Number(r.price),
        })),
      }),
    });
    if (!res.ok) {
      const data = await res.json().catch(() => ({}));
      throw new Error(data.error || '上架失败');
    }
    window.location.href = '/profile/listings';
  } catch (e) {
    error.value = e instanceof Error ? e.message : '上架失败';
  } finally {
    submitting.value = false;
  }
}

const cell =
  'w-full rounded-md border border-transparent bg-transparent px-2 py-1.5 outline-none transition focus:border-brand-300 focus:bg-white';
</script>

<template>
  <div class="space-y-4">
    <div class="overflow-x-auto rounded-xl border border-slate-200 bg-white">
      <table class="w-full min-w-[860px] table-fixed text-sm">
        <colgroup>
          <col style="width: 26%" />
          <col style="width: 15%" />
          <col style="width: 17%" />
          <col style="width: 16%" />
          <col style="width: 10%" />
          <col style="width: 12%" />
          <col style="width: 52px" />
        </colgroup>
        <thead class="bg-slate-50 text-left text-xs uppercase text-slate-500">
          <tr>
            <th class="px-3 py-2 font-medium">书名 *</th>
            <th class="px-3 py-2 font-medium">作者</th>
            <th class="px-3 py-2 font-medium">出版社</th>
            <th class="px-3 py-2 font-medium">ISBN</th>
            <th class="px-3 py-2 font-medium">版次</th>
            <th class="px-3 py-2 font-medium">价格 *</th>
            <th class="px-3 py-2"></th>
          </tr>
        </thead>
        <tbody class="divide-y divide-slate-100">
          <tr v-for="(row, i) in rows" :key="i" class="align-top">
            <td class="p-1"><input v-model="row.title" :class="cell" placeholder="必填" /></td>
            <td class="p-1"><input v-model="row.author" :class="cell" /></td>
            <td class="p-1"><input v-model="row.publisher" :class="cell" /></td>
            <td class="p-1"><input v-model="row.isbn" :class="cell" /></td>
            <td class="p-1"><input v-model="row.edition" :class="cell" /></td>
            <td class="p-1">
              <div class="flex items-center rounded-md focus-within:bg-white focus-within:ring-1 focus-within:ring-brand-300">
                <span class="pl-2 text-slate-400">¥</span>
                <input
                  v-model="row.price"
                  type="number"
                  min="0"
                  step="0.01"
                  class="w-full bg-transparent px-1 py-1.5 outline-none"
                  placeholder="0.00"
                />
              </div>
            </td>
            <td class="p-1 text-center">
              <button type="button" class="inline-flex text-slate-400 hover:text-rose-600" @click="removeRow(i)">
                <Trash2 :size="16" />
              </button>
            </td>
          </tr>
          <tr v-if="rows.length === 0">
            <td colspan="7" class="px-3 py-8 text-center text-slate-400">
              暂无书籍，先上传照片识别或手动添加
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <p v-if="error" class="text-sm text-rose-600">{{ error }}</p>

    <div class="flex flex-wrap items-center justify-between gap-3">
      <div class="flex flex-wrap items-center gap-2">
        <button
          type="button"
          @click="addRow"
          class="rounded-lg border border-slate-300 px-4 py-2 text-sm font-medium text-slate-600 hover:border-brand-300"
        >
          + 添加一行
        </button>
        <div v-if="rows.length > 0" class="flex items-center gap-2 rounded-lg border border-slate-200 bg-slate-50 px-2 py-1.5">
          <label class="text-sm text-slate-500">统一定价</label>
          <div class="flex items-center rounded-md border border-slate-300 bg-white focus-within:border-brand-300">
            <span class="pl-2 text-slate-400">¥</span>
            <input
              v-model="bulkPrice"
              type="number"
              min="0"
              step="0.01"
              placeholder="5"
              class="w-16 bg-transparent px-1 py-1 text-sm outline-none"
              @keyup.enter="applyBulkPrice"
            />
          </div>
          <button
            type="button"
            :disabled="bulkPrice === ''"
            @click="applyBulkPrice"
            class="rounded-md bg-brand-100 px-3 py-1 text-sm font-medium text-brand-700 hover:bg-brand-200 disabled:opacity-50"
          >
            全部应用
          </button>
        </div>
      </div>
      <button
        type="button"
        :disabled="submitting || rows.length === 0"
        @click="submit"
        class="rounded-lg bg-brand-600 px-6 py-2 text-sm font-medium text-white hover:bg-brand-700 disabled:opacity-50"
      >
        {{ submitting ? '上架中…' : `全部上架 (${rows.length})` }}
      </button>
    </div>
  </div>
</template>
