<script setup>
import { useRouter } from 'vue-router'
import { formatPrice, formatDate } from '@/utils/format'

const props = defineProps({
  listing: { type: Object, required: true },
})
const router = useRouter()

function open() {
  router.push(`/listings/${props.listing.id}`)
}
</script>

<template>
  <div class="card" @click="open">
    <div class="cover">
      <img :src="listing.cover_image" :alt="listing.title" loading="lazy" />
      <span v-if="listing.available_count === 0" class="vb-badge sold">已售罄</span>
      <span v-else-if="listing.status === 'removed'" class="vb-badge removed">已下架</span>
    </div>
    <div class="body">
      <h3 class="title">{{ listing.title }}</h3>
      <div class="meta">
        <span class="vb-badge" v-if="listing.campus">{{ listing.campus }}</span>
        <span class="text-muted">共 {{ listing.book_count }} 本</span>
        <span v-if="listing.available_count < listing.book_count" class="text-muted">
          剩 {{ listing.available_count }} 本
        </span>
      </div>
      <div class="bottom">
        <div class="price-tag">
          {{ formatPrice(listing.default_price) }}<small>/本起</small>
        </div>
        <div class="text-muted time">{{ formatDate(listing.created_at) }}</div>
      </div>
      <div v-if="listing.seller" class="seller text-muted">
        @{{ listing.seller.nickname || listing.seller.username }}
      </div>
    </div>
  </div>
</template>

<style scoped>
.card {
  background: #fff;
  border-radius: var(--radius);
  overflow: hidden;
  border: 1px solid var(--brand-100);
  transition: all 0.2s;
  cursor: pointer;
  height: 100%;
  display: flex;
  flex-direction: column;
}
.card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-lg);
  border-color: var(--brand-300);
}
.cover {
  position: relative;
  aspect-ratio: 4 / 3;
  background: var(--brand-50);
  overflow: hidden;
}
.cover img {
  width: 100%; height: 100%; object-fit: cover;
}
.cover .vb-badge {
  position: absolute; top: 8px; right: 8px;
}
.body { padding: 12px 14px 14px; flex: 1; display: flex; flex-direction: column; }
.title {
  font-size: 15px; font-weight: 600; color: var(--ink-900);
  margin: 0 0 6px;
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}
.meta {
  display: flex; gap: 8px; font-size: 12px;
  margin-bottom: 8px; align-items: center;
}
.bottom {
  display: flex; align-items: baseline; justify-content: space-between;
  margin-top: auto;
}
.time { font-size: 12px; }
.seller { font-size: 12px; margin-top: 4px; }
</style>
