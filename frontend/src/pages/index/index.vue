<script setup>
/**
 * 首页：浏览书单 + 搜索 + 校区筛选
 * 视觉：vUSTB 风格 —— hero 渐变卡 + search 行 + 3-4 列网格
 */
import { ref } from 'vue'
import { onShow, onPullDownRefresh, onReachBottom } from '@dcloudio/uni-app'
import { bookApi } from '@/api'
import ListingCard from '@/components/ListingCard.vue'

const q = ref('')
const campus = ref('')
const listings = ref([])
const page = ref(1)
const pageSize = 20
const loading = ref(false)
const finished = ref(false)

async function load(reset = false) {
  if (loading.value) return
  if (reset) {
    page.value = 1
    finished.value = false
    listings.value = []
  }
  if (finished.value) return
  loading.value = true
  try {
    const rows = await bookApi.listListings({
      q: q.value,
      campus: campus.value,
      page: page.value,
      page_size: pageSize,
    })
    listings.value = reset ? rows : listings.value.concat(rows)
    if (rows.length < pageSize) finished.value = true
    else page.value += 1
  } catch (e) {
    /* 错误提示已在拦截器处理 */
  } finally {
    loading.value = false
  }
}

function onSearch() {
  load(true)
}

let firstShown = false
onShow(() => {
  if (!firstShown) {
    firstShown = true
    load(true)
  }
})

onPullDownRefresh(async () => {
  await load(true)
  uni.stopPullDownRefresh()
})

onReachBottom(() => load())

function goSell() {
  uni.switchTab({ url: '/pages/sell/sell' })
}
</script>

<template>
  <view class="page">
    <view class="hero">
      <text class="hero-eyebrow">校园二手书流转平台</text>
      <text class="hero-title">拍照卖书，一键识别</text>
      <text class="hero-sub">把一摞书拍下来，AI 自动识别书名与价格</text>
      <view class="hero-actions">
        <button class="btn-primary hero-btn" @click="goSell">我要卖书</button>
      </view>
    </view>

    <view class="filters surface-card">
      <view class="search-row">
        <text class="search-icon">🔍</text>
        <input
          v-model="q"
          class="search-input"
          placeholder="搜索书名 / 作者 / 出版社"
          confirm-type="search"
          @confirm="onSearch"
        />
      </view>
      <view class="campus-row">
        <text class="filter-icon">📍</text>
        <input
          v-model="campus"
          class="campus-input"
          placeholder="按校区筛选（可选）"
          confirm-type="search"
          @confirm="onSearch"
        />
        <button class="btn-ghost filter-btn" @click="onSearch">筛选</button>
      </view>
    </view>

    <view class="section-head">
      <text class="section-kicker">在售书单</text>
      <text class="muted">共 {{ listings.length }} 单</text>
    </view>

    <view v-if="listings.length" class="grid">
      <view v-for="item in listings" :key="item.id" class="grid-item">
        <ListingCard :listing="item" />
      </view>
    </view>

    <view v-else-if="!loading" class="empty">
      <text class="empty-icon">📭</text>
      <text class="empty-text muted">暂无在售书单，去发布第一单吧～</text>
    </view>

    <view v-if="loading" class="loading muted">加载中…</view>
    <view v-else-if="finished && listings.length" class="loading muted">— 没有更多了 —</view>
  </view>
</template>

<style scoped lang="scss">
.page {
  padding: 24rpx;
}
/* ===== Hero ===== */
.hero {
  position: relative;
  background: linear-gradient(135deg, var(--vb-brand-600) 0%, var(--vb-brand-700) 50%, var(--vb-accent-500) 100%);
  border-radius: 16px;
  padding: 40rpx 36rpx;
  display: flex;
  flex-direction: column;
  gap: 12rpx;
  margin-bottom: 24rpx;
  overflow: hidden;
  color: #fff;
}
.hero::before {
  content: '';
  position: absolute;
  top: -40rpx;
  right: -40rpx;
  width: 220rpx;
  height: 220rpx;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.08);
}
.hero::after {
  content: '';
  position: absolute;
  bottom: -60rpx;
  right: 80rpx;
  width: 140rpx;
  height: 140rpx;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.05);
}
.hero-eyebrow {
  font-size: 22rpx;
  font-weight: 600;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: rgba(255, 255, 255, 0.78);
}
.hero-title {
  font-size: 38rpx;
  font-weight: 700;
  letter-spacing: 0.02em;
  position: relative;
}
.hero-sub {
  font-size: 24rpx;
  color: rgba(255, 255, 255, 0.86);
}
.hero-actions {
  margin-top: 12rpx;
  position: relative;
}
.hero-btn {
  background: #fff;
  color: var(--vb-brand-700);
  border: none;
  padding: 14rpx 32rpx;
  font-weight: 600;
  border-radius: 10px;
  font-size: 26rpx;
}
.hero-btn::after {
  border: none;
}

/* ===== Filters ===== */
.filters {
  padding: 20rpx;
  margin-bottom: 24rpx;
  border-radius: 16rpx;
}
.search-row {
  display: flex;
  align-items: center;
  gap: 12rpx;
  padding: 6rpx 16rpx;
  background: var(--vb-bg-soft);
  border-radius: 10px;
  border: 1px solid var(--vb-border);
}
.search-icon {
  font-size: 26rpx;
  color: var(--vb-ink-400);
}
.search-input {
  flex: 1;
  font-size: 26rpx;
  color: var(--vb-ink-900);
}
.campus-row {
  display: flex;
  align-items: center;
  gap: 12rpx;
  margin-top: 16rpx;
}
.filter-icon {
  font-size: 26rpx;
  color: var(--vb-ink-400);
}
.campus-input {
  flex: 1;
  background: var(--vb-bg-soft);
  border: 1px solid var(--vb-border);
  border-radius: 10px;
  padding: 14rpx 16rpx;
  font-size: 26rpx;
  color: var(--vb-ink-900);
}
.filter-btn {
  padding: 12rpx 24rpx;
  font-size: 24rpx;
}
.filter-btn::after {
  border: none;
}

/* ===== Section ===== */
.section-head {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  margin-bottom: 18rpx;
}
.section-kicker {
  font-size: 24rpx;
  font-weight: 700;
  letter-spacing: 0.04em;
  color: var(--vb-heading);
  text-transform: none;
}
.muted {
  color: var(--vb-ink-500);
  font-size: 22rpx;
}

/* ===== Grid ===== */
.grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20rpx;
}
.grid-item {
  width: 100%;
}

/* ===== Empty / Loading ===== */
.empty {
  text-align: center;
  padding: 80rpx 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12rpx;
}
.empty-icon {
  font-size: 80rpx;
  opacity: 0.6;
}
.empty-text {
  font-size: 26rpx;
}
.loading {
  text-align: center;
  padding: 48rpx 0;
  font-size: 24rpx;
}
</style>