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
  // 用 reLaunch 替换整栈，避免浏览器后退回到本页造成死循环
  uni.reLaunch({ url: '/pages/login/login?from=pcnav' })
}
</script>

<template>
  <!-- PC 端顶部导航（移动端隐藏，靠 uni-app 自带 tabBar 导航） -->
  <view class="pc-nav">
    <view class="pc-nav-inner">
      <view class="pc-brand" @tap="go('/pages/index/index', 'tab')">
        <text class="pc-logo">B</text>
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
        <text v-if="isLogin" class="pc-user" @tap="go('/pages/profile/profile', 'tab')">
          {{ userNick }}
        </text>
        <text v-else class="pc-login" @tap="goLogin">登录 / 注册</text>
      </view>
    </view>
  </view>

  <!-- App.vue 不渲染内容，页面由 pages.json 驱动 -->
</template>

<style lang="scss">
@import './styles/theme.scss';
@import './styles/desktop.scss';

/* .pc-nav 的基线 display:none 在 styles/desktop.scss 里，PC 端 @media 块覆盖 */
</style>