<script setup lang="ts">
import { ref } from 'vue';

const props = defineProps<{ modelValue: string }>();
const emit = defineEmits<{
  (e: 'update:modelValue', value: string): void;
  (e: 'change', value: string): void;
}>();

const options = [
  { value: '', label: '全部校区' },
  { value: 'main', label: '主校区' },
  { value: 'north', label: '北校区' },
  { value: 'south', label: '南校区' },
  { value: 'east', label: '东校区' },
];

const current = ref(props.modelValue);

function select(value: string) {
  current.value = value;
  emit('update:modelValue', value);
  emit('change', value);
}
</script>

<template>
  <div class="flex flex-wrap gap-2">
    <button
      v-for="opt in options"
      :key="opt.value"
      type="button"
      @click="select(opt.value)"
      :class="[
        'px-3 py-1.5 rounded-full text-sm font-medium transition-colors border',
        current === opt.value
          ? 'bg-brand-600 text-white border-brand-600'
          : 'bg-white text-slate-600 border-slate-200 hover:border-brand-300',
      ]"
    >
      {{ opt.label }}
    </button>
  </div>
</template>
