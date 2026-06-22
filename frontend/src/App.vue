<script setup>
import { computed } from 'vue'
import { onLaunch } from '@dcloudio/uni-app'
import { useUserStore } from '@/store/user'

onLaunch(() => {
  // 启动时恢复本地登录态
  useUserStore().loadFromStorage()
})

// 顶部导航数据（PC 端显示，移动端隐藏）
const userStore = useUserStore()
const isLogin = computed(() => userStore.isLogin)
const userNick = computed(() => userStore.user?.nickname || userStore.user?.username || '')

const navItems = [
  { key: 'home', label: '首页', path: '/pages/index/index', type: 'tab' },
  { key: 'sell', label: '卖书', path: '/pages/sell/sell', type: 'tab' },
  { key: 'orders', label: '订单', path: '/pages/orders/orders', type: 'tab' },
  { key: 'profile', label: '我的', path: '/pages/profile/profile', type: 'tab' },
]

function go(path, type) {
  if (type === 'tab') uni.switchTab({ url: path })
  else uni.navigateTo({ url: path })
}

function goLogin() {
  uni.navigateTo({ url: '/pages/login/login' })
}
</script>

<template>
  <!-- PC 端顶部导航（移动端隐藏，靠 uni-app 自带 tabBar 导航） -->
  <view class="pc-nav">
    <view class="pc-nav-inner">
      <view class="pc-brand" @tap="go('/pages/index/index', 'tab')">
        <text class="pc-logo">📚</text>
        <text class="pc-name">贝壳易书</text>
      </view>
      <view class="pc-menu">
        <text
          v-for="item in navItems"
          :key="item.key"
          class="pc-menu-item"
          @tap="go(item.path, item.type)"
        >
          {{ item.label }}
        </text>
      </view>
      <view class="pc-right">
        <template v-if="isLogin">
          <text class="pc-user" @tap="go('/pages/profile/profile', 'tab')">
            {{ userNick }}
          </text>
        </template>
        <text v-else class="pc-login" @tap="goLogin">登录 / 注册</text>
      </view>
    </view>
  </view>

  <!-- App.vue 不渲染内容，页面由 pages.json 驱动 -->
</template>

<style lang="scss">
@import './styles/theme.scss';
@import './styles/desktop.scss';

/* 全局基础样式（小程序 / H5 通用） */
page {
  background: var(--vb-bg);
  color: var(--vb-ink-900);
  font-size: 28rpx;
  font-family: -apple-system, BlinkMacSystemFont, 'PingFang SC', 'Helvetica Neue', Helvetica, Arial,
    'Microsoft YaHei', sans-serif;
}

.vb-container {
  padding: 24rpx;
}

.vb-card {
  background: #fff;
  border-radius: 20rpx;
  border: 1rpx solid var(--vb-brand-100);
  box-shadow: 0 4rpx 16rpx rgba(37, 99, 235, 0.06);
}

.vb-price {
  color: #e23d3d;
  font-weight: 700;
}

.vb-muted {
  color: var(--vb-ink-500);
}

.vb-badge {
  display: inline-block;
  padding: 2rpx 14rpx;
  border-radius: 999rpx;
  font-size: 22rpx;
  background: var(--vb-brand-50);
  color: var(--vb-brand-600);
}

.vb-badge.is-danger {
  background: #fdeaea;
  color: #e23d3d;
}

/* 工具类 */
.vb-stack {
  display: flex;
  flex-direction: column;
}
.vb-row {
  display: flex;
  align-items: center;
}
.vb-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20rpx;
}
.vb-spacer {
  flex: 1;
}

/* .pc-nav 的基线 display:none 在 styles/desktop.scss 里，PC 端 @media 块覆盖 */
</style>
