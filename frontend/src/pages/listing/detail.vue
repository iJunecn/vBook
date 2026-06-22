<script setup>
/**
 * 书单详情页（vUSTB surface-card 风格）
 *  - 顶部封面 + 头卡（标题 / 校区徽章 / 卖家 / 描述）
 *  - 书目列表（surface-card + 价格 + 购买按钮）
 *  - 卖家管理操作
 */
import { ref, computed } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import { bookApi, orderApi } from '@/api'
import { useUserStore } from '@/store/user'
import { formatPrice, formatDate, mediaUrl } from '@/utils/format'

const userStore = useUserStore()
const listing = ref(null)
const loading = ref(true)
let listingId = null

const isOwner = computed(
  () => listing.value && userStore.user && listing.value.seller_id === userStore.user.id,
)

onLoad((opts) => {
  listingId = opts.id
  fetchDetail()
})

async function fetchDetail() {
  loading.value = true
  try {
    listing.value = await bookApi.getListing(listingId)
  } catch (e) {
    /* 拦截器已提示 */
  } finally {
    loading.value = false
  }
}

function buy(book) {
  if (!userStore.isLogin) {
    uni.navigateTo({ url: '/pages/login/login' })
    return
  }
  uni.showModal({
    title: '确认购买',
    content: `《${book.title}》 ${formatPrice(book.price)}`,
    success: async (r) => {
      if (!r.confirm) return
      try {
        await orderApi.create({ book_id: book.id })
        uni.showToast({ title: '下单成功', icon: 'success' })
        fetchDetail()
      } catch (e) {
        /* 拦截器已提示 */
      }
    },
  })
}

// ---- 卖家操作 ----
async function toggleStatus(book) {
  const next = book.status === 'available' ? 'sold' : 'available'
  try {
    await bookApi.updateBook(book.id, { status: next })
    fetchDetail()
  } catch (e) {
    /* 拦截器已提示 */
  }
}

function removeBook(book) {
  uni.showModal({
    title: '删除这本书？',
    content: book.title,
    success: async (r) => {
      if (!r.confirm) return
      try {
        await bookApi.deleteBook(book.id)
        fetchDetail()
      } catch (e) {
        /* 拦截器已提示 */
      }
    },
  })
}

function delist() {
  uni.showModal({
    title: '下架整个书单？',
    content: '下架后买家将无法看到此书单',
    success: async (r) => {
      if (!r.confirm) return
      try {
        await bookApi.deleteListing(listingId)
        uni.showToast({ title: '已下架', icon: 'success' })
        setTimeout(() => uni.navigateBack(), 600)
      } catch (e) {
        /* 拦截器已提示 */
      }
    },
  })
}
</script>

<template>
  <view v-if="loading" class="loading muted">加载中…</view>

  <view v-else-if="listing" class="page">
    <view class="cover-wrap surface-card">
      <image class="cover" :src="mediaUrl(listing.cover_image)" mode="widthFix" />
    </view>

    <view class="head surface-card">
      <text class="title">{{ listing.title }}</text>
      <view class="meta">
        <text v-if="listing.campus" class="campus-badge">{{ listing.campus }}</text>
        <text class="muted">{{ formatDate(listing.created_at) }}</text>
        <text v-if="listing.book_count" class="muted">· 共 {{ listing.book_count }} 本</text>
      </view>
      <text v-if="listing.seller" class="seller muted">
        👤 卖家：{{ listing.seller.nickname || listing.seller.username }}
      </text>
      <text v-if="listing.description" class="desc">{{ listing.description }}</text>
    </view>

    <view class="section-head">
      <text class="section-kicker">书目清单</text>
    </view>

    <view class="books">
      <view v-for="book in listing.books" :key="book.id" class="book surface-card">
        <view class="book-main">
          <text class="b-title">{{ book.title }}</text>
          <text v-if="book.author || book.publisher" class="b-sub muted">
            {{ [book.author, book.publisher].filter(Boolean).join(' · ') }}
          </text>
          <text v-if="book.isbn" class="b-sub muted">ISBN: {{ book.isbn }}</text>
        </view>
        <view class="book-right">
          <text class="price">{{ formatPrice(book.price) }}</text>

          <!-- 买家：购买 -->
          <template v-if="!isOwner">
            <button
              v-if="book.status === 'available'"
              class="btn-primary buy-btn"
              @click="buy(book)"
            >
              购买
            </button>
            <text v-else class="sold-badge">已售</text>
          </template>

          <!-- 卖家：管理 -->
          <template v-else>
            <button class="btn-ghost mgmt-btn" @click="toggleStatus(book)">
              {{ book.status === 'available' ? '标记已售' : '恢复在售' }}
            </button>
            <text class="del" @tap="removeBook(book)">删除</text>
          </template>
        </view>
      </view>
    </view>

    <view v-if="isOwner" class="owner-actions">
      <button class="btn-danger owner-btn" @click="delist">下架整个书单</button>
    </view>
  </view>
</template>

<style scoped lang="scss">
.loading {
  text-align: center;
  padding: 80rpx 0;
  font-size: 26rpx;
}
.muted {
  color: var(--vb-ink-500);
}
.page {
  padding: 24rpx;
  display: flex;
  flex-direction: column;
  gap: 20rpx;
}
.cover-wrap {
  padding: 0;
  overflow: hidden;
}
.cover {
  width: 100%;
  display: block;
}
.head {
  padding: 24rpx;
  display: flex;
  flex-direction: column;
  gap: 12rpx;
}
.title {
  font-size: 34rpx;
  font-weight: 700;
  color: var(--vb-heading);
  letter-spacing: 0.01em;
}
.meta {
  display: flex;
  align-items: center;
  gap: 12rpx;
  font-size: 22rpx;
  flex-wrap: wrap;
}
.campus-badge {
  display: inline-block;
  padding: 2rpx 12rpx;
  border-radius: 999px;
  font-size: 20rpx;
  font-weight: 500;
  background: var(--vb-brand-50);
  color: var(--vb-brand-700);
}
.seller {
  font-size: 24rpx;
}
.desc {
  font-size: 26rpx;
  color: var(--vb-ink-700);
  line-height: 1.65;
  margin-top: 4rpx;
}
.section-head {
  margin-top: 8rpx;
}
.section-kicker {
  font-size: 22rpx;
  font-weight: 700;
  letter-spacing: 0.06em;
  color: var(--vb-ink-500);
}
.books {
  display: flex;
  flex-direction: column;
  gap: 16rpx;
}
.book {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 22rpx;
  gap: 16rpx;
}
.book-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 6rpx;
  min-width: 0;
}
.b-title {
  font-size: 28rpx;
  font-weight: 600;
  color: var(--vb-heading);
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}
.b-sub {
  font-size: 22rpx;
}
.book-right {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 12rpx;
}
.price {
  font-size: 30rpx;
  font-weight: 700;
  color: var(--vb-danger);
}
.buy-btn {
  padding: 10rpx 28rpx;
  font-size: 24rpx;
  border: none;
}
.buy-btn::after {
  border: none;
}
.mgmt-btn {
  padding: 8rpx 20rpx;
  font-size: 22rpx;
  border: none;
}
.mgmt-btn::after {
  border: none;
}
.sold-badge {
  display: inline-block;
  padding: 8rpx 20rpx;
  border-radius: 8rpx;
  font-size: 22rpx;
  font-weight: 600;
  background: #fdeaea;
  color: var(--vb-danger);
}
.del {
  font-size: 22rpx;
  color: var(--vb-danger);
  font-weight: 500;
}
.owner-actions {
  margin-top: 16rpx;
}
.owner-btn {
  width: 100%;
  padding: 18rpx;
  font-size: 28rpx;
  border: none;
}
.owner-btn::after {
  border: none;
}
</style>