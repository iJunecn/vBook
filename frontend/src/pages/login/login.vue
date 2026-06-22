<script setup>
/**
 * 登录页 - 三种登录方式
 *  1. 邮箱/用户名 + 密码（账号体系，H5 和小程序都可用）
 *  2. 注册账号（跳到 /pages/register/register）
 *  3. 微信一键登录（仅小程序 / 已配置 WECHAT_APPID 时可用）
 */
import { ref, computed } from 'vue'
import { useUserStore } from '@/store/user'

const userStore = useUserStore()

const account = ref('')
const password = ref('')
const loading = ref(false)
const errMsg = ref('')
const showPwd = ref(false)
const isWechatMp = computed(() => typeof uni !== 'undefined' && !!uni.getSystemInfoSync)

async function onPasswordLogin() {
  if (loading.value) return
  if (!account.value.trim() || !password.value) {
    errMsg.value = '请输入账号和密码'
    return
  }
  errMsg.value = ''
  loading.value = true
  uni.showLoading({ title: '登录中…' })
  try {
    await userStore.login({ account: account.value.trim(), password: password.value })
    uni.hideLoading()
    uni.showToast({ title: '登录成功', icon: 'success' })
    setTimeout(goBack, 500)
  } catch (e) {
    uni.hideLoading()
    errMsg.value = e?.detail || '登录失败'
  } finally {
    loading.value = false
  }
}

async function onWechatLogin() {
  if (loading.value) return
  loading.value = true
  uni.showLoading({ title: '登录中…' })
  try {
    await userStore.wechatLogin()
    uni.hideLoading()
    uni.showToast({ title: '登录成功', icon: 'success' })
    setTimeout(goBack, 500)
  } catch (e) {
    uni.hideLoading()
    errMsg.value = e?.detail || '微信登录失败'
  } finally {
    loading.value = false
  }
}

function goRegister() {
  uni.navigateTo({ url: '/pages/register/register' })
}

function goBack() {
  const pages = getCurrentPages()
  if (pages.length > 1) uni.navigateBack()
  else uni.switchTab({ url: '/pages/index/index' })
}
</script>

<template>
  <view class="page">
    <view class="card">
      <view class="brand">
        <text class="logo">📚</text>
        <text class="name">贝壳易书</text>
        <text class="slogan">校园二手书 · 拍照一键卖</text>
      </view>

      <!-- 邮箱 / 用户名 + 密码登录 -->
      <view class="form">
        <view class="field">
          <text class="lbl">账号</text>
          <input
            v-model="account"
            class="ipt"
            placeholder="邮箱或用户名"
            :maxlength="120"
            placeholder-class="ipt-ph"
          />
        </view>
        <view class="field">
          <text class="lbl">密码</text>
          <view class="pwd-row">
            <input
              v-model="password"
              class="ipt"
              :password="!showPwd"
              placeholder="至少 6 位"
              :maxlength="64"
              placeholder-class="ipt-ph"
            />
            <text class="toggle" @tap="showPwd = !showPwd">{{ showPwd ? '隐藏' : '显示' }}</text>
          </view>
        </view>
        <view v-if="errMsg" class="err">{{ errMsg }}</view>
        <wd-button type="primary" block size="large" :loading="loading" @click="onPasswordLogin">
          登录
        </wd-button>

        <view class="aux">
          <text class="link" @tap="goRegister">还没账号？立即注册</text>
        </view>
      </view>

      <!-- 分隔线 -->
      <view class="divider"><text class="line" /><text class="txt">其他登录方式</text><text class="line" /></view>

      <!-- 微信一键登录（小程序里始终显示；H5 隐藏以免误导） -->
      <view v-if="isWechatMp" class="wechat-wrap">
        <wd-button block size="large" @click="onWechatLogin">微信一键登录</wd-button>
        <text class="tip vb-muted">登录即表示同意用户协议与隐私政策</text>
      </view>
      <text v-else class="tip vb-muted">登录即表示同意用户协议与隐私政策</text>
    </view>
  </view>
</template>

<style scoped lang="scss">
.page {
  min-height: 100vh;
  padding: 80rpx 32rpx 40rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}
.card {
  width: 100%;
  max-width: 520rpx;
  background: #fff;
  border-radius: 24rpx;
  padding: 64rpx 40rpx 48rpx;
  box-shadow: 0 8rpx 32rpx rgba(37, 99, 235, 0.08);
}
.brand {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 56rpx;
}
.logo {
  font-size: 96rpx;
}
.name {
  font-size: 40rpx;
  font-weight: 700;
  color: var(--vb-brand-600);
  margin-top: 12rpx;
}
.slogan {
  font-size: 24rpx;
  color: var(--vb-ink-500);
  margin-top: 8rpx;
}
.form {
  display: flex;
  flex-direction: column;
  gap: 22rpx;
}
.field {
  display: flex;
  flex-direction: column;
  gap: 8rpx;
}
.lbl {
  font-size: 24rpx;
  color: var(--vb-ink-700);
}
.ipt {
  width: 100%;
  box-sizing: border-box;
  border: 1rpx solid var(--vb-brand-100);
  border-radius: 12rpx;
  padding: 18rpx 20rpx;
  font-size: 28rpx;
  background: #fff;
}
.ipt-ph {
  color: var(--vb-ink-300);
}
.pwd-row {
  position: relative;
}
.toggle {
  position: absolute;
  right: 20rpx;
  top: 50%;
  transform: translateY(-50%);
  font-size: 24rpx;
  color: var(--vb-brand-600);
}
.err {
  font-size: 24rpx;
  color: #e23d3d;
  background: #fdeaea;
  padding: 12rpx 16rpx;
  border-radius: 8rpx;
}
.aux {
  display: flex;
  justify-content: flex-end;
}
.link {
  font-size: 24rpx;
  color: var(--vb-brand-600);
}
.divider {
  display: flex;
  align-items: center;
  gap: 16rpx;
  margin: 40rpx 0 24rpx;
}
.line {
  flex: 1;
  height: 1rpx;
  background: var(--vb-brand-100);
}
.txt {
  font-size: 22rpx;
  color: var(--vb-ink-300);
}
.wechat-wrap {
  display: flex;
  flex-direction: column;
  gap: 16rpx;
  align-items: center;
}
.tip {
  font-size: 22rpx;
  text-align: center;
}
</style>
