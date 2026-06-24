<script setup lang="ts">
import { Search } from 'lucide-vue-next';

defineProps<{ modelValue: string }>();
const emit = defineEmits<{ (e: 'update:modelValue', value: string): void }>();
</script>

<template>
  <div class="relative">
    <span class="pointer-events-none absolute inset-y-0 left-3 flex items-center text-slate-400">
      <Search :size="18" />
    </span>
    <input
      :value="modelValue"
      @input="emit('update:modelValue', ($event.target as HTMLInputElement).value)"
      type="search"
      placeholder="搜索书名、作者、出版社…"
      class="w-full rounded-xl border border-slate-200 bg-white py-3 pl-10 pr-4 text-sm outline-none transition focus:border-brand-400 focus:ring-2 focus:ring-brand-100"
    />
  </div>
</template>
