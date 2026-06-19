<script setup>
import { ref } from 'vue'
import { useUserStore } from '@/store/user'

const userStore = useUserStore()
const loading = ref(false)

async function onWechatLogin() {
  if (loading.value) return
  loading.value = true
  uni.showLoading({ title: '登录中…' })
  try {
    await userStore.wechatLogin()
    uni.hideLoading()
    uni.showToast({ title: '登录成功', icon: 'success' })
    setTimeout(() => {
      const pages = getCurrentPages()
      if (pages.length > 1) uni.navigateBack()
      else uni.switchTab({ url: '/pages/index/index' })
    }, 600)
  } catch (e) {
    uni.hideLoading()
    uni.showToast({ title: e?.detail || '登录失败', icon: 'none' })
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <view class="login">
    <view class="brand">
      <text class="logo">📚</text>
      <text class="name">贝壳易书</text>
      <text class="slogan">校园二手书 · 拍照一键卖</text>
    </view>

    <view class="actions">
      <wd-button type="primary" block size="large" :loading="loading" @click="onWechatLogin">
        微信一键登录
      </wd-button>
      <text class="tip vb-muted">登录即表示同意用户协议与隐私政策</text>
    </view>
  </view>
</template>

<style scoped lang="scss">
.login {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 0 64rpx;
}
.brand {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 96rpx;
}
.logo {
  font-size: 120rpx;
}
.name {
  font-size: 48rpx;
  font-weight: 700;
  color: var(--vb-brand-600);
  margin-top: 16rpx;
}
.slogan {
  font-size: 26rpx;
  color: var(--vb-ink-500);
  margin-top: 12rpx;
}
.actions {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 24rpx;
}
.tip {
  font-size: 22rpx;
}
</style>
