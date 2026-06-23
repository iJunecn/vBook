<script setup lang="ts">
import { computed, ref } from 'vue';
import type { BookListItem } from './types';
import SearchBar from './SearchBar.vue';
import CampusFilter from './CampusFilter.vue';
import BookCard from './BookCard.vue';

const props = defineProps<{ books: BookListItem[] }>();

const query = ref('');
const campus = ref('');

const filtered = computed(() => {
  const q = query.value.trim().toLowerCase();
  return props.books.filter((b) => {
    if (campus.value && b.sellerCampus !== campus.value) return false;
    if (!q) return true;
    return [b.title, b.author, b.publisher]
      .filter(Boolean)
      .some((field) => field!.toLowerCase().includes(q));
  });
});
</script>

<template>
  <div class="space-y-5">
    <SearchBar v-model="query" />
    <CampusFilter v-model="campus" />

    <p class="text-sm text-slate-400">共 {{ filtered.length }} 本在售</p>

    <div
      v-if="filtered.length"
      class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4"
    >
      <BookCard v-for="book in filtered" :key="book.id" :book="book" />
    </div>

    <div v-else class="rounded-xl border border-dashed border-slate-300 py-16 text-center text-slate-400">
      没有找到符合条件的书籍
    </div>
  </div>
</template>
