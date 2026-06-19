<script setup>
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
      <text class="hero-title">📚 拍照卖书，一键识别</text>
      <text class="hero-sub">把一摞书拍下来，AI 自动识别书名与价格</text>
      <wd-button type="primary" size="medium" @click="goSell">我要卖书</wd-button>
    </view>

    <view class="filters">
      <wd-search
        v-model="q"
        placeholder="搜索书名 / 作者 / 出版社"
        hide-cancel
        @search="onSearch"
        @clear="onSearch"
      />
      <view class="campus-row">
        <input
          v-model="campus"
          class="campus-input"
          placeholder="按校区筛选（可选）"
          confirm-type="search"
          @confirm="onSearch"
        />
        <wd-button size="small" plain @click="onSearch">筛选</wd-button>
      </view>
    </view>

    <view v-if="listings.length" class="grid">
      <view v-for="item in listings" :key="item.id" class="grid-item">
        <ListingCard :listing="item" />
      </view>
    </view>

    <view v-else-if="!loading" class="empty">
      <text class="vb-muted">暂无在售书单，去发布第一单吧～</text>
    </view>

    <view v-if="loading" class="loading vb-muted">加载中…</view>
    <view v-else-if="finished && listings.length" class="loading vb-muted">没有更多了</view>
  </view>
</template>

<style scoped lang="scss">
.page {
  padding: 24rpx;
}
.hero {
  background: linear-gradient(135deg, #2563eb, #1d4ed8);
  border-radius: 24rpx;
  padding: 36rpx 32rpx;
  display: flex;
  flex-direction: column;
  gap: 14rpx;
  margin-bottom: 24rpx;
}
.hero-title {
  color: #fff;
  font-size: 36rpx;
  font-weight: 700;
}
.hero-sub {
  color: rgba(255, 255, 255, 0.85);
  font-size: 24rpx;
  margin-bottom: 8rpx;
}
.filters {
  margin-bottom: 20rpx;
}
.campus-row {
  display: flex;
  align-items: center;
  gap: 16rpx;
  margin-top: 16rpx;
}
.campus-input {
  flex: 1;
  background: #fff;
  border: 1rpx solid var(--vb-brand-100);
  border-radius: 16rpx;
  padding: 16rpx 20rpx;
  font-size: 26rpx;
}
.grid {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
}
.grid-item {
  width: 48.5%;
  margin-bottom: 20rpx;
}
.empty,
.loading {
  text-align: center;
  padding: 48rpx 0;
  font-size: 26rpx;
}
</style>
