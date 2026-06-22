<script setup>
/**
 * 登录页 - 邮箱 / 用户名 + 密码（也可微信一键登录）
 * 视觉对齐 vUSTB /login：
 *  - 顶部简洁文字 header（无大 emoji）
 *  - <label> 包裹输入 + 14px span 标签
 *  - 玻璃态 auth-panel + 26px 大圆角
 *  - 左上角返回按钮（H5/PC 上确保可以离开登录页）
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
    setTimeout(goHome, 500)
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
    setTimeout(goHome, 500)
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

function goHome() {
  // 登录成功 / 主动离开：回到首页 tab，跳过登录栈
  uni.switchTab({ url: '/pages/index/index' })
}

function goBack() {
  // 用户主动返回：用 switchTab 到首页（登录页不允许在栈里卡住）
  uni.switchTab({ url: '/pages/index/index' })
}
</script>

<template>
  <view class="auth-shell">
    <!-- 左上角返回按钮（H5 / PC 端尤为关键：手机物理返回 / 浏览器后退都能用） -->
    <view class="back-bar">
      <view class="back-btn" @tap="goBack">
        <text class="back-arrow">←</text>
        <text class="back-text">返回</text>
      </view>
    </view>

    <view class="auth-panel glass-card animate-slide-up">
      <view class="head">
        <text class="title">欢迎回来</text>
        <text class="sub">登录你的贝壳易书账户</text>
      </view>

      <!-- 邮箱 / 用户名 + 密码登录 -->
      <view class="form">
        <label class="field">
          <span class="lbl">账号</span>
          <input
            v-model="account"
            class="input"
            placeholder="邮箱或用户名"
            :maxlength="120"
            placeholder-class="ipt-ph"
            confirm-type="next"
          />
        </label>

        <label class="field">
          <span class="lbl">密码</span>
          <view class="pwd-row">
            <input
              v-model="password"
              class="input"
              :password="!showPwd"
              placeholder="至少 6 位"
              :maxlength="64"
              placeholder-class="ipt-ph"
              confirm-type="done"
              @confirm="onPasswordLogin"
            />
            <text class="toggle" @tap="showPwd = !showPwd">
              {{ showPwd ? '隐藏' : '显示' }}
            </text>
          </view>
        </label>

        <view v-if="errMsg" class="err">{{ errMsg }}</view>

        <button
          class="btn-primary submit"
          :disabled="loading"
          @click="onPasswordLogin"
        >
          {{ loading ? '登录中…' : '登 录' }}
        </button>

        <view class="meta-row">
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
      <text v-else class="tip">登录即表示同意《用户协议》与《隐私政策》</text>
    </view>
  </view>
</template>

<style scoped lang="scss">
.auth-shell {
  position: relative;
  min-height: 100vh;
  padding: 80rpx 32rpx 40rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* ===== 返回按钮（H5 / PC 端永远可见，不依赖 uni-app 原生 navBar） ===== */
.back-bar {
  position: absolute;
  top: 24rpx;
  left: 24rpx;
  z-index: 10;
}
.back-btn {
  display: inline-flex;
  align-items: center;
  gap: 6rpx;
  padding: 12rpx 22rpx;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.75);
  border: 1px solid var(--vb-border);
  box-shadow: var(--vb-shadow-sm);
  font-size: 26rpx;
  color: var(--vb-ink-700);
  font-weight: 500;
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
}
.back-btn:active {
  background: var(--vb-bg-mute);
}
.back-arrow {
  font-size: 30rpx;
  line-height: 1;
  color: var(--vb-brand-700);
}

/* ===== 玻璃态卡 ===== */
.auth-panel {
  width: 100%;
  max-width: 460rpx;
  padding: 56rpx 44rpx 48rpx;
  border-radius: 26px;
}
.head {
  text-align: center;
  margin-bottom: 40rpx;
}
.title {
  display: block;
  font-size: 36rpx;
  font-weight: 700;
  color: var(--vb-heading);
  letter-spacing: 0.01em;
  margin-bottom: 8rpx;
}
.sub {
  display: block;
  font-size: 24rpx;
  color: var(--vb-ink-500);
}

/* ===== 表单 ===== */
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
  font-size: 26rpx;
  font-weight: 500;
  color: var(--vb-ink-700);
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
  padding: 6rpx 10rpx;
}
.ipt-ph {
  color: var(--vb-ink-400);
}

/* ===== 错误条 ===== */
.err {
  font-size: 24rpx;
  color: var(--vb-danger);
  background: #fdeaea;
  padding: 14rpx 18rpx;
  border-radius: 10rpx;
  border: 1px solid rgba(220, 38, 38, 0.18);
}

/* ===== 提交按钮 ===== */
.submit {
  width: 100%;
  padding: 22rpx 0;
  font-size: 28rpx;
  border: none;
  font-weight: 600;
  margin-top: 8rpx;
}
.submit::after {
  border: none;
}

/* ===== 底部辅助行 ===== */
.meta-row {
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

/* ===== 分隔线 ===== */
.divider {
  display: flex;
  align-items: center;
  gap: 16rpx;
  margin: 36rpx 0 22rpx;
}
.line {
  flex: 1;
  height: 1rpx;
  background: var(--vb-border);
}
.txt {
  font-size: 22rpx;
  color: var(--vb-ink-400);
  letter-spacing: 0.04em;
}

/* ===== 微信登录 ===== */
.wechat-wrap {
  display: flex;
  flex-direction: column;
  gap: 14rpx;
  align-items: center;
}
.wechat-wrap .btn-ghost {
  width: 100%;
  border: none;
  font-family: inherit;
}
.wechat-wrap .btn-ghost::after {
  border: none;
}
.tip {
  display: block;
  font-size: 22rpx;
  text-align: center;
  color: var(--vb-ink-400);
  margin-top: 6rpx;
}
</style>
