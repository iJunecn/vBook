<script setup>
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
  <view v-if="loading" class="loading vb-muted">加载中…</view>

  <view v-else-if="listing" class="page">
    <image class="cover" :src="mediaUrl(listing.cover_image)" mode="widthFix" />

    <view class="head vb-card">
      <text class="title">{{ listing.title }}</text>
      <view class="meta">
        <text v-if="listing.campus" class="vb-badge">{{ listing.campus }}</text>
        <text class="vb-muted">{{ formatDate(listing.created_at) }}</text>
      </view>
      <text v-if="listing.seller" class="vb-muted seller">
        卖家：{{ listing.seller.nickname || listing.seller.username }}
      </text>
      <text v-if="listing.description" class="desc">{{ listing.description }}</text>
    </view>

    <view class="books">
      <view v-for="book in listing.books" :key="book.id" class="book vb-card">
        <view class="book-main">
          <text class="b-title">{{ book.title }}</text>
          <text v-if="book.author || book.publisher" class="vb-muted b-sub">
            {{ [book.author, book.publisher].filter(Boolean).join(' · ') }}
          </text>
          <text v-if="book.isbn" class="vb-muted b-sub">ISBN: {{ book.isbn }}</text>
        </view>
        <view class="book-right">
          <text class="vb-price">{{ formatPrice(book.price) }}</text>

          <!-- 买家：购买 -->
          <template v-if="!isOwner">
            <wd-button
              v-if="book.status === 'available'"
              type="primary"
              size="small"
              @click="buy(book)"
            >
              购买
            </wd-button>
            <text v-else class="vb-badge is-danger">已售</text>
          </template>

          <!-- 卖家：管理 -->
          <template v-else>
            <wd-button size="small" plain @click="toggleStatus(book)">
              {{ book.status === 'available' ? '标记已售' : '恢复在售' }}
            </wd-button>
            <text class="del" @tap="removeBook(book)">删除</text>
          </template>
        </view>
      </view>
    </view>

    <view v-if="isOwner" class="owner-actions">
      <wd-button type="error" block plain @click="delist">下架整个书单</wd-button>
    </view>
  </view>
</template>

<style scoped lang="scss">
.loading {
  text-align: center;
  padding: 80rpx 0;
}
.page {
  padding: 24rpx;
}
.cover {
  width: 100%;
  border-radius: 20rpx;
  margin-bottom: 20rpx;
}
.head {
  padding: 24rpx;
  margin-bottom: 20rpx;
  display: flex;
  flex-direction: column;
  gap: 12rpx;
}
.title {
  font-size: 34rpx;
  font-weight: 700;
  color: var(--vb-ink-900);
}
.meta {
  display: flex;
  align-items: center;
  gap: 14rpx;
  font-size: 24rpx;
}
.seller {
  font-size: 24rpx;
}
.desc {
  font-size: 26rpx;
  color: var(--vb-ink-700);
  line-height: 1.6;
}
.book {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 22rpx;
  margin-bottom: 16rpx;
}
.book-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 6rpx;
  margin-right: 16rpx;
}
.b-title {
  font-size: 28rpx;
  font-weight: 600;
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
.del {
  font-size: 22rpx;
  color: #e23d3d;
}
.owner-actions {
  margin-top: 12rpx;
}
</style>
