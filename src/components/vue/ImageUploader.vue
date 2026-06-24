<script setup lang="ts">
import { ref } from 'vue';
import { Library } from 'lucide-vue-next';

const props = defineProps<{ loading?: boolean }>();
const emit = defineEmits<{ (e: 'recognize', file: File): void }>();

const MAX_SIZE = 10 * 1024 * 1024;
const preview = ref<string | null>(null);
const error = ref<string | null>(null);
const dragging = ref(false);
const fileInput = ref<HTMLInputElement | null>(null);
let selected: File | null = null;

function handleFile(file: File | undefined | null) {
  error.value = null;
  if (!file) return;
  if (!file.type.startsWith('image/')) {
    error.value = '请选择图片文件';
    return;
  }
  if (file.size > MAX_SIZE) {
    error.value = '图片不能超过 10MB';
    return;
  }
  selected = file;
  if (preview.value) URL.revokeObjectURL(preview.value);
  preview.value = URL.createObjectURL(file);
}

function onInputChange(e: Event) {
  handleFile((e.target as HTMLInputElement).files?.[0]);
}

function onDrop(e: DragEvent) {
  dragging.value = false;
  handleFile(e.dataTransfer?.files?.[0]);
}

function recognize() {
  if (selected && !props.loading) emit('recognize', selected);
}
</script>

<template>
  <div class="space-y-3">
    <div
      @click="fileInput?.click()"
      @dragover.prevent="dragging = true"
      @dragleave.prevent="dragging = false"
      @drop.prevent="onDrop"
      :class="[
        'flex cursor-pointer flex-col items-center justify-center rounded-xl border-2 border-dashed p-8 text-center transition-colors',
        dragging ? 'border-brand-400 bg-brand-50' : 'border-slate-300 bg-white hover:border-brand-300',
      ]"
    >
      <template v-if="preview">
        <img :src="preview" alt="预览" class="max-h-64 rounded-lg object-contain" />
        <p class="mt-2 text-xs text-slate-400">点击或拖拽以更换图片</p>
      </template>
      <template v-else>
        <Library :size="40" :stroke-width="1.5" class="text-slate-400" />
        <p class="mt-2 font-medium text-slate-600">点击上传 或 拖拽书脊照片到此处</p>
        <p class="text-xs text-slate-400">支持 JPG / PNG / WEBP，最大 10MB</p>
      </template>
      <input
        ref="fileInput"
        type="file"
        accept="image/*"
        class="hidden"
        @change="onInputChange"
      />
    </div>

    <p v-if="error" class="text-sm text-rose-600">{{ error }}</p>

    <button
      type="button"
      :disabled="!preview || loading"
      @click="recognize"
      class="w-full rounded-xl bg-brand-600 py-3 font-medium text-white transition hover:bg-brand-700 disabled:cursor-not-allowed disabled:opacity-50"
    >
      <span v-if="loading" class="inline-flex items-center gap-2">
        <span class="h-4 w-4 animate-spin rounded-full border-2 border-white/40 border-t-white"></span>
        AI 识别中…
      </span>
      <span v-else>开始 AI 识别</span>
    </button>
  </div>
</template>
