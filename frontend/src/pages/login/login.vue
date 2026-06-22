<script setup>
/**
 * 登录页 - 三种登录方式
 *  1. 邮箱/用户名 + 密码（账号体系，H5 和小程序都可用）
 *  2. 注册账号（跳到 /pages/register/register）
 *  3. 微信一键登录（仅小程序 / 已配置 WECHAT_APPID 时可用）
 *
 * 视觉风格：vUSTB auth-panel —— 玻璃态圆角大卡 + 居中布局 + 标签式表单
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
  <view class="auth-shell">
    <view class="auth-panel glass-card animate-slide-up">
      <view class="head">
        <text class="logo">📚</text>
        <text class="name">贝壳易书</text>
        <text class="slogan">欢迎回来 · 校园二手书流转平台</text>
      </view>

      <!-- 邮箱 / 用户名 + 密码登录 -->
      <view class="form">
        <view class="field">
          <text class="lbl">账号</text>
          <input
            v-model="account"
            class="input"
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
              class="input"
              :password="!showPwd"
              placeholder="至少 6 位"
              :maxlength="64"
              placeholder-class="ipt-ph"
            />
            <text class="toggle" @tap="showPwd = !showPwd">{{ showPwd ? '隐藏' : '显示' }}</text>
          </view>
        </view>
        <view v-if="errMsg" class="err">{{ errMsg }}</view>

        <button class="btn-primary" :disabled="loading" @click="onPasswordLogin">
          {{ loading ? '登录中…' : '登录' }}
        </button>

        <view class="aux">
          <text class="muted">还没有账号？</text>
          <text class="link" @tap="goRegister">立即注册</text>
        </view>
      </view>

      <!-- 分隔线 -->
      <view class="divider">
        <text class="line" />
        <text class="txt">其他登录方式</text>
        <text class="line" />
      </view>

      <!-- 微信一键登录（小程序里始终显示；H5 隐藏以免误导） -->
      <view v-if="isWechatMp" class="wechat-wrap">
        <button class="btn-ghost" @click="onWechatLogin">微信一键登录</button>
        <text class="tip">登录即表示同意用户协议与隐私政策</text>
      </view>
      <text v-else class="tip">登录即表示同意用户协议与隐私政策</text>
    </view>
  </view>
</template>

<style scoped lang="scss">
.auth-shell {
  min-height: 100vh;
  padding: 80rpx 32rpx 40rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}
.auth-panel {
  width: 100%;
  max-width: 520rpx;
  padding: 56rpx 40rpx 48rpx;
}
.head {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 48rpx;
}
.logo {
  font-size: 80rpx;
  margin-bottom: 12rpx;
}
.name {
  font-size: 36rpx;
  font-weight: 700;
  color: var(--vb-heading);
  letter-spacing: 0.02em;
}
.slogan {
  font-size: 24rpx;
  color: var(--vb-ink-500);
  margin-top: 10rpx;
}
.form {
  display: flex;
  flex-direction: column;
  gap: 22rpx;
}
.field {
  display: flex;
  flex-direction: column;
  gap: 10rpx;
}
.lbl {
  font-size: 24rpx;
  color: var(--vb-ink-700);
  font-weight: 500;
}
.pwd-row {
  position: relative;
}
.toggle {
  position: absolute;
  right: 24rpx;
  top: 50%;
  transform: translateY(-50%);
  font-size: 24rpx;
  color: var(--vb-brand-700);
  font-weight: 500;
  cursor: pointer;
}
.ipt-ph {
  color: var(--vb-ink-400);
}
.err {
  font-size: 24rpx;
  color: var(--vb-danger);
  background: #fdeaea;
  padding: 14rpx 18rpx;
  border-radius: 10rpx;
}
.aux {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 8rpx;
  font-size: 24rpx;
  margin-top: 4rpx;
}
.muted {
  color: var(--vb-ink-500);
}
.link {
  color: var(--vb-brand-700);
  font-weight: 600;
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
  background: var(--vb-border);
}
.txt {
  font-size: 22rpx;
  color: var(--vb-ink-400);
}
.wechat-wrap {
  display: flex;
  flex-direction: column;
  gap: 16rpx;
  align-items: center;
}
.tip {
  display: block;
  font-size: 22rpx;
  text-align: center;
  color: var(--vb-ink-400);
  margin-top: 8rpx;
}

/* 让 button 元素继承 button reset，撑满宽度 */
.btn-primary,
.btn-ghost {
  width: 100%;
  border: none;
  font-family: inherit;
}
.btn-primary::after,
.btn-ghost::after {
  border: none;
}
</style>