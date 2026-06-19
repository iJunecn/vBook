<script setup>
import { ref, computed } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { orderApi } from '@/api'
import { useUserStore } from '@/store/user'
import { formatPrice, formatDate } from '@/utils/format'

const userStore = useUserStore()
const tab = ref('bought')
const orders = ref([])
const loading = ref(false)

const myId = computed(() => userStore.user?.id)
const bought = computed(() => orders.value.filter((o) => o.buyer_id === myId.value))
const sold = computed(() => orders.value.filter((o) => o.seller_id === myId.value))
const list = computed(() => (tab.value === 'bought' ? bought.value : sold.value))

onShow(() => {
  if (!userStore.isLogin) {
    uni.showToast({ title: '请先登录', icon: 'none' })
    setTimeout(() => uni.navigateTo({ url: '/pages/login/login' }), 300)
    return
  }
  load()
})

async function load() {
  loading.value = true
  try {
    orders.value = await orderApi.mine()
  } catch (e) {
    /* 拦截器已提示 */
  } finally {
    loading.value = false
  }
}

const statusText = (s) => ({ paid: '已支付', completed: '已完成', cancelled: '已取消' })[s] || s
</script>

<template>
  <view class="page">
    <view class="tabs">
      <text :class="['tab', tab === 'bought' ? 'on' : '']" @tap="tab = 'bought'">
        我买的 ({{ bought.length }})
      </text>
      <text :class="['tab', tab === 'sold' ? 'on' : '']" @tap="tab = 'sold'">
        我卖的 ({{ sold.length }})
      </text>
    </view>

    <view v-if="list.length" class="list">
      <view v-for="o in list" :key="o.id" class="order vb-card">
        <view class="order-top">
          <text class="o-title">{{ o.book?.title || '书籍' }}</text>
          <text class="vb-badge">{{ statusText(o.status) }}</text>
        </view>
        <view class="order-bottom">
          <text class="vb-muted">{{ formatDate(o.created_at) }}</text>
          <text class="vb-price">{{ formatPrice(o.price) }}</text>
        </view>
        <text v-if="o.note" class="vb-muted note">备注：{{ o.note }}</text>
      </view>
    </view>

    <view v-else-if="!loading" class="empty vb-muted">
      {{ tab === 'bought' ? '还没有买过书' : '还没有卖出记录' }}
    </view>
  </view>
</template>

<style scoped lang="scss">
.page {
  padding: 24rpx;
}
.tabs {
  display: flex;
  gap: 16rpx;
  margin-bottom: 24rpx;
}
.tab {
  flex: 1;
  text-align: center;
  padding: 18rpx 0;
  font-size: 28rpx;
  background: #fff;
  border-radius: 16rpx;
  border: 1rpx solid var(--vb-brand-100);
  color: var(--vb-ink-500);
}
.tab.on {
  background: var(--vb-brand-600);
  color: #fff;
  border-color: var(--vb-brand-600);
}
.order {
  padding: 22rpx;
  margin-bottom: 16rpx;
}
.order-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12rpx;
}
.o-title {
  font-size: 28rpx;
  font-weight: 600;
}
.order-bottom {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  font-size: 24rpx;
}
.note {
  display: block;
  font-size: 22rpx;
  margin-top: 10rpx;
}
.empty {
  text-align: center;
  padding: 80rpx 0;
}
</style>
