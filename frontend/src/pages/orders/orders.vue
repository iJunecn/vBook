<script setup>
/**
 * 订单页（vUSTB 风格）
 *  - tab 切换（我买的 / 我卖的）
 *  - 订单卡片用 surface-card
 */
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
const statusClass = (s) =>
  ({ paid: 'badge-warn', completed: 'badge-ok', cancelled: 'badge-muted' })[s] || 'badge-muted'
</script>

<template>
  <view class="page">
    <view class="tabs surface-card">
      <text :class="['tab', tab === 'bought' ? 'on' : '']" @tap="tab = 'bought'">
        我买的
        <text class="count">({{ bought.length }})</text>
      </text>
      <text :class="['tab', tab === 'sold' ? 'on' : '']" @tap="tab = 'sold'">
        我卖的
        <text class="count">({{ sold.length }})</text>
      </text>
    </view>

    <view v-if="list.length" class="list">
      <view v-for="o in list" :key="o.id" class="order surface-card">
        <view class="order-top">
          <text class="o-title">《{{ o.book?.title || '书籍' }}》</text>
          <text :class="['status-badge', statusClass(o.status)]">{{ statusText(o.status) }}</text>
        </view>
        <view class="order-bottom">
          <text class="muted">{{ formatDate(o.created_at) }}</text>
          <text class="price">{{ formatPrice(o.price) }}</text>
        </view>
        <text v-if="o.note" class="note muted">备注：{{ o.note }}</text>
      </view>
    </view>

    <view v-else-if="!loading" class="empty">
      <text class="empty-icon">📋</text>
      <text class="muted">
        {{ tab === 'bought' ? '还没有买过书' : '还没有卖出记录' }}
      </text>
    </view>
  </view>
</template>

<style scoped lang="scss">
.page {
  padding: 24rpx;
  display: flex;
  flex-direction: column;
  gap: 20rpx;
}
.tabs {
  display: flex;
  gap: 0;
  padding: 6rpx;
  border-radius: 12px;
}
.tab {
  flex: 1;
  text-align: center;
  padding: 16rpx 0;
  font-size: 26rpx;
  font-weight: 500;
  color: var(--vb-ink-500);
  border-radius: 8px;
  transition: background 0.15s ease, color 0.15s ease;
}
.tab.on {
  background: var(--vb-brand-600);
  color: #fff;
  font-weight: 600;
  box-shadow: 0 2px 8px rgba(47, 120, 186, 0.25);
}
.tab .count {
  font-weight: 400;
  font-size: 22rpx;
  opacity: 0.85;
}
.tab.on .count {
  opacity: 0.9;
}
.list {
  display: flex;
  flex-direction: column;
  gap: 16rpx;
}
.order {
  padding: 22rpx 24rpx;
  display: flex;
  flex-direction: column;
  gap: 10rpx;
}
.order-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12rpx;
}
.o-title {
  flex: 1;
  font-size: 28rpx;
  font-weight: 600;
  color: var(--vb-heading);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.status-badge {
  padding: 4rpx 14rpx;
  border-radius: 999px;
  font-size: 22rpx;
  font-weight: 600;
  flex-shrink: 0;
}
.badge-ok {
  background: rgba(34, 197, 94, 0.12);
  color: #15803d;
}
.badge-warn {
  background: rgba(234, 179, 8, 0.14);
  color: #b45309;
}
.badge-muted {
  background: var(--vb-bg-mute);
  color: var(--vb-ink-500);
}
.order-bottom {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
}
.muted {
  color: var(--vb-ink-500);
  font-size: 22rpx;
}
.price {
  font-size: 30rpx;
  font-weight: 700;
  color: var(--vb-danger);
}
.note {
  font-size: 22rpx;
  margin-top: 4rpx;
  display: block;
}
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
  opacity: 0.5;
}
</style>