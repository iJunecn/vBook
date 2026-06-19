<script setup>
import { onLaunch } from '@dcloudio/uni-app'
import { useUserStore } from '@/store/user'

onLaunch(() => {
  // 启动时恢复本地登录态
  useUserStore().loadFromStorage()
})
</script>

<template>
  <!-- App.vue 不渲染内容，页面由 pages.json 驱动 -->
</template>

<style lang="scss">
@import './styles/theme.scss';

/* 全局基础样式（小程序 / H5 通用） */
page {
  background: var(--vb-bg);
  color: var(--vb-ink-900);
  font-size: 28rpx;
  font-family: -apple-system, BlinkMacSystemFont, 'PingFang SC', 'Helvetica Neue', Helvetica, Arial,
    sans-serif;
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
</style>
