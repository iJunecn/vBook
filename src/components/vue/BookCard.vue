<script setup lang="ts">
import type { BookListItem } from './types';
import { CAMPUS_LABELS } from './types';

defineProps<{ book: BookListItem }>();
</script>

<template>
  <a
    :href="`/book/${book.id}`"
    class="group flex flex-col rounded-xl border border-slate-200 bg-white p-4 transition-all hover:-translate-y-0.5 hover:border-brand-300 hover:shadow-md"
  >
    <div class="flex items-start justify-between gap-2">
      <h3 class="font-semibold text-slate-800 line-clamp-2 group-hover:text-brand-700">
        {{ book.title }}
      </h3>
      <span
        v-if="book.sellerCampus"
        class="shrink-0 rounded-full bg-brand-50 px-2 py-0.5 text-xs font-medium text-brand-700"
      >
        {{ CAMPUS_LABELS[book.sellerCampus] || book.sellerCampus }}
      </span>
    </div>

    <p v-if="book.author" class="mt-1 text-sm text-slate-500 line-clamp-1">
      {{ book.author }}
    </p>
    <p v-if="book.publisher" class="text-xs text-slate-400 line-clamp-1">
      {{ book.publisher }}
    </p>

    <div class="mt-auto flex items-end justify-between pt-3">
      <span class="text-lg font-bold text-rose-600">¥{{ book.price }}</span>
      <span class="text-xs text-slate-400">{{ book.sellerNickname || '匿名卖家' }}</span>
    </div>
  </a>
</template>
